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
        'decimal_places': 2,
        'locale': 'en_UG'  # Added for locale-specific formatting
    },
    'Cameroon': {
        'symbol': 'XAF',
        'name': 'Central African CFA Franc',
        'divisor': 1e9,  # Display in billions
        'suffix': 'B',
        'decimal_places': 2,
        'locale': 'fr_CM'
    },
    'Lesotho': {
        'symbol': 'LSL',
        'name': 'Lesotho Loti',
        'divisor': 1e9,  # Display in billions
        'suffix': 'B',
        'decimal_places': 2,
        'locale': 'en_LS'
    },
    'Malawi': {
        'symbol': 'MWK',
        'name': 'Malawian Kwacha',
        'divisor': 1e9,  # Display in billions
        'suffix': 'B',
        'decimal_places': 2,
        'locale': 'en_MW'
    }
}

# Default configuration for unknown countries
DEFAULT_CONFIG = {
    'symbol': 'LCU',  # Local Currency Units
    'name': 'Local Currency',
    'divisor': 1e6,
    'suffix': 'M',
    'decimal_places': 1,
    'locale': 'en_US'
}

# Supported scales for dynamic formatting
SCALE_CONFIGS = {
    'T': 1e12,  # Trillions
    'B': 1e9,   # Billions
    'M': 1e6,   # Millions
    'K': 1e3,   # Thousands
    '': 1       # Units
}

def get_currency_config(country):
    """
    Get currency configuration for a country
    
    Args:
        country (str): Country name
    
    Returns:
        dict: Currency configuration
    
    Raises:
        TypeError: If country is not a string
    """
    if not isinstance(country, str):
        raise TypeError(f"Country must be a string, got {type(country)}")
    
    country_normalized = country.strip().title()
    return CURRENCY_CONFIG.get(country_normalized, DEFAULT_CONFIG.copy())

def format_currency(value, country, include_symbol=True, decimal_places=None, auto_scale=False):
    """
    Format a monetary value with appropriate currency symbol and scale
    
    Args:
        value (float): Raw value in local currency
        country (str): Country name
        include_symbol (bool): Whether to include currency symbol
        decimal_places (int): Override default decimal places
        auto_scale (bool): Automatically choose appropriate scale (B/M/K)
    
    Returns:
        str: Formatted currency string (e.g., "15.5B UGX")
    
    Raises:
        ValueError: If value is not numeric
    """
    if not isinstance(value, (int, float)):
        raise ValueError(f"Value must be numeric, got {type(value)}")
    
    config = get_currency_config(country)
    
    # Handle auto-scaling
    if auto_scale:
        scaled_value, suffix = _auto_scale_value(value)
    else:
        scaled_value = value / config['divisor']
        suffix = config['suffix']
    
    # Determine decimal places
    decimals = decimal_places if decimal_places is not None else config['decimal_places']
    
    # Format based on magnitude for cleaner output
    if abs(scaled_value) < 0.01 and scaled_value != 0:
        # Use scientific notation for very small values
        formatted_value = f"{scaled_value:.2e}"
    elif abs(scaled_value) < 1:
        # More decimals for small values
        decimals = max(decimals, 3)
        formatted_value = f"{scaled_value:,.{decimals}f}"
    elif abs(scaled_value) >= 1000:
        # Use thousands separator for large values
        formatted_value = f"{scaled_value:,.0f}"
    else:
        # Standard formatting
        formatted_value = f"{scaled_value:,.{decimals}f}"
    
    # Build the final string
    if include_symbol:
        return f"{formatted_value}{suffix} {config['symbol']}"
    else:
        return f"{formatted_value}{suffix}"

def _auto_scale_value(value):
    """
    Automatically determine the best scale for a value
    
    Args:
        value (float): Raw numeric value
    
    Returns:
        tuple: (scaled_value, suffix)
    """
    abs_value = abs(value)
    
    for suffix, divisor in SCALE_CONFIGS.items():
        if abs_value >= divisor or divisor == 1:  # Always match at least the unit scale
            scaled = value / divisor
            # Only use this scale if the result is reasonably sized or it's the smallest scale
            if 0.1 <= abs(scaled) < 10000 or divisor == 1:
                return scaled, suffix
    
    # Fallback to scientific notation for very small values
    return value, ''

def format_currency_multi_country(value, countries, include_symbol=True, auto_scale=False):
    """
    Format currency when multiple countries are selected
    
    Args:
        value (float): Aggregate value
        countries (list): List of country names
        include_symbol (bool): Whether to include currency indicator
        auto_scale (bool): Automatically choose appropriate scale
    
    Returns:
        str: Formatted string with appropriate indicator
    """
    if not countries:
        # No countries selected - use default
        config = DEFAULT_CONFIG
        if auto_scale:
            scaled_value, suffix = _auto_scale_value(value)
        else:
            scaled_value = value / config['divisor']
            suffix = config['suffix']
        
        if include_symbol:
            return f"{scaled_value:,.1f}{suffix} {config['symbol']}"
        else:
            return f"{scaled_value:,.1f}{suffix}"
    
    elif len(countries) == 1:
        # Single country - use specific currency
        return format_currency(value, countries[0], include_symbol, auto_scale=auto_scale)
    
    else:
        # Multiple countries - indicate mixed currencies
        # Use the first country's divisor for scaling but indicate mixed
        config = get_currency_config(countries[0])
        
        if auto_scale:
            scaled_value, suffix = _auto_scale_value(value)
        else:
            scaled_value = value / config['divisor']
            suffix = config['suffix']
        
        if include_symbol:
            # Get all unique currency symbols
            symbols = sorted(set(get_currency_config(c)['symbol'] for c in countries))
            symbol_str = '/'.join(symbols)
            return f"{scaled_value:,.1f}{suffix} ({symbol_str})"
        else:
            return f"{scaled_value:,.1f}{suffix} (Mixed)"

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

def get_available_countries():
    """
    Get list of all available countries with currency configurations
    
    Returns:
        list: Sorted list of country names
    """
    return sorted(CURRENCY_CONFIG.keys())

def validate_currency_config():
    """
    Validate that all currency configurations are properly defined
    
    Returns:
        dict: Validation results with any issues found
    """
    required_keys = {'symbol', 'name', 'divisor', 'suffix', 'decimal_places'}
    issues = {}
    
    for country, config in CURRENCY_CONFIG.items():
        missing_keys = required_keys - set(config.keys())
        if missing_keys:
            issues[country] = f"Missing keys: {missing_keys}"
        
        # Validate divisor is positive
        if config.get('divisor', 0) <= 0:
            issues[country] = "Divisor must be positive"
    
    return issues

# Example usage and testing
if __name__ == "__main__":
    # Test the functions
    test_value = 1500000000  # 1.5 billion
    
    print("Currency Formatting Examples:")
    print(f"Uganda: {format_currency(test_value, 'Uganda')}")
    print(f"Cameroon: {format_currency(test_value, 'Cameroon')}")
    print(f"Auto-scale (large): {format_currency(2500000, 'Uganda', auto_scale=True)}")
    print(f"Auto-scale (small): {format_currency(1500, 'Uganda', auto_scale=True)}")
    
    print(f"\nMulti-country:")
    print(f"Single: {format_currency_multi_country(test_value, ['Uganda'])}")
    print(f"Multiple: {format_currency_multi_country(test_value, ['Uganda', 'Cameroon'])}")
    
    # Validate configuration
    validation_issues = validate_currency_config()
    if validation_issues:
        print(f"\nConfiguration issues: {validation_issues}")
    else:
        print("\n✓ All currency configurations are valid")