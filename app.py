import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, abort, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from jinja2 import TemplateNotFound
from functools import wraps
from urllib.parse import quote
from werkzeug.utils import secure_filename

# Import custom configuration and helpers
from config import Config
from helpers import upload_image_to_cloudinary, delete_image_from_cloudinary, allowed_file

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Load configurations
app.config.from_object(Config)

# Make sure the instance folder exists dynamically (for fallback SQLite)
os.makedirs(app.instance_path, exist_ok=True)

# Initialize the SQLAlchemy instance
db = SQLAlchemy(app)

# Database Model for Contact Form Submissions
class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(150))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Contact {self.name} - {self.email}>"

class HeroSlider(db.Model):
    __tablename__ = 'hero_sliders'
    
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    heading = db.Column(db.String(255), nullable=False)
    sub_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<HeroSlider {self.id}>"

class CatalogProduct(db.Model):
    __tablename__ = 'catalog_products'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False) # e.g. furniture, home-decor
    name = db.Column(db.String(100), nullable=False)
    mrp = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    in_stock = db.Column(db.Boolean, default=True, nullable=False)
    short_description = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    gallery_images = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CatalogProduct {self.name}>"

class GalleryImage(db.Model):
    __tablename__ = 'gallery_images'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False) # e.g. living-room, bedroom
    image_url = db.Column(db.String(255), nullable=False)
    alt_text = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<GalleryImage {self.id} - {self.category}>"

