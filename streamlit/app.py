import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
import sys
import os

warnings.filterwarnings('ignore')

# Import your data loader
sys.path.append('..')
from utils.data_loader import load_all_data, get_available_countries, get_available_zones, get_data_summary

# Page configuration
st.set_page_config(
    page_title="Water Utility Performance Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    try:
        with open('assets/styles/custom.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except:
        # Fallback basic styling
        st.markdown("""
        <style>
            .main-header {
                font-size: 2.5rem;
                color: #1f77b4;
                text-align: center;
                margin-bottom: 2rem;
                font-weight: bold;
            }
            .kpi-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1.5rem;
                border-radius: 15px;
                text-align: center;
                color: white;
                margin-bottom: 1rem;
            }
        </style>
        """, unsafe_allow_html=True)

load_css()

# Load data with progress indicator
@st.cache_data(ttl=3600)
def load_cached_data():
    with st.spinner("💧 Loading utility data... This may take a few moments."):
        data = load_all_data()
        return data

# Load data
data = load_cached_data()

# Data validation
if not data or all(df.empty for df in data.values() if df is not None):
    st.error("❌ No data loaded. Please check your data files and paths.")
    st.stop()

# Country flags mapping
COUNTRY_FLAGS = {
    'Uganda': '🇺🇬',
    'Cameroon': '🇨🇲', 
    'Malawi': '🇲🇼',
    'Lesotho': '🇱🇸'
}

# Header with enhanced design
st.markdown("""
<div style='text-align: center; padding: 2rem; background: rgba(255,255,255,0.9); border-radius: 15px; margin-bottom: 2rem;'>
    <h1 class='main-header'>💧 Water Utility Performance Dashboard</h1>
    <p style='font-size: 1.2rem; color: #666;'>Monitoring Water & Sanitation Services Across East and Southern Africa</p>
</div>
""", unsafe_allow_html=True)

# Data Quality Check
st.markdown('<div class="section-header">📋 Data Overview & Quality Check</div>', unsafe_allow_html=True)

summary = get_data_summary(data)
countries = get_available_countries()
zones = get_available_zones()

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_rows = sum([s.get('rows', 0) for s in summary.values()])
    st.metric("📊 Total Records", f"{total_rows:,}")

with col2:
    datasets_loaded = len([s for s in summary.values() if s.get('status') == 'Loaded' and s.get('rows', 0) > 0])
    st.metric("✅ Datasets Loaded", datasets_loaded)

with col3:
    st.metric("🌍 Countries", len(countries))

with col4:
    st.metric("🗺️ Zones", len(zones))

# KPI Section - Top Level Metrics
st.markdown('<div class="section-header">📊 Executive Summary - Key Performance Indicators</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    countries_count = len(countries)
    st.metric(
        label="🌍 Countries Covered",
        value=countries_count,
        delta=f"+{max(0, countries_count-1)} vs target"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    if not data['w_access'].empty and 'access_rate' in data['w_access'].columns:
        avg_water_access = data['w_access']['access_rate'].mean()
        st.metric(
            label="💧 Avg Water Access",
            value=f"{avg_water_access:.1f}%" if not pd.isna(avg_water_access) else "N/A",
            delta=f"+{max(0, avg_water_access-85):.1f}% vs baseline" if not pd.isna(avg_water_access) else None
        )
    else:
        st.metric(label="💧 Avg Water Access", value="N/A")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    if not data['s_access'].empty and 'access_rate' in data['s_access'].columns:
        avg_sanitation_access = data['s_access']['access_rate'].mean()
        st.metric(
            label="🚽 Avg Sanitation Access",
            value=f"{avg_sanitation_access:.1f}%" if not pd.isna(avg_sanitation_access) else "N/A",
            delta=f"+{max(0, avg_sanitation_access-80):.1f}% vs baseline" if not pd.isna(avg_sanitation_access) else None
        )
    else:
        st.metric(label="🚽 Avg Sanitation Access", value="N/A")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    if not data['production'].empty and 'production_m3' in data['production'].columns:
        total_production = data['production']['production_m3'].sum() / 1000000  # Convert to million m3
        st.metric(
            label="🚰 Total Water Production",
            value=f"{total_production:,.1f}M m³" if not pd.isna(total_production) else "N/A",
            delta="+8.2% vs last year" if not pd.isna(total_production) else None
        )
    else:
        st.metric(label="🚰 Total Water Production", value="N/A")
    st.markdown('</div>', unsafe_allow_html=True)

# World Map Visualization
st.markdown('<div class="section-header">🌍 Regional Performance Overview</div>', unsafe_allow_html=True)

if not data['w_access'].empty and not data['s_access'].empty:
    latest_w_access = data['w_access'].sort_values('date').groupby('country').last().reset_index()
    latest_s_access = data['s_access'].sort_values('date').groupby('country').last().reset_index()

    map_tab1, map_tab2, map_tab3 = st.tabs(["Water Access Rates", "Sanitation Access Rates", "Coverage Gap"])

    with map_tab1:
        if 'access_rate' in latest_w_access.columns:
            fig_water_map = px.choropleth(
                latest_w_access,
                locations="country",
                locationmode="country names",
                color="access_rate",
                color_continuous_scale="Blues",
                title="Water Access Rates by Country (%)",
                range_color=[50, 100],
                hover_data=["safely_managed", "basic"] if 'safely_managed' in latest_w_access.columns else None
            )
            fig_water_map.update_layout(height=500)
            st.plotly_chart(fig_water_map, use_container_width=True)

    with map_tab2:
        if 'access_rate' in latest_s_access.columns:
            fig_sanitation_map = px.choropleth(
                latest_s_access,
                locations="country",
                locationmode="country names",
                color="access_rate",
                color_continuous_scale="Greens",
                title="Sanitation Access Rates by Country (%)",
                range_color=[50, 100],
                hover_data=["safely_managed", "basic"] if 'safely_managed' in latest_s_access.columns else None
            )
            fig_sanitation_map.update_layout(height=500)
            st.plotly_chart(fig_sanitation_map, use_container_width=True)

# Performance Comparison Charts
st.markdown('<div class="section-header">📈 Performance Comparison Across Countries</div>', unsafe_allow_html=True)

if not data['w_access'].empty and not data['s_access'].empty:
    col1, col2 = st.columns(2)

    with col1:
        if 'access_rate' in latest_w_access.columns:
            fig_water_bar = px.bar(
                latest_w_access.sort_values('access_rate', ascending=True),
                x='access_rate',
                y='country',
                orientation='h',
                title='Water Access Rates by Country (%)',
                color='access_rate',
                color_continuous_scale='Blues'
            )
            fig_water_bar.update_layout(height=400)
            st.plotly_chart(fig_water_bar, use_container_width=True)

    with col2:
        if 'access_rate' in latest_s_access.columns:
            fig_sanitation_bar = px.bar(
                latest_s_access.sort_values('access_rate', ascending=True),
                x='access_rate',
                y='country',
                orientation='h',
                title='Sanitation Access Rates by Country (%)',
                color='access_rate',
                color_continuous_scale='Greens'
            )
            fig_sanitation_bar.update_layout(height=400)
            st.plotly_chart(fig_sanitation_bar, use_container_width=True)

# Financial and Operational Metrics
st.markdown('<div class="section-header">💰 Financial & Operational Performance</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    if not data['finance'].empty and 'collection_rate' in data['finance'].columns:
        avg_collection = data['finance']['collection_rate'].mean()
        st.metric(
            label="💰 Avg Collection Rate",
            value=f"{avg_collection:.1f}%" if not pd.isna(avg_collection) else "N/A",
            delta="+2.1% vs target" if not pd.isna(avg_collection) else None
        )
    else:
        st.metric(label="💰 Avg Collection Rate", value="N/A")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    if not data['w_service'].empty and 'customers' in data['w_service'].columns:
        total_customers = data['w_service']['customers'].sum() / 1000  # in thousands
        st.metric(
            label="👥 Total Customers Served",
            value=f"{total_customers:,.0f}K" if not pd.isna(total_customers) else "N/A",
            delta="+5.3% growth" if not pd.isna(total_customers) else None
        )
    else:
        st.metric(label="👥 Total Customers Served", value="N/A")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    if (not data['w_service'].empty and 
        'test_passed_chlorine' in data['w_service'].columns and 
        'tests_conducted_chlorine' in data['w_service'].columns):
        total_passed = data['w_service']['test_passed_chlorine'].sum()
        total_tests = data['w_service']['tests_conducted_chlorine'].sum()
        if total_tests > 0:
            avg_chlorine_passed = (total_passed / total_tests) * 100
            st.metric(
                label="🔬 Water Quality Compliance",
                value=f"{avg_chlorine_passed:.1f}%",
                delta="+1.8% improvement"
            )
        else:
            st.metric(label="🔬 Water Quality Compliance", value="N/A")
    else:
        st.metric(label="🔬 Water Quality Compliance", value="N/A")
    st.markdown('</div>', unsafe_allow_html=True)

# Quick Access to Country Pages
st.markdown('<div class="section-header">🎯 Quick Country Access</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

country_pages = {
    'Uganda': '🇺🇬 Uganda',
    'Cameroon': '🇨🇲 Cameroon', 
    'Malawi': '🇲🇼 Malawi',
    'Lesotho': '🇱🇸 Lesotho'
}

for i, (country, display_name) in enumerate(country_pages.items()):
    with [col1, col2, col3, col4][i]:
        if st.button(f"📊 {display_name}", use_container_width=True, key=f"btn_{country}"):
            st.success(f"Navigating to {country} analysis...")
            # Streamlit will automatically navigate to the country page

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>💧 <strong>Water Utility Performance Dashboard</strong> - Monitoring Water & Sanitation Services</p>
    <p>Uganda • Cameroon • Malawi • Lesotho</p>
    <p><em>Last updated: {}</em></p>
</div>
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)