import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(page_title="Uganda Analysis", page_icon="🇺🇬", layout="wide")

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
    df['metering_coverage'] = (df['metered'] / df['households'] * 100).round(2)
    df['nrw_percentage'] = ((df['w_supplied'] - df['total_consumption']) / df['w_supplied'] * 100).round(2)
    
    return df

df = load_data()
uganda_df = df[df['country'] == 'Uganda'].copy()

# Header
st.title("🇺🇬 Uganda - Water & Sanitation Analytics")
st.markdown("### Kampala Service Performance Dashboard")

# Sidebar Filters
st.sidebar.header("🔍 Filters")

# Date range filter
min_date = uganda_df['date_parsed'].min()
max_date = uganda_df['date_parsed'].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Zone filter (Kampala zones: Rubaga, Central, Nakawa, Kawempe)
zones = ['All'] + sorted(uganda_df['zone'].unique().tolist())
selected_zones = st.sidebar.multiselect(
    "Select Zones",
    options=zones,
    default=['All']
)

# Year filter
years = ['All'] + sorted(uganda_df['year'].unique().tolist())
selected_years = st.sidebar.multiselect(
    "Select Years",
    options=years,
    default=['All']
)

# Focus period for complaint analysis
focus_period = st.sidebar.selectbox(
    "Complaint Analysis Period",
    ["All Years", "2022-2024", "2020-2021"]
)

# Apply filters
filtered_df = uganda_df.copy()

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
    avg_complaints = filtered_df['complaints_per_1000_hh'].mean()
    st.metric("Complaints/1000 HH", f"{avg_complaints:.1f}")

with col3:
    avg_resolution_time = filtered_df['complaint_resolution'].mean()
    st.metric("Avg Resolution Time", f"{avg_resolution_time:.0f} days",
              delta="Above Target" if avg_resolution_time > 15 else "✓",
              delta_color="inverse")

with col4:
    avg_resolution_eff = filtered_df['complaint_resolution_efficiency'].mean()
    st.metric("Resolution Efficiency", f"{avg_resolution_eff:.1f}%")

with col5:
    avg_metering = filtered_df['metering_coverage'].mean()
    st.metric("Metering Coverage", f"{avg_metering:.1f}%")

st.markdown("---")

# Featured Insight: Complaint Resolution Crisis
st.subheader("⚠️ Featured Insight: Complaint Resolution Crisis in Kampala")

# Filter for 2022-2024 period for the featured insight
kampala_recent = uganda_df[uganda_df['year'] >= 2022].copy()

# Create figure with secondary y-axis
fig_featured = make_subplots(specs=[[{"secondary_y": True}]])

zone_colors = {'Rubaga': 'blue', 'Central': 'green', 'Nakawa': 'orange', 'Kawempe': 'red'}

for zone in kampala_recent['zone'].unique():
    zone_data = kampala_recent[kampala_recent['zone'] == zone].sort_values('date_parsed')
    
    # Resolution time as lines
    fig_featured.add_trace(
        go.Scatter(
            x=zone_data['date_parsed'],
            y=zone_data['complaint_resolution'],
            name=f'{zone} - Resolution Time',
            line=dict(color=zone_colors.get(zone, 'gray'), width=2),
            mode='lines+markers'
        ),
        secondary_y=False
    )

# Add stacked area for total complaints
for zone in kampala_recent['zone'].unique():
    zone_data = kampala_recent[kampala_recent['zone'] == zone].sort_values('date_parsed')
    
    fig_featured.add_trace(
        go.Scatter(
            x=zone_data['date_parsed'],
            y=zone_data['complaints'],
            name=f'{zone} - Complaints',
            line=dict(width=0),
            stackgroup='one',
            fillcolor=zone_colors.get(zone, 'gray'),
            opacity=0.3
        ),
        secondary_y=True
    )

fig_featured.add_hline(y=15, line_dash="dash", line_color="darkgreen",
              annotation_text="Target: 15 days", secondary_y=False)

fig_featured.update_xaxes(title_text="Date")
fig_featured.update_yaxes(title_text="Average Resolution Time (days)", secondary_y=False)
fig_featured.update_yaxes(title_text="Total Complaints", secondary_y=True)

