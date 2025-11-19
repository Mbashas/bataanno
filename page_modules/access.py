"""
Access Domain Page
Access & equity analysis (urban vs rural)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.visualizations import create_stacked_area, create_treemap, COLORS


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
    
    st.plotly_chart(fig, width='stretch')
    
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
    
    st.plotly_chart(fig, width='stretch')
    
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
    
    st.plotly_chart(fig, width='stretch')
    
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
    
    st.plotly_chart(fig, width='stretch')
    
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
        
        st.plotly_chart(fig, width='stretch')
    
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
        
        st.plotly_chart(fig, width='stretch')
    
    st.markdown("---")
    
    # Zone-level analysis
    st.header("📍 Zone-Level Access Analysis")
    
    # Get zones with lowest coverage
    zone_coverage = w_access_latest.copy()
    zone_coverage['coverage'] = (
        (zone_coverage['safely_managed'] + zone_coverage['basic']) / 
        zone_coverage['popn_total'] * 100
    )
    worst_zones = zone_coverage.nsmallest(15, 'coverage')[['country', 'zone', 'coverage', 'popn_total']]
    
    fig = px.bar(
        worst_zones,
        x='coverage',
        y='zone',
        color='country',
        title='Zones with Lowest Water Coverage (Bottom 15)',
        orientation='h',
        color_discrete_map=COLORS['countries']
    )
    fig.update_layout(height=500)
    
    st.plotly_chart(fig, width='stretch')
    
    # Population treemap
    pop_treemap_data = w_access_latest.copy()
    pop_treemap_data['access_level'] = pd.cut(
        pop_treemap_data['safely_managed_pct'],
        bins=[0, 25, 50, 75, 100],
        labels=['Poor (<25%)', 'Low (25-50%)', 'Medium (50-75%)', 'Good (>75%)']
    )
    
    fig = px.treemap(
        pop_treemap_data,
        path=['country', 'access_level', 'zone'],
        values='popn_total',
        title='Population Distribution by Access Level',
        color='safely_managed_pct',
        color_continuous_scale='RdYlGn',
        color_continuous_midpoint=50
    )
    fig.update_layout(height=600)
    
    st.plotly_chart(fig, width='stretch')
    
    st.markdown("---")
    
    # Prescriptive Insights
    st.header("💡 Prescriptive Insights & Recommendations")
    
    # Identify underserved zones
    underserved = zone_coverage[zone_coverage['coverage'] < 50].copy()
    underserved_pop = underserved['popn_total'].sum()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ Priority Investment Zones")
        
        if len(underserved) > 0:
            st.warning(f"""
            **{len(underserved)} zones** have coverage below 50%
            
            - **Total underserved population**: {underserved_pop:,.0f}
            - **Average coverage in these zones**: {underserved['coverage'].mean():.1f}%
            
            **Recommended Actions:**
            1. Prioritize infrastructure expansion in these zones
            2. Consider Small-Scale Service Providers (SSSPs) for rapid deployment
            3. Implement pro-poor tariff structures to ensure affordability
            4. Allocate budget proportional to population gap
            """)
            
            # Show top priority zones
            st.dataframe(
                worst_zones.head(10)[['zone', 'country', 'coverage', 'popn_total']],
                width='stretch'
            )
        else:
            st.success("✅ No zones with critically low coverage (<50%)")
    
    with col2:
        st.subheader("📊 Open Defecation Hotspots")
        
        # Zones with highest open defecation
        od_zones = s_access_latest.nlargest(10, 'open_def')[['country', 'zone', 'open_def', 'open_def_pct']]
        
        if len(od_zones) > 0:
            st.error(f"""
            **{len(s_access_latest[s_access_latest['open_def_pct'] > 5])} zones** have open defecation >5%
            
            **Highest Open Defecation Zones:**
            """)
            
            st.dataframe(
                od_zones,
                width='stretch'
            )
            
            st.markdown("""
            **Recommended Actions:**
            1. Launch Community-Led Total Sanitation (CLTS) programs
            2. Provide subsidies for household latrine construction
            3. Increase public toilet facilities in high-density areas
            4. Conduct sanitation awareness campaigns
            """)
    
    # Equity analysis
    st.subheader("⚖️ Equity Analysis")
    
    # Calculate Gini coefficient or disparity metrics
    coverage_std = zone_coverage.groupby('country')['coverage'].std()
    
    st.info(f"""
    **Coverage Disparity by Country:**
    
    {chr(10).join([f"- **{country}**: Standard deviation of {std:.1f}% across zones" 
                   for country, std in coverage_std.items()])}
    
    **Interpretation**: Higher standard deviation indicates greater inequality in access across zones.
    Countries should aim for uniform coverage to achieve equitable service delivery.
    
    **Equity Targets:**
    - Reduce within-country coverage gap to <10 percentage points
    - Ensure all zones achieve minimum 75% coverage by 2025
    - Prioritize marginalized and rural communities in expansion plans
    """)

