"""
Access Domain Page
Access & equity analysis (urban vs rural)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.visualizations import create_stacked_area, create_treemap, COLORS, apply_theme_to_chart
from utils.ai_insights import generate_access_insights, render_ai_insights, is_ai_available


def show_chart(fig, **kwargs):
    """Apply theme and display chart with proper dark mode support"""
    apply_theme_to_chart(fig)
    st.plotly_chart(fig, **kwargs)


def render_access_page(data, countries_filter, date_range=None):
    """Render the access domain page"""
    
    st.title("🌍 Access Domain")
    st.markdown("### Access & Equity Analysis")
    
    # Filter data
    w_access = data['w_access']
    s_access = data['s_access']
    
    if countries_filter:
        w_access = w_access[w_access['country'].isin(countries_filter)]
        s_access = s_access[s_access['country'].isin(countries_filter)]
    
    # Get latest year
    latest_year = w_access['year'].max()
    w_access_latest = w_access[w_access['year'] == latest_year]
    s_access_latest = s_access[s_access['year'] == latest_year]
    
    st.markdown("---")
    
    # Key Metrics
    st.header("📊 Access Coverage Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_pop_w = w_access_latest['popn_total'].sum()
        safely_managed_w = w_access_latest['safely_managed'].sum()
        coverage_sm_w = (safely_managed_w / total_pop_w * 100) if total_pop_w > 0 else 0
        
        st.metric(
            "Water - Safely Managed",
            f"{coverage_sm_w:.1f}%",
            help="% population with safely managed water access"
        )
    
    with col2:
        basic_w = w_access_latest['basic'].sum()
        coverage_basic_w = (basic_w / total_pop_w * 100) if total_pop_w > 0 else 0
        
        st.metric(
            "Water - Basic",
            f"{coverage_basic_w:.1f}%",
            help="% population with basic water access"
        )
    
    with col3:
        total_pop_s = s_access_latest['popn_total'].sum()
        safely_managed_s = s_access_latest['safely_managed'].sum()
        coverage_sm_s = (safely_managed_s / total_pop_s * 100) if total_pop_s > 0 else 0
        
        st.metric(
            "Sanitation - Safely Managed",
            f"{coverage_sm_s:.1f}%",
            help="% population with safely managed sanitation"
        )
    
    with col4:
        basic_s = s_access_latest['basic'].sum()
        coverage_basic_s = (basic_s / total_pop_s * 100) if total_pop_s > 0 else 0
        
        st.metric(
            "Sanitation - Basic",
            f"{coverage_basic_s:.1f}%",
            help="% population with basic sanitation"
        )
    
    st.markdown("---")
    
    # JMP Service Ladder - Water
    st.header("💧 Water Access - JMP Service Ladder")
    
    # Calculate ladder breakdown
    water_ladder = w_access_latest.groupby('country').agg({
        'safely_managed': 'sum',
        'basic': 'sum',
        'limited': 'sum',
        'unimproved': 'sum',
        'surface_water': 'sum',
        'popn_total': 'sum'
    }).reset_index()
    
    # Convert to percentages
    for col in ['safely_managed', 'basic', 'limited', 'unimproved', 'surface_water']:
        water_ladder[f'{col}_pct'] = (water_ladder[col] / water_ladder['popn_total'] * 100)
    
    # Stacked bar chart
    fig = go.Figure()
    
    categories = ['safely_managed_pct', 'basic_pct', 'limited_pct', 'unimproved_pct', 'surface_water_pct']
    colors = [COLORS['good'], COLORS['acceptable'], '#f1c40f', COLORS['poor'], '#34495e']
    names = ['Safely Managed', 'Basic', 'Limited', 'Unimproved', 'Surface Water']
    
    for cat, color, name in zip(categories, colors, names):
        fig.add_trace(go.Bar(
            name=name,
            x=water_ladder['country'],
            y=water_ladder[cat],
            marker_color=color
        ))
    
    fig.update_layout(
        barmode='stack',
        title='Water Access Distribution by Country (JMP Ladder)',
        xaxis_title='Country',
        yaxis_title='Population (%)',
        height=450,
        hovermode='x unified'
    )
    
    show_chart(fig, use_container_width=True)
    
    # Trends over time
    water_trend = w_access.groupby(['year', 'country']).agg({
        'safely_managed': 'sum',
        'basic': 'sum',
        'popn_total': 'sum'
    }).reset_index()
    water_trend['coverage'] = (
        (water_trend['safely_managed'] + water_trend['basic']) / water_trend['popn_total'] * 100
    )
    
    fig = px.line(
        water_trend,
        x='year',
        y='coverage',
        color='country',
        title='Water Coverage Trend (Safely Managed + Basic)',
        color_discrete_map=COLORS['countries'],
        markers=True
    )
    fig.add_hline(
        y=100,
        line_dash="dash",
        line_color="red",
        annotation_text="Universal Coverage Target"
    )
    fig.update_layout(height=400, hovermode='x unified')
    
    show_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # JMP Service Ladder - Sanitation
    st.header("🚽 Sanitation Access - JMP Service Ladder")
    
    # Calculate ladder breakdown
    san_ladder = s_access_latest.groupby('country').agg({
        'safely_managed': 'sum',
        'basic': 'sum',
        'limited': 'sum',
        'unimproved': 'sum',
        'open_def': 'sum',
        'popn_total': 'sum'
    }).reset_index()
    
    # Convert to percentages
    for col in ['safely_managed', 'basic', 'limited', 'unimproved', 'open_def']:
        san_ladder[f'{col}_pct'] = (san_ladder[col] / san_ladder['popn_total'] * 100)
    
    # Stacked bar chart
    fig = go.Figure()
    
    categories = ['safely_managed_pct', 'basic_pct', 'limited_pct', 'unimproved_pct', 'open_def_pct']
    colors = [COLORS['good'], COLORS['acceptable'], '#f1c40f', COLORS['poor'], '#000000']
    names = ['Safely Managed', 'Basic', 'Limited', 'Unimproved', 'Open Defecation']
    
    for cat, color, name in zip(categories, colors, names):
        fig.add_trace(go.Bar(
            name=name,
            x=san_ladder['country'],
            y=san_ladder[cat],
            marker_color=color
        ))
    
    fig.update_layout(
        barmode='stack',
        title='Sanitation Access Distribution by Country (JMP Ladder)',
        xaxis_title='Country',
        yaxis_title='Population (%)',
        height=450,
        hovermode='x unified'
    )
    
    show_chart(fig, use_container_width=True)
    
    # Sanitation trends
    san_trend = s_access.groupby(['year', 'country']).agg({
        'safely_managed': 'sum',
        'basic': 'sum',
        'popn_total': 'sum'
    }).reset_index()
    san_trend['coverage'] = (
        (san_trend['safely_managed'] + san_trend['basic']) / san_trend['popn_total'] * 100
    )
    
    fig = px.line(
        san_trend,
        x='year',
        y='coverage',
        color='country',
        title='Sanitation Coverage Trend (Safely Managed + Basic)',
        color_discrete_map=COLORS['countries'],
        markers=True
    )
    fig.add_hline(
        y=100,
        line_dash="dash",
        line_color="red",
        annotation_text="Universal Coverage Target"
    )
    fig.update_layout(height=400, hovermode='x unified')
    
    show_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Urban vs Rural Gap Analysis
    st.header("🏙️ Urban vs Rural Coverage Gap")
    
    # Calculate municipal (urban) vs non-municipal coverage
    urban_rural = w_access_latest.groupby('country').agg({
        'municipal_coverage': 'sum',
        'popn_total': 'sum'
    }).reset_index()
    # Safe division with zero-check
    urban_rural['municipal_pct'] = np.where(
        urban_rural['popn_total'] != 0,
        (urban_rural['municipal_coverage'] / urban_rural['popn_total'] * 100),
        0
    )
    urban_rural['rural_pct'] = 100 - urban_rural['municipal_pct']
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            urban_rural,
            x='country',
            y=['municipal_pct', 'rural_pct'],
            title='Urban vs Rural Population Distribution',
            barmode='stack',
            color_discrete_sequence=[COLORS['primary'], COLORS['secondary']],
            labels={'value': 'Population (%)', 'variable': 'Area Type'}
        )
        fig.update_layout(height=400)
        
        show_chart(fig, use_container_width=True)
    
    with col2:
        # Coverage gap calculation
        coverage_gap = w_access_latest.groupby('country').agg({
            'safely_managed': 'sum',
            'basic': 'sum',
            'municipal_coverage': 'sum',
            'popn_total': 'sum'
        }).reset_index()
        coverage_gap['total_coverage'] = (
            (coverage_gap['safely_managed'] + coverage_gap['basic']) / 
            coverage_gap['popn_total'] * 100
        )
        coverage_gap['gap'] = 100 - coverage_gap['total_coverage']
        
        fig = px.bar(
            coverage_gap,
            x='country',
            y='gap',
            title='Water Access Gap by Country',
            color='country',
            color_discrete_map=COLORS['countries']
        )
        fig.update_layout(height=400, showlegend=False)
        fig.update_yaxes(title='Coverage Gap (%)')
        
        show_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Zone-level analysis - Renamed for positive framing
    st.header("📍 Priority Zone Analysis")
    
    # Get zones with lowest coverage - priority for improvement
    zone_coverage = w_access_latest.copy()
    zone_coverage['coverage'] = (
        (zone_coverage['safely_managed'] + zone_coverage['basic']) / 
        zone_coverage['popn_total'].replace({0: np.nan}) * 100
    )
    zone_coverage['coverage'] = zone_coverage['coverage'].fillna(0)  # Replace NaN with 0 for display
    worst_zones = zone_coverage.nsmallest(15, 'coverage')[['country', 'zone', 'coverage', 'popn_total']]
    
    fig = px.bar(
        worst_zones,
        x='coverage',
        y='zone',
        color='country',
        title='Priority Zones for Coverage Improvement',
        orientation='h',
        color_discrete_map=COLORS['countries']
    )
    fig.update_layout(height=500)
    
    show_chart(fig, use_container_width=True)
    
    # Population distribution by access level - Horizontal stacked bar chart
    pop_chart_data = w_access_latest.copy()
    pop_chart_data['access_level'] = pd.cut(
        pop_chart_data['safely_managed_pct'],
        bins=[0, 25, 50, 75, 100],
        labels=['Poor (<25%)', 'Low (25-50%)', 'Medium (50-75%)', 'Good (>75%)']
    )
    
    # Aggregate by country and access level
    access_dist = pop_chart_data.groupby(['country', 'access_level'])['popn_total'].sum().reset_index()
    
    # Create stacked bar chart
    fig = px.bar(
        access_dist,
        x='popn_total',
        y='country',
        color='access_level',
        title='Population Distribution by Access Level',
        orientation='h',
        color_discrete_map={
            'Poor (<25%)': COLORS['poor'],
            'Low (25-50%)': COLORS['acceptable'],
            'Medium (50-75%)': '#f1c40f',
            'Good (>75%)': COLORS['good']
        },
        labels={'popn_total': 'Population', 'access_level': 'Access Level'},
        category_orders={'access_level': ['Poor (<25%)', 'Low (25-50%)', 'Medium (50-75%)', 'Good (>75%)']}
    )
    fig.update_layout(
        height=400,
        barmode='stack',
        legend_title='Access Level',
        xaxis_title='Total Population',
        yaxis_title='Country'
    )
    
    show_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Prescriptive Insights - AI Generated
    st.header("💡 Insights & Recommendations")
    
    # Identify underserved zones
    underserved = zone_coverage[zone_coverage['coverage'] < 50].copy()
    underserved_pop = underserved['popn_total'].sum()
    
    # Calculate coverage data for AI context
    coverage_data = {
        'water_safely_managed': coverage_sm_w,
        'water_basic': coverage_basic_w,
        'sanitation_safely_managed': coverage_sm_s,
        'sanitation_basic': coverage_basic_s,
        'total_population': total_pop_w
    }
    
    # Calculate zone data for AI context
    zone_data = {
        'low_coverage_zones': len(underserved),
        'avg_gap': 100 - zone_coverage['coverage'].mean() if not zone_coverage.empty else 0,
        'highest_disparity_zone': worst_zones.iloc[0]['zone'] if len(worst_zones) > 0 else 'N/A'
    }
    
    # Get country context
    country_context = countries_filter[0] if countries_filter and len(countries_filter) == 1 else None
    
    # Generate AI insights - only shows if AI is available
    ai_insights = generate_access_insights(coverage_data, zone_data, country_context) if is_ai_available() else None
    render_ai_insights(ai_insights, "🤖 AI-Powered Analysis")
    
    # Priority Zones Table
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ Priority Investment Zones")
        if len(underserved) > 0:
            st.caption(f"{len(underserved)} zones have coverage below 50%")
            st.dataframe(
                worst_zones.head(10)[['zone', 'country', 'coverage', 'popn_total']],
                use_container_width=True
            )
        else:
            st.success("✅ No zones with critically low coverage (<50%)")
    
    with col2:
        st.subheader("📊 Open Defecation Hotspots")
        od_zones = s_access_latest.nlargest(10, 'open_def')[['country', 'zone', 'open_def', 'open_def_pct']]
        if len(od_zones) > 0:
            od_count = len(s_access_latest[s_access_latest['open_def_pct'] > 5])
            st.caption(f"{od_count} zones have open defecation >5%")
            st.dataframe(od_zones, use_container_width=True)

