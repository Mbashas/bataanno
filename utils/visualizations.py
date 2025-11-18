"""
Visualization Utilities Module
Reusable Plotly chart creation functions
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


# HIGH-CONTRAST COLOR PALETTE - WCAG AAA Compliant
# All colors chosen for maximum readability and accessibility
COLORS = {
    'good': '#198754',      # Dark green (WCAG AAA)
    'acceptable': '#fd7e14',  # Orange (WCAG AA)
    'poor': '#dc3545',      # Red (WCAG AAA)
    'primary': '#0056b3',   # Dark blue (WCAG AAA)
    'secondary': '#6f42c1',  # Purple (WCAG AA)
    'tertiary': '#0f6674',  # Dark teal (WCAG AAA)
    'text_dark': '#1e1e1e', # Almost black (text on light)
    'text_medium': '#333333', # Dark gray (general text)
    'text_light': '#ffffff', # White (text on dark - not used in light theme)
    'bg_light': '#ffffff',  # Pure white background
    'bg_card': '#f8f9fa',   # Light gray card background
    'bg_chart': '#ffffff',  # Chart background
    'border': '#dee2e6',    # Light border
    'grid': '#e9ecef',      # Grid lines
    'countries': {
        'Uganda': '#dc3545',   # Red
        'Cameroon': '#0056b3', # Blue
        'Lesotho': '#198754',  # Green
        'Malawi': '#fd7e14'    # Orange
    }
}

# STANDARD LAYOUT - Applied to ALL charts for consistency
# Ensures dark text on light background for maximum readability
STANDARD_LAYOUT = {
    'paper_bgcolor': COLORS['bg_chart'],
    'plot_bgcolor': COLORS['bg_chart'],
    'font': {
        'family': 'Arial, Helvetica, sans-serif',
        'size': 13,
        'color': COLORS['text_dark']
    },
    'title': {
        'font': {
            'size': 18,
            'color': COLORS['text_dark'],
            'family': 'Arial, Helvetica, sans-serif',
            'weight': 600
        },
        'x': 0.5,
        'xanchor': 'center'
    },
    'xaxis': {
        'title': {
            'font': {
                'color': COLORS['text_dark'],
                'size': 13,
                'weight': 600
            }
        },
        'tickfont': {
            'color': COLORS['text_dark'],
            'size': 12
        },
        'gridcolor': COLORS['grid'],
        'showgrid': True,
        'linecolor': COLORS['border']
    },
    'yaxis': {
        'title': {
            'font': {
                'color': COLORS['text_dark'],
                'size': 13,
                'weight': 600
            }
        },
        'tickfont': {
            'color': COLORS['text_dark'],
            'size': 12
        },
        'gridcolor': COLORS['grid'],
        'showgrid': True,
        'linecolor': COLORS['border']
    },
    'legend': {
        'font': {
            'color': COLORS['text_dark'],
            'size': 12
        },
        'bgcolor': 'rgba(255, 255, 255, 0.9)',
        'bordercolor': COLORS['border'],
        'borderwidth': 1
    },
    'margin': {'l': 60, 'r': 30, 't': 80, 'b': 60}
}

# Benchmark values
BENCHMARKS = {
    'water_coverage': 100,
    'sanitation_coverage': 100,
    'nrw': 25,
    'water_quality': 95,
    'service_hours': 20,
    'collection_efficiency': 95,
    'occr': 110,
    'metering_ratio': 95,
    'staff_productivity': 7
}


def create_kpi_card(title, value, benchmark, unit='%', inverse=False):
    """
    Create a KPI card with status indicator
    
    Args:
        title: KPI name
        value: Current value
        benchmark: Target benchmark
        unit: Unit of measurement
        inverse: If True, lower is better
    
    Returns:
        Plotly figure object
    """
    # Determine status
    if inverse:
        if value <= benchmark:
            color = COLORS['good']
            status = '✓ Good'
        elif value <= benchmark * 1.5:
            color = COLORS['acceptable']
            status = '⚠ Acceptable'
        else:
            color = COLORS['poor']
            status = '✗ Needs Attention'
    else:
        if value >= benchmark:
            color = COLORS['good']
            status = '✓ Good'
        elif value >= benchmark * 0.8:
            color = COLORS['acceptable']
            status = '⚠ Acceptable'
        else:
            color = COLORS['poor']
            status = '✗ Needs Attention'
    
    # Normalise unit formatting
    unit = unit or ''
    if unit and unit not in {'%'} and not unit.startswith(' '):
        unit_suffix = f" {unit}"
    else:
        unit_suffix = unit

    # Determine gauge range
    max_range = max(abs(value), abs(benchmark)) * 1.2
    if max_range == 0:
        max_range = benchmark * 1.5 if benchmark else 1
    max_range = max(max_range, benchmark * 1.5 if benchmark else 1)
    
    if inverse:
        steps = [
            {'range': [0, benchmark], 'color': "rgba(46, 204, 113, 0.15)"},
            {'range': [benchmark, benchmark * 1.5], 'color': "rgba(243, 156, 18, 0.15)"},
            {'range': [benchmark * 1.5, max_range], 'color': "rgba(231, 76, 60, 0.15)"}
        ]
        threshold_value = benchmark
        target_text = f"Benchmark: ≤{benchmark}{unit_suffix}"
    else:
        steps = [
            {'range': [0, benchmark * 0.8], 'color': "rgba(231, 76, 60, 0.15)"},
            {'range': [benchmark * 0.8, benchmark], 'color': "rgba(243, 156, 18, 0.15)"},
            {'range': [benchmark, max_range], 'color': "rgba(46, 204, 113, 0.15)"}
        ]
        threshold_value = benchmark
        target_text = f"Target: ≥{benchmark}{unit_suffix}"

    # Create gauge chart with improved styling
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={
            'text': f"<b>{title}</b>",
            'font': {'size': 14, 'color': COLORS['text_dark']}  # Dark, bold title
        },
        delta={
            'reference': benchmark,
            'font': {'size': 12},  # Smaller delta font
            'increasing': {'color': COLORS['good'] if not inverse else COLORS['poor']},
            'decreasing': {'color': COLORS['poor'] if not inverse else COLORS['good']},
            'valueformat': '.1f'
        },
        number={
            'suffix': unit_suffix,
            'font': {'size': 28, 'color': color},  # Reduced from 36 to 28
            'valueformat': '.1f'
        },
        gauge={
            'axis': {
                'range': [None, max_range],
                'tickwidth': 2,
                'tickcolor': COLORS['text_dark'],
                'tickfont': {'size': 12, 'color': COLORS['text_dark']}
            },
            'bar': {'color': color, 'thickness': 0.8},
            'bgcolor': 'rgba(240, 240, 240, 0.5)',
            'steps': steps,
            'threshold': {
                'line': {'color': COLORS['text_dark'], 'width': 3},
                'thickness': 0.8,
                'value': threshold_value
            }
        }
    ))
    
    fig.update_layout(
        height=200,  # Further reduced height to prevent overlapping
        margin=dict(l=15, r=15, t=40, b=15),  # Tighter margins
        paper_bgcolor=COLORS['bg_light'],
        plot_bgcolor=COLORS['bg_light'],
        font={'color': COLORS['text_dark'], 'family': 'Arial, sans-serif'},
        annotations=[
            dict(
                text=f"<b style='color:{COLORS['text_dark']}'>{status}</b><br><span style='color:#666666; font-size:9px'>{target_text}</span>",
                x=0.5, y=-0.08,
                showarrow=False,
                font=dict(size=10, color=COLORS['text_dark']),
                xanchor='center'
            )
        ]
    )
    
    # Force light template to ensure readability
    fig.update_layout(template='plotly_white')
    
    return fig


def create_trend_line(df, x_col, y_col, title, color=None, benchmark=None):
    """Create a line chart showing trends over time with high-contrast styling"""
    fig = px.line(
        df, 
        x=x_col, 
        y=y_col,
        title=title,
        color_discrete_sequence=[color or COLORS['primary']]
    )
    
    # Add benchmark line if provided
    if benchmark is not None:
        fig.add_hline(
            y=benchmark, 
            line_dash="dash", 
            line_color=COLORS['poor'],
            line_width=2,
            annotation_text=f"Benchmark: {benchmark}",
            annotation=dict(
                font=dict(color=COLORS['text_dark'], size=12)
            )
        )
    
    # Apply standard layout
    fig.update_layout(
        **STANDARD_LAYOUT,
        height=400,
        hovermode='x unified',
        xaxis_title=x_col.replace('_', ' ').title(),
        yaxis_title=y_col.replace('_', ' ').title()
    )
    
    return fig


def create_comparison_bar(df, x_col, y_col, title, color_col=None, orientation='v'):
    """Create bar chart for comparing values across categories with high-contrast styling"""
    fig = px.bar(
        df,
        x=x_col if orientation == 'v' else y_col,
        y=y_col if orientation == 'v' else x_col,
        title=title,
        color=color_col,
        color_discrete_map=COLORS['countries'] if color_col == 'country' else None,
        orientation=orientation
    )
    
    # Apply standard layout
    fig.update_layout(
        **STANDARD_LAYOUT,
        height=400,
        xaxis_title=x_col.replace('_', ' ').title(),
        yaxis_title=y_col.replace('_', ' ').title()
    )
    
    return fig


def create_waterfall_chart(categories, values, title, yaxis_title="Amount (Currency)"):
    """
    Create waterfall chart for financial flow visualization with high-contrast styling
    
    Args:
        categories: List of category names
        values: List of values (positive for additions, negative for subtractions)
        title: Chart title
    """
    fig = go.Figure(go.Waterfall(
        name="Financial Flow",
        orientation="v",
        measure=["relative"] * (len(categories) - 1) + ["total"],
        x=categories,
        y=values,
        connector={"line": {"color": COLORS['text_dark'], "width": 2}},
        decreasing={"marker": {"color": COLORS['poor']}},
        increasing={"marker": {"color": COLORS['good']}},
        totals={"marker": {"color": COLORS['primary']}},
        text=values,
        textposition="outside",
        textfont={"color": COLORS['text_dark'], "size": 12}
    ))
    
    # Create layout without conflicting keys
    layout = STANDARD_LAYOUT.copy()
    layout.update({
        'title': {'text': title, 'font': {'size': 18, 'color': COLORS['text_dark'], 'weight': 600}, 'x': 0.5, 'xanchor': 'center'},
        'height': 500,
        'showlegend': False,
        'xaxis_title': "",
        'yaxis_title': yaxis_title
    })
    fig.update_layout(**layout)
    
    return fig


def create_heatmap(df, x_col, y_col, value_col, title):
    """Create heatmap for visualizing values across two dimensions with high-contrast styling"""
    pivot_df = df.pivot_table(
        values=value_col,
        index=y_col,
        columns=x_col,
        aggfunc='mean'
    )
    
    fig = px.imshow(
        pivot_df,
        title=title,
        labels=dict(x=x_col.replace('_', ' ').title(), 
                   y=y_col.replace('_', ' ').title(), 
                   color=value_col.replace('_', ' ').title()),
        aspect="auto",
        color_continuous_scale='RdYlGn',
        text_auto='.1f'
    )
    
    # Apply standard layout
    fig.update_layout(
        **STANDARD_LAYOUT,
        height=400
    )
    
    # Ensure text is dark
    fig.update_traces(textfont=dict(color=COLORS['text_dark']))
    
    return fig


def create_scatter_plot(df, x_col, y_col, title, color_col=None, size_col=None):
    """Create scatter plot for correlation analysis with high-contrast styling"""
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        title=title,
        color=color_col,
        size=size_col,
        color_discrete_map=COLORS['countries'] if color_col == 'country' else None,
        hover_data=df.columns.tolist()
    )
    
    # Apply standard layout
    fig.update_layout(
        **STANDARD_LAYOUT,
        height=500,
        xaxis_title=x_col.replace('_', ' ').title(),
        yaxis_title=y_col.replace('_', ' ').title()
    )
    
    return fig


def create_stacked_area(df, x_col, y_cols, title):
    """Create stacked area chart for composition over time with high-contrast styling"""
    fig = go.Figure()
    
    for col in y_cols:
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[col],
            name=col.replace('_', ' ').title(),
            mode='lines',
            stackgroup='one',
            fillcolor=COLORS.get(col, None)
        ))
    
    # Apply standard layout
    fig.update_layout(
        **STANDARD_LAYOUT,
        title=title,
        height=400,
        hovermode='x unified',
        xaxis_title=x_col.replace('_', ' ').title(),
        yaxis_title="Value"
    )
    
    return fig


def create_occr_dashboard(finance_df):
    """
    Create comprehensive OCCR dashboard with 2x2 layout
    
    Args:
        finance_df: Financial data DataFrame
    
    Returns:
        Plotly figure with subplots
    """
    # Calculate OCCR by country
    country_occr = finance_df.groupby('country').agg({
        'sewer_revenue': 'sum',
        'opex': 'sum',
        'propoor_popn': 'sum'
    }).reset_index()
    country_occr['occr'] = (country_occr['sewer_revenue'] / country_occr['opex']) * 100
    
    # Create subplots (2x2)
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'OCCR by Country',
            'OCCR Trends (Country × Year)',
            'Revenue vs Operating Costs',
            'Pro-Poor Population vs OCCR'
        ),
        specs=[
            [{'type': 'bar'}, {'type': 'heatmap'}],
            [{'type': 'bar'}, {'type': 'scatter'}]
        ],
        vertical_spacing=0.20,  # Increased spacing
        horizontal_spacing=0.15  # Increased spacing
    )
    
    # Top Left: Bar chart instead of gauges for better readability
    fig.add_trace(
        go.Bar(
            x=country_occr['country'],
            y=country_occr['occr'],
            text=[f"{val:.1f}%" for val in country_occr['occr']],
            textposition='outside',
            marker=dict(
                color=[COLORS['good'] if val >= 110 else COLORS['acceptable'] if val >= 100 else COLORS['poor'] 
                       for val in country_occr['occr']]
            ),
            showlegend=False,
            hovertemplate="<b>%{x}</b><br>OCCR: %{y:.1f}%<extra></extra>"
        ),
        row=1, col=1
    )
    
    # Add benchmark line
    fig.add_hline(
        y=110, line_dash="dash", line_color="red",
        annotation_text="Target: 110%",
        annotation_position="right",
        row=1, col=1
    )
    
    # Top Right: Heatmap (OCCR by country and year)
    occr_by_year = finance_df.groupby(['country', 'year']).agg({
        'sewer_revenue': 'sum',
        'opex': 'sum'
    }).reset_index()
    occr_by_year['occr'] = (occr_by_year['sewer_revenue'] / occr_by_year['opex']) * 100
    
    pivot_occr = occr_by_year.pivot_table(
        values='occr',
        index='country',
        columns='year',
        aggfunc='mean'
    )
    
    fig.add_trace(
        go.Heatmap(
            z=pivot_occr.values,
            x=pivot_occr.columns,
            y=pivot_occr.index,
            colorscale='RdYlGn',
            text=np.round(pivot_occr.values, 1),
            texttemplate='%{text}%',
            textfont={"size": 10},
            colorbar=dict(title="OCCR %")
        ),
        row=1, col=2
    )
    
    # Bottom Left: Grouped bar chart (Revenue vs Opex)
    fig.add_trace(
        go.Bar(
            name='Revenue',
            x=country_occr['country'],
            y=country_occr['sewer_revenue'],
            marker_color=[COLORS['countries'].get(c, COLORS['primary']) for c in country_occr['country']],
            offsetgroup=0
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(
            name='Operating Expenditure',
            x=country_occr['country'],
            y=country_occr['opex'],
            marker_color=[COLORS['countries'].get(c, COLORS['secondary']) for c in country_occr['country']],
            offsetgroup=1
        ),
        row=2, col=1
    )
    
    # Bottom Right: Scatter plot (simplified without population data)
    fig.add_trace(
        go.Scatter(
            x=country_occr['propoor_popn'],
            y=country_occr['occr'],
            mode='markers',
            marker=dict(
                size=np.clip(country_occr['sewer_revenue'] / 1e8, 10, 40),
                color=[COLORS['countries'].get(c, COLORS['primary']) for c in country_occr['country']],
                sizemode='diameter',
                sizeref=2.0
            ),
            text=[f"{c}<br>Revenue: {rev/1e9:.2f} B" for c, rev in zip(country_occr['country'], country_occr['sewer_revenue'])],
            hovertemplate="<b>%{text}</b><br>Population: %{x:,.0f}<br>OCCR: %{y:.1f}%<extra></extra>",
            showlegend=False
        ),
        row=2, col=2
    )
    
    # Update subplot title styling to prevent overlap and improve readability
    fig.update_annotations(font=dict(size=13, color=COLORS['text_dark'], weight=600), yshift=-20)

    # Create layout without conflicting keys
    layout = STANDARD_LAYOUT.copy()
    # Remove keys that we'll override
    layout.pop('margin', None)
    layout.pop('title', None)
    
    layout.update({
        'height': 850,
        'title': {
            'text': "<b>OCCR Performance Dashboard</b>",
            'font': {'size': 20, 'color': COLORS['text_dark'], 'weight': 600},
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.98,
            'yanchor': 'top'
        },
        'margin': {'t': 90, 'b': 80, 'l': 60, 'r': 60},
        'showlegend': True,
        'legend': {
            'orientation': "h",
            'yanchor': "bottom",
            'y': -0.15,
            'xanchor': "center",
            'x': 0.5,
            'font': {'size': 11, 'color': COLORS['text_dark']},
            'bgcolor': 'rgba(255, 255, 255, 0.9)',
            'bordercolor': COLORS['border'],
            'borderwidth': 1
        }
    })
    
    fig.update_layout(**layout)
    
    # Update all axes to use dark text
    fig.update_xaxes(title_font=dict(color=COLORS['text_dark']), tickfont=dict(color=COLORS['text_dark']))
    fig.update_yaxes(title_font=dict(color=COLORS['text_dark']), tickfont=dict(color=COLORS['text_dark']))
    
    return fig


def create_map_choropleth(df, locations_col, values_col, title):
    """
    Create choropleth map (placeholder - requires geographic data)
    For now, creates a bar chart as substitute with high-contrast styling
    """
    fig = px.bar(
        df,
        x=locations_col,
        y=values_col,
        title=title,
        color=values_col,
        color_continuous_scale='RdYlGn'
    )
    
    # Apply standard layout
    fig.update_layout(
        **STANDARD_LAYOUT,
        height=500
    )
    
    return fig


def create_treemap(df, path_cols, values_col, title):
    """Create treemap for hierarchical data visualization with high-contrast styling"""
    fig = px.treemap(
        df,
        path=path_cols,
        values=values_col,
        title=title,
        color=values_col,
        color_continuous_scale='RdYlGn'
    )
    
    # Apply standard layout
    fig.update_layout(
        **STANDARD_LAYOUT,
        height=600
    )
    
    # Ensure treemap text is dark
    fig.update_traces(
        textfont=dict(color=COLORS['text_dark'], size=12),
        marker=dict(line=dict(color=COLORS['border'], width=2))
    )
    
    return fig