# Create the SQLite tables on application startup
with app.app_context():
    db.create_all()
    
    # Ensure gallery_images column exists in SQLite table
    try:
        db.session.execute(db.text("SELECT gallery_images FROM catalog_products LIMIT 1"))
    except Exception:
        db.session.rollback()
        try:
            db.session.execute(db.text("ALTER TABLE catalog_products ADD COLUMN gallery_images TEXT"))
            db.session.commit()
            print("Successfully added gallery_images column to catalog_products table.")
        except Exception as e:
            db.session.rollback()
            print(f"Error migrating database: {e}")
    
    # Seed default sliders if the table is empty
    if HeroSlider.query.count() == 0:
        default_sliders = [
            {
                "image_url": "/static/img/hero/banner-1.jpg",
                "heading": 'MAKE YOUR <span class="secondary">HOME</span><br />FEEL LIKE <span class="secondary">HOME</span>',
                "sub_text": 'Your space should tell your story. We carefully blend textures, colors, and lighting to create interiors that bring comfort, warmth, and character — a perfect backdrop for moments and memories that matter.'
            },
            {
                "image_url": "https://images.pexels.com/photos/1571460/pexels-photo-1571460.jpeg?auto=compress&cs=tinysrgb&w=1920&q=80",
                "heading": 'LUXURY <span class="secondary">DESIGN</span><br />FOR MODERN <span class="secondary">LIVING</span>',
                "sub_text": 'Experience unparalleled elegance and sophistication. We specialize in crafting modern, bespoke interiors that elevate your lifestyle with premium furnishings and exquisite finishes.'
            },
            {
                "image_url": "https://images.pexels.com/photos/2988860/pexels-photo-2988860.jpeg?auto=compress&cs=tinysrgb&w=1920&q=80",
                "heading": 'CUSTOM <span class="secondary">FURNITURE</span><br />& OUTDOOR <span class="secondary">WORKS</span>',
                "sub_text": 'Transform your spaces with bespoke solutions. From expertly crafted custom furniture to stunning pergolas and outdoor retreats, we bring visionary designs to life.'
            }
        ]
        for slide_data in default_sliders:
            new_slide = HeroSlider(**slide_data)
            db.session.add(new_slide)
            
    # Seed default catalog products if the table is empty
    if CatalogProduct.query.count() == 0:
        default_products = [
            {
                "category": "furniture",
                "name": "Modern Sofa",
                "mrp": "$1,250",
                "image_url": "/static/img/products/sectional2.webp",
                "short_description": "A stylish and comfortable 3-seater sofa with premium fabric upholstery, perfect for modern living rooms.",
                "description": "Elevate your living space with our premium Modern Sofa. Crafted with a solid hardwood frame, high-density foam cushioning, and upholstered in a luxurious, durable fabric, this sofa offers both exceptional comfort and contemporary style. Designed to fit seamlessly into modern apartments or houses, it features clean lines, sleek steel legs, and soft armrests."
            },
            {
                "category": "furniture",
                "name": "Luxury Dining Table",
                "mrp": "$2,400",
                "image_url": "/static/img/products/Dining.webp",
                "short_description": "Elegant 6-seater wooden dining table with a polished marble top and sturdy timber legs.",
                "description": "Host unforgettable dinners with the Luxury Dining Table. Featuring a stunning natural marble top with unique veining patterns and supported by a robust solid oak frame, this table blends strength with sheer elegance. Comfortably seating up to six guests, it serves as a stunning centerpiece for any modern dining area."
            },
            {
                "category": "outdoor",
                "name": "Outdoor Pergola",
                "mrp": "$3,800",
                "image_url": "/static/img/products/Outdoor_Pergola.webp",
                "short_description": "Weather-resistant wooden outdoor pergola, ideal for gardens, patios, and terrace decks.",
                "description": "Transform your outdoor living area with our custom wooden Pergola. Made from premium, weather-treated teak wood, this pergola provides a perfect balance of shade and sunshine. Whether set up in a garden, by the pool, or on a spacious terrace, it creates a cozy, elegant outdoor retreat perfect for relaxing or entertaining guests."
            },
            {
                "category": "home-decor",
                "name": "Minimal Table Lamp",
                "mrp": "$180",
                "image_url": "/static/img/products/Minimal.webp",
                "short_description": "A sleek, minimalist ceramic table lamp providing warm ambient lighting.",
                "description": "Bring warmth and sophisticated style to your bedside table or desk with the Minimal Table Lamp. Its geometric ceramic base paired with a textured fabric drum shade creates a soft, diffused glow. Equipped with energy-efficient LED compatibility, it features a clean white matte finish that complements any modern minimalist decor."
            },
            {
                "category": "home-decor",
                "name": "Luxury Wall Mirror",
                "mrp": "$420",
                "image_url": "/static/img/products/Luxury_Wall_Mirror.webp",
                "short_description": "A large statement wall mirror with a bespoke brushed brass frame.",
                "description": "Make your rooms feel larger and brighter with this gorgeous Luxury Wall Mirror. Hand-finished with a premium brushed brass frame, its clean round design adds a modern architectural touch to entryways, bedrooms, or living spaces. Featuring distortion-free high-definition glass, it serves as both a functional mirror and a striking piece of wall art."
            },
            {
                "category": "accessories",
                "name": "Decorative Vase Set",
                "mrp": "$140",
                "image_url": "/static/img/products/Decorative.webp",
                "short_description": "A trio of hand-painted matte ceramic vases in earth tones.",
                "description": "Add an artistic touch to your shelves, console tables, or mantels with the Decorative Vase Set. This collection of three textured ceramic vases features varying heights and organic shapes, finished in a harmonious earthy color palette. Perfect for displaying dry botanicals, pampas grass, or standing alone as modern sculptural accents."
            }
        ]
        for prod_data in default_products:
            db.session.add(CatalogProduct(**prod_data))
            
    db.session.commit()

    # Seed/Update gallery images for default products
    default_gallery_images = {
        "Modern Sofa": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1484101403633-562f891dc89a?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=800&q=80",
        "Luxury Dining Table": "https://images.unsplash.com/photo-1615066390971-03e4e1c36ddf?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1577140917170-285929fb55b7?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1604014237800-1c9102c219da?auto=format&fit=crop&w=800&q=80",
        "Outdoor Pergola": "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=800&q=80",
        "Minimal Table Lamp": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1540932239986-30128078f3c5?auto=format&fit=crop&w=800&q=80",
        "Luxury Wall Mirror": "https://images.unsplash.com/photo-1618220179428-22790b461013?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?auto=format&fit=crop&w=800&q=80",
        "Decorative Vase Set": "https://images.unsplash.com/photo-1578500494198-246f612d3b3d?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1612196808214-b8e1d6145a8c?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=800&q=80"
    }
    for name, gallery_str in default_gallery_images.items():
        prod = CatalogProduct.query.filter_by(name=name).first()
        if prod:
            prod.gallery_images = gallery_str
    db.session.commit()

    # Seed default gallery images if table is empty
    if GalleryImage.query.count() == 0:
        gallery_dir = os.path.join(app.static_folder, 'img', 'gallery')
        categories_map = {
            'living_room': 'living-room',
            'bedroom': 'bedroom',
            'kitchen': 'kitchen',
            'office': 'office',
            'sofaset': 'sofaset',
            'other': 'other'
        }
        for dir_name, filter_class in categories_map.items():
            cat_dir = os.path.join(gallery_dir, dir_name)
            if os.path.exists(cat_dir):
                for file in os.listdir(cat_dir):
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        alt_text = file.split('.')[0].replace('_', ' ').replace('-', ' ').title()
                        image_url = f"/static/img/gallery/{dir_name}/{file}"
                        new_gallery_img = GalleryImage(
                            category=filter_class,
                            image_url=image_url,
                            alt_text=alt_text
                        )
                        db.session.add(new_gallery_img)
        db.session.commit()

