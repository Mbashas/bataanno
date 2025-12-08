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
from utils.ai_insights import generate_service_insights, render_ai_insights, is_ai_available
from utils.visualizations import apply_theme_to_chart


def show_chart(fig, **kwargs):
    """Apply theme and display chart with proper dark mode support"""
    apply_theme_to_chart(fig)
    st.plotly_chart(fig, **kwargs)

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
    
    # DELETED: Country-level water quality bar charts and associated data calculations.
    
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
        
        show_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Metering Analysis
    st.header("📊 Metering Analysis & Revenue Impact")
    
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
        title='Zones Needing Meter Installation',
        orientation='h',
        color_discrete_map=COLORS['countries'],
        labels={'metering_ratio': 'Metering Ratio (%)', 'zone': 'Zone'}
    )
    fig.add_vline(
        x=95,
        line_dash="dash",
        line_color="red",
        annotation_text="Target: 95%"
    )
    fig.update_layout(height=600)
    
    show_chart(fig, use_container_width=True)
    st.caption("Zones with lowest metering ratios - priority for meter installation programs.")
    
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
            title='Impact of Metering on Revenue Collection',
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
        
        show_chart(fig, use_container_width=True)
    
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
        
        show_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Complaints Analysis
    st.header("📞 Complaints and Resolution")
    
    # Complaints by country (data calculation kept for trend chart)
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
    
    # DELETED: Total Complaints, Resolved, Overall Resolution Metrics
    
    # Complaints trend over time (kept per feedback)
    st.subheader("Complaint and Resolution Trend")
    
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
    show_chart(fig, use_container_width=True)
    
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
        
        show_chart(fig, use_container_width=True)
    
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
        
        show_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Service Insights - AI Generated
    st.header("🔍 Service Quality Insights")
    
    # Calculate wastewater treatment rate for AI context
    ww_collected_total = s_service['ww_collected'].sum() if 'ww_collected' in s_service.columns else 0
    ww_treated_total = s_service['ww_treated'].sum() if 'ww_treated' in s_service.columns else 0
    treatment_rate_val = (ww_treated_total / ww_collected_total * 100) if ww_collected_total > 0 else 0
    
    # Prepare service data for AI context
    service_ai_data = {
        'chlorine_compliance': quality_rate,
        'ecoli_compliance': ecoli_rate,
        'metering_ratio': metering_rate,
        'resolution_rate': resolution_rate,
        'total_complaints': complaints,
        'unresolved': complaints - resolved,
        'treatment_rate': treatment_rate_val
    }
    
    # Get country context
    country_context = countries_filter[0] if countries_filter and len(countries_filter) == 1 else None
    
    # Generate AI insights - only shows if AI is available
    ai_insights = generate_service_insights(service_ai_data, country_context) if is_ai_available() else None
    render_ai_insights(ai_insights, "🤖 AI-Powered Service Analysis")