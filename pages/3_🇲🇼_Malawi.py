import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(page_title="Malawi Analysis", page_icon="🇲🇼", layout="wide")

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
    df['population_estimate'] = df['households'] * 5
    df['people_per_toilet'] = (df['population_estimate'] / df['public_toilets']).round(0)
    df['metering_coverage'] = (df['metered'] / df['households'] * 100).round(2)
    df['nrw_percentage'] = ((df['w_supplied'] - df['total_consumption']) / df['w_supplied'] * 100).round(2)
    
    return df

df = load_data()
malawi_df = df[df['country'] == 'malawi'].copy()

# Header
st.title("🇲🇼 Malawi - Water & Sanitation Analytics")
st.markdown("### Lilongwe Service Performance Dashboard")

# Sidebar Filters
st.sidebar.header("🔍 Filters")

# Date range filter
min_date = malawi_df['date_parsed'].min()
max_date = malawi_df['date_parsed'].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Zone filter
zones = ['All'] + sorted(malawi_df['zone'].unique().tolist())
selected_zones = st.sidebar.multiselect(
    "Select Zones",
    options=zones,
    default=['All']
)

# Year filter
years = ['All'] + sorted(malawi_df['year'].unique().tolist())
selected_years = st.sidebar.multiselect(
    "Select Years",
    options=years,
    default=['All']
)

# Metric selector
metric_view = st.sidebar.selectbox(
    "Focus Area",
    ["Overview", "Water Quality", "Customer Service", "Infrastructure"]
)

# Apply filters
filtered_df = malawi_df.copy()

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
    avg_resolution = filtered_df['complaint_resolution_efficiency'].mean()
    st.metric("Resolution Efficiency", f"{avg_resolution:.1f}%")

with col4:
    avg_people_toilet = filtered_df['people_per_toilet'].mean()
    st.metric("People/Toilet", f"{avg_people_toilet:.0f}",
              delta="Above WHO" if avg_people_toilet > 500 else "✓",
              delta_color="inverse")

with col5:
    avg_metering = filtered_df['metering_coverage'].mean()
    st.metric("Metering Coverage", f"{avg_metering:.1f}%")

st.markdown("---")

# Featured Insight: Public Toilet Infrastructure
st.subheader("🚻 Featured Insight: Public Toilet Infrastructure")

toilet_trends = filtered_df.groupby('date_parsed').agg({
    'people_per_toilet': 'mean',
    'public_toilets': 'mean',
    'population_estimate': 'mean'
}).reset_index()

fig_featured = go.Figure()

fig_featured.add_trace(go.Scatter(
    x=toilet_trends['date_parsed'],
    y=toilet_trends['people_per_toilet'],
    mode='lines+markers',
    name='People per Toilet',
    line=dict(color='coral', width=3),
    fill='tozeroy'
))

fig_featured.add_hline(y=500, line_dash="dash", line_color="green",
               annotation_text="WHO Guideline: 500 people/toilet", 
               annotation_position="right")

fig_featured.update_layout(
    title='Public Toilet Access Over Time - Lilongwe (2020-2024)',
    xaxis_title='Date',
    yaxis_title='People per Toilet',
    height=450,
    template='plotly_white'
)

st.plotly_chart(fig_featured, use_container_width=True)

avg_people_per_toilet = filtered_df['people_per_toilet'].mean()
if avg_people_per_toilet > 500:
    st.error(f"""
    **Critical Issue:** Lilongwe averages **{avg_people_per_toilet:.0f} people per public toilet**, 
    significantly exceeding WHO guidelines of 500 people per toilet. This indicates severe 
    infrastructure gaps in public sanitation facilities.
    """)
else:
    st.success(f"""
    Lilongwe averages {avg_people_per_toilet:.0f} people per public toilet, 
    meeting WHO guidelines.
    """)

st.markdown("---")

# Visualization Tabs
tab1, tab2, tab3, tab4 = st.tabs(["💧 Water Quality", "🎧 Customer Service", "🚻 Sanitation", "📈 Operations"])

