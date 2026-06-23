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
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategories.id', ondelete='SET NULL'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    mrp = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    in_stock = db.Column(db.Boolean, default=True, nullable=False)
    short_description = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    gallery_images = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    category_rel = db.relationship('Category', backref='catalog_products', lazy=True)
    subcategory_rel = db.relationship('Subcategory', backref='catalog_products', lazy=True)

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

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    short_description = db.Column(db.Text, nullable=True)
    page_link = db.Column(db.String(255), nullable=True)
    bg_color = db.Column(db.String(50), default='#b0a483')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    subcategories = db.relationship('Subcategory', backref='category', lazy=True, cascade="all, delete-orphan", order_by="Subcategory.position")

    def __repr__(self):
        return f"<Category {self.name}>"

class Subcategory(db.Model):
    __tablename__ = 'subcategories'
    
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    page_link = db.Column(db.String(255), nullable=True)
    position = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<Subcategory {self.name}>"

if os.getenv('FLASK_ENV') != 'production':
    with app.app_context():
        db.create_all()

        # Ensure dynamic columns exist in SQLite table
        for col_name, col_type in [("gallery_images", "TEXT"), ("category_id", "INTEGER"), ("subcategory_id", "INTEGER")]:
            try:
                db.session.execute(db.text(f"SELECT {col_name} FROM catalog_products LIMIT 1"))
            except Exception:
                db.session.rollback()
                try:
                    db.session.execute(db.text(f"ALTER TABLE catalog_products ADD COLUMN {col_name} {col_type}"))
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()

        # Ensure position column exists in subcategories table
        try:
            db.session.execute(db.text("SELECT position FROM subcategories LIMIT 1"))
        except Exception:
            db.session.rollback()
            try:
                db.session.execute(db.text("ALTER TABLE subcategories ADD COLUMN position INTEGER DEFAULT 0"))
                db.session.commit()
            except Exception as e:
                db.session.rollback()

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
                db.session.add(HeroSlider(**slide_data))
            db.session.commit()

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
                            db.session.add(GalleryImage(
                                category=filter_class,
                                image_url=image_url,
                                alt_text=alt_text
                            ))
            db.session.commit()

        if Category.query.count() == 0:
            default_categories = [
                {
                    "name": "Living Room",
                    "image_url": "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Elegant luxury living spaces",
                    "page_link": "/shop",
                    "bg_color": "#b0a483",
                    "subcategories": ["Sofas", "Recliners", "Sofa cum Beds", "Lounge Chairs", "Storage"]
                },
                {
                    "name": "Bedroom",
                    "image_url": "https://images.unsplash.com/photo-1616594039964-ae9021a400a0?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Cozy modern bedroom designs",
                    "page_link": "/shop",
                    "bg_color": "#f4bcae",
                    "subcategories": ["Beds", "Modular Beds", "Wardrobes", "Night Stands", "Bedroom Sets"]
                },
                {
                    "name": "Dining Room",
                    "image_url": "https://images.unsplash.com/photo-1615066390971-03e4e1c36ddf?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Luxury dining room tables and chairs",
                    "page_link": "/shop",
                    "bg_color": "#b9c8df",
                    "subcategories": ["Dining Sets", "Dining Tables", "Dining Chairs", "Dining Benches", "Serving Carts"]
                },
                {
                    "name": "Decor & Lighting",
                    "image_url": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Sophisticated home decorations and lighting",
                    "page_link": "/shop",
                    "bg_color": "#e6d5b3",
                    "subcategories": ["Wall Decor", "Home Accent", "Garden", "Lighting", "Home Fragrances"]
                }
            ]
            for cat_data in default_categories:
                subcategories_names = cat_data.pop("subcategories")
                cat = Category(**cat_data)
                db.session.add(cat)
                db.session.flush()
                for sub_name in subcategories_names:
                    sub = Subcategory(name=sub_name, category_id=cat.id, page_link="#")
                    db.session.add(sub)
            db.session.commit()

        # Seed products (2 per subcategory)
        if CatalogProduct.query.filter(CatalogProduct.category_id != None).count() == 0:
            # Delete old products if any
            CatalogProduct.query.delete()
            db.session.commit()
            
            # Map subcategories
            all_categories = Category.query.all()
            cat_map = {c.name: c for c in all_categories}
            
            # Define 40 products matching Category -> Subcategory
            products_seed_data = [
                # --- LIVING ROOM ---
                {
                    "cat_name": "Living Room", "sub_name": "Sofas",
                    "name": "Chesterfield Velvet Sofa", "mrp": "45,000",
                    "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Classic Chesterfield sofa in plush velvet upholstery.",
                    "description": "Indulge in royal comfort with our Chesterfield Velvet Sofa. It features deep button tufting, elegant scrolled arms, and a sturdy hardwood frame. Upholstered in premium, easy-to-clean velvet fabric, this sofa serves as a majestic statement piece for any traditional or modern living room."
                },
                {
                    "cat_name": "Living Room", "sub_name": "Sofas",
                    "name": "Modern L-Shape Sectional", "mrp": "65,000",
                    "image_url": "https://images.unsplash.com/photo-1484101403633-562f891dc89a?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Spacious L-shape sectional sofa, perfect for family lounges.",
                    "description": "Maximize seating and style with the Modern L-Shape Sectional. Featuring modular pieces, premium foam cushioning, and durable woven fabric, it easily accommodates your family and guests. Its clean lines and low-profile design bring a chic mid-century charm to your home."
                },
                {
                    "cat_name": "Living Room", "sub_name": "Recliners",
                    "name": "Classic Leather Recliner", "mrp": "24,000",
                    "image_url": "https://images.unsplash.com/photo-1592078615290-033ee584e267?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Ergonomic leather recliner with smooth push-back mechanism.",
                    "description": "Relax in style after a long day. Our Classic Leather Recliner features high-grade leatherette upholstery, overstuffed armrests, and an adjustable leg rest. The heavy-duty steel mechanism ensures smooth transition from upright to fully reclined position."
                },
                {
                    "cat_name": "Living Room", "sub_name": "Recliners",
                    "name": "Power Motion Lounge Recliner", "mrp": "32,000",
                    "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Smart power recliner with built-in USB charging port.",
                    "description": "Experience luxury at the press of a button. Upholstered in breathable performance fabric, this modern power recliner lets you customize your comfort angle effortlessly while charging your devices."
                },
                {
                    "cat_name": "Living Room", "sub_name": "Sofa cum Beds",
                    "name": "Convertible Futon Bed", "mrp": "18,000",
                    "image_url": "https://images.unsplash.com/photo-1540518614846-7eded433c457?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Space-saving three-seater futon that converts to a cozy bed.",
                    "description": "Ideal for compact apartments and guest rooms. This futon features a click-clack mechanism for instant conversion. Crafted with solid wood legs and dense foam padding for comfortable sitting or sleeping."
                },
                {
                    "cat_name": "Living Room", "sub_name": "Sofa cum Beds",
                    "name": "Pull-Out Luxury Daybed", "mrp": "28,000",
                    "image_url": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Premium pull-out daybed with integrated trundle storage.",
                    "description": "A stylish sofa by day, and a spacious double bed by night. Includes a smooth pull-out underbed mechanism and storage drawers for bedding essentials."
                },
                {
                    "cat_name": "Living Room", "sub_name": "Lounge Chairs",
                    "name": "Velvet Accent Chair", "mrp": "12,500",
                    "image_url": "https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Glamorous accent chair with golden metal legs.",
                    "description": "Add a touch of elegance to any corner. This velvet upholstered accent chair features a curved shell back design and high-density foam padding for superb comfort."
                },
                {
                    "cat_name": "Living Room", "sub_name": "Lounge Chairs",
                    "name": "Modernist Wingback Chair", "mrp": "15,000",
                    "image_url": "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Contemporary interpretation of the classic wingback chair.",
                    "description": "Combining heritage design with modern minimalism, this lounge chair is wrapped in a textured linen-blend fabric and supported by sleek black tapered timber legs."
                },
                {
                    "cat_name": "Living Room", "sub_name": "Storage",
                    "name": "Oak Wood Sideboard", "mrp": "22,000",
                    "image_url": "https://images.unsplash.com/photo-1595428774223-ef52624120d2?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Solid oak sideboard with spacious cabinets and drawers.",
                    "description": "An elegant storage solution for dining or living spaces. Features soft-closing hinges, adjustable internal shelves, and a polished natural oak finish."
                },
                {
                    "cat_name": "Living Room", "sub_name": "Storage",
                    "name": "Minimalist TV Console", "mrp": "16,500",
                    "image_url": "https://images.unsplash.com/photo-1601887389937-0b02c26b6c3c?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Sleek low-profile media console with cable management ports.",
                    "description": "Organize your media devices with ease. Offers open shelving for consoles, sliding slatted doors for hidden storage, and pre-drilled holes for wires."
                },
                # --- BEDROOM ---
                {
                    "cat_name": "Bedroom", "sub_name": "Beds",
                    "name": "Tufted King Size Bed", "mrp": "38,000",
                    "image_url": "https://images.unsplash.com/photo-1505693395321-883724634266?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Luxurious king size bed frame with deep tufted headboard.",
                    "description": "Sleep like royalty. This premium bed frame features a tall, padded headboard in soft fabric, supported by a heavy-duty slatted wood base that eliminates the need for a box spring."
                },
                {
                    "cat_name": "Bedroom", "sub_name": "Beds",
                    "name": "Solid Teak Wood Bed", "mrp": "42,000",
                    "image_url": "https://images.unsplash.com/photo-1578894381163-e72c17f2d45f?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Durable teak bed with rich wood grain pattern.",
                    "description": "Crafted from carefully selected seasoned teak wood, this bed frame offers timeless appeal and lifelong durability. Sealed with a premium matte polish."
                },
                {
                    "cat_name": "Bedroom", "sub_name": "Modular Beds",
                    "name": "Hydraulic Storage Bed", "mrp": "48,000",
                    "image_url": "https://images.unsplash.com/photo-1616594039964-ae9021a400a0?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Smart bed with easy-lift hydraulic underbed storage.",
                    "description": "Declutter your bedroom effortlessly. The lift mechanism reveals a massive dust-proof storage compartment beneath the mattress, perfect for extra blankets, cushions, and luggage."
                },
                {
                    "cat_name": "Bedroom", "sub_name": "Modular Beds",
                    "name": "Space-Saving Floating Bed", "mrp": "35,000",
                    "image_url": "https://images.unsplash.com/photo-1617806118233-18e1db207f62?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Modern floating platform bed with underbed LED channels.",
                    "description": "Create a futuristic and airy look in your bedroom. Upholstered in premium linen-look fabric with hidden support legs that create the illusion of floating."
                },
                {
                    "cat_name": "Bedroom", "sub_name": "Wardrobes",
                    "name": "3-Door Sliding Wardrobe", "mrp": "28,500",
                    "image_url": "https://images.unsplash.com/photo-1558882224-cca166733360?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Elegant wardrobe with sliding doors and a full-length mirror.",
                    "description": "Optimize space with smooth sliding doors. This wardrobe features hanger rails, multiple shelves, lockable drawers, and a built-in dressing mirror."
                },
                {
                    "cat_name": "Bedroom", "sub_name": "Wardrobes",
                    "name": "Luxury Walk-In Wardrobe Unit", "mrp": "55,000",
                    "image_url": "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Open-concept modular walk-in wardrobe system.",
                    "description": "Bespoke storage layout featuring warm integrated LED shelf lighting, high-quality laminate shelves, soft-closing drawers, and elegant metal racks."
                },
                {
                    "cat_name": "Bedroom", "sub_name": "Night Stands",
                    "name": "Floating Oak Bedside Table", "mrp": "4,500",
                    "image_url": "https://images.unsplash.com/photo-1532372320572-cda25653a26d?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Wall-mounted single drawer bedside unit.",
                    "description": "A sleek, wall-mounted nightstand that keeps floor space clear. Features a smooth drawer for personal items and a top shelf for books or a lamp."
                },
                {
                    "cat_name": "Bedroom", "sub_name": "Night Stands",
                    "name": "Mid-Century Modern Nightstand", "mrp": "6,000",
                    "image_url": "https://images.unsplash.com/photo-1618220179428-22790b461013?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Bedside table with open shelf and drawer on tapered legs.",
                    "description": "Classic mid-century silhouette crafted in warm oak tones, perfect for lamps, chargers, and nighttime reads."
                },
                {
                    "cat_name": "Bedroom", "sub_name": "Bedroom Sets",
                    "name": "Master Bedroom Premium Set", "mrp": "95,000",
                    "image_url": "https://images.unsplash.com/photo-1616594039964-ae9021a400a0?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Complete master bedroom set: Bed, Wardrobe, & 2 Nightstands.",
                    "description": "Coordinated luxury for your master bedroom. Includes a premium velvet king bed, a 3-door sliding wardrobe, and matching dual nightstands for a cohesive aesthetic."
                },
                {
                    "cat_name": "Bedroom", "sub_name": "Bedroom Sets",
                    "name": "Minimalist Zen Suite", "mrp": "82,000",
                    "image_url": "https://images.unsplash.com/photo-1540518614846-7eded433c457?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Low-profile platform bed set with matching chest of drawers.",
                    "description": "Embody peace and simplicity. Features a low platform bed, 2 low nightstands, and a 5-drawer storage chest in a light birch wood finish."
                },
                # --- DINING ROOM ---
                {
                    "cat_name": "Dining Room", "sub_name": "Dining Sets",
                    "name": "6-Seater Marble Dining Set", "mrp": "72,000",
                    "image_url": "https://images.unsplash.com/photo-1615066390971-03e4e1c36ddf?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Luxurious dining table with 6 velvet upholstered chairs.",
                    "description": "Elevate meal times. Features a heavy natural marble dining table with custom brass-accented chairs, providing unparalleled comfort and class."
                },
                {
                    "cat_name": "Dining Room", "sub_name": "Dining Sets",
                    "name": "Modern Wooden 4-Seater Set", "mrp": "45,000",
                    "image_url": "https://images.unsplash.com/photo-1577140917170-285929fb55b7?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Compact solid ash wood dining set for cozy dining spaces.",
                    "description": "Includes a solid ash wood table and four matching chairs with cushioned fabric seats, designed with clean Scandinavian lines."
                },
                {
                    "cat_name": "Dining Room", "sub_name": "Dining Tables",
                    "name": "Bespoke Walnut Dining Table", "mrp": "38,000",
                    "image_url": "https://images.unsplash.com/photo-1604014237800-1c9102c219da?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Handcrafted live-edge American walnut table.",
                    "description": "Showcasing the natural beauty of solid walnut wood with beautiful grains, supported by raw industrial black iron U-legs."
                },
                {
                    "cat_name": "Dining Room", "sub_name": "Dining Tables",
                    "name": "Polished Marble Top Table", "mrp": "52,000",
                    "image_url": "https://images.unsplash.com/photo-1615066390971-03e4e1c36ddf?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Premium white marble dining table with chrome frame.",
                    "description": "Featuring a highly polished scratch-resistant marble top with a heavy chrome steel frame, this table adds an elegant shine to any dining hall."
                },
                {
                    "cat_name": "Dining Room", "sub_name": "Dining Chairs",
                    "name": "Upholstered Dining Chair", "mrp": "5,500",
                    "image_url": "https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Comfortable tufted dining chair with high backrest.",
                    "description": "Padded with high-resilience foam and upholstered in stain-resistant linen fabric. Features solid dark-oak legs."
                },
                {
                    "cat_name": "Dining Room", "sub_name": "Dining Chairs",
                    "name": "Nordic Wooden Dining Chair", "mrp": "4,200",
                    "image_url": "https://images.unsplash.com/photo-1503602642458-232111445657?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Minimalist wooden dining chair with curved back support.",
                    "description": "Crafted in solid beech wood, this lightweight chair combines ergonomic comfort with a sleek classic look."
                },
                {
                    "cat_name": "Dining Room", "sub_name": "Dining Benches",
                    "name": "Live Edge Oak Bench", "mrp": "12,000",
                    "image_url": "https://images.unsplash.com/photo-1595428774223-ef52624120d2?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Rustic live-edge oak dining bench for informal seating.",
                    "description": "A stylish alternative to dining chairs. Made of natural oak slab with metal legs, comfortably seating 2-3 adults."
                },
                {
                    "cat_name": "Dining Room", "sub_name": "Dining Benches",
                    "name": "Industrial Metal & Wood Bench", "mrp": "9,500",
                    "image_url": "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Modern industrial bench in pine wood and dark iron frame.",
                    "description": "Versatile bench that fits perfectly in dining areas, entryways, or hallway corners. Made with weather-resistant coat."
                },
                {
                    "cat_name": "Dining Room", "sub_name": "Serving Carts",
                    "name": "Gold Trimmed Bar Cart", "mrp": "14,500",
                    "image_url": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Glamorous mobile bar cart with glass shelves.",
                    "description": "Includes handles, lockable caster wheels, and safety rails. Perfect for hosting dinners and serving cocktails."
                },
                {
                    "cat_name": "Dining Room", "sub_name": "Serving Carts",
                    "name": "Industrial Wood Serving Trolley", "mrp": "11,000",
                    "image_url": "https://images.unsplash.com/photo-1604014237800-1c9102c219da?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Rustic wooden utility serving cart on steel wheels.",
                    "description": "Features solid pine wood shelves and a durable iron frame, including dedicated wine bottle holders."
                },
                # --- DECOR & LIGHTING ---
                {
                    "cat_name": "Decor & Lighting", "sub_name": "Wall Decor",
                    "name": "Abstract Metal Wall Art", "mrp": "4,800",
                    "image_url": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Hand-painted abstract geometric metal wall sculpture.",
                    "description": "A striking modern focal point. Made of rust-proof iron sheets with dynamic hand-finished gold and grey colors."
                },
                {
                    "cat_name": "Decor & Lighting", "sub_name": "Wall Decor",
                    "name": "Asymmetrical Brass Mirror", "mrp": "6,500",
                    "image_url": "https://images.unsplash.com/photo-1618220179428-22790b461013?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Stunning asymmetrical statement wall mirror with a brass frame.",
                    "description": "Create an artistic illusion of space. Features premium brass rim detailing, perfect for halls or powder rooms."
                },
                {
                    "cat_name": "Decor & Lighting", "sub_name": "Home Accent",
                    "name": "Handcrafted Ceramic Vase", "mrp": "2,400",
                    "image_url": "https://images.unsplash.com/photo-1578500494198-246f612d3b3d?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Textured ceramic vase in neutral beige tone.",
                    "description": "Featuring a rustic hand-thrown texture, ideal for displaying pampas grass, dried flowers, or as a standalone centerpiece."
                },
                {
                    "cat_name": "Decor & Lighting", "sub_name": "Home Accent",
                    "name": "Sculptural Marble Tray", "mrp": "3,200",
                    "image_url": "https://images.unsplash.com/photo-1612196808214-b8e1d6145a8c?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Elegant white marble vanity and display tray.",
                    "description": "Crafted from solid natural marble with gray veining. Ideal for displaying perfumes, jewelry, or holding keys on your entryway console."
                },
                {
                    "cat_name": "Decor & Lighting", "sub_name": "Garden",
                    "name": "Minimalist Metal Planter Stand", "mrp": "1,800",
                    "image_url": "https://images.unsplash.com/photo-1485955900006-10f4d324d411?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Powder-coated indoor/outdoor metal plant stand.",
                    "description": "Showcase your houseplants beautifully. Features lightweight but sturdy construction with a removable pot."
                },
                {
                    "cat_name": "Decor & Lighting", "sub_name": "Garden",
                    "name": "Self-Watering Ceramic Pot Set", "mrp": "2,200",
                    "image_url": "https://images.unsplash.com/photo-1485955900006-10f4d324d411?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Three ceramic flower pots with built-in drainage trays.",
                    "description": "Modern round glazed ceramic pots in assorted pastel shades, perfect for succulents, herbs, or indoor ferns."
                },
                {
                    "cat_name": "Decor & Lighting", "sub_name": "Lighting",
                    "name": "Minimalist Brass Table Lamp", "mrp": "3,800",
                    "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Golden brass table lamp with structured linen shade.",
                    "description": "Provides warm, diffused lighting for cozy bedrooms or workspaces. Includes energy-efficient warm LED bulb."
                },
                {
                    "cat_name": "Decor & Lighting", "sub_name": "Lighting",
                    "name": "Nordic Pendant Ceiling Light", "mrp": "8,500",
                    "image_url": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Contemporary multi-light pendant ceiling lamp.",
                    "description": "Featuring elegant matte wood and metal details, this adjustable pendant lamp is a perfect centerpiece for dining areas."
                },
                {
                    "cat_name": "Decor & Lighting", "sub_name": "Home Fragrances",
                    "name": "Premium Scented Soy Candle Set", "mrp": "1,200",
                    "image_url": "https://images.unsplash.com/photo-1603006905003-be475563bc59?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Trio of lavender, jasmine, and vanilla soy candles.",
                    "description": "Eco-friendly natural soy wax candles hand-poured in beautiful glass jars, offering up to 30 hours of relaxing burn time each."
                },
                {
                    "cat_name": "Decor & Lighting", "sub_name": "Home Fragrances",
                    "name": "Luxury Reed Diffuser", "mrp": "1,800",
                    "image_url": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=800&q=80",
                    "short_description": "Amber wood and bergamot oil reed diffuser.",
                    "description": "Provides long-lasting, flame-free home fragrance for entryways, living rooms, or bathrooms. Includes natural rattan sticks."
                }
            ]
            
            for item in products_seed_data:
                cat_obj = cat_map.get(item["cat_name"])
                if not cat_obj:
                    continue
                sub_obj = next((s for s in cat_obj.subcategories if s.name == item["sub_name"]), None)
                if not sub_obj:
                    continue
                
                new_prod = CatalogProduct(
                    category=item["cat_name"].lower().replace(" & ", "-").replace(" ", "-"),
                    category_id=cat_obj.id,
                    subcategory_id=sub_obj.id,
                    name=item["name"],
                    mrp=item["mrp"],
                    image_url=item["image_url"],
                    in_stock=True,
                    short_description=item["short_description"],
                    description=item["description"],
                    gallery_images=None
                )
                db.session.add(new_prod)
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
    
    # Get dynamic categories for home page with pagination
    page = request.args.get('page', 1, type=int)
    home_categories_pagination = Category.query.order_by(Category.created_at.asc()).paginate(page=page, per_page=9, error_out=False)
    home_categories = home_categories_pagination.items
    
    return render_template('pages/index.html', sliders=sliders, catalog_products=catalog_products, unique_categories=unique_categories, home_categories=home_categories, home_categories_pagination=home_categories_pagination)

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
    """Renders the Shop Page with all products."""
    page = request.args.get('page', 1, type=int)
    categories = Category.query.order_by(Category.created_at.asc()).all()
    
    products_pagination = CatalogProduct.query.order_by(CatalogProduct.created_at.desc()).paginate(page=page, per_page=9, error_out=False)
    products = products_pagination.items
    
    return render_template(
        'pages/shop.html', 
        categories=categories, 
        products=products, 
        products_pagination=products_pagination,
        selected_category=None, 
        selected_subcategory=None
    )

