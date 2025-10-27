import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(page_title="Lesotho Analysis", page_icon="🇱🇸", layout="wide")

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
    df['sewer_connection_density'] = (df['sewer_connections'] / df['households']).round(3)
    df['metering_coverage'] = (df['metered'] / df['households'] * 100).round(2)
    df['nrw_percentage'] = ((df['w_supplied'] - df['total_consumption']) / df['w_supplied'] * 100).round(2)
    
    return df

df = load_data()
lesotho_df = df[df['country'] == 'lesotho'].copy()

# Header
st.title("🇱🇸 Lesotho - Water & Sanitation Analytics")
st.markdown("### Urban vs Rural Service Performance Comparison")

# Sidebar Filters
st.sidebar.header("🔍 Filters")

# Date range filter
min_date = lesotho_df['date_parsed'].min()
max_date = lesotho_df['date_parsed'].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Zone filter (Urban/Rural focus)
zones = ['All'] + sorted(lesotho_df['zone'].unique().tolist())
selected_zones = st.sidebar.multiselect(
    "Select Zones",
    options=zones,
    default=['All']
)

# Year filter
years = ['All'] + sorted(lesotho_df['year'].unique().tolist())
selected_years = st.sidebar.multiselect(
    "Select Years",
    options=years,
    default=['All']
)

# Apply filters
filtered_df = lesotho_df.copy()

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df['date_parsed'].dt.date >= start_date) & 
        (filtered_df['date_parsed'].dt.date <= end_date)
    ]

if 'All' not in selected_zones and selected_zones:
    filtered_df = filtered_df[filtered_df['zone'].isin(selected_zones)]

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
    st.metric("E. Coli Pass Rate", f"{avg_ecoli:.1f}%")

with col2:
    avg_chlorine_exec = filtered_df['chlorine_execution_rate'].mean()
    st.metric("Chlorine Test Execution", f"{avg_chlorine_exec:.1f}%",
              delta="Below Target" if avg_chlorine_exec < 90 else "✓")

with col3:
    avg_complaints = filtered_df['complaints_per_1000_hh'].mean()
    st.metric("Complaints/1000 HH", f"{avg_complaints:.1f}")

with col4:
    avg_sewer = filtered_df['sewer_connection_density'].mean()
    st.metric("Sewer Connection Density", f"{avg_sewer:.3f}")

with col5:
    avg_metering = filtered_df['metering_coverage'].mean()
    st.metric("Metering Coverage", f"{avg_metering:.1f}%")

st.markdown("---")

# Featured Insight: Water Quality Testing Gaps
st.subheader("🎯 Featured Insight: Water Quality Testing Gaps")

zone_wq = filtered_df.groupby('zone').agg({
    'chlorine_execution_rate': 'mean',
    'chlorine_pass_rate': 'mean',
    'ecoli_execution_rate': 'mean',
    'ecoli_pass_rate': 'mean',
    'tests_chlorine': 'sum',
    'tests_conducted_chlorine': 'sum'
}).round(2).reset_index()

fig_featured = go.Figure()

fig_featured.add_trace(go.Bar(
    name='Chlorine Test Execution Rate (%)',
    x=zone_wq['zone'],
    y=zone_wq['chlorine_execution_rate'],
    marker_color='steelblue',
    text=zone_wq['chlorine_execution_rate'].round(1),
    textposition='outside',
    texttemplate='%{text}%'
))

fig_featured.add_trace(go.Bar(
    name='Chlorine Test Pass Rate (%)',
    x=zone_wq['zone'],
    y=zone_wq['chlorine_pass_rate'],
    marker_color='lightcoral',
    text=zone_wq['chlorine_pass_rate'].round(1),
    textposition='outside',
    texttemplate='%{text}%'
))

fig_featured.add_hline(y=90, line_dash="dash", line_color="green",
              annotation_text="Target: 90%", annotation_position="right")
