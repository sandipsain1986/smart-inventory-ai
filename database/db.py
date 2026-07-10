import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# Database path
DB_PATH = "data/inventory.db"

def init_db():
    """Initialize database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            supplier TEXT,
            price REAL,
            quantity INTEGER DEFAULT 0,
            min_stock INTEGER DEFAULT 0,
            mfg_date TEXT,
            exp_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Sales table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            quantity INTEGER,
            revenue REAL,
            date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    
    conn.commit()
    conn.close()

def get_all_products():
    """Get all products from database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY id DESC")
        products = cursor.fetchall()
        conn.close()
        return products
    except:
        return []

def get_product_by_id(product_id):
    """Get product by ID."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        conn.close()
        return product
    except:
        return None

def add_product(name, category, supplier, price, quantity, min_stock, mfg_date=None, exp_date=None):
    """Add new product to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, category, supplier, price, quantity, min_stock, mfg_date, exp_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, category, supplier, price, quantity, min_stock, mfg_date, exp_date))
    conn.commit()
    conn.close()

def update_product(product_id, quantity=None, price=None, min_stock=None):
    """Update product details."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if quantity is not None:
        cursor.execute("UPDATE products SET quantity = ? WHERE id = ?", (quantity, product_id))
    if price is not None:
        cursor.execute("UPDATE products SET price = ? WHERE id = ?", (price, product_id))
    if min_stock is not None:
        cursor.execute("UPDATE products SET min_stock = ? WHERE id = ?", (min_stock, product_id))
    
    conn.commit()
    conn.close()

def delete_product(product_id):
    """Delete product from database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

def add_sale(product_id, quantity, revenue, date=None):
    """Record a sale transaction."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute("""
        INSERT INTO sales (product_id, quantity, revenue, date)
        VALUES (?, ?, ?, ?)
    """, (product_id, quantity, revenue, date))
    
    # Update product quantity
    cursor.execute(
        "UPDATE products SET quantity = quantity - ? WHERE id = ?",
        (quantity, product_id)
    )
    
    conn.commit()
    conn.close()

def get_sales_history(days=30):
    """Get sales history for specified days."""
    try:
        conn = sqlite3.connect(DB_PATH)
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        query = """
            SELECT id, product_id, date, quantity, revenue
            FROM sales
            WHERE date >= ?
            ORDER BY date DESC
        """
        
        df = pd.read_sql_query(query, conn, params=(start_date,))
        conn.close()
        return df
    except:
        return pd.DataFrame()

def get_inventory_value():
    """Calculate total inventory value."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(price * quantity) FROM products")
        value = cursor.fetchone()[0] or 0
        conn.close()
        return value
    except:
        return 0

def get_low_stock_products():
    """Get products with low stock."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE quantity <= min_stock AND quantity > 0")
        products = cursor.fetchall()
        conn.close()
        return products
    except:
        return []

def get_expiring_products(days=30):
    """Get products expiring within specified days."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        end_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        cursor.execute(
            "SELECT * FROM products WHERE exp_date <= ? AND exp_date IS NOT NULL",
            (end_date,)
        )
        products = cursor.fetchall()
        conn.close()
        return products
    except:
        return []

# Initialize database on import
try:
    init_db()
except:
    pass
