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
from utils.currency_config import format_currency_multi_country, get_currency_label


def render_finance_page(data, countries_filter, date_range=None):
    """Render the finance domain page"""
    
    st.title("💰 Finance Domain")
    st.markdown("### Financial Sustainability and Cost Recovery")
    
    # Filter data
    finance_df = data['finance']
    
    if countries_filter:
        finance_df = finance_df[finance_df['country'].isin(countries_filter)]
    
    # Currency context banner
    selected_countries = finance_df['country'].unique().tolist() if not finance_df.empty else []
    if len(selected_countries) == 1:
        currency_label = get_currency_label(selected_countries[0])
        st.info(f"💱 **Currency Context:** All financial metrics displayed in {currency_label}")
    elif len(selected_countries) > 1:
        from utils.currency_config import CURRENCY_CONFIG
        currencies = ', '.join([CURRENCY_CONFIG.get(c, {}).get('symbol', 'LCU') for c in selected_countries])
        st.warning(f"💱 **Multi-Currency View:** Data includes {currencies}. Values are in local currencies and NOT directly comparable without conversion.")
    
    st.markdown("---")
    
    # Key Financial Metrics
    st.header("📊 Key Financial Metrics")
    
    # Calculate aggregates
    total_billed = finance_df['sewer_billed'].sum()
    total_revenue = finance_df['sewer_revenue'].sum()
    total_opex = finance_df['opex'].sum()
    uncollected = total_billed - total_revenue
    
    # Get selected countries for currency formatting
    selected_countries = finance_df['country'].unique().tolist() if not finance_df.empty else []
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Billed",
            format_currency_multi_country(total_billed, selected_countries),
            help="Total amount billed to customers (local currency)"
        )
    
    with col2:
        st.metric(
            "Revenue Collected",
            format_currency_multi_country(total_revenue, selected_countries),
            help="Total revenue collected from customers (local currency)"
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
            format_currency_multi_country(total_opex, selected_countries),
            help="Total operational expenditure (local currency)"
        )
    
    with col6:
        surplus_deficit = total_revenue - total_opex
        st.metric(
            "Operating Surplus/Deficit",
            format_currency_multi_country(surplus_deficit, selected_countries),
            delta_color="normal" if surplus_deficit >= 0 else "inverse",
            help="Revenue minus operating expenses (local currency)"
        )
    
    with col7:
        st.metric(
            "Uncollected Revenue",
            format_currency_multi_country(uncollected, selected_countries),
            delta_color="inverse",
            help="Billed amount not yet collected (local currency)"
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
    
    # ============================================================================
    # SECTION C: CUSTOMER PAYMENT BEHAVIOR BY ZONE (NEW)
    # ============================================================================
    st.markdown("---")
    st.header("💳 Customer Payment Behavior by Zone")
    st.markdown("Analyze revenue collection efficiency at the zone level using customer billing data")
    
    # Check if billing data is available
    if 'billing' in data and len(data['billing']) > 0:
        billing_df = data['billing']
        
        # Apply filters
        if countries_filter:
            billing_df = billing_df[billing_df['country'].isin(countries_filter)]
        
        # Get payment by zone
        from utils.kpi_calculator import get_payment_by_zone
        payment_by_zone = get_payment_by_zone(billing_df)
        
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Total Customers",
                f"{payment_by_zone['customer_count'].sum():,.0f}",
                help="Total number of customers in selected countries"
            )
        with col2:
            avg_collection_rate = payment_by_zone['collection_rate'].mean()
            st.metric(
                "Avg Collection Rate",
                f"{avg_collection_rate:.1f}%",
                help="Average collection rate across all zones"
            )
        with col3:
            # Safe idxmax with empty check
            if not payment_by_zone.empty and len(payment_by_zone) > 0:
                best_zone = payment_by_zone.loc[payment_by_zone['collection_rate'].idxmax()]
                st.metric(
                    "Best Performing Zone",
                    f"{best_zone['zone']}",
                    f"{best_zone['collection_rate']:.1f}%",
                    help="Zone with highest collection rate"
                )
            else:
                st.metric("Best Performing Zone", "N/A", help="No zone data available")
        with col4:
            # Safe idxmin with empty check
            if not payment_by_zone.empty and len(payment_by_zone) > 0:
                worst_zone = payment_by_zone.loc[payment_by_zone['collection_rate'].idxmin()]
                st.metric(
                    "Needs Attention",
                    f"{worst_zone['zone']}",
                    f"{worst_zone['collection_rate']:.1f}%",
                    delta_color="inverse",
                    help="Zone with lowest collection rate"
                )
            else:
                st.metric("Needs Attention", "N/A", help="No zone data available")
        
        # Bar chart visualization
        st.subheader("Collection Rate by Zone")
        
        # Validate data before visualization
        if payment_by_zone.empty or len(payment_by_zone) == 0:
            st.info("No zone-level payment data available for visualization.")
        else:
            fig = px.bar(
                payment_by_zone.sort_values('collection_rate', ascending=False),
                x='zone',
                y='collection_rate',
                color='collection_rate',
                color_continuous_scale='RdYlGn',
                range_color=[0, 100],
                hover_data=['total_billed', 'total_paid', 'customer_count'],
                title='Revenue Collection Efficiency by Zone',
                labels={'collection_rate': 'Collection Rate (%)', 'zone': 'Zone'}
            )
            
            fig.update_layout(
                height=500,
                xaxis_tickangle=-45,
                paper_bgcolor=COLORS['bg_chart'],
                plot_bgcolor=COLORS['bg_chart'],
                font={'color': COLORS['text_dark']}
            )
            
            st.plotly_chart(fig, width='stretch')
        
        # Zone comparison table
        st.subheader("Zone Performance Details")
        display_df = payment_by_zone.copy()
        display_df['total_billed'] = display_df['total_billed'].apply(lambda x: f"${x/1e6:.2f}M")
        display_df['total_paid'] = display_df['total_paid'].apply(lambda x: f"${x/1e6:.2f}M")
        display_df['collection_rate'] = display_df['collection_rate'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(
            display_df[['country', 'zone', 'customer_count', 'total_billed', 'total_paid', 'collection_rate']],
            use_container_width=True
        )
    else:
        st.warning("⚠️ Customer billing data not available. Please ensure billing.csv is loaded.")
    
    # ============================================================================
    # SECTION D: PAYMENT RISK DASHBOARD (NEW)
    # ============================================================================
    st.markdown("---")
    st.header("⚠️ Customer Payment Risk Analysis")
    st.markdown("Identify customers at risk of non-payment and prioritize collection efforts")
    
    if 'billing' in data and len(data['billing']) > 0:
        billing_df = data['billing']
        
        # Apply filters
        if countries_filter:
            billing_df = billing_df[billing_df['country'].isin(countries_filter)]
        
        # Identify risk customers
        from utils.kpi_calculator import identify_payment_risk_customers
        risk_customers = identify_payment_risk_customers(billing_df)
        
        # Display risk metrics
        st.subheader("Customer Risk Segmentation")
        col1, col2, col3 = st.columns(3)
        
        high_risk_count = len(risk_customers[risk_customers['risk_category'] == 'High Risk'])
        medium_risk_count = len(risk_customers[risk_customers['risk_category'] == 'Medium Risk'])
        low_risk_count = len(risk_customers[risk_customers['risk_category'] == 'Low Risk'])
        
        with col1:
            st.metric(
                "🔴 High Risk Customers",
                f"{high_risk_count:,}",
                f"{high_risk_count/len(risk_customers)*100:.1f}%",
                delta_color="inverse",
                help="Customers who paid < 50% of billed amount"
            )
        
        with col2:
            st.metric(
                "🟡 Medium Risk Customers",
                f"{medium_risk_count:,}",
                f"{medium_risk_count/len(risk_customers)*100:.1f}%",
                help="Customers who paid 50-80% of billed amount"
            )
        
        with col3:
            st.metric(
                "🟢 Low Risk Customers",
                f"{low_risk_count:,}",
                f"{low_risk_count/len(risk_customers)*100:.1f}%",
                help="Customers who paid ≥ 80% of billed amount"
            )
        
        # Risk distribution pie chart
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("Risk Category Distribution")
            risk_counts = risk_customers['risk_category'].value_counts()
            
            fig = go.Figure(data=[go.Pie(
                labels=risk_counts.index,
                values=risk_counts.values,
                hole=0.3,
                marker=dict(colors=[COLORS['poor'], COLORS['acceptable'], COLORS['good']])
            )])
            
            fig.update_layout(
                title='Customer Distribution by Risk Category',
                height=400,
                paper_bgcolor=COLORS['bg_chart'],
                font={'color': COLORS['text_dark']}
            )
            
            st.plotly_chart(fig, width='stretch')
        
        with col_right:
            st.subheader("Unpaid Amount by Risk Category")
            unpaid_by_risk = risk_customers.groupby('risk_category')['unpaid_amount'].sum().reset_index()
            
            fig = px.bar(
                unpaid_by_risk,
                x='risk_category',
                y='unpaid_amount',
                color='risk_category',
                color_discrete_map={
                    'High Risk': COLORS['poor'],
                    'Medium Risk': COLORS['acceptable'],
                    'Low Risk': COLORS['good']
                },
                title='Total Unpaid Amount by Risk Category',
                labels={'unpaid_amount': 'Unpaid Amount ($)', 'risk_category': 'Risk Category'}
            )
            
            fig.update_layout(
                height=400,
                showlegend=False,
                paper_bgcolor=COLORS['bg_chart'],
                plot_bgcolor=COLORS['bg_chart'],
                font={'color': COLORS['text_dark']}
            )
            st.plotly_chart(fig, width='stretch')
        
        # Top 10 Non-Payers
        st.subheader("🔴 Top 10 Customers with Highest Unpaid Bills")
        top_unpaid = risk_customers.nlargest(10, 'unpaid_amount')
        
        fig = px.bar(
            top_unpaid,
            x='customer_id',
            y='unpaid_amount',
            color='zone',
            hover_data=['country', 'billed', 'paid', 'payment_ratio'],
            title='Top 10 Customers by Unpaid Amount',
            labels={'unpaid_amount': 'Unpaid Amount ($)', 'customer_id': 'Customer ID'}
        )
        
        fig.update_layout(
            height=500,
            xaxis_title='Customer ID',
            yaxis_title='Unpaid Amount ($)',
            paper_bgcolor=COLORS['bg_chart'],
            plot_bgcolor=COLORS['bg_chart'],
            font={'color': COLORS['text_dark']}
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # Actionable recommendations
        high_risk_unpaid = risk_customers[risk_customers['risk_category'] == 'High Risk']['unpaid_amount'].sum()
        top_zones = risk_customers[risk_customers['risk_category'] == 'High Risk'].groupby('zone').size().nlargest(3).index.tolist()
        
        st.info(f"""
        **💡 Recommended Actions:**
        - **Immediate Priority**: Contact {high_risk_count:,} high-risk customers for payment follow-up
        - **Potential Revenue Recovery**: ${high_risk_unpaid/1e6:.2f}M from high-risk customers
        - **Focus Zones**: {', '.join(top_zones[:3])}
        """)
    else:
        st.warning("⚠️ Customer billing data not available. Please ensure billing.csv is loaded.")
    
    # ============================================================================
    # SECTION E: COMMERCIAL VS. PHYSICAL NRW BREAKDOWN (NEW)
    # ============================================================================
    st.markdown("---")
    st.header("📊 Non-Revenue Water: Commercial vs. Physical Losses")
    st.markdown("Diagnose the root cause of NRW - infrastructure issues or revenue management")
    
    if 'billing' in data and 'production' in data and len(data['billing']) > 0:
        billing_df = data['billing']
        production_df = data['production']
        
        # Apply filters
        if countries_filter:
            billing_df = billing_df[billing_df['country'].isin(countries_filter)]
            production_df = production_df[production_df['country'].isin(countries_filter)]
        
        # Calculate losses
        from utils.kpi_calculator import calculate_commercial_nrw, calculate_physical_nrw
        
        commercial_losses = calculate_commercial_nrw(billing_df, finance_df)
        physical_losses = calculate_physical_nrw(production_df, billing_df)
        
        # Calculate revenue water
        total_produced = production_df['production_m3'].sum()
        revenue_water = max(total_produced - physical_losses - commercial_losses, 0)
        
        # Display summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            physical_pct = (physical_losses / total_produced * 100) if total_produced > 0 else 0
            st.metric(
                "Physical Losses",
                f"{physical_losses/1e6:.2f}M m³",
                f"{physical_pct:.1f}% of production",
                delta_color="inverse",
                help="Water lost through leaks, theft, meter inaccuracies"
            )
        
        with col2:
            commercial_pct = (commercial_losses / total_produced * 100) if total_produced > 0 else 0
            st.metric(
                "Commercial Losses",
                f"{commercial_losses/1e6:.2f}M m³",
                f"{commercial_pct:.1f}% of production",
                delta_color="inverse",
                help="Revenue lost due to non-payment (volume equivalent)"
            )
        
        with col3:
            revenue_pct = (revenue_water / total_produced * 100) if total_produced > 0 else 0
            st.metric(
                "Revenue Water",
                f"{revenue_water/1e6:.2f}M m³",
                f"{revenue_pct:.1f}% of production",
                help="Water that generates revenue"
            )
        
        # Pie chart visualization
        col_chart, col_insights = st.columns([2, 1])
        
        with col_chart:
            fig = go.Figure(data=[go.Pie(
                labels=['Physical Losses', 'Commercial Losses', 'Revenue Water'],
                values=[physical_losses, commercial_losses, revenue_water],
                hole=0.4,
                marker=dict(colors=[COLORS['poor'], '#ff7043', COLORS['good']]),
                textinfo='label+percent',
                textposition='outside'
            )])
            
            fig.update_layout(
                title='NRW Breakdown: Physical vs. Commercial Losses',
                height=500,
                showlegend=True,
                paper_bgcolor=COLORS['bg_chart'],
                font={'color': COLORS['text_dark']}
            )
            
            st.plotly_chart(fig, width='stretch')
        
        with col_insights:
            st.subheader("Key Insights")
            
            if physical_pct > commercial_pct:
                st.error(f"""
                **🔧 Infrastructure Priority**
                
                Physical losses ({physical_pct:.1f}%) exceed commercial losses ({commercial_pct:.1f}%).
                
                **Recommended Actions:**
                - Conduct leak detection surveys
                - Repair aging infrastructure
                - Upgrade meter accuracy
                - Implement pressure management
                """)
            else:
                st.warning(f"""
                **💰 Revenue Management Priority**
                
                Commercial losses ({commercial_pct:.1f}%) exceed physical losses ({physical_pct:.1f}%).
                
                **Recommended Actions:**
                - Improve billing accuracy
                - Enhance collection efforts
                - Implement disconnection policies
                - Offer payment plans
                """)
            
            total_nrw_pct = physical_pct + commercial_pct
            benchmark = 25.0
            
            if total_nrw_pct > benchmark:
                gap_volume = (total_produced * (total_nrw_pct - benchmark) / 100) / 1e6
                st.info(f"""
                **📊 Overall NRW Status**
                
                Total NRW: {total_nrw_pct:.1f}%  
                Benchmark: ≤{benchmark}%  
                Gap: {total_nrw_pct - benchmark:.1f}%
                
                Reducing NRW to benchmark could save:
                - {gap_volume:.2f}M m³
                """)
    else:
        st.warning("⚠️ Billing or production data not available. Please ensure all datasets are loaded.")

