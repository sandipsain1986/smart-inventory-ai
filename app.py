import streamlit as st
from pages import dashboard, inventory, sales, forecast, reports
from utils.theme import set_page_config, apply_theme

# Set page config
set_page_config()
apply_theme()

# Sidebar navigation
st.sidebar.title("📦 Smart Inventory AI")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Dashboard", "📦 Inventory", "🛒 Sales", "🤖 Forecast", "📊 Reports"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("**About**")
st.sidebar.info(
    "Smart Inventory Forecast AI\n\n"
    "AI-powered inventory management system with demand forecasting, "
    "automated alerts, and smart reorder recommendations."
)

# Route to appropriate page
if page == "🏠 Dashboard":
    dashboard.show_dashboard()
elif page == "📦 Inventory":
    inventory.show_inventory()
elif page == "🛒 Sales":
    sales.show_sales()
elif page == "🤖 Forecast":
    forecast.show_forecast()
elif page == "📊 Reports":
    reports.show_reports()
