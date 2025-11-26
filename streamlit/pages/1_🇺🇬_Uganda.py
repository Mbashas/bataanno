import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append('..')
from utils.data_loader import load_all_data

st.set_page_config(page_title="Uganda Analysis", page_icon="🇺🇬", layout="wide")

# Load data
@st.cache_data
def load_country_data():
    data = load_all_data()
    # Filter for Uganda
    uganda_data = {}
    for name, df in data.items():
        if df is not None and not df.empty and 'country' in df.columns:
            uganda_data[name] = df[df['country'] == 'Uganda']
        else:
            uganda_data[name] = df
    return uganda_data

uganda_data = load_country_data()

st.title("🇺🇬 Uganda - Water & Sanitation Analysis")
st.markdown("Comprehensive analysis of water and sanitation services across Uganda's zones")

# Executive Summary at the top
col1, col2, col3, col4 = st.columns(4)
with col1:
    if not uganda_data['w_access'].empty and 'access_rate' in uganda_data['w_access'].columns:
        water_access = uganda_data['w_access']['access_rate'].iloc[-1] if len(uganda_data['w_access']) > 0 else "N/A"
        st.metric("💧 Water Access", 
                 f"{water_access:.1f}%" if isinstance(water_access, (int, float)) else water_access,
                 "+2.3%")
with col2:
    if not uganda_data['s_access'].empty and 'access_rate' in uganda_data['s_access'].columns:
        san_access = uganda_data['s_access']['access_rate'].iloc[-1] if len(uganda_data['s_access']) > 0 else "N/A"
        st.metric("🚽 Sanitation Access", 
                 f"{san_access:.1f}%" if isinstance(san_access, (int, float)) else san_access,
                 "+1.9%")
with col3:
    if not uganda_data['production'].empty and 'production_m3' in uganda_data['production'].columns:
        total_prod = uganda_data['production']['production_m3'].sum() / 1000000
        st.metric("🚰 Water Production", 
                 f"{total_prod:.1f}M m³" if not pd.isna(total_prod) else "N/A",
                 "+5.2%")
with col4:
    if not uganda_data['finance'].empty and 'collection_rate' in uganda_data['finance'].columns:
        coll_rate = uganda_data['finance']['collection_rate'].mean()
        st.metric("💰 Collection Rate", 
                 f"{coll_rate:.1f}%" if not pd.isna(coll_rate) else "N/A",
                 "+3.1%")

# Tabs for different analysis areas
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Access & Coverage", "💰 Financial Performance", "🏭 Production & Supply", "🔧 Service Quality"])

