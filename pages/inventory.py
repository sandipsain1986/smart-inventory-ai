import streamlit as st
import pandas as pd
from datetime import datetime
from database.db import (
    add_product, get_all_products, get_product_by_id,
    update_product, delete_product
)

# ============================================================================
# INVENTORY PAGE
# ============================================================================

def show_inventory():
    """Display inventory management interface."""
    st.title("📦 Inventory Management")
    st.markdown("Manage your product inventory")
    
    # Tab selection
    tab1, tab2, tab3 = st.tabs(["View Inventory", "Add Product", "Edit/Delete"])
    
    # ====================================================================
    # TAB 1: VIEW INVENTORY
    # ====================================================================
    
    with tab1:
        st.markdown("### Current Inventory")
        
        try:
            products = get_all_products()
            
            if products:
                # Create DataFrame
                data = []
                for product in products:
                    data.append({
                        'Product ID': product[0],
                        'Product Name': product[1],
                        'Category': product[2],
                        'Supplier': product[3],
                        'Price': f"${product[4]:.2f}",
                        'Quantity': product[5],
                        'Min Stock': product[6],
                        'Status': 'In Stock' if product[5] > product[6] else 'Low Stock'
                    })
                
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No products in inventory")
        
        except Exception as e:
            st.error(f"Error loading inventory: {str(e)}")
    
    # ====================================================================
    # TAB 2: ADD PRODUCT
    # ====================================================================
    
    with tab2:
        st.markdown("### Add New Product")
        
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_name = st.text_input("Product Name", placeholder="e.g., Laptop")
                category = st.text_input("Category", placeholder="e.g., Electronics")
                supplier = st.text_input("Supplier", placeholder="e.g., Dell")
            
            with col2:
                price = st.number_input("Unit Price ($)", min_value=0.0, step=0.01)
                quantity = st.number_input("Initial Quantity", min_value=0, step=1)
                min_stock = st.number_input("Minimum Stock", min_value=0, step=1)
            
            col3, col4 = st.columns(2)
            
            with col3:
                mfg_date = st.date_input("Manufacturing Date", value=datetime.now())
            
            with col4:
                exp_date = st.date_input("Expiry Date", value=datetime.now() + pd.Timedelta(days=365))
            
            submit = st.form_submit_button("✔️ Add Product")
            
            if submit:
                if product_name and category and supplier:
                    try:
                        add_product(
                            name=product_name,
                            category=category,
                            supplier=supplier,
                            price=price,
                            quantity=quantity,
                            min_stock=min_stock,
                            mfg_date=str(mfg_date),
                            exp_date=str(exp_date)
                        )
                        st.success("✅ Product added successfully!")
                    except Exception as e:
                        st.error(f"Error adding product: {str(e)}")
                else:
                    st.warning("⚠️ Please fill in all required fields")
    
    # ====================================================================
    # TAB 3: EDIT/DELETE
    # ====================================================================
    
    with tab3:
        st.markdown("### Edit or Delete Product")
        
        products = get_all_products()
        if products:
            product_names = {p[1]: p[0] for p in products}
            selected_name = st.selectbox(
                "Select Product",
                list(product_names.keys())
            )
            
            product_id = product_names[selected_name]
            product = get_product_by_id(product_id)
            
            if product:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("**Product Details**")
                    
                    with st.form("edit_product_form"):
                        new_quantity = st.number_input(
                            "Quantity",
                            value=int(product[5]),
                            min_value=0
                        )
                        new_price = st.number_input(
                            "Price",
                            value=float(product[4]),
                            min_value=0.0,
                            step=0.01
                        )
                        new_min_stock = st.number_input(
                            "Min Stock",
                            value=int(product[6]),
                            min_value=0
                        )
                        
                        submit = st.form_submit_button("🗐️ Update Product")
                        
                        if submit:
                            try:
                                update_product(
                                    product_id,
                                    quantity=new_quantity,
                                    price=new_price,
                                    min_stock=new_min_stock
                                )
                                st.success("✅ Product updated!")
                            except Exception as e:
                                st.error(f"Error updating: {str(e)}")
                
                with col2:
                    st.markdown("**Actions**")
                    if st.button("🗑️ Delete", use_container_width=True):
                        try:
                            delete_product(product_id)
                            st.success("✅ Product deleted!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting: {str(e)}")
        else:
            st.info("No products available")
