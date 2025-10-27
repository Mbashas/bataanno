import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(page_title="Cameroon Analysis", page_icon="🇨🇲", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('service_data.csv')
    df['date_parsed'] = pd.to_datetime(df['date'], format='%b %Y')
    
    # Calculate all KPIs
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
    df['fs_reuse_rate'] = (df['fs_reused'] / df['fs_treated'] * 100).round(2)
    df['metering_coverage'] = (df['metered'] / df['households'] * 100).round(2)
    df['nrw_percentage'] = ((df['w_supplied'] - df['total_consumption']) / df['w_supplied'] * 100).round(2)
    
    return df

df = load_data()
cameroon_df = df[df['country'] == 'cameroon'].copy()

# Header
st.title("🇨🇲 Cameroon - Water & Sanitation Analytics")
st.markdown("### Comprehensive Service Performance Dashboard")

# Sidebar Filters
st.sidebar.header("🔍 Filters")

# Date range filter
min_date = cameroon_df['date_parsed'].min()
max_date = cameroon_df['date_parsed'].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Zone filter
zones = ['All'] + sorted(cameroon_df['zone'].unique().tolist())
selected_zones = st.sidebar.multiselect(
    "Select Zones",
    options=zones,
    default=['All']
)

# City filter
cities = ['All'] + sorted(cameroon_df['city'].unique().tolist())
selected_city = st.sidebar.selectbox("Select City", cities)

# Year filter
years = ['All'] + sorted(cameroon_df['year'].unique().tolist())
selected_years = st.sidebar.multiselect(
    "Select Years",
    options=years,
    default=['All']
)

# Apply filters
filtered_df = cameroon_df.copy()

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df['date_parsed'].dt.date >= start_date) & 
        (filtered_df['date_parsed'].dt.date <= end_date)
    ]

if 'All' not in selected_zones and selected_zones:
    filtered_df = filtered_df[filtered_df['zone'].isin(selected_zones)]

if selected_city != 'All':
    filtered_df = filtered_df[filtered_df['city'] == selected_city]

if 'All' not in selected_years and selected_years:
    filtered_df = filtered_df[filtered_df['year'].isin(selected_years)]

# Display filter summary
st.sidebar.markdown("---")
st.sidebar.metric("Filtered Records", len(filtered_df))

# Overview Metrics
st.subheader("📊 Key Performance Indicators")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    avg_ecoli = filtered_df['ecoli_pass_rate'].mean()
    st.metric("E. Coli Pass Rate", f"{avg_ecoli:.1f}%", 
              delta=f"{avg_ecoli - 95:.1f}%" if avg_ecoli < 95 else "✓")

with col2:
    avg_complaints = filtered_df['complaints_per_1000_hh'].mean()
    st.metric("Complaints/1000 HH", f"{avg_complaints:.1f}")

with col3:
    avg_resolution = filtered_df['complaint_resolution_efficiency'].mean()
    st.metric("Resolution Efficiency", f"{avg_resolution:.1f}%")

with col4:
    avg_utilization = filtered_df['ww_capacity_utilization'].mean()
    st.metric("WW Capacity Usage", f"{avg_utilization:.1f}%")

with col5:
    avg_metering = filtered_df['metering_coverage'].mean()
    st.metric("Metering Coverage", f"{avg_metering:.1f}%")

st.markdown("---")

# Visualization Tabs
tab1, tab2, tab3, tab4 = st.tabs(["💧 Water Quality", "🎧 Customer Service", "♻️ Wastewater", "📈 Operations"])

