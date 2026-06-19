import os
from helpers import upload_image_to_cloudinary
from io import BytesIO

class DummyFile:
    def __init__(self, content, filename):
        self.content = content
        self.filename = filename
    def read(self):
        return self.content

def test_upload():
    from config import Config
    print("Cloudinary URL:", Config.CLOUDINARY_URL)
    # 1x1 transparent PNG
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDAT\x08\x99c\xf8\x0f\x04\x00\x09\xfb\x03\xfd\xe3U\xf2\x9c\x00\x00\x00\x00IEND\xaeB`\x82'
    dummy = DummyFile(png_data, "test.png")
    
    print("Uploading to Cloudinary...")
    url = upload_image_to_cloudinary(dummy, "test_folder")
    print("Upload result:", url)

if __name__ == "__main__":
    test_upload()
