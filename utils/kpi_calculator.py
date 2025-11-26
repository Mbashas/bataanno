"""
KPI Calculation Module
Contains all formulas and calculations for dashboard KPIs
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
import logging

logger = logging.getLogger(__name__)

# KPI Benchmark definitions
KPI_BENCHMARKS = {
    'water_coverage': {'target': 100, 'unit': '%', 'inverse': False, 'description': 'Water Service Coverage'},
    'sanitation_coverage': {'target': 100, 'unit': '%', 'inverse': False, 'description': 'Sanitation Service Coverage'},
    'nrw': {'target': 25, 'unit': '%', 'inverse': True, 'description': 'Non-Revenue Water'},
    'occr': {'target': 110, 'unit': '%', 'inverse': False, 'description': 'Operating Cost Coverage Ratio'},
    'collection_efficiency': {'target': 95, 'unit': '%', 'inverse': False, 'description': 'Revenue Collection Efficiency'},
    'water_quality': {'target': 95, 'unit': '%', 'inverse': False, 'description': 'Water Quality Compliance'},
    'metering_ratio': {'target': 95, 'unit': '%', 'inverse': False, 'description': 'Water Metering Ratio'},
    'staff_productivity': {'target': 7, 'unit': 'staff/1k', 'inverse': True, 'description': 'Staff Productivity'},
    'service_hours': {'target': 20, 'unit': 'hrs/day', 'inverse': False, 'description': 'Daily Service Hours'},
    'personnel_cost_ratio': {'target': 35, 'unit': '%', 'inverse': True, 'description': 'Personnel Cost Ratio'},
    'complaint_resolution': {'target': 90, 'unit': '%', 'inverse': False, 'description': 'Complaint Resolution Rate'},
    'ww_treatment_rate': {'target': 80, 'unit': '%', 'inverse': False, 'description': 'Wastewater Treatment Rate'}
}

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers with zero division protection"""
    if denominator == 0 or pd.isna(denominator) or pd.isna(numerator):
        return default
    return numerator / denominator

def calculate_water_coverage(safely_managed: float, basic: float, popn_total: float) -> float:
    """Calculate Water Coverage % with safe handling"""
    try:
        if popn_total == 0 or pd.isna(popn_total):
            return 0.0
        served_population = safely_managed + basic
        return (served_population / popn_total) * 100
    except Exception as e:
        logger.warning(f"Error calculating water coverage: {e}")
        return 0.0

def calculate_sanitation_coverage(safely_managed: float, basic: float, popn_total: float) -> float:
    """Calculate Sanitation Coverage % with safe handling"""
    try:
        if popn_total == 0 or pd.isna(popn_total):
            return 0.0
        served_population = safely_managed + basic
        return (served_population / popn_total) * 100
    except Exception as e:
        logger.warning(f"Error calculating sanitation coverage: {e}")
        return 0.0

def calculate_nrw(production: float, billed_volume: float) -> float:
    """Calculate Non-Revenue Water % with safe handling"""
    try:
        if production == 0 or pd.isna(production):
            return 0.0
        losses = production - billed_volume
        return (losses / production) * 100
    except Exception as e:
        logger.warning(f"Error calculating NRW: {e}")
        return 0.0

def calculate_occr(revenue: float, opex: float) -> float:
    """Calculate Operating Cost Coverage Ratio with safe handling"""
    try:
        return safe_divide(revenue, opex, 0.0) * 100
    except Exception as e:
        logger.warning(f"Error calculating OCCR: {e}")
        return 0.0

def calculate_collection_efficiency(total_collection: float, total_billing: float) -> float:
    """Calculate Revenue Collection Efficiency with safe handling"""
    try:
        return safe_divide(total_collection, total_billing, 0.0) * 100
    except Exception as e:
        logger.warning(f"Error calculating collection efficiency: {e}")
        return 0.0

def calculate_metering_ratio(metered: float, total_consumption: float) -> float:
    """Calculate Metering Ratio with safe handling"""
    try:
        return safe_divide(metered, total_consumption, 0.0) * 100
    except Exception as e:
        logger.warning(f"Error calculating metering ratio: {e}")
        return 0.0

