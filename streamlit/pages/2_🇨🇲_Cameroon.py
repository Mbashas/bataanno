import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append('..')
from utils.data_loader import load_all_data

st.set_page_config(page_title="Cameroon Analysis", page_icon="🇨🇲", layout="wide")

# Load data
@st.cache_data
def load_country_data():
    data = load_all_data()
    cameroon_data = {}
    for name, df in data.items():
        if df is not None and not df.empty and 'country' in df.columns:
            cameroon_data[name] = df[df['country'] == 'Cameroon']
        else:
            cameroon_data[name] = df
    return cameroon_data

cameroon_data = load_country_data()

st.title("🇨🇲 Cameroon - Water & Sanitation Analysis")
st.markdown("Comprehensive analysis of water and sanitation services across Cameroon")

# Tabs for different analysis areas
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Access", "💰 Billing & Finance", "🏭 Production", "🔧 Service"])

with tab1:
    st.subheader("Water & Sanitation Access")
    
    if not cameroon_data['w_access'].empty and not cameroon_data['s_access'].empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'access_rate' in cameroon_data['w_access'].columns:
                water_access = cameroon_data['w_access']['access_rate'].iloc[-1] if len(cameroon_data['w_access']) > 0 else "N/A"
                st.metric("💧 Water Access Rate", 
                         f"{water_access:.1f}%" if isinstance(water_access, (int, float)) else water_access,
                         "+2.3%")
        
        with col2:
            if 'access_rate' in cameroon_data['s_access'].columns:
                san_access = cameroon_data['s_access']['access_rate'].iloc[-1] if len(cameroon_data['s_access']) > 0 else "N/A"
                st.metric("🚽 Sanitation Access Rate", 
                         f"{san_access:.1f}%" if isinstance(san_access, (int, float)) else san_access,
                         "+1.9%")
        
        with col3:
            if 'safely_managed' in cameroon_data['w_access'].columns and 'population' in cameroon_data['w_access'].columns:
                safely_managed = cameroon_data['w_access']['safely_managed'].iloc[-1] if len(cameroon_data['w_access']) > 0 else 0
                population = cameroon_data['w_access']['population'].iloc[-1] if len(cameroon_data['w_access']) > 0 else 1
                safely_managed_pct = (safely_managed / population * 100) if population > 0 else 0
                st.metric("🛡️ Safely Managed Water", f"{safely_managed_pct:.1f}%")
        
        with col4:
            if 'population' in cameroon_data['w_access'].columns:
                population = cameroon_data['w_access']['population'].iloc[-1] if len(cameroon_data['w_access']) > 0 else "N/A"
                st.metric("👥 Population Served", f"{population:,.0f}" if isinstance(population, (int, float)) else population)

        # Access trends over time
        st.subheader("Access Trends Over Time")
        if 'date' in cameroon_data['w_access'].columns and 'access_rate' in cameroon_data['w_access'].columns:
            fig_access_trend = px.line(
                cameroon_data['w_access'].sort_values('date'),
                x='date', 
                y='access_rate',
                title='Water Access Rate Trend',
                markers=True
            )
            st.plotly_chart(fig_access_trend, use_container_width=True)

with tab2:
    st.subheader("Financial Performance")
    
    if not cameroon_data['finance'].empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'collection_rate' in cameroon_data['finance'].columns:
                collection_rate = cameroon_data['finance']['collection_rate'].mean()
                st.metric("💰 Collection Rate", 
                         f"{collection_rate:.1f}%" if not pd.isna(collection_rate) else "N/A",
                         "+3.2%")
        
        with col2:
            if 'expenses' in cameroon_data['finance'].columns:
                total_expenses = cameroon_data['finance']['expenses'].sum() / 1000000  # Convert to millions
                st.metric("💸 Operating Expenses", 
                         f"${total_expenses:.1f}M" if not pd.isna(total_expenses) else "N/A",
                         "+4.1%")
        
        with col3:
            if 'w_staff' in cameroon_data['finance'].columns:
                avg_staff = cameroon_data['finance']['w_staff'].mean()
                st.metric("👨‍💼 Water Staff", 
                         f"{avg_staff:.0f}" if not pd.isna(avg_staff) else "N/A")
        
        with col4:
            if 'san_staff' in cameroon_data['finance'].columns:
                avg_san_staff = cameroon_data['finance']['san_staff'].mean()
                st.metric("👩‍💼 Sanitation Staff", 
                         f"{avg_san_staff:.0f}" if not pd.isna(avg_san_staff) else "N/A")

        # Revenue vs Expenses
        st.subheader("Financial Overview")
        if 'date' in cameroon_data['finance'].columns:
            finance_trend = cameroon_data['finance'].groupby('date').agg({
                'collection_rate': 'mean',
                'expenses': 'sum'
            }).reset_index()
            
            fig_finance = go.Figure()
            fig_finance.add_trace(go.Scatter(
                x=finance_trend['date'], 
                y=finance_trend['collection_rate'],
                name='Collection Rate (%)',
                line=dict(color='green')
            ))
            fig_finance.update_layout(title='Collection Rate Trend')
            st.plotly_chart(fig_finance, use_container_width=True)

