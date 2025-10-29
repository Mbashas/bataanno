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
    page_title="African Water & Sanitation Regulatory Dashboard",
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
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .metric-red {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    }
    .metric-amber {
        background: linear-gradient(135deg, #f09819 0%, #edde5d 100%);
    }
    .metric-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .headline {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .subheadline {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1f2937;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #6b7280;
        margin-top: 0.25rem;
    }
    .alert-critical {
        background-color: #fee2e2;
        border-left: 4px solid #dc2626;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .alert-warning {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .alert-success {
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
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

# Helper function to determine KPI status color
def get_kpi_status(value, benchmark, higher_is_better=True):
    """Returns color based on performance vs benchmark"""
    if higher_is_better:
        if value >= benchmark:
            return "🟢", "success"
        elif value >= benchmark * 0.8:
            return "🟡", "warning"
        else:
            return "🔴", "critical"
    else:
        if value <= benchmark:
            return "🟢", "success"
        elif value <= benchmark * 1.2:
            return "🟡", "warning"
        else:
            return "🔴", "critical"

# Main page
def main():
    # Header Section
    st.markdown('<h1 style="color: #1f2937; margin-bottom: 0;">💧 African Water & Sanitation Regulatory Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheadline">Real-time performance data from Cameroon, Lesotho, Malawi, and Uganda — covering Service, Production, Access, and Finance.</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6b7280; font-size: 1rem; margin-bottom: 2rem;">Track progress toward universal access — see which utilities are improving and which need support.</p>', unsafe_allow_html=True)
    
    df = load_data()
    
    # ===== SIDEBAR: QUICK FILTERS =====
    st.sidebar.title("🎛️ Quick Filters")
    st.sidebar.markdown("---")
    
    # Country filter
    all_countries = sorted(df['country'].unique())
    selected_countries = st.sidebar.multiselect(
        "Select Countries",
        options=all_countries,
        default=all_countries,
        help="Choose one or more countries to analyze"
    )
    
    # Year filter
    year_range = st.sidebar.slider(
        "Time Period",
        min_value=int(df['year'].min()),
        max_value=int(df['year'].max()),
        value=(int(df['year'].min()), int(df['year'].max())),
        help="Select the time range for analysis"
    )
    
    # Metric selector for visualizations
    metric_options = {
        'Water Coverage (%)': 'metering_coverage',
        'NRW (%)': 'nrw_percentage',
        'E. Coli Pass Rate (%)': 'ecoli_pass_rate',
        'Complaint Resolution (%)': 'complaint_resolution_efficiency',
        'Wastewater Treatment Coverage (%)': 'ww_treatment_coverage'
    }
    selected_metric_display = st.sidebar.selectbox(
        "Select Metric for Visualization",
        options=list(metric_options.keys()),
        index=0
    )
    selected_metric = metric_options[selected_metric_display]
    
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **💡 Navigation Tip:**
    
    Use the pages in the sidebar to explore detailed country-specific analytics with advanced filtering.
    """)
    
    # Filter data based on selections
    filtered_df = df[
        (df['country'].isin(selected_countries)) &
        (df['year'] >= year_range[0]) &
        (df['year'] <= year_range[1])
    ]
    
    # ===== SECTION 1: HIGH-LEVEL KPI CARDS =====
    st.markdown("## 📊 Where Are We? — Current State Overview")
    st.markdown("*Aggregate sector performance across all selected countries*")
    st.markdown("")
    
    # Calculate aggregate KPIs
    total_population = (filtered_df['households'].sum() * 5)  # Assuming 5 people per household
    total_metered = filtered_df['metered'].sum()
    total_households = filtered_df['households'].sum()
    avg_water_coverage = (total_metered / total_households * 100) if total_households > 0 else 0
    
    avg_nrw = filtered_df['nrw_percentage'].mean()
    avg_ecoli = filtered_df['ecoli_pass_rate'].mean()
    
    # Calculate cost recovery (O&M coverage proxy using complaints resolution as performance indicator)
    avg_resolution = filtered_df['complaint_resolution_efficiency'].mean()
    
    # Compliance metric (using water quality compliance as proxy)
    total_utilities = len(filtered_df['zone'].unique())
    compliant_utilities = len(filtered_df[filtered_df['ecoli_pass_rate'] >= 95]['zone'].unique())
    
    # Display KPI Cards
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric(
            "Total Population Served",
            f"{total_population/1_000_000:.1f}M",
            help="Estimated population served across all selected utilities"
        )
    
    with col2:
        nrw_icon, nrw_status = get_kpi_status(avg_nrw, 25, higher_is_better=False)
        st.metric(
            "Sector-Wide NRW",
            f"{avg_nrw:.1f}%",
            delta=f"{nrw_icon} {'Above' if avg_nrw > 25 else 'Below'} 25% benchmark",
            help="Non-Revenue Water - Target: <25%"
        )
    
    with col3:
        coverage_icon, coverage_status = get_kpi_status(avg_water_coverage, 80, higher_is_better=True)
        st.metric(
            "Avg Water Coverage",
            f"{avg_water_coverage:.1f}%",
            delta=f"{coverage_icon} Metering rate",
            help="Average percentage of households with metered connections"
        )
    
    with col4:
        ecoli_icon, ecoli_status = get_kpi_status(avg_ecoli, 95, higher_is_better=True)
        st.metric(
            "Water Quality (E. Coli)",
            f"{avg_ecoli:.1f}%",
            delta=f"{ecoli_icon} Pass rate",
            help="E. Coli test pass rate - WHO Target: >95%"
        )
    
    with col5:
        st.metric(
            "Service Efficiency",
            f"{avg_resolution:.1f}%",
            delta="Complaint resolution",
            help="Average complaint resolution rate"
        )
    
    with col6:
        compliance_rate = (compliant_utilities / total_utilities * 100) if total_utilities > 0 else 0
        st.metric(
            "Quality Compliance",
            f"{compliant_utilities}/{total_utilities}",
            delta=f"{compliance_rate:.0f}% zones",
            help="Zones meeting WHO water quality standards (>95% E. Coli pass rate)"
        )
    
    st.markdown("---")
    
    # ===== SECTION 2: WHAT NEEDS ATTENTION — ACTIONABLE INSIGHTS =====
    st.markdown("## ⚠️ What Needs Attention? — Critical Gaps & Priorities")
    
    # Calculate critical gaps
    high_nrw_count = len(filtered_df[filtered_df['nrw_percentage'] > 25])
    total_records = len(filtered_df)
    high_nrw_pct = (high_nrw_count / total_records * 100) if total_records > 0 else 0
    
    low_coverage_zones = filtered_df[filtered_df['metering_coverage'] < 50].groupby('zone')['metering_coverage'].mean()
    
    poor_quality_zones = filtered_df[filtered_df['ecoli_pass_rate'] < 95].groupby('zone')['ecoli_pass_rate'].mean().sort_values()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="alert-critical">
        <h4 style="margin-top: 0; color: #dc2626;">🚨 High Non-Revenue Water</h4>
        <p style="margin-bottom: 0;"><strong>{high_nrw_pct:.1f}%</strong> of zones exceed the 25% NRW benchmark</p>
        <p style="font-size: 0.85rem; color: #991b1b; margin-bottom: 0;">Priority: Infrastructure leak detection and repair programs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="alert-warning">
        <h4 style="margin-top: 0; color: #f59e0b;">⚡ Low Coverage Zones</h4>
        <p style="margin-bottom: 0;"><strong>{len(low_coverage_zones)}</strong> zones with less than 50% coverage</p>
        <p style="font-size: 0.85rem; color: #92400e; margin-bottom: 0;">Priority: Expand connection programs and infrastructure</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="alert-warning">
        <h4 style="margin-top: 0; color: #f59e0b;">💧 Water Quality Concerns</h4>
        <p style="margin-bottom: 0;"><strong>{len(poor_quality_zones)}</strong> zones below 95% E. Coli compliance</p>
        <p style="font-size: 0.85rem; color: #92400e; margin-bottom: 0;">Priority: Enhanced treatment and monitoring protocols</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== SECTION 3: COUNTRY COMPARISON =====
    st.markdown("## 🌍 How Are We Doing? — Country Comparison")
    st.markdown("*Side-by-side comparison across Service, Production, Access, and Finance domains*")
    st.markdown("")
    
    # Aggregate by country
    country_comparison = filtered_df.groupby('country').agg({
        'metering_coverage': 'mean',
        'nrw_percentage': 'mean',
        'ecoli_pass_rate': 'mean',
        'complaint_resolution_efficiency': 'mean',
        'ww_treatment_coverage': 'mean',
        'households': 'sum',
        'population_estimate': 'sum'
    }).round(2).reset_index()
    
    country_comparison.columns = [
        'Country',
        'Water Coverage (%)',
        'NRW (%)',
        'E. Coli Pass Rate (%)',
        'Complaint Resolution (%)',
        'WW Treatment Coverage (%)',
        'Total Households',
        'Population Served'
    ]
    
    # Create interactive comparison chart
    col1, col2 = st.columns(2)
    
    with col1:
        # Multi-metric radar chart would be ideal, but let's use grouped bar chart
        comparison_melted = country_comparison.melt(
            id_vars=['Country'],
            value_vars=['Water Coverage (%)', 'E. Coli Pass Rate (%)', 'Complaint Resolution (%)'],
            var_name='Metric',
            value_name='Value'
        )
        
        fig_comparison = px.bar(
            comparison_melted,
            x='Country',
            y='Value',
            color='Metric',
            barmode='group',
            title='Service Performance Indicators by Country',
            color_discrete_sequence=['#4facfe', '#11998e', '#667eea']
        )
        fig_comparison.update_layout(
            height=400,
            yaxis_title='Percentage (%)',
            template='plotly_white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_comparison, use_container_width=True)
    
    with col2:
        # NRW comparison with benchmark
        fig_nrw = go.Figure()
        
        colors = ['#10b981' if val <= 25 else '#f59e0b' if val <= 35 else '#dc2626' 
                  for val in country_comparison['NRW (%)']]
        
        fig_nrw.add_trace(go.Bar(
            x=country_comparison['Country'],
            y=country_comparison['NRW (%)'],
            marker_color=colors,
            text=country_comparison['NRW (%)'],
            texttemplate='%{text:.1f}%',
            textposition='outside'
        ))
        
        fig_nrw.add_hline(
            y=25,
            line_dash="dash",
            line_color="#10b981",
            annotation_text="Benchmark: 25%",
            annotation_position="right"
        )
        
        fig_nrw.update_layout(
            title='Non-Revenue Water by Country (Lower is Better)',
            yaxis_title='NRW (%)',
            height=400,
            template='plotly_white',
            showlegend=False
        )
        st.plotly_chart(fig_nrw, use_container_width=True)
    
    # Detailed comparison table with color coding
    st.markdown("### 📋 Detailed Performance Metrics")
    
    # Format and style the dataframe
    styled_comparison = country_comparison.style.background_gradient(
        subset=['Water Coverage (%)', 'E. Coli Pass Rate (%)', 'Complaint Resolution (%)'],
        cmap='RdYlGn',
        vmin=0,
        vmax=100
    ).background_gradient(
        subset=['NRW (%)'],
        cmap='RdYlGn_r',
        vmin=0,
        vmax=50
    ).format({
        'Water Coverage (%)': '{:.1f}%',
        'NRW (%)': '{:.1f}%',
        'E. Coli Pass Rate (%)': '{:.1f}%',
        'Complaint Resolution (%)': '{:.1f}%',
        'WW Treatment Coverage (%)': '{:.1f}%',
        'Total Households': '{:,.0f}',
        'Population Served': '{:,.0f}'
    })
    
    st.dataframe(styled_comparison, use_container_width=True)
    
    st.markdown("---")
    
    # ===== SECTION 4: TREND ANALYSIS =====
    st.markdown("## 📈 Progress & Trends — Are We Improving?")
    st.markdown(f"*Tracking **{selected_metric_display}** over time ({year_range[0]}-{year_range[1]})*")
    st.markdown("")
    
    # Time series data
    trends = filtered_df.groupby(['country', 'year']).agg({
        selected_metric: 'mean'
    }).reset_index()
    
    # Create trend line chart
    fig_trends = px.line(
        trends,
        x='year',
        y=selected_metric,
        color='country',
        markers=True,
        title=f'{selected_metric_display} Trends by Country',
        color_discrete_map={
            'cameroon': '#4facfe',
            'lesotho': '#f09819',
            'malawi': '#11998e',
            'Uganda': '#eb3349'
        }
    )
    
    # Add benchmark lines based on metric
    if selected_metric == 'nrw_percentage':
        fig_trends.add_hline(y=25, line_dash="dash", line_color="green", 
                            annotation_text="Target: 25%", annotation_position="right")
    elif selected_metric == 'ecoli_pass_rate':
        fig_trends.add_hline(y=95, line_dash="dash", line_color="green",
                            annotation_text="WHO Target: 95%", annotation_position="right")
    elif selected_metric == 'metering_coverage':
        fig_trends.add_hline(y=80, line_dash="dash", line_color="green",
                            annotation_text="Target: 80%", annotation_position="right")
    
    fig_trends.update_layout(
        height=450,
        xaxis_title='Year',
        yaxis_title=selected_metric_display,
        template='plotly_white',
        hovermode='x unified',
        legend=dict(
            title="Country",
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)"
        )
    )
    
    st.plotly_chart(fig_trends, use_container_width=True)
    
    # Year-over-year change analysis
    st.markdown("### 📊 Year-over-Year Performance Change")
    
    if len(filtered_df['year'].unique()) >= 2:
        latest_year = filtered_df['year'].max()
        previous_year = latest_year - 1
        
        latest_data = filtered_df[filtered_df['year'] == latest_year].groupby('country')[selected_metric].mean()
        previous_data = filtered_df[filtered_df['year'] == previous_year].groupby('country')[selected_metric].mean()
        
        yoy_change = ((latest_data - previous_data) / previous_data * 100).round(2)
        
        col1, col2, col3, col4 = st.columns(4)
        cols = [col1, col2, col3, col4]
        
        for idx, (country, change) in enumerate(yoy_change.items()):
            if idx < 4:
                with cols[idx]:
                    delta_color = "normal" if (selected_metric == 'nrw_percentage' and change < 0) or \
                                            (selected_metric != 'nrw_percentage' and change > 0) else "inverse"
                    st.metric(
                        country.title(),
                        f"{latest_data[country]:.1f}{'%' if selected_metric != 'connections_per_employee' else ''}",
                        delta=f"{change:+.1f}% vs {previous_year}",
                        delta_color=delta_color
                    )
    
    st.markdown("---")
    
    # ===== SECTION 5: MAP VISUALIZATION (Simplified) =====
    st.markdown("## 🗺️ Geographic Performance Overview")
    
    # Create a simple geographic comparison
    country_geo_data = filtered_df.groupby('country').agg({
        selected_metric: 'mean',
        'households': 'sum'
    }).reset_index()
    
    # Color code based on performance
    def get_performance_color(value, metric):
        if metric == 'nrw_percentage':
            if value <= 25:
                return '#10b981'
            elif value <= 35:
                return '#f59e0b'
            else:
                return '#dc2626'
        else:  # Higher is better
            if value >= 80:
                return '#10b981'
            elif value >= 60:
                return '#f59e0b'
            else:
                return '#dc2626'
    
    country_geo_data['color'] = country_geo_data[selected_metric].apply(
        lambda x: get_performance_color(x, selected_metric)
    )
    
    fig_map = go.Figure(data=[go.Bar(
        x=country_geo_data['country'],
        y=country_geo_data[selected_metric],
        marker_color=country_geo_data['color'],
        text=country_geo_data[selected_metric],
        texttemplate='%{text:.1f}%',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>' +
                      selected_metric_display + ': %{y:.1f}%<br>' +
                      '<extra></extra>'
    )])
    
    fig_map.update_layout(
        title=f'{selected_metric_display} by Country (Color-coded by Performance)',
        xaxis_title='Country',
        yaxis_title=selected_metric_display,
        height=400,
        template='plotly_white',
        showlegend=False
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
    
    st.markdown("---")
    
    # ===== CALL TO ACTION =====
    st.markdown("## 🎯 Take Action")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="alert-success">
        <h4 style="margin-top: 0; color: #047857;">✅ Explore the Data</h4>
        <p style="margin-bottom: 0.5rem;">Use the country-specific pages in the sidebar for detailed analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="alert-success">
        <h4 style="margin-top: 0; color: #047857;">🔍 Identify Gaps</h4>
        <p style="margin-bottom: 0.5rem;">Review critical alerts and compare performance across regions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="alert-success">
        <h4 style="margin-top: 0; color: #047857;">📊 Track Progress</h4>
        <p style="margin-bottom: 0.5rem;">Monitor trends toward SDG 6 targets and national objectives</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

