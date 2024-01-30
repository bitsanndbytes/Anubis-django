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
    return render(request,'Notify.html')


#Logic fo Unknownfaces
@login_required(login_url='Unknown')
def Unknownfaces(request):
    return render(request, 'unknownface.html')


#test