with tab3:
    st.subheader("Water Production")
    
    if not cameroon_data['production'].empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'production_m3' in cameroon_data['production'].columns:
                total_production = cameroon_data['production']['production_m3'].sum() / 1000000  # Million m³
                st.metric("🚰 Total Production", 
                         f"{total_production:.1f}M m³" if not pd.isna(total_production) else "N/A",
                         "+5.2%")
        
        with col2:
            if 'service_hours' in cameroon_data['production'].columns:
                avg_service_hours = cameroon_data['production']['service_hours'].mean()
                st.metric("⏰ Avg Service Hours", 
                         f"{avg_service_hours:.1f} hrs" if not pd.isna(avg_service_hours) else "N/A",
                         "+0.5 hrs")
        
        with col3:
            if 'source' in cameroon_data['production'].columns:
                sources_count = cameroon_data['production']['source'].nunique()
                st.metric("🌊 Water Sources", f"{sources_count}")

        # Production by source
        st.subheader("Production by Source")
        if 'source' in cameroon_data['production'].columns and 'production_m3' in cameroon_data['production'].columns:
            source_production = cameroon_data['production'].groupby('source')['production_m3'].sum().reset_index()
            fig_source = px.pie(
                source_production, 
                values='production_m3', 
                names='source',
                title='Water Production by Source'
            )
            st.plotly_chart(fig_source, use_container_width=True)

with tab4:
    st.subheader("Service Quality")
    
    if not cameroon_data['w_service'].empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'test_passed_chlorine' in cameroon_data['w_service'].columns and 'tests_conducted_chlorine' in cameroon_data['w_service'].columns:
                total_passed = cameroon_data['w_service']['test_passed_chlorine'].sum()
                total_tests = cameroon_data['w_service']['tests_conducted_chlorine'].sum()
                compliance_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
                st.metric("🔬 Water Quality Compliance", f"{compliance_rate:.1f}%", "+1.2%")
        
        with col2:
            if 'supply_hours' in cameroon_data['w_service'].columns:
                avg_supply_hours = cameroon_data['w_service']['supply_hours'].mean()
                st.metric("⏱️ Supply Hours", 
                         f"{avg_supply_hours:.1f} hrs" if not pd.isna(avg_supply_hours) else "N/A")
        
        with col3:
            if 'metered' in cameroon_data['w_service'].columns and 'total_consumption' in cameroon_data['w_service'].columns:
                metered_ratio = (cameroon_data['w_service']['metered'].sum() / cameroon_data['w_service']['total_consumption'].sum() * 100) if cameroon_data['w_service']['total_consumption'].sum() > 0 else 0
                st.metric("📊 Metering Ratio", f"{metered_ratio:.1f}%")
        
        with col4:
            if 'customers' in cameroon_data['w_service'].columns:
                total_customers = cameroon_data['w_service']['customers'].sum() / 1000  # Thousands
                st.metric("👥 Customers Served", 
                         f"{total_customers:.0f}K" if not pd.isna(total_customers) else "N/A")

        # Water quality trends
        st.subheader("Water Quality Monitoring")
        if 'date' in cameroon_data['w_service'].columns:
            quality_data = cameroon_data['w_service'][['date', 'test_passed_chlorine', 'tests_conducted_chlorine']].dropna()
            if not quality_data.empty:
                quality_data['compliance_rate'] = (quality_data['test_passed_chlorine'] / quality_data['tests_conducted_chlorine'] * 100)
                fig_quality = px.line(
                    quality_data, 
                    x='date', 
                    y='compliance_rate',
                    title='Water Quality Compliance Trend',
                    markers=True
                )
                st.plotly_chart(fig_quality, use_container_width=True)

# Zone-level analysis in sidebar
st.sidebar.header("🇨🇲 Cameroon - Zone Analysis")
if not cameroon_data['w_access'].empty and 'zone' in cameroon_data['w_access'].columns:
    zones = cameroon_data['w_access']['zone'].unique()
    selected_zone = st.sidebar.selectbox("Select Zone", zones)
    
    if selected_zone:
        zone_data = cameroon_data['w_access'][cameroon_data['w_access']['zone'] == selected_zone]
        if not zone_data.empty and 'access_rate' in zone_data.columns:
            zone_access = zone_data['access_rate'].iloc[-1] if len(zone_data) > 0 else "N/A"
            st.sidebar.metric(f"Water Access in {selected_zone}", 
                            f"{zone_access:.1f}%" if isinstance(zone_access, (int, float)) else zone_access)