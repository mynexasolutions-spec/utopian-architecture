import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from werkzeug.utils import secure_filename
from config import Config

# Configure Cloudinary globally using the URL from config
if Config.CLOUDINARY_URL and Config.CLOUDINARY_URL.startswith("cloudinary://"):
    _url = Config.CLOUDINARY_URL[13:]
    if "@" in _url:
        _creds, _cloud_name = _url.split("@", 1)
        if ":" in _creds:
            _api_key, _api_secret = _creds.split(":", 1)
            cloudinary.config(
                cloud_name=_cloud_name,
                api_key=_api_key,
                api_secret=_api_secret,
                secure=True
            )

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image_to_cloudinary(file, folder_name="utopia"):
    """
    Uploads an image file to Cloudinary.
    
    Args:
        file: The file-like object from request.files
        folder_name: The Cloudinary folder to store the image in.
        
    Returns:
        The secure URL of the uploaded image if successful, or None if failed.
    """
    if not file or file.filename == '':
        return None
        
    if not allowed_file(file.filename):
        return None
        
    try:
        # Upload the file to Cloudinary
        upload_result = cloudinary.uploader.upload(
            file,
            folder=f"utopia/{folder_name}",
            resource_type="image"
        )
        # Return the secure URL provided by Cloudinary
        return upload_result.get("secure_url")
    except Exception as e:
        print(f"Cloudinary upload error: {e}")
        return None

def delete_image_from_cloudinary(image_url):
    """
    Deletes an image from Cloudinary given its secure URL.
    This attempts to extract the public_id from the URL.
    """
    if not image_url or "cloudinary.com" not in image_url:
        return False
        
    try:
        # Extract public_id from the standard Cloudinary URL
        # e.g., https://res.cloudinary.com/cloud_name/image/upload/v1234567/utopia/slider/filename.jpg
        # The public_id is "utopia/slider/filename"
        parts = image_url.split('/upload/')
        if len(parts) == 2:
            path_part = parts[1]
            # Remove the version part if exists (e.g., v123456/)
            if path_part.startswith('v') and '/' in path_part:
                parts_after_v = path_part.split('/', 1)
                if parts_after_v[0][1:].isdigit():
                    path_part = parts_after_v[1]
            
            # Remove file extension
            public_id = path_part.rsplit('.', 1)[0]
            
            # Delete the resource
            result = cloudinary.uploader.destroy(public_id)
            return result.get("result") == "ok"
    except Exception as e:
        print(f"Cloudinary delete error: {e}")
        return False
        
    return False
