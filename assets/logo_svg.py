"""
Custom SVG Logo for WASH Dashboard
Professional water services branding
"""

def get_wash_logo_svg(size=48, color="#FFFFFF"):
    """
    Generate a professional WASH logo SVG
    Simple, clean water drop with waves design
    
    Args:
        size: Logo size in pixels
        color: Primary color for the logo
    
    Returns:
        str: SVG markup (single line to prevent markdown parsing issues)
    """
    # Keep SVG on single line to prevent Streamlit markdown parsing issues
    return f'<svg width="{size}" height="{size}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="46" fill="none" stroke="{color}" stroke-width="2" opacity="0.3"/><path d="M50 20 C50 20 25 50 25 65 C25 80 35 90 50 90 C65 90 75 80 75 65 C75 50 50 20 50 20Z" fill="{color}" opacity="0.9"/><path d="M35 75 Q45 70 55 75 T75 75" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" opacity="0.5"/></svg>'


def get_wash_logo_colored_svg(size=48):
    """
    Generate a colored version of WASH logo (for light backgrounds)
    
    Args:
        size: Logo size in pixels
    
    Returns:
        str: SVG markup
    """
    return f'<svg width="{size}" height="{size}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="wash-grad" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" style="stop-color:#113F67"/><stop offset="100%" style="stop-color:#58A0C8"/></linearGradient></defs><circle cx="50" cy="50" r="46" fill="none" stroke="url(#wash-grad)" stroke-width="2" opacity="0.3"/><path d="M50 20 C50 20 25 50 25 65 C25 80 35 90 50 90 C65 90 75 80 75 65 C75 50 50 20 50 20Z" fill="url(#wash-grad)"/><path d="M35 75 Q45 70 55 75 T75 75" fill="none" stroke="#58A0C8" stroke-width="2" stroke-linecap="round" opacity="0.6"/></svg>'


def get_login_illustration_svg():
    """
    Generate a simple illustration for the login page
    
    Returns:
        str: SVG markup
    """
    return '<svg width="300" height="200" viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg"><circle cx="60" cy="60" r="40" fill="#58A0C8" opacity="0.1"/><circle cx="240" cy="140" r="50" fill="#113F67" opacity="0.1"/><rect x="100" y="80" width="100" height="60" rx="8" fill="#FFFFFF" opacity="0.15"/><path d="M120 110 L140 95 L160 105 L180 90" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.6"/><circle cx="150" cy="50" r="20" fill="#58A0C8" opacity="0.3"/><path d="M150 35 L150 30 M140 40 L135 35 M160 40 L165 35" stroke="#FFFFFF" stroke-width="2" opacity="0.5"/></svg>'
