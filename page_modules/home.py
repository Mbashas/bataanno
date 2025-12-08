"""
Landing Page / Home Page
Entry point with navigation cards and summary KPIs
Redesigned with modern UI and custom branding
"""

import streamlit as st
import pandas as pd # Needed for the multi-country KPI comparison table
import numpy as np # Needed for checking NaN in table utilities
import plotly.graph_objects as go
from utils.data_loader import load_all_data, get_latest_update_date
# NOTE: You MUST have a function like this in utils/kpi_calculator.py
# If not, the multi-country table will fail to find 'calculate_all_country_kpis'
from utils.kpi_calculator import calculate_summary_kpis, calculate_all_country_kpis 
from utils.visualizations import COLORS
from utils.theme import get_theme, BRAND, LIGHT_THEME
from assets.logo_svg import get_wash_logo_colored_svg


# --- New Utility Functions for Table Formatting ---

def format_kpi_value(value, unit=''):
    """Utility function to safely format KPI values for the table"""
    if pd.isna(value) or value is None:
        return "N/A"
    
    # Check for NaN and return "N/A" first
    if np.isnan(value):
        return "N/A"
        
    if unit == '%':
        return f"{value:.1f}%"
    elif unit.lower() in ('hrs/day', 'days'):
        return f"{value:.1f} {unit}"
    else:
        # Standard large number formatting
        return f"{value:,.0f}"

def get_status_icon(value, benchmark, inverse=False):
    """Get status icon based on value, benchmark, and direction (inverse)"""
    if pd.isna(value) or value is None or np.isnan(value):
        return "⚪"
    
    # Calculate difference
    delta = value - benchmark
    
    # Define "good" direction
    is_good = (delta >= 0 and not inverse) or (delta <= 0 and inverse)
    
    # Define "close" (e.g., within 10% of benchmark)
    try:
        is_close = abs(delta) < (0.10 * abs(benchmark))
    except (ZeroDivisionError, TypeError):
        # Handle benchmark being 0 or non-numeric
        is_close = False 

    if is_good:
        return '✅' # Meeting or Exceeding Target
    elif is_close:
        return '⚠️' # Close to Target, Needs Attention
    else:
        return '❌' # Needs significant improvement

# --- END Utility Functions ---


