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
    """Render the home/landing page with country selection cards"""
    
    st.title("🌊 Multi-Country Water Services Performance Dashboard")
    
    # Mission statement
    st.markdown("""
    ### Empowering Utility Managers Across Africa
    
    This dashboard provides actionable insights for water and sanitation service providers in 
    **Uganda**, **Cameroon**, **Lesotho**, and **Malawi**. Make data-driven decisions to improve 
    operational efficiency, financial sustainability, service quality, and equitable access.
    """)
    
    st.markdown("---")
    
    # Country Selection Section
    st.header("🌍 Select a Country to Explore")
    st.markdown("Choose a country below to view its comprehensive water services dashboard:")
    
    # Country configuration with flag emojis and descriptions
    countries_config = [
        {
            'name': 'Uganda',
            'emoji': '🇺🇬',
            'description': 'National Water and Sewerage Corporation (NWSC)',
            'zones': 'Central, Kawempe, Nakawa, Rubaga',
            'color': '#FFD700'
        },
        {
            'name': 'Malawi',
            'emoji': '🇲🇼',
            'description': 'Lilongwe Water Board (LWB)',
            'zones': 'Capital Hill, Kanengo, Lumbadzi, Old Town',
            'color': '#FF6347'
        },
        {
            'name': 'Lesotho',
            'emoji': '🇱🇸',
            'description': 'Water and Sewerage Company (WASCO)',
            'zones': 'Maseru Urban, Maseru Rural, Rural Hinterland',
            'color': '#4682B4'
        },
        {
            'name': 'Cameroon',
            'emoji': '🇨🇲',
            'description': 'Camerounaise Des Eaux (CDE)',
            'zones': 'Yaounde 1-7',
            'color': '#32CD32'
        }
    ]
    
    # Display country cards in 2x2 grid
    col1, col2 = st.columns(2)
    
    for idx, country_info in enumerate(countries_config):
        col = col1 if idx % 2 == 0 else col2
        
        with col:
            render_country_card(
                country_info['name'],
                country_info['emoji'],
                country_info['description'],
                country_info['zones'],
                country_info['color']
            )
    
    st.markdown("---")
    
    # Overall Statistics Summary
    st.header("📊 Multi-Country Overview")
    st.markdown("Key performance indicators across all four countries:")
    
    kpis = calculate_summary_kpis(data)

    if not kpis:
        st.warning("No data available. Please check data files.")
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

    # --- START OF CORRECTED BLOCK ---
    
    # Initialize row_cols to an empty list.
    row_cols = [] 

    for idx, (key, title) in enumerate(kpi_layout):
        if key not in kpis:
            continue

        col_index = idx % 5 

        # If it's the start of a new row (index 0, 5, 10, etc.), create 5 columns.
        if col_index == 0:
            # This is the ONLY place where row_cols is assigned st.columns(5)
            # This ensures that row_cols is a list of 5 elements before it's used.
            row_cols = st.columns(5)
            
        # The list row_cols is now guaranteed to hold 5 columns if we continue.
        # Check to prevent an IndexError if kpis somehow had fewer than 5 items
        # AND was missing keys that should have been skipped (a very unlikely edge case).
        if col_index >= len(row_cols):
             continue

        metric = kpis[key]
        inverse = metric.get('inverse', False)
        status, color = get_status(metric['value'], metric['benchmark'], inverse=inverse)
        value_label = format_metric_value(metric)
        target_label = format_metric_target(key, metric)

        # Access the column safely using the index (0 to 4)
        with row_cols[col_index]: 
            render_kpi_card(
                title,
                value_label,
                target_label,
                color
            )
    # --- END OF CORRECTED BLOCK ---
    
    st.markdown("---")
    
    # How to Use Guide
    with st.expander("📖 How to Use This Dashboard"):
        st.markdown("""
        ### Getting Started
        
        1. **Select a Country**: Click "View Dashboard" on any country card above
        2. **Explore Domains**: Use tabs to navigate between Overview, Production, Service, Access, and Finance
        3. **Filter by Zone**: Use the sidebar to select specific zones within the country
        4. **Adjust Date Range**: Filter data by selecting a date range in the sidebar
        5. **Generate Reports**: Click the "Generate Reports" button in the sidebar for actionable insights
        
        ### Dashboard Domains
        
        - **Overview**: Comprehensive KPI scorecard with sector benchmarks
        - **Production**: Analyze water production volumes, service hours, and capacity
        - **Service**: Monitor water quality, complaints, and service reliability
        - **Access**: Track JMP service ladder coverage and equity gaps
        - **Finance**: Evaluate OCCR, revenue collection, and cost recovery
        
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


def render_country_card(country_name, emoji, description, zones, color):
    """Render a country selection card with View Dashboard button"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color}20 0%, {color}40 100%);
        border-left: 5px solid {color};
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <h2 style="margin: 0 0 10px 0; color: #1e1e1e; font-size: 32px;">{emoji} {country_name}</h2>
        <p style="margin: 0 0 10px 0; font-size: 16px; color: #333; font-weight: 500;">{description}</p>
        <p style="margin: 0; font-size: 13px; color: #666;"><strong>Zones:</strong> {zones}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(f"🔍 View {country_name} Dashboard", key=f"country_{country_name}", use_container_width=True):
        st.session_state.selected_country = country_name
        st.rerun()


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
    """Render a navigation card (deprecated in new flow but kept for compatibility)"""
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
    
    if st.button(button_text, key=f"nav_{page_key}", use_container_width=True):
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