fig_featured.update_layout(
    title='Complaint Resolution Performance - Kampala Zones (2022-2024)',
    height=550,
    template='plotly_white',
    hovermode='x unified'
)

st.plotly_chart(fig_featured, use_container_width=True)

# Summary table
summary = kampala_recent.groupby('zone').agg({
    'complaints': 'mean',
    'resolved': 'mean',
    'complaint_resolution': 'mean',
    'complaint_resolution_efficiency': 'mean',
    'households': 'mean',
    'complaints_per_1000_hh': 'mean'
}).round(2)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Zone Performance (2022-2024)")
    st.dataframe(summary, use_container_width=True)

with col2:
    st.subheader("Key Findings")
    st.warning("""
    **Critical Issues Identified:**
    - **Nakawa zone** has highest complaint rate (28.10 per 1,000 households)
    - Average resolution time exceeds **22 days** across all zones
    - Target of 15 days is consistently missed
    - Resolution efficiency averages ~79%, indicating service gaps
    - High-density zones face disproportionate service challenges
    """)

st.markdown("---")

# Visualization Tabs
tab1, tab2, tab3, tab4 = st.tabs(["💧 Water Quality", "🎧 Customer Service Deep Dive", "📊 Zone Comparison", "📈 Trends"])

with tab1:
    st.subheader("Water Quality Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Water quality trends
        wq_trends = filtered_df.groupby('date_parsed').agg({
            'chlorine_pass_rate': 'mean',
            'ecoli_pass_rate': 'mean'
        }).reset_index()
        
        fig1 = go.Figure()
        
        fig1.add_trace(go.Scatter(
            x=wq_trends['date_parsed'],
            y=wq_trends['chlorine_pass_rate'],
            name='Chlorine',
            line=dict(color='blue', width=2),
            mode='lines+markers',
            fill='tonexty'
        ))
        
        fig1.add_trace(go.Scatter(
            x=wq_trends['date_parsed'],
            y=wq_trends['ecoli_pass_rate'],
            name='E. Coli',
            line=dict(color='red', width=2),
            mode='lines+markers'
        ))
        
        fig1.add_hline(y=95, line_dash="dash", line_color="green",
                      annotation_text="WHO: 95%")
        
        fig1.update_layout(
            title='Water Quality Pass Rates',
            xaxis_title='Date',
            yaxis_title='Pass Rate (%)',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Zone water quality comparison
        zone_wq = filtered_df.groupby('zone').agg({
            'chlorine_pass_rate': 'mean',
            'ecoli_pass_rate': 'mean'
        }).round(2).reset_index()
        
        fig2 = go.Figure(data=[
            go.Bar(name='Chlorine', x=zone_wq['zone'], y=zone_wq['chlorine_pass_rate'],
                  text=zone_wq['chlorine_pass_rate'], texttemplate='%{text:.1f}%',
                  marker_color='steelblue'),
            go.Bar(name='E. Coli', x=zone_wq['zone'], y=zone_wq['ecoli_pass_rate'],
                  text=zone_wq['ecoli_pass_rate'], texttemplate='%{text:.1f}%',
                  marker_color='lightcoral')
        ])
        
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
    st.subheader("Customer Service Deep Dive")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly complaint patterns
        monthly_complaints = filtered_df.groupby(['zone', 'date_parsed']).agg({
            'complaints': 'sum'
        }).reset_index()
        
        fig3 = px.line(monthly_complaints, x='date_parsed', y='complaints',
                      color='zone', title='Monthly Complaint Trends by Zone',
                      labels={'complaints': 'Total Complaints', 'date_parsed': 'Date'})
        
        fig3.update_layout(height=400, template='plotly_white')
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Resolution efficiency heatmap
        zone_month = filtered_df.copy()
        zone_month['month'] = zone_month['date_parsed'].dt.to_period('M').astype(str)
        
        heatmap_data = zone_month.groupby(['zone', 'month']).agg({
            'complaint_resolution_efficiency': 'mean'
        }).reset_index()
        
        pivot_data = heatmap_data.pivot(index='zone', columns='month', 
                                        values='complaint_resolution_efficiency')
        
        fig4 = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns[-12:],  # Last 12 months
            y=pivot_data.index,
            colorscale='RdYlGn',
            text=pivot_data.values,
            texttemplate='%{text:.0f}%',
            colorbar=dict(title="Efficiency %")
        ))
        
        fig4.update_layout(
            title='Resolution Efficiency Heatmap (Last 12 Months)',
            xaxis_title='Month',
            yaxis_title='Zone',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.subheader("Zone-by-Zone Comparison")
    
    # Comprehensive zone metrics
    zone_metrics = filtered_df.groupby('zone').agg({
        'households': 'mean',
        'complaints_per_1000_hh': 'mean',
        'complaint_resolution': 'mean',
        'complaint_resolution_efficiency': 'mean',
        'ecoli_pass_rate': 'mean',
        'metering_coverage': 'mean',
        'connections_per_employee': 'mean'
    }).round(2).reset_index()
    
    # Multi-metric comparison
    fig5 = go.Figure()
    
    metrics = ['ecoli_pass_rate', 'complaint_resolution_efficiency', 'metering_coverage']
    metric_names = ['E. Coli Pass Rate', 'Resolution Efficiency', 'Metering Coverage']
    
    for zone in zone_metrics['zone']:
        zone_data = zone_metrics[zone_metrics['zone'] == zone]
        fig5.add_trace(go.Scatterpolar(
            r=[zone_data[m].values[0] for m in metrics],
            theta=metric_names,
            fill='toself',
            name=zone
        ))
    
    fig5.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title='Zone Performance Radar Chart',
        height=500,
        template='plotly_white'
    )
    
    st.plotly_chart(fig5, use_container_width=True)
    
    # Detailed zone table
    st.dataframe(zone_metrics, use_container_width=True)

