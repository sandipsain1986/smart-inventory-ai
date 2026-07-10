import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import os

# Import custom modules
from database.db import init_db, get_all_products, get_sales_history
from utils.theme import apply_theme, set_page_config
from pages import dashboard, inventory, sales, forecast, reports

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

set_page_config()
apply_theme()

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = True

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

init_db()

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

with st.sidebar:
    st.markdown("""<div style='text-align: center; padding: 20px;'>
        <h1 style='color: #1f77b4; font-size: 28px;'>📦</h1>
        <h2 style='color: #1f77b4;'>Smart Inventory</h2>
        <p style='color: #666; font-size: 12px;'>AI-Powered Forecasting</p>
    </div>""", unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### 🔗 Navigation")
    
    pages = {
        "📊 Dashboard": "Dashboard",
        "📦 Inventory": "Inventory",
        "🛒 Sales": "Sales",
        "🤖 Forecasting": "Forecasting",
        "📋 Reports": "Reports",
    }
    
    selected_page = st.radio(
        "Select Page:",
        list(pages.keys()),
        key="page_selector"
    )
    
    st.session_state.current_page = pages[selected_page]
    
    st.divider()
    
    # Quick Stats in Sidebar
    st.markdown("### 📈 Quick Stats")
    
    try:
        products = get_all_products()
        sales_df = get_sales_history()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Products", len(products))
        with col2:
            if not sales_df.empty:
                st.metric("Total Sales", f"${sales_df['revenue'].sum():,.2f}")
            else:
                st.metric("Total Sales", "$0.00")
        
        # Low stock warning
        low_stock_count = sum([1 for p in products if p[5] <= p[6]])  # quantity <= min_stock
        if low_stock_count > 0:
            st.warning(f"⚠️ {low_stock_count} items low in stock")
    
    except Exception as e:
        st.error(f"Error loading stats: {str(e)}")
    
    st.divider()
    
    st.markdown("### ℹ️ About")
    st.markdown("""\n**Version:** 1.0.0  
**Built with:** Streamlit, Python, ML  
**Database:** SQLite  
**Last Updated:** 2024
    """)

# ============================================================================
# MAIN CONTENT AREA
# ============================================================================

def main():
    page = st.session_state.current_page
    
    try:
        if page == "Dashboard":
            dashboard.show_dashboard()
        elif page == "Inventory":
            inventory.show_inventory()
        elif page == "Sales":
            sales.show_sales()
        elif page == "Forecasting":
            forecast.show_forecast()
        elif page == "Reports":
            reports.show_reports()
        else:
            st.error("Page not found!")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Please try refreshing the page or check your data.")

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    main()
