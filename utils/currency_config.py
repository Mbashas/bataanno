"""
Currency Configuration Module
Defines currency symbols, divisors, and formatting for each country
"""

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

