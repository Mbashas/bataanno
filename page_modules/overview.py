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

MODEL_NAME = "gemini-2.5-flash"


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


def _render_chat_panel(summary_kpis, country_kpis):
    """
    Render the inner chat experience (history, suggested prompts, input and
    export) for the floating AI Data Assistant widget.
    """
    # Rebuild the session whenever the underlying KPI context changes
    system_prompt = build_system_prompt(summary_kpis, country_kpis)

    context_changed = (
        "chat_session" not in st.session_state
        or st.session_state.get("chat_session") is None
        or st.session_state.get("chat_system_prompt") != system_prompt
    )

    if context_changed:
        with st.spinner("Initializing AI context..."):
            st.session_state.chat_session, st.session_state.chat_system_prompt = get_chat_session(system_prompt)
            st.session_state.messages = []  # Reset history for new context

    chat = st.session_state.chat_session
    if not chat:
        return

    # Are we waiting for an AI response to the last user message?
    is_waiting_for_response = (
        st.session_state.messages and st.session_state.messages[-1]["role"] == "user"
    )

    # Seed a welcome message the first time the panel opens
    if not st.session_state.messages:
        st.session_state.messages.append(
            {"role": "assistant",
             "content": """
Hello! I'm your **AI Data Assistant** for this dashboard.
I can analyze all current KPI data, explain correlations, and help you navigate the system.

Feel free to ask me:
1. **Data Questions:** "What is the Cost Recovery Ratio?"
2. **Diagnostic Questions:** "Why is our NRW a financial risk?"
3. **System Help:** "Where can I find the country-level comparison charts?"

Start by clicking one of the suggested prompts below!
"""}
        )

    # --- Chat history (scrollable, sized to fit the floating panel) ---
    chat_history_container = st.container(height=300, border=True)
    with chat_history_container:
        for message in st.session_state.messages:
            avatar = "🤖" if message["role"] == "assistant" else "👤"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

    prompt = None
    submitted_prompt = None

    # --- Suggested prompts (only before the conversation starts) ---
    conversation_started = any(m["role"] == "user" for m in st.session_state.messages)
    if not conversation_started and not is_waiting_for_response:
        suggested_prompts = [
            "What is the biggest operational challenge (NRW)?",
            "How does low Revenue Collection affect profit/loss?",
            "Where can I find the Service Continuity trend?",
        ]
        for i, prompt_text in enumerate(suggested_prompts):
            if st.button(prompt_text, use_container_width=True, key=f"suggested_btn_{i}"):
                st.session_state.input_prompt = prompt_text
                st.rerun()

    # --- Capture prompt: suggested button OR the chat input box ---
    if "input_prompt" in st.session_state and st.session_state.input_prompt:
        prompt = st.session_state.input_prompt
        del st.session_state.input_prompt
    elif not is_waiting_for_response:
        submitted_prompt = st.chat_input("Ask me about coverage, costs, or efficiency...")
        if submitted_prompt:
            prompt = submitted_prompt

    # Phase 1: capture prompt and rerun to immediately show the user's message
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    # --- Export the dialog ---
    if st.session_state.messages:
        dialog_content = ""
        for msg in st.session_state.messages:
            role = "USER" if msg["role"] == "user" else "ASSISTANT"
            dialog_content += f"**{role}:**\n{msg['content']}\n\n---\n\n"

        st.download_button(
            label="📥 Export Chat (TXT)",
            data=dialog_content,
            file_name="ai_data_assistant_dialog.txt",
            mime="text/plain",
            type="secondary",
            use_container_width=True,
        )

    # Phase 2: stream the AI response
    if is_waiting_for_response:
        current_prompt = st.session_state.messages[-1]["content"]

        with chat_history_container:
            with st.chat_message("assistant", avatar="🤖"):
                response_container = st.empty()
                with st.spinner(f"Analyzing data for '{current_prompt[:30]}...'"):
                    full_response = ""
                    try:
                        chat = st.session_state.chat_session
                        response = chat.send_message(current_prompt, stream=True)
                        for chunk in response:
                            if chunk.text:
                                full_response += chunk.text
                                response_container.markdown(full_response + "▌")
                        response_container.markdown(full_response)
                    except Exception as e:
                        full_response = f"An error occurred: {e}"
                        st.error(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()


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
    
    # --- Key Insights Section (AI GENERATED ONLY) ---
    if api_key_configured:
        st.header("💡 Key Insights")
        
        with st.spinner("Running AI Diagnostic Analysis..."):
            ai_insights_markdown = get_ai_insights(summary_kpis, country_kpis)

        if ai_insights_markdown:
            st.markdown(ai_insights_markdown)
        # If no AI insights available, show nothing (no fallback)
    
    # --- 2. AI Chat Assistant: floating toggle widget (bottom-right) ---

    # Collapsed/expanded state persists across reruns
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False
    chat_is_open = st.session_state.chat_open

    # Pin the widget to the bottom-right corner. Streamlit tags keyed
    # containers with a `st-key-<key>` class that we can target with CSS.
    if chat_is_open:
        # `!important` is required so the opaque card background wins over
        # Streamlit's default (transparent) vertical-block styling.
        panel_style = (
            "width: 420px; max-width: 92vw;"
            "background-color: #FFFFFF !important;"
            "border: 1px solid rgba(17, 63, 103, 0.15) !important;"
            "border-radius: 14px !important;"
            "padding: 0.75rem 1rem 0.5rem 1rem !important;"
            "box-shadow: 0 10px 30px rgba(17, 63, 103, 0.25) !important;"
            "max-height: 85vh; overflow-y: auto;"
        )
    else:
        panel_style = "width: auto;"

    st.markdown(
        f"""
        <style>
        .st-key-ai_chat_widget {{
            position: fixed;
            bottom: 1.5rem;
            right: 1.5rem;
            z-index: 1000;
            {panel_style}
        }}
        /* Circular floating action button when collapsed */
        .st-key-chat_fab button {{
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 1.6rem;
            padding: 0;
            box-shadow: 0 6px 18px rgba(17, 63, 103, 0.35);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    widget = st.container(key="ai_chat_widget")
    with widget:
        if not chat_is_open:
            # Collapsed: show only the floating action button
            fab = st.container(key="chat_fab")
            with fab:
                if st.button("💬", help="Ask the AI Data Assistant"):
                    st.session_state.chat_open = True
                    st.rerun()
        else:
            # Expanded: header bar with a close control, then the chat panel
            head_l, head_r = st.columns([0.8, 0.2], vertical_alignment="center")
            head_l.markdown("#### 💬 AI Data Assistant")
            if head_r.button("✕", key="chat_close", help="Close assistant", use_container_width=True):
                st.session_state.chat_open = False
                st.rerun()

            if not api_key_configured:
                st.info(
                    "AI Assistant requires a valid API key. "
                    "Configure GEMINI_API_KEY in .streamlit/secrets.toml to enable."
                )
            else:
                _render_chat_panel(summary_kpis, country_kpis)