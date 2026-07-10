import streamlit as st
import pandas as pd
from datetime import datetime
from database.db import add_sale, get_all_products, get_sales_history

# ============================================================================
# SALES PAGE
# ============================================================================

def show_sales():
    """Display sales management interface."""
    st.title("🛒 Sales Management")
    st.markdown("Record and view sales transactions")
    
    # Tab selection
    tab1, tab2 = st.tabs(["Record Sale", "View Sales History"])
    
    # ====================================================================
    # TAB 1: RECORD SALE
    # ====================================================================
    
    with tab1:
        st.markdown("### Record New Sale")
        
        products = get_all_products()
        if products:
            product_names = {p[1]: p[0] for p in products}
            product_prices = {p[0]: p[4] for p in products}
            
            with st.form("sale_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_product = st.selectbox(
                        "Select Product",
                        list(product_names.keys())
                    )
                    product_id = product_names[selected_product]
                    unit_price = product_prices[product_id]
                
                with col2:
                    quantity_sold = st.number_input(
                        "Quantity Sold",
                        min_value=1,
                        step=1
                    )
                
                # Calculate revenue
                revenue = quantity_sold * unit_price
                st.metric("Total Revenue", f"${revenue:,.2f}")
                
                sale_date = st.date_input("Sale Date", value=datetime.now())
                
                submit = st.form_submit_button("📈 Record Sale")
                
                if submit:
                    try:
                        add_sale(
                            product_id=product_id,
                            quantity=quantity_sold,
                            revenue=revenue,
                            date=str(sale_date)
                        )
                        st.success("✅ Sale recorded successfully!")
                    except Exception as e:
                        st.error(f"Error recording sale: {str(e)}")
        else:
            st.warning("No products available. Add products first!")
    
    # ====================================================================
    # TAB 2: VIEW SALES HISTORY
    # ====================================================================
    
    with tab2:
        st.markdown("### Sales History")
        
        period = st.selectbox(
            "Select Period",
            [7, 30, 90, 365],
            format_func=lambda x: f"Last {x} days"
        )
        
        try:
            sales_df = get_sales_history(days=period)
            
            if not sales_df.empty:
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Sales", len(sales_df))
                
                with col2:
                    st.metric("Total Revenue", f"${sales_df['revenue'].sum():,.2f}")
                
                with col3:
                    st.metric("Avg Sale", f"${sales_df['revenue'].mean():,.2f}")
                
                st.divider()
                
                # Display table
                display_df = sales_df.copy()
                display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')
                display_df.columns = ['Sale ID', 'Product ID', 'Date', 'Quantity', 'Revenue']
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info(f"No sales data for the selected period")
        
        except Exception as e:
            st.error(f"Error loading sales history: {str(e)}")
