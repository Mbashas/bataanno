"""
Floating AI Chat Assistant
==========================

The chat bubble used to live inside `page_modules/overview.py`. That caused two
problems reported during UAT:

1. It vanished on every other tab — Streamlit renders inactive tab panels with
   `display: none`, so a bubble anchored inside the Overview panel is hidden
   whenever another tab is active.
2. It only ever received the Overview scorecard KPIs, so questions about
   metering ratio, water quality, JMP ladders, payment risk, wastewater and so
   on were answered with "I do not have data on that within the provided
   context."

The widget now lives here so `app.py` can render it ONCE per country dashboard,
outside the tab container: the bubble is visible on every tab and the model is
handed the full cross-domain snapshot built by `utils.ai_context`.
"""

import streamlit as st

from utils.ai_context import get_dashboard_context

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None


MODEL_NAME = "gemini-2.5-flash"

# Values that mean "nobody filled this in yet". Treated as no key at all, so the
# panel shows a clear "not configured" note instead of failing on first message.
PLACEHOLDER_KEYS = {"your_api_key_here", "api_key", "api_key_here", "changeme"}

SUGGESTED_PROMPTS = [
    "What is the biggest operational challenge right now?",
    "How is our metering ratio, and which zones are worst?",
    "Which zones have the weakest revenue collection?",
]


def is_chat_available():
    """
    Configure Gemini once per session and report whether the chat can run.

    Returns False when the library is missing, no `GEMINI_API_KEY` is set, or
    the key is still the placeholder — the dashboard then simply shows a short
    "not configured" note instead of a broken chat.
    """
    cached = st.session_state.get('_chat_ready')
    if cached is not None:
        return cached

    ready = False
    if GENAI_AVAILABLE:
        try:
            api_key = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else None
            if api_key and str(api_key).strip().lower() not in PLACEHOLDER_KEYS:
                genai.configure(api_key=api_key)
                ready = True
        except Exception:
            ready = False

    st.session_state['_chat_ready'] = ready
    return ready


def build_system_prompt(context_text, scope_label):
    """
    Wrap the dashboard data snapshot in the assistant's operating instructions.

    `context_text` covers every domain (Overview, Production, Service, Access,
    Finance) — see `utils.ai_context.build_dashboard_context`.
    """
    return f"""
You are an expert Water Sector Performance Analyst assisting users of a WASH
performance dashboard. The current selection is: {scope_label}.

You have been given a complete snapshot of the dashboard's data below, covering
ALL FIVE domains — Overview, Production, Service, Access and Finance — plus a
per-country breakdown and the app's navigation structure. Answer questions using
that snapshot.

{context_text}

RULES:
1. Answer concisely and professionally, and always quote the specific numbers
   from the snapshot that support your answer.
2. The snapshot spans every dashboard tab. Before saying a metric is
   unavailable, look for it under EVERY section heading above — for example
   metering ratio and water quality sit under "Service Quality", the JMP
   ladders under "Access & Equity", payment risk under "Finance", and service
   hours and the water balance under "Production".
3. Only if a figure genuinely does not appear anywhere above, say so plainly and
   name the tab or dataset where the user would normally find it.
4. When the user asks where to find something, use the "Dashboard Navigation"
   section to point them at the right tab.
5. When a metric has a benchmark or target, compare the actual value against it
   and say whether it passes.
6. All monetary values are in the local currency of the selected country unless
   the snapshot states otherwise. Never invent exchange rates.
7. Do not invent, extrapolate or estimate figures that are not in the snapshot.
8. Detect the language of the user's question and reply entirely in that
   language.
"""


def get_chat_session(system_prompt):
    """Start a Gemini chat session carrying the dashboard context."""
    if not is_chat_available():
        return None, None
    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=system_prompt,
        )
        return model.start_chat(history=[]), system_prompt
    except Exception as exc:
        st.error(f"Error initializing chat session: {exc}")
        return None, None


