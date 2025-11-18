"""
Overview Dashboard Page
High-level KPI scorecard with trends and comparisons
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.kpi_calculator import calculate_summary_kpis, calculate_country_kpis, get_kpi_status
from utils.visualizations import create_kpi_card, create_trend_line, COLORS, BENCHMARKS


def render_overview_page(data, countries_filter, date_range=None):
    """Render the overview dashboard page"""
    
    st.title("📊 Overview Dashboard")
    st.markdown("### High-Level Performance Metrics Across All Countries")
    
    # Filter data by selected countries
    if countries_filter:
        data_filtered = {
            key: df[df['country'].isin(countries_filter)] if 'country' in df.columns else df
            for key, df in data.items()
        }
    else:
        data_filtered = data
    
    # Calculate KPIs
    summary_kpis = calculate_summary_kpis(data_filtered)
    
    if not summary_kpis:
        st.warning("No KPI data is available for the current filter selection. Adjust the filters to load results.")
        return

    st.markdown("---")
    
    # KPI Scorecard Section
    st.header("🎯 KPI Scorecard")
    st.markdown("Compare performance against sector benchmarks across the four insight domains.")

    kpi_card_config = [
        ('water_coverage', "Water Coverage"),
        ('sanitation_coverage', "Sanitation Coverage"),
        ('nrw', "Non-Revenue Water"),
        ('water_quality', "Drinking Water Quality"),
        ('service_hours', "Hours of Supply"),
        ('collection_efficiency', "Revenue Collection Efficiency"),
        ('occr', "O&M Cost Coverage (OCCR)"),
        ('personnel_cost_ratio', "Personnel Cost as % of O&M"),
        ('metering_ratio', "Metering Ratio"),
        ('staff_productivity', "Staff Productivity (per 1k connections)"),
    ]

    # Display KPI cards in rows of 4 to prevent overlap
    cols_per_row = 4
    for idx, (key, title) in enumerate(kpi_card_config):
        metric = summary_kpis.get(key)
        if metric is None:
            continue

        if idx % cols_per_row == 0:
            row_cols = st.columns(cols_per_row)

        inverse = metric.get('inverse', False)
        fig = create_kpi_card(
            title,
            metric['value'],
            metric['benchmark'],
            unit=metric.get('unit', ''),
            inverse=inverse
        )

        with row_cols[idx % cols_per_row]:
            st.plotly_chart(fig, width='stretch')
    
    # Add spacing after KPI cards
    st.markdown("<br>", unsafe_allow_html=True)

    # Cross-country status heatmap setup
    kpi_column_map = {
        'water_coverage': 'Water Coverage (%)',
        'sanitation_coverage': 'Sanitation Coverage (%)',
        'nrw': 'NRW (%)',
        'water_quality': 'Water Quality (%)',
        'service_hours': 'Hours of Supply',
        'collection_efficiency': 'Collection Efficiency (%)',
        'occr': 'OCCR (%)',
        'personnel_cost_ratio': 'Personnel Cost % of O&M',
        'metering_ratio': 'Metering Ratio (%)',
        'staff_productivity': 'Staff / 1k Connections'
    }

    production_df = data_filtered.get('production', pd.DataFrame())
    countries = countries_filter if countries_filter else sorted(production_df['country'].unique()) if not production_df.empty else []
    if len(countries) == 0 and 'w_access' in data_filtered and not data_filtered['w_access'].empty:
        countries = sorted(data_filtered['w_access']['country'].unique())

    country_comparison = []
    for country in countries:
        kpis = calculate_country_kpis(data_filtered, country)
        if not kpis:
            continue

        record = {'Country': country}
        for key, column_name in kpi_column_map.items():
            record[column_name] = kpis.get(key, 0)
        country_comparison.append(record)

    if country_comparison:
        st.subheader("🗺️ KPI Status by Country")
        comparison_df = pd.DataFrame(country_comparison)

        status_map = {'poor': 0, 'acceptable': 1, 'good': 2}
        heatmap_metrics = list(kpi_column_map.items())
        z_values = []
        text_values = []

        for key, column_name in heatmap_metrics:
            metric = summary_kpis.get(key, {})
            benchmark = metric.get('benchmark', 0)
            inverse = metric.get('inverse', False)
            unit = metric.get('unit', '')

            row_status = []
            row_text = []
            for _, row in comparison_df.iterrows():
                value = row[column_name]
                status, _ = get_kpi_status(value, benchmark, inverse=inverse)
                row_status.append(status_map.get(status, None))

                if unit == '%':
                    text = f"{value:.1f}%"
                elif key == 'service_hours':
                    text = f"{value:.1f} hrs"
                elif key == 'staff_productivity':
                    text = f"{value:.1f}"
                else:
                    text = f"{value:.1f}"
                row_text.append(text)

            z_values.append(row_status)
            text_values.append(row_text)

        heatmap_fig = go.Figure(
            data=go.Heatmap(
                z=z_values,
                x=comparison_df['Country'],
                y=[label for _, label in heatmap_metrics],
                text=text_values,
                texttemplate="%{text}",
                colorscale=[
                    [0.0, COLORS['poor']],
                    [0.5, COLORS['acceptable']],
                    [1.0, COLORS['good']]
                ],
                zmin=0,
                zmax=2,
                hovertemplate="<b>%{y}</b><br>Country: %{x}<br>Value: %{text}<extra></extra>"
            )
        )

        heatmap_fig.update_layout(
            height=420,
            margin=dict(l=80, r=40, t=60, b=60),
            title="KPI Status Matrix (Good → Green, Acceptable → Amber, Needs Attention → Red)",
            xaxis=dict(title="Country"),
            yaxis=dict(title="Key KPIs")
        )

        st.plotly_chart(heatmap_fig, width='stretch')
        st.caption("Color-coded KPI matrix helps quickly identify top performers and areas that need attention.")
    else:
        comparison_df = pd.DataFrame(columns=['Country'])
    
    st.markdown("---")
    
    # Trend Analysis Section
    st.header("📈 Trends Over Time (2020-2024)")
    
    # Prepare trend data
    w_access = data_filtered['w_access']
    finance = data_filtered['finance']
    
    # Water coverage trend by year
    coverage_trend = w_access.groupby('year').agg({
        'safely_managed': 'sum',
        'basic': 'sum',
        'popn_total': 'sum'
    }).reset_index()
    coverage_trend['water_coverage'] = (
        (coverage_trend['safely_managed'] + coverage_trend['basic']) / 
        coverage_trend['popn_total'] * 100
    )
    
    # OCCR trend by year
    occr_trend = finance.groupby('year').agg({
        'sewer_revenue': 'sum',
        'opex': 'sum'
    }).reset_index()
    occr_trend['occr'] = (occr_trend['sewer_revenue'] / occr_trend['opex']) * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = create_trend_line(
            coverage_trend,
            'year',
            'water_coverage',
            'Water Coverage Trend',
            color=COLORS['primary'],
            benchmark=100
        )
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        fig = create_trend_line(
            occr_trend,
            'year',
            'occr',
            'OCCR Trend',
            color=COLORS['good'],
            benchmark=110
        )
        st.plotly_chart(fig, width='stretch')
    
    st.markdown("---")
    
    # Country Comparison Section
    st.header("🌍 Cross-Country Comparison")
    
    if comparison_df.empty:
        st.info("No country-level KPIs to compare for the selected filters.")
        countries = []
    else:
        display_columns = ['Country'] + list(kpi_column_map.values())
        comparison_df = comparison_df.reindex(columns=display_columns).fillna(0)

    st.dataframe(
        comparison_df.set_index('Country').style.background_gradient(
            cmap='RdYlGn',
            subset=['Water Coverage (%)', 'Sanitation Coverage (%)', 'OCCR (%)', 'Collection Efficiency (%)', 'Metering Ratio (%)']
        ),
        width='stretch'
    )

    countries = comparison_df['Country'].tolist()
    
    # Radar chart for multi-dimensional comparison
    if countries:
        fig = go.Figure()
        
        categories = ['Water Coverage', 'Sanitation Coverage', 'OCCR', 'Collection Efficiency']
        
        for _, row in comparison_df.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[
                    row['Water Coverage (%)'],
                    row['Sanitation Coverage (%)'],
                    row['OCCR (%)'],
                    row['Collection Efficiency (%)']
                ],
                theta=categories,
                fill='toself',
                name=row['Country'],
                line_color=COLORS['countries'].get(row['Country'], COLORS['primary'])
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 120]
                )
            ),
            title="Multi-Dimensional Country Comparison",
            height=500
        )
        
        st.plotly_chart(fig, width='stretch')
    
    st.markdown("---")
    
    # Performance Highlights
    st.header("🏆 Performance Highlights")
    
    col1, col2 = st.columns(2)
    
    if comparison_df.empty:
        with col1:
            st.info("No performance highlights available for the selected filters.")
        with col2:
            st.info("Adjust filters to review country performance rankings.")
    else:
        with col1:
            st.subheader("✅ Top Performers")
            
            top_coverage = comparison_df.nlargest(3, 'Water Coverage (%)')
            st.markdown("**🥇 Best Water Coverage:**")
            for _, row in top_coverage.iterrows():
                st.markdown(f"- **{row['Country']}**: {row['Water Coverage (%)']:.1f}%")
            
            top_occr = comparison_df.nlargest(3, 'OCCR (%)')
            st.markdown("**💰 Best Cost Recovery (OCCR):**")
            for _, row in top_occr.iterrows():
                st.markdown(f"- **{row['Country']}**: {row['OCCR (%)']:.1f}%")

            top_collection = comparison_df.nlargest(3, 'Collection Efficiency (%)')
            st.markdown("**💵 Highest Collection Efficiency:**")
            for _, row in top_collection.iterrows():
                st.markdown(f"- **{row['Country']}**: {row['Collection Efficiency (%)']:.1f}%")
        
        with col2:
            st.subheader("⚠️ Areas Needing Attention")
            
            bottom_coverage = comparison_df.nsmallest(3, 'Water Coverage (%)')
            st.markdown("**💧 Lowest Water Coverage:**")
            for _, row in bottom_coverage.iterrows():
                st.markdown(f"- **{row['Country']}**: {row['Water Coverage (%)']:.1f}%")
            
            top_nrw = comparison_df.nlargest(3, 'NRW (%)')
            st.markdown("**💸 Highest Non-Revenue Water:**")
            for _, row in top_nrw.iterrows():
                st.markdown(f"- **{row['Country']}**: {row['NRW (%)']:.1f}%")

            high_personnel = comparison_df.nlargest(3, 'Personnel Cost % of O&M')
            st.markdown("**👥 Highest Personnel Cost Share:**")
            for _, row in high_personnel.iterrows():
                st.markdown(f"- **{row['Country']}**: {row['Personnel Cost % of O&M']:.1f}%")
    
    st.markdown("---")
    
    # Key Insights
    st.header("💡 Key Insights")
    
    st.info(
        """
    **Descriptive Insights:**
    - Average water coverage across selected filters: **{water_cov:.1f}%** (Target: 100%)
    - Average sanitation coverage: **{san_cov:.1f}%** (Target: 100%)
    - Average non-revenue water: **{nrw:.1f}%** (Benchmark: ≤25%)
    - Average hours of supply: **{service_hours:.1f} hrs/day** (Benchmark: ≥20 hrs)
    - Staff productivity averages **{staff_prod:.1f} staff/1k connections** (Benchmark: ≤7)
    - Personnel costs represent **{personnel:.1f}%** of O&M spend (Target: ≤35%)
    
    **Diagnostic Insights:**
    - Countries with higher metering ratios consistently realize stronger revenue collection efficiency.
    - Persistent high NRW correlates with lower OCCR, eroding cost recovery.
    - Elevated personnel cost shares often coincide with staff productivity above the 7 staff/1k connections benchmark.
    """.format(
            water_cov=summary_kpis['water_coverage']['value'],
            san_cov=summary_kpis['sanitation_coverage']['value'],
            nrw=summary_kpis['nrw']['value'],
            service_hours=summary_kpis['service_hours']['value'],
            staff_prod=summary_kpis['staff_productivity']['value'],
            personnel=summary_kpis['personnel_cost_ratio']['value'],
        )
    )