with tab4:
    st.subheader("Historical Trends & Patterns")
    
    # Yearly trends
    yearly_trends = filtered_df.groupby('year').agg({
        'ecoli_pass_rate': 'mean',
        'complaints_per_1000_hh': 'mean',
        'complaint_resolution': 'mean',
        'metering_coverage': 'mean'
    }).round(2).reset_index()
    
    fig6 = make_subplots(
        rows=2, cols=2,
        subplot_titles=('E. Coli Pass Rate', 'Complaints per 1000 HH',
                       'Avg Resolution Time (days)', 'Metering Coverage (%)')
    )
    
    fig6.add_trace(go.Scatter(x=yearly_trends['year'], y=yearly_trends['ecoli_pass_rate'],
                             mode='lines+markers', name='E. Coli', line=dict(color='red', width=3)),
                  row=1, col=1)
    
    fig6.add_trace(go.Scatter(x=yearly_trends['year'], y=yearly_trends['complaints_per_1000_hh'],
                             mode='lines+markers', name='Complaints', line=dict(color='orange', width=3)),
                  row=1, col=2)
    
    fig6.add_trace(go.Scatter(x=yearly_trends['year'], y=yearly_trends['complaint_resolution'],
                             mode='lines+markers', name='Resolution', line=dict(color='purple', width=3)),
                  row=2, col=1)
    
    fig6.add_trace(go.Scatter(x=yearly_trends['year'], y=yearly_trends['metering_coverage'],
                             mode='lines+markers', name='Metering', line=dict(color='green', width=3)),
                  row=2, col=2)
    
    fig6.update_layout(height=600, showlegend=False, template='plotly_white')
    st.plotly_chart(fig6, use_container_width=True)

# Performance Summary
st.markdown("---")
st.subheader("📊 Overall Performance Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Households Served", f"{filtered_df['households'].sum():,.0f}")
    st.metric("Average Workforce", f"{filtered_df['workforce'].mean():.0f}")

with col2:
    st.metric("Total Complaints", f"{filtered_df['complaints'].sum():,.0f}")
    st.metric("Total Resolved", f"{filtered_df['resolved'].sum():,.0f}")

with col3:
    st.metric("Avg Water Quality", f"{filtered_df['ecoli_pass_rate'].mean():.1f}%")
    st.metric("Avg NRW", f"{filtered_df['nrw_percentage'].mean():.1f}%")

# Data Table
st.markdown("---")
st.subheader("📋 Detailed Data")
st.dataframe(filtered_df[['date', 'zone', 'complaints', 'resolved', 'complaint_resolution',
                          'ecoli_pass_rate', 'metering_coverage']].head(20),
             use_container_width=True)

