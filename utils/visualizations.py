"""
Visualization Utilities Module
Reusable Plotly chart creation functions for Water Services Dashboard
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any
import logging

logger = logging.getLogger(__name__)

# HIGH-CONTRAST COLOR PALETTE - WCAG AAA Compliant
COLORS = {
    'good': '#198754',      # Dark green (WCAG AAA)
    'acceptable': '#fd7e14',  # Orange (WCAG AA)
    'poor': '#dc3545',      # Red (WCAG AAA)
    'primary': '#0056b3',   # Dark blue (WCAG AAA)
    'secondary': '#6f42c1',  # Purple (WCAG AA)
    'tertiary': '#0f6674',  # Dark teal (WCAG AAA)
    'text_dark': '#1e1e1e', # Almost black (text on light)
    'text_medium': '#333333', # Dark gray (general text)
    'text_light': '#ffffff', # White (text on dark)
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

# Benchmark values for water services KPIs
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

def _validate_data_for_visualization(df: pd.DataFrame, required_columns: List[str], 
                                   visualization_name: str) -> bool:
    """
    Validate data before creating visualization
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        visualization_name: Name of visualization for error logging
    
    Returns:
        bool: True if data is valid
    """
    if df is None or df.empty:
        logger.warning(f"Empty or None DataFrame for {visualization_name}")
        return False
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.warning(f"Missing columns for {visualization_name}: {missing_columns}")
        return False
    
    return True

def _safe_aggregate_data(df: pd.DataFrame, group_cols: List[str], 
                        value_cols: List[str]) -> pd.DataFrame:
    """
    Safely aggregate data with error handling
    
    Args:
        df: Input DataFrame
        group_cols: Columns to group by
        value_cols: Columns to aggregate
    
    Returns:
        pd.DataFrame: Aggregated data
    """
    try:
        # Filter to only existing columns
        existing_group_cols = [col for col in group_cols if col in df.columns]
        existing_value_cols = [col for col in value_cols if col in df.columns]
        
        if not existing_group_cols or not existing_value_cols:
            return pd.DataFrame()
        
        aggregated = df.groupby(existing_group_cols)[existing_value_cols].sum().reset_index()
        return aggregated
        
    except Exception as e:
        logger.error(f"Error aggregating data: {e}")
        return pd.DataFrame()

def create_kpi_card(title: str, value: float, benchmark: float, unit: str = '%', 
                   inverse: bool = False, height: int = 200) -> go.Figure:
    """
    Create a KPI card with status indicator
    
    Args:
        title: KPI name
        value: Current value
        benchmark: Target benchmark
        unit: Unit of measurement
        inverse: If True, lower is better
        height: Chart height in pixels
    
    Returns:
        Plotly figure object
    """
    try:
        # Handle NaN values
        if pd.isna(value):
            value = 0.0
        if pd.isna(benchmark):
            benchmark = 0.0
        
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
        
        # Normalize unit formatting
        unit_suffix = f" {unit}" if unit and unit not in {'%'} and not unit.startswith(' ') else unit

        # Determine gauge range
        max_range = max(abs(value), abs(benchmark)) * 1.2
        if max_range == 0:
            max_range = benchmark * 1.5 if benchmark else 1
        max_range = max(max_range, benchmark * 1.5 if benchmark else 1)
        
        # Create gauge steps
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

        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={
                'text': f"<b>{title}</b>",
                'font': {'size': 14, 'color': COLORS['text_dark']}
            },
            delta={
                'reference': benchmark,
                'font': {'size': 12},
                'increasing': {'color': COLORS['good'] if not inverse else COLORS['poor']},
                'decreasing': {'color': COLORS['poor'] if not inverse else COLORS['good']},
                'valueformat': '.1f'
            },
            number={
                'suffix': unit_suffix,
                'font': {'size': 28, 'color': color},
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
            height=height,
            margin=dict(l=15, r=15, t=40, b=15),
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
        
        # Force light template
        fig.update_layout(template='plotly_white')
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating KPI card for {title}: {e}")
        # Return empty figure on error
        fig = go.Figure()
        fig.update_layout(
            title=f"Error creating {title}",
            height=height,
            paper_bgcolor=COLORS['bg_light']
        )
        return fig

def create_trend_line(df: pd.DataFrame, x_col: str, y_col: str, title: str, 
                     color: Optional[str] = None, benchmark: Optional[float] = None,
                     group_col: Optional[str] = None) -> go.Figure:
    """
    Create a line chart showing trends over time
    
    Args:
        df: Input DataFrame
        x_col: Column for x-axis (typically date)
        y_col: Column for y-axis (metric)
        title: Chart title
        color: Single color or column name for coloring
        benchmark: Benchmark value to display as horizontal line
        group_col: Column to group lines by
    
    Returns:
        Plotly figure object
    """
    if not _validate_data_for_visualization(df, [x_col, y_col], 'trend_line'):
        return _create_empty_plot(title)
    
    try:
        # Sort by x_col for proper line plotting
        df = df.sort_values(x_col)
        
        if group_col and group_col in df.columns:
            fig = px.line(
                df, 
                x=x_col, 
                y=y_col,
                color=group_col,
                title=title,
                color_discrete_map=COLORS.get('countries', {})
            )
        else:
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
        
    except Exception as e:
        logger.error(f"Error creating trend line: {e}")
        return _create_empty_plot(title)

def create_comparison_bar(df: pd.DataFrame, x_col: str, y_col: str, title: str, 
                         color_col: Optional[str] = None, orientation: str = 'v',
                         aggregation: str = 'sum') -> go.Figure:
    """
    Create bar chart for comparing values across categories
    
    Args:
        df: Input DataFrame
        x_col: Column for x-axis (categories)
        y_col: Column for y-axis (values)
        title: Chart title
        color_col: Column for coloring bars
        orientation: 'v' for vertical, 'h' for horizontal
        aggregation: Aggregation function ('sum', 'mean', 'count')
    
    Returns:
        Plotly figure object
    """
    if not _validate_data_for_visualization(df, [x_col, y_col], 'comparison_bar'):
        return _create_empty_plot(title)
    
    try:
        # Aggregate data if needed
        if color_col and color_col in df.columns:
            agg_df = df.groupby([x_col, color_col])[y_col].agg(aggregation).reset_index()
        else:
            agg_df = df.groupby(x_col)[y_col].agg(aggregation).reset_index()
        
        fig = px.bar(
            agg_df,
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
        
    except Exception as e:
        logger.error(f"Error creating comparison bar: {e}")
        return _create_empty_plot(title)

def create_waterfall_chart(categories: List[str], values: List[float], title: str, 
                          yaxis_title: str = "Amount") -> go.Figure:
    """
    Create waterfall chart for financial flow visualization
    
    Args:
        categories: List of category names
        values: List of values (positive for additions, negative for subtractions)
        title: Chart title
        yaxis_title: Y-axis title
    
    Returns:
        Plotly figure object
    """
    try:
        if len(categories) != len(values):
            raise ValueError("Categories and values must have the same length")
        
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
            text=[f"{v:+,.0f}" for v in values],
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
        
    except Exception as e:
        logger.error(f"Error creating waterfall chart: {e}")
        return _create_empty_plot(title)

def create_heatmap(df: pd.DataFrame, x_col: str, y_col: str, value_col: str, 
                  title: str, aggregation: str = 'mean') -> go.Figure:
    """
    Create heatmap for visualizing values across two dimensions
    
    Args:
        df: Input DataFrame
        x_col: Column for x-axis
        y_col: Column for y-axis
        value_col: Column for values
        title: Chart title
        aggregation: Aggregation function ('mean', 'sum', 'count')
    
    Returns:
        Plotly figure object
    """
    if not _validate_data_for_visualization(df, [x_col, y_col, value_col], 'heatmap'):
        return _create_empty_plot(title)
    
    try:
        pivot_df = df.pivot_table(
            values=value_col,
            index=y_col,
            columns=x_col,
            aggfunc=aggregation
        ).fillna(0)
        
        fig = px.imshow(
            pivot_df,
            title=title,
            labels=dict(x=x_col.replace('_', ' ').title(), 
                       y=y_col.replace('_', ' ').title(), 
                       color=value_col.replace('_', ' ').title()),
            aspect="auto",
            color_continuous_scale='RdYlGn_r',  # Reversed for better intuition
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
        
    except Exception as e:
        logger.error(f"Error creating heatmap: {e}")
        return _create_empty_plot(title)

def create_scatter_plot(df: pd.DataFrame, x_col: str, y_col: str, title: str, 
                       color_col: Optional[str] = None, size_col: Optional[str] = None,
                       trendline: bool = False) -> go.Figure:
    """
    Create scatter plot for correlation analysis
    
    Args:
        df: Input DataFrame
        x_col: Column for x-axis
        y_col: Column for y-axis
        title: Chart title
        color_col: Column for point colors
        size_col: Column for point sizes
        trendline: Whether to add trendline
    
    Returns:
        Plotly figure object
    """
    if not _validate_data_for_visualization(df, [x_col, y_col], 'scatter_plot'):
        return _create_empty_plot(title)
    
    try:
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            title=title,
            color=color_col,
            size=size_col,
            color_discrete_map=COLORS['countries'] if color_col == 'country' else None,
            hover_data=df.columns.tolist(),
            trendline="ols" if trendline else None
        )
        
        # Apply standard layout
        fig.update_layout(
            **STANDARD_LAYOUT,
            height=500,
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title()
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating scatter plot: {e}")
        return _create_empty_plot(title)

def create_stacked_area(df: pd.DataFrame, x_col: str, y_cols: List[str], 
                       title: str) -> go.Figure:
    """
    Create stacked area chart for composition over time
    
    Args:
        df: Input DataFrame
        x_col: Column for x-axis (typically date)
        y_cols: List of columns for stacking
        title: Chart title
    
    Returns:
        Plotly figure object
    """
    required_cols = [x_col] + y_cols
    if not _validate_data_for_visualization(df, required_cols, 'stacked_area'):
        return _create_empty_plot(title)
    
    try:
        fig = go.Figure()
        
        for col in y_cols:
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[col],
                name=col.replace('_', ' ').title(),
                mode='lines',
                stackgroup='one',
                fillcolor=None  # Let Plotly choose colors
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
        
    except Exception as e:
        logger.error(f"Error creating stacked area: {e}")
        return _create_empty_plot(title)

def create_occr_dashboard(finance_df: pd.DataFrame) -> go.Figure:
    """
    Create comprehensive OCCR dashboard with 2x2 layout
    
    Args:
        finance_df: Financial data DataFrame
    
    Returns:
        Plotly figure with subplots
    """
    if not _validate_data_for_visualization(finance_df, ['country', 'sewer_revenue', 'opex'], 'occr_dashboard'):
        return _create_empty_plot("OCCR Performance Dashboard")
    
    try:
        # Calculate OCCR by country
        country_occr = finance_df.groupby('country').agg({
            'sewer_revenue': 'sum',
            'opex': 'sum'
        }).reset_index()
        country_occr['occr'] = (country_occr['sewer_revenue'] / country_occr['opex']) * 100
        
        # Create subplots (2x2)
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'OCCR by Country',
                'OCCR Trends (Country × Year)',
                'Revenue vs Operating Costs',
                'OCCR Distribution'
            ),
            specs=[
                [{'type': 'bar'}, {'type': 'heatmap'}],
                [{'type': 'bar'}, {'type': 'box'}]
            ],
            vertical_spacing=0.20,
            horizontal_spacing=0.15
        )
        
        # Top Left: Bar chart for OCCR by country
        fig.add_trace(
            go.Bar(
                x=country_occr['country'],
                y=country_occr['occr'],
                text=[f"{val:.1f}%" for val in country_occr['occr']],
                textposition='outside',
                marker_color=[
                    COLORS['good'] if val >= 110 else 
                    COLORS['acceptable'] if val >= 100 else 
                    COLORS['poor'] 
                    for val in country_occr['occr']
                ],
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
        
        # Top Right: Heatmap (OCCR by country and year) - simplified
        if 'year' in finance_df.columns:
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
            ).fillna(0)
            
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
        else:
            # Add placeholder if year column not available
            fig.add_annotation(
                row=1, col=2,
                text="Year data not available",
                showarrow=False,
                font=dict(color=COLORS['text_dark'])
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
        
        # Bottom Right: Box plot for OCCR distribution
        fig.add_trace(
            go.Box(
                y=country_occr['occr'],
                name="OCCR Distribution",
                marker_color=COLORS['primary'],
                boxpoints='all'
            ),
            row=2, col=2
        )
        
        # Update layout
        layout = STANDARD_LAYOUT.copy()
        layout.update({
            'height': 800,
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
                'font': {'size': 11, 'color': COLORS['text_dark']}
            }
        })
        
        fig.update_layout(**layout)
        
        # Update all axes to use dark text
        fig.update_xaxes(title_font=dict(color=COLORS['text_dark']), tickfont=dict(color=COLORS['text_dark']))
        fig.update_yaxes(title_font=dict(color=COLORS['text_dark']), tickfont=dict(color=COLORS['text_dark']))
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating OCCR dashboard: {e}")
        return _create_empty_plot("OCCR Performance Dashboard")

def create_pie_chart(df: pd.DataFrame, names_col: str, values_col: str, 
                    title: str) -> go.Figure:
    """
    Create pie chart for composition analysis
    
    Args:
        df: Input DataFrame
        names_col: Column for slice names
        values_col: Column for slice values
        title: Chart title
    
    Returns:
        Plotly figure object
    """
    if not _validate_data_for_visualization(df, [names_col, values_col], 'pie_chart'):
        return _create_empty_plot(title)
    
    try:
        fig = px.pie(
            df,
            names=names_col,
            values=values_col,
            title=title,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        # Apply standard layout with modifications for pie chart
        pie_layout = STANDARD_LAYOUT.copy()
        pie_layout.update({
            'height': 500,
            'showlegend': True,
            'legend': {
                'font': {'color': COLORS['text_dark'], 'size': 12},
                'orientation': 'v'
            }
        })
        
        fig.update_layout(**pie_layout)
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating pie chart: {e}")
        return _create_empty_plot(title)

def _create_empty_plot(title: str, message: str = "No data available") -> go.Figure:
    """
    Create an empty plot with message
    
    Args:
        title: Plot title
        message: Message to display
    
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    fig.update_layout(
        title=title,
        height=400,
        paper_bgcolor=COLORS['bg_light'],
        plot_bgcolor=COLORS['bg_light'],
        annotations=[dict(
            text=message,
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=16, color=COLORS['text_medium'])
        )]
    )
    return fig

