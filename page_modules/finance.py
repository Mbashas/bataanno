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
from utils.kpi_calculator import calculate_cost_recovery_ratio, calculate_collection_efficiency
from utils.visualizations import create_cost_recovery_dashboard, create_waterfall_chart, COLORS
from utils.currency_config import (
    format_currency_multi_country, 
    get_currency_label,
    format_currency_auto,
    is_usd_mode,
    toggle_currency_mode,
    get_currency_mode_label,
    convert_to_usd,
    format_usd,
    CURRENCY_CONFIG,
    EXCHANGE_RATE_DATE
)
from utils.ai_insights import generate_finance_insights, render_on_demand_insights, is_ai_available
from utils.visualizations import apply_theme_to_chart


def show_chart(fig, **kwargs):
    """Apply theme and display chart with proper dark mode support"""
    apply_theme_to_chart(fig)
    st.plotly_chart(fig, **kwargs)


def render_finance_page(data, countries_filter, date_range=None):
    """Render the finance domain page"""
    
    st.title("💰 Finance Domain")
    st.markdown("### Financial Sustainability and Cost Recovery")
    
    # Filter data
    finance_df = data['finance']
    
    if countries_filter:
        finance_df = finance_df[finance_df['country'].isin(countries_filter)]
    
    # Get selected countries for currency formatting
    selected_countries = finance_df['country'].unique().tolist() if not finance_df.empty else []
    
    # ========================================================================
    # USD CONVERSION TOGGLE
    # ========================================================================
    col_banner, col_toggle = st.columns([4, 1])
    
    with col_banner:
        # Currency context banner - updated to show current mode
        if is_usd_mode():
            st.success(f"💵 **USD Mode Active:** All values converted to US Dollars (Exchange rates from {EXCHANGE_RATE_DATE})")
        elif len(selected_countries) == 1:
            currency_label = get_currency_label(selected_countries[0])
            st.info(f"💱 **Currency Context:** All financial metrics displayed in {currency_label}")
        elif len(selected_countries) > 1:
            currencies = ', '.join([CURRENCY_CONFIG.get(c, {}).get('symbol', 'LCU') for c in selected_countries])
            st.warning(f"💱 **Multi-Currency View:** Data includes {currencies}. Values are in local currencies and NOT directly comparable without conversion. **Toggle USD mode for comparison.**")
    
    with col_toggle:
        # USD Toggle Button
        if is_usd_mode():
            button_label = "🌍 Show Local"
            button_help = "Switch to local currencies"
        else:
            button_label = "💵 Show USD"
            button_help = "Convert all values to USD for comparison"
        
        if st.button(button_label, key="usd_toggle", help=button_help, use_container_width=True):
            toggle_currency_mode()
            st.rerun()
    
    st.markdown("---")
    
    # Key Financial Metrics
    st.header("📊 Key Financial Metrics")
    
    # Calculate aggregates
    total_billed = finance_df['sewer_billed'].sum()
    total_revenue = finance_df['sewer_revenue'].sum()
    total_opex = finance_df['opex'].sum()
    uncollected = total_billed - total_revenue
    
    # Get selected countries for currency formatting (already defined above, but refresh for this section)
    selected_countries = finance_df['country'].unique().tolist() if not finance_df.empty else []
    
    # Helper for currency display based on mode
    def fmt_currency(value):
        return format_currency_auto(value, selected_countries)
    
    # Currency help text based on mode
    currency_help = "USD equivalent" if is_usd_mode() else "local currency"
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Billed",
            fmt_currency(total_billed),
            help=f"Total amount billed to customers ({currency_help})"
        )
    
    with col2:
        st.metric(
            "Revenue Collected",
            fmt_currency(total_revenue),
            help=f"Total revenue collected from customers ({currency_help})"
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
        occr = calculate_cost_recovery_ratio(total_revenue, total_opex)
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
            fmt_currency(total_opex),
            help=f"Total operational expenditure ({currency_help})"
        )
    
    with col6:
        surplus_deficit = total_revenue - total_opex
        st.metric(
            "Operating Surplus/Deficit",
            fmt_currency(surplus_deficit),
            delta_color="normal" if surplus_deficit >= 0 else "inverse",
            help=f"Revenue minus operating expenses ({currency_help})"
        )
    
    with col7:
        st.metric(
            "Uncollected Revenue",
            fmt_currency(uncollected),
            delta_color="inverse",
            help=f"Billed amount not yet collected ({currency_help})"
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
    fig = create_cost_recovery_dashboard(finance_df)
    show_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Financial Waterfall Charts
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
               [{'type': 'waterfall'}, {'type': 'waterfall'}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.12
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
        
        # Convert values based on currency mode - STANDARDIZED UNITS
        if is_usd_mode():
            # USD mode: Always show in Millions (M)
            billed_disp = convert_to_usd(billed, country) / 1e6
            uncollected_disp = convert_to_usd(uncollected, country) / 1e6
            opex_disp = convert_to_usd(opex, country) / 1e6
            surplus_disp = convert_to_usd(surplus, country) / 1e6
            symbol = "$"
            suffix = "M"
        else:
            # Local currency mode: Use Millions (M) for consistency
            billed_disp = billed / 1e6
            uncollected_disp = uncollected / 1e6
            opex_disp = opex / 1e6
            surplus_disp = surplus / 1e6
            symbol = CURRENCY_CONFIG.get(country, {}).get('symbol', 'LCU') + " "
            suffix = "M"
        
        fig.add_trace(
            go.Waterfall(
                name=country,
                orientation="v",
                measure=["relative", "relative", "relative", "total"],
                x=["Billed", "Uncollected", "OpEx", "Surplus"],
                y=[billed_disp, -uncollected_disp, -opex_disp, surplus_disp],
                connector={"line": {"color": "rgb(63, 63, 63)"}},
                decreasing={"marker": {"color": COLORS['poor']}},
                increasing={"marker": {"color": COLORS['good']}},
                totals={"marker": {"color": COLORS['primary'] if surplus >= 0 else COLORS['poor']}},
                text=[f"{symbol}{billed_disp:.1f}{suffix}", f"-{symbol}{uncollected_disp:.1f}{suffix}", f"-{symbol}{opex_disp:.1f}{suffix}", f"{symbol}{surplus_disp:.1f}{suffix}"],
                textposition="outside",
                textfont=dict(size=9)
            ),
            row=row,
            col=col
        )
    
    # Update subplot titles to prevent overlap
    fig.update_annotations(font=dict(size=13), yshift=15)
    
    # Improve layout spacing
    fig.update_layout(
        height=900,
        title_text="Financial Flow: Billed → Revenue → Operating Surplus/Deficit",
        showlegend=False,
        margin=dict(t=100, b=80, l=80, r=60)
    )
    
    show_chart(fig, use_container_width=True)
    
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
            yaxis_title='Amount (USD)' if is_usd_mode() else 'Amount (Local Currency)',
            xaxis_title='Date'
        )
        
        show_chart(fig, use_container_width=True)
    
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
        
        show_chart(fig, use_container_width=True)
    
    # OCCR and Collection Efficiency
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
            title='OCCR Performance',
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
        
        show_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            country_finance,
            x='country',
            y='collection_eff',
            title='Collection Efficiency',
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
        
        show_chart(fig, use_container_width=True)
    
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
            title='Average Staffing Levels',
            barmode='group',
            color_discrete_sequence=[COLORS['primary'], COLORS['secondary']],
            labels={'value': 'Average Staff Count', 'variable': 'Department'}
        )
        fig.update_layout(height=400)
        
        show_chart(fig, use_container_width=True)
    
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
            title='Operating Expenses per Staff Member (Annual)',
            color='country',
            color_discrete_map=COLORS['countries']
        )
        fig.update_layout(height=400, showlegend=False)
        fig.update_yaxes(title='OpEx per Staff (Annual, Local Currency)')
        
        show_chart(fig, use_container_width=True)
    
    # Financial Performance - Grouped Bar Chart
    st.subheader("Financial Performance Comparison")
    
    # Calculate key metrics by country
    performance_data = finance_df.groupby('country').agg({
        'sewer_revenue': 'sum',
        'opex': 'sum',
        'complaints': 'sum'
    }).reset_index()
    performance_data['occr'] = (performance_data['sewer_revenue'] / performance_data['opex']) * 100
    performance_data['surplus_pct'] = ((performance_data['sewer_revenue'] - performance_data['opex']) / performance_data['opex']) * 100
    
    # Create grouped bar showing OCCR and Surplus %
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='OCCR (%)',
        x=performance_data['country'],
        y=performance_data['occr'],
        marker_color=COLORS['primary'],
        text=performance_data['occr'].apply(lambda x: f'{x:.1f}%'),
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        name='Surplus/Deficit (%)',
        x=performance_data['country'],
        y=performance_data['surplus_pct'],
        marker_color=performance_data['surplus_pct'].apply(lambda x: COLORS['good'] if x >= 0 else COLORS['poor']),
        text=performance_data['surplus_pct'].apply(lambda x: f'{x:.1f}%'),
        textposition='outside'
    ))
    
    fig.add_hline(
        y=110,
        line_dash="dash",
        line_color="red",
        annotation_text="OCCR Target (110%)"
    )
    fig.add_hline(
        y=0,
        line_dash="solid",
        line_color="gray",
        annotation_text="Break-even"
    )
    
    fig.update_layout(
        title='Financial Performance: OCCR & Operating Surplus',
        height=450,
        barmode='group',
        xaxis_title='Country',
        yaxis_title='Percentage (%)',
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    
    show_chart(fig, use_container_width=True)
    
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
            
            show_chart(fig, use_container_width=True)
        
        # Zone comparison table
        st.subheader("Zone Performance Details")
        display_df = payment_by_zone.copy()
        
        # Format currency based on mode
        if is_usd_mode():
            # Need to convert each row based on its country
            def format_billed_usd(row):
                usd_val = convert_to_usd(row['total_billed'], row['country'])
                return f"${usd_val/1e6:.2f}M"
            def format_paid_usd(row):
                usd_val = convert_to_usd(row['total_paid'], row['country'])
                return f"${usd_val/1e6:.2f}M"
            display_df['total_billed'] = display_df.apply(format_billed_usd, axis=1)
            display_df['total_paid'] = display_df.apply(format_paid_usd, axis=1)
        else:
            display_df['total_billed'] = display_df.apply(
                lambda row: f"{row['total_billed']/1e9:.2f}B {CURRENCY_CONFIG.get(row['country'], {}).get('symbol', 'LCU')}", axis=1)
            display_df['total_paid'] = display_df.apply(
                lambda row: f"{row['total_paid']/1e9:.2f}B {CURRENCY_CONFIG.get(row['country'], {}).get('symbol', 'LCU')}", axis=1)
        display_df['collection_rate'] = display_df['collection_rate'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(
            display_df[['country', 'zone', 'customer_count', 'total_billed', 'total_paid', 'collection_rate']],
            use_container_width=True
        )
    else:
        st.info("ℹ️ Customer billing data not available for current filters. Try selecting different countries or clearing filters.")
    
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
                marker=dict(colors=[COLORS['poor'], COLORS['acceptable'], COLORS['good']]),
                textinfo='label+percent',
                textposition='outside',
                textfont=dict(size=11)
            )])
            
            fig.update_layout(
                title='Customer Distribution by Risk Category',
                height=450,
                paper_bgcolor=COLORS['bg_chart'],
                font={'color': COLORS['text_dark']},
                margin=dict(t=60, b=40, l=40, r=40)
            )
            
            show_chart(fig, use_container_width=True)
        
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
                labels={'unpaid_amount': 'Unpaid Amount (USD)' if is_usd_mode() else 'Unpaid Amount (Local)', 'risk_category': 'Risk Category'}
            )
            
            fig.update_layout(
                height=400,
                showlegend=False,
                paper_bgcolor=COLORS['bg_chart'],
                plot_bgcolor=COLORS['bg_chart'],
                font={'color': COLORS['text_dark']}
            )
            show_chart(fig, use_container_width=True)
        
        # Top Non-Payers
        st.subheader("🔴 Top Customers with Highest Unpaid Bills")
        top_unpaid = risk_customers.nlargest(10, 'unpaid_amount')
        
        fig = px.bar(
            top_unpaid,
            x='customer_id',
            y='unpaid_amount',
            color='zone',
            hover_data={'customer_id': True, 'country': True, 'zone': True, 'billed': ':.2f', 'paid': ':.2f', 'payment_ratio': ':.1%', 'unpaid_amount': ':.2f'},
            title='Top Customers by Unpaid Amount',
            labels={'unpaid_amount': 'Unpaid Amount (USD)' if is_usd_mode() else 'Unpaid Amount (Local)', 'customer_id': 'Customer ID'}
        )
        # Add customer ID as text on bars for better visibility
        fig.update_traces(texttemplate='ID: %{x}', textposition='outside', textfont_size=9)
        
        fig.update_layout(
            height=500,
            xaxis_title='Customer ID',
            yaxis_title='Unpaid Amount (USD)' if is_usd_mode() else 'Unpaid Amount (Local)',
            paper_bgcolor=COLORS['bg_chart'],
            plot_bgcolor=COLORS['bg_chart'],
            font={'color': COLORS['text_dark']}
        )
        
        show_chart(fig, use_container_width=True)
        
        # Actionable recommendations
        high_risk_unpaid = risk_customers[risk_customers['risk_category'] == 'High Risk']['unpaid_amount'].sum()
        top_zones = risk_customers[risk_customers['risk_category'] == 'High Risk'].groupby('zone').size().nlargest(3).index.tolist()
        
        # Format high risk unpaid based on currency mode
        if is_usd_mode() and selected_countries:
            high_risk_unpaid_fmt = format_usd(convert_to_usd(high_risk_unpaid, selected_countries[0]))
        else:
            high_risk_unpaid_fmt = fmt_currency(high_risk_unpaid)
        
        # Display summary metrics
        st.metric("High Risk Customers", f"{high_risk_count:,}")
        st.metric("Unpaid Amount (High Risk)", high_risk_unpaid_fmt)
        if top_zones:
            st.caption(f"Top Risk Zones: {', '.join(top_zones[:3])}")
    else:
        st.info("ℹ️ Customer billing data not available for current filters. Try selecting different countries or clearing filters.")
    
    # ============================================================================
    # SECTION E: COMMERCIAL VS. PHYSICAL NRW BREAKDOWN (NEW)
    # ============================================================================
    st.markdown("---")
    st.header("📊 Non-Revenue Water: Commercial vs. Physical Losses")
    st.markdown("Diagnose the root cause of NRW - infrastructure issues or revenue management")
    
    # Methodology note (per feedback about NRW discrepancy)
    with st.expander("ℹ️ **NRW Calculation Methodology**", expanded=False):
        st.markdown("""
        **This section uses customer-level billing data** to provide a detailed breakdown:
        - **Physical Losses**: Production volume minus billed consumption (leaks, theft, meter errors)
        - **Commercial Losses**: Billed but unpaid revenue converted to volume equivalent
        
        **Note**: The NRW shown in the Overview/Summary pages uses a different calculation:
        - Overview NRW = (Production - Metered Consumption) / Production
        - This breakdown uses billing data for more granular analysis
        
        Minor differences between pages are expected due to different data sources and aggregation levels.
        """)
    
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
            # Calculate currency value of commercial losses
            # Estimate average tariff from billing data
            total_billed_vol = billing_df['consumption_m3'].sum() if 'consumption_m3' in billing_df.columns else 0
            total_billed_amt = billing_df['billed'].sum() if 'billed' in billing_df.columns else 0
            avg_tariff = (total_billed_amt / total_billed_vol) if total_billed_vol > 0 else 0
            commercial_losses_currency = commercial_losses * avg_tariff
            
            # Format currency based on mode
            if is_usd_mode() and selected_countries:
                currency_val_display = format_usd(convert_to_usd(commercial_losses_currency, selected_countries[0]))
            else:
                currency_val_display = fmt_currency(commercial_losses_currency)
            
            st.metric(
                "Commercial Losses",
                currency_val_display,  # Currency as main value
                f"{commercial_losses/1e6:.2f}M m³ ({commercial_pct:.1f}%)",  # Volume as secondary
                delta_color="inverse",
                help="Revenue lost due to non-payment (amount billed but not collected)"
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
                textposition='outside',
                textfont=dict(size=11)
            )])
            
            fig.update_layout(
                title='NRW Breakdown: Physical vs. Commercial Losses',
                height=500,
                showlegend=True,
                paper_bgcolor=COLORS['bg_chart'],
                font={'color': COLORS['text_dark']},
                margin=dict(t=60, b=40, l=60, r=60)
            )
            
            show_chart(fig, use_container_width=True)
        
        with col_insights:
            st.subheader("NRW Summary")
            
            total_nrw_pct = physical_pct + commercial_pct
            benchmark = 25.0
            
            # Display factual metrics only
            st.metric("Physical Losses", f"{physical_pct:.1f}%")
            st.metric("Commercial Losses", f"{commercial_pct:.1f}%")
            st.metric("Total NRW", f"{total_nrw_pct:.1f}%", delta=f"Benchmark: ≤{benchmark}%")
            
            if physical_pct > commercial_pct:
                st.caption("🔧 Physical losses exceed commercial losses")
            else:
                st.caption("💰 Commercial losses exceed physical losses")
    else:
        st.info("ℹ️ NRW breakdown requires both billing and production data for selected filters.")
    
    # ============================================================================
    # SECTION F: AI-POWERED FINANCIAL INSIGHTS (MOVED TO END per feedback)
    # ============================================================================
    st.markdown("---")
    st.header("🔍 Financial Insights")
    
    # Prepare finance data for AI context
    occr = (total_revenue / total_opex * 100) if total_opex > 0 else 0
    finance_ai_data = {
        'occr': occr,
        'collection_efficiency': collection_eff,
        'total_revenue': total_revenue,
        'total_opex': total_opex,
        'surplus_deficit': total_revenue - total_opex,
        'uncollected': uncollected,
        'nrw_revenue_impact': (uncollected / total_billed * 100) if total_billed > 0 else 0
    }
    
    # Get country context
    country_context = countries_filter[0] if countries_filter and len(countries_filter) == 1 else None
    
    # AI insights are generated on demand so the tab renders instantly
    render_on_demand_insights(
        "🤖 AI-Powered Financial Analysis",
        lambda: generate_finance_insights(finance_ai_data, country_context),
        context_key=f"finance_{country_context}",
    )
    
    # Key metrics summary (factual data only, no projections)
    low_occr = country_finance[country_finance['occr'] < 110]
    
    st.subheader("📉 Countries Below OCCR Target")
    if len(low_occr) > 0:
        for _, row in low_occr.iterrows():
            status_color = "🔴" if row['occr'] < 80 else "🟡"
            st.markdown(f"{status_color} **{row['country']}**: {row['occr']:.1f}% OCCR")
    else:
        st.success("✅ All countries meeting OCCR benchmark")

