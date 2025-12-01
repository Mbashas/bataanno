"""
Theme Configuration Module
Centralized theming system with dark/light mode toggle
Water Services Dashboard - Blue Ocean Theme
"""

import streamlit as st

# ============================================================================
# WASH DASHBOARD BRAND COLORS
# ============================================================================

BRAND = {
    'name': 'WASH Performance Dashboard',
    'tagline': 'Multi-Country Water Services Analytics',
    'logo_emoji': '💧',
    'version': '3.0.0'
}

# ============================================================================
# COLOR PALETTES
# ============================================================================

LIGHT_THEME = {
    # Primary Brand Colors (Blue Water Theme)
    'primary': '#113F67',          # Deep Navy - headers, primary buttons
    'primary_light': '#1a5a8a',    # Lighter navy for hover
    'secondary': '#34699A',        # Medium Blue - secondary elements
    'tertiary': '#58A0C8',         # Sky Blue - accents, charts
    'accent': '#FDF5AA',           # Soft Yellow - alerts, highlights
    
    # Background Colors - Softer, warmer palette
    'bg_main': '#F7F9FC',          # Soft blue-white background
    'bg_main_gradient': 'linear-gradient(180deg, #FFFFFF 0%, #F0F5FA 50%, #E8EFF7 100%)',
    'bg_card': '#FFFFFF',          # Clean white card background
    'bg_card_hover': '#FAFBFD',    # Subtle hover state
    'bg_sidebar': '#113F67',       # Navy sidebar
    'bg_header': '#FFFFFF',        # White header
    
    # Text Colors
    'text_primary': '#1A202C',     # Almost black - main text
    'text_secondary': '#4A5568',   # Dark gray - secondary text
    'text_muted': '#718096',       # Medium gray - muted text
    'text_on_primary': '#FFFFFF',  # White text on primary bg
    'text_on_dark': '#E2E8F0',     # Light text on dark bg
    
    # Status Colors (WCAG AA Compliant)
    'success': '#059669',          # Emerald green
    'success_bg': '#D1FAE5',       # Light green background
    'warning': '#D97706',          # Amber
    'warning_bg': '#FEF3C7',       # Light amber background
    'danger': '#DC2626',           # Red
    'danger_bg': '#FEE2E2',        # Light red background
    'info': '#0284C7',             # Sky blue
    'info_bg': '#E0F2FE',          # Light blue background
    
    # Chart Colors
    'chart_primary': '#113F67',
    'chart_secondary': '#34699A',
    'chart_tertiary': '#58A0C8',
    'chart_quaternary': '#93C5FD',
    'chart_grid': '#E2E8F0',
    'chart_axis': '#64748B',
    
    # Country Colors (Accessible)
    'countries': {
        'Uganda': '#DC2626',       # Red
        'Cameroon': '#059669',     # Green
        'Lesotho': '#7C3AED',      # Purple
        'Malawi': '#D97706'        # Orange
    },
    
    # Borders & Shadows
    'border': '#E2E8F0',
    'border_dark': '#CBD5E1',
    'shadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    'shadow_lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
}

DARK_THEME = {
    # Primary Brand Colors (Blue Water Theme - Adjusted for Dark)
    'primary': '#58A0C8',          # Sky Blue - primary on dark
    'primary_light': '#7AB8D8',    # Lighter blue for hover
    'secondary': '#34699A',        # Medium Blue
    'tertiary': '#113F67',         # Deep Navy - accents
    'accent': '#FDF5AA',           # Soft Yellow - alerts
    
    # Background Colors
    'bg_main': '#0a1929',          # Dark navy main background (better contrast)
    'bg_card': '#1a2942',          # Medium dark card background
    'bg_sidebar': '#0a1929',       # Dark sidebar
    'bg_header': '#1a2942',        # Dark header
    
    # Text Colors
    'text_primary': '#F8FAFC',     # Bright white - main text (improved contrast)
    'text_secondary': '#E2E8F0',   # Very light gray - secondary text (improved)
    'text_muted': '#94A3B8',       # Medium gray - muted text
    'text_on_primary': '#0F172A',  # Dark text on primary bg
    'text_on_dark': '#F8FAFC',     # Bright white on dark bg (improved)
    
    # Status Colors (WCAG AA Compliant on Dark)
    'success': '#34D399',          # Emerald light
    'success_bg': '#064E3B',       # Dark green background
    'warning': '#FBBF24',          # Yellow
    'warning_bg': '#78350F',       # Dark amber background
    'danger': '#F87171',           # Light red
    'danger_bg': '#7F1D1D',        # Dark red background
    'info': '#38BDF8',             # Light blue
    'info_bg': '#0C4A6E',          # Dark blue background
    
    # Chart Colors
    'chart_primary': '#58A0C8',
    'chart_secondary': '#34699A',
    'chart_tertiary': '#93C5FD',
    'chart_quaternary': '#BFDBFE',
    'chart_grid': '#334155',
    'chart_axis': '#94A3B8',
    
    # Country Colors (Accessible on Dark)
    'countries': {
        'Uganda': '#F87171',       # Light Red
        'Cameroon': '#34D399',     # Light Green
        'Lesotho': '#A78BFA',      # Light Purple
        'Malawi': '#FBBF24'        # Yellow
    },
    
    # Borders & Shadows
    'border': '#334155',
    'border_dark': '#475569',
    'shadow': '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)',
    'shadow_lg': '0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2)',
}

