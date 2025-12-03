"""
Currency Configuration Module
Defines currency symbols, divisors, and formatting for each country
Includes USD conversion support with exchange rates
"""

import streamlit as st

# Exchange rates to USD (as of December 2025 - approximate rates)
# These are static rates - update periodically for accuracy
EXCHANGE_RATES_TO_USD = {
    'UGX': 0.00027,    # 1 UGX = 0.00027 USD (1 USD ≈ 3,700 UGX)
    'XAF': 0.0016,     # 1 XAF = 0.0016 USD (1 USD ≈ 625 XAF)
    'LSL': 0.055,      # 1 LSL = 0.055 USD (1 USD ≈ 18 LSL)
    'MWK': 0.00058,    # 1 MWK = 0.00058 USD (1 USD ≈ 1,725 MWK)
    'LCU': 1.0,        # Default: assume 1:1 for unknown currencies
}

# Last update date for exchange rates
EXCHANGE_RATE_DATE = "December 2025"

# USD display configuration
USD_CONFIG = {
    'symbol': 'USD',
    'name': 'US Dollar',
    'divisor': 1e6,  # Display in millions
    'suffix': 'M',
    'decimal_places': 2
}

# Currency configuration for each country
CURRENCY_CONFIG = {
    'Uganda': {
        'symbol': 'UGX',
        'name': 'Ugandan Shilling',
        'divisor': 1e9,  # Display in billions
        'suffix': 'B',
        'decimal_places': 2
    },
    'Cameroon': {
        'symbol': 'XAF',
        'name': 'Central African CFA Franc',
        'divisor': 1e9,  # Display in billions
        'suffix': 'B',
        'decimal_places': 2
    },
    'Lesotho': {
        'symbol': 'LSL',
        'name': 'Lesotho Loti',
        'divisor': 1e9,  # Display in billions
        'suffix': 'B',
        'decimal_places': 2
    },
    'Malawi': {
        'symbol': 'MWK',
        'name': 'Malawian Kwacha',
        'divisor': 1e9,  # Display in billions
        'suffix': 'B',
        'decimal_places': 2
    }
}

# Default configuration for unknown countries
DEFAULT_CONFIG = {
    'symbol': 'LCU',  # Local Currency Units
    'name': 'Local Currency',
    'divisor': 1e6,
    'suffix': 'M',
    'decimal_places': 1
}


def get_currency_config(country):
    """
    Get currency configuration for a country
    
    Args:
        country (str): Country name
    
    Returns:
        dict: Currency configuration
    """
    return CURRENCY_CONFIG.get(country, DEFAULT_CONFIG)


def format_currency(value, country, include_symbol=True, decimal_places=None):
    """
    Format a monetary value with appropriate currency symbol and scale
    
    Args:
        value (float): Raw value in local currency
        country (str): Country name
        include_symbol (bool): Whether to include currency symbol
        decimal_places (int): Override default decimal places
    
    Returns:
        str: Formatted currency string (e.g., "15.5B UGX")
    """
    config = get_currency_config(country)
    
    # Scale the value
    scaled_value = value / config['divisor']
    
    # Determine decimal places
    decimals = decimal_places if decimal_places is not None else config['decimal_places']
    
    # Format the value
    if include_symbol:
        return f"{scaled_value:,.{decimals}f}{config['suffix']} {config['symbol']}"
    else:
        return f"{scaled_value:,.{decimals}f}{config['suffix']}"