# Utility function to get available visualizations
def get_available_visualizations() -> Dict[str, str]:
    """
    Get dictionary of available visualization functions and their descriptions
    
    Returns:
        Dict with function names as keys and descriptions as values
    """
    return {
        'create_kpi_card': 'KPI gauge with benchmark comparison',
        'create_trend_line': 'Line chart for time series data',
        'create_comparison_bar': 'Bar chart for categorical comparisons',
        'create_waterfall_chart': 'Waterfall chart for financial flows',
        'create_heatmap': 'Heatmap for two-dimensional data',
        'create_scatter_plot': 'Scatter plot for correlation analysis',
        'create_stacked_area': 'Stacked area chart for composition over time',
        'create_occr_dashboard': 'Comprehensive OCCR performance dashboard',
        'create_pie_chart': 'Pie chart for composition analysis'
    }

# Test function
if __name__ == "__main__":
    # Test data creation
    test_data = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=12, freq='M'),
        'value': np.random.rand(12) * 100,
        'category': ['A', 'B'] * 6,
        'country': ['Uganda', 'Cameroon'] * 6
    })
    
    # Test visualizations
    fig1 = create_trend_line(test_data, 'date', 'value', 'Test Trend')
    fig2 = create_comparison_bar(test_data, 'category', 'value', 'Test Bar')
    
    print("Visualization test completed successfully!")
    print(f"Available visualizations: {list(get_available_visualizations().keys())}")