# ============================================================================
# BENCHMARKS & KPI THRESHOLDS
# ============================================================================

BENCHMARKS = {
    'water_coverage': {'target': 100, 'unit': '%', 'inverse': False},
    'sanitation_coverage': {'target': 100, 'unit': '%', 'inverse': False},
    'nrw': {'target': 25, 'unit': '%', 'inverse': True},
    'water_quality': {'target': 95, 'unit': '%', 'inverse': False},
    'service_hours': {'target': 20, 'unit': 'hrs/day', 'inverse': False},
    'collection_efficiency': {'target': 95, 'unit': '%', 'inverse': False},
    'occr': {'target': 110, 'unit': '%', 'inverse': False},
    'cost_recovery_ratio': {'target': 100, 'unit': '%', 'inverse': False},
    'metering_ratio': {'target': 95, 'unit': '%', 'inverse': False},
    'staff_productivity': {'target': 7, 'unit': 'staff/1k', 'inverse': True},
    'personnel_cost_ratio': {'target': 35, 'unit': '%', 'inverse': True},
}

# ============================================================================
# THEME MANAGEMENT FUNCTIONS
# ============================================================================

def init_theme():
    """Initialize theme in session state"""
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'


def get_theme():
    """Get current theme colors"""
    init_theme()
    return LIGHT_THEME if st.session_state.theme == 'light' else DARK_THEME


def toggle_theme():
    """Toggle between light and dark theme"""
    init_theme()
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'


def get_status_color(value, benchmark, inverse=False):
    """
    Get status color based on value vs benchmark
    
    Args:
        value: Current metric value
        benchmark: Target benchmark
        inverse: If True, lower is better (e.g., NRW)
    
    Returns:
        tuple: (status_name, color_hex)
    """
    theme = get_theme()
    
    if inverse:
        if value <= benchmark:
            return ('good', theme['success'])
        elif value <= benchmark * 1.5:
            return ('warning', theme['warning'])
        else:
            return ('critical', theme['danger'])
    else:
        if value >= benchmark:
            return ('good', theme['success'])
        elif value >= benchmark * 0.8:
            return ('warning', theme['warning'])
        else:
            return ('critical', theme['danger'])


def get_status_pill_html(status):
    """Generate HTML for a status pill badge"""
    theme = get_theme()
    
    config = {
        'good': {'bg': theme['success_bg'], 'text': theme['success'], 'label': '● On Track'},
        'warning': {'bg': theme['warning_bg'], 'text': theme['warning'], 'label': '● Warning'},
        'critical': {'bg': theme['danger_bg'], 'text': theme['danger'], 'label': '● Critical'},
    }
    
    c = config.get(status, config['warning'])
    
    return f"""
    <span style="
        background-color: {c['bg']};
        color: {c['text']};
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
    ">{c['label']}</span>
    """


# ============================================================================
# CSS GENERATION
# ============================================================================