def render_home_page(data, countries_filter, date_range=None):
    """Render the home/landing page with country selection cards"""
    theme = get_theme()
    
    # Clean page header with styled logo box (UNCHANGED)
    st.markdown(f"""
    <div style="margin-bottom: 40px; display: flex; align-items: center; gap: 20px;">
        <div style="
            width: 56px;
            height: 56px;
            background: linear-gradient(135deg, #58A0C8 0%, #34699A 50%, #113F67 100%);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(17, 63, 103, 0.25);
            flex-shrink: 0;
        ">
            <span style="font-size: 28px; filter: drop-shadow(0 2px 2px rgba(0,0,0,0.15));">💧</span>
        </div>
        <div>
            <h1 style="
                font-size: 2rem; 
                font-weight: 700; 
                color: {theme['text_primary']}; 
                margin: 0 0 4px 0;
                line-height: 1.2;
            ">
                WASH Performance Dashboard
            </h1>
            <p style="
                font-size: 0.95rem; 
                color: {theme['text_secondary']}; 
                margin: 0;
            ">
                Multi-country water services analytics for Uganda, Cameroon, Lesotho, and Malawi
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Country Selection Section (UNCHANGED)
    st.markdown(f"""
    <div style="
        margin-bottom: 24px; 
        padding: 16px 20px; 
        background: linear-gradient(135deg, rgba(17, 63, 103, 0.03) 0%, rgba(88, 160, 200, 0.05) 100%);
        border-radius: 12px;
        border-left: 4px solid #113F67;
    ">
        <h2 style="
            font-size: 1.25rem; 
            font-weight: 700; 
            color: {theme['text_primary']}; 
            margin: 0 0 4px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        ">
            <span>🌍</span> Select a Country
        </h2>
        <p style="color: {theme['text_secondary']}; margin: 0; font-size: 14px;">
            Choose a country below to explore detailed analytics and performance metrics
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Country configuration (UNCHANGED)
    countries_config = [
        {
            'name': 'Uganda',
            'emoji': '🇺🇬',
            'description': 'National Water and Sewerage Corporation (NWSC)',
            'zones': 'Central, Kawempe, Nakawa, Rubaga',
            'color': theme['countries']['Uganda'],
            'is_hero': True 
        },
        {
            'name': 'Malawi',
            'emoji': '🇲🇼',
            'description': 'Lilongwe Water Board (LWB)',
            'zones': 'Capital Hill, Kanengo, Lumbadzi, Old Town',
            'color': theme['countries']['Malawi'],
            'is_hero': False
        },
        {
            'name': 'Lesotho',
            'emoji': '🇱🇸',
            'description': 'Water and Sewerage Company (WASCO)',
            'zones': 'Maseru Urban, Maseru Rural, Rural Hinterland',
            'color': theme['countries']['Lesotho'],
            'is_hero': False
        },
        {
            'name': 'Cameroon',
            'emoji': '🇨🇲',
            'description': 'Camerounaise Des Eaux (CDE)',
            'zones': 'Yaounde 1-7',
            'color': theme['countries']['Cameroon'],
            'is_hero': False
        }
    ]
    
    # 💥 FIX 1: Change to 2x2 Grid Layout and remove hero logic
    cols = st.columns(2)
    
    for i, country_info in enumerate(countries_config):
        col = cols[i % 2] # 0, 1, 0, 1
        
        with col:
            # All cards rendered as non-hero to maintain uniform height in 2x2 grid
            render_country_card_new(
                country_info['name'],
                country_info['emoji'],
                country_info['description'],
                country_info['zones'],
                country_info['color'],
                is_hero=False, 
                theme=theme
            )
    
    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
    
    # Overall Statistics Summary
    st.markdown("---")
    st.header("📊 Multi-Country Overview")
    st.markdown("Comparison of key performance indicators (KPIs) across all countries.")

    # 💥 FIX 2: Replace aggregated KPI cards with the multi-country comparison table 💥
    
    try:
        # Load KPIs for all countries
        all_country_kpis = calculate_all_country_kpis(data)
    except NameError:
        st.error("Error: `calculate_all_country_kpis` not found. Ensure it is defined and imported from `utils.kpi_calculator.py`.")
        return

    # 1. Define the Key KPIs to compare 
    comparison_kpis_config = [
        ('collection_efficiency', 'Revenue Collection Efficiency', '%', 95, False),
        ('nrw', 'Non-Revenue Water (NRW)', '%', 25, True), # Inverse: lower is better
        ('occr', 'O&M Cost Recovery Ratio', '%', 110, False), # Changed to use 'occr' key from original code
        ('water_coverage', 'Water Service Coverage', '%', 100, False), # Changed to use 'water_coverage' key
        ('service_hours', 'Service Continuity', 'hrs/day', 20, False), # Changed to use 'service_hours' key
        ('water_quality', 'Water Quality Test Pass Rate', '%', 95, False), # Added a new KPI for comparison
    ]
    
    # 2. Build the data structure
    kpi_data = {}
    for country, kpi_dict in all_country_kpis.items():
        kpi_data[country] = {}
        for kpi_key, kpi_title, unit, benchmark, inverse in comparison_kpis_config:
            
            # Safely extract the KPI object
            metric = kpi_dict.get(kpi_key) 
            value = None
            if isinstance(metric, dict):
                # Expected format: {'value': 25.5, ...}
                value = metric.get('value')
            elif isinstance(metric, (float, int, np.float64, np.int64)):
                # Error format: metric is the raw value
                value = metric
            
            if value is not None:
                # Get icon and format value
                status_icon = get_status_icon(value, benchmark, inverse)
                formatted_value = format_kpi_value(value, unit)
                kpi_data[country][kpi_title] = f"{status_icon} {formatted_value}"
            else:
                kpi_data[country][kpi_title] = "N/A"
    
    # 3. Create DataFrame and display
    if kpi_data:
        df_kpis = pd.DataFrame(kpi_data).T.fillna('N/A')
        
        # Prepare column tooltips from config
        column_configs = {
            col_title: st.column_config.Column(
                col_title,
                help=f"Target: {benchmark}{unit} ({'Lower is Better' if inverse else 'Higher is Better'})",
                width="small"
            ) for kpi_key, col_title, unit, benchmark, inverse in comparison_kpis_config
        }
        
        st.dataframe(
            df_kpis, 
            use_container_width=True,
            column_config=column_configs
        )
        
        st.markdown("""
        <p style='font-size: 12px; color: var(--text-secondary); margin-top: 10px;'>
        <span style='font-size: 14px;'>✅</span>: Meeting Target | 
        <span style='font-size: 14px;'>⚠️</span>: Near Target | 
        <span style='font-size: 14px;'>❌</span>: Needs Improvement |
        <span style='font-size: 14px;'>⚪</span>: Data Not Available
        </p>
        """, unsafe_allow_html=True)
    
    # Original aggregated KPI card section is removed to avoid redundancy and layout conflicts.

    st.markdown("---")
    
    # How to Use Guide (UNCHANGED)
    with st.expander("📖 Quick Start Guide"):
        st.markdown("""
        **Getting Started**
        1. Select a country card above to view its dashboard
        2. Use tabs to explore different domains (Production, Service, Access, Finance)
        3. Filter by zone and date range using the sidebar
        4. Generate reports for actionable insights
        
        **Key Indicators**
        - **Water/Sanitation Coverage**: % population with managed access (Target: 100%)
        - **NRW**: Non-Revenue Water (Benchmark: ≤25%)
        - **OCCR**: Operating Cost Coverage Ratio (Benchmark: ≥110%)
        - **Collection Efficiency**: Revenue vs billed (Benchmark: ≥95%)
        - **Water Quality**: Tests passed (Benchmark: ≥95%)
        - **Service Hours**: Hours of supply (Benchmark: ≥20 hrs/day)
        
        **Data Updated**: {update_date}
        """.format(update_date=get_latest_update_date()))
    
    # Footer (UNCHANGED)
    st.markdown("---")
    st.caption(f"📅 Data Last Updated: {get_latest_update_date()} | 🔄 Dashboard refreshes every hour")


def render_country_card(country_name, emoji, description, zones, color):
    """Render a country selection card with View Dashboard button (legacy)"""
    theme = get_theme()
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color}20 0%, {color}40 100%);
        border-left: 5px solid {color};
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <h2 style="margin: 0 0 10px 0; color: {theme['text_primary']}; font-size: 32px;">{emoji} {country_name}</h2>
        <p style="margin: 0 0 10px 0; font-size: 16px; color: {theme['text_secondary']}; font-weight: 500;">{description}</p>
        <p style="margin: 0; font-size: 13px; color: {theme['text_muted']};"><strong>Zones:</strong> {zones}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(f"🔍 View {country_name} Dashboard", key=f"country_{country_name}", use_container_width=True):
        st.session_state.selected_country = country_name
        st.rerun()


