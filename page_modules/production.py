"""
Production Domain Page
Operational efficiency of water production
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.kpi_calculator import calculate_nrw
from utils.visualizations import create_trend_line, create_comparison_bar, create_waterfall_chart, COLORS


def render_production_page(data, countries_filter, date_range=None):
    """Render the production domain page"""
    
    st.title("🏭 Production Domain")
    st.markdown("### Operational Efficiency of Water Production")
    
    # Filter data
    production_df = data.get('production', pd.DataFrame()).copy()
    w_service_df = data.get('w_service', pd.DataFrame()).copy()
    finance_df = data.get('finance', pd.DataFrame()).copy()

    if countries_filter:
        production_df = production_df[production_df['country'].isin(countries_filter)]
        w_service_df = w_service_df[w_service_df['country'].isin(countries_filter)]
        finance_df = finance_df[finance_df['country'].isin(countries_filter)]

    if production_df.empty:
        st.warning("No production data available for the selected filters.")
        return
    
    st.markdown("---")
    
    # Key Metrics
    st.header("📊 Key Production Metrics")

    total_production_m3 = production_df['production_m3'].sum()
    total_production_million = total_production_m3 / 1_000_000
    avg_service_hours = production_df['service_hours'].mean()
    daily_totals = production_df.groupby('date')['production_m3'].sum()
    capacity_utilization = (daily_totals.mean() / daily_totals.max() * 100) if not daily_totals.empty and daily_totals.max() else 0
    total_opex = finance_df['opex'].sum() if not finance_df.empty else 0
    unit_cost = (total_opex / total_production_m3) if total_production_m3 else None
    unique_sources = production_df['source'].nunique()
    daily_avg = daily_totals.mean() if not daily_totals.empty else 0
    metered_total = w_service_df['metered'].sum() if not w_service_df.empty else 0
    nrw_pct = calculate_nrw(total_production_m3, metered_total) if total_production_m3 else 0

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Production",
            f"{total_production_million:.2f}M m³",
            help="Total water production volume across all sources"
        )
    
    with col2:
        delta = avg_service_hours - 20  # Benchmark is 20 hrs/day
        st.metric(
            "Avg Service Hours",
            f"{avg_service_hours:.1f} hrs/day",
            f"{delta:+.1f} hrs",
            delta_color="normal" if delta >= 0 else "inverse",
            help="Average hours of water supply per day"
        )
    
    with col3:
        st.metric(
            "Capacity Utilisation",
            f"{capacity_utilization:.1f}%",
            help="Average share of peak daily production achieved"
        )
    
    with col4:
        unit_cost_display = f"{unit_cost:,.2f} LCU/m³" if unit_cost else "N/A"
        st.metric(
            "Unit Production Cost",
            unit_cost_display,
            help="Operating expenditure per cubic metre produced (local currency units)"
        )

    col5, col6, col7 = st.columns(3)

    with col5:
        st.metric(
            "Water Sources",
            f"{unique_sources}",
            help="Number of unique water extraction sources"
        )
    
    with col6:
        st.metric(
            "Daily Avg Production",
            f"{daily_avg:,.0f} m³",
            help="Average daily production volume"
        )

    with col7:
        st.metric(
            "Non-Revenue Water",
            f"{nrw_pct:.1f}%",
            help="Estimated losses between production and metered consumption"
        )
    
    st.markdown("---")
    
    # Production Trends
    st.header("📈 Production Trends Over Time")
    
    # Daily production trend
    daily_prod = production_df.groupby('date').agg({
        'production_m3': 'sum'
    }).reset_index()
    
    # Validate data before visualization
    if daily_prod.empty or len(daily_prod) < 2:
        st.info("Insufficient data for daily production trend. Need at least 2 data points.")
    else:
        fig = px.line(
            daily_prod,
            x='date',
            y='production_m3',
            title='Daily Total Production Volume',
            labels={'production_m3': 'Production (m³)', 'date': 'Date'}
        )
        fig.update_traces(line_color=COLORS['primary'])
        fig.update_layout(height=400, hovermode='x unified')
        
        st.plotly_chart(fig, width='stretch')
    
    # Monthly trends by country
    production_df['month_year'] = production_df['date'].dt.to_period('M').astype(str)
    monthly_by_country = production_df.groupby(['month_year', 'country']).agg({
        'production_m3': 'sum'
    }).reset_index()
    
    fig = px.line(
        monthly_by_country,
        x='month_year',
        y='production_m3',
        color='country',
        title='Monthly Production by Country',
        labels={'production_m3': 'Production (m³)', 'month_year': 'Month'},
        color_discrete_map=COLORS['countries']
    )
    fig.update_layout(height=400, hovermode='x unified')
    fig.update_xaxes(tickangle=45)
    
    st.plotly_chart(fig, width='stretch')
    
    st.subheader("💧 Production vs Consumption vs Losses")
    if w_service_df.empty:
        st.info("Consumption and metering details are not available for the selected filters.")
    else:
        total_consumption = w_service_df['total_consumption'].sum()
        nrw_volume = max(total_production_m3 - metered_total, 0)
        categories = ["Total Production", "Metered Consumption", "Non-Revenue Water"]
        values = [
            total_production_m3 / 1_000_000,
            -metered_total / 1_000_000,
            -nrw_volume / 1_000_000
        ]
        waterfall_fig = create_waterfall_chart(
            categories,
            values,
            "Water Balance Overview",
            yaxis_title="Volume (million m³)"
        )
        st.plotly_chart(waterfall_fig, width='stretch')
        st.caption("Waterfall illustrates how much of the produced volume is metered and how much is lost as non-revenue water.")
    
    st.markdown("---")
    
    # Service Hours Analysis
    st.header("⏰ Service Hours Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Average service hours by country
        service_by_country = production_df.groupby('country').agg({
            'service_hours': 'mean'
        }).reset_index().sort_values('service_hours', ascending=True)
        
        fig = px.bar(
            service_by_country,
            x='service_hours',
            y='country',
            title='Average Service Hours by Country',
            orientation='h',
            color='country',
            color_discrete_map=COLORS['countries']
        )
        fig.add_vline(
            x=20,
            line_dash="dash",
            line_color="red",
            annotation_text="Benchmark: 20 hrs/day"
        )
        fig.update_layout(height=400, showlegend=False)
        
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        # Service hours distribution
        fig = px.histogram(
            production_df,
            x='service_hours',
            nbins=30,
            title='Service Hours Distribution',
            labels={'service_hours': 'Service Hours (hrs/day)', 'count': 'Frequency'},
            color_discrete_sequence=[COLORS['primary']]
        )
        fig.add_vline(
            x=20,
            line_dash="dash",
            line_color="red",
            annotation_text="Benchmark"
        )
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, width='stretch')
    
    st.markdown("---")
    
    # Source Analysis
    st.header("💧 Water Source Analysis")
    
    # Production by source
    prod_by_source = production_df.groupby('source').agg({
        'production_m3': 'sum',
        'service_hours': 'mean'
    }).reset_index().sort_values('production_m3', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 sources by production
        top_sources = prod_by_source.head(10)
        
        fig = px.bar(
            top_sources,
            x='production_m3',
            y='source',
            title='Top 10 Water Sources by Production Volume',
            orientation='h',
            color='production_m3',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400, showlegend=False)
        
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        # Service hours by source (top 10)
        fig = px.bar(
            top_sources,
            x='service_hours',
            y='source',
            title='Average Service Hours by Top Sources',
            orientation='h',
            color='service_hours',
            color_continuous_scale='Greens'
        )
        fig.add_vline(
            x=20,
            line_dash="dash",
            line_color="red",
            annotation_text="Benchmark"
        )
        fig.update_layout(height=400, showlegend=False)
        
        st.plotly_chart(fig, width='stretch')
    
    # Production source breakdown by country
    st.subheader("Production Distribution by Source and Country")
    
    source_country = production_df.groupby(['country', 'source']).agg({
        'production_m3': 'sum'
    }).reset_index()
    
    # Get top 5 sources per country
    top_sources_per_country = source_country.groupby('country').apply(
        lambda x: x.nlargest(5, 'production_m3')
    ).reset_index(drop=True)
    
    fig = px.sunburst(
        top_sources_per_country,
        path=['country', 'source'],
        values='production_m3',
        title='Production Volume by Country and Source (Top 5 per Country)',
        color='production_m3',
        color_continuous_scale='Blues'
    )
    fig.update_layout(height=600)
    
    st.plotly_chart(fig, width='stretch')
    
    st.markdown("---")
    
    # Diagnostic Insights
    st.header("🔍 Diagnostic Insights")
    
    # Identify sources with low service hours
    low_service_sources = prod_by_source[prod_by_source['service_hours'] < 20]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ Sources Below Benchmark")
        if len(low_service_sources) > 0:
            st.warning(f"""
            **{len(low_service_sources)} sources** are operating below the 20 hrs/day benchmark:
            
            - **Average service hours**: {low_service_sources['service_hours'].mean():.1f} hrs/day
            - **Total affected production**: {low_service_sources['production_m3'].sum() / 1_000_000:.2f}M m³
            
            **Recommendation**: Investigate infrastructure issues, power supply, or maintenance schedules 
            for these sources to improve service continuity.
            """)
            
            # Show table of problematic sources
            st.dataframe(
                low_service_sources[['source', 'service_hours', 'production_m3']].head(10),
                width='stretch'
            )
        else:
            st.success("✅ All sources are meeting or exceeding the service hours benchmark!")
    
    with col2:
        st.subheader("📊 Production Efficiency")
        
        # Calculate production per service hour
        prod_by_source['efficiency'] = prod_by_source['production_m3'] / prod_by_source['service_hours']
        top_efficient = prod_by_source.nlargest(5, 'efficiency')
        
        st.info(f"""
        **Most Efficient Sources** (m³ per service hour):
        
        {chr(10).join([f"- **{row['source']}**: {row['efficiency']:,.0f} m³/hr" 
                       for _, row in top_efficient.iterrows()])}
        
        **Insight**: These sources demonstrate high production capacity relative to operating time. 
        Consider replicating their operational practices at lower-performing sources.
        """)
    
    if not finance_df.empty:
        st.subheader("💸 Production Cost Hotspots")
        cost_by_country = finance_df.groupby('country')['opex'].sum()
        production_by_country = production_df.groupby('country')['production_m3'].sum()
        unit_cost_by_country = (cost_by_country / production_by_country.replace({0: np.nan})).dropna().reset_index(name='unit_cost')
        
        if not unit_cost_by_country.empty:
            high_cost = unit_cost_by_country.sort_values('unit_cost', ascending=False).head(5)
            st.warning(f"""
            **{len(high_cost)} countries/utilities** record the highest unit production costs:
            
            {chr(10).join([f"- **{row['country']}**: {row['unit_cost']:,.2f} LCU/m³" for _, row in high_cost.iterrows()])}
            
            **Recommendation:** Investigate high energy spend, chemical usage, and staffing levels. 
            Prioritise energy efficiency and process optimisation programmes in these utilities.
            """)
        else:
            st.info("Unit production cost could not be calculated for the selected filters.")
    
    # Seasonal patterns
    if len(production_df) > 0:
        production_df['month'] = production_df['date'].dt.month
        monthly_pattern = production_df.groupby('month').agg({
            'production_m3': 'mean'
        }).reset_index()
        
        st.subheader("🌦️ Seasonal Production Patterns")
        
        fig = px.line(
            monthly_pattern,
            x='month',
            y='production_m3',
            title='Average Production by Month',
            labels={'month': 'Month', 'production_m3': 'Avg Production (m³)'},
            markers=True
        )
        fig.update_traces(line_color=COLORS['good'])
        fig.update_layout(height=350)
        fig.update_xaxes(tickmode='linear', tick0=1, dtick=1)
        
        st.plotly_chart(fig, width='stretch')
        
        # Safe idxmax/idxmin with empty check
        if not monthly_pattern.empty and len(monthly_pattern) > 0:
            try:
                peak_month = monthly_pattern.loc[monthly_pattern['production_m3'].idxmax(), 'month']
                low_month = monthly_pattern.loc[monthly_pattern['production_m3'].idxmin(), 'month']
                
                st.info(f"""
                **Peak Production Month**: Month {int(peak_month)}  
                **Lowest Production Month**: Month {int(low_month)}
                
                Consider seasonal demand patterns and plan maintenance during low-demand periods.
                """)
            except (ValueError, KeyError):
                st.info("Insufficient data to identify peak and low production months.")

