import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from database.db import get_low_stock_products, get_expiring_products, get_sales_history, get_all_products, get_inventory_value

# ============================================================================
# ALERT SYSTEM
# ============================================================================

def check_low_stock_alerts():
    """Check for low stock items and display alerts."""
    try:
        low_stock_items = get_low_stock_products()
        
        if low_stock_items:
            for item in low_stock_items[:5]:  # Show top 5
                product_id, name, category, supplier, price, quantity, min_stock = item[0:7]
                st.warning(
                    f"⚠️ **Low Stock Alert**: {name} (ID: {product_id})\n"
                    f"Current: {quantity} | Minimum: {min_stock}"
                )
    except Exception as e:
        st.error(f"Error checking low stock: {str(e)}")

def check_expiry_alerts():
    """Check for expiring products and display alerts."""
    try:
        expiring_items = get_expiring_products(days=30)
        
        if expiring_items:
            for item in expiring_items[:3]:  # Show top 3
                product_id, name, category, supplier, price, quantity, min_stock, mfg_date, exp_date = item[0:9]
                st.error(
                    f"🔴 **Expiry Alert**: {name} (ID: {product_id})\n"
                    f"Expires: {exp_date}"
                )
    except Exception as e:
        st.error(f"Error checking expiry: {str(e)}")

def check_overstock_alerts():
    """Check for overstocked items and display alerts."""
    try:
        products = get_all_products()
        
        overstock_items = []
        for product in products:
            product_id, name, category, supplier, price, quantity, min_stock = product[0:7]
            # Overstock if quantity > min_stock * 5
            if quantity > (min_stock * 5):
                overstock_items.append((name, product_id, quantity, min_stock))
        
        if overstock_items:
            for name, product_id, quantity, min_stock in overstock_items[:3]:  # Show top 3
                st.warning(
                    f"📦 **Overstock Alert**: {name} (ID: {product_id})\n"
                    f"Current: {quantity} | Recommended Max: {min_stock * 5}"
                )
    except Exception as e:
        st.error(f"Error checking overstock: {str(e)}")

def check_stockout_prediction(product_id, forecast_days=7):
    """Predict potential stockouts based on sales velocity."""
    try:
        from models.forecasting_model import predict_stockout
        
        will_stockout = predict_stockout(product_id, days=forecast_days)
        
        if will_stockout:
            from database.db import get_product_by_id
            product = get_product_by_id(product_id)
            if product:
                name = product[1]
                st.error(
                    f"🚨 **Stockout Prediction**: {name} (ID: {product_id})\n"
                    f"Predicted stockout within {forecast_days} days!"
                )
                return True
    
    except Exception as e:
        st.error(f"Error predicting stockout: {str(e)}")
    
    return False

def display_all_alerts():
    """Display all active alerts."""
    st.markdown("### 🚨 Active Alerts")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        low_stock = len(get_low_stock_products())
        st.metric("Low Stock Items", low_stock, delta=-1 if low_stock > 0 else 0)
    
    with col2:
        expiring = len(get_expiring_products(days=30))
        st.metric("Expiring Soon", expiring, delta=-1 if expiring > 0 else 0)
    
    with col3:
        # Calculate overstock
        products = get_all_products()
        overstock = sum([1 for p in products if p[5] > (p[6] * 5)])
        st.metric("Overstocked Items", overstock)
    
    st.divider()
    
    # Display detailed alerts
    check_low_stock_alerts()
    check_expiry_alerts()
    check_overstock_alerts()

# ============================================================================
# ALERT SEVERITY LEVELS
# ============================================================================

def get_alert_severity(product_id):
    """Determine alert severity for a product."""
    from database.db import get_product_by_id
    
    product = get_product_by_id(product_id)
    
    if not product:
        return 'none'
    
    product_id, name, category, supplier, price, quantity, min_stock, mfg_date, exp_date = product[0:9]
    
    # Check expiry - highest priority
    if exp_date:
        expiry_date = datetime.strptime(exp_date, '%Y-%m-%d')
        if expiry_date < datetime.now():
            return 'critical'  # Expired
        elif expiry_date < datetime.now() + timedelta(days=7):
            return 'high'  # Expiring soon
    
    # Check stock level
    if quantity == 0:
        return 'critical'  # Out of stock
    elif quantity <= min_stock:
        return 'high'  # Low stock
    elif quantity > (min_stock * 5):
        return 'medium'  # Overstock
    
    return 'low'  # Normal

# ============================================================================
# ALERT COUNTERS
# ============================================================================

def count_alerts():
    """Count total active alerts."""
    try:
        low_stock_count = len(get_low_stock_products())
        expiring_count = len(get_expiring_products(days=30))
        
        products = get_all_products()
        overstock_count = sum([1 for p in products if p[5] > (p[6] * 5)])
        
        return low_stock_count + expiring_count + overstock_count
    
    except Exception as e:
        print(f"Error counting alerts: {str(e)}")
        return 0
