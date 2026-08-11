"""
Inline SVG country flags
========================

Regional-indicator emoji (🇺🇬 🇲🇼 🇱🇸 🇨🇲) do NOT render on Windows: the OS
ships no glyphs for them, so Chrome, Edge and Firefox on Windows fall back to
showing the two letters ("UG", "MW", ...) in tofu boxes. macOS, iOS and Android
render them fine, which is why this only breaks on some machines.

These inline SVGs render identically everywhere, need no font, and make no
external requests (nothing to block or fail to load).

Each flag is sized in `em`, so it inherits whatever `font-size` the call site
already sets — the SVG drops straight in where the emoji used to be, with no
styling changes needed.

Emblem geometry (sun rays, star points) is computed with `math` rather than
hand-typed, so the shapes are symmetric by construction.
"""

import math

# All four flags are drawn to the same 3:2 box so they line up in a row.
_W, _H = 60.0, 40.0
_VIEWBOX = f"0 0 {_W:g} {_H:g}"


def _wrap(body, title):
    """Wrap flag shapes in a self-sizing, accessible <svg>."""
    return (
        f'<svg viewBox="{_VIEWBOX}" role="img" aria-label="{title} flag" '
        f'style="width:1.5em;height:1em;vertical-align:-0.15em;border-radius:2px;'
        f'box-shadow:0 0 0 1px rgba(0,0,0,0.12);display:inline-block;">'
        f'<title>{title}</title>{body}</svg>'
    )


def _bands_h(colors):
    """Equal horizontal bands, top to bottom."""
    n = len(colors)
    h = _H / n
    return "".join(
        f'<rect x="0" y="{i * h:.4g}" width="{_W:g}" height="{h:.4g}" fill="{c}"/>'
        for i, c in enumerate(colors)
    )


def _bands_v(colors):
    """Equal vertical bands, left to right."""
    n = len(colors)
    w = _W / n
    return "".join(
        f'<rect x="{i * w:.4g}" y="0" width="{w:.4g}" height="{_H:g}" fill="{c}"/>'
        for i, c in enumerate(colors)
    )


def _star(cx, cy, outer, fill, points=5):
    """A regular n-pointed star, first point straight up."""
    inner = outer * 0.382  # golden-ratio waist, the standard 5-point star look
    coords = []
    for i in range(points * 2):
        r = outer if i % 2 == 0 else inner
        # -90deg puts the first point at the top; SVG y grows downward.
        a = math.radians(-90 + i * 180.0 / points)
        coords.append(f"{cx + r * math.cos(a):.3f},{cy + r * math.sin(a):.3f}")
    return f'<polygon fill="{fill}" points="{" ".join(coords)}"/>'


def _rising_sun(cx, cy, disc_r, ray_in, ray_out, color, rays=13):
    """A disc with straight rays fanning across the upper half."""
    out = [f'<circle cx="{cx:g}" cy="{cy:g}" r="{disc_r:g}" fill="{color}"/>']
    for i in range(rays):
        # 180deg..360deg sweeps the upper half (SVG y grows downward).
        a = math.radians(180 + i * (180.0 / (rays - 1)))
        ca, sa = math.cos(a), math.sin(a)
        out.append(
            f'<line x1="{cx + ray_in * ca:.3f}" y1="{cy + ray_in * sa:.3f}" '
            f'x2="{cx + ray_out * ca:.3f}" y2="{cy + ray_out * sa:.3f}" '
            f'stroke="{color}" stroke-width="0.9" stroke-linecap="round"/>'
        )
    return "".join(out)


# --- Uganda: six bands (black, yellow, red, black, yellow, red) + white disc
# bearing the grey crowned crane.
_UGANDA = _wrap(
    _bands_h(["#000000", "#FCDC04", "#D90000", "#000000", "#FCDC04", "#D90000"])
    + '<circle cx="30" cy="20" r="7.2" fill="#FFFFFF"/>'
    # Simplified crowned crane, kept well inside the disc (x 22.8-37.2, y 12.8-27.2).
    + '<g fill="#9C9C9C">'
      '<ellipse cx="30.8" cy="21.6" rx="3.4" ry="2.0"/>'
      '<path d="M28.9 20.6 L27.6 17.0 L28.8 16.7 L30.1 20.3 Z"/>'
      '<circle cx="27.4" cy="16.3" r="1.1"/>'
      '<rect x="29.9" y="23.4" width="0.55" height="2.0"/>'
      '<rect x="31.7" y="23.4" width="0.55" height="2.0"/>'
      '</g>'
      '<path d="M26.4 15.5 L25.3 13.9 L27.0 14.7 Z" fill="#111111"/>'
      '<path d="M26.4 16.6 L25.0 17.0 L26.5 17.4 Z" fill="#D90000"/>',
    "Uganda",
)


# --- Malawi: black / red / green bands with the red rising sun on the black band.
_MALAWI = _wrap(
    _bands_h(["#000000", "#CE1126", "#339E35"])
    + _rising_sun(cx=30, cy=11.2, disc_r=3.3, ray_in=4.2, ray_out=6.6, color="#CE1126"),
    "Malawi",
)


# --- Lesotho: blue / white / green in 3:4:3 with a black mokorotlo hat centred.
_LESOTHO = _wrap(
    f'<rect x="0" y="0" width="{_W:g}" height="12" fill="#00209F"/>'
    f'<rect x="0" y="12" width="{_W:g}" height="16" fill="#FFFFFF"/>'
    f'<rect x="0" y="28" width="{_W:g}" height="12" fill="#009543"/>'
    # Mokorotlo (conical straw hat): brim, cone, finial.
    '<g fill="#111111">'
    '<path d="M23.6 25.6 Q30 27.5 36.4 25.6 Q30 24.3 23.6 25.6 Z"/>'
    '<path d="M26.3 25.2 Q30 16.0 33.7 25.2 Z"/>'
    '<path d="M29.5 16.6 L30 14.2 L30.5 16.6 Z"/>'
    '</g>',
    "Lesotho",
)


# --- Cameroon: green / red / yellow vertical bands with the yellow star.
_CAMEROON = _wrap(
    _bands_v(["#007A5E", "#CE1126", "#FCD116"])
    + _star(cx=30, cy=20, outer=6.2, fill="#FCD116"),
    "Cameroon",
)


# --- Neutral fallback for a country without a drawn flag (replaces the 🌍 default).
_GENERIC = _wrap(
    f'<rect x="0" y="0" width="{_W:g}" height="{_H:g}" fill="#58A0C8"/>'
    '<g fill="none" stroke="#FFFFFF" stroke-width="1.5">'
    '<circle cx="30" cy="20" r="11"/>'
    '<ellipse cx="30" cy="20" rx="4.6" ry="11"/>'
    '<path d="M19 20 H41 M21.2 13.6 H38.8 M21.2 26.4 H38.8"/>'
    '</g>',
    "Country",
)


FLAG_SVGS = {
    'Uganda': _UGANDA,
    'Malawi': _MALAWI,
    'Lesotho': _LESOTHO,
    'Cameroon': _CAMEROON,
}


def get_flag_svg(country):
    """
    Return an inline SVG flag for `country`, sized in `em`.

    Drop it into markup wherever a flag emoji used to sit — it inherits the
    surrounding `font-size`, so existing styling keeps working unchanged.
    Unknown countries get a neutral globe rather than an empty gap.
    """
    return FLAG_SVGS.get(country, _GENERIC)
