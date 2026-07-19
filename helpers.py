import os
import urllib.parse
import cloudinary
import cloudinary.uploader
import cloudinary.api
from werkzeug.utils import secure_filename
from config import Config

def ensure_cloudinary_configured():
    """
    Dynamically configures Cloudinary using CLOUDINARY_URL from os.environ or Config.
    Returns True if configured successfully with valid credentials.
    """
    url = os.getenv('CLOUDINARY_URL') or getattr(Config, 'CLOUDINARY_URL', None)
    if not url or not url.startswith("cloudinary://"):
        return False
        
    if "API_KEY" in url or "CLOUD_NAME" in url:
        return False

    os.environ['CLOUDINARY_URL'] = url

    try:
        parsed = urllib.parse.urlsplit(url)
        api_key = urllib.parse.unquote(parsed.username) if parsed.username else None
        api_secret = urllib.parse.unquote(parsed.password) if parsed.password else None
        cloud_name = parsed.hostname
        
        if not cloud_name and "@" in url:
            cloud_name = url.split("@")[-1].split("/")[0].split("?")[0]

        if cloud_name and api_key and api_secret:
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret,
                secure=True
            )
            return True
    except Exception as e:
        print(f"Error parsing CLOUDINARY_URL credentials: {e}")

    try:
        cloudinary.config(secure=True)
        return True
    except Exception as e:
        print(f"Cloudinary auto-config error: {e}")
        return False

ensure_cloudinary_configured()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'jfif', 'avif', 'heic', 'heif', 'svg'}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image_to_cloudinary(file, folder_name="utopia", folder=None):
    """
    Uploads an image file to Cloudinary, or falls back to local storage if Cloudinary is not configured.
    Returns:
        The secure URL of the uploaded image if successful, or None if failed.
    """
    if folder:
        folder_name = folder
    if not file or file.filename == '':
        return None
        
    if not allowed_file(file.filename):
        return None
        
    # Reset stream cursor before uploading
    try:
        file.seek(0)
    except Exception:
        pass
        
    if ensure_cloudinary_configured():
        try:
            upload_result = cloudinary.uploader.upload(
                file,
                folder=f"utopia/{folder_name}",
                resource_type="image"
            )
            if upload_result.get("secure_url"):
                return upload_result.get("secure_url")
            elif upload_result.get("url"):
                return upload_result.get("url")
        except Exception as e:
            print(f"Cloudinary upload error: {e}. Falling back to local storage...")
            try:
                file.seek(0)
            except Exception:
                pass
            
    # Local fallback
    try:
        import time
        filename = secure_filename(file.filename)
        if '.' in filename:
            name_parts = filename.rsplit('.', 1)
            timestamped_filename = f"{name_parts[0]}_{int(time.time())}.{name_parts[1]}"
        else:
            timestamped_filename = f"{filename}_{int(time.time())}"
        
        basedir = os.path.abspath(os.path.dirname(__file__))
        upload_folder = os.path.join(basedir, 'static', 'uploads', folder_name)
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, timestamped_filename)
        file.seek(0)
        file.save(filepath)
        
        return f"/static/uploads/{folder_name}/{timestamped_filename}"
    except Exception as e:
        print(f"Local file upload error: {e}")
        return None

def delete_image_from_cloudinary(image_url):
    """
    Deletes an image from Cloudinary given its secure URL, or from local storage if it's a local file.
    """
    if not image_url:
        return False
        
    if image_url.startswith('/static/uploads/'):
        try:
            basedir = os.path.abspath(os.path.dirname(__file__))
            relative_path = image_url.lstrip('/')
            filepath = os.path.join(basedir, relative_path)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception as e:
            print(f"Local file delete error: {e}")
            return False
            
    if "cloudinary.com" not in image_url:
        return False
        
    ensure_cloudinary_configured()
    try:
        parts = image_url.split('/upload/')
        if len(parts) == 2:
            path_part = parts[1]
            if path_part.startswith('v') and '/' in path_part:
                parts_after_v = path_part.split('/', 1)
                if parts_after_v[0][1:].isdigit():
                    path_part = parts_after_v[1]
            
            public_id = path_part.rsplit('.', 1)[0]
            result = cloudinary.uploader.destroy(public_id)
            return result.get("result") == "ok"
    except Exception as e:
        print(f"Cloudinary delete error: {e}")
        return False
        
    return False

