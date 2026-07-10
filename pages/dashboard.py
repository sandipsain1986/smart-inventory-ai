import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from database.db import get_all_products, get_sales_history, get_inventory_value
from utils.calculations import get_dashboard_kpis, calculate_inventory_health_score
from utils.alerts import display_all_alerts
from models.forecasting_model import get_top_selling_products

# ============================================================================
# DASHBOARD PAGE
# ============================================================================

def show_dashboard():
    """Display the main dashboard."""
    st.title("📊 Smart Inventory Dashboard")
    st.markdown("Real-time inventory analytics and insights")
    
    # Get KPI data
    kpis = get_dashboard_kpis()
    
    # ====================================================================
    # KPI CARDS
    # ====================================================================
    
    st.markdown("### 📊 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Products",
            kpis.get('total_products', 0),
            delta="",
            help="Total unique products in inventory"
        )
    
    with col2:
        st.metric(
            "Total Inventory Value",
            f"${kpis.get('total_value', 0):,.2f}",
            help="Sum of (quantity × price) for all products"
        )
    
    with col3:
        st.metric(
            "Total Units in Stock",
            f"{kpis.get('total_units', 0):,}",
            help="Total quantity across all products"
        )
    
    with col4:
        st.metric(
            "Monthly Revenue",
            f"${kpis.get('monthly_revenue', 0):,.2f}",
            help="Revenue from last 30 days"
        )
    
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric(
            "Total Sales (30d)",
            f"${kpis.get('total_sales', 0):,.2f}",
            help="All revenue from last 30 days"
        )
    
    with col6:
        st.metric(
            "Low Stock Items",
            kpis.get('low_stock_count', 0),
            delta=kpis.get('low_stock_count', 0) if kpis.get('low_stock_count', 0) > 0 else None,
            help="Products below minimum threshold"
        )
    
    with col7:
        st.metric(
            "Out of Stock",
            kpis.get('stockout_count', 0),
            delta=kpis.get('stockout_count', 0) if kpis.get('stockout_count', 0) > 0 else None,
            help="Products with zero inventory"
        )
    
    with col8:
        health_score = kpis.get('health_score', 0)
        health_color = "🟢" if health_score > 70 else "🟡" if health_score > 40 else "🔴"
        st.metric(
            "Health Score",
            f"{health_score}%",
            delta=f"{health_score}% overall",
            help="Inventory management efficiency (0-100)"
        )
    
    st.divider()
    
    # ====================================================================
    # ALERTS SECTION
    # ====================================================================
    
    try:
        display_all_alerts()
    except Exception as e:
        st.warning(f"Could not load alerts: {str(e)}")
    
    st.divider()
    
    # ====================================================================
    # CHARTS
    # ====================================================================
    
    col1, col2 = st.columns(2)
    
    # Sales Trend Chart
    with col1:
        st.markdown("### 📈 Sales Trend (Last 30 Days)")
        try:
            sales_df = get_sales_history(days=30)
            if not sales_df.empty:
                sales_df['date'] = pd.to_datetime(sales_df['date'])
                daily_sales = sales_df.groupby('date')['revenue'].sum().reset_index()
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=daily_sales['date'],
                    y=daily_sales['revenue'],
                    mode='lines+markers',
                    fill='tozeroy',
                    line=dict(color='#1f77b4', width=3),
                    marker=dict(size=8),
                    hovertemplate='<b>%{x|%B %d}</b><br>Revenue: $%{y:,.2f}<extra></extra>'
                ))
                fig.update_layout(
                    height=300,
                    hovermode='x unified',
                    showlegend=False,
                    margin=dict(l=0, r=0, t=0, b=0)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No sales data available")
        except Exception as e:
            st.error(f"Error loading sales trend: {str(e)}")
    
    # Category Distribution
    with col2:
        st.markdown("### 🏷️ Inventory by Category")
        try:
            products = get_all_products()
            if products:
                category_data = {}
                for product in products:
                    category = product[2]
                    quantity = product[5]
                    category_data[category] = category_data.get(category, 0) + quantity
                
                fig = go.Figure(data=[go.Pie(
                    labels=list(category_data.keys()),
                    values=list(category_data.values()),
                    hovertemplate='<b>%{label}</b><br>Units: %{value}<extra></extra>'
                )])
                fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No products available")
        except Exception as e:
            st.error(f"Error loading category distribution: {str(e)}")
    
    col3, col4 = st.columns(2)
    
    # Inventory Value by Category
    with col3:
        st.markdown("### 💰 Inventory Value by Category")
        try:
            products = get_all_products()
            if products:
                category_value = {}
                for product in products:
                    category = product[2]
                    value = product[4] * product[5]  # price * quantity
                    category_value[category] = category_value.get(category, 0) + value
                
                fig = go.Figure(data=[go.Bar(
                    x=list(category_value.keys()),
                    y=list(category_value.values()),
                    marker=dict(color='#2ca02c'),
                    hovertemplate='<b>%{x}</b><br>Value: $%{y:,.2f}<extra></extra>'
                )])
                fig.update_layout(
                    height=300,
                    xaxis_title="Category",
                    yaxis_title="Value ($)",
                    hovermode='x unified',
                    margin=dict(l=0, r=0, t=0, b=0)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No products available")
        except Exception as e:
            st.error(f"Error loading category value: {str(e)}")
    
    # Top Selling Products
    with col4:
        st.markdown("### 🏆 Top Selling Products (90 Days)")
        try:
            top_products = get_top_selling_products(limit=5)
            if not top_products.empty:
                fig = go.Figure(data=[go.Bar(
                    x=top_products['total_quantity'],
                    y=top_products['product_name'],
                    orientation='h',
                    marker=dict(color='#ff7f0e'),
                    hovertemplate='<b>%{y}</b><br>Units Sold: %{x}<extra></extra>'
                )])
                fig.update_layout(
                    height=300,
                    xaxis_title="Units Sold",
                    hovermode='y unified',
                    margin=dict(l=0, r=0, t=0, b=0)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No sales data available")
        except Exception as e:
            st.error(f"Error loading top products: {str(e)}")
    
    st.divider()
    
    # ====================================================================
    # STOCK STATUS TABLE
    # ====================================================================
    
    st.markdown("### 📦 Stock Status Summary")
    try:
        products = get_all_products()
        if products:
            status_data = []
            for product in products:
                product_id, name, category, supplier, price, quantity, min_stock = product[0:7]
                
                # Determine status
                if quantity == 0:
                    status = "🔴 Out of Stock"
                elif quantity <= min_stock:
                    status = "🟡 Low Stock"
                else:
                    status = "🟢 In Stock"
                
                status_data.append({
                    'Product ID': product_id,
                    'Product Name': name,
                    'Category': category,
                    'Current Stock': quantity,
                    'Min Stock': min_stock,
                    'Status': status,
                    'Value': f"${price * quantity:,.2f}"
                })
            
            status_df = pd.DataFrame(status_data).head(10)
            st.dataframe(status_df, use_container_width=True, hide_index=True)
            
            if len(status_data) > 10:
                st.caption(f"Showing 10 of {len(status_data)} products")
        else:
            st.info("No products in inventory")
    except Exception as e:
        st.error(f"Error loading stock status: {str(e)}")
