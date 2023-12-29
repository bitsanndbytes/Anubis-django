from models import CameraDetails 
# Retrieve all items
all_camera_details = CameraDetails.objects.all()

# Display each item's details
for camera_detail in all_camera_details:
    print(f"ID: {camera_detail.id}, Camera ID: {camera_detail.camera_id}, Name: {camera_detail.name}, URL: {camera_detail.url}")
