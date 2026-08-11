"""
Overview Dashboard Page
High-level KPI scorecard with trends and comparisons
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import sys
import os

# --- PATH FIX: This allows imports from sibling directories like 'utils' ---
# It adds the project root to the path, assuming this file is in a subdirectory (e.g., page_modules)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# --------------------------------------------------------------------------

# Gemini is still used here for the on-demand "Key Insights" block.
# The chat assistant itself now lives in utils/ai_chat.py.
import google.generativeai as genai

# NOTE: calculate_all_country_kpis is now available from this import
from utils.kpi_calculator import calculate_summary_kpis, calculate_country_kpis, calculate_all_country_kpis, get_kpi_status 
from utils.visualizations import create_kpi_card, create_trend_line, COLORS, BENCHMARKS


# --- 1. LLM Configuration and Setup ---

# Initialize LLM Client
# NOTE: Client initialization happens outside the render function for efficiency
try:
    # Use st.secrets to securely access the API key
    if "GEMINI_API_KEY" not in st.secrets:
        api_key_configured = False
    else:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        api_key_configured = True
except Exception as e:
    st.error(f"Error configuring Gemini client: {e}")
    api_key_configured = False

MODEL_NAME = "gemini-2.5-flash"



# NOTE: The floating chat assistant used to live in this file. It now lives in
# `utils/ai_chat.py` and is rendered once per dashboard by `app.py`, OUTSIDE the
# tab container — so the bubble stays visible on every tab and the model gets
# the full cross-domain data snapshot (see `utils/ai_context.py`) instead of
# only these Overview KPIs.

# --- NEW FUNCTION FOR DYNAMIC INSIGHTS ---

def build_insights_prompt(kpis, country_kpis):
    """
    Constructs the prompt for the AI to generate a list of descriptive and
    diagnostic insights based on the current KPI data (for the Key Insights box).
    """
    # --- UPDATED: KPI LIST FOR AI CONTEXT ---
    kpi_list = (
        f"Total Households: {kpis.get('total_households', {}).get('value', 0):,.0f}",
        f"Access Rate Growth: {kpis.get('access_rate_growth', {}).get('value', 0):.1f}% (Target: >0%)",
        f"NRW (Non-Revenue Water): {kpis.get('nrw', {}).get('value', 0):.1f}% (Benchmark: ≤25%)",
        f"Revenue Collection Efficiency: {kpis.get('collection_efficiency', {}).get('value', 0):.1f}% (Target: ≥95%)",
        f"Total Reported Complaints: {kpis.get('complaints_count', {}).get('value', 0):,.0f}",
        f"Water Service Coverage: {kpis.get('water_service_coverage', {}).get('value', 0):.1f}% (Target: 100%)",
        f"Service Continuity: {kpis.get('service_continuity', {}).get('value', 0):.1f} hrs/day (Benchmark: 24 hrs)",
        f"Cost Recovery Ratio: {kpis.get('cost_recovery_ratio', {}).get('value', 0):.1f}% (Target: ≥100%)",
        f"Operational Profit/Loss: {kpis.get('operational_profit_loss', {}).get('value', 0):,.0f} (Target: >0)",
        f"Avg. Complaint Resolution Time: {kpis.get('complaint_resolution_time', {}).get('value', 0):.1f} days (Target: ≤5 days)",
    )


    country_data_string = ""
    if country_kpis:
        country_data_string = "\n\nDETAILED COUNTRY KPIS:\n"
        for country, data in country_kpis.items():
            country_data_string += f"--- {country} ---\n"
            country_data_string += f"- NRW: {data.get('nrw', 0):.1f}% (Target ≤25%)\n"
            country_data_string += f"- Cost Recovery Ratio: {data.get('cost_recovery_ratio', 0):.1f}% (Target ≥100%)\n"
            country_data_string += f"- Water Service Coverage: {data.get('water_service_coverage', 0):.1f}% (Target 100%)\n"

    return f"""
    You are an expert Water Sector Performance Analyst. Generate exactly 4 SHORT bullet points:

    • **Key Finding**: Most critical metric vs benchmark (1 sentence max)
    • **Top Performer**: Best performing country/area with data
    • **Concern**: Biggest underperformance with specific number  
    • **Root Cause**: Main driver linking NRW, Collection, or Cost Recovery

    RULES: 
    - Each bullet MUST be 1-2 sentences maximum
    - Include specific numbers from the data
    - NO introductions, conclusions, or extra text
    - Use bullet format only (•)

    KPI DATA:
    {'\n'.join([f'- {item}' for item in kpi_list])}
    {country_data_string}
    """


@st.cache_data(show_spinner=False)
def _insights_cache_key(kpis, country_kpis):
    """Stable session-state cache key for a given data context."""
    return f"insights_cache_{hash(build_insights_prompt(kpis, country_kpis))}"


def get_ai_insights(kpis, country_kpis):
    """Fetches the generated insights from the AI, cached per data context."""
    # Bail out early if AI is unavailable or was disabled after a fatal error
    if not api_key_configured or st.session_state.get("_ai_disabled"):
        return None

    # Cache per context so we only hit the network ONCE per country/filter
    # combination, instead of regenerating on every rerun.
    cache_key = _insights_cache_key(kpis, country_kpis)
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    prompt = build_insights_prompt(kpis, country_kpis)

    try:
        model = genai.GenerativeModel(model_name=MODEL_NAME)
        response = model.generate_content(prompt)
        st.session_state[cache_key] = response.text
        return response.text
    except Exception:
        # Don't disable AI session-wide on a single failed click — the caller
        # surfaces a retry message and the button stays available.
        return None


# --- END NEW FUNCTIONS ---


def render_overview_page(data, countries_filter, date_range=None):
    """Render the overview dashboard page"""
    
    st.title("📊 Overview Dashboard")
    st.markdown("### High-Level Performance Metrics Across All Countries")
    
    # Filter data by selected countries (Existing Logic)
    if countries_filter:
        data_filtered = {
            key: df[df['country'].isin(countries_filter)] if 'country' in df.columns else df
            for key, df in data.items()
        }
    else:
        data_filtered = data
    
    # Calculate KPIs (Existing Logic)
    summary_kpis = calculate_summary_kpis(data_filtered)
    
    # --- NEW: Calculate Country KPIs for AI Context ---
    country_kpis = calculate_all_country_kpis(data_filtered)
    
    if not summary_kpis:
        st.warning("No KPI data is available for the current filter selection. Adjust the filters to load results.")
        return

    st.markdown("---")
    
    # Existing KPI Scorecard Section 
    st.header("🎯 KPI Scorecard")
    
    # --- MAJOR CHANGE: UPDATING KPI CARDS TO NEW LIST ---
    kpi_card_config = [
        # Households & Access
        ('total_households', "Total Households"),
        ('water_service_coverage', "Water Service Coverage"), 
        ('access_rate_growth', "Access Rate Growth"),
        
        # Financial
        ('collection_efficiency', "Revenue Collection Efficiency"),
        ('cost_recovery_ratio', "Cost Recovery Ratio"), 
        ('operational_profit_loss', "Operational Profit/Loss"),
        
        # Operations & Quality
        ('nrw', "Non-Revenue Water"),
        ('service_continuity', "Service Continuity (Hrs/Day)"),
        ('complaints_count', "Reported Complaints (Total)"),
        ('complaint_resolution_time', "Avg. Resolution Time (Days)"),
    ]
    
    # Display KPI cards in rows of 4 (REFRESHED LOGIC)
    cols_per_row = 4
    
    # Initialize the columns container outside the loop
    cols = st.columns(cols_per_row)
    
    for idx, (key, title) in enumerate(kpi_card_config):
        metric = summary_kpis.get(key)
        
        # Check if metric is calculated and valid before displaying
        if metric is None or 'value' not in metric:
            # For the refactoring, we'll keep the skip, but once 
            # kpi_calculator is fixed, all 10 should show.
            continue 

        value = metric['value']
        benchmark = metric['benchmark']
        unit = metric.get('unit', '')
        inverse = metric.get('inverse', False)
        
        # --- NEW METRIC CALCULATION FOR ST.METRIC ---
        
        # Calculate Delta and format Delta Value
        delta = value - benchmark
        
        if key == 'operational_profit_loss':
            # Operational P/L usually doesn't compare to a benchmark value, 
            # but rather to the previous period. Using the current 'delta' 
            # (value - benchmark) is misleading. For now, let's show the value simply.
            value_display = f"{value:,.0f}"
            delta_value = None # No delta for P/L benchmark comparison
            delta_color = 'off'
        elif key == 'total_households' or key == 'complaints_count':
            # These are absolute counts, usually compared to previous period, not a static benchmark.
            value_display = f"{value:,.0f}"
            delta_value = None 
            delta_color = 'off'
        else:
            # Standard KPI comparison (Percent or Time)
            value_display = f"{value:,.1f}{unit}"
            delta_value = f"{delta:+.1f}{unit}" # Show change with +/- sign
            
            # Determine color based on whether the delta is good or bad
            if inverse:
                # E.g., NRW (lower is better): positive delta is bad (red), negative delta is good (green)
                delta_color = 'inverse' 
            else:
                # E.g., Cost Recovery (higher is better): positive delta is good (green), negative delta is bad (red)
                delta_color = 'normal'
            
        
        # Get the current column index for the st.metric placement
        col_idx = idx % cols_per_row
        
        with cols[col_idx]:
            st.metric(
                label=f"**{title}** (Target: {benchmark}{unit})",
                value=value_display,
                delta=delta_value,
                delta_color=delta_color
            )
            
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")
    
    # --- Key Insights Section (AI GENERATED, ON-DEMAND) ---
    # Generated only when the user asks for it, so the dashboard renders
    # instantly when switching countries instead of blocking on the AI call.
    if api_key_configured and not st.session_state.get("_ai_disabled"):
        st.header("💡 Key Insights")

        cache_key = _insights_cache_key(summary_kpis, country_kpis)
        already_generated = cache_key in st.session_state

        if not already_generated:
            if st.button("✨ Generate AI Insights", key="gen_insights"):
                with st.spinner("Running AI Diagnostic Analysis..."):
                    result = get_ai_insights(summary_kpis, country_kpis)
                if result:
                    st.rerun()  # redraw cleanly: hide the button, show insights
                else:
                    st.warning("⚠️ Couldn't generate insights. Make sure a valid GEMINI_API_KEY is configured.")
            else:
                st.caption("Click to generate an AI diagnostic summary for the current selection.")

        # Show the result once it has been generated for this context
        ai_insights_markdown = st.session_state.get(cache_key)
        if ai_insights_markdown:
            st.markdown(ai_insights_markdown)
