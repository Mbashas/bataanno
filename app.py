import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Water & Sanitation Service Analytics",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('service_data.csv')
    df['date_parsed'] = pd.to_datetime(df['date'], format='%b %Y')
    
    # Calculate derived KPIs
    df['chlorine_execution_rate'] = (df['tests_conducted_chlorine'] / df['tests_chlorine'] * 100).round(2)
    df['chlorine_pass_rate'] = (df['test_passed_chlorine'] / df['tests_conducted_chlorine'] * 100).round(2)
    df['ecoli_execution_rate'] = (df['test_conducted_ecoli'] / df['tests_ecoli'] * 100).round(2)
    df['ecoli_pass_rate'] = (df['tests_passed_ecoli'] / df['test_conducted_ecoli'] * 100).round(2)
    df['complaint_resolution_efficiency'] = (df['resolved'] / df['complaints'] * 100).round(2)
    df['complaints_per_1000_hh'] = (df['complaints'] / df['households'] * 1000).round(2)
    df['female_workforce_ratio'] = (df['f_workforce'] / df['workforce'] * 100).round(2)
    df['connections_per_employee'] = (df['metered'] / df['workforce']).round(2)
    df['ww_capacity_utilization'] = (df['ww_treated'] / df['ww_capacity'] * 100).round(2)
    df['ww_collection_efficiency'] = (df['ww_collected'] / df['total_consumption'] * 100).round(2)
    df['ww_treatment_coverage'] = (df['ww_treated'] / df['ww_collected'] * 100).round(2)
    df['sewer_connection_density'] = (df['sewer_connections'] / df['households']).round(3)
    df['fs_service_coverage'] = (df['hh_emptied'] / df['households'] * 100).round(2)
    df['fs_reuse_rate'] = (df['fs_reused'] / df['fs_treated'] * 100).round(2)
    df['water_per_connection'] = (df['w_supplied'] / df['metered']).round(2)
    df['nrw_percentage'] = ((df['w_supplied'] - df['total_consumption']) / df['w_supplied'] * 100).round(2)
    df['metering_coverage'] = (df['metered'] / df['households'] * 100).round(2)
    df['population_estimate'] = df['households'] * 5
    df['people_per_toilet'] = (df['population_estimate'] / df['public_toilets']).round(0)
    
    return df