# --- USER ROUTES ---

@app.route('/')
def home():
    """Renders the Home Page."""
    sliders = HeroSlider.query.order_by(HeroSlider.created_at.asc()).all()
    catalog_products = CatalogProduct.query.order_by(CatalogProduct.created_at.desc()).all()
    
    # Get unique categories for frontend filters
    categories = db.session.query(CatalogProduct.category).distinct().all()
    unique_categories = [cat[0] for cat in categories]
    
    return render_template('pages/index.html', sliders=sliders, catalog_products=catalog_products, unique_categories=unique_categories)

@app.route('/about')
def about():
    """Renders the About Page."""
    return render_template('pages/about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    Handles Contact Page rendering (GET) and Form Submissions (POST).
    Stores form inputs inside contacts.db.
    """
    if request.method == 'POST':
        # Retrieve form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json' or request.content_type == 'application/json'
        
        # Simple validations
        if not name or not email or not message:
            if is_ajax:
                return {"status": "error", "message": "Please fill out all required fields."}, 400
            flash("Please fill out all required fields.", "danger")
            return redirect(url_for('contact'))
            
        try:
            # Create a new Contact record
            new_contact = Contact(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message
            )
            db.session.add(new_contact)
            db.session.commit()
            
            if is_ajax:
                return {"status": "success", "message": "Your message has been sent successfully! We will get back to you soon."}, 200
                
            flash("Your message has been sent successfully! We will get back to you soon.", "success")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error saving contact form: {e}")
            if is_ajax:
                return {"status": "error", "message": "An error occurred while sending your message. Please try again later."}, 500
                
            flash("An error occurred while sending your message. Please try again later.", "danger")
            
        return redirect(url_for('contact'))
        
    return render_template('pages/contact.html')

@app.route('/services')
def services():
    """Renders the Services Page."""
    return render_template('pages/services.html')

@app.route('/gallery')
def gallery():
    """Renders the Gallery Page."""
    images = GalleryImage.query.order_by(GalleryImage.created_at.desc()).all()
    
    gallery_items = []
    for img in images:
        gallery_items.append({
            'filter_class': img.category,
            'image_url': img.image_url,
            'alt': img.alt_text or "Gallery Image"
        })
        
    return render_template('pages/gallery.html', gallery_items=gallery_items)

@app.route('/shop')
def shop():
    """Renders the Shop Page."""
    return render_template('pages/shop.html')

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Renders the Product Detail Page."""
    product = CatalogProduct.query.get_or_404(product_id)
    return render_template('pages/product_detail.html', product=product)

# --- DYNAMIC PAGE ROUTING FALLBACK ---

@app.route('/page/<slug>')
def dynamic_page(slug):
    """
    Dynamic page router. 
    Attempts to match templates under templates/pages/{slug}.html.
    """
    try:
        return render_template(f"pages/{slug}.html")
    except TemplateNotFound:
        abort(404)

# --- ADMIN PANEL ROUTES ---

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            next_param = quote(request.path, safe='')
            return redirect(f"{url_for('admin_login')}?next={next_param}")
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin_user = os.getenv('ADMIN_USERNAME', 'admin')
        admin_pass = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        if username == admin_user and password == admin_pass:
            session['admin_logged_in'] = True
            flash("Logged in successfully.", "success")
            next_url = request.args.get('next')
            return redirect(next_url or url_for('admin_dashboard'))
        else:
            flash("Invalid credentials.", "danger")
            
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('admin_login', next='/admin'))

