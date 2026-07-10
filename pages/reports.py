import streamlit as st
import pandas as pd
from datetime import datetime
from database.db import (
    get_all_products, get_sales_history, get_inventory_value,
    get_low_stock_products, get_expiring_products
)
from utils.calculations import get_dashboard_kpis
from models.forecasting_model import forecast_demand

# ============================================================================
# REPORTS PAGE
# ============================================================================

def show_reports():
    """Display reports and export functionality."""
    st.title("📋 Reports & Analytics")
    st.markdown("Generate and download comprehensive reports")
    
    # Tab selection
    tab1, tab2, tab3, tab4 = st.tabs([
        "📦 Inventory Report",
        "🛒 Sales Report",
        "📈 Forecast Report",
        "📊 Alerts Report"
    ])
    
    # ====================================================================
    # TAB 1: INVENTORY REPORT
    # ====================================================================
    
    with tab1:
        st.markdown("### 📦 Inventory Report")
        st.markdown("Complete current inventory status and details")
        
        try:
            products = get_all_products()
            
            if products:
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                total_value = get_inventory_value()
                total_units = sum([p[5] for p in products])
                low_stock = len(get_low_stock_products())
                out_of_stock = sum([1 for p in products if p[5] == 0])
                
                with col1:
                    st.metric("Total Products", len(products))
                
                with col2:
                    st.metric("Total Inventory Value", f"${total_value:,.2f}")
                
                with col3:
                    st.metric("Total Units", f"{total_units:,}")
                
                with col4:
                    st.metric("Out of Stock", out_of_stock)
                
                st.divider()
                
                # Build report
                report_data = []
                for product in products:
                    product_id, name, category, supplier, price, quantity, min_stock, mfg_date, exp_date = product[0:9]
                    
                    if quantity == 0:
                        status = "Out of Stock"
                    elif quantity <= min_stock:
                        status = "Low Stock"
                    else:
                        status = "In Stock"
                    
                    report_data.append({
                        'Product ID': product_id,
                        'Product Name': name,
                        'Category': category,
                        'Supplier': supplier,
                        'Unit Price': f"${price:.2f}",
                        'Quantity': quantity,
                        'Min Stock': min_stock,
                        'Stock Value': f"${price * quantity:.2f}",
                        'Status': status,
                        'Mfg Date': mfg_date or 'N/A',
                        'Expiry Date': exp_date or 'N/A'
                    })
                
                df = pd.DataFrame(report_data)
                
                # Display table
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download Inventory Report (CSV)",
                    data=csv,
                    file_name=f"inventory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_inventory"
                )
            else:
                st.info("No inventory data available")
        
        except Exception as e:
            st.error(f"Error generating inventory report: {str(e)}")
    
    # ====================================================================
    # TAB 2: SALES REPORT
    # ====================================================================
    
    with tab2:
        st.markdown("### Sales Report")
        st.markdown("Sales transactions and revenue analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            report_days = st.selectbox(
                "Report Period",
                [7, 30, 90, 180, 365],
                format_func=lambda x: f"Last {x} days",
                key="sales_report_days"
            )
        
        with col2:
            include_summary = st.checkbox(
                "Include Summary Stats",
                value=True,
                key="sales_include_summary"
            )
        
        try:
            sales_df = get_sales_history(days=report_days)
            
            if not sales_df.empty:
                # Summary
                if include_summary:
                    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                    
                    with col_s1:
                        st.metric("Total Transactions", len(sales_df))
                    
                    with col_s2:
                        st.metric("Total Revenue", f"${sales_df['revenue'].sum():,.2f}")
                    
                    with col_s3:
                        st.metric("Avg Transaction", f"${sales_df['revenue'].mean():,.2f}")
                    
                    with col_s4:
                        st.metric("Total Units Sold", f"{sales_df['quantity'].sum():,}")
                    
                    st.divider()
                
                # Prepare report data
                sales_df['date'] = pd.to_datetime(sales_df['date'])
                report_data = []
                
                for _, row in sales_df.iterrows():
                    product = get_all_products()
                    product_name = None
                    for p in product:
                        if p[0] == row['product_id']:
                            product_name = p[1]
                            break
                    
                    report_data.append({
                        'Sale ID': row['sale_id'],
                        'Product ID': row['product_id'],
                        'Product Name': product_name or 'Unknown',
                        'Date': row['date'].strftime('%Y-%m-%d'),
                        'Quantity Sold': int(row['quantity']),
                        'Revenue': f"${row['revenue']:,.2f}"
                    })
                
                df = pd.DataFrame(report_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download Sales Report (CSV)",
                    data=csv,
                    file_name=f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_sales"
                )
            else:
                st.info(f"No sales data for the selected period ({report_days} days)")
        
        except Exception as e:
            st.error(f"Error generating sales report: {str(e)}")
    
    # ====================================================================
    # TAB 3: FORECAST REPORT
    # ====================================================================
    
    with tab3:
        st.markdown("### Forecast Report")
        st.markdown("Demand forecasts and inventory recommendations")
        
        try:
            products = get_all_products()
            
            if products:
                forecast_days = st.selectbox(
                    "Forecast Period",
                    [7, 30, 90],
                    format_func=lambda x: f"{x} Days",
                    key="forecast_report_days"
                )
                
                # Generate forecasts for all products
                forecast_data = []
                
                for product in products:
                    product_id = product[0]
                    name = product[1]
                    current_stock = product[5]
                    
                    try:
                        forecast_df = forecast_demand(product_id, days=forecast_days)
                        
                        if forecast_df is not None and not forecast_df.empty:
                            predicted_demand = forecast_df['predicted_quantity'].sum()
                            
                            forecast_data.append({
                                'Product ID': product_id,
                                'Product Name': name,
                                'Current Stock': current_stock,
                                'Predicted Demand': f"{predicted_demand:.1f}",
                                'Stock Status': 'At Risk' if current_stock < predicted_demand else 'Adequate',
                                'Avg Daily Demand': f"{predicted_demand / forecast_days:.2f}"
                            })
                    except:
                        continue
                
                if forecast_data:
                    df = pd.DataFrame(forecast_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Download button
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download Forecast Report (CSV)",
                        data=csv,
                        file_name=f"forecast_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="download_forecast"
                    )
                else:
                    st.info("Insufficient data to generate forecasts")
            else:
                st.info("No products available")
        
        except Exception as e:
            st.error(f"Error generating forecast report: {str(e)}")
    
    # ====================================================================
    # TAB 4: ALERTS REPORT
    # ====================================================================
    
    with tab4:
        st.markdown("### Alerts & Issues Report")
        st.markdown("Summary of all active alerts and issues")
        
        try:
            # Low Stock
            st.markdown("#### Low Stock Products")
            low_stock_products = get_low_stock_products()
            
            if low_stock_products:
                low_stock_data = []
                for product in low_stock_products:
                    low_stock_data.append({
                        'Product ID': product[0],
                        'Product Name': product[1],
                        'Current Stock': product[5],
                        'Min Stock': product[6],
                        'Category': product[2]
                    })
                
                df_low = pd.DataFrame(low_stock_data)
                st.dataframe(df_low, use_container_width=True, hide_index=True)
            else:
                st.success("No low stock items")
            
            st.divider()
            
            # Expiring Products
            st.markdown("#### Expiring Products (Within 30 Days)")
            expiring_products = get_expiring_products(days=30)
            
            if expiring_products:
                expiring_data = []
                for product in expiring_products:
                    expiring_data.append({
                        'Product ID': product[0],
                        'Product Name': product[1],
                        'Current Stock': product[5],
                        'Expiry Date': product[8],
                        'Category': product[2]
                    })
                
                df_expiring = pd.DataFrame(expiring_data)
                st.dataframe(df_expiring, use_container_width=True, hide_index=True)
            else:
                st.success("No products expiring soon")
            
            st.divider()
            
            # Out of Stock
            st.markdown("#### Out of Stock Products")
            products = get_all_products()
            out_of_stock = [p for p in products if p[5] == 0]
            
            if out_of_stock:
                oos_data = []
                for product in out_of_stock:
                    oos_data.append({
                        'Product ID': product[0],
                        'Product Name': product[1],
                        'Category': product[2],
                        'Supplier': product[3]
                    })
                
                df_oos = pd.DataFrame(oos_data)
                st.dataframe(df_oos, use_container_width=True, hide_index=True)
            else:
                st.success("No out of stock items")
            
            st.divider()
            
            # Generate comprehensive alert report
            st.markdown("#### Comprehensive Alert Report")
            
            alert_summary = {
                'Low Stock Items': len(low_stock_products),
                'Expiring Products': len(expiring_products),
                'Out of Stock': len(out_of_stock),
                'Total Alerts': len(low_stock_products) + len(expiring_products) + len(out_of_stock)
            }
            
            alert_df = pd.DataFrame([alert_summary])
            st.dataframe(alert_df, use_container_width=True, hide_index=True)
            
            # Download complete alert report
            combined_report = f"""INVENTORY ALERTS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY:
- Low Stock Items: {alert_summary['Low Stock Items']}
- Expiring Products: {alert_summary['Expiring Products']}
- Out of Stock: {alert_summary['Out of Stock']}
- Total Alerts: {alert_summary['Total Alerts']}
"""
            
            st.download_button(
                label="Download Alert Report (TXT)",
                data=combined_report,
                file_name=f"alerts_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                key="download_alerts"
            )
        
        except Exception as e:
            st.error(f"Error generating alerts report: {str(e)}")
