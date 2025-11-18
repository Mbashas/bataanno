"""
Multi-Country Water Services Performance Dashboard
Main application file with navigation and page routing

Built with Streamlit for utility managers in Uganda, Cameroon, Lesotho, and Malawi
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add utils and pages to path
sys.path.append(str(Path(__file__).parent))

# Import data loaders
from utils.data_loader import (
    load_all_data,
    get_available_countries,
    get_available_years,
    apply_filters,
)

# Import page modules
from page_modules import home, overview, production, service, access, finance, reports


# Page configuration
st.set_page_config(
    page_title="Water Services Performance Dashboard",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== ENFORCE HIGH-CONTRAST THEME =====
# Light mode with dark text for maximum readability
st.markdown("""
<style>
    /* ===== GLOBAL THEME ENFORCEMENT ===== */
    :root {
        --text-dark: #1e1e1e;
        --text-medium: #333333;
        --bg-light: #ffffff;
        --bg-card: #f8f9fa;
        --border-light: #e0e0e0;
    }
    
    /* Force light background everywhere */
    .stApp {
        background-color: var(--bg-light) !important;
    }
    
    .main {
        padding: 0rem 1rem;
        background-color: var(--bg-light) !important;
    }
    
    /* ===== ALL HEADINGS AND TEXT - DARK COLOR ===== */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-dark) !important;
        font-weight: 600 !important;
    }
    
    p, span, div, label {
        color: var(--text-dark) !important;
    }
    
    /* ===== METRIC CARDS - LIGHT BACKGROUND WITH DARK TEXT ===== */
    .stMetric {
        background-color: var(--bg-light) !important;
        padding: 15px !important;
        border-radius: 8px !important;
        border: 1px solid var(--border-light) !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08) !important;
    }
    
    /* Force dark text for ALL metric labels */
    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] *,
    div[data-testid="stMetricLabel"] label,
    div[data-testid="stMetricLabel"] span,
    div[data-testid="stMetricLabel"] p {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: var(--text-dark) !important;
        text-shadow: none !important;
        -webkit-text-fill-color: var(--text-dark) !important;
        opacity: 1 !important;
    }
    
    /* Force dark text for ALL metric values */
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] *,
    div[data-testid="stMetricValue"] span,
    div[data-testid="stMetricValue"] p {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: var(--text-dark) !important;
        text-shadow: none !important;
        -webkit-text-fill-color: var(--text-dark) !important;
        opacity: 1 !important;
    }
    
    /* Delta colors - maintain visibility */
    div[data-testid="stMetricDelta"] {
        font-size: 14px !important;
        font-weight: 500 !important;
        opacity: 1 !important;
    }
    
    div[data-testid="stMetricDelta"] svg {
        fill: currentColor !important;
    }
    
    div[data-testid="stMetricDelta"] span,
    div[data-testid="stMetricDelta"] * {
        color: inherit !important;
        text-shadow: none !important;
        opacity: 1 !important;
    }
    
    /* Positive delta - visible green */
    div[data-testid="stMetricDelta"][style*="positive"] {
        color: #28a745 !important;
    }
    
    /* Negative delta - visible red */
    div[data-testid="stMetricDelta"][style*="negative"] {
        color: #dc3545 !important;
    }
    
    /* ===== SIDEBAR - LIGHT BACKGROUND WITH DARK TEXT ===== */
    [data-testid="stSidebar"] {
        background-color: var(--bg-card) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: var(--text-dark) !important;
    }
    
    [data-testid="stSidebar"] .stMetric {
        background-color: var(--bg-light) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }
    
    [data-testid="stSidebar"] div[data-testid="stMetricLabel"],
    [data-testid="stSidebar"] div[data-testid="stMetricLabel"] *,
    [data-testid="stSidebar"] div[data-testid="stMetricValue"],
    [data-testid="stSidebar"] div[data-testid="stMetricValue"] *,
    [data-testid="stSidebar"] div[data-testid="stMetricDelta"],
    [data-testid="stSidebar"] div[data-testid="stMetricDelta"] * {
        color: var(--text-dark) !important;
        text-shadow: none !important;
        -webkit-text-fill-color: var(--text-dark) !important;
        opacity: 1 !important;
    }
    
    /* ===== PLOTLY CHARTS - DARK TEXT ON LIGHT BACKGROUND ===== */
    .js-plotly-plot {
        background-color: var(--bg-light) !important;
    }
    
    .js-plotly-plot .plotly,
    .js-plotly-plot .plotly text,
    .js-plotly-plot text {
        fill: var(--text-dark) !important;
        color: var(--text-dark) !important;
    }
    
    /* Chart titles */
    .js-plotly-plot .gtitle,
    .js-plotly-plot .g-gtitle text {
        fill: var(--text-dark) !important;
        font-size: 16px !important;
        font-weight: 600 !important;
    }
    
    /* Axis labels and tick text */
    .js-plotly-plot .xtick text,
    .js-plotly-plot .ytick text,
    .js-plotly-plot .ztick text {
        fill: var(--text-dark) !important;
        opacity: 1 !important;
    }
    
    /* Legend text */
    .js-plotly-plot .legend text {
        fill: var(--text-dark) !important;
    }
    
    /* ===== DATAFRAMES - READABLE TEXT ===== */
    .stDataFrame {
        border: 1px solid var(--border-light) !important;
        border-radius: 8px !important;
    }
    
    .stDataFrame td,
    .stDataFrame th {
        color: var(--text-dark) !important;
    }
    
    /* ===== BUTTONS AND INPUTS ===== */
    .stButton button {
        color: var(--text-dark) !important;
        border: 1px solid var(--border-light) !important;
    }
    
    .stSelectbox label,
    .stMultiSelect label,
    .stTextInput label,
    .stDateInput label {
        color: var(--text-dark) !important;
        font-weight: 600 !important;
    }
    
    /* ===== INFO/WARNING/SUCCESS BOXES ===== */
    .stAlert {
        border-radius: 8px !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
    }
    
    .stAlert * {
        color: var(--text-dark) !important;
    }
    
    /* ===== HIDE STREAMLIT BRANDING ===== */
    .reportview-container .main footer {
        display: none;
    }
    #MainMenu {
        visibility: hidden;
    }
    header {
        visibility: hidden;
    }
    
    /* ===== ANTI-ALIASING FOR SMOOTH TEXT ===== */
    * {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* ===== NUCLEAR OPTION: OVERRIDE ALL INLINE STYLES ===== */
    [style*="color: rgb(250"] {
        color: var(--text-dark) !important;
    }
    [style*="color: white"] {
        color: var(--text-dark) !important;
    }
    [style*="color: #fff"] {
        color: var(--text-dark) !important;
    }
    [style*="color: #f"] {
        color: var(--text-dark) !important;
    }
    [style*="color: rgba(255"] {
        color: var(--text-dark) !important;
    }
    
    /* Force visibility on all text elements */
    .stMetric *,
    div[data-testid="column"] * {
        opacity: 1 !important;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False


def load_data_cached():
    """Load all data with caching"""
    if not st.session_state.data_loaded:
        with st.spinner("Loading data... This may take a moment on first load."):
            data = load_all_data()
            st.session_state.data = data
            st.session_state.data_loaded = True
    return st.session_state.data


def render_sidebar(raw_data):
    """Render sidebar with navigation and filters"""
    with st.sidebar:
        # Dashboard branding
        st.markdown("""
        <div style="text-align: center; padding: 20px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 20px;">
            <h1 style="color: white; margin: 0; font-size: 24px;">🌊 WASH Dashboard</h1>
            <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0; font-size: 12px;">Multi-Country Water Services</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.title("Navigation")
        
        # Page navigation
        page_options = {
            '🏠 Home': 'home',
            '📊 Overview Dashboard': 'overview',
            '🏭 Production Domain': 'production',
            '🚰 Service Domain': 'service',
            '🌍 Access Domain': 'access',
            '💰 Finance Domain': 'finance',
            '📋 Reports': 'reports'
        }
        
        # Radio button navigation
        selected_page = st.radio(
            "Select Page:",
            list(page_options.keys()),
            index=list(page_options.values()).index(st.session_state.current_page)
        )
        
        # Update current page
        st.session_state.current_page = page_options[selected_page]
        
        st.markdown("---")
        
        # Filters Section
        st.header("🔍 Filters")
        
        # Country filter
        available_countries = get_available_countries()
        countries_filter = st.multiselect(
            "Select Countries:",
            available_countries,
            default=available_countries,
            help="Filter data by selected countries"
        )
        
        # Date range filter
        available_years = get_available_years()
        if available_years:
            min_year = min(available_years)
            max_year = max(available_years)
            
            date_range = st.date_input(
                "Date Range:",
                value=(
                    datetime(min_year, 1, 1),
                    datetime(max_year, 12, 31)
                ),
                min_value=datetime(min_year, 1, 1),
                max_value=datetime(max_year, 12, 31),
                help="Select date range for analysis"
            )
        else:
            date_range = None
        
        st.markdown("---")
        
        # Quick Stats
        st.header("📊 Quick Stats")
        filtered_data = apply_filters(
            raw_data,
            countries=countries_filter,
            date_range=date_range
        )

        data = filtered_data
        
        # Calculate quick metrics
        if 'production' in data and len(data['production']) > 0:
            total_production = data['production']['production_m3'].sum() / 1_000_000
            st.metric("Total Production", f"{total_production:.1f}M m³")
        
        if 'w_access' in data and len(data['w_access']) > 0:
            latest_year = data['w_access']['year'].max()
            w_access_latest = data['w_access'][data['w_access']['year'] == latest_year]
            total_pop = w_access_latest['popn_total'].sum()
            st.metric("Total Population", f"{total_pop / 1_000_000:.2f}M")
        
        if 'finance' in data and len(data['finance']) > 0:
            total_revenue = data['finance']['sewer_revenue'].sum() / 1_000_000
            st.metric("Total Revenue", f"${total_revenue:.1f}M")
        
        st.markdown("---")
        
        # About section
        with st.expander("ℹ️ About"):
            st.markdown("""
            ### Water Services Dashboard
            
            **Version:** 1.0.0  
            **Last Updated:** November 2024
            
            This dashboard provides comprehensive insights into water and sanitation 
            services across Uganda, Cameroon, Lesotho, and Malawi.
            
            **Data Sources:**
            - Production records
            - Service delivery data
            - Access statistics (JMP)
            - Financial reports
            - National accounts
            
            **Support:** dashboard@washservices.org
            """)
        
        # Data refresh info
        st.caption("Data refreshes automatically every hour")
        
        return countries_filter, date_range, filtered_data


def render_current_page(data, countries_filter, date_range):
    """Render the currently selected page"""
    current_page = st.session_state.current_page
    
    if current_page == 'home':
        home.render_home_page(data, countries_filter, date_range)
    elif current_page == 'overview':
        overview.render_overview_page(data, countries_filter, date_range)
    elif current_page == 'production':
        production.render_production_page(data, countries_filter, date_range)
    elif current_page == 'service':
        service.render_service_page(data, countries_filter, date_range)
    elif current_page == 'access':
        access.render_access_page(data, countries_filter, date_range)
    elif current_page == 'finance':
        finance.render_finance_page(data, countries_filter, date_range)
    elif current_page == 'reports':
        reports.render_reports_page(data, countries_filter, date_range)
    else:
        st.error(f"Page '{current_page}' not found!")


def main():
    """Main application entry point"""
    # Initialize session state
    initialize_session_state()
    
    # Load data
    try:
        data = load_data_cached()
    except Exception as e:
        st.error(f"""
        ### Error Loading Data
        
        Unable to load data files. Please ensure all CSV files are in the `Data/` directory.
        
        **Error details:** {str(e)}
        
        **Required files:**
        - production.csv
        - w_service.csv
        - s_service.csv
        - w_access.csv
        - s_access.csv
        - all_fin_service.csv
        - all_national.csv
        """)
        st.stop()
    
    # Render sidebar and get filters
    countries_filter, date_range, filtered_data = render_sidebar(data)
    
    # Render current page
    render_current_page(filtered_data, countries_filter, date_range)


if __name__ == "__main__":
    main()