def format_currency_multi_country(value, countries, include_symbol=True):
    """
    Format currency when multiple countries are selected
    
    Args:
        value (float): Aggregate value
        countries (list): List of country names
        include_symbol (bool): Whether to include currency indicator
    
    Returns:
        str: Formatted string with appropriate indicator
    """
    if not countries or len(countries) == 0:
        # No countries selected - use default
        config = DEFAULT_CONFIG
        scaled_value = value / config['divisor']
        if include_symbol:
            return f"{scaled_value:,.1f}{config['suffix']} {config['symbol']}"
        else:
            return f"{scaled_value:,.1f}{config['suffix']}"
    
    elif len(countries) == 1:
        # Single country - use specific currency
        return format_currency(value, countries[0], include_symbol)
    
    else:
        # Multiple countries - indicate mixed currencies
        # Use the first country's divisor for scaling but indicate mixed
        config = get_currency_config(countries[0])
        scaled_value = value / config['divisor']
        
        if include_symbol:
            # Get all unique currency symbols
            symbols = sorted(set(CURRENCY_CONFIG.get(c, DEFAULT_CONFIG)['symbol'] for c in countries))
            symbol_str = '/'.join(symbols)
            return f"{scaled_value:,.1f}{config['suffix']} ({symbol_str})"
        else:
            return f"{scaled_value:,.1f}{config['suffix']} (Mixed)"


def get_currency_label(country):
    """
    Get a descriptive currency label for display
    
    Args:
        country (str): Country name
    
    Returns:
        str: Currency label (e.g., "UGX (Ugandan Shilling)")
    """
    config = get_currency_config(country)
    return f"{config['symbol']} ({config['name']})"


# ============================================================================
# USD CONVERSION FUNCTIONS
# ============================================================================

def is_usd_mode():
    """
    Check if USD conversion mode is enabled
    
    Returns:
        bool: True if USD mode is active
    """
    return st.session_state.get('currency_mode', 'local') == 'usd'


def get_exchange_rate(country):
    """
    Get the exchange rate to USD for a country's currency
    
    Args:
        country (str): Country name
    
    Returns:
        float: Exchange rate (local currency to USD)
    """
    config = get_currency_config(country)
    symbol = config['symbol']
    return EXCHANGE_RATES_TO_USD.get(symbol, 1.0)


def convert_to_usd(value, country):
    """
    Convert a value from local currency to USD
    
    Args:
        value (float): Value in local currency
        country (str): Country name
    
    Returns:
        float: Value in USD
    """
    rate = get_exchange_rate(country)
    return value * rate


def format_usd(value, decimal_places=2):
    """
    Format a value as USD with appropriate scaling
    
    Args:
        value (float): Value in USD
        decimal_places (int): Number of decimal places
    
    Returns:
        str: Formatted USD string (e.g., "$15.5M")
    """
    config = USD_CONFIG
    scaled_value = value / config['divisor']
    return f"${scaled_value:,.{decimal_places}f}{config['suffix']}"


def format_currency_auto(value, countries, include_symbol=True):
    """
    Format currency based on current mode (local or USD)
    Automatically checks session state for currency_mode
    
    Args:
        value (float): Raw value in local currency
        countries (list): List of country names (for context)
        include_symbol (bool): Whether to include currency symbol
    
    Returns:
        str: Formatted currency string
    """
    if is_usd_mode():
        # Convert to USD
        if countries and len(countries) == 1:
            # Single country - convert using that country's rate
            usd_value = convert_to_usd(value, countries[0])
        elif countries and len(countries) > 1:
            # Multiple countries - use average rate or first country's rate
            # For aggregates, we use first country's rate as approximation
            usd_value = convert_to_usd(value, countries[0])
        else:
            # No country context - assume value is already in base units
            usd_value = value
        return format_usd(usd_value)
    else:
        # Use local currency formatting
        return format_currency_multi_country(value, countries, include_symbol)


def get_currency_mode_label():
    """
    Get a label describing the current currency mode
    
    Returns:
        str: Mode description
    """
    if is_usd_mode():
        return f"USD (Converted at rates from {EXCHANGE_RATE_DATE})"
    else:
        return "Local Currency"


def toggle_currency_mode():
    """Toggle between local currency and USD mode"""
    current = st.session_state.get('currency_mode', 'local')
    st.session_state.currency_mode = 'usd' if current == 'local' else 'local'