def calculate_water_quality_compliance(tests_passed: float, tests_conducted: float) -> float:
    """Calculate Water Quality Compliance Rate with safe handling"""
    try:
        return safe_divide(tests_passed, tests_conducted, 0.0) * 100
    except Exception as e:
        logger.warning(f"Error calculating water quality compliance: {e}")
        return 0.0

def calculate_staff_productivity(staff: float, connections: float) -> float:
    """Calculate Staff Productivity with safe handling"""
    try:
        if connections == 0 or pd.isna(connections):
            return 0.0
        return (staff / connections) * 1000
    except Exception as e:
        logger.warning(f"Error calculating staff productivity: {e}")
        return 0.0

def calculate_complaint_resolution_rate(resolved: float, complaints: float) -> float:
    """Calculate Complaint Resolution Rate with safe handling"""
    try:
        return safe_divide(resolved, complaints, 0.0) * 100
    except Exception as e:
        logger.warning(f"Error calculating complaint resolution rate: {e}")
        return 0.0

def calculate_ww_treatment_rate(ww_treated: float, ww_collected: float) -> float:
    """Calculate Wastewater Treatment Rate with safe handling"""
    try:
        return safe_divide(ww_treated, ww_collected, 0.0) * 100
    except Exception as e:
        logger.warning(f"Error calculating wastewater treatment rate: {e}")
        return 0.0

def get_kpi_status(value: float, kpi_name: str, custom_benchmark: Optional[float] = None) -> Tuple[str, str]:
    """Determine KPI status based on benchmark"""
    if pd.isna(value):
        return 'unknown', '#808080'
    
    benchmark_info = KPI_BENCHMARKS.get(kpi_name, {})
    benchmark = custom_benchmark if custom_benchmark is not None else benchmark_info.get('target', 0)
    inverse = benchmark_info.get('inverse', False)
    
    if inverse:
        if value <= benchmark:
            return 'good', '#198754'
        elif value <= benchmark * 1.2:
            return 'acceptable', '#fd7e14'
        else:
            return 'poor', '#dc3545'
    else:
        if value >= benchmark:
            return 'good', '#198754'
        elif value >= benchmark * 0.8:
            return 'acceptable', '#fd7e14'
        else:
            return 'poor', '#dc3545'