def generate_css():
    """Generate complete CSS based on current theme"""
    t = get_theme()
    is_dark = st.session_state.get('theme', 'light') == 'dark'
    
    # Light mode background - Professional Water Theme (Soft & Clean)
    light_bg = '#F0F7FA'
    light_bg_gradient = 'linear-gradient(180deg, #FFFFFF 0%, #F4F9FC 50%, #E6F0F7 100%)'
    
    # Dark mode specific overrides
    dark_mode_css = ""
    if is_dark:
        dark_mode_css = f"""
        /* ===== DARK MODE OVERRIDES ===== */
        .stApp {{
            background-color: {t['bg_main']} !important;
        }}
        
        /* Force dark text colors on main content */
        .main,
        .main p,
        .main span,
        .main div,
        .main label,
        .main h1,
        .main h2,
        .main h3,
        .main h4,
        .main h5,
        .main h6,
        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] span,
        [data-testid="stMetricValue"],
        [data-testid="stMetricLabel"],
        .stMetric label,
        .stMetric [data-testid="stMetricValue"] {{
            color: {t['text_primary']} !important;
        }}
        
        /* Dark mode cards */
        [data-testid="stExpander"],
        .streamlit-expanderHeader {{
            background-color: {t['bg_card']} !important;
            border-color: {t['border']} !important;
        }}
        
        .streamlit-expanderHeader {{
            color: {t['text_primary']} !important;
        }}
        
        /* Dark mode inputs */
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stMultiSelect > div > div,
        .stDateInput > div > div > input,
        .stNumberInput > div > div > input {{
            background-color: {t['bg_card']} !important;
            color: {t['text_primary']} !important;
            border-color: {t['border']} !important;
        }}
        
        /* Dark mode tabs */
        .stTabs [data-baseweb="tab"] {{
            color: {t['text_secondary']} !important;
        }}
        
        .stTabs [aria-selected="true"] {{
            color: {t['primary']} !important;
        }}
        
        /* Dark mode dataframe */
        .stDataFrame {{
            background-color: {t['bg_card']} !important;
        }}
        
        [data-testid="stDataFrame"] div {{
            color: {t['text_primary']} !important;
        }}
        
        /* Dark mode alerts */
        [data-baseweb="notification"] {{
            background-color: {t['bg_card']} !important;
        }}
        
        [data-baseweb="notification"] div {{
            color: {t['text_primary']} !important;
        }}
        """
    
    return f"""
    <style>
        /* ===== CSS VARIABLES ===== */
        :root {{
            --primary: {t['primary']};
            --primary-light: {t['primary_light']};
            --secondary: {t['secondary']};
            --tertiary: {t['tertiary']};
            --accent: {t['accent']};
            
            --bg-main: {t['bg_main']};
            --bg-card: {t['bg_card']};
            --bg-sidebar: {t['bg_sidebar']};
            
            --text-primary: {t['text_primary']};
            --text-secondary: {t['text_secondary']};
            --text-muted: {t['text_muted']};
            --text-on-primary: {t['text_on_primary']};
            
            --success: {t['success']};
            --warning: {t['warning']};
            --danger: {t['danger']};
            --info: {t['info']};
            
            --border: {t['border']};
            --shadow: {t['shadow']};
        }}
        
        /* ===== GLOBAL BACKGROUND - AGGRESSIVE OVERRIDE ===== */
        html, body {{
            background: {t['bg_main'] if is_dark else light_bg} !important;
        }}
        
        .stApp {{
            background: {t['bg_main'] if is_dark else light_bg_gradient} !important;
            min-height: 100vh;
        }}
        
        .stApp > div,
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewBlockContainer"],
        .main,
        .main > div,
        section.main,
        section.main > div {{
            background: {t['bg_main'] if is_dark else 'transparent'} !important;
        }}
        
        /* Override Streamlit's default white backgrounds */
        .st-emotion-cache-zy6yx3,
        .st-emotion-cache-tn0cau,
        .block-container,
        .e4man114,
        .e1wguzas3 {{
            background: transparent !important;
        }}
        
        .main .block-container {{
            padding: 2rem 3rem !important;
            max-width: 1400px !important;
            background: transparent !important;
        }}
        
        /* Force all vertical blocks to be transparent */
        .main [data-testid="stVerticalBlock"],
        .main [data-testid="stHorizontalBlock"] {{
            background: transparent !important;
        }}
        
        /* ===== TYPOGRAPHY ===== */
        h1, h2, h3, h4, h5, h6 {{
            color: {t['text_primary']} !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
            font-weight: 700 !important;
        }}
        
        h1 {{ font-size: 2.25rem !important; }}
        h2 {{ font-size: 1.75rem !important; }}
        h3 {{ font-size: 1.5rem !important; }}
        
        /* Main content text - NOT sidebar */
        .main p, .main span, .main div, .main label {{
            color: {t['text_primary']} !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        }}
        
        {dark_mode_css}
        
        /* ===== SIDEBAR ===== */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #113F67 0%, #0a2540 100%) !important;
        }}
        
        /* Sidebar text - VERY specific selectors */
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] * {{
            color: #F8FAFC !important;
        }}
        
        /* Sidebar buttons */
        [data-testid="stSidebar"] .stButton button,
        [data-testid="stSidebar"] button {{
            background-color: rgba(255, 255, 255, 0.15) !important;
            color: #F8FAFC !important;
            border: 1px solid rgba(255, 255, 255, 0.25) !important;
            transition: all 0.2s ease !important;
            background-image: none !important;
        }}
        
        [data-testid="stSidebar"] .stButton button:hover,
        [data-testid="stSidebar"] button:hover {{
            background-color: rgba(255, 255, 255, 0.25) !important;
            border-color: rgba(255, 255, 255, 0.4) !important;
        }}
        
        /* Sidebar expander text */
        [data-testid="stSidebar"] .streamlit-expanderHeader,
        [data-testid="stSidebar"] .streamlit-expanderContent {{
            color: #F8FAFC !important;
            background-color: rgba(255, 255, 255, 0.05) !important;
        }}
        
        /* Sidebar selectbox */
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stMultiSelect label {{
            color: #F8FAFC !important;
        }}
        
        [data-testid="stSidebar"] .stSelectbox > div > div,
        [data-testid="stSidebar"] .stMultiSelect > div > div {{
            background-color: rgba(255, 255, 255, 0.1) !important;
            border-color: rgba(255, 255, 255, 0.2) !important;
            color: #F8FAFC !important;
        }}
        
        /* Sidebar radio and checkbox */
        [data-testid="stSidebar"] .stRadio label,
        [data-testid="stSidebar"] .stCheckbox label {{
            color: #F8FAFC !important;
        }}
        
        /* Sidebar info/success/warning boxes */
        [data-testid="stSidebar"] [data-baseweb="notification"] {{
            background-color: rgba(255, 255, 255, 0.1) !important;
            border-color: rgba(255, 255, 255, 0.2) !important;
        }}
        
        [data-testid="stSidebar"] [data-baseweb="notification"] div {{
            color: #F8FAFC !important;
        }}
        
        /* ===== CARDS ===== */
        .wash-card {{
            background: {'linear-gradient(180deg, #FFFFFF 0%, #FAFBFD 100%)' if not is_dark else t['bg_card']};
            border-radius: 16px;
            padding: 24px;
            box-shadow: {'0 2px 8px rgba(17, 63, 103, 0.06), 0 1px 3px rgba(17, 63, 103, 0.04)' if not is_dark else t['shadow']};
            border: 1px solid {'rgba(17, 63, 103, 0.08)' if not is_dark else t['border']};
            transition: all 0.25s ease;
            backdrop-filter: blur(8px);
        }}
        
        .wash-card:hover {{
            box-shadow: {'0 8px 24px rgba(17, 63, 103, 0.1), 0 4px 8px rgba(17, 63, 103, 0.06)' if not is_dark else t['shadow_lg']};
            transform: translateY(-2px);
            border-color: {'rgba(17, 63, 103, 0.12)' if not is_dark else t['border_dark']};
        }}
        
        /* ===== METRIC CARDS ===== */
        .metric-card {{
            background: {'linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)' if not is_dark else t['bg_card']};
            border-radius: 14px;
            padding: 18px 22px;
            border-left: 4px solid var(--primary);
            box-shadow: {'0 2px 6px rgba(17, 63, 103, 0.05), 0 1px 2px rgba(17, 63, 103, 0.03)' if not is_dark else t['shadow']};
            transition: all 0.25s ease;
        }}
        
        .metric-card:hover {{
            box-shadow: {'0 6px 16px rgba(17, 63, 103, 0.08), 0 2px 6px rgba(17, 63, 103, 0.04)' if not is_dark else t['shadow_lg']};
            transform: translateY(-2px);
        }}
        
        .metric-card .metric-icon {{
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        }}
        
        .metric-card .metric-value {{
            font-size: 28px;
            font-weight: 700;
            color: var(--text-primary);
            line-height: 1.2;
        }}
        
        .metric-card .metric-label {{
            font-size: 12px;
            color: var(--text-secondary);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .metric-card .metric-delta {{
            font-size: 12px;
            font-weight: 600;
        }}
        
        .metric-card .delta-positive {{
            color: var(--success);
        }}
        
        .metric-card .delta-negative {{
            color: var(--danger);
        }}
        
        /* ===== COUNTRY CARDS ===== */
        .country-card {{
            background: {'linear-gradient(180deg, #FFFFFF 0%, #FAFCFF 100%)' if not is_dark else t['bg_card']};
            border-radius: 16px;
            padding: 24px;
            box-shadow: {'0 2px 8px rgba(17, 63, 103, 0.06), 0 1px 3px rgba(17, 63, 103, 0.04)' if not is_dark else t['shadow']};
            border: 1px solid {'rgba(17, 63, 103, 0.06)' if not is_dark else t['border']};
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        
        .country-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--card-accent, var(--primary));
        }}
        
        .country-card:hover {{
            transform: translateY(-4px);
            box-shadow: {'0 12px 32px rgba(17, 63, 103, 0.12), 0 4px 12px rgba(17, 63, 103, 0.08)' if not is_dark else t['shadow_lg']};
            border-color: {'rgba(17, 63, 103, 0.1)' if not is_dark else t['border_dark']};
        }}
        
        .country-card .flag {{
            font-size: 40px;
            margin-bottom: 8px;
        }}
        
        .country-card .country-name {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 6px;
        }}
        
        .country-card .utility-name {{
            font-size: 13px;
            color: var(--text-secondary);
            margin-bottom: 12px;
        }}
        
        /* ===== BUTTONS ===== */
        .stButton > button {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 2px 8px rgba(17, 63, 103, 0.2) !important;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(17, 63, 103, 0.3) !important;
        }}
        
        /* Primary Button Type */
        .stButton > button[kind="primary"] {{
            background: linear-gradient(135deg, {t['primary']} 0%, {t['secondary']} 100%) !important;
        }}
        
        /* Secondary Button Style */
        .stButton > button[kind="secondary"] {{
            background: transparent !important;
            color: var(--primary) !important;
            border: 1.5px solid var(--primary) !important;
            box-shadow: none !important;
        }}
        
        /* ===== TABS ===== */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: {'rgba(255, 255, 255, 0.7)' if not is_dark else 'transparent'} !important;
            border-bottom: 2px solid {'rgba(17, 63, 103, 0.1)' if not is_dark else t['border']} !important;
            padding: 4px !important;
            gap: 4px !important;
            border-radius: 12px 12px 0 0 !important;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            color: {t['text_secondary']} !important;
            background: transparent !important;
            border-bottom: 3px solid transparent !important;
            transition: all 0.25s ease !important;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            color: {t['primary']} !important;
            background: {'rgba(17, 63, 103, 0.04)' if not is_dark else 'rgba(255, 255, 255, 0.05)'} !important;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: {'rgba(17, 63, 103, 0.08)' if not is_dark else 'rgba(255, 255, 255, 0.1)'} !important;
            color: {t['primary']} !important;
            border-bottom-color: {t['primary']} !important;
        }}
        
        /* ===== INPUTS ===== */
        .stSelectbox > div > div,
        .stMultiSelect > div > div,
        .stTextInput > div > div > input,
        .stDateInput > div > div > input {{
            background-color: {'#FFFFFF' if not is_dark else t['bg_card']} !important;
            border: {'1.5px solid rgba(17, 63, 103, 0.15)' if not is_dark else '2px solid ' + t['border']} !important;
            border-radius: 10px !important;
            color: {t['text_primary']} !important;
            transition: all 0.2s ease !important;
            box-shadow: {'0 1px 3px rgba(17, 63, 103, 0.04)' if not is_dark else 'none'} !important;
        }}
        
        .stSelectbox > div > div:focus-within,
        .stMultiSelect > div > div:focus-within,
        .stTextInput > div > div > input:focus,
        .stDateInput > div > div > input:focus {{
            border-color: {t['primary']} !important;
            box-shadow: 0 0 0 3px {'rgba(17, 63, 103, 0.08)' if not is_dark else 'rgba(88, 160, 200, 0.2)'} !important;
        }}
        
        /* ===== EXPANDER ===== */
        .streamlit-expanderHeader {{
            background-color: var(--bg-card) !important;
            border-radius: 12px !important;
            border: 1px solid var(--border) !important;
            color: var(--text-primary) !important;
            font-weight: 600 !important;
        }}
        
        /* ===== DATAFRAME ===== */
        .stDataFrame {{
            border-radius: 12px !important;
            overflow: hidden !important;
            border: 1px solid var(--border) !important;
        }}
        
        /* ===== ALERTS ===== */
        .stAlert {{
            border-radius: 12px !important;
            border-left-width: 4px !important;
        }}
        
        [data-baseweb="notification"] {{
            border-radius: 12px !important;
        }}
        
        /* ===== CHARTS ===== */
        .js-plotly-plot {{
            border-radius: 12px !important;
            overflow: hidden !important;
        }}
        
        /* ===== THEME TOGGLE ===== */
        .theme-toggle {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .theme-toggle:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}
        
        /* ===== LOGIN PAGE ===== */
        .login-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            min-height: 100vh;
            margin: -6rem -4rem;
        }}
        
        .login-brand {{
            background: linear-gradient(135deg, {t['primary']} 0%, {t['secondary']} 50%, {t['tertiary']} 100%);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 48px;
            color: white;
        }}
        
        .login-brand h1 {{
            font-size: 3rem;
            color: white !important;
            margin-bottom: 16px;
        }}
        
        .login-brand p {{
            font-size: 1.25rem;
            color: rgba(255, 255, 255, 0.9) !important;
            text-align: center;
            max-width: 400px;
        }}
        
        .login-form {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 48px 64px;
            background: var(--bg-card);
        }}
        
        /* ===== HIDE STREAMLIT BRANDING ===== */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: visible !important;}}
        
        /* ===== SCROLLBAR ===== */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--bg-main);
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--border);
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--text-muted);
        }}
        
        /* ===== ANIMATIONS ===== */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .animate-fade-in {{
            animation: fadeIn 0.5s ease forwards;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .skeleton {{
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
            background: linear-gradient(90deg, var(--border) 25%, var(--bg-card) 50%, var(--border) 75%);
            background-size: 200% 100%;
        }}
    </style>
    """


