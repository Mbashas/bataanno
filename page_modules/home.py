"""
Landing Page / Home Page
Entry point with navigation cards and summary KPIs
Redesigned with modern UI and custom branding
"""

import streamlit as st
import plotly.graph_objects as go
from utils.data_loader import load_all_data, get_latest_update_date
from utils.kpi_calculator import calculate_summary_kpis, calculate_country_kpis
from utils.visualizations import COLORS
from utils.theme import get_theme, BRAND, LIGHT_THEME
from assets.logo_svg import get_wash_logo_colored_svg


def render_home_page(data, countries_filter, date_range=None):
    """Render the home/landing page with country selection cards"""
    theme = get_theme()
    
    # Clean page header with styled logo box
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
    
    # Country Selection Section
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
    
    # Country configuration with equal treatment for all countries
    countries_config = [
        {
            'name': 'Uganda',
            'emoji': '🇺🇬',
            'description': 'National Water and Sewerage Corporation (NWSC)',
            'zones': 'Central, Kawempe, Nakawa, Rubaga',
            'color': theme['countries']['Uganda']
        },
        {
            'name': 'Malawi',
            'emoji': '🇲🇼',
            'description': 'Lilongwe Water Board (LWB)',
            'zones': 'Capital Hill, Kanengo, Lumbadzi, Old Town',
            'color': theme['countries']['Malawi']
        },
        {
            'name': 'Lesotho',
            'emoji': '🇱🇸',
            'description': 'Water and Sewerage Company (WASCO)',
            'zones': 'Maseru Urban, Maseru Rural, Rural Hinterland',
            'color': theme['countries']['Lesotho']
        },
        {
            'name': 'Cameroon',
            'emoji': '🇨🇲',
            'description': 'Camerounaise Des Eaux (CDE)',
            'zones': 'Yaounde 1-7',
            'color': theme['countries']['Cameroon']
        }
    ]
    
    # Country Performance Summary - Individual country KPI cards (MOVED UP per feedback)
    st.header("📊 Country Performance Summary")
    st.markdown("Key performance indicators for each country")
    
    # Calculate KPIs for each country
    country_names = ['Uganda', 'Malawi', 'Lesotho', 'Cameroon']
    country_emojis = {'Uganda': '🇺🇬', 'Malawi': '🇲🇼', 'Lesotho': '🇱🇸', 'Cameroon': '🇨🇲'}
    
    # Display country KPI summary cards in 2x2 grid
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    
    country_cols = [row1_col1, row1_col2, row2_col1, row2_col2]
    
    for idx, country_name in enumerate(country_names):
        country_kpis = calculate_country_kpis(data, country_name)
        
        with country_cols[idx]:
            render_country_kpi_summary(
                country_name,
                country_emojis[country_name],
                country_kpis,
                theme['countries'][country_name],
                theme
            )
    
    st.markdown("---")
    
    # Equal 2x2 Grid Layout for all countries
    # First row
    col1, col2 = st.columns(2)
    with col1:
        render_country_card_equal(
            countries_config[0]['name'],
            countries_config[0]['emoji'],
            countries_config[0]['description'],
            countries_config[0]['zones'],
            countries_config[0]['color'],
            theme=theme
        )
    with col2:
        render_country_card_equal(
            countries_config[1]['name'],
            countries_config[1]['emoji'],
            countries_config[1]['description'],
            countries_config[1]['zones'],
            countries_config[1]['color'],
            theme=theme
        )
    
    # Second row
    col3, col4 = st.columns(2)
    with col3:
        render_country_card_equal(
            countries_config[2]['name'],
            countries_config[2]['emoji'],
            countries_config[2]['description'],
            countries_config[2]['zones'],
            countries_config[2]['color'],
            theme=theme
        )
    with col4:
        render_country_card_equal(
            countries_config[3]['name'],
            countries_config[3]['emoji'],
            countries_config[3]['description'],
            countries_config[3]['zones'],
            countries_config[3]['color'],
            theme=theme
        )
    
    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # How to Use Guide
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
    
    # Footer
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
    """Render a modern country selection card with clean styling (DEPRECATED - use render_country_card_equal)"""
    if theme is None:
        theme = get_theme()
    
    # Use theme-aware background colors
    bg_color = theme['bg_card']
    
    # Card styling based on hero status
    if is_hero:
        # Hero card container with accent border
        st.markdown(f"""
        <div style="
            background: {bg_color};
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 16px;
            border: 1px solid {theme['border']};
            border-left: 5px solid {color};
            box-shadow: {theme['shadow']};
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
        # Regular card (compact)
        st.markdown(f"""
        <div style="
            background: {bg_color};
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 12px;
            border: 1px solid {theme['border']};
            border-left: 4px solid {color};
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


def render_country_card_equal(country_name, emoji, description, zones, color, theme=None):
    """Render an equal-sized country selection card for 2x2 grid layout"""
    if theme is None:
        theme = get_theme()
    
    # Use theme-aware background colors
    bg_color = theme['bg_card']
    
    st.markdown(f"""
    <div style="
        background: {bg_color};
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        border: 1px solid {theme['border']};
        border-left: 5px solid {color};
        box-shadow: {theme['shadow']};
        min-height: 140px;
    ">
        <div style="display: flex; align-items: flex-start; gap: 16px;">
            <div style="font-size: 42px; line-height: 1;">{emoji}</div>
            <div style="flex: 1;">
                <h3 style="color: {theme['text_primary']}; margin: 0 0 6px 0; font-size: 1.25rem; font-weight: 700;">{country_name}</h3>
                <p style="color: {theme['text_secondary']}; margin: 0 0 6px 0; font-size: 13px;">{description}</p>
                <p style="color: {theme['text_muted']}; margin: 0; font-size: 11px;">📍 <strong>Zones:</strong> {zones}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(f"🔍 View {country_name} Dashboard", key=f"country_{country_name}_equal", use_container_width=True):
        st.session_state.selected_country = country_name
        st.rerun()


def render_country_kpi_summary(country_name, emoji, kpis, color, theme):
    """Render a country KPI summary card with key metrics"""
    # Extract key KPIs
    nrw = kpis.get('nrw', 0)
    cost_recovery = kpis.get('cost_recovery_ratio', 0)
    water_coverage = kpis.get('water_service_coverage', 0)
    service_hours = kpis.get('service_continuity', 0)
    
    # Determine NRW status color (Benchmark: ≤25%)
    nrw_color = COLORS['good'] if nrw <= 25 else (COLORS['acceptable'] if nrw <= 37.5 else COLORS['poor'])
    # Cost recovery status (Benchmark: ≥100%)
    cr_color = COLORS['good'] if cost_recovery >= 100 else (COLORS['acceptable'] if cost_recovery >= 80 else COLORS['poor'])
    # Water coverage status (Target: 100%)
    wc_color = COLORS['good'] if water_coverage >= 90 else (COLORS['acceptable'] if water_coverage >= 70 else COLORS['poor'])
    # Service hours status (Target: ≥20 hrs/day)
    sh_color = COLORS['good'] if service_hours >= 20 else (COLORS['acceptable'] if service_hours >= 16 else COLORS['poor'])
    
    # Check for data quality issues (Cameroon NRW)
    nrw_warning = ""
    if country_name == "Cameroon" and nrw == 0:
        nrw_warning = "⚠️ Data Issue"
        nrw_color = COLORS['acceptable']
    
    st.markdown(f"""
    <div style="
        background: {theme['bg_card']};
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 12px;
        border: 1px solid {theme['border']};
        border-top: 4px solid {color};
        box-shadow: {theme['shadow']};
    ">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 14px;">
            <span style="font-size: 28px;">{emoji}</span>
            <h4 style="color: {theme['text_primary']}; margin: 0; font-size: 1.1rem; font-weight: 700;">{country_name}</h4>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div style="background: rgba(0,0,0,0.02); padding: 10px; border-radius: 8px;" title="Non-Revenue Water: Target ≤25%">
                <p style="margin: 0; font-size: 11px; color: {theme['text_muted']};">NRW <span style="font-size: 9px; opacity: 0.7;">(≤25%)</span></p>
                <p style="margin: 2px 0 0 0; font-size: 18px; font-weight: 700; color: {nrw_color};">
                    {nrw_warning if nrw_warning else f"{nrw:.1f}%"}
                </p>
            </div>
            <div style="background: rgba(0,0,0,0.02); padding: 10px; border-radius: 8px;" title="Cost Recovery Ratio: Target ≥100%">
                <p style="margin: 0; font-size: 11px; color: {theme['text_muted']};">Cost Recovery <span style="font-size: 9px; opacity: 0.7;">(≥100%)</span></p>
                <p style="margin: 2px 0 0 0; font-size: 18px; font-weight: 700; color: {cr_color};">{cost_recovery:.1f}%</p>
            </div>
            <div style="background: rgba(0,0,0,0.02); padding: 10px; border-radius: 8px;" title="Water Service Coverage: Target 100%">
                <p style="margin: 0; font-size: 11px; color: {theme['text_muted']};">Water Coverage <span style="font-size: 9px; opacity: 0.7;">(100%)</span></p>
                <p style="margin: 2px 0 0 0; font-size: 18px; font-weight: 700; color: {wc_color};">{water_coverage:.1f}%</p>
            </div>
            <div style="background: rgba(0,0,0,0.02); padding: 10px; border-radius: 8px;" title="Service Hours: Target ≥20 hrs/day">
                <p style="margin: 0; font-size: 11px; color: {theme['text_muted']};">Service Hours <span style="font-size: 9px; opacity: 0.7;">(≥20)</span></p>
                <p style="margin: 2px 0 0 0; font-size: 18px; font-weight: 700; color: {sh_color};">{service_hours:.1f} hrs</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


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