with tab1:
    st.subheader("Water Quality Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Water quality trends
        wq_trends = filtered_df.groupby('date_parsed').agg({
            'chlorine_pass_rate': 'mean',
            'ecoli_pass_rate': 'mean',
            'chlorine_execution_rate': 'mean',
            'ecoli_execution_rate': 'mean'
        }).reset_index()
        
        fig1 = go.Figure()
        
        fig1.add_trace(go.Scatter(
            x=wq_trends['date_parsed'],
            y=wq_trends['chlorine_pass_rate'],
            name='Chlorine Pass Rate',
            line=dict(color='blue', width=2),
            mode='lines+markers'
        ))
        
        fig1.add_trace(go.Scatter(
            x=wq_trends['date_parsed'],
            y=wq_trends['ecoli_pass_rate'],
            name='E. Coli Pass Rate',
            line=dict(color='red', width=2),
            mode='lines+markers'
        ))
        
        fig1.add_hline(y=95, line_dash="dash", line_color="green",
                      annotation_text="WHO: 95%")
        
        fig1.update_layout(
            title='Water Quality Pass Rates Over Time',
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
    st.subheader("Customer Service Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Complaint trends
        complaint_trends = filtered_df.groupby('date_parsed').agg({
            'complaints': 'sum',
            'resolved': 'sum',
            'complaint_resolution': 'mean'
        }).reset_index()
        
        fig3 = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig3.add_trace(
            go.Bar(name='Complaints', x=complaint_trends['date_parsed'],
                  y=complaint_trends['complaints'], marker_color='orange'),
            secondary_y=False
        )
        
        fig3.add_trace(
            go.Scatter(name='Avg Resolution Time', x=complaint_trends['date_parsed'],
                      y=complaint_trends['complaint_resolution'],
                      mode='lines+markers', line=dict(color='red', width=3)),
            secondary_y=True
        )
        
        fig3.update_xaxes(title_text="Date")
        fig3.update_yaxes(title_text="Total Complaints", secondary_y=False)
        fig3.update_yaxes(title_text="Resolution Days", secondary_y=True)
        
        fig3.update_layout(
            title='Complaints & Resolution Time',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Zone performance
        zone_cs = filtered_df.groupby('zone').agg({
            'complaint_resolution_efficiency': 'mean',
            'complaints_per_1000_hh': 'mean'
        }).round(2).reset_index()
        
        fig4 = go.Figure()
        
        fig4.add_trace(go.Bar(
            x=zone_cs['zone'],
            y=zone_cs['complaint_resolution_efficiency'],
            text=zone_cs['complaint_resolution_efficiency'],
            texttemplate='%{text:.1f}%',
            marker_color='teal'
        ))
        
        fig4.update_layout(
            title='Resolution Efficiency by Zone',
            xaxis_title='Zone',
            yaxis_title='Efficiency (%)',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.subheader("Sanitation Infrastructure")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Public toilets by zone
        zone_toilets = filtered_df.groupby('zone').agg({
            'public_toilets': 'mean',
            'people_per_toilet': 'mean',
            'population_estimate': 'mean'
        }).round(0).reset_index()
        
        fig5 = go.Figure()
        
        fig5.add_trace(go.Bar(
            x=zone_toilets['zone'],
            y=zone_toilets['people_per_toilet'],
            text=zone_toilets['people_per_toilet'],
            texttemplate='%{text:.0f}',
            marker_color=['red' if x > 500 else 'green' 
                         for x in zone_toilets['people_per_toilet']]
        ))
        
        fig5.add_hline(y=500, line_dash="dash", line_color="orange",
                      annotation_text="WHO: 500")
        
        fig5.update_layout(
            title='People per Public Toilet by Zone',
            xaxis_title='Zone',
            yaxis_title='People per Toilet',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig5, use_container_width=True)
    
    with col2:
        # Toilet availability trends
        yearly_toilets = filtered_df.groupby('year').agg({
            'public_toilets': 'mean',
            'people_per_toilet': 'mean'
        }).reset_index()
        
        fig6 = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig6.add_trace(
            go.Bar(name='Public Toilets', x=yearly_toilets['year'],
                  y=yearly_toilets['public_toilets'], marker_color='lightblue'),
            secondary_y=False
        )
        
        fig6.add_trace(
            go.Scatter(name='People per Toilet', x=yearly_toilets['year'],
                      y=yearly_toilets['people_per_toilet'],
                      mode='lines+markers', line=dict(color='red', width=3)),
            secondary_y=True
        )
        
        fig6.update_layout(
            title='Public Toilet Infrastructure Trends',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig6, use_container_width=True)

with tab4:
    st.subheader("Operational Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Workforce productivity
        fig7 = px.box(filtered_df, x='zone', y='connections_per_employee',
                     title='Workforce Productivity by Zone',
                     color='zone',
                     labels={'connections_per_employee': 'Connections per Employee'})
        
        fig7.update_layout(height=400, showlegend=False, template='plotly_white')
        st.plotly_chart(fig7, use_container_width=True)
    
    with col2:
        # NRW and Metering
        ops_trends = filtered_df.groupby('date_parsed').agg({
            'nrw_percentage': 'mean',
            'metering_coverage': 'mean'
        }).reset_index()
        
        fig8 = go.Figure()
        
        fig8.add_trace(go.Scatter(
            x=ops_trends['date_parsed'],
            y=ops_trends['nrw_percentage'],
            name='NRW %',
            line=dict(color='red', width=2),
            mode='lines+markers'
        ))
        
        fig8.add_trace(go.Scatter(
            x=ops_trends['date_parsed'],
            y=ops_trends['metering_coverage'],
            name='Metering Coverage %',
            line=dict(color='green', width=2),
            mode='lines+markers'
        ))
        
        fig8.update_layout(
            title='NRW & Metering Coverage Trends',
            xaxis_title='Date',
            yaxis_title='Percentage (%)',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig8, use_container_width=True)

# Summary Statistics
st.markdown("---")
st.subheader("📊 Summary Statistics by Zone")

summary_stats = filtered_df.groupby('zone').agg({
    'ecoli_pass_rate': 'mean',
    'chlorine_pass_rate': 'mean',
    'complaints_per_1000_hh': 'mean',
    'complaint_resolution_efficiency': 'mean',
    'people_per_toilet': 'mean',
    'metering_coverage': 'mean'
}).round(2)

st.dataframe(summary_stats, use_container_width=True)

# Data Table
st.markdown("---")
st.subheader("📋 Detailed Data")
st.dataframe(filtered_df[['date', 'zone', 'ecoli_pass_rate', 'complaints_per_1000_hh',
                          'people_per_toilet', 'metering_coverage']].head(20),
             use_container_width=True)

