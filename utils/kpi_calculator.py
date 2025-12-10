"""
KPI Calculation Module
Contains all formulas and calculations for dashboard KPIs
"""

import pandas as pd
import numpy as np


# --- BENCHMARK CONSTANTS ---
# Centralized benchmarks to ensure consistency across all modules
BENCHMARKS = {
    'cost_recovery_ratio': 100,      # >= 100% to cover operating costs
    'collection_efficiency': 95,      # >= 95% target collection
    'nrw': 25,                        # <= 25% non-revenue water
    'water_coverage': 100,            # Target 100% coverage
    'sanitation_coverage': 100,       # Target 100% coverage
    'service_hours': 24,              # 24 hours/day target
    'water_quality': 95,              # >= 95% compliance
    'metering_ratio': 95,             # >= 95% metered
    'complaint_resolution': 90,       # >= 90% resolved
    'staff_productivity': 7,          # <= 7 staff/1000 connections
    'personnel_cost_ratio': 35,       # <= 35% of O&M
    'complaint_resolution_time': 5,   # <= 5 days
}


# --- CORE CALCULATIONS ---

def calculate_cost_recovery_ratio(revenue, opex):
    """
    Calculate Cost Recovery Ratio (CRR). Often OCCR is used for this.
    Formula: (total_revenue ÷ opex) × 100
    Benchmark: ≥100% (to cover operating costs)
    """
    if opex == 0 or pd.isna(opex):
        return 0
    return (revenue / opex) * 100


def calculate_nrw(production, billed_volume):
    """
    Calculate Non-Revenue Water (NRW)
    Formula: ((production_m3 - billed_volume) ÷ production_m3) × 100
    Benchmark: ≤25%
    
    Note: Returns 0 if metered > production (data quality issue)
    """
    if production == 0 or pd.isna(production):
        return 0
    
    nrw = ((production - billed_volume) / production) * 100
    # CRITICAL FIX: Ensure NRW cannot be negative (e.g., due to over-billing/metering)
    # This typically indicates a data quality issue (metered > production is impossible)
    return max(0.0, nrw)


def check_nrw_data_quality(production, metered):
    """
    Check for NRW data quality issues (metered > production)
    Returns True if there's a data quality issue
    """
    if production == 0 or pd.isna(production):
        return False
    return metered > production


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


# --- STATUS MAPPING ---

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

# -------------------------------------------------------------
# --- NEW HELPER FUNCTIONS FOR SUMMARY KPIs (Structural Fix) ---
# -------------------------------------------------------------

def calculate_access_rate_growth_yoy(access_df):
    """
    Calculate the year-over-year growth rate of water service access.
    Formula: (ACR_current - ACR_prev) / ACR_prev * 100
    """
    if access_df.empty or 'year' not in access_df.columns:
        return 0.0

    REQUIRED_COLS = ['year', 'safely_managed', 'basic', 'popn_total']
    if not all(col in access_df.columns for col in REQUIRED_COLS):
        return 0.0

    # Aggregate total access and total population by year
    annual_data = access_df.groupby('year')[REQUIRED_COLS[1:]].sum().reset_index()
    
    # Calculate Access Coverage Ratio (ACR) for each year
    annual_data['acr'] = (annual_data['safely_managed'] + annual_data['basic']) / annual_data['popn_total']
    
    annual_data = annual_data.sort_values('year')
    
    # Get the ACR from the previous year
    annual_data['acr_prev'] = annual_data['acr'].shift(1)
    
    latest_data = annual_data.dropna().iloc[-1] if not annual_data.dropna().empty else None
    
    if latest_data is None:
        return 0.0
        
    current_acr = latest_data['acr']
    previous_acr = latest_data['acr_prev']
    
    # Growth Calculation (YoY %)
    if previous_acr == 0:
        return 0.0 
    
    access_growth_rate = ((current_acr - previous_acr) / previous_acr) * 100
    
    return access_growth_rate


