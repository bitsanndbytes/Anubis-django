from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required
from Anubis.upload import save_image
from django.http import JsonResponse
from .models import CameraDetails
from Anubis.test import display_multiple_cameras
from django.http import HttpRequest
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from datetime import datetime, timedelta
from django.conf import settings
import os

# Create your views here.

def login(request):
    #Login Logic
    if request.method == 'POST':
        if 'username' in request.POST:
            username1 = request.POST['username']
            password2 = request.POST['password']
            user = authenticate(request, username=username1, password=password2)
            if user is not None:
                auth_login(request, user)
                return redirect('dashboard')
            else:
                messages.add_message(request, messages.ERROR, 'Invalid Username or Password!')
                return redirect('login')
        #Signup logic 
        elif "signupname" in request.POST:
            signupname = request.POST.get('signupname', None)
            password1 = request.POST.get('password1', None)

            if User.objects.exists():
                messages.error(request, "Sorry only one account is allowed!")
                return redirect('login')
            if not password1:
                messages.error(request, 'Password Field is Required!')
                return redirect('login')
            if not signupname:
                messages.error(request, "Username Must be Given!")
                return redirect('login')
            if User.objects.filter(username=signupname).exists():
                messages.info(request, 'Username is already Taken!')
                return redirect('login')
            else:
                myuser = User.objects.create_user(signupname, password=password1)
                myuser.save()
                messages.success(request, 'Account Created Successfully!')

    return render(request, 'Login.html')
 
#Dashboard Logic
@login_required(login_url='login')
def dashboard(request):
    # Get the complete host string (including hostname and port)
    complete_host = HttpRequest.get_host(request)

    # Split the host into hostname and port
    server_ip, server_port = complete_host.split(':')
    server_port = 8000
    ws_url = f'ws://{server_ip}:{server_port}'
    context = {'server_ip': server_ip, 'server_port': server_port, 'ws_url': ws_url}
    # empty dictionary list for post input request
    camera_info = []
    # for loop to process 4 forms in the dashboard
    if request.method == "POST":
        for i in range(1,5):
            camera_name = request.POST.get(f'camera{i}', '')
            camera_url = request.POST.get(f'camera{i}url', '')

            if camera_name and camera_url:
                # logic to save user input to db
                try:
                    # checks the for loop {i} against camera_id to update or save new camera details
                    camera_details = CameraDetails.objects.get(camera_id=f'{i}')
                    camera_details.name = camera_name
                    camera_details.url = camera_url
                    camera_details.save()
                except CameraDetails.DoesNotExist:
                    CameraDetails.objects.create(camera_id=f'{i}', name=camera_name, url=camera_url)
                    # prints items in the db
        all_camera_instances = CameraDetails.objects.all()
        for camera_instance in all_camera_instances:
            #testing
            info_dict = {
                'url': camera_instance.url,
                'name': camera_instance.name,
            }
            camera_info.append(info_dict)
        if camera_info:
            print(f"ID: {camera_instance.id}, Name: {camera_instance.name}, URL: {camera_instance.url}")
    return render (request, 'dashboard.html', context)



#Logout logic
@login_required(login_url='login')
def logout_route(request):
    logout(request)
    messages.info(request, 'You have been logged out! ')
    return redirect('login')

#logic for upload
@login_required(login_url='login')
def Upload(request):
    if request.method == 'POST':
        username = request.POST.get('Recusername', None)
        file = request.FILES.get('Recimage', None)
        if not username:
            messages.error(request, 'Image Name is Needed!')
            return redirect('Upload')
        if not file:
            messages.error(request, 'Image file is needed!')
            return redirect('Upload')
        messages.success(request, "Image save Successfully!")
        save_image(username, file)
    return render(request,'Upload.html')

#Logic for Notify
@login_required(login_url='login')
def Notify(request):
    return render(request,'notify_new.html')


#Logic fo Unknownfaces
@login_required(login_url='Unknown')
def Unknownfaces(request):
    return render(request, 'unknownface.html')


#test

@csrf_exempt
@require_POST
def save_camera(request):
    try:
        data = json.loads(request.body)
        camera_id = data.get('camera_id')
        camera_name = data.get('camera_name')
        rtsp_url = data.get('rtsp_url')

        logging.info(f"Received camera details - ID: {camera_id}, Name: {camera_name}, URL: {rtsp_url}")

        if not all([camera_id, camera_name, rtsp_url]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Validate RTSP URL format
        if not rtsp_url.startswith('rtsp://'):
            return JsonResponse({'error': 'Invalid RTSP URL format'}, status=400)

        # Update or create camera details
        try:
            camera, created = CameraDetails.objects.update_or_create(
                id=camera_id,
                defaults={
                    'name': camera_name,
                    'url': rtsp_url,
                    'camera_id': str(camera_id)  # Ensure camera_id is set
                }
            )
            logging.info(f"Camera {'created' if created else 'updated'} successfully with ID: {camera.id}")

            return JsonResponse({
                'status': 'success',
                'camera_id': camera.id,
                'message': 'Camera details saved successfully'
            })
        except Exception as e:
            logging.error(f"Database error while saving camera: {str(e)}")
            return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logging.error(f"Unexpected error in save_camera: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
@csrf_exempt
def stop_stream(request, camera_id):
    try:
        # Get the channel layer
        channel_layer = get_channel_layer()
        
        # Send a message to the consumer to stop the stream
        async_to_sync(channel_layer.group_send)(
            f"camera_{camera_id}",
            {
                "type": "stop.stream",
                "camera_id": camera_id
            }
        )
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@login_required(login_url='login')
def settings_view(request):
    return render(request, 'settings.html')

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        user = request.user
        
        # Verify current password
        if not user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('settings')
            
        # Check if new passwords match
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('settings')
            
        # Change the password
        user.set_password(new_password)
        user.save()
        
        # Re-authenticate the user
        updated_user = authenticate(username=user.username, password=new_password)
        auth_login(request, updated_user)
        
        messages.success(request, 'Password changed successfully.')
        return redirect('settings')
        
    return redirect('settings')

@login_required(login_url='login')
def activity_log(request):
    # Get filter parameters
    activity_type = request.GET.get('activity_type', '')
    date_range = request.GET.get('date_range', '')
    
    # Initialize activities list
    activities = []
    
    # Read from activity log file
    log_file = os.path.join(settings.BASE_DIR, 'activity.log')
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    # Parse log line
                    timestamp_str, type_, description = line.strip().split('|')
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    
                    # Apply filters
                    if activity_type and type_ != activity_type:
                        continue
                    if date_range:
                        filter_date = datetime.strptime(date_range, '%Y-%m-%d')
                        if timestamp.date() != filter_date.date():
                            continue
                    
                    activities.append({
                        'timestamp': timestamp,
                        'type': type_,
                        'description': description
                    })
                except ValueError:
                    continue
    
    # Sort activities by timestamp (newest first)
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    context = {
        'activities': activities,
        'selected_type': activity_type,
        'selected_date': date_range
    }
    return render(request, 'activity_log.html', context)

def log_activity(activity_type, description):
    """Helper function to log activities"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp}|{activity_type}|{description}\n"
    
    log_file = os.path.join(settings.BASE_DIR, 'activity.log')
    with open(log_file, 'a') as f:
        f.write(log_entry)

