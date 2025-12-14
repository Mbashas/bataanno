"""
Multi-Country Water Services Performance Dashboard
Main application file with navigation and page routing

Built with Streamlit for utility managers in Uganda, Cameroon, Lesotho, and Malawi
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path
import yaml
import streamlit_authenticator as stauth

# Add utils and pages to path
sys.path.append(str(Path(__file__).parent))

# Import data loaders
from utils.data_loader import (
    load_all_data,
    get_available_countries,
    get_available_years,
    apply_filters,
)

# Import theme system
from utils.theme import (
    BRAND, 
    get_theme, 
    init_theme, 
    toggle_theme, 
    generate_css,
    LIGHT_THEME,
    DARK_THEME
)

# Import custom logo
from assets.logo_svg import get_wash_logo_svg, get_wash_logo_colored_svg, get_login_illustration_svg

# Import page modules
from page_modules import home, overview, production, service, access, finance, reports


# Page configuration
st.set_page_config(
    page_title="WASH Performance Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme
init_theme()

# Apply dynamic CSS based on current theme
st.markdown(generate_css(), unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'selected_country' not in st.session_state:
        st.session_state.selected_country = None
    # Authentication session state
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_country' not in st.session_state:
        st.session_state.user_country = None
    # Currency mode: 'local' or 'usd'
    if 'currency_mode' not in st.session_state:
        st.session_state.currency_mode = 'local'


def load_auth_config():
    """Load authentication configuration from YAML file"""
    config_path = Path(__file__).parent / 'config' / 'users.yaml'
    with open(config_path) as file:
        config = yaml.safe_load(file)
    return config


def get_user_info(username, config):
    """Get user role and country from config"""
    if username in config['credentials']['usernames']:
        user_data = config['credentials']['usernames'][username]
        return {
            'role': user_data.get('role', 'country_manager'),
            'country': user_data.get('country'),
            'name': user_data.get('name', username)
        }
    return None


def load_data_cached():
    """Load all data with caching"""
    if not st.session_state.data_loaded:
        with st.spinner("Loading data... This may take a moment on first load."):
            data = load_all_data()
            st.session_state.data = data
            st.session_state.data_loaded = True
    return st.session_state.data


def get_zones_for_country(country, data):
    """Get available zones for a given country"""
    if 'w_service' in data and len(data['w_service']) > 0:
        country_data = data['w_service'][data['w_service']['country'] == country]
        return sorted(country_data['zone'].unique().tolist())
    return []


def render_sidebar_landing(authenticator):
    """Render minimal sidebar for landing page (no navigation)"""
    
    with st.sidebar:
        # Styled CSS logo - Water droplet with infrastructure motif
        st.markdown("""
        <div style="text-align: center; padding: 20px 12px; margin-bottom: 20px;">
            <div style="
                width: 56px;
                height: 56px;
                margin: 0 auto 12px auto;
                background: linear-gradient(135deg, #58A0C8 0%, #34699A 50%, #113F67 100%);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                position: relative;
            ">
                <span style="font-size: 28px; filter: drop-shadow(0 2px 2px rgba(0,0,0,0.2));">💧</span>
                <div style="
                    position: absolute;
                    bottom: -2px;
                    right: -2px;
                    width: 18px;
                    height: 18px;
                    background: #059669;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 10px;
                    border: 2px solid #113F67;
                ">📊</div>
            </div>
            <h1 style="color: #F8FAFC; margin: 0; font-size: 18px; font-weight: 700; line-height: 1.3;">
                WASH Dashboard
            </h1>
            <p style="color: rgba(255,255,255,0.7); margin: 4px 0 0 0; font-size: 11px; letter-spacing: 0.5px;">Water • Sanitation • Hygiene</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Theme toggle
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("<p style='color: #F8FAFC; margin: 0; font-size: 13px;'>🎨 Theme</p>", unsafe_allow_html=True)
        with col2:
            theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
            if st.button(theme_icon, key="theme_toggle_landing", help="Toggle dark/light mode"):
                toggle_theme()
                st.rerun()
        
        st.markdown("---")
        
        # Show user info and logout
        if 'name' in st.session_state:
            st.markdown(f"""
            <div style="padding: 12px; background: rgba(255,255,255,0.1); border-radius: 12px; margin-bottom: 16px;">
                <p style="color: #F8FAFC; margin: 0; font-size: 14px; font-weight: 600;">
                    👤 {st.session_state.name}
                </p>
                <p style="color: rgba(255,255,255,0.7); margin: 4px 0 0 0; font-size: 12px;">
                    🔑 Administrator
                </p>
            </div>
            """, unsafe_allow_html=True)
            authenticator.logout("🚪 Logout", "sidebar")
            st.markdown("---")
        
        st.info("👉 Select a country to explore the dashboard")
        
        # About section
        with st.expander("ℹ️ About"):
            st.markdown(f"""
            **Version:** {BRAND['version']}  
            **Updated:** December 2024
            
            Multi-country water services analytics for Uganda, Cameroon, Lesotho, and Malawi.
            
            **Data Sources:** Production, Service, Access, Finance
            
            **Contact:** support@wash-dashboard.org
            """)


def render_sidebar_country_dashboard(raw_data, selected_country, authenticator):
    """Render sidebar for country dashboard with zone filters"""
    theme = get_theme()
    
    with st.sidebar:
        # Styled CSS logo - Water droplet with infrastructure motif
        st.markdown("""
        <div style="text-align: center; padding: 20px 12px; margin-bottom: 20px;">
            <div style="
                width: 56px;
                height: 56px;
                margin: 0 auto 12px auto;
                background: linear-gradient(135deg, #58A0C8 0%, #34699A 50%, #113F67 100%);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                position: relative;
            ">
                <span style="font-size: 28px; filter: drop-shadow(0 2px 2px rgba(0,0,0,0.2));">💧</span>
                <div style="
                    position: absolute;
                    bottom: -2px;
                    right: -2px;
                    width: 18px;
                    height: 18px;
                    background: #059669;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 10px;
                    border: 2px solid #113F67;
                ">📊</div>
            </div>
            <h1 style="color: #F8FAFC; margin: 0; font-size: 18px; font-weight: 700; line-height: 1.3;">
                WASH Dashboard
            </h1>
            <p style="color: rgba(255,255,255,0.7); margin: 4px 0 0 0; font-size: 11px; letter-spacing: 0.5px;">Water • Sanitation • Hygiene</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Theme toggle
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("<p style='color: #F8FAFC; margin: 0; font-size: 13px;'>🎨 Theme</p>", unsafe_allow_html=True)
        with col2:
            theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
            if st.button(theme_icon, key="theme_toggle_country", help="Toggle dark/light mode"):
                toggle_theme()
                st.rerun()
        
        st.markdown("---")
        
        # Show user info
        if 'name' in st.session_state:
            role_label = "🔑 Administrator" if st.session_state.user_role == 'admin' else f"📍 {st.session_state.user_country} Manager"
            st.markdown(f"""
            <div style="padding: 12px; background: rgba(255,255,255,0.1); border-radius: 12px; margin-bottom: 16px;">
                <p style="color: #F8FAFC; margin: 0; font-size: 14px; font-weight: 600;">
                    👤 {st.session_state.name}
                </p>
                <p style="color: rgba(255,255,255,0.7); margin: 4px 0 0 0; font-size: 12px;">
                    {role_label}
                </p>
            </div>
            """, unsafe_allow_html=True)
            authenticator.logout("🚪 Logout", "sidebar")
        
        # Back to Home button - ONLY for admin users
        if st.session_state.user_role == 'admin':
            if st.button("← Back to Home", use_container_width=True):
                st.session_state.selected_country = None
                st.rerun()
        
        st.markdown("---")
        
        # Country indicator with flag
        country_flags = {'Uganda': '🇺🇬', 'Malawi': '🇲🇼', 'Lesotho': '🇱🇸', 'Cameroon': '🇨🇲'}
        flag = country_flags.get(selected_country, '🌍')
        st.markdown(f"""
        <div style="padding: 16px; background: rgba(255,255,255,0.1); border-radius: 12px; margin-bottom: 16px; text-align: center;">
            <div style="font-size: 32px; margin-bottom: 8px;">{flag}</div>
            <h3 style="color: #F8FAFC; margin: 0; font-size: 18px;">{selected_country}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Filters Section
        st.header("🔍 Filters")
        
        # Zone filter (dynamically populated based on selected country)
        available_zones = get_zones_for_country(selected_country, raw_data)
        zones_filter = st.multiselect(
            "Select Zones:",
            available_zones,
            default=available_zones,
            help="Filter data by selected zones"
        )
        
        # Zone filter applicability notice
        st.caption("ℹ️ Zone filter applies to: Service, Access data. Finance & Production data are at country level.")
        
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
        
        # Reports link
        if st.button("📋 Generate Reports", use_container_width=True):
            st.session_state.show_reports = True
            st.rerun()
        
        st.markdown("---")
        
        # Quick Stats
        st.header("📊 Quick Stats")
        filtered_data = apply_filters(
            raw_data,
            countries=[selected_country],
            zones=zones_filter,
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
        
        # Data refresh info
        st.caption("Data refreshes automatically every hour")
        
        return zones_filter, date_range, filtered_data


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


def render_country_dashboard(data, selected_country, zones_filter, date_range):
    """Render country dashboard with tabs for different domains"""
    
    # Check if reports should be shown
    if st.session_state.get('show_reports', False):
        st.session_state.show_reports = False
        reports.render_reports_page(data, [selected_country], date_range)
        return
    
    # Dashboard header
    # Page header with styled branding
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 2px solid rgba(17, 63, 103, 0.1);">
        <div style="
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #58A0C8 0%, #34699A 50%, #113F67 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(17, 63, 103, 0.2);
        ">
            <span style="font-size: 24px;">💧</span>
        </div>
        <div>
            <h1 style="margin: 0; font-size: 1.75rem; color: var(--text-primary);">{selected_country} Water Services</h1>
            <p style="margin: 0; font-size: 14px; color: var(--text-secondary);">Performance Analytics Dashboard</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"Comprehensive performance metrics across all service domains")
    st.markdown("---")
    
    # Create tabs for different domains
    tab_overview, tab_production, tab_service, tab_access, tab_finance = st.tabs([
        "📊 Overview",
        "🏭 Production",
        "🚰 Service",
        "🌍 Access",
        "💰 Finance"
    ])
    
    with tab_overview:
        overview.render_overview_page(data, [selected_country], date_range)
    
    with tab_production:
        production.render_production_page(data, [selected_country], date_range)
    
    with tab_service:
        service.render_service_page(data, [selected_country], date_range)
    
    with tab_access:
        access.render_access_page(data, [selected_country], date_range)
    
    with tab_finance:
        finance.render_finance_page(data, [selected_country], date_range)


def render_login_page():
    """Render a modern login page with branding"""
    theme = get_theme()
    
    st.markdown("""
    <style>
        /* Hide sidebar on login page */
        [data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* Center content */
        .main .block-container {
            max-width: 500px !important;
            padding: 2rem !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Centered branding header using Streamlit components
    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
    
    # Logo using columns for centering - styled professional logo
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="
                width: 80px;
                height: 80px;
                margin: 0 auto 16px auto;
                background: linear-gradient(135deg, #58A0C8 0%, #34699A 50%, #113F67 100%);
                border-radius: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 8px 24px rgba(17, 63, 103, 0.3);
                position: relative;
            ">
                <span style="font-size: 40px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));">💧</span>
                <div style="
                    position: absolute;
                    bottom: -4px;
                    right: -4px;
                    width: 24px;
                    height: 24px;
                    background: #059669;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 12px;
                    border: 3px solid white;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                ">📊</div>
            </div>
            <h1 style="color: {theme['text_primary']}; font-size: 1.75rem; font-weight: 700; margin: 0;">
                WASH Dashboard
            </h1>
            <p style="color: {theme['text_secondary']}; margin: 8px 0 0 0; font-size: 13px; letter-spacing: 1px;">
                Water • Sanitation • Hygiene
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    
    # Welcome text
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 24px;">
        <h2 style="color: {theme['text_primary']}; font-size: 1.5rem; font-weight: 600; margin: 0 0 8px 0;">
            Welcome Back
        </h2>
        <p style="color: {theme['text_secondary']}; font-size: 14px; margin: 0;">
            Sign in to access your dashboard
        </p>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main application entry point"""
    # Initialize session state
    initialize_session_state()
    
    # Load authentication config
    try:
        config = load_auth_config()
    except Exception as e:
        st.error(f"Error loading authentication config: {str(e)}")
        st.stop()
    
    # Create authenticator object
    # Using session-only authentication (no persistent cookies)
    authenticator = stauth.Authenticate(
        config['credentials'],
        cookie_name='wash_session',
        cookie_key='wash_temp_key',
        cookie_expiry_days=0  # Session-only, expires when browser closes
    )
    
    # Check authentication status
    if st.session_state.get("authentication_status") is None:
        # Not logged in - show login page
        render_login_page()
        
        # Login form
        authenticator.login(location='main')
        
        theme = get_theme()
        st.markdown(f"""
        <div style="text-align: center; margin-top: 24px; padding: 14px; background: {theme['info_bg']}; border-radius: 8px; border: 1px solid {theme['border']};">
            <p style="color: {theme['text_secondary']}; font-size: 12px; margin: 0 0 8px 0; font-weight: 600;">Demo Credentials</p>
            <p style="color: {theme['text_muted']}; font-size: 11px; margin: 0;">
                <strong>Admin:</strong> <code style="background: {theme['bg_main']}; padding: 2px 6px; border-radius: 4px; font-size: 11px;">admin</code> / <code style="background: {theme['bg_main']}; padding: 2px 6px; border-radius: 4px; font-size: 11px;">admin123</code>
            </p>
            <p style="color: {theme['text_muted']}; font-size: 11px; margin: 6px 0 0 0;">
                <strong>Uganda:</strong> <code style="background: {theme['bg_main']}; padding: 2px 6px; border-radius: 4px; font-size: 11px;">uganda_manager</code> / <code style="background: {theme['bg_main']}; padding: 2px 6px; border-radius: 4px; font-size: 11px;">uganda123</code>
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    elif st.session_state.get("authentication_status") is False:
        # Failed login
        render_login_page()
        
        authenticator.login(location='main')
        st.error("❌ Username or password is incorrect")
        st.stop()
    
    elif st.session_state.get("authentication_status"):
        # Successfully logged in
        username = st.session_state.get("username")
        user_info = get_user_info(username, config)
        
        if user_info:
            st.session_state.user_role = user_info['role']
            st.session_state.user_country = user_info['country']
        
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
        
        # Role-based routing
        if st.session_state.user_role == 'admin':
            # Admin can see home page and navigate freely
            selected_country = st.session_state.selected_country
            
            if selected_country is None:
                # Landing Page Mode: Show home page with country cards
                render_sidebar_landing(authenticator)
                home.render_home_page(data, None, None)
            else:
                # Country Dashboard Mode: Show tabs with zone filtering
                zones_filter, date_range, filtered_data = render_sidebar_country_dashboard(data, selected_country, authenticator)
                render_country_dashboard(filtered_data, selected_country, zones_filter, date_range)
        
        elif st.session_state.user_role == 'country_manager':
            # Country managers go directly to their country dashboard
            # Force their country selection
            assigned_country = st.session_state.user_country
            st.session_state.selected_country = assigned_country
            
            # Render country dashboard (no back button, locked to their country)
            zones_filter, date_range, filtered_data = render_sidebar_country_dashboard(data, assigned_country, authenticator)
            render_country_dashboard(filtered_data, assigned_country, zones_filter, date_range)
        
        else:
            st.error("Unknown user role. Please contact administrator.")
            authenticator.logout("Logout", "main")


if __name__ == "__main__":
    main()

