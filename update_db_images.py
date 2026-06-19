import os
from app import app, db, CatalogProduct

with app.app_context():
    products = CatalogProduct.query.all()
    updates = {
        "Modern Sofa": "/static/img/products/sectional2.webp",
        "Luxury Dining Table": "/static/img/products/Dining.webp",
        "Outdoor Pergola": "/static/img/products/Outdoor_Pergola.webp",
        "Minimal Table Lamp": "/static/img/products/Minimal.webp",
        "Luxury Wall Mirror": "/static/img/products/Luxury_Wall_Mirror.webp",
        "Decorative Vase Set": "/static/img/products/Decorative.webp"
    }

    for prod in products:
        if prod.name in updates:
            prod.image_url = updates[prod.name]
    
    db.session.commit()
    print("Database updated successfully.")