fig_featured.add_hline(y=80, line_dash="dash", line_color="orange",
              annotation_text="Warning: 80%", annotation_position="right")

fig_featured.update_layout(
    title='Water Quality Testing Performance by Zone - Execution vs Pass Rates',
    xaxis_title='Zone',
    yaxis_title='Percentage (%)',
    barmode='group',
    height=500,
    template='plotly_white'
)

st.plotly_chart(fig_featured, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.dataframe(zone_wq, use_container_width=True)
with col2:
    st.info("""
    **Key Findings:**
    - All zones operate below 90% execution target
    - Rural Hinterland shows highest pass rate but lowest execution
    - ~15% of planned water quality tests are not conducted
    - Despite execution gaps, pass rates remain above 90%
    """)

st.markdown("---")

# Visualization Tabs
tab1, tab2, tab3, tab4 = st.tabs(["💧 Water Quality", "🏘️ Urban vs Rural", "📈 Trends", "🔧 Infrastructure"])

with tab1:
    st.subheader("Water Quality Monitoring")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly water quality trends
        monthly_wq = filtered_df.groupby('date_parsed').agg({
            'chlorine_pass_rate': 'mean',
            'ecoli_pass_rate': 'mean'
        }).reset_index()
        
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=monthly_wq['date_parsed'],
            y=monthly_wq['chlorine_pass_rate'],
            name='Chlorine',
            line=dict(color='blue', width=2),
            mode='lines+markers'
        ))
        
        fig1.add_trace(go.Scatter(
            x=monthly_wq['date_parsed'],
            y=monthly_wq['ecoli_pass_rate'],
            name='E. Coli',
            line=dict(color='red', width=2),
            mode='lines+markers'
        ))
        
        fig1.add_hline(y=95, line_dash="dash", line_color="green")
        
        fig1.update_layout(
            title='Water Quality Pass Rates Over Time',
            xaxis_title='Date',
            yaxis_title='Pass Rate (%)',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Execution vs Pass Rate comparison
        fig2 = go.Figure()
        
        for zone in zone_wq['zone']:
            zone_data = zone_wq[zone_wq['zone'] == zone]
            fig2.add_trace(go.Scatter(
                x=[zone_data['chlorine_execution_rate'].values[0]],
                y=[zone_data['chlorine_pass_rate'].values[0]],
                mode='markers+text',
                name=zone,
                text=[zone],
                textposition='top center',
                marker=dict(size=15)
            ))
        
        fig2.update_layout(
            title='Execution Rate vs Pass Rate by Zone',
            xaxis_title='Execution Rate (%)',
            yaxis_title='Pass Rate (%)',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Urban vs Rural Comparison")
    
    # Categorize zones
    filtered_df['area_type'] = filtered_df['zone'].apply(
        lambda x: 'Urban' if 'Urban' in x else 'Rural'
    )
    
    urban_rural = filtered_df.groupby('area_type').agg({
        'ecoli_pass_rate': 'mean',
        'chlorine_pass_rate': 'mean',
        'complaints_per_1000_hh': 'mean',
        'metering_coverage': 'mean',
        'sewer_connection_density': 'mean',
        'households': 'sum'
    }).round(2).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Service quality comparison
        metrics = ['ecoli_pass_rate', 'chlorine_pass_rate', 'metering_coverage']
        
        fig3 = go.Figure()
        
        for area in urban_rural['area_type']:
            area_data = urban_rural[urban_rural['area_type'] == area]
            fig3.add_trace(go.Bar(
                name=area,
                x=metrics,
                y=[area_data[m].values[0] for m in metrics],
                text=[f"{area_data[m].values[0]:.1f}%" for m in metrics],
                textposition='outside'
            ))
        
        fig3.update_layout(
            title='Service Quality: Urban vs Rural',
            xaxis_title='Metric',
            yaxis_title='Percentage (%)',
            barmode='group',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Infrastructure comparison
        fig4 = go.Figure(data=[
            go.Bar(name='Urban', x=['Households', 'Sewer Density', 'Complaints/1000HH'],
                   y=[urban_rural[urban_rural['area_type']=='Urban']['households'].values[0],
                      urban_rural[urban_rural['area_type']=='Urban']['sewer_connection_density'].values[0]*1000,
                      urban_rural[urban_rural['area_type']=='Urban']['complaints_per_1000_hh'].values[0]],
                   marker_color='lightblue'),
            go.Bar(name='Rural', x=['Households', 'Sewer Density', 'Complaints/1000HH'],
                   y=[urban_rural[urban_rural['area_type']=='Rural']['households'].values[0],
                      urban_rural[urban_rural['area_type']=='Rural']['sewer_connection_density'].values[0]*1000,
                      urban_rural[urban_rural['area_type']=='Rural']['complaints_per_1000_hh'].values[0]],
                   marker_color='coral')
        ])
        
        fig4.update_layout(
            title='Infrastructure & Service Metrics',
            barmode='group',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.subheader("Historical Trends")
    
    yearly_trends = filtered_df.groupby('year').agg({
        'ecoli_pass_rate': 'mean',
        'chlorine_execution_rate': 'mean',
        'complaints_per_1000_hh': 'mean',
        'metering_coverage': 'mean'
    }).round(2).reset_index()
    
    fig5 = make_subplots(
        rows=2, cols=2,
        subplot_titles=('E. Coli Pass Rate', 'Chlorine Execution Rate',
                       'Complaints per 1000 HH', 'Metering Coverage')
    )
    
    fig5.add_trace(go.Scatter(x=yearly_trends['year'], y=yearly_trends['ecoli_pass_rate'],
                             mode='lines+markers', name='E. Coli', line=dict(color='red')),
                  row=1, col=1)
    
    fig5.add_trace(go.Scatter(x=yearly_trends['year'], y=yearly_trends['chlorine_execution_rate'],
                             mode='lines+markers', name='Chlorine Exec', line=dict(color='blue')),
                  row=1, col=2)
    
    fig5.add_trace(go.Scatter(x=yearly_trends['year'], y=yearly_trends['complaints_per_1000_hh'],
                             mode='lines+markers', name='Complaints', line=dict(color='orange')),
                  row=2, col=1)
    
    fig5.add_trace(go.Scatter(x=yearly_trends['year'], y=yearly_trends['metering_coverage'],
                             mode='lines+markers', name='Metering', line=dict(color='green')),
                  row=2, col=2)
    
    fig5.update_layout(height=600, showlegend=False, template='plotly_white')
    st.plotly_chart(fig5, use_container_width=True)

with tab4:
    st.subheader("Infrastructure & Workforce")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Workforce productivity by zone
        fig6 = px.box(filtered_df, x='zone', y='connections_per_employee',
                     title='Connections per Employee Distribution',
                     color='zone')
        fig6.update_layout(height=400, showlegend=False, template='plotly_white')
        st.plotly_chart(fig6, use_container_width=True)
    
    with col2:
        # NRW trends
        nrw_time = filtered_df.groupby('date_parsed')['nrw_percentage'].mean().reset_index()
        
        fig7 = go.Figure()
        fig7.add_trace(go.Scatter(
            x=nrw_time['date_parsed'],
            y=nrw_time['nrw_percentage'],
            fill='tozeroy',
            line=dict(color='red', width=2),
            mode='lines+markers'
        ))
        
        fig7.update_layout(
            title='Non-Revenue Water Trends',
            xaxis_title='Date',
            yaxis_title='NRW %',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig7, use_container_width=True)

# Data Table
st.markdown("---")
st.subheader("📋 Detailed Data")
st.dataframe(filtered_df[['date', 'zone', 'ecoli_pass_rate', 'chlorine_execution_rate',
                          'complaints_per_1000_hh', 'metering_coverage']].head(20),
             use_container_width=True)

