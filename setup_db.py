import os
from app import app, db
from app import Contact, HeroSlider, CatalogProduct, GalleryImage

def setup_database():
    """
    Initializes the Supabase PostgreSQL database by creating all necessary tables.
    Also runs the seeding logic that's already in app.py during app_context.
    """
    with app.app_context():
        print(f"Connecting to database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("Creating tables...")
        try:
            db.create_all()
            print("Tables created successfully!")
            print("Seeding defaults if empty...")
            # The seeding logic will automatically run in app.py's app_context block
            print("Database setup complete.")
        except Exception as e:
            print(f"Error creating tables: {e}")

if __name__ == "__main__":
    setup_database()
