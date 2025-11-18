"""
Landing Page / Home Page
Entry point with navigation cards and summary KPIs
"""

import streamlit as st
import plotly.graph_objects as go
from utils.data_loader import load_all_data, get_latest_update_date
from utils.kpi_calculator import calculate_summary_kpis
from utils.visualizations import COLORS


def render_home_page(data, countries_filter, date_range=None):
    """Render the home/landing page"""
    
    st.title("🌊 Multi-Country Water Services Performance Dashboard")
    
    # Mission statement
    st.markdown("""
    ### Empowering Utility Managers Across Africa
    
    This dashboard provides actionable insights for water and sanitation service providers in 
    **Uganda**, **Cameroon**, **Lesotho**, and **Malawi**. Make data-driven decisions to improve 
    operational efficiency, financial sustainability, service quality, and equitable access.
    """)
    
    st.markdown("---")
    
    # Summary KPIs
    st.header("📊 Key Performance Indicators")
    
    kpis = calculate_summary_kpis(data)

    if not kpis:
        st.warning("No data available for the selected filters. Please adjust your filters to view KPIs.")
        return

    kpi_layout = [
        ('water_coverage', "💧 Water Coverage"),
        ('sanitation_coverage', "🚽 Sanitation Coverage"),
        ('nrw', "💸 Non-Revenue Water"),
        ('water_quality', "🔬 Water Quality"),
        ('service_hours', "⏰ Hours of Supply"),
        ('collection_efficiency', "💵 Revenue Collection Efficiency"),
        ('occr', "📈 O&M Cost Coverage (OCCR)"),
        ('personnel_cost_ratio', "👥 Personnel Cost Share"),
        ('metering_ratio', "📊 Metering Ratio"),
        ('staff_productivity', "🧑‍🔧 Staff Productivity"),
    ]

    row_cols = None
    for idx, (key, title) in enumerate(kpi_layout):
        if key not in kpis:
            continue

        if idx % 5 == 0:
            row_cols = st.columns(5)

        metric = kpis[key]
        inverse = metric.get('inverse', False)
        status, color = get_status(metric['value'], metric['benchmark'], inverse=inverse)
        value_label = format_metric_value(metric)
        target_label = format_metric_target(key, metric)

        with row_cols[idx % 5]:
            render_kpi_card(
                title,
                value_label,
                target_label,
                color
            )
    
    st.markdown("---")
    
    # Navigation Cards
    st.header("🧭 Navigate to Domain")
    st.markdown("Select a domain below to explore detailed insights:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_nav_card(
            "📊 Overview Dashboard",
            "High-level KPI scorecard with trends and benchmarks",
            "overview",
            "🔍 View Overview"
        )
        
        render_nav_card(
            "🏭 Production Domain",
            "Operational efficiency of water production",
            "production",
            "⚙️ View Production"
        )
    
    with col2:
        render_nav_card(
            "🚰 Service Domain",
            "Service quality and reliability metrics",
            "service",
            "🔧 View Service"
        )
        
        render_nav_card(
            "🌍 Access Domain",
            "Access & equity analysis (urban vs rural)",
            "access",
            "🗺️ View Access"
        )
    
    with col3:
        render_nav_card(
            "💰 Finance Domain",
            "Financial sustainability and cost recovery",
            "finance",
            "💵 View Finance"
        )
        
        render_nav_card(
            "📊 Reports",
            "Actionable recommendations and exports",
            "reports",
            "📄 View Reports"
        )
    
    st.markdown("---")
    
    # How to Use Guide
    with st.expander("📖 How to Use This Dashboard"):
        st.markdown("""
        ### Getting Started
        
        1. **Filter Data**: Use the sidebar to select countries and date ranges
        2. **Navigate**: Click on domain cards above or use the sidebar menu
        3. **Explore Visuals**: Hover over charts for detailed information
        4. **Export Data**: Visit the Reports page to download insights
        
        ### Dashboard Domains
        
        - **Overview**: Comprehensive KPI scorecard with sector benchmarks
        - **Production**: Analyze water production volumes, service hours, and capacity
        - **Service**: Monitor water quality, complaints, and service reliability
        - **Access**: Track JMP service ladder coverage and equity gaps
        - **Finance**: Evaluate OCCR, revenue collection, and cost recovery
        - **Reports**: Generate action plans and export data
        
        ### Key Performance Indicators
        
        - **Water Coverage**: % population with safely managed or basic water access (Target: 100%)
        - **Sanitation Coverage**: % population with safely managed or basic sanitation (Target: 100%)
        - **NRW**: Non-Revenue Water as % of production (Benchmark: ≤25%)
        - **OCCR**: Operating Cost Coverage Ratio (Benchmark: ≥110%)
        - **Collection Efficiency**: Revenue collected vs billed (Benchmark: ≥95%)
        - **Water Quality**: % tests passed for drinking water compliance (Benchmark: ≥95%)
        - **Metering Ratio**: % consumption recorded through meters (Benchmark: ≥95%)
        - **Service Hours**: Average hours of water supply per day (Benchmark: ≥20 hrs)
        
        ### Data Sources
        
        This dashboard integrates data from:
        - Daily production records
        - Monthly service delivery data
        - Annual access statistics (JMP ladder)
        - Financial and operational expenditure
        - National accounts and regulatory data
        
        **Last Updated**: {update_date}
        """.format(update_date=get_latest_update_date()))
    
    # Footer
    st.markdown("---")
    st.caption(f"📅 Data Last Updated: {get_latest_update_date()} | 🔄 Dashboard refreshes every hour")


