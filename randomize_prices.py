import sqlite3
import os
import random

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'contacts.db')

def randomize_prices():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT id FROM catalog_products')
        products = cursor.fetchall()

        for product in products:
            prod_id = product[0]
            
            # Generate a random MRP between 1500 and 85000, rounded to nearest 100
            mrp_val = round(random.uniform(1500, 85000) / 100) * 100
            
            # Generate a random discount between 10% and 60%
            discount_pct = random.choice([10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60])
            
            sale_price_val = mrp_val * (1 - (discount_pct / 100.0))
            
            # Format to string without decimals
            mrp_str = f"{mrp_val:.0f}"
            sale_price_str = f"{sale_price_val:.0f}"
            
            cursor.execute('UPDATE catalog_products SET mrp = ?, sale_price = ? WHERE id = ?', (mrp_str, sale_price_str, prod_id))
            print(f"Updated product ID {prod_id}: MRP {mrp_str}, Sale {sale_price_str} ({discount_pct}% OFF)")

        conn.commit()
        print("Successfully updated all product prices with varying discounts!")
    except Exception as e:
        print(f"Error during update: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    randomize_prices()
