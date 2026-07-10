import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database.db import get_all_products, get_product_by_id, get_sales_history
from models.forecasting_model import (
    forecast_demand, get_actual_vs_predicted, predict_stockout,
    forecast_inventory_requirement, calculate_forecast_accuracy
)
from utils.calculations import calculate_reorder_quantity, calculate_reorder_date, get_reorder_priority

# ============================================================================
# FORECASTING PAGE
# ============================================================================

def show_forecast():
    """Display demand forecasting and reorder recommendations."""
    st.title("🤖 AI Demand Forecasting")
    st.markdown("Predict future demand and optimize inventory levels")
    
    # Tab selection
    tab1, tab2, tab3 = st.tabs(["📈 Demand Forecast", "💡 Reorder Recommendations", "📄 Forecast Details"])
    
    # ====================================================================
    # TAB 1: DEMAND FORECAST
    # ====================================================================
    
    with tab1:
        st.markdown("### 📈 Demand Forecasting")
        
        col1, col2, col3 = st.columns(3)
        
        products = get_all_products()
        if not products:
            st.warning("No products available. Add products first!")
        else:
            product_names = {p[1]: p[0] for p in products}
            
            with col1:
                selected_product_name = st.selectbox(
                    "Select Product",
                    list(product_names.keys()),
                    key="forecast_product"
                )
                product_id = product_names[selected_product_name]
            
            with col2:
                forecast_days = st.selectbox(
                    "Forecast Period",
                    [7, 30, 90],
                    format_func=lambda x: f"{x} Days"
                )
            
            with col3:
                method = st.selectbox(
                    "Forecast Method",
                    ["ensemble", "linear", "moving_average", "exponential"],
                    format_func=lambda x: x.replace('_', ' ').title()
                )
            
            # Get forecast
            try:
                forecast_df = forecast_demand(product_id, days=forecast_days, method=method)
                
                if forecast_df is not None and not forecast_df.empty:
                    # Get product info
                    product = get_product_by_id(product_id)
                    if product:
                        st.markdown(f"**Product**: {product[1]} (ID: {product[0]})")
                        st.markdown(f"**Current Stock**: {product[5]} units | **Price**: ${product[4]:.2f}")
                    
                    st.divider()
                    
                    # Forecast metrics
                    col_m1, col_m2, col_m3 = st.columns(3)
                    
                    total_predicted = forecast_df['predicted_quantity'].sum()
                    avg_daily = forecast_df['predicted_quantity'].mean()
                    
                    with col_m1:
                        st.metric("Total Predicted Demand", f"{int(total_predicted)} units")
                    
                    with col_m2:
                        st.metric("Avg Daily Demand", f"{avg_daily:.1f} units")
                    
                    with col_m3:
                        if product and product[5] < total_predicted:
                            st.metric(
                                "Stock Status",
                                "🔴 Potential Stockout",
                                delta="Urgent reorder needed"
                            )
                        else:
                            st.metric(
                                "Stock Status",
                                "🟢 Sufficient",
                                delta="No immediate action"
                            )
                    
                    st.divider()
                    
                    # Forecast Chart
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=forecast_df['date'],
                        y=forecast_df['predicted_quantity'],
                        mode='lines+markers',
                        fill='tozeroy',
                        name='Predicted Demand',
                        line=dict(color='#1f77b4', width=3),
                        marker=dict(size=8),
                        hovertemplate='<b>%{x|%B %d}</b><br>Predicted: %{y:.1f} units<extra></extra>'
                    ))
                    
                    # Add current stock line
                    if product:
                        fig.add_hline(
                            y=product[5],
                            line_dash="dash",
                            line_color="red",
                            annotation_text="Current Stock",
                            annotation_position="right"
                        )
                    
                    fig.update_layout(
                        title=f"Demand Forecast - {selected_product_name} ({forecast_days} Days)",
                        xaxis_title="Date",
                        yaxis_title="Quantity (Units)",
                        height=400,
                        hovermode='x unified',
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Forecast Table
                    st.markdown("**Detailed Forecast**")
                    display_df = forecast_df.copy()
                    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
                    display_df.columns = ['Date', 'Predicted Quantity']
                    display_df['Predicted Quantity'] = display_df['Predicted Quantity'].apply(lambda x: f"{x:.2f}")
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                else:
                    st.warning(
                        "Insufficient sales data for accurate forecasting. "
                        "Please ensure the product has at least 7 days of sales history."
                    )
            
            except Exception as e:
                st.error(f"Error generating forecast: {str(e)}")
    
    # ====================================================================
    # TAB 2: REORDER RECOMMENDATIONS
    # ====================================================================
    
    with tab2:
        st.markdown("### 💡 Smart Reorder Recommendations")
        
        try:
            products = get_all_products()
            if products:
                # Calculate reorder for all products
                recommendations = []
                
                for product in products:
                    product_id, name, category, supplier, price, quantity, min_stock = product[0:7]
                    
                    reorder_qty = calculate_reorder_quantity(product_id)
                    priority = get_reorder_priority(product_id)
                    reorder_date = calculate_reorder_date(product_id)
                    
                    # Determine if reorder is needed
                    needs_reorder = quantity <= min_stock or reorder_qty > 0
                    
                    if needs_reorder or priority in ["Urgent", "High"]:
                        recommendations.append({
                            'Product ID': product_id,
                            'Product Name': name,
                            'Category': category,
                            'Current Stock': quantity,
                            'Min Stock': min_stock,
                            'Reorder Qty': reorder_qty,
                            'Priority': priority,
                            'Reorder Date': reorder_date.strftime('%Y-%m-%d'),
                            'Unit Price': f"${price:.2f}",
                            'Total Cost': f"${reorder_qty * price:,.2f}"
                        })
                
                if recommendations:
                    # Sort by priority
                    priority_order = {"Urgent": 0, "High": 1, "Medium": 2, "Low": 3}
                    recommendations.sort(key=lambda x: priority_order.get(x['Priority'], 4))
                    
                    df = pd.DataFrame(recommendations)
                    
                    # Display summary
                    col_s1, col_s2, col_s3 = st.columns(3)
                    
                    urgent_count = len([r for r in recommendations if r['Priority'] == 'Urgent'])
                    high_count = len([r for r in recommendations if r['Priority'] == 'High'])
                    total_cost = sum([float(r['Total Cost'].replace('$', '').replace(',', '')) for r in recommendations])
                    
                    with col_s1:
                        st.metric("🔴 Urgent Orders", urgent_count)
                    
                    with col_s2:
                        st.metric("🟡 High Priority", high_count)
                    
                    with col_s3:
                        st.metric("Total Reorder Cost", f"${total_cost:,.2f}")
                    
                    st.divider()
                    
                    # Display table
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Export option
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Recommendations as CSV",
                        data=csv,
                        file_name=f"reorder_recommendations_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.success("🙋 No urgent reorders needed at this time!")
            else:
                st.info("No products available")
        
        except Exception as e:
            st.error(f"Error generating recommendations: {str(e)}")
    
    # ====================================================================
    # TAB 3: FORECAST DETAILS
    # ====================================================================
    
    with tab3:
        st.markdown("### 📄 Forecast Analysis Details")
        
        products = get_all_products()
        if products:
            product_names = {p[1]: p[0] for p in products}
            selected_product_name = st.selectbox(
                "Select Product for Detailed Analysis",
                list(product_names.keys()),
                key="detail_product"
            )
            product_id = product_names[selected_product_name]
            
            col1, col2 = st.columns(2)
            
            with col1:
                detail_days = st.selectbox(
                    "Analysis Period",
                    [7, 30, 90],
                    format_func=lambda x: f"{x} Days",
                    key="detail_days"
                )
            
            with col2:
                detail_method = st.selectbox(
                    "Forecast Method",
                    ["ensemble", "linear", "moving_average", "exponential"],
                    format_func=lambda x: x.replace('_', ' ').title(),
                    key="detail_method"
                )
            
            try:
                # Get forecast accuracy
                accuracy = calculate_forecast_accuracy(product_id, days=detail_days)
                
                col_acc1, col_acc2 = st.columns(2)
                
                with col_acc1:
                    if accuracy:
                        st.metric("Forecast Accuracy", f"{accuracy}%")
                    else:
                        st.metric("Forecast Accuracy", "N/A", help="Insufficient data")
                
                with col_acc2:
                    inventory_req = forecast_inventory_requirement(product_id, days=detail_days)
                    st.metric("Required Inventory", f"{int(inventory_req)} units", help=f"Total demand for {detail_days} days")
                
                st.divider()
                
                # Actual vs Predicted
                st.markdown("**Actual vs Predicted Sales Comparison**")
                
                comparison_df = get_actual_vs_predicted(product_id, forecast_days=detail_days)
                
                if comparison_df is not None and not comparison_df.empty:
                    # Chart
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=comparison_df['date'],
                        y=comparison_df['predicted_quantity'],
                        mode='lines',
                        name='Predicted',
                        line=dict(color='#1f77b4', width=3),
                        hovertemplate='<b>%{x|%B %d}</b><br>Predicted: %{y:.1f}<extra></extra>'
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=comparison_df['date'],
                        y=comparison_df['actual_quantity'],
                        mode='lines+markers',
                        name='Actual',
                        line=dict(color='#2ca02c', width=2, dash='dash'),
                        marker=dict(size=6),
                        hovertemplate='<b>%{x|%B %d}</b><br>Actual: %{y:.1f}<extra></extra>'
                    ))
                    
                    fig.update_layout(
                        title="Forecast Accuracy Analysis",
                        xaxis_title="Date",
                        yaxis_title="Quantity",
                        height=400,
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Stockout prediction
                    st.divider()
                    st.markdown("**Stockout Risk Analysis**")
                    
                    will_stockout = predict_stockout(product_id, days=detail_days)
                    product = get_product_by_id(product_id)
                    
                    if will_stockout:
                        st.error(
                            f"🚨 **Stockout Risk**: Based on current stock ({product[5]} units) "
                            f"and predicted demand, this product may go out of stock within {detail_days} days."
                        )
                        
                        reorder_qty = calculate_reorder_quantity(product_id)
                        st.warning(
                            f"💡 **Recommended Action**: Order {reorder_qty} units immediately to avoid stockout."
                        )
                    else:
                        st.success(
                            f"✅ **No Immediate Risk**: Current stock ({product[5]} units) "
                            f"is sufficient for predicted demand in the next {detail_days} days."
                        )
                else:
                    st.info("Insufficient data for comparison")
            
            except Exception as e:
                st.error(f"Error analyzing forecast: {str(e)}")
        else:
            st.info("No products available")