def format_product_description(raw_text, category_name, subcategory_name, mrp):
    """
    Automatically formats a plain paragraph product description into structured HTML.
    Includes Overview, Key Features, and Specifications.
    """
    if not raw_text:
        return ""
        
    # If it seems like it's already HTML formatted, return as is
    if "<h3>" in raw_text or "<p>" in raw_text or "<ul>" in raw_text:
        return raw_text

    import re
    
    # Defaults
    overview_text = ""
    features_list = []
    dimensions_val = 'Standard (Customizable on request)'
    price_val = f"₹{mrp}" if mrp else "N/A"
    cat_display = category_name.replace('-', ' ').title() if category_name else "N/A"
    subcat_display = subcategory_name if subcategory_name else "N/A"
    
    # Regex to split by labels
    pattern = re.compile(r'(Features:|Dimensions:|Price:|Category:|Sub-Category:)', re.IGNORECASE)
    parts = pattern.split(raw_text)
    
    if len(parts) > 1:
        overview_text = parts[0].strip()
        
        for i in range(1, len(parts), 2):
            label = parts[i].lower()
            content = parts[i+1].strip()
            
            if label == "features:":
                # Clean features into a list, stripping existing bullets and newlines
                lines = [line.strip() for line in re.split(r'\n|•|-', content) if line.strip()]
                # If there was no clear separator, try splitting by sentences
                if len(lines) == 1 and not content.startswith('•') and '.' in content:
                     lines = [s.strip() for s in re.split(r'(?<=[.!?]) +', content) if s.strip()]
                features_list = lines
                
            elif label == "dimensions:":
                dimensions_val = content.strip('.,; ')
            elif label == "price:":
                price_val = content.strip('.,; ')
            elif label == "category:":
                cat_display = content.strip('.,; ')
            elif label == "sub-category:":
                subcat_display = content.strip('.,; ')
                
    else:
        # Fallback to existing logic if no labels found
        sentences = re.split(r'(?<=[.!?]) +', raw_text.strip())
        if len(sentences) <= 2:
            overview_text = raw_text
            features_list.extend([
                "Premium quality materials and craftsmanship.",
                "Modern and elegant design suitable for any space.",
                "Durable and built for long-lasting comfort."
            ])
        else:
            overview_text = " ".join(sentences[:2])
            for s in sentences[2:]:
                if s.strip():
                    features_list.append(s.strip())

    features_html = "\n".join([f"<li>{f.strip('• -')}</li>" for f in features_list])
    
    html = f"""<h3>Product Overview</h3>
<p>{overview_text}</p>

<h3 style="margin-top: 25px;">Key Features</h3>
<ul style="padding-left: 20px; margin-bottom: 25px;">
{features_html}
</ul>

<h3 style="margin-top: 25px;">Specifications</h3>
<div class="specifications" style="background: #fdfcf9; padding: 25px; border-radius: 16px; border: 1px solid rgba(144, 110, 73, 0.15); margin-top: 15px; box-shadow: 0px 4px 15px rgba(0,0,0,0.02);">
<p style="margin-bottom: 12px; font-size: 15px;"><strong>Dimensions:</strong> {dimensions_val}</p>
<p style="margin-bottom: 12px; font-size: 15px;"><strong>Price:</strong> {price_val}</p>
<p style="margin-bottom: 12px; font-size: 15px;"><strong>Category:</strong> {cat_display}</p>
<p style="margin-bottom: 0; font-size: 15px;"><strong>Sub-Category:</strong> {subcat_display}</p>
</div>"""

    return html

def upload_pdf_to_cloudinary(file, folder_name="catalogue"):
    """
    Saves the PDF file locally to avoid Cloudinary raw delivery security blocks.
    """
    if not file or file.filename == '':
        return None
        
    if not file.filename.lower().endswith('.pdf'):
        return None
        
    try:
        import time
        filename = secure_filename(file.filename)
        if '.' in filename:
            name_parts = filename.rsplit('.', 1)
            timestamped_filename = f"{name_parts[0]}_{int(time.time())}.pdf"
        else:
            timestamped_filename = f"{filename}_{int(time.time())}.pdf"
        
        basedir = os.path.abspath(os.path.dirname(__file__))
        upload_folder = os.path.join(basedir, 'static', 'uploads', folder_name)
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, timestamped_filename)
        file.seek(0)
        file.save(filepath)
        
        return f"/static/uploads/{folder_name}/{timestamped_filename}"
    except Exception as e:
        print(f"Local PDF upload error: {e}")
        return None