def calculate_complaints_kpis(finance_df, national_df):
    """
    Calculate Total Reported Complaints (from finance data) and 
    Average Resolution Time (from national data).
    
    Assumes: 
    1. 'complaints' in finance_df (from all_fin_service.csv)
    2. 'complaint_resolution' in national_df (from all_national.csv)
    """
    # 1. Total Reported Complaints (Count)
    # Note: Data uses 'complaints' column, not 'total_complaints'
    COMPLAINTS_COL = 'complaints' 
    if not finance_df.empty and COMPLAINTS_COL in finance_df.columns:
        total_complaints = finance_df[COMPLAINTS_COL].sum()
    else:
        total_complaints = 0
    
    
    # 2. Average Resolution Time (Days)
    RESOLUTION_TIME_COL = 'complaint_resolution' 
    if not national_df.empty and RESOLUTION_TIME_COL in national_df.columns:
        # Use mean as it represents the average time across all reported data points
        avg_resolution_time = national_df[RESOLUTION_TIME_COL].mean()
    else:
        avg_resolution_time = 0.0
        
    return total_complaints, avg_resolution_time


# -------------------------------------------------------------
# --- SUMMARY KPI CALCULATION (MAIN FOCUS) ---
# -------------------------------------------------------------

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
    latest_year = w_access['year'].max() if 'year' in w_access.columns and not w_access.empty else None
    
    if latest_year is not None:
        w_access_latest = w_access[w_access['year'] == latest_year]
        s_access_latest = s_access[s_access['year'] == latest_year] if 'year' in s_access.columns and not s_access.empty else s_access
        finance_latest_year = finance[finance['year'] == latest_year] if ('year' in finance.columns and not finance.empty) else finance
        national_latest = national[national['year'] == latest_year] if ('year' in national.columns and not national.empty) else national
        # For w_service, grab the latest date for household counts
        w_service_latest_date = w_service.sort_values('date').drop_duplicates(subset=['country', 'zone'], keep='last') if 'date' in w_service.columns else w_service
    else:
        w_access_latest = w_access
        s_access_latest = s_access
        finance_latest_year = finance
        national_latest = national
        w_service_latest_date = w_service
    
    # Calculate aggregate KPIs
    kpis = {}
    
    # --- 1. Total Households (FIXED) ---
    total_households_val = w_service_latest_date['households'].sum() if 'households' in w_service_latest_date.columns else 0
    kpis['total_households'] = {
        'value': total_households_val,
        'benchmark': 0, # No target, just reporting
        'unit': '',
        'inverse': False
    }
    
    # --- 2. Water Service Coverage (FIXED NAME) ---
    total_pop = w_access_latest['popn_total'].sum()
    total_safely_basic = (w_access_latest['safely_managed'] + w_access_latest['basic']).sum()
    kpis['water_service_coverage'] = {
        'value': (total_safely_basic / total_pop * 100) if total_pop > 0 else 0,
        'benchmark': 100,
        'unit': '%'
    }
    
    # --- 3. Access Rate Growth (FIXED - using YOY helper) ---
    kpis['access_rate_growth'] = {
        'value': calculate_access_rate_growth_yoy(w_access),
        'benchmark': 0.0,
        'unit': '%',
        'inverse': False # Higher is better
    }

    # --- 4. Revenue Collection Efficiency (EXISTING) ---
    total_revenue_billed = finance['sewer_revenue'].sum() # Assuming 'sewer_revenue' is the collected amount
    total_billing_amount = finance['sewer_billed'].sum()
    kpis['collection_efficiency'] = {
        'value': calculate_collection_efficiency(total_revenue_billed, total_billing_amount),
        'benchmark': 95,
        'unit': '%'
    }
    
    # --- 5. Cost Recovery Ratio (FIXED NAME) ---
    total_opex = finance['opex'].sum()
    # Assuming 'sewer_revenue' is the total operating revenue for this calculation
    kpis['cost_recovery_ratio'] = {
        'value': calculate_cost_recovery_ratio(total_revenue_billed, total_opex),
        'benchmark': 100, # Using 100% as the target for Cost Recovery
        'unit': '%'
    }
    
    # --- 6. Operational Profit/Loss (NEW) ---
    # Profit/Loss = Total Revenue - Total OPEX
    operational_pl_val = total_revenue_billed - total_opex
    kpis['operational_profit_loss'] = {
        'value': operational_pl_val,
        'benchmark': 0,
        'unit': '', # Currency unit implied
        'inverse': False
    }
    
    # --- 7. Non-Revenue Water (NRW) - Using billing consumption data for accuracy ---
    prod_total = production['production_m3'].sum()
    # Use billing consumption_m3 if available, otherwise fall back to w_service metered
    billing = data.get('billing', pd.DataFrame()).copy()
    if not billing.empty and 'consumption_m3' in billing.columns:
        billed_consumption = billing['consumption_m3'].sum()
    else:
        billed_consumption = w_service['metered'].sum() if 'metered' in w_service.columns else 0
    kpis['nrw'] = {
        'value': calculate_nrw(prod_total, billed_consumption),
        'benchmark': 25,
        'unit': '%',
        'inverse': True
    }
    
    # --- 8. Service Continuity (FIXED NAME) ---
    # Check if production is not empty before calculating mean
    service_continuity_val = production['service_hours'].mean() if 'service_hours' in production.columns and not production.empty else 0
    kpis['service_continuity'] = {
        'value': service_continuity_val,
        'benchmark': 24, # Target is 24 hours
        'unit': 'hrs/day'
    }

    # --- 9. Reported Complaints (Total) (FIXED - using complaints helper) ---
    # --- 10. Avg. Resolution Time (Days) (FIXED - using complaints helper) ---
    complaints_count_val, complaint_resolution_time_val = calculate_complaints_kpis(finance, national_latest)

    kpis['complaints_count'] = {
        'value': complaints_count_val,
        'benchmark': 0, # No target, just reporting
        'unit': ''
    }
    
    kpis['complaint_resolution_time'] = {
        'value': complaint_resolution_time_val,
        'benchmark': 5,
        'unit': ' days',
        'inverse': True # Lower days is better
    }
    
    # --- The old Sanitation, Personnel, Water Quality, and Metering KPIs are kept in this file 
    # but removed from the summary KPI list in overview.py (as per the user's focus on 10 specific KPIs)

    # Sanitation Coverage (still calculated if needed for other pages)
    san_total_pop = s_access_latest['popn_total'].sum()
    san_safely_basic = (s_access_latest['safely_managed'] + s_access_latest['basic']).sum()
    kpis['sanitation_coverage'] = {
        'value': (san_safely_basic / san_total_pop * 100) if san_total_pop > 0 else 0,
        'benchmark': 100,
        'unit': '%'
    }
    
    # Water Quality (Chlorine)
    chlorine_passed = w_service['test_passed_chlorine'].sum() if 'test_passed_chlorine' in w_service.columns else 0
    chlorine_conducted = w_service['tests_conducted_chlorine'].sum() if 'tests_conducted_chlorine' in w_service.columns else 0
    kpis['water_quality'] = {
        'value': calculate_water_quality_compliance(chlorine_passed, chlorine_conducted),
        'benchmark': 95,
        'unit': '%'
    }
    
    # Metering Ratio
    metered_total = w_service['metered'].sum() if 'metered' in w_service.columns else 0
    total_consumption = w_service['total_consumption'].sum() if 'total_consumption' in w_service.columns else 0
    kpis['metering_ratio'] = {
        'value': calculate_metering_ratio(metered_total, total_consumption),
        'benchmark': 95,
        'unit': '%'
    }

    # Personnel Cost as % of O&M (latest year)
    staff_cost_total = national_latest['staff_cost'].sum() if 'staff_cost' in national_latest.columns and not national_latest.empty else 0
    opex_latest = finance_latest_year['opex'].sum() if 'opex' in finance_latest_year.columns and not finance_latest_year.empty else total_opex
    personnel_ratio = (staff_cost_total / opex_latest * 100) if opex_latest else 0
    kpis['personnel_cost_ratio'] = {
        'value': personnel_ratio,
        'benchmark': 35,
        'unit': '%',
        'inverse': True
    }

    # Staff Productivity (staff per 1000 connections/households)
    total_connections = total_households_val
    total_staff = finance['san_staff'].sum() + finance['w_staff'].sum() if 'san_staff' in finance.columns and 'w_staff' in finance.columns else 0
    staff_productivity = calculate_staff_productivity(total_staff, total_connections)
    kpis['staff_productivity'] = {
        'value': staff_productivity,
        'benchmark': 7,
        'unit': 'staff/1k',
        'inverse': True
    }
    
    return kpis