def render_kpi_card(title, value, target, color):
    """Render a KPI metric card"""
    st.markdown(f"""
    <div style="
        background-color: {color}20;
        border-left: 5px solid {color};
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
    ">
        <p style="margin: 0; font-size: 12px; color: #666;">{title}</p>
        <p style="margin: 5px 0; font-size: 28px; font-weight: bold; color: {color};">{value}</p>
        <p style="margin: 0; font-size: 11px; color: #888;">{target}</p>
    </div>
    """, unsafe_allow_html=True)


def render_nav_card(title, description, page_key, button_text):
    """Render a navigation card"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        color: white;
    ">
        <h3 style="margin: 0 0 10px 0; color: white;">{title}</h3>
        <p style="margin: 0; font-size: 14px; opacity: 0.9;">{description}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(button_text, key=f"nav_{page_key}", width='stretch'):
        st.session_state.current_page = page_key
        st.rerun()


def get_status(value, benchmark, inverse=False):
    """Get status color based on value and benchmark"""
    if inverse:
        if value <= benchmark:
            return 'good', COLORS['good']
        elif value <= benchmark * 1.5:
            return 'acceptable', COLORS['acceptable']
        else:
            return 'poor', COLORS['poor']
    else:
        if value >= benchmark:
            return 'good', COLORS['good']
        elif value >= benchmark * 0.8:
            return 'acceptable', COLORS['acceptable']
        else:
            return 'poor', COLORS['poor']


def format_metric_value(metric):
    """Format metric value with appropriate unit."""
    value = metric.get('value', 0)
    unit = metric.get('unit', '').strip()

    if unit == '%':
        return f"{value:.1f}%"
    if unit.lower() in {'hrs/day', 'hours/day'}:
        return f"{value:.1f} hrs/day"
    if unit == 'staff/1k':
        return f"{value:.1f} staff/1k"
    if unit:
        return f"{value:.1f} {unit}"
    return f"{value:.1f}"


def format_metric_target(metric_key, metric):
    """Create human-readable target label for KPI cards."""
    benchmark = metric.get('benchmark', 0)
    unit = metric.get('unit', '').strip()

    if metric_key in {'water_coverage', 'sanitation_coverage'}:
        return f"Target: {benchmark}{unit}"
    if metric_key in {'nrw', 'personnel_cost_ratio'}:
        return f"Benchmark: ≤{benchmark}{unit}"
    if metric_key == 'staff_productivity':
        return f"Benchmark: ≤{benchmark} staff/1k"
    if metric_key == 'service_hours':
        return f"Target: ≥{benchmark} hrs/day"
    if unit.lower() in {'hrs/day', 'hours/day'}:
        return f"Target: ≥{benchmark} {unit}"
    if unit:
        return f"Target: ≥{benchmark}{unit}"
    return f"Target: ≥{benchmark}"