def calculate_summary_kpis(data: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, Any]]:
    """
    Calculate high-level summary KPIs for all countries with enhanced robustness
    """
    try:
        kpis = {}
        
        # Get datasets with safe access
        w_access = data.get('w_access', pd.DataFrame())
        s_access = data.get('s_access', pd.DataFrame())
        w_service = data.get('w_service', pd.DataFrame())
        finance = data.get('finance', pd.DataFrame())
        production = data.get('production', pd.DataFrame())
        national = data.get('national', pd.DataFrame())
        
        # Calculate each KPI with individual error handling
        
        # Water Coverage - with multiple fallbacks
        water_coverage_value = 0.0
        if not w_access.empty:
            try:
                # Try multiple ways to calculate water coverage
                if 'access_rate' in w_access.columns:
                    water_coverage_value = w_access['access_rate'].mean()
                elif 'safely_managed_pct' in w_access.columns and 'basic_pct' in w_access.columns:
                    water_coverage_value = (w_access['safely_managed_pct'] + w_access['basic_pct']).mean()
                elif 'safely_managed' in w_access.columns and 'basic' in w_access.columns and 'popn_total' in w_access.columns:
                    total_pop = w_access['popn_total'].sum()
                    if total_pop > 0:
                        safely_managed_total = w_access['safely_managed'].sum()
                        basic_total = w_access['basic'].sum()
                        water_coverage_value = ((safely_managed_total + basic_total) / total_pop) * 100
            except Exception as e:
                logger.warning(f"Error calculating water coverage: {e}")
                water_coverage_value = 0.0
        
        kpis['water_coverage'] = {'value': water_coverage_value}
        
        # Sanitation Coverage - with multiple fallbacks
        sanitation_coverage_value = 0.0
        if not s_access.empty:
            try:
                if 'access_rate' in s_access.columns:
                    sanitation_coverage_value = s_access['access_rate'].mean()
                elif 'safely_managed_pct' in s_access.columns and 'basic_pct' in s_access.columns:
                    sanitation_coverage_value = (s_access['safely_managed_pct'] + s_access['basic_pct']).mean()
                elif 'safely_managed' in s_access.columns and 'basic' in s_access.columns and 'popn_total' in s_access.columns:
                    total_pop = s_access['popn_total'].sum()
                    if total_pop > 0:
                        safely_managed_total = s_access['safely_managed'].sum()
                        basic_total = s_access['basic'].sum()
                        sanitation_coverage_value = ((safely_managed_total + basic_total) / total_pop) * 100
            except Exception as e:
                logger.warning(f"Error calculating sanitation coverage: {e}")
                sanitation_coverage_value = 0.0
        
        kpis['sanitation_coverage'] = {'value': sanitation_coverage_value}
        
        # NRW
        nrw_value = 0.0
        if not production.empty and not w_service.empty:
            try:
                prod_total = production['production_m3'].sum()
                metered_total = w_service.get('metered', pd.Series([0])).sum()
                nrw_value = calculate_nrw(prod_total, metered_total)
            except Exception as e:
                logger.warning(f"Error calculating NRW: {e}")
        
        kpis['nrw'] = {'value': nrw_value}
        
        # OCCR
        occr_value = 0.0
        if not finance.empty:
            try:
                total_revenue = finance.get('sewer_revenue', pd.Series([0])).sum()
                total_opex = finance.get('opex', pd.Series([0])).sum()
                occr_value = calculate_occr(total_revenue, total_opex)
            except Exception as e:
                logger.warning(f"Error calculating OCCR: {e}")
        
        kpis['occr'] = {'value': occr_value}
        
        # Collection Efficiency
        collection_value = 0.0
        if not finance.empty:
            try:
                total_revenue = finance.get('sewer_revenue', pd.Series([0])).sum()
                total_billing = finance.get('sewer_billed', pd.Series([0])).sum()
                collection_value = calculate_collection_efficiency(total_revenue, total_billing)
            except Exception as e:
                logger.warning(f"Error calculating collection efficiency: {e}")
        
        kpis['collection_efficiency'] = {'value': collection_value}
        
        # Water Quality
        water_quality_value = 0.0
        if not w_service.empty:
            try:
                chlorine_passed = w_service.get('test_passed_chlorine', pd.Series([0])).sum()
                chlorine_conducted = w_service.get('tests_conducted_chlorine', pd.Series([0])).sum()
                water_quality_value = calculate_water_quality_compliance(chlorine_passed, chlorine_conducted)
            except Exception as e:
                logger.warning(f"Error calculating water quality: {e}")
        
        kpis['water_quality'] = {'value': water_quality_value}
        
        # Metering Ratio
        metering_value = 0.0
        if not w_service.empty:
            try:
                metered_total = w_service.get('metered', pd.Series([0])).sum()
                total_consumption = w_service.get('total_consumption', pd.Series([0])).sum()
                metering_value = calculate_metering_ratio(metered_total, total_consumption)
            except Exception as e:
                logger.warning(f"Error calculating metering ratio: {e}")
        
        kpis['metering_ratio'] = {'value': metering_value}
        
        # Service Hours
        service_hours_value = 0.0
        if not production.empty:
            try:
                service_hours_value = production.get('service_hours', pd.Series([0])).mean()
            except Exception as e:
                logger.warning(f"Error calculating service hours: {e}")
        
        kpis['service_hours'] = {'value': service_hours_value}
        
        # Staff Productivity
        staff_productivity_value = 0.0
        if not w_service.empty and not finance.empty:
            try:
                total_connections = w_service.get('households', pd.Series([0])).sum()
                total_staff = finance.get('w_staff', pd.Series([0])).sum() + finance.get('san_staff', pd.Series([0])).sum()
                staff_productivity_value = calculate_staff_productivity(total_staff, total_connections)
            except Exception as e:
                logger.warning(f"Error calculating staff productivity: {e}")
        
        kpis['staff_productivity'] = {'value': staff_productivity_value}
        
        # Add metadata to each KPI
        for kpi_name in kpis:
            if kpi_name in KPI_BENCHMARKS:
                kpis[kpi_name].update({
                    'benchmark': KPI_BENCHMARKS[kpi_name]['target'],
                    'unit': KPI_BENCHMARKS[kpi_name]['unit'],
                    'inverse': KPI_BENCHMARKS[kpi_name]['inverse'],
                    'description': KPI_BENCHMARKS[kpi_name]['description']
                })
                
                # Calculate status
                status, color = get_kpi_status(kpis[kpi_name]['value'], kpi_name)
                kpis[kpi_name]['status'] = status
                kpis[kpi_name]['color'] = color
        
        return kpis
        
    except Exception as e:
        logger.error(f"Error calculating summary KPIs: {e}")
        return _get_empty_kpis()

