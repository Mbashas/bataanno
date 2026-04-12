"""
AI Insights Generation Module
Provides reusable functions for generating AI-powered insights across all dashboard pages
Uses Google Gemini API for intelligent analysis
"""

import streamlit as st
from typing import Dict, Any, Optional, List

# Try to import genai, but handle if not available
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None


def init_ai():
    """Initialize the Gemini AI client"""
    # Check if we've already determined AI is unavailable
    if st.session_state.get('_ai_disabled', False):
        return False
    
    if not GENAI_AVAILABLE:
        st.session_state['_ai_disabled'] = True
        return False
        
    try:
        if "GEMINI_API_KEY" not in st.secrets:
            st.session_state['_ai_disabled'] = True
            return False
        
        api_key = st.secrets["GEMINI_API_KEY"]
        if not api_key or api_key == "your_api_key_here":
            st.session_state['_ai_disabled'] = True
            return False
            
        genai.configure(api_key=api_key)
        return True
    except Exception:
        st.session_state['_ai_disabled'] = True
        return False


def is_ai_available():
    """Check if AI is available for generating insights"""
    return init_ai()


MODEL_NAME = "gemini-1.5-flash"


def _generate_insights(prompt: str, cache_key: str) -> Optional[str]:
    """
    Internal function to generate insights with caching
    
    Args:
        prompt: The full prompt to send to the AI
        cache_key: Unique key for caching results
        
    Returns:
        Generated insights text or None if failed
    """
    # Check if AI was disabled due to previous errors
    if st.session_state.get('_ai_disabled', False):
        return None
    
    if not is_ai_available():
        return None
    
    # Use session state for caching to persist across reruns
    if f"ai_cache_{cache_key}" in st.session_state:
        return st.session_state[f"ai_cache_{cache_key}"]
    
    # Check if this specific request already failed
    if f"ai_failed_{cache_key}" in st.session_state:
        return None
    
    try:
        model = genai.GenerativeModel(model_name=MODEL_NAME)
        response = model.generate_content(prompt)
        result = response.text
        
        # Cache the result
        st.session_state[f"ai_cache_{cache_key}"] = result
        return result
    except Exception as e:
        error_msg = str(e).lower()
        # If API key is invalid, disable AI for the session
        if 'api_key' in error_msg or 'invalid' in error_msg or '400' in error_msg:
            st.session_state['_ai_disabled'] = True
        else:
            # Mark this specific request as failed
            st.session_state[f"ai_failed_{cache_key}"] = True
        return None


def generate_access_insights(
    coverage_data: Dict[str, Any],
    zone_data: Dict[str, Any],
    country: Optional[str] = None
) -> str:
    """
    Generate AI insights for the Access domain
    
    Args:
        coverage_data: Water and sanitation coverage statistics
        zone_data: Zone-level coverage breakdown
        country: Optional country filter
    """
    context = f"""
You are a water sector analyst. Analyze this access data and provide actionable insights.

COVERAGE DATA:
- Water (Safely Managed): {coverage_data.get('water_safely_managed', 0):.1f}%
- Water (Basic): {coverage_data.get('water_basic', 0):.1f}%
- Sanitation (Safely Managed): {coverage_data.get('sanitation_safely_managed', 0):.1f}%
- Sanitation (Basic): {coverage_data.get('sanitation_basic', 0):.1f}%
- Total Population Served: {coverage_data.get('total_population', 0):,.0f}

ZONE ANALYSIS:
- Zones below 50% coverage: {zone_data.get('low_coverage_zones', 0)}
- Average coverage gap: {zone_data.get('avg_gap', 0):.1f}%
- Highest disparity zone: {zone_data.get('highest_disparity_zone', 'N/A')}

Country Context: {country if country else 'All Countries'}

Generate 3-4 concise bullet points:
• **Key Findings**: 1-2 critical data observations (with numbers)
• **Root Cause**: Main driver of underperformance
• **Priority Action**: Single most impactful intervention

Format as SHORT bullet points. Maximum 1-2 sentences each. No introductions or conclusions.
"""
    
    cache_key = f"access_{country}_{hash(str(coverage_data))}"
    return _generate_insights(context, cache_key)


