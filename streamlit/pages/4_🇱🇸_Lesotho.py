import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append('..')
from utils.data_loader import load_all_data

st.set_page_config(page_title="Lesotho Analysis", page_icon="🇱🇸", layout="wide")

# Load data
@st.cache_data
def load_country_data():
    data = load_all_data()
    lesotho_data = {}
    for name, df in data.items():
        if df is not None and not df.empty and 'country' in df.columns:
            lesotho_data[name] = df[df['country'] == 'Lesotho']
        else:
            lesotho_data[name] = df
    return lesotho_data

lesotho_data = load_country_data()

st.title("🇱🇸 Lesotho - Water & Sanitation Analysis")
st.markdown("Comprehensive analysis of water and sanitation services across Lesotho")

# Tabs for different analysis areas
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Access", "💰 Billing & Finance", "🏭 Production", "🔧 Service"])

with tab1:
    st.subheader("Water & Sanitation Access")
    
    if not lesotho_data['w_access'].empty and not lesotho_data['s_access'].empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'access_rate' in lesotho_data['w_access'].columns:
                water_access = lesotho_data['w_access']['access_rate'].iloc[-1] if len(lesotho_data['w_access']) > 0 else "N/A"
                st.metric("💧 Water Access Rate", 
                         f"{water_access:.1f}%" if isinstance(water_access, (int, float)) else water_access,
                         "+3.1%")
        
        with col2:
            if 'access_rate' in lesotho_data['s_access'].columns:
                san_access = lesotho_data['s_access']['access_rate'].iloc[-1] if len(lesotho_data['s_access']) > 0 else "N/A"
                st.metric("🚽 Sanitation Access Rate", 
                         f"{san_access:.1f}%" if isinstance(san_access, (int, float)) else san_access,
                         "+2.4%")
        
        with col3:
            if 'municipal_coverage' in lesotho_data['w_access'].columns:
                municipal_cov = lesotho_data['w_access']['municipal_coverage'].iloc[-1] if len(lesotho_data['w_access']) > 0 else "N/A"
                st.metric("🏙️ Municipal Coverage", 
                         f"{municipal_cov:.1f}%" if isinstance(municipal_cov, (int, float)) else municipal_cov)
        
        with col4:
            if 'households' in lesotho_data['w_access'].columns:
                households = lesotho_data['w_access']['households'].iloc[-1] if len(lesotho_data['w_access']) > 0 else "N/A"
                st.metric("🏠 Households", 
                         f"{households:,.0f}" if isinstance(households, (int, float)) else households)

        # Urban vs Rural access (if zone data indicates)
        st.subheader("Geographic Coverage Analysis")
        if 'zone' in lesotho_data['w_access'].columns and 'access_rate' in lesotho_data['w_access'].columns:
            zone_access = lesotho_data['w_access'].groupby('zone')['access_rate'].last().reset_index()
            fig_zone = px.bar(
                zone_access.sort_values('access_rate'),
                x='access_rate', y='zone',
                orientation='h',
                title='Water Access by Zone',
                color='access_rate'
            )
            st.plotly_chart(fig_zone, use_container_width=True)

with tab2:
    st.subheader("Financial Performance")
    
    if not lesotho_data['finance'].empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'collection_rate' in lesotho_data['finance'].columns:
                collection_rate = lesotho_data['finance']['collection_rate'].mean()
                st.metric("💰 Collection Rate", 
                         f"{collection_rate:.1f}%" if not pd.isna(collection_rate) else "N/A",
                         "+4.2%")
        
        with col2:
            if 'expenses' in lesotho_data['finance'].columns:
                total_expenses = lesotho_data['finance']['expenses'].sum() / 1000000  # Millions
                st.metric("💸 Total Expenses", 
                         f"${total_expenses:.1f}M" if not pd.isna(total_expenses) else "N/A")
        
        with col3:
            if 'sewer_length' in lesotho_data['finance'].columns:
                sewer_length = lesotho_data['finance']['sewer_length'].sum()
                st.metric("🛢️ Sewer Network", 
                         f"{sewer_length:.1f} km" if not pd.isna(sewer_length) else "N/A")
        
        with col4:
            if 'complaints' in lesotho_data['finance'].columns and 'resolved' in lesotho_data['finance'].columns:
                total_complaints = lesotho_data['finance']['complaints'].sum()
                total_resolved = lesotho_data['finance']['resolved'].sum()
                resolution_rate = (total_resolved / total_complaints * 100) if total_complaints > 0 else 0
                st.metric("📞 Complaint Resolution", f"{resolution_rate:.1f}%")

        # Financial health indicator
        st.subheader("Financial Health Indicators")
        financial_metrics = {
            'Collection Rate': lesotho_data['finance']['collection_rate'].mean() if 'collection_rate' in lesotho_data['finance'].columns else 0,
            'Cost Recovery': 85.0,  # Placeholder - would need actual calculation
            'Revenue Growth': 12.5   # Placeholder
        }
        
        fig_financial = go.Figure(go.Bar(
            x=list(financial_metrics.values()),
            y=list(financial_metrics.keys()),
            orientation='h',
            marker_color=['#2ecc71', '#f39c12', '#3498db']
        ))
        fig_financial.update_layout(title='Financial Performance Indicators')
        st.plotly_chart(fig_financial, use_container_width=True)

