def check_stockout_alerts():
    """Check for stockout alerts."""
    try:
        from database.db import get_all_products
        
        products = get_all_products()
        alerts = [p for p in products if p[5] == 0]
        
        return alerts
    except:
        return []

def check_expiry_alerts(days=30):
    """Check for expiry alerts."""
    try:
        from database.db import get_expiring_products
        
        alerts = get_expiring_products(days=days)
        
        return alerts
    except:
        return []

def check_low_stock_alerts():
    """Check for low stock alerts."""
    try:
        from database.db import get_low_stock_products
        
        alerts = get_low_stock_products()
        
        return alerts
    except:
        return []