# Main page
def main():
    st.title("💧 Water & Sanitation Service Analytics Dashboard")
    st.markdown("### Multi-Country Service Performance Analysis (2020-2024)")
    st.markdown("""
    This interactive dashboard provides comprehensive analytics on water and sanitation services 
    across **Cameroon, Lesotho, Malawi, and Uganda**. Use the sidebar to navigate to country-specific 
    pages with advanced filtering capabilities.
    """)
    
    df = load_data()
    
    # Overview metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Records", f"{len(df):,}")
    with col2:
        st.metric("Countries", len(df['country'].unique()))
    with col3:
        st.metric("Date Range", f"{df['year'].min()}-{df['year'].max()}")
    with col4:
        st.metric("Total Households", f"{df['households'].sum():,.0f}")
    with col5:
        avg_ecoli = df['ecoli_pass_rate'].mean()
        st.metric("Avg E. Coli Pass", f"{avg_ecoli:.1f}%")
    
    st.markdown("---")
    
    # Country comparison
    st.subheader("📊 Country Comparison Dashboard")
    
    country_stats = df.groupby('country').agg({
        'households': 'sum',
        'workforce': 'sum',
        'metered': 'sum',
        'complaints': 'sum',
        'resolved': 'sum',
        'ecoli_pass_rate': 'mean',
        'complaints_per_1000_hh': 'mean',
        'metering_coverage': 'mean'
    }).round(2).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.bar(country_stats, x='country', y='households', 
                     title='Total Households by Country',
                     color='country',
                     text='households',
                     color_discrete_map={
                         'cameroon': '#1f77b4',
                         'lesotho': '#ff7f0e', 
                         'malawi': '#2ca02c',
                         'Uganda': '#d62728'
                     })
        fig1.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig1.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            name='E. Coli Pass Rate',
            x=country_stats['country'],
            y=country_stats['ecoli_pass_rate'],
            text=country_stats['ecoli_pass_rate'],
            texttemplate='%{text:.1f}%',
            marker_color='lightblue'
        ))
        fig2.add_hline(y=95, line_dash="dash", line_color="green",
                      annotation_text="WHO Target: 95%")
        fig2.update_layout(
            title='Average E. Coli Pass Rate by Country',
            xaxis_title='Country',
            yaxis_title='Pass Rate (%)',
            height=400,
            template='plotly_white'
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Multi-metric comparison
    st.subheader("🎯 Key Performance Indicators by Country")
    
    # Rename columns for better display
    display_stats = country_stats[['country', 'households', 'workforce', 'ecoli_pass_rate', 
                                    'complaints_per_1000_hh', 'metering_coverage']].copy()
    display_stats.columns = ['Country', 'Households', 'Workforce', 'E. Coli Pass Rate (%)',
                              'Complaints/1000 HH', 'Metering Coverage (%)']
    
    st.dataframe(display_stats, use_container_width=True)
    
    st.markdown("---")
    
    # Monthly trends
    st.subheader("📈 Cross-Country Trends")
    
    monthly_trends = df.groupby(['country', 'date_parsed']).agg({
        'ecoli_pass_rate': 'mean',
        'complaints_per_1000_hh': 'mean'
    }).reset_index()
    
    fig3 = px.line(monthly_trends, x='date_parsed', y='ecoli_pass_rate',
                   color='country', title='E. Coli Pass Rate Trends by Country',
                   labels={'ecoli_pass_rate': 'E. Coli Pass Rate (%)', 'date_parsed': 'Date'})
    fig3.update_layout(height=400, template='plotly_white')
    st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("---")
    
    # Featured insights
    st.subheader("🔍 Featured Insights by Country")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **🇨🇲 Cameroon (Yaounde)**
        - Wastewater treatment capacity underutilization
        - Strong water quality performance
        - Opportunities for faecal sludge reuse
        """)
        
        st.info("""
        **🇱🇸 Lesotho**
        - Water quality testing gaps in rural areas
        - Urban vs rural service disparities
        - Execution rate below 90% target
        """)
    
    with col2:
        st.info("""
        **🇲🇼 Malawi (Lilongwe)**
        - Public toilet infrastructure challenges
        - People per toilet exceeds WHO guidelines
        - Growing service demand
        """)
        
        st.warning("""
        **🇺🇬 Uganda (Kampala)**
        - Complaint resolution crisis in high-density zones
        - Resolution time exceeds 22 days on average
        - Nakawa zone shows highest complaint rates
        """)
    
    st.markdown("---")
    
    # Data preview
    st.subheader("📋 Data Preview")
    st.dataframe(df[['country', 'city', 'zone', 'date', 'year', 'households', 
                     'ecoli_pass_rate', 'complaints_per_1000_hh']].head(15), 
                use_container_width=True)
    
    # Sidebar
    st.sidebar.title("🌍 Navigation")
    st.sidebar.info("""
    👈 Select a country from the sidebar to explore detailed analytics with interactive filters.
    
    **Available Countries:**
    - 🇨🇲 Cameroon (Yaounde)
    - 🇱🇸 Lesotho (Urban & Rural)
    - 🇲🇼 Malawi (Lilongwe)
    - 🇺🇬 Uganda (Kampala)
    
    Each country page includes:
    - Date range and zone filters
    - Water quality monitoring
    - Customer service metrics
    - Infrastructure analysis
    - Operational efficiency
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Quick Stats")
    st.sidebar.metric("Countries", len(df['country'].unique()))
    st.sidebar.metric("Total Records", len(df))
    st.sidebar.metric("Date Range", f"{df['year'].min()}-{df['year'].max()}")

if __name__ == "__main__":
    main()