def render_country_card_new(country_name, emoji, description, zones, color, is_hero=False, theme=None):
    """Render a modern country selection card with clean styling - FIX APPLIED HERE"""
    if theme is None:
        theme = get_theme()
    
    # Card styling based on hero status
    if is_hero:
        # Hero card container - FIX: Use existing theme variables for border and shadow
        st.markdown(f"""
        <div style="
            /* FIX: Use theme variables for light/dark mode adaptability */
            background: {theme['bg_card']}; /* Replaces linear-gradient(135deg, #FFFFFF 0%, #F8FAFF 100%); */
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 16px;
            /* **FIX:** Replaced 'border_color' with existing 'border' key */
            border: 1px solid {theme['border']}; 
            border-left: 5px solid {color};
            /* Using existing 'shadow_lg' for the hero card */
            box-shadow: {theme['shadow_lg']}; 
        ">
            <div style="display: flex; align-items: flex-start; gap: 20px;">
                <div style="font-size: 56px; line-height: 1;">{emoji}</div>
                <div style="flex: 1;">
                    <h3 style="color: {theme['text_primary']}; margin: 0 0 8px 0; font-size: 1.5rem; font-weight: 700;">{country_name}</h3>
                    <p style="color: {theme['text_secondary']}; margin: 0 0 8px 0; font-size: 14px;">{description}</p>
                    <p style="color: {theme['text_muted']}; margin: 0; font-size: 12px;">📍 <strong>Zones:</strong> {zones}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 Explore Dashboard", key=f"country_{country_name}_new", use_container_width=True, type="primary"):
            st.session_state.selected_country = country_name
            st.rerun()
    else:
        # Regular card (compact) - FIX: Use existing theme variables for border and shadow
        st.markdown(f"""
        <div style="
            /* FIX APPLIED HERE: Use theme variables for background, border, and shadow */
            background: {theme['bg_card']}; /* Replaces #FFFFFF */
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 12px;
            /* **FIX:** Replaced 'border_color' with existing 'border' key */
            border: 1px solid {theme['border']}; 
            border-left: 4px solid {color};
            /* Using existing 'shadow' key */
            box-shadow: {theme['shadow']}; 
            transition: all 0.2s ease;
        ">
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="font-size: 32px; line-height: 1;">{emoji}</div>
                <div style="flex: 1;">
                    <h4 style="color: {theme['text_primary']}; margin: 0; font-size: 1.1rem; font-weight: 700;">{country_name}</h4>
                    <p style="color: {theme['text_secondary']}; margin: 2px 0 0 0; font-size: 12px;">{description}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"→ View {country_name}", key=f"country_{country_name}_new", use_container_width=True):
            st.session_state.selected_country = country_name
            st.rerun()

def render_kpi_card(title, value, target, color):
    """Render a KPI metric card"""
    theme = get_theme()
    st.markdown(f"""
    <div style="
        background-color: {theme['bg_card']};
        border-left: 4px solid {color};
        padding: 16px 20px;
        border-radius: 12px;
        margin-bottom: 12px;
        box-shadow: {theme['shadow']};
    ">
        <p style="margin: 0; font-size: 12px; color: {theme['text_muted']}; font-weight: 500;">{title}</p>
        <p style="margin: 6px 0; font-size: 28px; font-weight: 700; color: {color};">{value}</p>
        <p style="margin: 0; font-size: 11px; color: {theme['text_secondary']};">{target}</p>
    </div>
    """, unsafe_allow_html=True)


def render_nav_card(title, description, page_key, button_text):
    """Render a navigation card (deprecated in new flow but kept for compatibility)"""
    theme = get_theme()
    st.markdown(f"""
    <div style="
        /* FIX: Use theme variables for light/dark mode adaptability */
        background: linear-gradient(135deg, {theme['bg_dark']} 0%, {theme['bg_secondary']} 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        color: {theme['text_primary']};
    ">
        <h3 style="margin: 0 0 10px 0; color: {theme['text_primary']};">{title}</h3>
        <p style="margin: 0; font-size: 14px; opacity: 0.9; color: {theme['text_secondary']};">{description}</p>
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