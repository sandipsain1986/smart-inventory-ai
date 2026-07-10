import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database.db import add_sale, get_sales_history, get_all_products, get_product_by_id

# ============================================================================
# SALES MANAGEMENT PAGE
# ============================================================================

def show_sales():
    """Display sales management interface."""
    st.title("🛒 Sales Management")
    st.markdown("Record sales, track revenue, and analyze sales trends")
    
    # Tab selection
    tab1, tab2, tab3 = st.tabs(["📊 Sales History", "➕ Record Sale", "📈 Analytics"])
    
    # ====================================================================
    # TAB 1: SALES HISTORY
    # ====================================================================
    
    with tab1:
        st.markdown("### 📊 Sales History")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            days_filter = st.selectbox(
                "Time Period",
                [7, 30, 90, 180, 365],
                format_func=lambda x: f"Last {x} days"
            )
        
        with col2:
            product_filter = st.selectbox(
                "Filter by Product",
                ["All"] + [p[1] for p in get_all_products()],
                key="sales_product_filter"
            )
        
        with col3:
            sort_option = st.selectbox(
                "Sort by",
                ["Date (Recent)", "Date (Oldest)", "Revenue (High)", "Revenue (Low)"],
                key="sales_sort"
            )
        
        # Get sales data
        try:
            if product_filter == "All":
                sales_df = get_sales_history(days=days_filter)
            else:
                product_id = None
                for p in get_all_products():
                    if p[1] == product_filter:
                        product_id = p[0]
                        break
                sales_df = get_sales_history(product_id=product_id, days=days_filter)
            
            if not sales_df.empty:
                sales_df['date'] = pd.to_datetime(sales_df['date'])
                
                # Add product name
                sales_df['product_name'] = sales_df['product_id'].apply(
                    lambda x: get_product_by_id(x)[1] if get_product_by_id(x) else x
                )
                
                # Sorting
                if sort_option == "Date (Recent)":
                    sales_df = sales_df.sort_values('date', ascending=False)
                elif sort_option == "Date (Oldest)":
                    sales_df = sales_df.sort_values('date', ascending=True)
                elif sort_option == "Revenue (High)":
                    sales_df = sales_df.sort_values('revenue', ascending=False)
                elif sort_option == "Revenue (Low)":
                    sales_df = sales_df.sort_values('revenue', ascending=True)
                
                # Display metrics
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                
                with col_m1:
                    st.metric("Total Transactions", len(sales_df))
                
                with col_m2:
                    st.metric("Total Revenue", f"${sales_df['revenue'].sum():,.2f}")
                
                with col_m3:
                    st.metric("Avg Transaction", f"${sales_df['revenue'].mean():,.2f}")
                
                with col_m4:
                    st.metric("Total Units Sold", f"{sales_df['quantity'].sum():,}")
                
                st.divider()
                
                # Display table
                display_df = sales_df[['sale_id', 'product_name', 'date', 'quantity', 'revenue']].copy()
                display_df.columns = ['Sale ID', 'Product', 'Date', 'Qty', 'Revenue']
                display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
                display_df['Revenue'] = display_df['Revenue'].apply(lambda x: f"${x:,.2f}")
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("No sales found for the selected period")
        
        except Exception as e:
            st.error(f"Error loading sales: {str(e)}")
    
    # ====================================================================
    # TAB 2: RECORD SALE
    # ====================================================================
    
    with tab2:
        st.markdown("### ➕ Record New Sale")
        
        with st.form("record_sale_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                products = get_all_products()
                if products:
                    product_names = {p[1]: p[0] for p in products}
                    selected_product_name = st.selectbox(
                        "Select Product",
                        list(product_names.keys())
                    )
                    product_id = product_names[selected_product_name]
                    
                    # Get product details
                    product = get_product_by_id(product_id)
                    if product:
                        st.info(
                            f"💵 Price: ${product[4]:.2f} | "
                            f"📦 Current Stock: {product[5]}"
                        )
                    
                    quantity_sold = st.number_input(
                        "Quantity Sold",
                        min_value=1,
                        step=1,
                        help="Number of units sold"
                    )
                else:
                    st.warning("No products available. Add products first!")
                    quantity_sold = 0
            
            with col2:
                sale_date = st.date_input(
                    "Sale Date",
                    value=datetime.now()
                )
                
                if products and product:
                    revenue = quantity_sold * product[4]
                    st.metric("Revenue", f"${revenue:,.2f}")
                else:
                    revenue = 0
            
            submitted = st.form_submit_button(
                "✅ Record Sale",
                use_container_width=True
            )
            
            if submitted:
                if not products:
                    st.error("No products available")
                elif quantity_sold <= 0:
                    st.error("Quantity must be greater than 0")
                else:
                    try:
                        sale_id = add_sale(
                            product_id=product_id,
                            date=sale_date.strftime('%Y-%m-%d'),
                            quantity=quantity_sold,
                            revenue=revenue
                        )
                        
                        st.success(f"✅ Sale recorded successfully! (ID: {sale_id})")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error recording sale: {str(e)}")
    
    # ====================================================================
    # TAB 3: ANALYTICS
    # ====================================================================
    
    with tab3:
        st.markdown("### 📈 Sales Analytics")
        
        try:
            sales_df = get_sales_history(days=90)
            
            if not sales_df.empty:
                sales_df['date'] = pd.to_datetime(sales_df['date'])
                
                col1, col2 = st.columns(2)
                
                # Daily Revenue Chart
                with col1:
                    st.markdown("**Daily Revenue (90 Days)**")
                    daily_revenue = sales_df.groupby('date')['revenue'].sum().reset_index()
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=daily_revenue['date'],
                        y=daily_revenue['revenue'],
                        mode='lines+markers',
                        fill='tozeroy',
                        line=dict(color='#2ca02c', width=2),
                        hovertemplate='<b>%{x|%B %d}</b><br>Revenue: $%{y:,.2f}<extra></extra>'
                    ))
                    fig.update_layout(
                        height=350,
                        hovermode='x unified',
                        margin=dict(l=0, r=0, t=0, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Product Sales Distribution
                with col2:
                    st.markdown("**Sales by Product (90 Days)**")
                    product_sales = sales_df.groupby('product_id')['quantity'].sum().reset_index()
                    product_sales['product_name'] = product_sales['product_id'].apply(
                        lambda x: get_product_by_id(x)[1] if get_product_by_id(x) else x
                    )
                    product_sales = product_sales.nlargest(10, 'quantity')
                    
                    fig = go.Figure(data=[go.Bar(
                        x=product_sales['quantity'],
                        y=product_sales['product_name'],
                        orientation='h',
                        marker=dict(color='#1f77b4'),
                        hovertemplate='<b>%{y}</b><br>Units: %{x}<extra></extra>'
                    )])
                    fig.update_layout(
                        height=350,
                        xaxis_title="Units Sold",
                        margin=dict(l=0, r=0, t=0, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                col3, col4 = st.columns(2)
                
                # Monthly Revenue Trend
                with col3:
                    st.markdown("**Monthly Revenue Trend**")
                    sales_df['month'] = sales_df['date'].dt.to_period('M')
                    monthly_revenue = sales_df.groupby('month')['revenue'].sum().reset_index()
                    monthly_revenue['month'] = monthly_revenue['month'].astype(str)
                    
                    fig = go.Figure(data=[go.Bar(
                        x=monthly_revenue['month'],
                        y=monthly_revenue['revenue'],
                        marker=dict(color='#ff7f0e'),
                        hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>'
                    )])
                    fig.update_layout(
                        height=350,
                        xaxis_title="Month",
                        yaxis_title="Revenue ($)",
                        margin=dict(l=0, r=0, t=0, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Top Customers/Products by Revenue
                with col4:
                    st.markdown("**Top Products by Revenue (90 Days)**")
                    revenue_by_product = sales_df.groupby('product_id')['revenue'].sum().reset_index()
                    revenue_by_product['product_name'] = revenue_by_product['product_id'].apply(
                        lambda x: get_product_by_id(x)[1] if get_product_by_id(x) else x
                    )
                    revenue_by_product = revenue_by_product.nlargest(10, 'revenue')
                    
                    fig = go.Figure(data=[go.Bar(
                        x=revenue_by_product['revenue'],
                        y=revenue_by_product['product_name'],
                        orientation='h',
                        marker=dict(color='#d62728'),
                        hovertemplate='<b>%{y}</b><br>Revenue: $%{x:,.2f}<extra></extra>'
                    )])
                    fig.update_layout(
                        height=350,
                        xaxis_title="Revenue ($)",
                        margin=dict(l=0, r=0, t=0, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No sales data available for analysis")
        
        except Exception as e:
            st.error(f"Error loading analytics: {str(e)}")
