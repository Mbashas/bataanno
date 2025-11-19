"""
KPI Calculation Module
Contains all formulas and calculations for dashboard KPIs
"""

import pandas as pd
import numpy as np


def calculate_occr(revenue, opex):
    """
    Calculate Operating Cost Coverage Ratio (OCCR)
    Formula: (sewer_revenue ÷ opex) × 100
    Benchmark: ≥110%
    """
    if opex == 0 or pd.isna(opex):
        return 0
    return (revenue / opex) * 100


def calculate_nrw(production, billed_volume):
    """
    Calculate Non-Revenue Water (NRW)
    Formula: ((production_m3 - billed_volume) ÷ production_m3) × 100
    Benchmark: ≤25%
    """
    if production == 0 or pd.isna(production):
        return 0
    return ((production - billed_volume) / production) * 100


def calculate_collection_efficiency(total_collection, total_billing):
    """
    Calculate Revenue Collection Efficiency
    Formula: (total_collection ÷ total_billing) × 100
    Benchmark: ≥95%
    """
    if total_billing == 0 or pd.isna(total_billing):
        return 0
    return (total_collection / total_billing) * 100


def calculate_water_coverage(safely_managed, basic, popn_total):
    """
    Calculate Water Coverage %
    Formula: ((safely_managed + basic) ÷ popn_total) × 100
    Benchmark: 100%
    """
    if popn_total == 0 or pd.isna(popn_total):
        return 0
    return ((safely_managed + basic) / popn_total) * 100


def calculate_sanitation_coverage(safely_managed, basic, popn_total):
    """
    Calculate Sanitation Coverage %
    Formula: ((safely_managed + basic) ÷ popn_total) × 100
    Benchmark: 100%
    """
    if popn_total == 0 or pd.isna(popn_total):
        return 0
    return ((safely_managed + basic) / popn_total) * 100


def calculate_metering_ratio(metered, total_consumption):
    """
    Calculate Metering Ratio
    Formula: (metered ÷ total_consumption) × 100
    Benchmark: ≥95%
    """
    if total_consumption == 0 or pd.isna(total_consumption):
        return 0
    return (metered / total_consumption) * 100


def calculate_water_quality_compliance(tests_passed, tests_conducted):
    """
    Calculate Water Quality Compliance Rate
    Formula: (tests_passed ÷ tests_conducted) × 100
    Benchmark: ≥95%
    """
    if tests_conducted == 0 or pd.isna(tests_conducted):
        return 0
    return (tests_passed / tests_conducted) * 100


def calculate_staff_productivity(staff, connections):
    """
    Calculate Staff Productivity
    Formula: staff per 1000 connections
    Benchmark: ≤7 staff/1000 connections
    """
    if connections == 0 or pd.isna(connections):
        return 0
    return (staff / connections) * 1000


def calculate_complaint_resolution_rate(resolved, complaints):
    """
    Calculate Complaint Resolution Rate
    Formula: (resolved ÷ complaints) × 100
    Target: ≥90%
    """
    if complaints == 0 or pd.isna(complaints):
        return 0
    return (resolved / complaints) * 100


def calculate_ww_treatment_rate(ww_treated, ww_collected):
    """
    Calculate Wastewater Treatment Rate
    Formula: (ww_treated ÷ ww_collected) × 100
    """
    if ww_collected == 0 or pd.isna(ww_collected):
        return 0
    return (ww_treated / ww_collected) * 100


def get_kpi_status(value, benchmark, inverse=False):
    """
    Determine KPI status based on benchmark
    
    Args:
        value: Actual KPI value
        benchmark: Target benchmark value
        inverse: If True, lower is better (e.g., NRW)
    
    Returns:
        status: 'good', 'acceptable', 'poor'
        color: Color code for visualization
    """
    if pd.isna(value) or pd.isna(benchmark):
        return 'unknown', '#808080'
    
    if inverse:
        # For metrics like NRW where lower is better
        if value <= benchmark:
            return 'good', '#2ecc71'  # Green
        elif value <= benchmark * 1.5:
            return 'acceptable', '#f39c12'  # Amber
        else:
            return 'poor', '#e74c3c'  # Red
    else:
        # For metrics where higher is better
        if value >= benchmark:
            return 'good', '#2ecc71'  # Green
        elif value >= benchmark * 0.8:
            return 'acceptable', '#f39c12'  # Amber
        else:
            return 'poor', '#e74c3c'  # Red