# -------------------------------------------------------------
# --- COUNTRY KPI CALCULATION ---
# -------------------------------------------------------------

def calculate_country_kpis(data, country):
    """
    Calculate KPIs for a specific country
    
    Args:
        data: Dictionary of all datasets
        country: Country name
    
    Returns:
        dict: Country-specific KPIs
    """
    # Filter data by country (using copy for safety)
    w_access = data.get('w_access', pd.DataFrame()).copy()
    s_access = data.get('s_access', pd.DataFrame()).copy()
    w_service = data.get('w_service', pd.DataFrame()).copy()
    finance = data.get('finance', pd.DataFrame()).copy()
    production = data.get('production', pd.DataFrame()).copy()
    national = data.get('national', pd.DataFrame()).copy()

    w_access = w_access[w_access['country'] == country]
    s_access = s_access[s_access['country'] == country]
    w_service = w_service[w_service['country'] == country]
    finance = finance[finance['country'] == country]
    production = production[production['country'] == country]
    national = national[national['country'] == country]

    # Ensure all dataframes are not empty after filtering
    if w_access.empty and s_access.empty and w_service.empty and finance.empty and production.empty:
        # Return a dictionary with all keys set to 0 to prevent errors in AI context building
        return {
            'total_households': 0,
            'water_service_coverage': 0,
            'access_rate_growth': 0,
            'collection_efficiency': 0,
            'cost_recovery_ratio': 0,
            'operational_profit_loss': 0,
            'nrw': 0,
            'service_continuity': 0,
            'complaints_count': 0,
            'complaint_resolution_time': 0,
            'sanitation_coverage': 0,
            'personnel_cost_ratio': 0,
            'staff_productivity': 0,
            'water_quality': 0,
            'metering_ratio': 0
        }
    
    # Get latest year
    latest_year = w_access['year'].max() if 'year' in w_access.columns and not w_access.empty else None
    
    if latest_year is not None:
        w_access_latest = w_access[w_access['year'] == latest_year]
        s_access_latest = s_access[s_access['year'] == latest_year]
        finance_latest_year = finance[finance['year'] == latest_year] if 'year' in finance.columns else finance
        national_latest = national[national['year'] == latest_year] if not national.empty else national
        w_service_latest_date = w_service.sort_values('date').drop_duplicates(subset=['zone'], keep='last') if 'date' in w_service.columns else w_service
    else:
        w_access_latest = w_access
        s_access_latest = s_access
        finance_latest_year = finance
        national_latest = national
        w_service_latest_date = w_service
    
    kpis = {}
    
    # Water Coverage (FIXED NAME)
    total_pop = w_access_latest['popn_total'].sum()
    total_safely_basic = (w_access_latest['safely_managed'] + w_access_latest['basic']).sum()
    kpis['water_service_coverage'] = (total_safely_basic / total_pop * 100) if total_pop > 0 else 0
    
    # Sanitation Coverage
    san_total_pop = s_access_latest['popn_total'].sum()
    san_safely_basic = (s_access_latest['safely_managed'] + s_access_latest['basic']).sum()
    kpis['sanitation_coverage'] = (san_safely_basic / san_total_pop * 100) if san_total_pop > 0 else 0
    
    # NRW - Using billing consumption data for accuracy
    prod_total = production['production_m3'].sum()
    # Use billing consumption_m3 if available
    billing = data.get('billing', pd.DataFrame()).copy()
    if not billing.empty and 'consumption_m3' in billing.columns:
        billing_filtered = billing[billing['country'] == country]
        billed_consumption = billing_filtered['consumption_m3'].sum()
    else:
        billed_consumption = w_service['metered'].sum() if 'metered' in w_service.columns else 0
    kpis['nrw'] = calculate_nrw(prod_total, billed_consumption)
    
    # Cost Recovery Ratio (FIXED NAME)
    total_revenue_billed = finance['sewer_revenue'].sum()
    total_opex = finance['opex'].sum()
    kpis['cost_recovery_ratio'] = calculate_cost_recovery_ratio(total_revenue_billed, total_opex)
    
    # Operational Profit/Loss (NEW)
    kpis['operational_profit_loss'] = total_revenue_billed - total_opex
    
    # Collection Efficiency
    kpis['collection_efficiency'] = calculate_collection_efficiency(
        total_revenue_billed, finance['sewer_billed'].sum()
    )

    # Personnel Cost Ratio
    staff_cost_total = national_latest['staff_cost'].sum() if 'staff_cost' in national_latest.columns and not national_latest.empty else 0
    opex_latest = finance_latest_year['opex'].sum() if 'opex' in finance_latest_year.columns and not finance_latest_year.empty else total_opex
    kpis['personnel_cost_ratio'] = (staff_cost_total / opex_latest * 100) if opex_latest else 0

    # Total Households (NEW)
    total_connections = w_service_latest_date['households'].sum() if 'households' in w_service_latest_date.columns else 0
    kpis['total_households'] = total_connections

    # Staff Productivity
    total_staff = finance['san_staff'].sum() + finance['w_staff'].sum() if 'san_staff' in finance.columns and 'w_staff' in finance.columns else 0
    kpis['staff_productivity'] = calculate_staff_productivity(total_staff, total_connections)

    # Service Continuity (FIXED NAME)
    kpis['service_continuity'] = production['service_hours'].mean() if 'service_hours' in production.columns and not production.empty else 0

    # Water Quality
    chlorine_passed = w_service['test_passed_chlorine'].sum() if 'test_passed_chlorine' in w_service.columns else 0
    chlorine_conducted = w_service['tests_conducted_chlorine'].sum() if 'tests_conducted_chlorine' in w_service.columns else 0
    kpis['water_quality'] = calculate_water_quality_compliance(chlorine_passed, chlorine_conducted)

    # Metering Ratio
    kpis['metering_ratio'] = calculate_metering_ratio(
        w_service['metered'].sum(),
        w_service['total_consumption'].sum()
    )
    
    # Access Rate Growth
    kpis['access_rate_growth'] = calculate_access_rate_growth_yoy(w_access)
    
    # Complaints KPIs
    complaints_count_val, complaint_resolution_time_val = calculate_complaints_kpis(finance, national_latest)
    kpis['complaints_count'] = complaints_count_val
    kpis['complaint_resolution_time'] = complaint_resolution_time_val
    
    return kpis

