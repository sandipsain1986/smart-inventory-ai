import sqlite3
import pandas as pd
from datetime import datetime
import os

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DB_PATH = 'data/inventory.db'

# Create data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """Initialize the SQLite database with required tables."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Products Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                supplier TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                minimum_stock INTEGER NOT NULL,
                manufacturing_date TEXT,
                expiry_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sales Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                sale_id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                date TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                revenue REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        ''')
        
        # Forecast History Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forecast_history (
                forecast_id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                forecast_date TEXT NOT NULL,
                forecast_days INTEGER NOT NULL,
                predicted_demand REAL NOT NULL,
                actual_demand REAL,
                accuracy REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Load sample data if tables are empty
        _load_sample_data()
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")

# ============================================================================
# SAMPLE DATA LOADING
# ============================================================================

def _load_sample_data():
    """Load sample data into the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if products table is empty
        cursor.execute('SELECT COUNT(*) FROM products')
        if cursor.fetchone()[0] == 0:
            # Sample products
            products = [
                ('P001', 'Dell Laptop', 'Electronics', 'TechCorp', 999.99, 45, 10, '2023-01-15', '2025-01-15'),
                ('P002', 'iPhone 14', 'Electronics', 'AppleTech', 899.99, 30, 8, '2023-02-01', '2025-02-01'),
                ('P003', 'Samsung TV', 'Electronics', 'SamsungInt', 499.99, 20, 5, '2023-03-10', '2025-03-10'),
                ('P004', 'Organic Rice', 'Grocery', 'GreenFarm', 12.99, 500, 100, '2024-01-01', '2025-01-01'),
                ('P005', 'Whole Wheat Flour', 'Grocery', 'PureGrain', 8.99, 300, 50, '2024-02-01', '2025-02-01'),
                ('P006', 'Coffee Beans', 'Grocery', 'BrewMaster', 15.99, 200, 30, '2024-01-15', '2024-12-15'),
                ('P007', 'Blue Jeans', 'Fashion', 'DenimCo', 59.99, 150, 20, '2024-01-01', '2026-01-01'),
                ('P008', 'Cotton T-Shirt', 'Fashion', 'ComfortWear', 19.99, 300, 50, '2024-02-01', '2026-02-01'),
                ('P009', 'Running Shoes', 'Fashion', 'AthleteFit', 89.99, 80, 15, '2024-01-10', '2026-01-10'),
                ('P010', 'Microwave Oven', 'Home Appliances', 'CookSmart', 199.99, 25, 5, '2023-06-01', '2025-06-01'),
                ('P011', 'Washing Machine', 'Home Appliances', 'CleanTech', 499.99, 12, 3, '2023-05-15', '2025-05-15'),
                ('P012', 'Air Conditioner', 'Home Appliances', 'CoolComfort', 799.99, 8, 2, '2023-07-01', '2025-07-01'),
            ]
            
            for product in products:
                cursor.execute('''
                    INSERT INTO products 
                    (product_id, name, category, supplier, price, quantity, minimum_stock, manufacturing_date, expiry_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', product)
            
            conn.commit()
        
        # Check if sales table is empty
        cursor.execute('SELECT COUNT(*) FROM sales')
        if cursor.fetchone()[0] == 0:
            # Generate 6 months of sample sales data
            import random
            from datetime import datetime, timedelta
            
            sales_data = []
            sale_id = 1001
            product_ids = ['P001', 'P002', 'P003', 'P004', 'P005', 'P006', 'P007', 'P008', 'P009', 'P010', 'P011', 'P012']
            
            start_date = datetime.now() - timedelta(days=180)
            
            for i in range(180):
                current_date = start_date + timedelta(days=i)
                
                # Generate 2-5 sales per day
                num_sales = random.randint(2, 5)
                for _ in range(num_sales):
                    product_id = random.choice(product_ids)
                    
                    # Get product price
                    cursor.execute('SELECT price FROM products WHERE product_id = ?', (product_id,))
                    price_result = cursor.fetchone()
                    price = price_result[0] if price_result else 100
                    
                    quantity = random.randint(1, 10)
                    revenue = quantity * price
                    
                    sales_data.append((
                        f'S{sale_id}',
                        product_id,
                        current_date.strftime('%Y-%m-%d'),
                        quantity,
                        revenue
                    ))
                    sale_id += 1
            
            for sale in sales_data:
                cursor.execute('''
                    INSERT INTO sales
                    (sale_id, product_id, date, quantity, revenue)
                    VALUES (?, ?, ?, ?, ?)
                ''', sale)
            
            conn.commit()
        
        conn.close()
    
    except Exception as e:
        print(f"Error loading sample data: {str(e)}")

# ============================================================================
# PRODUCT OPERATIONS
# ============================================================================

def add_product(name, category, supplier, price, quantity, min_stock, mfg_date, exp_date):
    """Add a new product to the inventory."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Generate product ID
        cursor.execute('SELECT MAX(product_id) FROM products')
        last_id = cursor.fetchone()[0]
        
        if last_id:
            new_id = f"P{int(last_id[1:]) + 1:03d}"
        else:
            new_id = "P001"
        
        cursor.execute('''
            INSERT INTO products
            (product_id, name, category, supplier, price, quantity, minimum_stock, manufacturing_date, expiry_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (new_id, name, category, supplier, price, quantity, min_stock, mfg_date, exp_date))
        
        conn.commit()
        conn.close()
        
        return new_id
    
    except Exception as e:
        print(f"Error adding product: {str(e)}")
        return None

def get_all_products():
    """Get all products from the inventory."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM products ORDER BY name')
        products = cursor.fetchall()
        
        conn.close()
        return products
    
    except Exception as e:
        print(f"Error fetching products: {str(e)}")
        return []

def get_product_by_id(product_id):
    """Get a specific product by ID."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM products WHERE product_id = ?', (product_id,))
        product = cursor.fetchone()
        
        conn.close()
        return product
    
    except Exception as e:
        print(f"Error fetching product: {str(e)}")
        return None

def update_product(product_id, **kwargs):
    """Update product information."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Build update query
        allowed_fields = ['name', 'category', 'supplier', 'price', 'quantity', 'minimum_stock', 'manufacturing_date', 'expiry_date']
        update_fields = [f"{k} = ?" for k in kwargs.keys() if k in allowed_fields]
        
        if not update_fields:
            return False
        
        values = [kwargs[k] for k in kwargs.keys() if k in allowed_fields]
        values.append(product_id)
        
        query = f"UPDATE products SET updated_at = CURRENT_TIMESTAMP, {', '.join(update_fields)} WHERE product_id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        print(f"Error updating product: {str(e)}")
        return False

def delete_product(product_id):
    """Delete a product from the inventory."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM products WHERE product_id = ?', (product_id,))
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        print(f"Error deleting product: {str(e)}")
        return False

# ============================================================================
# SALES OPERATIONS
# ============================================================================

def add_sale(product_id, date, quantity, revenue):
    """Record a sales transaction."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Generate sale ID
        cursor.execute('SELECT MAX(sale_id) FROM sales')
        last_id = cursor.fetchone()[0]
        
        if last_id:
            new_id = f"S{int(last_id[1:]) + 1}"
        else:
            new_id = "S1001"
        
        cursor.execute('''
            INSERT INTO sales
            (sale_id, product_id, date, quantity, revenue)
            VALUES (?, ?, ?, ?, ?)
        ''', (new_id, product_id, date, quantity, revenue))
        
        # Update product quantity
        cursor.execute('SELECT quantity FROM products WHERE product_id = ?', (product_id,))
        current_qty = cursor.fetchone()[0]
        new_qty = max(0, current_qty - quantity)
        
        cursor.execute('UPDATE products SET quantity = ? WHERE product_id = ?', (new_qty, product_id))
        
        conn.commit()
        conn.close()
        
        return new_id
    
    except Exception as e:
        print(f"Error adding sale: {str(e)}")
        return None

def get_sales_history(product_id=None, days=None):
    """Get sales history with optional filtering."""
    try:
        conn = sqlite3.connect(DB_PATH)
        
        if product_id and days:
            query = f"""
                SELECT * FROM sales 
                WHERE product_id = ? 
                AND date >= date('now', '-{days} days')
                ORDER BY date DESC
            """
            df = pd.read_sql_query(query, conn, params=(product_id,))
        elif product_id:
            query = "SELECT * FROM sales WHERE product_id = ? ORDER BY date DESC"
            df = pd.read_sql_query(query, conn, params=(product_id,))
        elif days:
            query = f"SELECT * FROM sales WHERE date >= date('now', '-{days} days') ORDER BY date DESC"
            df = pd.read_sql_query(query, conn)
        else:
            query = "SELECT * FROM sales ORDER BY date DESC"
            df = pd.read_sql_query(query, conn)
        
        conn.close()
        return df
    
    except Exception as e:
        print(f"Error fetching sales: {str(e)}")
        return pd.DataFrame()

# ============================================================================
# FORECAST OPERATIONS
# ============================================================================

def add_forecast(product_id, forecast_days, predicted_demand):
    """Store forecast in database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Generate forecast ID
        cursor.execute('SELECT MAX(forecast_id) FROM forecast_history')
        last_id = cursor.fetchone()[0]
        
        if last_id:
            new_id = f"F{int(last_id[1:]) + 1}"
        else:
            new_id = "F1001"
        
        cursor.execute('''
            INSERT INTO forecast_history
            (forecast_id, product_id, forecast_date, forecast_days, predicted_demand)
            VALUES (?, ?, CURRENT_DATE, ?, ?)
        ''', (new_id, product_id, forecast_days, predicted_demand))
        
        conn.commit()
        conn.close()
        
        return new_id
    
    except Exception as e:
        print(f"Error adding forecast: {str(e)}")
        return None

# ============================================================================
# ANALYTICS QUERIES
# ============================================================================

def get_inventory_value():
    """Calculate total inventory value."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT SUM(price * quantity) FROM products')
        result = cursor.fetchone()[0]
        
        conn.close()
        return result or 0.0
    
    except Exception as e:
        print(f"Error calculating inventory value: {str(e)}")
        return 0.0

def get_low_stock_products():
    """Get products that are below minimum stock level."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM products WHERE quantity <= minimum_stock ORDER BY quantity')
        products = cursor.fetchall()
        
        conn.close()
        return products
    
    except Exception as e:
        print(f"Error fetching low stock products: {str(e)}")
        return []

def get_expiring_products(days=30):
    """Get products expiring within specified days."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT * FROM products 
            WHERE expiry_date IS NOT NULL 
            AND expiry_date <= date('now', '+{days} days')
            AND expiry_date >= date('now')
            ORDER BY expiry_date
        """)
        products = cursor.fetchall()
        
        conn.close()
        return products
    
    except Exception as e:
        print(f"Error fetching expiring products: {str(e)}")
        return []

def get_products_by_category(category):
    """Get all products in a specific category."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM products WHERE category = ? ORDER BY name', (category,))
        products = cursor.fetchall()
        
        conn.close()
        return products
    
    except Exception as e:
        print(f"Error fetching products by category: {str(e)}")
        return []

def get_categories():
    """Get all unique product categories."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT category FROM products ORDER BY category')
        categories = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return categories
    
    except Exception as e:
        print(f"Error fetching categories: {str(e)}")
        return []