def calculate_summary_kpis(data):
    """
    Calculate high-level summary KPIs for all countries
    
    Returns:
        dict: Dictionary of calculated KPIs with values and benchmarks
    """
    w_access = data.get('w_access', pd.DataFrame()).copy()
    s_access = data.get('s_access', pd.DataFrame()).copy()
    w_service = data.get('w_service', pd.DataFrame()).copy()
    finance = data.get('finance', pd.DataFrame()).copy()
    production = data.get('production', pd.DataFrame()).copy()
    national = data.get('national', pd.DataFrame()).copy()

    # Get latest year data where available
    latest_year = w_access['year'].max() if not w_access.empty else None
    if latest_year is not None:
        w_access_latest = w_access[w_access['year'] == latest_year]
        s_access_latest = s_access[s_access['year'] == latest_year] if not s_access.empty else s_access
        finance_latest_year = finance[finance['year'] == latest_year] if ('year' in finance.columns and not finance.empty) else finance
        national_latest = national[national['year'] == latest_year] if ('year' in national.columns and not national.empty) else national
    else:
        w_access_latest = w_access
        s_access_latest = s_access
        finance_latest_year = finance
        national_latest = national
    
    # Calculate aggregate KPIs
    kpis = {}
    
    # Water Coverage
    total_pop = w_access_latest['popn_total'].sum()
    total_safely_basic = (w_access_latest['safely_managed'] + w_access_latest['basic']).sum()
    kpis['water_coverage'] = {
        'value': (total_safely_basic / total_pop * 100) if total_pop > 0 else 0,
        'benchmark': 100,
        'unit': '%'
    }
    
    # Sanitation Coverage
    san_total_pop = s_access_latest['popn_total'].sum()
    san_safely_basic = (s_access_latest['safely_managed'] + s_access_latest['basic']).sum()
    kpis['sanitation_coverage'] = {
        'value': (san_safely_basic / san_total_pop * 100) if san_total_pop > 0 else 0,
        'benchmark': 100,
        'unit': '%'
    }
    
    # NRW (approximate from production vs metered)
    prod_total = production['production_m3'].sum()
    metered_total = w_service['metered'].sum()
    kpis['nrw'] = {
        'value': calculate_nrw(prod_total, metered_total),
        'benchmark': 25,
        'unit': '%',
        'inverse': True
    }
    
    # OCCR
    total_revenue = finance['sewer_revenue'].sum()
    total_opex = finance['opex'].sum()
    kpis['occr'] = {
        'value': calculate_occr(total_revenue, total_opex),
        'benchmark': 110,
        'unit': '%'
    }
    
    # Revenue Collection Efficiency
    kpis['collection_efficiency'] = {
        'value': calculate_collection_efficiency(total_revenue, finance['sewer_billed'].sum()),
        'benchmark': 95,
        'unit': '%'
    }
    
    # Water Quality (Chlorine)
    chlorine_passed = w_service['test_passed_chlorine'].sum()
    chlorine_conducted = w_service['tests_conducted_chlorine'].sum()
    kpis['water_quality'] = {
        'value': calculate_water_quality_compliance(chlorine_passed, chlorine_conducted),
        'benchmark': 95,
        'unit': '%'
    }
    
    # Metering Ratio
    kpis['metering_ratio'] = {
        'value': calculate_metering_ratio(metered_total, w_service['total_consumption'].sum()),
        'benchmark': 95,
        'unit': '%'
    }

    # Personnel Cost as % of O&M (latest year)
    staff_cost_total = national_latest['staff_cost'].sum() if not national_latest.empty else 0
    opex_latest = finance_latest_year['opex'].sum() if not finance_latest_year.empty else total_opex
    personnel_ratio = (staff_cost_total / opex_latest * 100) if opex_latest else 0
    kpis['personnel_cost_ratio'] = {
        'value': personnel_ratio,
        'benchmark': 35,
        'unit': '%',
        'inverse': True
    }

    # Staff Productivity (staff per 1000 connections/households)
    latest_connections = (
        w_service.sort_values('date')
        .dropna(subset=['households'])
        .groupby(['country', 'zone'], as_index=False)
        .tail(1)
    ) if 'zone' in w_service.columns else pd.DataFrame()

    total_connections = latest_connections['households'].sum() if not latest_connections.empty else w_service['households'].sum()
    total_staff = finance['san_staff'].sum() + finance['w_staff'].sum()
    staff_productivity = calculate_staff_productivity(total_staff, total_connections)
    kpis['staff_productivity'] = {
        'value': staff_productivity,
        'benchmark': 7,
        'unit': 'staff/1k',
        'inverse': True
    }

    
    # Service Hours (average)
    kpis['service_hours'] = {
        'value': production['service_hours'].mean(),
        'benchmark': 20,
        'unit': 'hrs/day'
    }
    
    return kpis