def generate_finance_insights(
    finance_data: Dict[str, Any],
    country: Optional[str] = None
) -> str:
    """
    Generate AI insights for the Finance domain
    
    Args:
        finance_data: Financial metrics including OCCR, collection efficiency, etc.
        country: Optional country filter
    """
    context = f"""
You are a water utility financial analyst. Analyze this financial data and provide actionable insights.

FINANCIAL METRICS:
- Cost Recovery Ratio (OCCR): {finance_data.get('occr', 0):.1f}% (Target: ≥110%)
- Collection Efficiency: {finance_data.get('collection_efficiency', 0):.1f}% (Target: ≥95%)
- Total Revenue: {finance_data.get('total_revenue', 0):,.0f}
- Total Operating Expenses: {finance_data.get('total_opex', 0):,.0f}
- Operating Surplus/Deficit: {finance_data.get('surplus_deficit', 0):,.0f}
- Uncollected Revenue: {finance_data.get('uncollected', 0):,.0f}
- NRW Impact on Revenue: {finance_data.get('nrw_revenue_impact', 0):.1f}%

Country Context: {country if country else 'All Countries'}

Generate 3-4 concise bullet points:
• **Financial Status**: Key metric vs benchmark (1 sentence)
• **Primary Risk**: Biggest threat to sustainability
• **Action Required**: Single most impactful fix

Format as SHORT bullet points. Maximum 1-2 sentences each. Be specific with numbers. No introductions.
"""
    
    cache_key = f"finance_{country}_{hash(str(finance_data))}"
    return _generate_insights(context, cache_key)


def generate_production_insights(
    production_data: Dict[str, Any],
    country: Optional[str] = None
) -> str:
    """
    Generate AI insights for the Production domain
    
    Args:
        production_data: Production metrics including NRW, service hours, etc.
        country: Optional country filter
    """
    context = f"""
You are a water production operations analyst. Analyze this production data and provide actionable insights.

PRODUCTION METRICS:
- Total Production: {production_data.get('total_production_m3', 0)/1e6:.2f} million m³
- Daily Average: {production_data.get('daily_avg', 0):,.0f} m³
- Non-Revenue Water (NRW): {production_data.get('nrw', 0):.1f}% (Target: ≤25%)
- Average Service Hours: {production_data.get('avg_service_hours', 0):.1f} hrs/day (Target: ≥20 hrs)
- Capacity Utilization: {production_data.get('capacity_utilization', 0):.1f}%
- Water Sources: {production_data.get('source_count', 0)}
- Sources Below Benchmark: {production_data.get('low_service_sources', 0)}

Country Context: {country if country else 'All Countries'}

Generate 3-4 concise bullet points:
• **Performance**: Key metric vs target (1 sentence)
• **Loss Driver**: Primary source of NRW or inefficiency
• **Quick Win**: Most impactful operational fix

Format as SHORT bullet points. Maximum 1-2 sentences each. Reference specific metrics. No introductions.
"""
    
    cache_key = f"production_{country}_{hash(str(production_data))}"
    return _generate_insights(context, cache_key)


def generate_service_insights(
    service_data: Dict[str, Any],
    country: Optional[str] = None
) -> str:
    """
    Generate AI insights for the Service domain
    
    Args:
        service_data: Service quality metrics including complaints, water quality, etc.
        country: Optional country filter
    """
    context = f"""
You are a water service quality analyst. Analyze this service data and provide actionable insights.

SERVICE QUALITY METRICS:
- Chlorine Test Compliance: {service_data.get('chlorine_compliance', 0):.1f}% (Target: ≥95%)
- E.coli Test Compliance: {service_data.get('ecoli_compliance', 0):.1f}% (Target: ≥95%)
- Metering Ratio: {service_data.get('metering_ratio', 0):.1f}% (Target: ≥95%)
- Complaint Resolution Rate: {service_data.get('resolution_rate', 0):.1f}% (Target: ≥90%)
- Total Complaints: {service_data.get('total_complaints', 0):,.0f}
- Unresolved Complaints: {service_data.get('unresolved', 0):,.0f}
- Wastewater Treatment Rate: {service_data.get('treatment_rate', 0):.1f}%

Country Context: {country if country else 'All Countries'}

Generate 3-4 concise bullet points:
• **Quality Status**: Key compliance metric vs 95% target
• **Service Gap**: Biggest customer issue or infrastructure need
• **Priority Fix**: Most impactful service improvement

Format as SHORT bullet points. Maximum 1-2 sentences each. Be specific with data. No introductions.
"""
    
    cache_key = f"service_{country}_{hash(str(service_data))}"
    return _generate_insights(context, cache_key)


def render_ai_insights(insights: Optional[str], section_title: str = "💡 Key Insights"):
    """
    Render AI insights - ONLY shows content if AI generated it
    
    Args:
        insights: AI-generated insights or None
        section_title: Header for the insights section
    """
    if insights:
        st.subheader(section_title)
        # Use markdown for proper bullet point rendering
        st.markdown(insights)
    # If no AI insights, show nothing - no fallback content


def clear_insights_cache(domain: Optional[str] = None):
    """
    Clear cached insights for a specific domain or all domains
    
    Args:
        domain: Optional domain name (access, finance, production, service) or None for all
    """
    keys_to_remove = []
    for key in st.session_state:
        if key.startswith("ai_cache_"):
            if domain is None or key.startswith(f"ai_cache_{domain}"):
                keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del st.session_state[key]

