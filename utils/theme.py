import streamlit as st

def set_page_config():
    """Set Streamlit page configuration."""
    st.set_page_config(
        page_title="Smart Inventory AI",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def apply_theme():
    """Apply custom theme and styling."""
    st.markdown("""
    <style>
        /* Main background */
        .main {
            background-color: #f5f7fa;
        }
        
        /* Sidebar styling */
        .sidebar .sidebar-content {
            background-color: #2c3e50;
        }
        
        /* Metric styling */
        .metric-container {
            border-radius: 10px;
            padding: 15px;
            background-color: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        /* Button styling */
        .stButton>button {
            border-radius: 5px;
            background-color: #3498db;
            color: white;
            font-weight: bold;
            padding: 10px 20px;
        }
        
        .stButton>button:hover {
            background-color: #2980b9;
        }
        
        /* Input styling */
        .stTextInput>div>div>input,
        .stNumberInput>div>div>input,
        .stSelectbox>div>div>select {
            border-radius: 5px;
            border: 1px solid #bdc3c7;
        }
    </style>
    """, unsafe_allow_html=True)
