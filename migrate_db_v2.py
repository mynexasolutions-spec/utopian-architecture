import sqlite3
import os

db_path = os.path.join('instance', 'contacts.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Check and add short_description
        try:
            cursor.execute('ALTER TABLE catalog_products ADD COLUMN short_description TEXT;')
            print("Added short_description column to catalog_products.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("short_description column already exists.")
            else:
                raise e

        # Check and add description
        try:
            cursor.execute('ALTER TABLE catalog_products ADD COLUMN description TEXT;')
            print("Added description column to catalog_products.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("description column already exists.")
            else:
                raise e

        # Update default seed product descriptions
        updates = {
            "Modern Sofa": (
                "A stylish and comfortable 3-seater sofa with premium fabric upholstery, perfect for modern living rooms.",
                "Elevate your living space with our premium Modern Sofa. Crafted with a solid hardwood frame, high-density foam cushioning, and upholstered in a luxurious, durable fabric, this sofa offers both exceptional comfort and contemporary style. Designed to fit seamlessly into modern apartments or houses, it features clean lines, sleek steel legs, and soft armrests."
            ),
            "Luxury Dining Table": (
                "Elegant 6-seater wooden dining table with a polished marble top and sturdy timber legs.",
                "Host unforgettable dinners with the Luxury Dining Table. Featuring a stunning natural marble top with unique veining patterns and supported by a robust solid oak frame, this table blends strength with sheer elegance. Comfortably seating up to six guests, it serves as a stunning centerpiece for any modern dining area."
            ),
            "Outdoor Pergola": (
                "Weather-resistant wooden outdoor pergola, ideal for gardens, patios, and terrace decks.",
                "Transform your outdoor living area with our custom wooden Pergola. Made from premium, weather-treated teak wood, this pergola provides a perfect balance of shade and sunshine. Whether set up in a garden, by the pool, or on a spacious terrace, it creates a cozy, elegant outdoor retreat perfect for relaxing or entertaining guests."
            ),
            "Minimal Table Lamp": (
                "A sleek, minimalist ceramic table lamp providing warm ambient lighting.",
                "Bring warmth and sophisticated style to your bedside table or desk with the Minimal Table Lamp. Its geometric ceramic base paired with a textured fabric drum shade creates a soft, diffused glow. Equipped with energy-efficient LED compatibility, it features a clean white matte finish that complements any modern minimalist decor."
            ),
            "Luxury Wall Mirror": (
                "A large statement wall mirror with a bespoke brushed brass frame.",
                "Make your rooms feel larger and brighter with this gorgeous Luxury Wall Mirror. Hand-finished with a premium brushed brass frame, its clean round design adds a modern architectural touch to entryways, bedrooms, or living spaces. Featuring distortion-free high-definition glass, it serves as both a functional mirror and a striking piece of wall art."
            ),
            "Decorative Vase Set": (
                "A trio of hand-painted matte ceramic vases in earth tones.",
                "Add an artistic touch to your shelves, console tables, or mantels with the Decorative Vase Set. This collection of three textured ceramic vases features varying heights and organic shapes, finished in a harmonious earthy color palette. Perfect for displaying dry botanicals, pampas grass, or standing alone as modern sculptural accents."
            )
        }

        for prod_name, (short_desc, desc) in updates.items():
            cursor.execute(
                'UPDATE catalog_products SET short_description = ?, description = ? WHERE name = ?',
                (short_desc, desc, prod_name)
            )
            print(f"Updated description fields for product: {prod_name}")

        conn.commit()
        print("Successfully migrated and updated all default product descriptions!")
    except Exception as e:
        print("Migration failed:", e)
    finally:
        conn.close()
else:
    print(f"DB not found at {db_path}, it will be generated with full schema upon app startup.")