def calculate_country_kpis(data, country):
    """
    Calculate KPIs for a specific country
    
    Args:
        data: Dictionary of all datasets
        country: Country name
    
    Returns:
        dict: Country-specific KPIs
    """
    # Filter data by country
    w_access = data.get('w_access', pd.DataFrame())
    s_access = data.get('s_access', pd.DataFrame())
    w_service = data.get('w_service', pd.DataFrame())
    finance = data.get('finance', pd.DataFrame())
    production = data.get('production', pd.DataFrame())
    national = data.get('national', pd.DataFrame())

    w_access = w_access[w_access['country'] == country]
    s_access = s_access[s_access['country'] == country]
    w_service = w_service[w_service['country'] == country]
    finance = finance[finance['country'] == country]
    production = production[production['country'] == country]
    national = national[national['country'] == country]

    if w_access.empty or s_access.empty or w_service.empty or finance.empty or production.empty:
        return {
            'water_coverage': 0,
            'sanitation_coverage': 0,
            'nrw': 0,
            'occr': 0,
            'collection_efficiency': 0,
            'personnel_cost_ratio': 0,
            'staff_productivity': 0,
            'service_hours': 0,
            'water_quality': 0,
            'metering_ratio': 0
        }
    
    # Get latest year
    latest_year = w_access['year'].max()
    w_access_latest = w_access[w_access['year'] == latest_year]
    s_access_latest = s_access[s_access['year'] == latest_year]
    finance_latest_year = finance[finance['year'] == latest_year] if 'year' in finance.columns else finance
    national_latest = national[national['year'] == latest_year] if not national.empty else national
    
    kpis = {}
    
    # Water Coverage
    total_pop = w_access_latest['popn_total'].sum()
    total_safely_basic = (w_access_latest['safely_managed'] + w_access_latest['basic']).sum()
    kpis['water_coverage'] = (total_safely_basic / total_pop * 100) if total_pop > 0 else 0
    
    # Sanitation Coverage
    san_total_pop = s_access_latest['popn_total'].sum()
    san_safely_basic = (s_access_latest['safely_managed'] + s_access_latest['basic']).sum()
    kpis['sanitation_coverage'] = (san_safely_basic / san_total_pop * 100) if san_total_pop > 0 else 0
    
    # NRW
    prod_total = production['production_m3'].sum()
    metered_total = w_service['metered'].sum()
    kpis['nrw'] = calculate_nrw(prod_total, metered_total)
    
    # OCCR
    total_revenue = finance['sewer_revenue'].sum()
    total_opex = finance['opex'].sum()
    kpis['occr'] = calculate_occr(total_revenue, total_opex)
    
    # Collection Efficiency
    kpis['collection_efficiency'] = calculate_collection_efficiency(
        total_revenue, finance['sewer_billed'].sum()
    )

    # Personnel Cost Ratio
    staff_cost_total = national_latest['staff_cost'].sum() if not national_latest.empty else 0
    opex_latest = finance_latest_year['opex'].sum() if not finance_latest_year.empty else total_opex
    kpis['personnel_cost_ratio'] = (staff_cost_total / opex_latest * 100) if opex_latest else 0

    # Staff Productivity
    latest_connections = (
        w_service.sort_values('date')
        .dropna(subset=['households'])
        .groupby('zone', as_index=False)
        .tail(1)
    ) if 'zone' in w_service.columns else pd.DataFrame()

    total_connections = latest_connections['households'].sum() if not latest_connections.empty else w_service['households'].sum()
    total_staff = finance['san_staff'].sum() + finance['w_staff'].sum()
    kpis['staff_productivity'] = calculate_staff_productivity(total_staff, total_connections)

    # Service Hours
    kpis['service_hours'] = production['service_hours'].mean() if not production.empty else 0

    # Water Quality
    chlorine_passed = w_service['test_passed_chlorine'].sum()
    chlorine_conducted = w_service['tests_conducted_chlorine'].sum()
    kpis['water_quality'] = calculate_water_quality_compliance(chlorine_passed, chlorine_conducted)

    # Metering Ratio
    kpis['metering_ratio'] = calculate_metering_ratio(
        w_service['metered'].sum(),
        w_service['total_consumption'].sum()
    )
    
    return kpis


