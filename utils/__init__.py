"""
Utilities package for the Water Services Dashboard
Contains data loading, KPI calculations, and visualization functions
"""

from .data_loader import (
    load_production_data,
    load_w_service_data,
    load_s_service_data,
    load_w_access_data,
    load_s_access_data,
    load_finance_data,
    load_national_data,
    load_all_data
)

from .kpi_calculator import (
    calculate_occr,
    calculate_nrw,
    calculate_collection_efficiency,
    calculate_water_coverage,
    calculate_sanitation_coverage,
    calculate_metering_ratio,
    calculate_water_quality_compliance,
    calculate_summary_kpis,
    calculate_country_kpis
)

from .visualizations import (
    create_kpi_card,
    create_trend_line,
    create_comparison_bar,
    create_waterfall_chart,
    create_heatmap,
    create_scatter_plot,
    create_occr_dashboard,
    COLORS,
    BENCHMARKS
)

__all__ = [
    'load_production_data',
    'load_w_service_data',
    'load_s_service_data',
    'load_w_access_data',
    'load_s_access_data',
    'load_finance_data',
    'load_national_data',
    'load_all_data',
    'calculate_occr',
    'calculate_nrw',
    'calculate_collection_efficiency',
    'calculate_water_coverage',
    'calculate_sanitation_coverage',
    'calculate_metering_ratio',
    'calculate_water_quality_compliance',
    'calculate_summary_kpis',
    'calculate_country_kpis',
    'create_kpi_card',
    'create_trend_line',
    'create_comparison_bar',
    'create_waterfall_chart',
    'create_heatmap',
    'create_scatter_plot',
    'create_occr_dashboard',
    'COLORS',
    'BENCHMARKS'
]

