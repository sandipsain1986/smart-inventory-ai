import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database.db import (
    add_product, get_all_products, get_product_by_id, update_product, delete_product,
    get_categories
)
from utils.calculations import get_reorder_priority, calculate_reorder_quantity, calculate_reorder_date

# ============================================================================
# INVENTORY MANAGEMENT PAGE
# ============================================================================

def show_inventory():
    """Display inventory management interface."""
    st.title("📦 Inventory Management")
    st.markdown("Manage products, update stock levels, and track inventory")
    
    # Tab selection
    tab1, tab2, tab3 = st.tabs(["📋 View Inventory", "➕ Add Product", "✏️ Update/Delete"])
    
    # ====================================================================
    # TAB 1: VIEW INVENTORY
    # ====================================================================
    
    with tab1:
        st.markdown("### 📋 Current Inventory")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input(
                "🔍 Search by product name or ID",
                key="search_products"
            )
        
        with col2:
            category_filter = st.selectbox(
                "📂 Filter by Category",
                ["All"] + get_categories(),
                key="category_filter"
            )
        
        with col3:
            sort_by = st.selectbox(
                "📊 Sort by",
                ["Name", "Stock (Low to High)", "Stock (High to Low)", "Value"],
                key="sort_inventory"
            )
        
        # Get and filter products
        try:
            products = get_all_products()
            
            if products:
                # Convert to DataFrame for easier filtering
                product_data = []
                for product in products:
                    product_id, name, category, supplier, price, quantity, min_stock, mfg_date, exp_date = product[0:9]
                    
                    # Apply filters
                    if search_term.lower() not in name.lower() and search_term.lower() not in product_id.lower():
                        continue
                    
                    if category_filter != "All" and category != category_filter:
                        continue
                    
                    # Determine stock status
                    if quantity == 0:
                        status = "🔴 Out of Stock"
                    elif quantity <= min_stock:
                        status = "🟡 Low Stock"
                    else:
                        status = "🟢 In Stock"
                    
                    product_data.append({
                        'ID': product_id,
                        'Product Name': name,
                        'Category': category,
                        'Supplier': supplier,
                        'Price': f"${price:.2f}",
                        'Current Stock': quantity,
                        'Min Stock': min_stock,
                        'Status': status,
                        'Inventory Value': f"${price * quantity:.2f}",
                        'Expiry Date': exp_date or "N/A"
                    })
                
                if product_data:
                    # Apply sorting
                    df = pd.DataFrame(product_data)
                    
                    if sort_by == "Stock (Low to High)":
                        df = df.sort_values('Current Stock', key=lambda x: pd.to_numeric(x))
                    elif sort_by == "Stock (High to Low)":
                        df = df.sort_values('Current Stock', key=lambda x: pd.to_numeric(x), ascending=False)
                    elif sort_by == "Value":
                        df = df.sort_values('Inventory Value', key=lambda x: x.str.replace('$', '').str.replace(',', '').astype(float), ascending=False)
                    else:
                        df = df.sort_values('Product Name')
                    
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No products match your filters")
            else:
                st.info("No products in inventory yet. Add one to get started!")
        
        except Exception as e:
            st.error(f"Error loading inventory: {str(e)}")
    
    # ====================================================================
    # TAB 2: ADD PRODUCT
    # ====================================================================
    
    with tab2:
        st.markdown("### ➕ Add New Product")
        
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_name = st.text_input(
                    "Product Name",
                    placeholder="e.g., Laptop",
                    help="Name of the product"
                )
                category = st.selectbox(
                    "Category",
                    ["Electronics", "Grocery", "Fashion", "Home Appliances", "Other"],
                    help="Product category"
                )
                supplier = st.text_input(
                    "Supplier",
                    placeholder="e.g., TechCorp",
                    help="Supplier name"
                )
                price = st.number_input(
                    "Price ($)",
                    min_value=0.0,
                    step=0.01,
                    help="Product price"
                )
            
            with col2:
                quantity = st.number_input(
                    "Initial Quantity",
                    min_value=0,
                    step=1,
                    help="Starting stock quantity"
                )
                min_stock = st.number_input(
                    "Minimum Stock Level",
                    min_value=0,
                    step=1,
                    help="Alert when stock falls below this"
                )
                mfg_date = st.date_input(
                    "Manufacturing Date",
                    value=datetime.now()
                )
                exp_date = st.date_input(
                    "Expiry Date",
                    value=datetime.now() + timedelta(days=365)
                )
            
            submitted = st.form_submit_button(
                "✅ Add Product",
                use_container_width=True
            )
            
            if submitted:
                if not product_name or not supplier:
                    st.error("Please fill in all required fields")
                else:
                    try:
                        product_id = add_product(
                            name=product_name,
                            category=category,
                            supplier=supplier,
                            price=price,
                            quantity=quantity,
                            min_stock=min_stock,
                            mfg_date=mfg_date.strftime('%Y-%m-%d'),
                            exp_date=exp_date.strftime('%Y-%m-%d')
                        )
                        
                        st.success(f"✅ Product added successfully! (ID: {product_id})")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error adding product: {str(e)}")
    
    # ====================================================================
    # TAB 3: UPDATE/DELETE
    # ====================================================================
    
    with tab3:
        st.markdown("### ✏️ Update or Delete Product")
        
        try:
            products = get_all_products()
            if not products:
                st.info("No products to update or delete")
            else:
                product_names = {p[1]: p[0] for p in products}
                selected_name = st.selectbox(
                    "Select Product",
                    list(product_names.keys()),
                    help="Choose a product to modify"
                )
                
                if selected_name:
                    selected_id = product_names[selected_name]
                    product = get_product_by_id(selected_id)
                    
                    if product:
                        product_id, name, category, supplier, price, quantity, min_stock, mfg_date, exp_date = product[0:9]
                        
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**Product Details**: {name} (ID: {product_id})")
                            
                            with st.form(f"update_product_form_{product_id}"):
                                col_a, col_b = st.columns(2)
                                
                                with col_a:
                                    new_quantity = st.number_input(
                                        "Update Quantity",
                                        min_value=0,
                                        value=quantity,
                                        step=1
                                    )
                                    new_min_stock = st.number_input(
                                        "Update Minimum Stock",
                                        min_value=0,
                                        value=min_stock,
                                        step=1
                                    )
                                    new_price = st.number_input(
                                        "Update Price",
                                        min_value=0.0,
                                        value=float(price),
                                        step=0.01
                                    )
                                
                                with col_b:
                                    new_supplier = st.text_input(
                                        "Update Supplier",
                                        value=supplier
                                    )
                                    new_category = st.selectbox(
                                        "Update Category",
                                        ["Electronics", "Grocery", "Fashion", "Home Appliances", "Other"],
                                        index=["Electronics", "Grocery", "Fashion", "Home Appliances", "Other"].index(category) if category in ["Electronics", "Grocery", "Fashion", "Home Appliances", "Other"] else 0
                                    )
                                
                                col_c, col_d = st.columns(2)
                                with col_c:
                                    update_btn = st.form_submit_button(
                                        "💾 Update Product",
                                        use_container_width=True
                                    )
                                    if update_btn:
                                        try:
                                            update_product(
                                                product_id,
                                                quantity=new_quantity,
                                                minimum_stock=new_min_stock,
                                                price=new_price,
                                                supplier=new_supplier,
                                                category=new_category
                                            )
                                            st.success("✅ Product updated successfully!")
                                        except Exception as e:
                                            st.error(f"Error updating product: {str(e)}")
                                
                                with col_d:
                                    delete_btn = st.form_submit_button(
                                        "🗑️ Delete Product",
                                        use_container_width=True,
                                        type="secondary"
                                    )
                                    if delete_btn:
                                        if st.checkbox("Confirm delete", key=f"confirm_delete_{product_id}"):
                                            try:
                                                delete_product(product_id)
                                                st.success("✅ Product deleted successfully!")
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"Error deleting product: {str(e)}")
        
        except Exception as e:
            st.error(f"Error loading update interface: {str(e)}")