@app.route('/admin')
@login_required
def admin_dashboard():
    """
    Displays the admin dashboard listing all contact submissions.
    """
    try:
        from datetime import date, timedelta
        # Fetch all submissions ordered by newest first
        submissions = Contact.query.order_by(Contact.created_at.desc()).all()
        today = date.today()
        yesterday = datetime.utcnow() - timedelta(days=1)
        return render_template(
            'admin/dashboard.html', 
            submissions=submissions, 
            datetime_today=today, 
            yesterday=yesterday
        )
    except Exception as e:
        app.logger.error(f"Error fetching admin submissions: {e}")
        return "An error occurred while loading the admin dashboard. Please verify database setup.", 500

@app.route('/admin/edit/<int:id>', methods=['POST'])
@login_required
def admin_edit_submission(id):
    """
    Endpoint for editing a contact submission (via POST from dashboard modal).
    """
    submission = Contact.query.get_or_404(id)
    submission.name = request.form.get('name')
    submission.email = request.form.get('email')
    submission.phone = request.form.get('phone')
    submission.subject = request.form.get('subject')
    submission.message = request.form.get('message')
    try:
        db.session.commit()
        flash("Submission updated successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating submission: {e}")
        flash("Failed to update the submission.", "danger")
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_submission(id):
    """
    Endpoint for deleting a contact submission.
    """
    submission = Contact.query.get_or_404(id)
    try:
        db.session.delete(submission)
        db.session.commit()
        flash("Submission deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting submission: {e}")
        flash("Failed to delete the submission.", "danger")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/slider')
@login_required
def admin_slider():
    """Displays the admin dashboard listing all hero slides."""
    try:
        sliders = HeroSlider.query.order_by(HeroSlider.created_at.asc()).all()
        return render_template('admin/slider.html', sliders=sliders)
    except Exception as e:
        app.logger.error(f"Error fetching admin sliders: {e}")
        return "An error occurred while loading the sliders. Please verify database setup.", 500

@app.route('/admin/slider/add', methods=['POST'])
@login_required
def admin_add_slider():
    """Endpoint for adding a new hero slide."""
    heading = request.form.get('heading')
    sub_text = request.form.get('sub_text')
    
    if not heading or not sub_text:
        flash("Please fill out heading and sub text.", "danger")
        return redirect(url_for('admin_slider'))
        
    image_file = request.files.get('image')
    if not image_file or image_file.filename == '':
        flash("Please upload an image.", "danger")
        return redirect(url_for('admin_slider'))
        
    image_url = upload_image_to_cloudinary(image_file, folder_name="slider")
    if not image_url:
        flash("Invalid file format or upload failed.", "danger")
        return redirect(url_for('admin_slider'))
        
    try:
        new_slide = HeroSlider(
            image_url=image_url,
            heading=heading,
            sub_text=sub_text
        )
        db.session.add(new_slide)
        db.session.commit()
        flash("Slide added successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding slide: {e}")
        flash("Failed to add the slide.", "danger")
        
    return redirect(url_for('admin_slider'))

@app.route('/admin/slider/edit/<int:id>', methods=['POST'])
@login_required
def admin_edit_slider(id):
    """Endpoint for editing a hero slide."""
    slide = HeroSlider.query.get_or_404(id)
    slide.heading = request.form.get('heading')
    slide.sub_text = request.form.get('sub_text')
    
    image_file = request.files.get('image')
    if image_file and image_file.filename != '':
        new_image_url = upload_image_to_cloudinary(image_file, folder_name="slider")
        if new_image_url:
            slide.image_url = new_image_url
        else:
            flash("Invalid file format or upload failed.", "danger")
            return redirect(url_for('admin_slider'))
            
    try:
        db.session.commit()
        flash("Slide updated successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating slide: {e}")
        flash("Failed to update the slide.", "danger")
        
    return redirect(url_for('admin_slider'))