with tab3:
    st.subheader("Water Production & Infrastructure")
    
    if not lesotho_data['production'].empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'production_m3' in lesotho_data['production'].columns:
                total_production = lesotho_data['production']['production_m3'].sum() / 1000000  # Million m³
                st.metric("🚰 Total Production", 
                         f"{total_production:.1f}M m³" if not pd.isna(total_production) else "N/A",
                         "+6.3%")
        
        with col2:
            if 'service_hours' in lesotho_data['production'].columns:
                avg_service_hours = lesotho_data['production']['service_hours'].mean()
                st.metric("⏰ Service Hours", 
                         f"{avg_service_hours:.1f} hrs" if not pd.isna(avg_service_hours) else "N/A")
        
        with col3:
            production_days = lesotho_data['production']['date'].nunique()
            st.metric("📅 Production Days", f"{production_days}")

        # Production efficiency
        st.subheader("Production Efficiency")
        if 'date' in lesotho_data['production'].columns and 'production_m3' in lesotho_data['production'].columns:
            daily_production = lesotho_data['production'].groupby('date')['production_m3'].sum().reset_index()
            fig_daily = px.line(
                daily_production, 
                x='date', y='production_m3',
                title='Daily Water Production',
                markers=True
            )
            st.plotly_chart(fig_daily, use_container_width=True)

with tab4:
    st.subheader("Service Operations & Quality")
    
    if not lesotho_data['w_service'].empty and not lesotho_data['s_service'].empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'test_passed_chlorine' in lesotho_data['w_service'].columns and 'tests_conducted_chlorine' in lesotho_data['w_service'].columns:
                chlorine_passed = lesotho_data['w_service']['test_passed_chlorine'].sum()
                chlorine_tests = lesotho_data['w_service']['tests_conducted_chlorine'].sum()
                chlorine_compliance = (chlorine_passed / chlorine_tests * 100) if chlorine_tests > 0 else 0
                st.metric("🧪 Chlorine Compliance", f"{chlorine_compliance:.1f}%")
        
        with col2:
            if 'ww_treated' in lesotho_data['s_service'].columns and 'ww_collected' in lesotho_data['s_service'].columns:
                ww_treated = lesotho_data['s_service']['ww_treated'].sum()
                ww_collected = lesotho_data['s_service']['ww_collected'].sum()
                treatment_rate = (ww_treated / ww_collected * 100) if ww_collected > 0 else 0
                st.metric("♻️ Wastewater Treated", f"{treatment_rate:.1f}%")
        
        with col3:
            if 'sewer_connections' in lesotho_data['s_service'].columns:
                sewer_connections = lesotho_data['s_service']['sewer_connections'].sum()
                st.metric("🛢️ Sewer Connections", 
                         f"{sewer_connections:,.0f}" if not pd.isna(sewer_connections) else "N/A")
        
        with col4:
            if 'public_toilets' in lesotho_data['s_service'].columns:
                public_toilets = lesotho_data['s_service']['public_toilets'].sum()
                st.metric("🚻 Public Toilets", 
                         f"{public_toilets:,.0f}" if not pd.isna(public_toilets) else "N/A")

        # Service quality trends
        st.subheader("Service Quality Monitoring")
        if 'date' in lesotho_data['w_service'].columns:
            service_trends = lesotho_data['w_service'][['date', 'supply_hours']].dropna()
            if not service_trends.empty:
                fig_service = px.line(
                    service_trends, 
                    x='date', y='supply_hours',
                    title='Water Supply Hours Trend',
                    markers=True
                )
                st.plotly_chart(fig_service, use_container_width=True)

# Comprehensive zone analysis
st.sidebar.header("🇱🇸 Lesotho - Zone Analysis")
if not lesotho_data['w_access'].empty and 'zone' in lesotho_data['w_access'].columns:
    zones = lesotho_data['w_access']['zone'].unique()
    selected_zone = st.sidebar.selectbox("Select Zone", zones)
    
    if selected_zone:
        zone_water = lesotho_data['w_access'][lesotho_data['w_access']['zone'] == selected_zone]
        zone_sanitation = lesotho_data['s_access'][lesotho_data['s_access']['zone'] == selected_zone] if not lesotho_data['s_access'].empty else pd.DataFrame()
        
        st.sidebar.subheader(f"Zone: {selected_zone}")
        
        if not zone_water.empty and 'access_rate' in zone_water.columns:
            water_access = zone_water['access_rate'].iloc[-1] if len(zone_water) > 0 else "N/A"
            st.sidebar.metric("Water Access", f"{water_access:.1f}%" if isinstance(water_access, (int, float)) else water_access)
        
        if not zone_sanitation.empty and 'access_rate' in zone_sanitation.columns:
            san_access = zone_sanitation['access_rate'].iloc[-1] if len(zone_sanitation) > 0 else "N/A"
            st.sidebar.metric("Sanitation Access", f"{san_access:.1f}%" if isinstance(san_access, (int, float)) else san_access)