def _render_chat_panel(system_prompt):
    """
    Render the inner chat experience — history, suggested prompts, input box and
    transcript export — for the floating AI Data Assistant.
    """
    # Rebuild the session whenever the underlying data context changes
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
    # NOTE: `bool(...)` matters. Without it, `[] and ...` evaluates to the
    # session-state list ITSELF, and appending the welcome message below then
    # makes that same object truthy — which used to fire a Gemini call with the
    # assistant's own greeting as the prompt on every first render.
    is_waiting_for_response = (
        bool(st.session_state.messages)
        and st.session_state.messages[-1]["role"] == "user"
    )

    # Seed a short welcome the first time the panel opens. Kept to one line —
    # the suggestion chips below double as examples, so no need to list them.
    if not st.session_state.messages:
        st.session_state.messages.append(
            {"role": "assistant",
             "content": "👋 Hi! I can analyze data from every tab — Overview, Production, "
                        "Service, Access and Finance. Ask me anything, or tap a suggestion below."}
        )

    # --- Chat history (scrollable, sized to fit the floating panel) ---
    chat_history_container = st.container(height=300, border=True)
    with chat_history_container:
        for message in st.session_state.messages:
            avatar = "🤖" if message["role"] == "assistant" else "👤"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

    prompt = None

    # --- Suggested prompts (only before the conversation starts) ---
    conversation_started = any(m["role"] == "user" for m in st.session_state.messages)
    if not conversation_started and not is_waiting_for_response:
        for i, prompt_text in enumerate(SUGGESTED_PROMPTS):
            if st.button(prompt_text, use_container_width=True, key=f"suggested_btn_{i}"):
                st.session_state.input_prompt = prompt_text
                st.rerun()

    # --- Capture prompt: suggested button OR the chat input box ---
    if st.session_state.get("input_prompt"):
        prompt = st.session_state.input_prompt
        del st.session_state.input_prompt
    elif not is_waiting_for_response:
        submitted_prompt = st.chat_input("Ask me about production, service, access or finance...")
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


def render_floating_chat(data, countries_filter=None):
    """
    Render the floating AI chat bubble for the whole dashboard.

    Call this ONCE per page render, OUTSIDE any `st.tabs` container — the bubble
    is `position: fixed`, so an ancestor tab panel being hidden would hide it
    too. Rendering it once also keeps the widget keys unique.

    Args:
        data: dict of already-filtered dataframes (from `apply_filters`).
        countries_filter: optional list of countries in scope.
    """
    # Built on st.popover: open/close happens client-side (no rerun, so no
    # transition flashes), the panel renders in Streamlit's overlay layer (it
    # cannot scatter into the page flow), and a popover is a supported inline
    # location for st.chat_input (a bare container is not — that's what caused
    # the input to escape and pin itself full-width to the page bottom).
    st.markdown(
        """
        <style>
        /* Pin just the popover trigger to the bottom-right corner,
           raised above the Streamlit footer / branding strip */
        .st-key-chat_popover {
            position: fixed;
            bottom: 4rem;
            right: 1.5rem;
            z-index: 999999;
            width: fit-content !important;
        }
        /* Style the trigger as a circular chat bubble */
        .st-key-chat_popover button {
            border-radius: 50%;
            width: 56px;
            height: 56px;
            font-size: 1.5rem;
            padding: 0;
            box-shadow: 0 2px 8px rgba(17, 63, 103, 0.35);
        }
        /* Give the panel content a chat-window width */
        .st-key-chat_panel {
            width: min(400px, 85vw);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    anchor = st.container(key="chat_popover")
    with anchor:
        with st.popover("💬", help="Ask the AI Data Assistant"):
            panel = st.container(key="chat_panel")
            with panel:
                st.markdown("#### 💬 AI Data Assistant")
                if not is_chat_available():
                    st.info(
                        "AI Assistant requires a valid API key. "
                        "Configure GEMINI_API_KEY in .streamlit/secrets.toml to enable."
                    )
                    return

                scope_label = ", ".join(countries_filter) if countries_filter else "All countries"
                context_text = get_dashboard_context(data, countries_filter)
                _render_chat_panel(build_system_prompt(context_text, scope_label))
