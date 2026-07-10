import streamlit as st

# ============================================================================
# THEME CONFIGURATION
# ============================================================================

def set_page_config():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Smart Inventory Forecast AI",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/sandipsain1986/smart-inventory-ai',
            'Report a bug': 'https://github.com/sandipsain1986/smart-inventory-ai/issues',
            'About': "Smart Inventory Forecast AI v1.0.0"
        }
    )

def apply_theme():
    """Apply custom theme and styling."""
    st.markdown("""
    <style>
        /* Primary Colors */
        :root {
            --primary-color: #1f77b4;
            --secondary-color: #2ca02c;
            --warning-color: #ff7f0e;
            --danger-color: #d62728;
            --text-color: #333333;
            --light-bg: #f8f9fa;
            --border-color: #e0e0e0;
        }
        
        /* Overall Background */
        .main {
            background-color: #ffffff;
        }
        
        /* Sidebar Styling */
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        
        /* Header Styling */
        h1, h2, h3 {
            color: #1f77b4;
            font-weight: 600;
        }
        
        /* Metric Cards */
        .metric-card {
            background-color: #f8f9fa;
            border-left: 4px solid #1f77b4;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Success Badge */
        .badge-success {
            background-color: #2ca02c;
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
        }
        
        /* Warning Badge */
        .badge-warning {
            background-color: #ff7f0e;
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
        }
        
        /* Danger Badge */
        .badge-danger {
            background-color: #d62728;
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
        }
        
        /* Table Styling */
        table {
            border-collapse: collapse;
            width: 100%;
        }
        
        th {
            background-color: #1f77b4;
            color: white;
            padding: 10px;
            text-align: left;
            font-weight: 600;
        }
        
        td {
            padding: 10px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        tr:hover {
            background-color: #f8f9fa;
        }
        
        /* Button Styling */
        .stButton > button {
            background-color: #1f77b4;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            font-weight: 600;
            border: none;
            transition: background-color 0.3s;
        }
        
        .stButton > button:hover {
            background-color: #155a9a;
        }
        
        /* Input Styling */
        .stTextInput, .stSelectbox, .stNumberInput, .stDateInput {
            border-radius: 5px;
        }
        
        /* Alert Styling */
        .stAlert {
            border-radius: 5px;
            padding: 15px;
        }
        
        /* Card Container */
        .card {
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Divider */
        .divider {
            border-top: 2px solid #e0e0e0;
            margin: 20px 0;
        }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# COLOR CONSTANTS
# ============================================================================

COLORS = {
    'primary': '#1f77b4',
    'secondary': '#2ca02c',
    'warning': '#ff7f0e',
    'danger': '#d62728',
    'success': '#2ca02c',
    'info': '#1f77b4',
    'text': '#333333',
    'light_bg': '#f8f9fa',
    'border': '#e0e0e0',
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_metric_card(title, value, delta=None, color='primary'):
    """Create a styled metric card."""
    color_code = COLORS.get(color, COLORS['primary'])
    
    html = f"""
    <div class='metric-card' style='border-left-color: {color_code};'>
        <p style='color: #666; font-size: 14px; margin: 0;'>{title}</p>
        <h3 style='color: {color_code}; margin: 10px 0 0 0;'>{value}</h3>
    """
    
    if delta:
        html += f"<p style='color: #666; font-size: 12px; margin: 5px 0 0 0;'>{delta}</p>"
    
    html += "</div>"
    
    return html

def create_badge(text, badge_type='success'):
    """Create a styled badge."""
    return f"<span class='badge-{badge_type}'>{text}</span>"
