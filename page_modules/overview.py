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

# New imports for Gemini Chatbot
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

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

MODEL_NAME = "gemini-2.0-flash-exp"


def get_chat_session(system_prompt):
    """Initializes the chat session with the system prompt."""
    if api_key_configured:
        try:
            # Initialize the model with system instruction
            model = genai.GenerativeModel(
                model_name=MODEL_NAME,
                system_instruction=system_prompt
            )
            # Start a chat session
            chat = model.start_chat(history=[])
            # Return the chat object AND the system prompt for later comparison
            return chat, system_prompt 
        except Exception as e:
            st.error(f"Error initializing chat session: {e}")
            return None, None
    return None, None


def build_system_prompt(kpis, country_kpis):
    """
    Constructs the detailed instruction (system prompt) for the AI, 
    injecting the current KPI data and system structure for context.
    """
    # --- KPI LIST FOR AI CONTEXT ---
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
    
    # --- DIAGNOSTIC INSIGHTS ---
    diagnostic_insights = (
        "High NRW negatively impacts cost recovery, as water is produced but not paid for.",
        "A Cost Recovery Ratio below 100% indicates unsustainable operations, as operating costs are not covered by revenue.",
        "Negative Access Rate Growth suggests that service expansion is not keeping pace with population growth or urban development.",
    )

    # --- DETAILED COUNTRY DATA INJECTION ---
    country_data_string = ""
    if country_kpis:
        country_data_string = "\n\nDETAILED COUNTRY KPIS:\n"
        for country, data in country_kpis.items():
            country_data_string += f"--- {country} ---\n"
            country_data_string += f"- NRW: {data.get('nrw', 0):.1f}% (Target ≤25%)\n"
            country_data_string += f"- Cost Recovery Ratio: {data.get('cost_recovery_ratio', 0):.1f}% (Target ≥100%)\n"
            country_data_string += f"- Water Service Coverage: {data.get('water_service_coverage', 0):.1f}% (Target 100%)\n"
            
    # --- APPLICATION STRUCTURE INJECTION (NEW) ---
    application_structure = (
        "This application is a Streamlit dashboard with pages accessible via the sidebar.",
        "The available pages are: Overview (Current Page), Production, Finance, Service, and Reports.",
        "To view country-level comparison charts and zonal data, users must navigate to the **Reports** page in the sidebar.",
        "Historical trends are available on the **Production** page."
    )
    
    # --- END: Application Structure Injection ---
    
    return f"""
    You are an expert Water Sector Performance Analyst chatbot. Your sole purpose is to provide analysis and answer questions based ONLY on the data and insights provided below.
    
    CURRENT KPIS (The current data context from the dashboard):
    {'\n'.join([f'- {item}' for item in kpi_list])}
    
    {country_data_string}
    
    DIAGNOSTIC INSIGHTS (The contextual rules and correlations):
    {'\n'.join([f'- {item}' for item in diagnostic_insights])}
    
    APPLICATION STRUCTURE (The Streamlit app navigation context):
    {'\n'.join([f'- {item}' for item in application_structure])}

    RULES:
    1. Respond concisely and professionally.
    2. Directly reference the data values provided in the CURRENT KPIS or DETAILED COUNTRY KPIS when possible.
    3. If the user asks about system navigation (e.g., 'where to find X'), use the **APPLICATION STRUCTURE** context to guide them.
    4. If the data is not provided or the question is outside the scope of the CURRENT KPIS, DIAGNOSTIC INSIGHTS, and APPLICATION STRUCTURE, state clearly that you can only answer based on the current context.
    5. Detect the language of the user's query and respond entirely in that detected language.
    
    Based on the CURRENT KPIS, the biggest operational challenge is likely related to **Non-Revenue Water (NRW)**, as the average is {kpis.get('nrw', {}).get('value', 0):.1f}%, which needs to be below the benchmark of ≤25% to ensure efficient resource use. A major financial challenge is the **Cost Recovery Ratio**, which is {kpis.get('cost_recovery_ratio', {}).get('value', 0):.1f}%, signaling that current revenues are not fully covering operating expenses.
    """


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
    You are an expert Water Sector Performance Analyst. Analyze the following KPI data and generate 3 to 5 clear, actionable, and concise insights.

    Divide your output into two sections:
    1. **Descriptive Insights:** State 2-3 key findings directly from the data (e.g., performance against benchmarks).
    2. **Diagnostic Insights:** State 1-2 key correlations or root causes identified from the data (e.g., 'Country X's high NRW is the main driver of low Cost Recovery').

    Format the output as a clean, single markdown block with bold headings and bullet points. Do NOT include any introductory or concluding conversational text.

    KPI DATA:
    {'\n'.join([f'- {item}' for item in kpi_list])}
    {country_data_string}

    Correlations to consider:
    - Low Cost Recovery Ratio correlates with high NRW and low Collection Efficiency.
    - High Complaint Volume/Resolution Time suggests inadequate service delivery quality.
    """


@st.cache_data(show_spinner=False)
def get_ai_insights(kpis, country_kpis):
    """Fetches the generated insights from the AI, using caching."""
    if not api_key_configured:
        return None
        
    prompt = build_insights_prompt(kpis, country_kpis)
    
    try:
        model = genai.GenerativeModel(model_name=MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"AI Analysis Error: {e}")
        return None


# --- END NEW FUNCTIONS ---


