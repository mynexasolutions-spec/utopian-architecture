import sqlite3
import os

# Determine database path
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'contacts.db')

def migrate():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if sale_price column already exists
        cursor.execute("PRAGMA table_info(catalog_products)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'sale_price' not in columns:
            cursor.execute('ALTER TABLE catalog_products ADD COLUMN sale_price TEXT;')
            print("Added sale_price column to catalog_products.")

            # Calculate the 40% discount for existing products so they look exactly as they did before
            cursor.execute('SELECT id, mrp FROM catalog_products')
            products = cursor.fetchall()

            for product in products:
                prod_id, mrp_raw = product
                if mrp_raw:
                    try:
                        mrp_val = float(str(mrp_raw).replace('$', '').replace(',', ''))
                        sale_price_val = mrp_val * 0.6
                        sale_price_str = f"{sale_price_val:.2f}".rstrip('0').rstrip('.') # Keep decimals if any, else could format without
                        cursor.execute('UPDATE catalog_products SET sale_price = ? WHERE id = ?', (sale_price_str, prod_id))
                    except ValueError:
                        pass
            
            print("Successfully populated existing products with a 40% discount.")
        else:
            print("Column sale_price already exists.")

        conn.commit()
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