def _get_empty_kpis() -> Dict[str, Dict[str, Any]]:
    """Return empty KPI structure when calculation fails"""
    empty_kpis = {}
    for kpi_name, benchmark_info in KPI_BENCHMARKS.items():
        empty_kpis[kpi_name] = {
            'value': 0.0,
            'benchmark': benchmark_info['target'],
            'unit': benchmark_info['unit'],
            'inverse': benchmark_info['inverse'],
            'description': benchmark_info['description'],
            'status': 'unknown',
            'color': '#808080'
        }
    return empty_kpis

def calculate_country_kpis(data: Dict[str, pd.DataFrame], country: str) -> Dict[str, float]:
    """
    Calculate KPIs for a specific country with enhanced error handling
    """
    try:
        # Filter data by country
        filtered_data = {}
        for name, df in data.items():
            if not df.empty and 'country' in df.columns:
                filtered_data[name] = df[df['country'] == country]
            else:
                filtered_data[name] = df
        
        # Calculate summary KPIs for the country
        country_kpis = calculate_summary_kpis(filtered_data)
        
        # Extract just the values for backward compatibility
        simple_kpis = {}
        for kpi_name, kpi_data in country_kpis.items():
            if isinstance(kpi_data, dict) and 'value' in kpi_data:
                simple_kpis[kpi_name] = kpi_data['value']
            else:
                simple_kpis[kpi_name] = kpi_data
        
        return simple_kpis
        
    except Exception as e:
        logger.error(f"Error calculating country KPIs for {country}: {e}")
        return {kpi: 0.0 for kpi in KPI_BENCHMARKS.keys()}

# Customer-level financial analysis functions
def calculate_revenue_collection_efficiency_customer_level(billing_df, country=None, date_range=None):
    """
    Calculate RCE using billing.csv for customer-level granularity
    """
    try:
        df = billing_df.copy()
        
        # Apply filters
        if country and 'country' in df.columns:
            if isinstance(country, str):
                df = df[df['country'] == country]
            else:
                df = df[df['country'].isin(country)]
        
        if date_range and 'date' in df.columns:
            df = df[(df['date'] >= pd.to_datetime(date_range[0])) & 
                    (df['date'] <= pd.to_datetime(date_range[1]))]
        
        total_billed = df['billed'].sum()
        total_paid = df['paid'].sum()
        rce = calculate_collection_efficiency(total_paid, total_billed)
        
        return rce, total_billed, total_paid
        
    except Exception as e:
        logger.error(f"Error calculating customer RCE: {e}")
        return 0.0, 0.0, 0.0

def identify_payment_risk_customers(billing_df, threshold_high=0.5, threshold_medium=0.8):
    """
    Segment customers by payment behavior
    """
    try:
        customer_summary = billing_df.groupby('customer_id').agg({
            'billed': 'sum',
            'paid': 'sum',
            'country': 'first',
            'zone': 'first'
        }).reset_index()
        
        # Calculate payment ratio with zero-division protection
        customer_summary['payment_ratio'] = np.where(
            customer_summary['billed'] != 0, 
            customer_summary['paid'] / customer_summary['billed'], 
            0
        )
        customer_summary['risk_category'] = customer_summary['payment_ratio'].apply(
            lambda x: 'High Risk' if x < threshold_high else (
                'Medium Risk' if x < threshold_medium else 'Low Risk'
            )
        )
        customer_summary['unpaid_amount'] = customer_summary['billed'] - customer_summary['paid']
        
        return customer_summary
        
    except Exception as e:
        logger.error(f"Error identifying payment risk customers: {e}")
        return pd.DataFrame()