@app.route('/shop/category/<int:category_id>')
def shop_category(category_id):
    """Renders the Shop Page filtered by a specific category."""
    page = request.args.get('page', 1, type=int)
    categories = Category.query.order_by(Category.created_at.asc()).all()
    selected_category = Category.query.get_or_404(category_id)
    
    products_pagination = CatalogProduct.query.filter_by(category_id=category_id).order_by(CatalogProduct.created_at.desc()).paginate(page=page, per_page=9, error_out=False)
    products = products_pagination.items
    
    return render_template(
        'pages/shop.html', 
        categories=categories, 
        products=products, 
        products_pagination=products_pagination,
        selected_category=selected_category, 
        selected_subcategory=None
    )

@app.route('/shop/subcategory/<int:subcategory_id>')
def shop_subcategory(subcategory_id):
    """Renders the Shop Page filtered by a specific subcategory."""
    page = request.args.get('page', 1, type=int)
    categories = Category.query.order_by(Category.created_at.asc()).all()
    selected_subcategory = Subcategory.query.get_or_404(subcategory_id)
    selected_category = selected_subcategory.category
    
    products_pagination = CatalogProduct.query.filter_by(subcategory_id=subcategory_id).order_by(CatalogProduct.created_at.desc()).paginate(page=page, per_page=9, error_out=False)
    products = products_pagination.items
    
    return render_template(
        'pages/shop.html', 
        categories=categories, 
        products=products, 
        products_pagination=products_pagination,
        selected_category=selected_category, 
        selected_subcategory=selected_subcategory
    )

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Renders the Product Detail Page."""
    product = CatalogProduct.query.get_or_404(product_id)
    related_products = CatalogProduct.query.filter(
        CatalogProduct.category_id == product.category_id,
        CatalogProduct.id != product.id
    ).limit(10).all()
    return render_template('pages/product_detail.html', product=product, related_products=related_products)

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
        categories = Category.query.order_by(Category.name.asc()).all()
        return render_template('admin/catalog.html', products=products, categories=categories)
    except Exception as e:
        app.logger.error(f"Error fetching admin catalog: {e}")
        return "An error occurred while loading the catalog. Please verify database setup.", 500

@app.route('/admin/catalog/add', methods=['POST'])
@login_required
def admin_add_catalog():
    """Endpoint for adding a new catalog product."""
    category_id = request.form.get('category_id')
    subcategory_id = request.form.get('subcategory_id')
    
    cat_obj = Category.query.get(category_id) if category_id else None
    if cat_obj:
        category_name = cat_obj.name.lower().replace(" & ", "-").replace(" ", "-")
    else:
        category_name = "other"
            
    name = request.form.get('name')
    mrp = request.form.get('mrp')
    in_stock = request.form.get('in_stock') == 'on'
    short_description = request.form.get('short_description')
    description = request.form.get('description')
    
    if not name or not mrp:
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
            category=category_name,
            category_id=int(category_id) if category_id else None,
            subcategory_id=int(subcategory_id) if subcategory_id else None,
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
    category_id = request.form.get('category_id')
    subcategory_id = request.form.get('subcategory_id')
    
    if category_id:
        prod.category_id = int(category_id)
        cat_obj = Category.query.get(category_id)
        if cat_obj:
            prod.category = cat_obj.name.lower().replace(" & ", "-").replace(" ", "-")
    else:
        prod.category_id = None
        prod.category = "other"
        
    if subcategory_id:
        prod.subcategory_id = int(subcategory_id)
    else:
        prod.subcategory_id = None
        
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

@app.route('/admin/catalog/duplicate/<int:id>', methods=['POST'])
@login_required
def admin_duplicate_catalog(id):
    """Endpoint for duplicating a catalog product."""
    prod = CatalogProduct.query.get_or_404(id)
    try:
        new_prod = CatalogProduct(
            category=prod.category,
            category_id=prod.category_id,
            subcategory_id=prod.subcategory_id,
            name=prod.name + " (Copy)",
            mrp=prod.mrp,
            image_url=prod.image_url,
            in_stock=prod.in_stock,
            short_description=prod.short_description,
            description=prod.description,
            gallery_images=prod.gallery_images
        )
        db.session.add(new_prod)
        db.session.commit()
        flash("Product duplicated successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error duplicating product: {e}")
        flash("Failed to duplicate the product.", "danger")
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

# --- ADMIN CATEGORY ROUTES ---

@app.route('/admin/categories')
@login_required
def admin_categories():
    """Displays the categories dashboard."""
    try:
        categories = Category.query.order_by(Category.created_at.desc()).all()
        return render_template('admin/categories.html', categories=categories)
    except Exception as e:
        app.logger.error(f"Error fetching admin categories: {e}")
        return "An error occurred while loading the categories. Please verify database setup.", 500

@app.route('/admin/categories/add', methods=['POST'])
@login_required
def admin_add_category():
    """Endpoint for adding a new category."""
    name = request.form.get('name')
    bg_color = request.form.get('bg_color')
    subcategories_str = request.form.get('subcategories')
    
    if not name:
        flash("Please fill out the category name.", "danger")
        return redirect(url_for('admin_categories'))
        
    image_file = request.files.get('image')
    if not image_file or image_file.filename == '':
        flash("Please upload a category image.", "danger")
        return redirect(url_for('admin_categories'))
        
    image_url = upload_image_to_cloudinary(image_file, folder_name="categories")
    if not image_url:
        flash("Invalid file format or upload failed.", "danger")
        return redirect(url_for('admin_categories'))
        
    try:
        new_cat = Category(
            name=name,
            image_url=image_url,
            short_description="",
            page_link="",
            bg_color=bg_color or '#b0a483'
        )
        db.session.add(new_cat)
        db.session.flush()
        
        # Automatically set page link based on the generated category ID
        new_cat.page_link = f"/shop/category/{new_cat.id}"
        
        if subcategories_str:
            sub_names = [s.strip() for s in subcategories_str.split(',') if s.strip()]
            for idx, s_name in enumerate(sub_names):
                sub = Subcategory(name=s_name, category_id=new_cat.id, page_link="#", position=idx)
                db.session.add(sub)
                
        db.session.commit()
        flash("Category added successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding category: {e}")
        flash("Failed to add the category.", "danger")
        
    return redirect(url_for('admin_categories'))

@app.route('/admin/categories/edit/<int:id>', methods=['POST'])
@login_required
def admin_edit_category(id):
    """Endpoint for editing a category."""
    cat = Category.query.get_or_404(id)
    cat.name = request.form.get('name')
    cat.short_description = ""
    cat.page_link = f"/shop/category/{cat.id}"
    cat.bg_color = request.form.get('bg_color') or '#b0a483'
    subcategories_str = request.form.get('subcategories')
    
    image_file = request.files.get('image')
    if image_file and image_file.filename != '':
        new_image_url = upload_image_to_cloudinary(image_file, folder_name="categories")
        if new_image_url:
            cat.image_url = new_image_url
        else:
            flash("Invalid file format or upload failed.", "danger")
            return redirect(url_for('admin_categories'))
            
    try:
        # Fetch existing subcategories for this category to update them in place
        existing_subs = {s.name.strip(): s for s in Subcategory.query.filter_by(category_id=cat.id).all()}
        
        # Parse new subcategories list
        new_sub_names = []
        if subcategories_str:
            new_sub_names = [s.strip() for s in subcategories_str.split(',') if s.strip()]
            
        seen_names = set()
        for idx, s_name in enumerate(new_sub_names):
            if s_name in seen_names:
                continue
            seen_names.add(s_name)
            
            if s_name in existing_subs:
                # Update position for existing subcategory (retains original ID and associations)
                sub = existing_subs[s_name]
                sub.position = idx
                existing_subs.pop(s_name)
            else:
                # Add new subcategory
                sub = Subcategory(name=s_name, category_id=cat.id, page_link="#", position=idx)
                db.session.add(sub)
                
        # Delete subcategories that were removed from the list
        for sub_to_delete in existing_subs.values():
            db.session.delete(sub_to_delete)
                
        db.session.commit()
        flash("Category updated successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating category: {e}")
        flash("Failed to update the category.", "danger")
        
    return redirect(url_for('admin_categories'))

@app.route('/admin/categories/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_category(id):
    """Endpoint for deleting a category."""
    cat = Category.query.get_or_404(id)
    try:
        db.session.delete(cat)
        db.session.commit()
        flash("Category deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting category: {e}")
        flash("Failed to delete the category.", "danger")
    return redirect(url_for('admin_categories'))

# --- CUSTOM 404 ERROR HANDLER ---

@app.errorhandler(404)
def page_not_found(e):
    """Handles 404 page rendering."""
    return render_template('404.html'), 404

# --- RUN LOCALLY ---
if __name__ == '__main__':
    # Local runtime port config
    app.run(host='0.0.0.0', port=5003, debug=True)
