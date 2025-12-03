"""
Service Domain Page
Service quality and reliability metrics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.kpi_calculator import (
    calculate_water_quality_compliance,
    calculate_metering_ratio,
    calculate_complaint_resolution_rate,
    calculate_collection_efficiency,
)
from utils.visualizations import create_kpi_card, COLORS

COUNTRY_ISO_MAP = {
    'Uganda': 'UGA',
    'Cameroon': 'CMR',
    'Lesotho': 'LSO',
    'Malawi': 'MWI'
}


def render_service_page(data, countries_filter, date_range=None):
    """Render the service domain page"""
    
    st.title("🚰 Service Domain")
    st.markdown("### Service Quality and Reliability Metrics")
    
    # Filter data
    w_service = data['w_service'].copy()
    s_service = data['s_service'].copy()
    finance = data['finance'].copy()
    production_df = data.get('production', pd.DataFrame()).copy()
    
    if countries_filter:
        w_service = w_service[w_service['country'].isin(countries_filter)]
        s_service = s_service[s_service['country'].isin(countries_filter)]
        finance = finance[finance['country'].isin(countries_filter)]
        if not production_df.empty:
            production_df = production_df[production_df['country'].isin(countries_filter)]
    
    st.markdown("---")
    
    # Key Metrics
    st.header("📊 Key Service Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Water quality compliance (chlorine)
        chlorine_passed = w_service['test_passed_chlorine'].sum()
        chlorine_conducted = w_service['tests_conducted_chlorine'].sum()
        quality_rate = calculate_water_quality_compliance(chlorine_passed, chlorine_conducted)
        delta = quality_rate - 95
        
        st.metric(
            "Water Quality (Chlorine)",
            f"{quality_rate:.1f}%",
            f"{delta:+.1f}%",
            delta_color="normal" if delta >= 0 else "inverse",
            help="Percentage of chlorine tests passed"
        )
    
    with col2:
        # E.coli compliance
        ecoli_passed = w_service['tests_passed_ecoli'].sum()
        ecoli_conducted = w_service['test_conducted_ecoli'].sum()
        ecoli_rate = calculate_water_quality_compliance(ecoli_passed, ecoli_conducted)
        delta_e = ecoli_rate - 95
        
        st.metric(
            "Water Quality (E.coli)",
            f"{ecoli_rate:.1f}%",
            f"{delta_e:+.1f}%",
            delta_color="normal" if delta_e >= 0 else "inverse",
            help="Percentage of E.coli tests passed"
        )
    
    with col3:
        # Metering ratio
        total_metered = w_service['metered'].sum()
        total_consumption = w_service['total_consumption'].sum()
        metering_rate = calculate_metering_ratio(total_metered, total_consumption)
        delta_m = metering_rate - 95
        
        st.metric(
            "Metering Ratio",
            f"{metering_rate:.1f}%",
            f"{delta_m:+.1f}%",
            delta_color="normal" if delta_m >= 0 else "inverse",
            help="Percentage of consumption recorded through meters"
        )
    
    with col4:
        # Complaint resolution rate
        resolved = finance['resolved'].sum()
        complaints = finance['complaints'].sum()
        resolution_rate = calculate_complaint_resolution_rate(resolved, complaints)
        
        st.metric(
            "Complaint Resolution",
            f"{resolution_rate:.1f}%",
            help="Percentage of complaints resolved"
        )
    
    st.markdown("---")
    
    # Water Quality Compliance Section
    st.header("🔬 Water Quality Compliance")
    
    # Quality trends over time
    quality_trend = w_service.groupby(['date', 'country']).agg({
        'test_passed_chlorine': 'sum',
        'tests_conducted_chlorine': 'sum',
        'tests_passed_ecoli': 'sum',
        'test_conducted_ecoli': 'sum'
    }).reset_index()
    
    quality_trend['chlorine_rate'] = (
        quality_trend['test_passed_chlorine'] / quality_trend['tests_conducted_chlorine'].replace({0: np.nan}) * 100
    )
    quality_trend['ecoli_rate'] = (
        quality_trend['tests_passed_ecoli'] / quality_trend['test_conducted_ecoli'].replace({0: np.nan}) * 100
    )
    
    chlorine_by_country = w_service.groupby('country').agg({
        'test_passed_chlorine': 'sum',
        'tests_conducted_chlorine': 'sum'
    }).reset_index()
    chlorine_by_country['compliance_rate'] = (
        chlorine_by_country['test_passed_chlorine'] /
        chlorine_by_country['tests_conducted_chlorine'].replace({0: np.nan})
    ) * 100

    ecoli_by_country = w_service.groupby('country').agg({
        'tests_passed_ecoli': 'sum',
        'test_conducted_ecoli': 'sum'
    }).reset_index()
    ecoli_by_country['compliance_rate'] = (
        ecoli_by_country['tests_passed_ecoli'] /
        ecoli_by_country['test_conducted_ecoli'].replace({0: np.nan})
    ) * 100

    countries_available = sorted(chlorine_by_country['country'].unique())

    if len(countries_available) == 0:
        st.info("Water quality testing data is not available for the selected filters.")
    else:
        st.subheader("Chlorine Compliance by Country")
        st.caption("Gauge benchmark set at ≥95% in line with WHO drinking water standards.")
        for i in range(0, len(countries_available), 4):
            row_countries = countries_available[i:i + 4]
            row_cols = st.columns(len(row_countries))
            for idx, country in enumerate(row_countries):
                # Safe iloc with empty check
                compliance_series = chlorine_by_country.loc[
                    chlorine_by_country['country'] == country, 'compliance_rate'
                ].fillna(0)
                compliance = compliance_series.iloc[0] if len(compliance_series) > 0 else 0
                
                fig = create_kpi_card(
                    f"{country} - Chlorine",
                    compliance,
                    95,
                    unit='%',
                    inverse=False
                )
                with row_cols[idx]:
                    st.plotly_chart(fig, width='stretch')

        st.subheader("E.coli Compliance by Country")
        for i in range(0, len(countries_available), 4):
            row_countries = countries_available[i:i + 4]
            row_cols = st.columns(len(row_countries))
            for idx, country in enumerate(row_countries):
                # Safe iloc with empty check
                compliance_series = ecoli_by_country.loc[
                    ecoli_by_country['country'] == country, 'compliance_rate'
                ].fillna(0)
                compliance = compliance_series.iloc[0] if len(compliance_series) > 0 else 0
                
                fig = create_kpi_card(
                    f"{country} - E.coli",
                    compliance,
                    95,
                    unit='%',
                    inverse=False
                )
                with row_cols[idx]:
                    st.plotly_chart(fig, width='stretch')

    st.subheader("🗺️ Hours of Supply Overview")
    if production_df.empty:
        st.info("Production time-series data is not available to map supply hours.")
    else:
        hours_by_country = production_df.groupby('country')['service_hours'].mean().reset_index()
        hours_by_country['iso_alpha'] = hours_by_country['country'].map(COUNTRY_ISO_MAP)

        fig = px.choropleth(
            hours_by_country,
            locations='iso_alpha',
            color='service_hours',
            hover_name='country',
            color_continuous_scale='Viridis',
            title='Average Hours of Supply by Country',
            labels={'service_hours': 'Hours of Supply (avg)'}
        )
        fig.update_geos(showcountries=True, fitbounds="locations")
        fig.update_layout(height=420, margin=dict(l=0, r=0, t=50, b=0))
        st.plotly_chart(fig, width='stretch')
        st.caption("Zone-level shapefiles were not provided; map shows country averages with detailed zone-level insights below.")
    
    # Quality trends over time
    st.subheader("Water Quality Trends Over Time")
    
    # Validate data before visualization
    if quality_trend.empty or len(quality_trend) < 2:
        st.info("Insufficient data for water quality trend visualization. Need at least 2 data points.")
    else:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=quality_trend['date'],
            y=quality_trend['chlorine_rate'],
            mode='lines',
            name='Chlorine Compliance',
            line=dict(color=COLORS['primary'])
        ))
        
        fig.add_trace(go.Scatter(
            x=quality_trend['date'],
            y=quality_trend['ecoli_rate'],
            mode='lines',
            name='E.coli Compliance',
            line=dict(color=COLORS['good'])
        ))
        
        fig.add_hline(
            y=95,
            line_dash="dash",
            line_color="red",
            annotation_text="Benchmark: 95%"
        )
        
        fig.update_layout(
            title="Water Quality Compliance Over Time",
            height=400,
            hovermode='x unified',
            yaxis_title="Compliance Rate (%)",
            xaxis_title="Date"
        )
        
        st.plotly_chart(fig, width='stretch')
    
    st.markdown("---")
    
    # Metering Analysis
    st.header("📊 Metering and Consumption Analysis")
    
    # Metering ratio by zone
    metering_by_zone = w_service.groupby(['country', 'zone']).agg({
        'metered': 'sum',
        'total_consumption': 'sum'
    }).reset_index()
    metering_by_zone['metering_ratio'] = (
        metering_by_zone['metered'] / metering_by_zone['total_consumption'] * 100
    )
    metering_by_zone = metering_by_zone.sort_values('metering_ratio', ascending=True).head(20)
    
    fig = px.bar(
        metering_by_zone,
        x='metering_ratio',
        y='zone',
        color='country',
        title='Metering Ratio by Zone (Bottom 20)',
        orientation='h',
        color_discrete_map=COLORS['countries']
    )
    fig.add_vline(
        x=95,
        line_dash="dash",
        line_color="red",
        annotation_text="Benchmark: 95%"
    )
    fig.update_layout(height=600)
    
    st.plotly_chart(fig, width='stretch')
    
    # Scatter: Metering ratio vs consumption
    metering_country = w_service.groupby('country').agg({
        'metered': 'sum',
        'total_consumption': 'sum',
        'w_supplied': 'sum'
    }).reset_index()
    metering_country['metering_ratio'] = (
        metering_country['metered'] / metering_country['total_consumption'].replace({0: np.nan}) * 100
    )
    finance_eff = finance.groupby('country').agg({
        'sewer_revenue': 'sum',
        'sewer_billed': 'sum',
        'complaints': 'sum'
    }).reset_index()
    metering_country = metering_country.merge(finance_eff, on='country', how='left')
    metering_country['collection_eff'] = metering_country.apply(
        lambda row: calculate_collection_efficiency(row['sewer_revenue'], row['sewer_billed']),
        axis=1
    )
    metering_country = metering_country.dropna(subset=['metering_ratio', 'collection_eff'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.scatter(
            metering_country,
            x='metering_ratio',
            y='collection_eff',
            size='complaints',
            color='country',
            title='Metering Ratio vs Revenue Collection Efficiency',
            color_discrete_map=COLORS['countries'],
            labels={
                'metering_ratio': 'Metering Ratio (%)',
                'collection_eff': 'Collection Efficiency (%)',
                'complaints': 'Complaints'
            },
            hover_data={'w_supplied': True, 'sewer_revenue': True}
        )
        fig.update_layout(height=400, legend_title="Country")
        fig.add_hline(
            y=95,
            line_dash="dash",
            line_color="red",
            annotation_text="Collection Target 95%"
        )
        fig.add_vline(
            x=95,
            line_dash="dash",
            line_color="red",
            annotation_text="Metering Target 95%"
        )
        
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        # Metering trend over time
        metering_trend = w_service.groupby(['year', 'country']).agg({
            'metered': 'sum',
            'total_consumption': 'sum'
        }).reset_index()
        metering_trend['metering_ratio'] = (
            metering_trend['metered'] / metering_trend['total_consumption'] * 100
        )
        
        fig = px.line(
            metering_trend,
            x='year',
            y='metering_ratio',
            color='country',
            title='Metering Ratio Trend by Country',
            color_discrete_map=COLORS['countries'],
            markers=True
        )
        fig.add_hline(
            y=95,
            line_dash="dash",
            line_color="red",
            annotation_text="Benchmark"
        )
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, width='stretch')
    
    st.markdown("---")
    
    # Complaints Analysis
    st.header("📞 Complaints and Resolution")
    
    # Complaints by country
    complaints_by_country = finance.groupby('country').agg({
        'complaints': 'sum',
        'resolved': 'sum'
    }).reset_index()
    complaints_by_country['resolution_rate'] = (
        complaints_by_country['resolved'] / complaints_by_country['complaints'] * 100
    )
    complaints_by_country['unresolved'] = (
        complaints_by_country['complaints'] - complaints_by_country['resolved']
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            complaints_by_country,
            x='country',
            y=['resolved', 'unresolved'],
            title='Complaints Resolved vs Unresolved by Country',
            barmode='stack',
            color_discrete_sequence=[COLORS['good'], COLORS['poor']]
        )
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        fig = px.bar(
            complaints_by_country,
            x='country',
            y='resolution_rate',
            title='Complaint Resolution Rate by Country',
            color='country',
            color_discrete_map=COLORS['countries']
        )
        fig.add_hline(
            y=90,
            line_dash="dash",
            line_color="red",
            annotation_text="Target: 90%"
        )
        fig.update_layout(height=400, showlegend=False)
        
        st.plotly_chart(fig, width='stretch')
    
    # Complaints trend over time
    complaints_trend = finance.groupby('date').agg({
        'complaints': 'sum',
        'resolved': 'sum'
    }).reset_index()
    complaints_trend['pending'] = complaints_trend['complaints'] - complaints_trend['resolved']
    
    fig = px.bar(
        complaints_trend,
        x='date',
        y=['resolved', 'pending'],
        title='Complaints Resolved vs Pending Over Time',
        labels={'value': 'Number of Complaints', 'date': 'Date', 'variable': 'Status'},
        color_discrete_map={'resolved': COLORS['good'], 'pending': COLORS['poor']}
    )
    fig.update_layout(
        barmode='stack',
        height=400,
        hovermode='x unified',
        legend_title="Status"
    )
    st.plotly_chart(fig, width='stretch')
    
    st.markdown("---")
    
    # Wastewater Treatment
    st.header("🏭 Wastewater Treatment Performance")
    
    # Treatment rates
    treatment_by_country = s_service.groupby('country').agg({
        'ww_collected': 'sum',
        'ww_treated': 'sum',
        'ww_reused': 'sum'
    }).reset_index()
    treatment_by_country['treatment_rate'] = (
        treatment_by_country['ww_treated'] / treatment_by_country['ww_collected'] * 100
    )
    treatment_by_country['reuse_rate'] = (
        treatment_by_country['ww_reused'] / treatment_by_country['ww_treated'] * 100
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            treatment_by_country,
            x='country',
            y='treatment_rate',
            title='Wastewater Treatment Rate by Country',
            color='country',
            color_discrete_map=COLORS['countries']
        )
        fig.update_layout(height=400, showlegend=False)
        fig.update_yaxes(range=[0, 100])
        
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        fig = px.bar(
            treatment_by_country,
            x='country',
            y='reuse_rate',
            title='Treated Wastewater Reuse Rate by Country',
            color='country',
            color_discrete_map=COLORS['countries']
        )
        fig.update_layout(height=400, showlegend=False)
        fig.update_yaxes(range=[0, 100])
        
        st.plotly_chart(fig, width='stretch')
    
    st.markdown("---")
    
    # Diagnostic Insights
    st.header("🔍 Diagnostic Insights")
    
    hours_complaints_corr = None
    if not production_df.empty and not finance.empty:
        service_hours_country = production_df.groupby('country')['service_hours'].mean().reset_index(name='avg_service_hours')
        complaints_country = finance.groupby('country')['complaints'].sum().reset_index(name='complaints')
        merged_corr = service_hours_country.merge(complaints_country, on='country')
        if len(merged_corr) > 1:
            hours_complaints_corr = merged_corr['avg_service_hours'].corr(merged_corr['complaints'])
    
    corr_display = f"{hours_complaints_corr:.2f}" if hours_complaints_corr is not None else "N/A"
    
    st.info(f"""
    **Water Quality:**
    - Chlorine test pass rate: **{quality_rate:.1f}%** {"✅" if quality_rate >= 95 else "⚠️"}
    - E.coli test pass rate: **{ecoli_rate:.1f}%** {"✅" if ecoli_rate >= 95 else "⚠️"}
    
    **Metering:**
    - Overall metering ratio: **{metering_rate:.1f}%** {"✅" if metering_rate >= 95 else "⚠️"}
    - Zones below 50% metering contribute significantly to commercial losses
    
    **Customer Service:**
    - Complaint resolution rate: **{resolution_rate:.1f}%** {"✅" if resolution_rate >= 90 else "⚠️"}
    - Total unresolved complaints: **{complaints - resolved:,.0f}**
    - Service hours vs complaints correlation: **{corr_display}** (negative indicates fewer complaints with longer supply)
    
    **Recommendations:**
    - Install meters in zones with <50% metering ratio to reduce commercial losses
    - Investigate and address water quality issues in zones failing tests
    - Improve complaint resolution processes to reach 90%+ resolution rate
    - Increase wastewater treatment capacity where treatment rate < 80%
    """)

