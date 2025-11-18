"""
Finance Domain Page
Financial sustainability and cost recovery analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from utils.kpi_calculator import calculate_occr, calculate_collection_efficiency
from utils.visualizations import create_occr_dashboard, create_waterfall_chart, COLORS


def render_finance_page(data, countries_filter, date_range=None):
    """Render the finance domain page"""
    
    st.title("💰 Finance Domain")
    st.markdown("### Financial Sustainability and Cost Recovery")
    
    # Filter data
    finance_df = data['finance']
    
    if countries_filter:
        finance_df = finance_df[finance_df['country'].isin(countries_filter)]
    
    st.markdown("---")
    
    # Key Financial Metrics
    st.header("📊 Key Financial Metrics")
    
    # Calculate aggregates
    total_billed = finance_df['sewer_billed'].sum()
    total_revenue = finance_df['sewer_revenue'].sum()
    total_opex = finance_df['opex'].sum()
    uncollected = total_billed - total_revenue
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Billed",
            f"${total_billed / 1_000_000:,.1f}M",
            help="Total amount billed to customers"
        )
    
    with col2:
        st.metric(
            "Revenue Collected",
            f"${total_revenue / 1_000_000:,.1f}M",
            help="Total revenue collected from customers"
        )
    
    with col3:
        collection_eff = calculate_collection_efficiency(total_revenue, total_billed)
        delta = collection_eff - 95
        st.metric(
            "Collection Efficiency",
            f"{collection_eff:.1f}%",
            f"{delta:+.1f}%",
            delta_color="normal" if delta >= 0 else "inverse",
            help="Revenue collected as % of billed amount"
        )
    
    with col4:
        occr = calculate_occr(total_revenue, total_opex)
        delta_occr = occr - 110
        st.metric(
            "OCCR",
            f"{occr:.1f}%",
            f"{delta_occr:+.1f}%",
            delta_color="normal" if delta_occr >= 0 else "inverse",
            help="Operating Cost Coverage Ratio"
        )
    
    # Second row
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric(
            "Operating Expenses",
            f"${total_opex / 1_000_000:,.1f}M",
            help="Total operational expenditure"
        )
    
    with col6:
        surplus_deficit = total_revenue - total_opex
        st.metric(
            "Operating Surplus/Deficit",
            f"${surplus_deficit / 1_000_000:,.1f}M",
            delta_color="normal" if surplus_deficit >= 0 else "inverse",
            help="Revenue minus operating expenses"
        )
    
    with col7:
        st.metric(
            "Uncollected Revenue",
            f"${uncollected / 1_000_000:,.1f}M",
            delta_color="inverse",
            help="Billed amount not yet collected"
        )
    
    with col8:
        total_staff = finance_df['san_staff'].sum() + finance_df['w_staff'].sum()
        st.metric(
            "Total Staff",
            f"{total_staff:,.0f}",
            help="Total water and sanitation staff"
        )
    
    st.markdown("---")
    
    # OCCR Dashboard (2x2 Layout)
    st.header("📈 OCCR Performance Dashboard")
    
    # Create comprehensive OCCR dashboard
    fig = create_occr_dashboard(finance_df)
    st.plotly_chart(fig, width='stretch')
    
    st.markdown("---")
    
    # Financial Waterfall Charts by Country
    st.header("💧 Financial Waterfall Analysis")
    st.markdown("Visualizing the flow from billing to surplus/deficit for each country")
    
    # Calculate waterfall data by country
    countries = finance_df['country'].unique()
    
    # Create 2x2 subplot layout for waterfall charts
    rows = 2
    cols = 2
    fig = make_subplots(
        rows=rows,
        cols=cols,
        subplot_titles=[f"{country}" for country in countries[:4]],
        specs=[[{'type': 'waterfall'}, {'type': 'waterfall'}],
               [{'type': 'waterfall'}, {'type': 'waterfall'}]]
    )
    
    for idx, country in enumerate(countries[:4]):
        country_data = finance_df[finance_df['country'] == country]
        
        billed = country_data['sewer_billed'].sum()
        revenue = country_data['sewer_revenue'].sum()
        opex = country_data['opex'].sum()
        uncollected = billed - revenue
        surplus = revenue - opex
        
        row = (idx // 2) + 1
        col = (idx % 2) + 1
        
        fig.add_trace(
            go.Waterfall(
                name=country,
                orientation="v",
                measure=["relative", "relative", "relative", "total"],
                x=["Billed", "Uncollected", "OpEx", "Surplus/Deficit"],
                y=[billed, -uncollected, -opex, surplus],
                connector={"line": {"color": "rgb(63, 63, 63)"}},
                decreasing={"marker": {"color": COLORS['poor']}},
                increasing={"marker": {"color": COLORS['good']}},
                totals={"marker": {"color": COLORS['primary'] if surplus >= 0 else COLORS['poor']}},
                text=[f"${billed/1e6:.1f}M", f"-${uncollected/1e6:.1f}M", f"-${opex/1e6:.1f}M", f"${surplus/1e6:.1f}M"],
                textposition="outside"
            ),
            row=row,
            col=col
        )
    
    fig.update_layout(
        height=800,
        title_text="Financial Flow: Billed → Revenue → Operating Surplus/Deficit",
        showlegend=False
    )
    
    st.plotly_chart(fig, width='stretch')
    
    st.markdown("---")
    
    # Revenue and Cost Trends
    st.header("📊 Revenue and Cost Trends")
    
    # Monthly trends
    monthly_finance = finance_df.groupby('date').agg({
        'sewer_revenue': 'sum',
        'opex': 'sum',
        'sewer_billed': 'sum'
    }).reset_index()
    monthly_finance['occr'] = (monthly_finance['sewer_revenue'] / monthly_finance['opex']) * 100
    monthly_finance['collection_eff'] = (monthly_finance['sewer_revenue'] / monthly_finance['sewer_billed']) * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue vs Opex over time
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=monthly_finance['date'],
            y=monthly_finance['sewer_revenue'],
            mode='lines',
            name='Revenue',
            line=dict(color=COLORS['good'], width=2),
            fill='tonexty'
        ))
        
        fig.add_trace(go.Scatter(
            x=monthly_finance['date'],
            y=monthly_finance['opex'],
            mode='lines',
            name='Operating Expenses',
            line=dict(color=COLORS['poor'], width=2),
            fill='tozeroy'
        ))
        
        fig.update_layout(
            title='Revenue vs Operating Expenses Over Time',
            height=400,
            hovermode='x unified',
            yaxis_title='Amount ($)',
            xaxis_title='Date'
        )
        
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        # OCCR trend
        fig = px.line(
            monthly_finance,
            x='date',
            y='occr',
            title='OCCR Trend Over Time',
            labels={'occr': 'OCCR (%)', 'date': 'Date'}
        )
        fig.add_hline(
            y=110,
            line_dash="dash",
            line_color="red",
            annotation_text="Benchmark: 110%"
        )
        fig.update_traces(line_color=COLORS['primary'])
        fig.update_layout(height=400, hovermode='x unified')
        
        st.plotly_chart(fig, width='stretch')
    
    # OCCR and Collection Efficiency by Country
    country_finance = finance_df.groupby('country').agg({
        'sewer_revenue': 'sum',
        'opex': 'sum',
        'sewer_billed': 'sum'
    }).reset_index()
    country_finance['occr'] = (country_finance['sewer_revenue'] / country_finance['opex']) * 100
    country_finance['collection_eff'] = (country_finance['sewer_revenue'] / country_finance['sewer_billed']) * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            country_finance,
            x='country',
            y='occr',
            title='OCCR by Country',
            color='country',
            color_discrete_map=COLORS['countries']
        )
        fig.add_hline(
            y=110,
            line_dash="dash",
            line_color="red",
            annotation_text="Benchmark: 110%"
        )
        fig.update_layout(height=400, showlegend=False)
        
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        fig = px.bar(
            country_finance,
            x='country',
            y='collection_eff',
            title='Collection Efficiency by Country',
            color='country',
            color_discrete_map=COLORS['countries']
        )
        fig.add_hline(
            y=95,
            line_dash="dash",
            line_color="red",
            annotation_text="Benchmark: 95%"
        )
        fig.update_layout(height=400, showlegend=False)
        
        st.plotly_chart(fig, width='stretch')
    
    st.markdown("---")
    
    # Cost Structure Analysis
    st.header("💼 Cost Structure and Staffing")
    
    # Staff costs and productivity
    col1, col2 = st.columns(2)
    
    with col1:
        # Staff distribution
        staff_by_country = finance_df.groupby('country').agg({
            'san_staff': 'mean',
            'w_staff': 'mean'
        }).reset_index()
        
        fig = px.bar(
            staff_by_country,
            x='country',
            y=['w_staff', 'san_staff'],
            title='Average Staffing Levels by Country',
            barmode='group',
            color_discrete_sequence=[COLORS['primary'], COLORS['secondary']],
            labels={'value': 'Average Staff Count', 'variable': 'Department'}
        )
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        # Opex per staff
        country_opex_staff = finance_df.groupby('country').agg({
            'opex': 'sum',
            'san_staff': 'sum',
            'w_staff': 'sum'
        }).reset_index()
        country_opex_staff['total_staff'] = (
            country_opex_staff['san_staff'] + country_opex_staff['w_staff']
        )
        country_opex_staff['opex_per_staff'] = (
            country_opex_staff['opex'] / country_opex_staff['total_staff']
        )
        
        fig = px.bar(
            country_opex_staff,
            x='country',
            y='opex_per_staff',
            title='Operating Expenses per Staff Member',
            color='country',
            color_discrete_map=COLORS['countries']
        )
        fig.update_layout(height=400, showlegend=False)
        fig.update_yaxes(title='OpEx per Staff ($)')
        
        st.plotly_chart(fig, width='stretch')
    
    # Complaints and blocks vs revenue
    st.subheader("Service Issues vs Financial Performance")
    
    # Calculate OCCR by country first
    complaints_vs_occr = finance_df.groupby('country').agg({
        'complaints': 'sum',
        'blocks': 'sum',
        'sewer_revenue': 'sum',
        'opex': 'sum'
    }).reset_index()
    complaints_vs_occr['occr'] = (complaints_vs_occr['sewer_revenue'] / complaints_vs_occr['opex']) * 100
    
    fig = px.scatter(
        complaints_vs_occr,
        x='complaints',
        y='occr',
        size='blocks',
        color='country',
        title='Complaints vs OCCR (sized by Blockages)',
        color_discrete_map=COLORS['countries'],
        labels={'complaints': 'Total Complaints', 'occr': 'OCCR (%)'}
    )
    fig.add_hline(
        y=110,
        line_dash="dash",
        line_color="red",
        annotation_text="OCCR Benchmark"
    )
    fig.update_layout(height=500)
    
    st.plotly_chart(fig, width='stretch')
    
    st.markdown("---")
    
    # Diagnostic & Predictive Insights
    st.header("🔍 Financial Insights & Projections")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📉 Diagnostic Analysis")
        
        # Countries below OCCR benchmark
        low_occr = country_finance[country_finance['occr'] < 110]
        
        if len(low_occr) > 0:
            st.warning(f"""
            **{len(low_occr)} countries** are operating below the OCCR benchmark of 110%:
            
            {chr(10).join([f"- **{row['country']}**: {row['occr']:.1f}% OCCR" 
                           for _, row in low_occr.iterrows()])}
            
            **Key Issues Identified:**
            - Low collection efficiency contributing to revenue shortfall
            - High operational costs relative to revenue
            - Insufficient tariff levels to cover O&M costs
            
            **Root Causes:**
            - High Non-Revenue Water (NRW) reducing billable volume
            - Uncollected bills and payment defaults
            - Inefficient operations and overstaffing
            """)
        else:
            st.success("✅ All countries are meeting the OCCR benchmark of 110%")
    
    with col2:
        st.subheader("📈 Predictive Projections")
        
        # Calculate potential revenue recovery
        potential_recovery = uncollected * 0.9  # Assume 90% could be recovered
        current_gap = total_opex * 1.1 - total_revenue  # 110% OCCR target
        
        st.info(f"""
            **Revenue Recovery Potential:**
            
            - **Current uncollected revenue**: ${uncollected / 1_000_000:.2f}M
            - **Potential recovery (90%)**: ${potential_recovery / 1_000_000:.2f}M
            - **Current OCCR gap**: ${max(0, current_gap) / 1_000_000:.2f}M
            
            **If collection efficiency improves to 95%:**
            - Projected OCCR: **{((total_revenue + potential_recovery) / total_opex * 100):.1f}%**
            - Financial sustainability: **{'✅ Achieved' if ((total_revenue + potential_recovery) / total_opex * 100) >= 110 else '⚠️ Still Below Target'}**
            
            **Recommended Actions:**
            1. Implement automated billing and mobile payment systems
            2. Enforce disconnection policies for chronic defaulters
            3. Offer payment plans to reduce accumulated arrears
            4. Conduct customer education on payment importance
            """)
    
    # Prescriptive recommendations
    st.subheader("💡 Prescriptive Recommendations")
    
    st.success("""
    **To Improve Financial Sustainability:**
    
    **Revenue Enhancement:**
    - 📊 Implement cost-reflective tariffs (ensure full O&M cost recovery)
    - 💳 Introduce mobile money and automated payment options
    - 📈 Improve metering ratio to reduce commercial losses
    - 🔧 Reduce NRW through leak detection and repair programs
    
    **Cost Optimization:**
    - ⚡ Optimize energy consumption in pumping and treatment
    - 👥 Right-size staffing based on productivity benchmarks
    - 🔧 Implement preventive maintenance to reduce emergency repairs
    - 📊 Adopt performance-based budgeting
    
    **Financial Management:**
    - 💰 Separate capital and operating budgets
    - 📊 Implement monthly financial reporting and variance analysis
    - 🎯 Set country-specific OCCR improvement targets
    - 🏦 Explore credit facilities for infrastructure investment
    """)