# ============================================================================
# CUSTOMER-LEVEL FINANCIAL ANALYSIS FUNCTIONS (NEW - for billing.csv)
# ============================================================================

def calculate_revenue_collection_efficiency_customer_level(billing_df, country=None, date_range=None):
    """
    Calculate RCE using billing.csv for customer-level granularity
    
    Args:
        billing_df: Customer billing dataframe
        country: Optional country filter (string or list)
        date_range: Optional (start_date, end_date) tuple
    
    Returns:
        tuple: (rce_percentage, total_billed, total_paid)
    """
    df = billing_df.copy()
    
    # Apply filters
    if country:
        if isinstance(country, str):
            df = df[df['country'] == country]
        else:
            df = df[df['country'].isin(country)]
    
    if date_range:
        df = df[(df['date'] >= pd.to_datetime(date_range[0])) & 
                (df['date'] <= pd.to_datetime(date_range[1]))]
    
    total_billed = df['billed'].sum()
    total_paid = df['paid'].sum()
    rce = (total_paid / total_billed * 100) if total_billed > 0 else 0
    
    return rce, total_billed, total_paid


def identify_payment_risk_customers(billing_df, threshold_high=0.5, threshold_medium=0.8):
    """
    Segment customers by payment behavior
    
    Args:
        billing_df: Customer billing dataframe
        threshold_high: Payment ratio below this is High Risk (default 0.5)
        threshold_medium: Payment ratio below this is Medium Risk (default 0.8)
    
    Returns:
        DataFrame with columns: customer_id, billed, paid, country, zone, 
                                payment_ratio, risk_category, unpaid_amount
    """
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


def calculate_commercial_nrw(billing_df, all_fin_service_df):
    """
    Calculate commercial NRW (revenue losses due to non-payment)
    
    Commercial losses represent the volume equivalent of unpaid bills.
    This is water that was delivered and billed but not paid for.
    
    Args:
        billing_df: Customer billing dataframe
        all_fin_service_df: Financial service dataframe
    
    Returns:
        float: Commercial losses in m³
    """
    total_billed_volume = billing_df['consumption_m3'].sum()
    
    # Calculate average tariff (revenue per m³)
    total_revenue = all_fin_service_df['sewer_revenue'].sum()
    total_billed_amount = billing_df['billed'].sum()
    
    if total_billed_volume == 0 or total_billed_amount == 0:
        return 0
    
    avg_tariff = total_revenue / total_billed_volume
    
    # Convert paid amount to volume equivalent
    total_paid = billing_df['paid'].sum()
    total_paid_volume_equivalent = total_paid / avg_tariff if avg_tariff > 0 else 0
    
    # Commercial losses = billed volume - paid volume equivalent
    commercial_losses = total_billed_volume - total_paid_volume_equivalent
    
    return max(commercial_losses, 0)  # Ensure non-negative


def calculate_physical_nrw(production_df, billing_df):
    """
    Calculate physical NRW (water lost through leaks, theft, meter inaccuracies)
    
    Physical losses represent actual water that was produced but never billed.
    This includes leaks, unauthorized connections, and meter under-registration.
    
    Args:
        production_df: Production dataframe
        billing_df: Customer billing dataframe
    
    Returns:
        float: Physical losses in m³
    """
    total_produced = production_df['production_m3'].sum()
    total_billed_volume = billing_df['consumption_m3'].sum()
    
    # Physical losses = produced - billed
    physical_losses = total_produced - total_billed_volume
    
    return max(physical_losses, 0)  # Ensure non-negative


def get_payment_by_zone(billing_df):
    """
    Aggregate payment data by zone for geographic analysis
    
    Args:
        billing_df: Customer billing dataframe
    
    Returns:
        DataFrame with columns: country, zone, total_billed, total_paid, 
                                customer_count, collection_rate
    """
    payment_by_zone = billing_df.groupby(['country', 'zone']).agg({
        'billed': 'sum',
        'paid': 'sum',
        'customer_id': 'count'
    }).reset_index()
    
    payment_by_zone.columns = ['country', 'zone', 'total_billed', 'total_paid', 'customer_count']
    payment_by_zone['collection_rate'] = (
        payment_by_zone['total_paid'] / payment_by_zone['total_billed'] * 100
    ).fillna(0)
    
    return payment_by_zone

