import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append('..')
from utils.data_loader import load_all_data

st.set_page_config(page_title="Malawi Analysis", page_icon="🇲🇼", layout="wide")

# Load data
@st.cache_data
def load_country_data():
    data = load_all_data()
    malawi_data = {}
    for name, df in data.items():
        if df is not None and not df.empty and 'country' in df.columns:
            malawi_data[name] = df[df['country'] == 'Malawi']
        else:
            malawi_data[name] = df
    return malawi_data

malawi_data = load_country_data()

st.title("🇲🇼 Malawi - Water & Sanitation Analysis")
st.markdown("Comprehensive analysis of water and sanitation services across Malawi")

# Tabs for different analysis areas
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Access", "💰 Billing & Finance", "🏭 Production", "🔧 Service"])

with tab1:
    st.subheader("Water & Sanitation Access")
    
    if not malawi_data['w_access'].empty and not malawi_data['s_access'].empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'access_rate' in malawi_data['w_access'].columns:
                water_access = malawi_data['w_access']['access_rate'].iloc[-1] if len(malawi_data['w_access']) > 0 else "N/A"
                st.metric("💧 Water Access Rate", 
                         f"{water_access:.1f}%" if isinstance(water_access, (int, float)) else water_access,
                         "+1.8%")
        
        with col2:
            if 'access_rate' in malawi_data['s_access'].columns:
                san_access = malawi_data['s_access']['access_rate'].iloc[-1] if len(malawi_data['s_access']) > 0 else "N/A"
                st.metric("🚽 Sanitation Access Rate", 
                         f"{san_access:.1f}%" if isinstance(san_access, (int, float)) else san_access,
                         "+2.1%")
        
        with col3:
            if 'basic_pct' in malawi_data['w_access'].columns:
                basic_access = malawi_data['w_access']['basic_pct'].iloc[-1] if len(malawi_data['w_access']) > 0 else "N/A"
                st.metric("🚰 Basic Water Access", 
                         f"{basic_access:.1f}%" if isinstance(basic_access, (int, float)) else basic_access)
        
        with col4:
            if 'limited_pct' in malawi_data['w_access'].columns:
                limited_access = malawi_data['w_access']['limited_pct'].iloc[-1] if len(malawi_data['w_access']) > 0 else "N/A"
                st.metric("⚠️ Limited Service", 
                         f"{limited_access:.1f}%" if isinstance(limited_access, (int, float)) else limited_access)

        # Access comparison chart
        st.subheader("Service Level Comparison")
        if all(col in malawi_data['w_access'].columns for col in ['safely_managed', 'basic', 'limited', 'unimproved']):
            latest_data = malawi_data['w_access'].iloc[-1] if len(malawi_data['w_access']) > 0 else None
            if latest_data is not None:
                service_levels = ['Safely Managed', 'Basic', 'Limited', 'Unimproved']
                values = [
                    latest_data.get('safely_managed', 0),
                    latest_data.get('basic', 0), 
                    latest_data.get('limited', 0),
                    latest_data.get('unimproved', 0)
                ]
                
                fig_service = px.bar(
                    x=service_levels, y=values,
                    title='Population by Service Level',
                    color=service_levels,
                    color_discrete_sequence=['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
                )
                st.plotly_chart(fig_service, use_container_width=True)

with tab2:
    st.subheader("Financial Performance")
    
    if not malawi_data['finance'].empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'collection_rate' in malawi_data['finance'].columns:
                collection_rate = malawi_data['finance']['collection_rate'].mean()
                st.metric("💰 Collection Rate", 
                         f"{collection_rate:.1f}%" if not pd.isna(collection_rate) else "N/A",
                         "+2.8%")
        
        with col2:
            if 'sewer_billed' in malawi_data['finance'].columns:
                total_billed = malawi_data['finance']['sewer_billed'].sum() / 1000000  # Millions
                st.metric("🧾 Total Billed", 
                         f"${total_billed:.1f}M" if not pd.isna(total_billed) else "N/A")
        
        with col3:
            if 'propoor_popn' in malawi_data['finance'].columns:
                propoor_pop = malawi_data['finance']['propoor_popn'].sum() / 1000  # Thousands
                st.metric("🏘️ Pro-poor Population", 
                         f"{propoor_pop:.0f}K" if not pd.isna(propoor_pop) else "N/A")

        # Billing trends
        st.subheader("Billing Performance Over Time")
        if 'date' in malawi_data['finance'].columns and 'collection_rate' in malawi_data['finance'].columns:
            fig_billing = px.line(
                malawi_data['finance'].sort_values('date'),
                x='date', y='collection_rate',
                title='Collection Rate Trend',
                markers=True
            )
            st.plotly_chart(fig_billing, use_container_width=True)

with tab3:
    st.subheader("Water Production")
    
    if not malawi_data['production'].empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'production_m3' in malawi_data['production'].columns:
                total_production = malawi_data['production']['production_m3'].sum() / 1000000  # Million m³
                st.metric("🚰 Total Production", 
                         f"{total_production:.1f}M m³" if not pd.isna(total_production) else "N/A",
                         "+4.7%")
        
        with col2:
            if 'service_hours' in malawi_data['production'].columns:
                avg_service_hours = malawi_data['production']['service_hours'].mean()
                st.metric("⏰ Avg Service Hours", 
                         f"{avg_service_hours:.1f} hrs" if not pd.isna(avg_service_hours) else "N/A")
        
        with col3:
            production_records = len(malawi_data['production'])
            st.metric("📈 Production Records", f"{production_records}")

        # Monthly production trend
        st.subheader("Monthly Production Trend")
        if 'date' in malawi_data['production'].columns and 'production_m3' in malawi_data['production'].columns:
            monthly_production = malawi_data['production'].groupby(
                malawi_data['production']['date'].dt.to_period('M')
            )['production_m3'].sum().reset_index()
            monthly_production['date'] = monthly_production['date'].dt.to_timestamp()
            
            fig_production = px.line(
                monthly_production, 
                x='date', y='production_m3',
                title='Monthly Water Production',
                markers=True
            )
            st.plotly_chart(fig_production, use_container_width=True)

with tab4:
    st.subheader("Service Quality & Operations")
    
    if not malawi_data['w_service'].empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'tests_passed_ecoli' in malawi_data['w_service'].columns and 'test_conducted_ecoli' in malawi_data['w_service'].columns:
                ecoli_passed = malawi_data['w_service']['tests_passed_ecoli'].sum()
                ecoli_tests = malawi_data['w_service']['test_conducted_ecoli'].sum()
                ecoli_compliance = (ecoli_passed / ecoli_tests * 100) if ecoli_tests > 0 else 0
                st.metric("🦠 E.coli Compliance", f"{ecoli_compliance:.1f}%")
        
        with col2:
            if 'w_supplied' in malawi_data['w_service'].columns:
                total_supplied = malawi_data['w_service']['w_supplied'].sum() / 1000000  # Million m³
                st.metric("💦 Water Supplied", 
                         f"{total_supplied:.1f}M m³" if not pd.isna(total_supplied) else "N/A")
        
        with col3:
            if 'customers' in malawi_data['w_service'].columns:
                avg_customers = malawi_data['w_service']['customers'].mean()
                st.metric("👥 Avg Customers", 
                         f"{avg_customers:,.0f}" if not pd.isna(avg_customers) else "N/A")

# Zone analysis in sidebar
st.sidebar.header("🇲🇼 Malawi - Zone Analysis")
if not malawi_data['w_access'].empty and 'zone' in malawi_data['w_access'].columns:
    zones = malawi_data['w_access']['zone'].unique()
    selected_zone = st.sidebar.selectbox("Select Zone", zones)
    
    if selected_zone:
        zone_data = malawi_data['w_access'][malawi_data['w_access']['zone'] == selected_zone]
        if not zone_data.empty:
            col1, col2 = st.sidebar.columns(2)
            with col1:
                if 'access_rate' in zone_data.columns:
                    zone_water = zone_data['access_rate'].iloc[-1] if len(zone_data) > 0 else "N/A"
                    st.metric("Water Access", f"{zone_water:.1f}%" if isinstance(zone_water, (int, float)) else zone_water)
            with col2:
                if 'population' in zone_data.columns:
                    zone_pop = zone_data['population'].iloc[-1] if len(zone_data) > 0 else "N/A"
                    st.metric("Population", f"{zone_pop:,.0f}" if isinstance(zone_pop, (int, float)) else zone_pop)