# ============================================================================
# COMPONENT HELPERS
# ============================================================================

def render_metric_card(icon, label, value, delta=None, delta_type='positive', status=None):
    """
    Render a styled metric card
    
    Args:
        icon: Emoji or icon character
        label: Metric label
        value: Metric value (formatted string)
        delta: Change value (optional)
        delta_type: 'positive' or 'negative'
        status: 'good', 'warning', or 'critical' (optional)
    """
    theme = get_theme()
    
    # Border color based on status
    border_color = theme['primary']
    if status:
        status_colors = {
            'good': theme['success'],
            'warning': theme['warning'],
            'critical': theme['danger']
        }
        border_color = status_colors.get(status, theme['primary'])
    
    delta_html = ""
    if delta is not None:
        delta_class = 'delta-positive' if delta_type == 'positive' else 'delta-negative'
        delta_icon = '↑' if delta_type == 'positive' else '↓'
        delta_html = f'<span class="metric-delta {delta_class}">{delta_icon} {delta}</span>'
    
    status_html = ""
    if status:
        status_html = get_status_pill_html(status)
    
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: {border_color};">
        <div style="display: flex; align-items: flex-start; justify-content: space-between;">
            <div>
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                {delta_html}
            </div>
            <div class="metric-icon">{icon}</div>
        </div>
        {f'<div style="margin-top: 12px;">{status_html}</div>' if status else ''}
    </div>
    """, unsafe_allow_html=True)


def render_country_card(country, emoji, utility, zones, color, is_hero=False):
    """Render a styled country selection card"""
    hero_class = 'hero' if is_hero else ''
    
    st.markdown(f"""
    <div class="country-card {hero_class}" style="--card-accent: {color};">
        <div class="flag">{emoji}</div>
        <div class="country-name">{country}</div>
        <div class="utility-name">{utility}</div>
        <div style="font-size: 13px; color: var(--text-muted);">
            <strong>Zones:</strong> {zones}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_section_header(icon, title, subtitle=None):
    """Render a styled section header"""
    subtitle_html = f'<p style="color: var(--text-secondary); margin: 0; font-size: 14px;">{subtitle}</p>' if subtitle else ''
    
    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <h2 style="display: flex; align-items: center; gap: 12px; margin: 0;">
            <span style="font-size: 28px;">{icon}</span>
            {title}
        </h2>
        {subtitle_html}
    </div>
    """, unsafe_allow_html=True)


def render_page_header(title, subtitle=None):
    """Render a styled page header"""
    theme = get_theme()
    subtitle_html = f'<p style="color: var(--text-secondary); font-size: 16px; margin: 8px 0 0 0;">{subtitle}</p>' if subtitle else ''
    
    st.markdown(f"""
    <div style="margin-bottom: 32px; padding-bottom: 24px; border-bottom: 1px solid var(--border);">
        <h1 style="margin: 0; font-size: 2.5rem;">{title}</h1>
        {subtitle_html}
    </div>
    """, unsafe_allow_html=True)