# -------------------------------------------------------------
# --- NEW FUNCTION FOR AI CONTEXT ---
# -------------------------------------------------------------

def calculate_all_country_kpis(data_filtered):
    """
    Calculates KPIs for ALL countries present in the filtered data.
    
    Returns:
        dict: A dictionary where keys are country names and values are their KPI dictionaries.
    """
    country_kpis_dict = {}
    
    # Get all unique countries from the 'w_access' DataFrame, if available
    w_access = data_filtered.get('w_access', pd.DataFrame())
    
    if 'country' in w_access.columns and not w_access.empty:
        unique_countries = w_access['country'].unique()
        
        for country in unique_countries:
            # Re-call calculate_country_kpis for each country
            country_kpis_dict[country] = calculate_country_kpis(data_filtered, country)
            
    return country_kpis_dict

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
        df['date'] = pd.to_datetime(df['date']) # Ensure date is datetime
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
    
    # Estimate the average price per billed unit (m3) based on total revenue and billed volume
    avg_tariff = total_revenue / total_billed_volume if total_billed_volume > 0 else 0
    
    # Convert paid amount to volume equivalent
    total_paid = billing_df['paid'].sum()
    # If the total paid amount was applied to the billed volume, how much volume does that represent?
    total_paid_volume_equivalent = total_paid / avg_tariff if avg_tariff > 0 else 0
    
    # Commercial losses = billed volume - paid volume equivalent (this is the volume that wasn't paid for)
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
        'customer_id': 'nunique' # Count unique customers in the zone
    }).reset_index()
    
    payment_by_zone.columns = ['country', 'zone', 'total_billed', 'total_paid', 'customer_count']
    payment_by_zone['collection_rate'] = (
        payment_by_zone['total_paid'] / payment_by_zone['total_billed'] * 100
    ).fillna(0)
    
    return payment_by_zone