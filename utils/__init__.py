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
    load_billing_data,
    load_all_data,
    apply_filters,
    get_available_countries,
    get_available_years,
    get_available_zones,
    get_latest_update_date,
    get_data_summary,
    check_data_quality,
    validate_kpi_calculations,
    safe_data_loader,
    kpi_calculation_wrapper,
    visualization_safe_mode
)

from .kpi_calculator import (
    calculate_occr,
    calculate_nrw,
    calculate_collection_efficiency,
    calculate_water_coverage,
    calculate_sanitation_coverage,
    calculate_metering_ratio,
    calculate_water_quality_compliance,
    calculate_staff_productivity,
    calculate_complaint_resolution_rate,
    calculate_ww_treatment_rate,
    calculate_summary_kpis,
    calculate_country_kpis,
    calculate_revenue_collection_efficiency_customer_level,
    identify_payment_risk_customers,
    get_kpi_status,
    KPI_BENCHMARKS
)

from .visualizations import (
    create_kpi_card,
    create_trend_line,
    create_comparison_bar,
    create_waterfall_chart,
    create_heatmap,
    create_scatter_plot,
    create_stacked_area,
    create_occr_dashboard,
    create_pie_chart,
    COLORS,
    BENCHMARKS
)

from .currency_config import (
    get_currency_config,
    format_currency,
    format_currency_multi_country,
    get_currency_label,
    get_available_countries as get_currency_countries,
    CURRENCY_CONFIG
)

__all__ = [
    # Data loading functions
    'load_production_data',
    'load_w_service_data',
    'load_s_service_data',
    'load_w_access_data',
    'load_s_access_data',
    'load_finance_data',
    'load_national_data',
    'load_billing_data',
    'load_all_data',
    'apply_filters',
    'get_available_countries',
    'get_available_years', 
    'get_available_zones',
    'get_latest_update_date',
    'get_data_summary',
    
    # KPI calculation functions
    'calculate_occr',
    'calculate_nrw',
    'calculate_collection_efficiency',
    'calculate_water_coverage',
    'calculate_sanitation_coverage',
    'calculate_metering_ratio',
    'calculate_water_quality_compliance',
    'calculate_staff_productivity',
    'calculate_complaint_resolution_rate',
    'calculate_ww_treatment_rate',
    'calculate_summary_kpis',
    'calculate_country_kpis',
    'calculate_revenue_collection_efficiency_customer_level',
    'identify_payment_risk_customers',
    'get_kpi_status',
    'KPI_BENCHMARKS',
    
    # Visualization functions
    'create_kpi_card',
    'create_trend_line',
    'create_comparison_bar',
    'create_waterfall_chart',
    'create_heatmap',
    'create_scatter_plot',
    'create_stacked_area',
    'create_occr_dashboard',
    'create_pie_chart',
    'COLORS',
    'BENCHMARKS',
    
    # Currency functions
    'get_currency_config',
    'format_currency',
    'format_currency_multi_country',
    'get_currency_label',
    'get_currency_countries',
    'CURRENCY_CONFIG',
    
    # Debugging and utility functions
    'check_data_quality',
    'validate_kpi_calculations',
    'safe_data_loader',
    'kpi_calculation_wrapper',
    'visualization_safe_mode'
]