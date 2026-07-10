import os
from datetime import datetime

def get_dashboard_kpis():
    """Calculate and return dashboard KPIs."""
    try:
        from database.db import get_all_products, get_inventory_value, get_low_stock_products, get_expiring_products
        
        products = get_all_products()
        
        kpis = {
            'total_products': len(products),
            'total_value': get_inventory_value(),
            'total_units': sum([p[5] for p in products]) if products else 0,
            'out_of_stock': len([p for p in products if p[5] == 0]) if products else 0,
            'low_stock': len(get_low_stock_products()),
            'expiring_soon': len(get_expiring_products(days=30))
        }
        
        return kpis
    except:
        return {
            'total_products': 0,
            'total_value': 0,
            'total_units': 0,
            'out_of_stock': 0,
            'low_stock': 0,
            'expiring_soon': 0
        }

def calculate_reorder_quantity(product_id):
    """Calculate reorder quantity based on demand."""
    try:
        from database.db import get_product_by_id, get_sales_history
        import pandas as pd
        
        product = get_product_by_id(product_id)
        if not product:
            return 0
        
        # Get average daily sales
        sales = get_sales_history(days=30)
        if not sales.empty:
            avg_daily = sales['quantity'].sum() / 30
        else:
            avg_daily = product[6]  # Use min stock as fallback
        
        # Reorder quantity = 90 days of supply
        reorder_qty = int(avg_daily * 90)
        
        return max(reorder_qty, product[6])
    except:
        return 0

def calculate_reorder_date(product_id):
    """Calculate when to reorder based on stock levels."""
    from datetime import datetime, timedelta
    
    try:
        from database.db import get_product_by_id, get_sales_history
        
        product = get_product_by_id(product_id)
        if not product:
            return datetime.now()
        
        sales = get_sales_history(days=30)
        if not sales.empty:
            avg_daily = sales['quantity'].sum() / 30
        else:
            avg_daily = 1
        
        # Days until min stock
        days_until_min = (product[5] - product[6]) / avg_daily if avg_daily > 0 else 0
        
        reorder_date = datetime.now() + timedelta(days=max(0, int(days_until_min - 7)))
        
        return reorder_date
    except:
        return datetime.now()

def get_reorder_priority(product_id):
    """Determine reorder priority."""
    try:
        from database.db import get_product_by_id
        
        product = get_product_by_id(product_id)
        if not product:
            return "Low"
        
        quantity = product[5]
        min_stock = product[6]
        price = product[4]
        
        if quantity == 0:
            return "Urgent"
        elif quantity <= min_stock:
            return "High" if price > 1000 else "High"
        elif quantity <= min_stock * 1.5:
            return "Medium"
        else:
            return "Low"
    except:
        return "Low"