with tab1:
    st.subheader("Water Quality Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Chlorine vs E.Coli Pass Rates over time
        fig1 = go.Figure()
        
        monthly_wq = filtered_df.groupby('date_parsed').agg({
            'chlorine_pass_rate': 'mean',
            'ecoli_pass_rate': 'mean'
        }).reset_index()
        
        fig1.add_trace(go.Scatter(
            x=monthly_wq['date_parsed'],
            y=monthly_wq['chlorine_pass_rate'],
            name='Chlorine Pass Rate',
            line=dict(color='blue', width=2),
            mode='lines+markers'
        ))
        
        fig1.add_trace(go.Scatter(
            x=monthly_wq['date_parsed'],
            y=monthly_wq['ecoli_pass_rate'],
            name='E. Coli Pass Rate',
            line=dict(color='red', width=2),
            mode='lines+markers'
        ))
        
        fig1.add_hline(y=95, line_dash="dash", line_color="green",
                      annotation_text="WHO Target: 95%")
        
        fig1.update_layout(
            title='Water Quality Trends',
            xaxis_title='Date',
            yaxis_title='Pass Rate (%)',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Zone comparison
        zone_wq = filtered_df.groupby('zone').agg({
            'chlorine_pass_rate': 'mean',
            'ecoli_pass_rate': 'mean',
            'chlorine_execution_rate': 'mean',
            'ecoli_execution_rate': 'mean'
        }).round(2).reset_index()
        
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            name='Chlorine Pass Rate',
            x=zone_wq['zone'],
            y=zone_wq['chlorine_pass_rate'],
            text=zone_wq['chlorine_pass_rate'],
            texttemplate='%{text:.1f}%',
            marker_color='steelblue'
        ))
        
        fig2.add_trace(go.Bar(
            name='E. Coli Pass Rate',
            x=zone_wq['zone'],
            y=zone_wq['ecoli_pass_rate'],
            text=zone_wq['ecoli_pass_rate'],
            texttemplate='%{text:.1f}%',
            marker_color='lightcoral'
        ))
        
        fig2.update_layout(
            title='Water Quality by Zone',
            xaxis_title='Zone',
            yaxis_title='Pass Rate (%)',
            barmode='group',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Customer Service Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Complaints over time
        complaints_time = filtered_df.groupby('date_parsed').agg({
            'complaints': 'sum',
            'resolved': 'sum',
            'complaint_resolution': 'mean'
        }).reset_index()
        
        fig3 = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig3.add_trace(
            go.Bar(name='Total Complaints', x=complaints_time['date_parsed'], 
                   y=complaints_time['complaints'], marker_color='orange'),
            secondary_y=False
        )
        
        fig3.add_trace(
            go.Scatter(name='Avg Resolution Time (days)', 
                      x=complaints_time['date_parsed'],
                      y=complaints_time['complaint_resolution'],
                      mode='lines+markers', line=dict(color='red', width=3)),
            secondary_y=True
        )
        
        fig3.update_xaxes(title_text="Date")
        fig3.update_yaxes(title_text="Total Complaints", secondary_y=False)
        fig3.update_yaxes(title_text="Resolution Time (days)", secondary_y=True)
        
        fig3.update_layout(
            title='Complaints & Resolution Time Trends',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Zone performance
        zone_complaints = filtered_df.groupby('zone').agg({
            'complaints_per_1000_hh': 'mean',
            'complaint_resolution_efficiency': 'mean'
        }).round(2).reset_index()
        
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            x=zone_complaints['zone'],
            y=zone_complaints['complaint_resolution_efficiency'],
            text=zone_complaints['complaint_resolution_efficiency'],
            texttemplate='%{text:.1f}%',
            marker_color='teal',
            name='Resolution Efficiency'
        ))
        
        fig4.update_layout(
            title='Complaint Resolution Efficiency by Zone',
            xaxis_title='Zone',
            yaxis_title='Efficiency (%)',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.subheader("Wastewater Treatment Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Capacity utilization over time
        ww_time = filtered_df.groupby('date_parsed').agg({
            'ww_capacity': 'mean',
            'ww_treated': 'mean',
            'ww_collected': 'mean'
        }).reset_index()
        
        fig5 = go.Figure()
        
        fig5.add_trace(go.Scatter(
            x=ww_time['date_parsed'],
            y=ww_time['ww_capacity'],
            name='Capacity',
            line=dict(color='lightblue', width=2, dash='dash'),
            fill='tonexty'
        ))
        
        fig5.add_trace(go.Scatter(
            x=ww_time['date_parsed'],
            y=ww_time['ww_treated'],
            name='Treated',
            line=dict(color='darkblue', width=2),
            fill='tozeroy'
        ))
        
        fig5.update_layout(
            title='Wastewater Treatment Capacity vs Actual',
            xaxis_title='Date',
            yaxis_title='Volume (m³)',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig5, use_container_width=True)
    
    with col2:
        # Faecal Sludge Reuse
        fs_data = filtered_df.groupby('zone').agg({
            'fs_treated': 'sum',
            'fs_reused': 'sum'
        }).reset_index()
        
        fs_data['fs_wasted'] = fs_data['fs_treated'] - fs_data['fs_reused']
        
        fig6 = go.Figure()
        fig6.add_trace(go.Bar(
            name='Reused',
            x=fs_data['zone'],
            y=fs_data['fs_reused'],
            marker_color='green'
        ))
        
        fig6.add_trace(go.Bar(
            name='Wasted',
            x=fs_data['zone'],
            y=fs_data['fs_wasted'],
            marker_color='red'
        ))
        
        fig6.update_layout(
            title='Faecal Sludge Treatment vs Reuse',
            xaxis_title='Zone',
            yaxis_title='Volume (m³)',
            barmode='stack',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig6, use_container_width=True)

with tab4:
    st.subheader("Operational Efficiency")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Workforce productivity
        fig7 = px.box(filtered_df, x='zone', y='connections_per_employee',
                     title='Workforce Productivity Distribution by Zone',
                     labels={'connections_per_employee': 'Connections per Employee',
                            'zone': 'Zone'},
                     color='zone')
        
        fig7.update_layout(height=400, template='plotly_white', showlegend=False)
        st.plotly_chart(fig7, use_container_width=True)
    
    with col2:
        # NRW and Metering
        ops_data = filtered_df.groupby('date_parsed').agg({
            'nrw_percentage': 'mean',
            'metering_coverage': 'mean'
        }).reset_index()
        
        fig8 = go.Figure()
        
        fig8.add_trace(go.Scatter(
            x=ops_data['date_parsed'],
            y=ops_data['nrw_percentage'],
            name='Non-Revenue Water %',
            line=dict(color='red', width=2),
            mode='lines+markers'
        ))
        
        fig8.add_trace(go.Scatter(
            x=ops_data['date_parsed'],
            y=ops_data['metering_coverage'],
            name='Metering Coverage %',
            line=dict(color='green', width=2),
            mode='lines+markers',
            yaxis='y2'
        ))
        
        fig8.update_layout(
            title='NRW & Metering Coverage Trends',
            xaxis_title='Date',
            yaxis_title='NRW %',
            yaxis2=dict(title='Metering Coverage %', overlaying='y', side='right'),
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig8, use_container_width=True)

# Data Table
st.markdown("---")
st.subheader("📋 Detailed Data")
st.dataframe(filtered_df[['date', 'zone', 'city', 'ecoli_pass_rate', 'chlorine_pass_rate', 
                          'complaints_per_1000_hh', 'complaint_resolution_efficiency',
                          'ww_capacity_utilization', 'metering_coverage']].head(20), 
             use_container_width=True)

