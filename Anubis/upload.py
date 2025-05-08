import os
from django.core.files.storage import default_storage
from django.contrib import messages


#logic for file-upload

def save_image(name, image):
   # Convert the name to a folder-friendly format
    folder_name = name.replace(" ", " ")

    # Check if the folder exists
    folder_path = os.path.join('Anubis/static/Knownfaces', folder_name)
    if not os.path.exists(folder_path):
        # Create the folder if it doesn't exist
        os.makedirs(folder_path)

    # Get the file extension and validate
    original_name = image.name
    ext = os.path.splitext(original_name)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png']:
        # Optionally, raise an error or just return None
        return None, None

    # Count existing images for sequential naming
    existimage = len(os.listdir(folder_path))
    image_name = f'image_{existimage + 1}{ext}'
    # Save the image in the folder
    image_path = os.path.join(folder_path, image_name)
    with default_storage.open(image_path, 'wb') as file:
        for chunk in image.chunks():
            file.write(chunk)

    # Return the folder name and image path for further use if needed
    return folder_name, image_path