@app.route('/admin/slider/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_slider(id):
    """Endpoint for deleting a hero slide."""
    slide = HeroSlider.query.get_or_404(id)
    try:
        db.session.delete(slide)
        db.session.commit()
        flash("Slide deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting slide: {e}")
        flash("Failed to delete the slide.", "danger")
    return redirect(url_for('admin_slider'))

@app.route('/admin/catalog')
@login_required
def admin_catalog():
    """Displays the catalog dashboard."""
    try:
        products = CatalogProduct.query.order_by(CatalogProduct.created_at.desc()).all()
        return render_template('admin/catalog.html', products=products)
    except Exception as e:
        app.logger.error(f"Error fetching admin catalog: {e}")
        return "An error occurred while loading the catalog. Please verify database setup.", 500

@app.route('/admin/catalog/add', methods=['POST'])
@login_required
def admin_add_catalog():
    """Endpoint for adding a new catalog product."""
    category = request.form.get('category')
    if category == 'other':
        custom_category = request.form.get('custom_category')
        if custom_category:
            category = custom_category.strip().lower().replace(' ', '-')
            
    name = request.form.get('name')
    mrp = request.form.get('mrp')
    in_stock = request.form.get('in_stock') == 'on'
    short_description = request.form.get('short_description')
    description = request.form.get('description')
    
    if not category or not name or not mrp:
        flash("Please fill out all product details.", "danger")
        return redirect(url_for('admin_catalog'))
        
    image_file = request.files.get('image')
    if not image_file or image_file.filename == '':
        flash("Please upload a product image.", "danger")
        return redirect(url_for('admin_catalog'))
        
    image_url = upload_image_to_cloudinary(image_file, folder_name="catalog")
    if not image_url:
        flash("Invalid file format or upload failed.", "danger")
        return redirect(url_for('admin_catalog'))

    # Handle multiple gallery images upload
    gallery_files = request.files.getlist('gallery_images')
    gallery_urls = []
    for g_file in gallery_files:
        if g_file and g_file.filename != '':
            g_url = upload_image_to_cloudinary(g_file, folder_name="catalog")
            if g_url:
                gallery_urls.append(g_url)
    
    gallery_images_str = ",".join(gallery_urls) if gallery_urls else None
        
    try:
        new_prod = CatalogProduct(
            category=category,
            name=name,
            mrp=mrp,
            image_url=image_url,
            in_stock=in_stock,
            short_description=short_description,
            description=description,
            gallery_images=gallery_images_str
        )
        db.session.add(new_prod)
        db.session.commit()
        flash("Product added successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding product: {e}")
        flash("Failed to add the product.", "danger")
        
    return redirect(url_for('admin_catalog'))

@app.route('/admin/catalog/edit/<int:id>', methods=['POST'])
@login_required
def admin_edit_catalog(id):
    """Endpoint for editing a catalog product."""
    prod = CatalogProduct.query.get_or_404(id)
    category = request.form.get('category')
    if category == 'other':
        custom_category = request.form.get('custom_category')
        if custom_category:
            category = custom_category.strip().lower().replace(' ', '-')
    
    if category:
        prod.category = category
        
    prod.name = request.form.get('name')
    prod.mrp = request.form.get('mrp')
    prod.in_stock = request.form.get('in_stock') == 'on'
    prod.short_description = request.form.get('short_description')
    prod.description = request.form.get('description')
    
    image_file = request.files.get('image')
    if image_file and image_file.filename != '':
        new_image_url = upload_image_to_cloudinary(image_file, folder_name="catalog")
        if new_image_url:
            prod.image_url = new_image_url
        else:
            flash("Invalid file format or upload failed.", "danger")
            return redirect(url_for('admin_catalog'))

    # Handle multiple gallery images upload
    gallery_files = request.files.getlist('gallery_images')
    gallery_urls = []
    has_new_gallery = False
    for g_file in gallery_files:
        if g_file and g_file.filename != '':
            has_new_gallery = True
            g_url = upload_image_to_cloudinary(g_file, folder_name="catalog")
            if g_url:
                gallery_urls.append(g_url)
                
    if has_new_gallery:
        prod.gallery_images = ",".join(gallery_urls) if gallery_urls else None
            
    try:
        db.session.commit()
        flash("Product updated successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating product: {e}")
        flash("Failed to update the product.", "danger")
        
    return redirect(url_for('admin_catalog'))

@app.route('/admin/catalog/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_catalog(id):
    """Endpoint for deleting a catalog product."""
    prod = CatalogProduct.query.get_or_404(id)
    try:
        db.session.delete(prod)
        db.session.commit()
        flash("Product deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting product: {e}")
        flash("Failed to delete the product.", "danger")
    return redirect(url_for('admin_catalog'))

@app.route('/admin/gallery')
@login_required
def admin_gallery():
    """Displays the gallery dashboard."""
    try:
        images = GalleryImage.query.order_by(GalleryImage.created_at.desc()).all()
        return render_template('admin/gallery.html', images=images)
    except Exception as e:
        app.logger.error(f"Error fetching admin gallery: {e}")
        return "An error occurred while loading the gallery. Please verify database setup.", 500

@app.route('/admin/gallery/add', methods=['POST'])
@login_required
def admin_add_gallery():
    """Endpoint for adding a new gallery image."""
    category = request.form.get('category')
    if category == 'other':
        custom_category = request.form.get('custom_category')
        if custom_category:
            category = custom_category.strip().lower().replace(' ', '-')
            
    alt_text = request.form.get('alt_text')
    
    if not category:
        flash("Please select or enter a category.", "danger")
        return redirect(url_for('admin_gallery'))
        
    image_file = request.files.get('image')
    if not image_file or image_file.filename == '':
        flash("Please upload an image.", "danger")
        return redirect(url_for('admin_gallery'))
        
    image_url = upload_image_to_cloudinary(image_file, folder_name="gallery")
    if not image_url:
        flash("Invalid file format or upload failed.", "danger")
        return redirect(url_for('admin_gallery'))
        
    try:
        new_img = GalleryImage(
            category=category,
            image_url=image_url,
            alt_text=alt_text
        )
        db.session.add(new_img)
        db.session.commit()
        flash("Gallery image added successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding gallery image: {e}")
        flash("Failed to add the gallery image.", "danger")
        
    return redirect(url_for('admin_gallery'))

@app.route('/admin/gallery/edit/<int:id>', methods=['POST'])
@login_required
def admin_edit_gallery(id):
    """Endpoint for editing a gallery image."""
    img = GalleryImage.query.get_or_404(id)
    category = request.form.get('category')
    if category == 'other':
        custom_category = request.form.get('custom_category')
        if custom_category:
            category = custom_category.strip().lower().replace(' ', '-')
            
    if category:
        img.category = category
        
    img.alt_text = request.form.get('alt_text')
    
    image_file = request.files.get('image')
    if image_file and image_file.filename != '':
        new_image_url = upload_image_to_cloudinary(image_file, folder_name="gallery")
        if new_image_url:
            img.image_url = new_image_url
        else:
            flash("Invalid file format or upload failed.", "danger")
            return redirect(url_for('admin_gallery'))
            
    try:
        db.session.commit()
        flash("Gallery image updated successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating gallery image: {e}")
        flash("Failed to update the gallery image.", "danger")
        
    return redirect(url_for('admin_gallery'))

@app.route('/admin/gallery/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_gallery(id):
    """Endpoint for deleting a gallery image."""
    img = GalleryImage.query.get_or_404(id)
    try:
        db.session.delete(img)
        db.session.commit()
        flash("Gallery image deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting gallery image: {e}")
        flash("Failed to delete the gallery image.", "danger")
    return redirect(url_for('admin_gallery'))

# --- CUSTOM 404 ERROR HANDLER ---

@app.errorhandler(404)
def page_not_found(e):
    """Handles 404 page rendering."""
    return render_template('404.html'), 404

# --- RUN LOCALLY ---
if __name__ == '__main__':
    # Local runtime port config
    app.run(host='0.0.0.0', port=5003, debug=True)