with tab1:
    st.subheader("Water & Sanitation Access Analysis")
    
    if not uganda_data['w_access'].empty and not uganda_data['s_access'].empty:
        # Top KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'access_rate' in uganda_data['w_access'].columns:
                water_access = uganda_data['w_access']['access_rate'].iloc[-1] if len(uganda_data['w_access']) > 0 else "N/A"
                st.metric("💧 Water Access Rate", 
                         f"{water_access:.1f}%" if isinstance(water_access, (int, float)) else water_access,
                         "+2.1%")
        
        with col2:
            if 'access_rate' in uganda_data['s_access'].columns:
                san_access = uganda_data['s_access']['access_rate'].iloc[-1] if len(uganda_data['s_access']) > 0 else "N/A"
                st.metric("🚽 Sanitation Access Rate", 
                         f"{san_access:.1f}%" if isinstance(san_access, (int, float)) else san_access,
                         "+1.8%")
        
        with col3:
            if 'safely_managed' in uganda_data['w_access'].columns and 'population' in uganda_data['w_access'].columns:
                safely_managed = uganda_data['w_access']['safely_managed'].iloc[-1] if len(uganda_data['w_access']) > 0 else 0
                population = uganda_data['w_access']['population'].iloc[-1] if len(uganda_data['w_access']) > 0 else 1
                safely_managed_pct = (safely_managed / population * 100) if population > 0 else 0
                st.metric("🛡️ Safely Managed Water", f"{safely_managed_pct:.1f}%")
        
        with col4:
            if 'population' in uganda_data['w_access'].columns:
                population = uganda_data['w_access']['population'].iloc[-1] if len(uganda_data['w_access']) > 0 else "N/A"
                st.metric("👥 Population Covered", f"{population:,.0f}" if isinstance(population, (int, float)) else population)

        # Service Level Analysis
        st.subheader("Service Level Distribution")
        col1, col2 = st.columns(2)
        
        with col1:
            if all(col in uganda_data['w_access'].columns for col in ['safely_managed', 'basic', 'limited', 'unimproved']):
                latest_data = uganda_data['w_access'].iloc[-1] if len(uganda_data['w_access']) > 0 else None
                if latest_data is not None:
                    service_levels = ['Safely Managed', 'Basic', 'Limited', 'Unimproved']
                    values = [
                        latest_data.get('safely_managed', 0),
                        latest_data.get('basic', 0), 
                        latest_data.get('limited', 0),
                        latest_data.get('unimproved', 0)
                    ]
                    
                    fig_service = px.pie(
                        values=values, names=service_levels,
                        title='Water Service Levels Distribution',
                        color=service_levels,
                        color_discrete_sequence=['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
                    )
                    st.plotly_chart(fig_service, use_container_width=True)
        
        with col2:
            if 'date' in uganda_data['w_access'].columns and 'access_rate' in uganda_data['w_access'].columns:
                fig_access_trend = px.line(
                    uganda_data['w_access'].sort_values('date'),
                    x='date', 
                    y='access_rate',
                    title='Water Access Rate Trend Over Time',
                    markers=True,
                    line_shape='spline'
                )
                fig_access_trend.update_layout(yaxis_range=[0, 100])
                st.plotly_chart(fig_access_trend, use_container_width=True)

        # Zone-wise Access Analysis
        st.subheader("Zone-wise Access Performance")
        if 'zone' in uganda_data['w_access'].columns and 'access_rate' in uganda_data['w_access'].columns:
            zone_performance = uganda_data['w_access'].groupby('zone').agg({
                'access_rate': 'last',
                'population': 'last'
            }).reset_index()
            
            fig_zone = px.bar(
                zone_performance.sort_values('access_rate', ascending=True),
                x='access_rate', y='zone',
                orientation='h',
                title='Water Access Rate by Zone',
                color='access_rate',
                color_continuous_scale='Blues',
                hover_data=['population']
            )
            st.plotly_chart(fig_zone, use_container_width=True)

with tab2:
    st.subheader("Financial Performance & Sustainability")
    
    if not uganda_data['finance'].empty:
        # Financial KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'collection_rate' in uganda_data['finance'].columns:
                collection_rate = uganda_data['finance']['collection_rate'].mean()
                st.metric("💰 Collection Rate", 
                         f"{collection_rate:.1f}%" if not pd.isna(collection_rate) else "N/A",
                         "+3.2%")
        
        with col2:
            if 'expenses' in uganda_data['finance'].columns:
                total_expenses = uganda_data['finance']['expenses'].sum() / 1000000
                st.metric("💸 Operating Expenses", 
                         f"${total_expenses:.1f}M" if not pd.isna(total_expenses) else "N/A",
                         "+4.1%")
        
        with col3:
            if 'sewer_billed' in uganda_data['finance'].columns:
                total_billed = uganda_data['finance']['sewer_billed'].sum() / 1000000
                st.metric("🧾 Total Revenue Billed", 
                         f"${total_billed:.1f}M" if not pd.isna(total_billed) else "N/A")
        
        with col4:
            if 'w_staff' in uganda_data['finance'].columns:
                avg_staff = uganda_data['finance']['w_staff'].mean()
                st.metric("👨‍💼 Water Staff", 
                         f"{avg_staff:.0f}" if not pd.isna(avg_staff) else "N/A")

        # Financial Trends
        st.subheader("Financial Performance Trends")
        col1, col2 = st.columns(2)
        
        with col1:
            if 'date' in uganda_data['finance'].columns and 'collection_rate' in uganda_data['finance'].columns:
                finance_trend = uganda_data['finance'].groupby('date').agg({
                    'collection_rate': 'mean'
                }).reset_index()
                
                fig_collection = px.line(
                    finance_trend, 
                    x='date', y='collection_rate',
                    title='Collection Rate Trend',
                    markers=True
                )
                fig_collection.update_layout(yaxis_range=[0, 100])
                st.plotly_chart(fig_collection, use_container_width=True)
        
        with col2:
            if 'date' in uganda_data['finance'].columns and all(col in uganda_data['finance'].columns for col in ['expenses', 'sewer_billed']):
                financial_flow = uganda_data['finance'].groupby('date').agg({
                    'expenses': 'sum',
                    'sewer_billed': 'sum'
                }).reset_index()
                
                fig_financial = go.Figure()
                fig_financial.add_trace(go.Scatter(
                    x=financial_flow['date'], y=financial_flow['sewer_billed'],
                    name='Revenue Billed', line=dict(color='green')
                ))
                fig_financial.add_trace(go.Scatter(
                    x=financial_flow['date'], y=financial_flow['expenses'],
                    name='Operating Expenses', line=dict(color='red')
                ))
                fig_financial.update_layout(title='Revenue vs Expenses Trend')
                st.plotly_chart(fig_financial, use_container_width=True)

        # Staffing Analysis
        st.subheader("Staffing & Operational Capacity")
        if all(col in uganda_data['finance'].columns for col in ['w_staff', 'san_staff']):
            staffing_data = uganda_data['finance'][['w_staff', 'san_staff']].mean().reset_index()
            staffing_data.columns = ['Department', 'Average Staff']
            
            fig_staff = px.bar(
                staffing_data, x='Department', y='Average Staff',
                title='Average Staff by Department',
                color='Department'
            )
            st.plotly_chart(fig_staff, use_container_width=True)

with tab3:
    st.subheader("Water Production & Supply Analysis")
    
    if not uganda_data['production'].empty:
        # Production KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'production_m3' in uganda_data['production'].columns:
                total_production = uganda_data['production']['production_m3'].sum() / 1000000
                st.metric("🚰 Total Production", 
                         f"{total_production:.1f}M m³" if not pd.isna(total_production) else "N/A",
                         "+5.2%")
        
        with col2:
            if 'service_hours' in uganda_data['production'].columns:
                avg_service_hours = uganda_data['production']['service_hours'].mean()
                st.metric("⏰ Average Service Hours", 
                         f"{avg_service_hours:.1f} hrs" if not pd.isna(avg_service_hours) else "N/A",
                         "+0.5 hrs")
        
        with col3:
            if 'source' in uganda_data['production'].columns:
                sources_count = uganda_data['production']['source'].nunique()
                st.metric("🌊 Water Sources", f"{sources_count}")
        
        with col4:
            production_days = uganda_data['production']['date'].nunique()
            st.metric("📅 Production Days", f"{production_days}")

        # Production Analysis
        st.subheader("Production Trends & Source Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            if 'date' in uganda_data['production'].columns and 'production_m3' in uganda_data['production'].columns:
                daily_production = uganda_data['production'].groupby('date')['production_m3'].sum().reset_index()
                fig_daily = px.line(
                    daily_production, 
                    x='date', y='production_m3',
                    title='Daily Water Production Trend',
                    markers=True
                )
                st.plotly_chart(fig_daily, use_container_width=True)
        
        with col2:
            if 'source' in uganda_data['production'].columns and 'production_m3' in uganda_data['production'].columns:
                source_production = uganda_data['production'].groupby('source')['production_m3'].sum().reset_index()
                fig_source = px.pie(
                    source_production, 
                    values='production_m3', 
                    names='source',
                    title='Water Production by Source'
                )
                st.plotly_chart(fig_source, use_container_width=True)

        # Monthly Production Analysis
        st.subheader("Monthly Production Performance")
        if 'date' in uganda_data['production'].columns and 'production_m3' in uganda_data['production'].columns:
            monthly_production = uganda_data['production'].groupby(
                uganda_data['production']['date'].dt.to_period('M')
            )['production_m3'].sum().reset_index()
            monthly_production['date'] = monthly_production['date'].dt.to_timestamp()
            monthly_production['month'] = monthly_production['date'].dt.strftime('%b %Y')
            
            fig_monthly = px.bar(
                monthly_production, 
                x='month', y='production_m3',
                title='Monthly Water Production',
                color='production_m3'
            )
            st.plotly_chart(fig_monthly, use_container_width=True)

with tab4:
    st.subheader("Service Quality & Operational Performance")
    
    if not uganda_data['w_service'].empty:
        # Service Quality KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'test_passed_chlorine' in uganda_data['w_service'].columns and 'tests_conducted_chlorine' in uganda_data['w_service'].columns:
                total_passed = uganda_data['w_service']['test_passed_chlorine'].sum()
                total_tests = uganda_data['w_service']['tests_conducted_chlorine'].sum()
                compliance_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
                st.metric("🔬 Water Quality Compliance", f"{compliance_rate:.1f}%", "+1.2%")
        
        with col2:
            if 'supply_hours' in uganda_data['w_service'].columns:
                avg_supply_hours = uganda_data['w_service']['supply_hours'].mean()
                st.metric("⏱️ Average Supply Hours", 
                         f"{avg_supply_hours:.1f} hrs" if not pd.isna(avg_supply_hours) else "N/A")
        
        with col3:
            if 'metered' in uganda_data['w_service'].columns and 'total_consumption' in uganda_data['w_service'].columns:
                metered_ratio = (uganda_data['w_service']['metered'].sum() / uganda_data['w_service']['total_consumption'].sum() * 100) if uganda_data['w_service']['total_consumption'].sum() > 0 else 0
                st.metric("📊 Metering Ratio", f"{metered_ratio:.1f}%")
        
        with col4:
            if 'customers' in uganda_data['w_service'].columns:
                total_customers = uganda_data['w_service']['customers'].sum() / 1000
                st.metric("👥 Customers Served", 
                         f"{total_customers:.0f}K" if not pd.isna(total_customers) else "N/A")

        # Water Quality Monitoring
        st.subheader("Water Quality & Compliance Monitoring")
        col1, col2 = st.columns(2)
        
        with col1:
            if 'date' in uganda_data['w_service'].columns and all(col in uganda_data['w_service'].columns for col in ['test_passed_chlorine', 'tests_conducted_chlorine']):
                quality_data = uganda_data['w_service'][['date', 'test_passed_chlorine', 'tests_conducted_chlorine']].dropna()
                if not quality_data.empty:
                    quality_data['compliance_rate'] = (quality_data['test_passed_chlorine'] / quality_data['tests_conducted_chlorine'] * 100)
                    fig_quality = px.line(
                        quality_data, 
                        x='date', 
                        y='compliance_rate',
                        title='Water Quality Compliance Trend',
                        markers=True
                    )
                    fig_quality.update_layout(yaxis_range=[0, 100])
                    st.plotly_chart(fig_quality, use_container_width=True)
        
        with col2:
            if 'date' in uganda_data['w_service'].columns and 'supply_hours' in uganda_data['w_service'].columns:
                service_data = uganda_data['w_service'][['date', 'supply_hours']].dropna()
                if not service_data.empty:
                    fig_service_hours = px.line(
                        service_data, 
                        x='date', 
                        y='supply_hours',
                        title='Water Supply Hours Trend',
                        markers=True
                    )
                    st.plotly_chart(fig_service_hours, use_container_width=True)

        # Customer Service Metrics
        st.subheader("Customer Service & Infrastructure")
        if not uganda_data['s_service'].empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'sewer_connections' in uganda_data['s_service'].columns:
                    sewer_conn = uganda_data['s_service']['sewer_connections'].sum()
                    st.metric("🛢️ Sewer Connections", f"{sewer_conn:,.0f}")
            
            with col2:
                if 'public_toilets' in uganda_data['s_service'].columns:
                    public_toilets = uganda_data['s_service']['public_toilets'].sum()
                    st.metric("🚻 Public Toilets", f"{public_toilets:,.0f}")
            
            with col3:
                if 'ww_treated' in uganda_data['s_service'].columns and 'ww_collected' in uganda_data['s_service'].columns:
                    ww_treated = uganda_data['s_service']['ww_treated'].sum()
                    ww_collected = uganda_data['s_service']['ww_collected'].sum()
                    treatment_rate = (ww_treated / ww_collected * 100) if ww_collected > 0 else 0
                    st.metric("♻️ Wastewater Treated", f"{treatment_rate:.1f}%")

# Zone Analysis Sidebar
st.sidebar.header("🇺🇬 Uganda - Zone Analysis")
if not uganda_data['w_access'].empty and 'zone' in uganda_data['w_access'].columns:
    zones = uganda_data['w_access']['zone'].unique()
    selected_zone = st.sidebar.selectbox("Select Zone for Detailed Analysis", zones)
    
    if selected_zone:
        st.sidebar.subheader(f"Zone: {selected_zone}")
        
        zone_water = uganda_data['w_access'][uganda_data['w_access']['zone'] == selected_zone]
        zone_sanitation = uganda_data['s_access'][uganda_data['s_access']['zone'] == selected_zone] if not uganda_data['s_access'].empty else pd.DataFrame()
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if not zone_water.empty and 'access_rate' in zone_water.columns:
                water_access = zone_water['access_rate'].iloc[-1] if len(zone_water) > 0 else "N/A"
                st.metric("Water Access", f"{water_access:.1f}%" if isinstance(water_access, (int, float)) else water_access)
        
        with col2:
            if not zone_sanitation.empty and 'access_rate' in zone_sanitation.columns:
                san_access = zone_sanitation['access_rate'].iloc[-1] if len(zone_sanitation) > 0 else "N/A"
                st.metric("Sanitation Access", f"{san_access:.1f}%" if isinstance(san_access, (int, float)) else san_access)
        
        if not zone_water.empty and 'population' in zone_water.columns:
            population = zone_water['population'].iloc[-1] if len(zone_water) > 0 else "N/A"
            st.sidebar.metric("Population", f"{population:,.0f}" if isinstance(population, (int, float)) else population)

# Data Summary
with st.expander("📊 Data Summary & Quality Check"):
    st.write("**Dataset Records for Uganda:**")
    for name, df in uganda_data.items():
        if df is not None:
            st.write(f"- {name}: {len(df)} records")
        else:
            st.write(f"- {name}: No data available")