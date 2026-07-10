import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database.db import get_all_products, get_low_stock_products, get_expiring_products
from utils.alerts import check_stockout_alerts, check_expiry_alerts
from utils.calculations import get_dashboard_kpis

# ============================================================================
# DASHBOARD PAGE
# ============================================================================

def show_dashboard():
    """Display main dashboard with KPIs and alerts."""
    st.title("🏠 Dashboard")
    st.markdown("Welcome to Smart Inventory Forecast AI")
    
    # Fetch dashboard KPIs
    kpis = get_dashboard_kpis()
    
    # Display KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Products",
            kpis.get('total_products', 0),
            help="Total number of products in inventory"
        )
    
    with col2:
        st.metric(
            "Total Inventory Value",
            f"${kpis.get('total_value', 0):,.2f}",
            help="Total value of all inventory"
        )
    
    with col3:
        st.metric(
            "Total Units",
            f"{kpis.get('total_units', 0):,}",
            help="Total units in stock"
        )
    
    with col4:
        st.metric(
            "Out of Stock",
            kpis.get('out_of_stock', 0),
            delta=f"{kpis.get('low_stock', 0)} low stock",
            help="Products out of stock"
        )
    
    st.divider()
    
    # Alerts Section
    col_alerts1, col_alerts2 = st.columns(2)
    
    with col_alerts1:
        st.markdown("### 🚨 Active Alerts")
        
        low_stock = get_low_stock_products()
        expiring = get_expiring_products(days=30)
        
        if low_stock or expiring:
            if low_stock:
                st.warning(f"🟡 **Low Stock**: {len(low_stock)} products")
                for product in low_stock[:3]:
                    st.caption(f"{product[1]} - {product[5]} units (min: {product[6]})")
            
            if expiring:
                st.error(f"🔴 **Expiring Soon**: {len(expiring)} products")
                for product in expiring[:3]:
                    st.caption(f"{product[1]} - Expires: {product[8]}")
        else:
            st.success("퉰5 No active alerts")
    
    with col_alerts2:
        st.markdown("### 📊 Quick Stats")
        
        products = get_all_products()
        if products:
            avg_stock = sum([p[5] for p in products]) / len(products)
            st.info(f"📈 Average Stock: {avg_stock:.0f} units")
            
            categories = set([p[2] for p in products])
            st.info(f📦 Categories: {len(categories)}")
        else:
            st.info("No products in inventory")

def get_all_products():
    """Placeholder function - import from database.db"""
    try:
        from database.db import get_all_products as db_get_all
        return db_get_all()
    except:
        return []
