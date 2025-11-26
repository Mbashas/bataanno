"""
Data Loading and Preprocessing Module
Handles loading all CSV files and preparing data for analysis
"""

import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple, Union, Any

logger = logging.getLogger(__name__)

# Data directory path
DATA_DIR = Path(__file__).parent.parent / "Data"

# Updated column mapping based on your actual CSV files
COLUMN_MAPPINGS = {
    'w_service': {
        'required': ['date_MMYY', 'country'],
        'optional': {
            'customers': ['households'],
            'supply_hours': ['service_hours'],
            'metered': ['metered'],
            'total_consumption': ['total_consumption'],
            'test_passed_chlorine': ['test_passed_chlorine'],
            'tests_conducted_chlorine': ['tests_conducted_chlorine'],
            'households': ['households'],
            'w_supplied': ['w_supplied']
        }
    },
    's_service': {
        'required': ['date_MMYY', 'country'],
        'optional': {
            'customers': ['households'],
            'treatment_quality': ['ww_treated'],
            'households': ['households'],
            'sewer_connections': ['sewer_connections'],
            'ww_collected': ['ww_collected'],
            'ww_treated': ['ww_treated'],
            'ww_reused': ['ww_reused']
        }
    },
    'w_access': {
        'required': ['date_YY', 'country'],
        'optional': {
            'population': ['popn_total'],
            'access_rate': ['safely_managed_pct', 'basic_pct'],
            'safely_managed': ['safely_managed'],
            'basic': ['basic'],
            'limited': ['limited'],
            'unimproved': ['unimproved'],
            'surface_water': ['surface_water'],
            'municipal_coverage': ['municipal_coverage'],
            'popn_total': ['popn_total'],
            'households': ['households']
        }
    },
    's_access': {
        'required': ['date_YY', 'country'],
        'optional': {
            'population': ['popn_total'],
            'access_rate': ['safely_managed_pct', 'basic_pct'],
            'safely_managed': ['safely_managed'],
            'basic': ['basic'],
            'limited': ['limited'],
            'unimproved': ['unimproved'],
            'open_def': ['open_def'],
            'popn_total': ['popn_total'],
            'households': ['households']
        }
    },
    'finance': {
        'required': ['date_MMYY', 'country'],
        'optional': {
            'revenue': ['sewer_revenue'],
            'expenses': ['opex'],
            'collection_rate': ['sewer_revenue', 'sewer_billed'],
            'sewer_billed': ['sewer_billed'],
            'sewer_revenue': ['sewer_revenue'],
            'opex': ['opex'],
            'w_staff': ['w_staff'],
            'san_staff': ['san_staff'],
            'propoor_popn': ['propoor_popn']
        }
    },
    'national': {
        'required': ['date_YY', 'country'],
        'optional': {
            'gdp': ['water_resources'],
            'population': ['popn_total'],
            'water_investment': ['wat_allocation'],
            'staff_cost': ['staff_cost'],
            'wat_allocation': ['wat_allocation'],
            'san_allocation': ['san_allocation']
        }
    },
    'production': {
        'required': ['date_YYMMDD', 'country'],
        'optional': {
            'production_m3': ['production_m3'],
            'source': ['source'],
            'service_hours': ['service_hours']
        }
    },
    'billing': {
        'required': ['date', 'country'],
        'optional': {
            'customer_id': ['customer_id'],
            'billed': ['billed'],
            'paid': ['paid'],
            'consumption_m3': ['consumption_m3'],
            'zone': ['zone'],
            'source': ['source']
        }
    }
}

def _find_column(df, possible_names):
    """Find a column in dataframe using possible names"""
    for name in possible_names:
        if name in df.columns:
            return name
    return None

def _safe_read_csv(file_path: Path, dataset_name: str) -> pd.DataFrame:
    """Safely read CSV file with comprehensive error handling"""
    try:
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return pd.DataFrame()
        
        # Use low_memory=False to handle mixed types and avoid DtypeWarning
        df = pd.read_csv(file_path, low_memory=False)
        logger.info(f"Successfully loaded {file_path.name} with {len(df)} rows, {len(df.columns)} columns")
        
        return df
        
    except Exception as e:
        logger.error(f"Error loading {file_path}: {str(e)}")
        return pd.DataFrame()

def _map_columns(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    """Map actual columns to expected column names"""
    if df.empty:
        return df
    
    mapping_info = COLUMN_MAPPINGS.get(dataset_name, {})
    required_cols = mapping_info.get('required', [])
    optional_mappings = mapping_info.get('optional', {})
    
    # Check required columns
    missing_required = []
    for col in required_cols:
        if col not in df.columns:
            missing_required.append(col)
    
    if missing_required:
        logger.warning(f"Missing required columns in {dataset_name}: {missing_required}")
    
    # Map optional columns
    column_mapping = {}
    for expected_col, possible_names in optional_mappings.items():
        actual_col = _find_column(df, possible_names)
        if actual_col and actual_col != expected_col:
            column_mapping[actual_col] = expected_col
            logger.info(f"Mapping {actual_col} -> {expected_col} in {dataset_name}")
    
    if column_mapping:
        df = df.rename(columns=column_mapping)
    
    return df

def _calculate_derived_columns(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    """Calculate derived columns that don't exist in raw data"""
    if df.empty:
        return df
    
    try:
        if dataset_name == 'w_access':
            if 'safely_managed_pct' in df.columns and 'basic_pct' in df.columns:
                df['access_rate'] = df['safely_managed_pct'] + df['basic_pct']
            elif 'safely_managed' in df.columns and 'basic' in df.columns and 'popn_total' in df.columns:
                df['access_rate'] = (df['safely_managed'] + df['basic']) / df['popn_total'] * 100
        
        elif dataset_name == 's_access':
            if 'safely_managed_pct' in df.columns and 'basic_pct' in df.columns:
                df['access_rate'] = df['safely_managed_pct'] + df['basic_pct']
            elif 'safely_managed' in df.columns and 'basic' in df.columns and 'popn_total' in df.columns:
                df['access_rate'] = (df['safely_managed'] + df['basic']) / df['popn_total'] * 100
        
        elif dataset_name == 'finance':
            if 'sewer_revenue' in df.columns and 'sewer_billed' in df.columns:
                df['collection_rate'] = np.where(
                    df['sewer_billed'] > 0,
                    (df['sewer_revenue'] / df['sewer_billed']) * 100,
                    0
                )
        
        elif dataset_name == 'w_service':
            # Add supply_hours from production data if missing
            if 'supply_hours' not in df.columns:
                df['supply_hours'] = None
        
        elif dataset_name == 's_service':
            # Calculate treatment quality if ww_treated and ww_collected exist
            if 'ww_treated' in df.columns and 'ww_collected' in df.columns:
                df['treatment_quality'] = np.where(
                    df['ww_collected'] > 0,
                    (df['ww_treated'] / df['ww_collected']) * 100,
                    0
                )
        
    except Exception as e:
        logger.warning(f"Error calculating derived columns for {dataset_name}: {e}")
    
    return df

@st.cache_data(ttl=3600, show_spinner="Loading production data...")
def load_production_data() -> pd.DataFrame:
    """Load and preprocess production data"""
    df = _safe_read_csv(DATA_DIR / "production.csv", 'production')
    df = _map_columns(df, 'production')
    df = _calculate_derived_columns(df, 'production')
    
    if df.empty:
        return pd.DataFrame()
    
    # Parse dates
    df = _handle_date_parsing(df, 'date_YYMMDD', '%Y/%m/%d')
    df = _standardize_country_names(df)
    
    return df

@st.cache_data(ttl=3600, show_spinner="Loading water service data...")
def load_w_service_data() -> pd.DataFrame:
    """Load and preprocess water service data"""
    df = _safe_read_csv(DATA_DIR / "w_service.csv", 'w_service')
    df = _map_columns(df, 'w_service')
    df = _calculate_derived_columns(df, 'w_service')
    
    if df.empty:
        return pd.DataFrame()
    
    # Parse dates (format: Jan/20)
    df = _handle_date_parsing(df, 'date_MMYY', '%b/%y')
    df = _standardize_country_names(df)
    
    return df

@st.cache_data(ttl=3600, show_spinner="Loading sanitation service data...")
def load_s_service_data() -> pd.DataFrame:
    """Load and preprocess sanitation service data"""
    df = _safe_read_csv(DATA_DIR / "s_service.csv", 's_service')
    df = _map_columns(df, 's_service')
    df = _calculate_derived_columns(df, 's_service')
    
    if df.empty:
        return pd.DataFrame()
    
    # Parse dates (format: Jan/20)
    df = _handle_date_parsing(df, 'date_MMYY', '%b/%y')
    df = _standardize_country_names(df)
    
    return df

@st.cache_data(ttl=3600, show_spinner="Loading water access data...")
def load_w_access_data() -> pd.DataFrame:
    """Load and preprocess water access data"""
    df = _safe_read_csv(DATA_DIR / "w_access.csv", 'w_access')
    df = _map_columns(df, 'w_access')
    df = _calculate_derived_columns(df, 'w_access')
    
    if df.empty:
        return pd.DataFrame()
    
    # Parse dates (format: 2020)
    df = _handle_date_parsing(df, 'date_YY', '%Y')
    df = _standardize_country_names(df)
    
    return df

@st.cache_data(ttl=3600, show_spinner="Loading sanitation access data...")
def load_s_access_data() -> pd.DataFrame:
    """Load and preprocess sanitation access data"""
    df = _safe_read_csv(DATA_DIR / "s_access.csv", 's_access')
    df = _map_columns(df, 's_access')
    df = _calculate_derived_columns(df, 's_access')
    
    if df.empty:
        return pd.DataFrame()
    
    # Parse dates (format: 2020)
    df = _handle_date_parsing(df, 'date_YY', '%Y')
    df = _standardize_country_names(df)
    
    return df

@st.cache_data(ttl=3600, show_spinner="Loading financial data...")
def load_finance_data() -> pd.DataFrame:
    """Load and preprocess financial service data"""
    df = _safe_read_csv(DATA_DIR / "all_fin_service.csv", 'finance')
    df = _map_columns(df, 'finance')
    df = _calculate_derived_columns(df, 'finance')
    
    if df.empty:
        return pd.DataFrame()
    
    # Parse dates (format: Jan/20)
    df = _handle_date_parsing(df, 'date_MMYY', '%b/%y')
    df = _standardize_country_names(df)
    
    return df

@st.cache_data(ttl=3600, show_spinner="Loading national data...")
def load_national_data() -> pd.DataFrame:
    """Load and preprocess national accounts data"""
    df = _safe_read_csv(DATA_DIR / "all_national.csv", 'national')
    df = _map_columns(df, 'national')
    df = _calculate_derived_columns(df, 'national')
    
    if df.empty:
        return pd.DataFrame()
    
    # Parse dates (format: 2020)
    df = _handle_date_parsing(df, 'date_YY', '%Y')
    df = _standardize_country_names(df)
    
    return df

@st.cache_data(ttl=3600, show_spinner="Loading billing data...")
def load_billing_data() -> pd.DataFrame:
    """Load and preprocess customer billing data"""
    df = _safe_read_csv(DATA_DIR / "billing.csv", 'billing')
    df = _map_columns(df, 'billing')
    df = _calculate_derived_columns(df, 'billing')
    
    if df.empty:
        return pd.DataFrame()
    
    # Parse dates - handle multiple formats
    df = _handle_billing_dates(df)
    df = _standardize_country_names(df)
    
    return df

def _handle_date_parsing(df: pd.DataFrame, date_column: str, date_format: str) -> pd.DataFrame:
    """Handle date parsing with comprehensive error handling"""
    if date_column not in df.columns:
        return df
    
    try:
        df['date'] = pd.to_datetime(df[date_column], format=date_format, errors='coerce')
        
        # Add year and month columns
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        
        return df
    except Exception as e:
        logger.error(f"Error parsing dates: {e}")
        return df

def _handle_billing_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Handle billing date parsing with multiple formats"""
    if 'date' not in df.columns:
        return df
    
    try:
        # Try multiple date formats
        date_formats = ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
        
        for date_format in date_formats:
            try:
                df['date'] = pd.to_datetime(df['date'], format=date_format, errors='coerce')
                if not df['date'].isna().all():
                    break
            except:
                continue
        
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        
        return df
    except Exception as e:
        logger.error(f"Error parsing billing dates: {e}")
        return df

def _standardize_country_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize country names across all datasets"""
    if 'country' in df.columns:
        df['country'] = (
            df['country']
            .astype(str)
            .str.strip()
            .str.title()
        )
    return df

@st.cache_data(ttl=3600, show_spinner="Loading all datasets...")
def load_all_data() -> Dict[str, pd.DataFrame]:
    """Load all datasets at once"""
    datasets = {
        'production': load_production_data(),
        'w_service': load_w_service_data(),
        's_service': load_s_service_data(),
        'w_access': load_w_access_data(),
        's_access': load_s_access_data(),
        'finance': load_finance_data(),
        'national': load_national_data(),
        'billing': load_billing_data()
    }
    
    # Log loading statistics
    loaded_stats = {}
    empty_datasets = []
    
    for name, df in datasets.items():
        if df.empty:
            empty_datasets.append(name)
        else:
            loaded_stats[name] = f"{len(df)} rows, {len(df.columns)} columns"
    
    if loaded_stats:
        logger.info(f"Successfully loaded datasets: {list(loaded_stats.keys())}")
    if empty_datasets:
        logger.warning(f"Empty or failed datasets: {empty_datasets}")
    
    return datasets

def apply_filters(data: Dict[str, pd.DataFrame], countries: Optional[List[str]] = None, 
                 zones: Optional[List[str]] = None, date_range: Optional[Tuple] = None) -> Dict[str, pd.DataFrame]:
    """Apply filters to datasets"""
    if not data:
        return {}

    filtered = {}
    start_date = end_date = None

    if date_range and len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

    for name, df in data.items():
        if df is None or len(df) == 0:
            filtered[name] = df
            continue

        temp_df = df.copy()

        # Apply country filter
        if countries and 'country' in temp_df.columns:
            temp_df = temp_df[temp_df['country'].isin(countries)]

        # Apply zone filter
        if zones and 'zone' in temp_df.columns and name != 'production':
            temp_df = temp_df[temp_df['zone'].isin(zones)]

        # Apply date range filter
        if start_date is not None and end_date is not None and 'date' in temp_df.columns:
            temp_df = temp_df[
                (temp_df['date'] >= start_date) &
                (temp_df['date'] <= end_date)
            ]

        filtered[name] = temp_df

    return filtered

def get_data_summary(data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Get data summary"""
    summary = {}
    
    for name, df in data.items():
        if df is None or df.empty:
            summary[name] = {'status': 'Empty or failed to load', 'rows': 0, 'columns': 0}
            continue
            
        summary[name] = {
            'status': 'Loaded',
            'rows': len(df),
            'columns': len(df.columns),
            'date_range': None,
            'countries': [],
            'memory_mb': round(df.memory_usage(deep=True).sum() / 1024**2, 2)
        }
        
        # Date range
        if 'date' in df.columns and not df['date'].isna().all():
            valid_dates = df[df['date'].notna()]
            if not valid_dates.empty:
                summary[name]['date_range'] = {
                    'min': valid_dates['date'].min().strftime('%Y-%m-%d'),
                    'max': valid_dates['date'].max().strftime('%Y-%m-%d')
                }
        
        # Countries
        if 'country' in df.columns:
            summary[name]['countries'] = sorted(df['country'].unique().tolist())
    
    return summary

def get_available_countries():
    """Get list of available countries across all datasets"""
    all_data = load_all_data()
    countries = set()
    
    for df in all_data.values():
        if not df.empty and 'country' in df.columns:
            countries.update(df['country'].unique())
    
    return sorted([c for c in countries if c and c != 'Unknown'])

def get_available_years():
    """Get list of available years across all datasets"""
    all_data = load_all_data()
    years = set()
    
    for df in all_data.values():
        if not df.empty and 'year' in df.columns:
            years.update(df['year'].dropna().unique())
    
    return sorted([int(y) for y in years if pd.notna(y)])

def get_available_zones():
    """Get list of available zones across zone-based datasets"""
    all_data = load_all_data()
    zones = set()
    
    zone_datasets = ['w_service', 's_service', 'w_access', 's_access']
    for name in zone_datasets:
        df = all_data.get(name)
        if df is not None and not df.empty and 'zone' in df.columns:
            zones.update(df['zone'].dropna().unique())
    
    return sorted([z for z in zones if z and z != 'Unknown'])

def get_latest_update_date():
    """Get the latest data update date from all datasets"""
    all_data = load_all_data()
    latest_dates = []
    
    for name, df in all_data.items():
        if not df.empty and 'date' in df.columns:
            latest_date = df['date'].max()
            if pd.notna(latest_date):
                latest_dates.append(latest_date)
    
    if latest_dates:
        return max(latest_dates).strftime('%B %d, %Y')
    return "Unknown"

def filter_by_country(df: pd.DataFrame, countries: List[str]) -> pd.DataFrame:
    """Filter dataframe by selected countries"""
    if not countries or 'country' not in df.columns:
        return df
    return df[df['country'].isin(countries)]

def filter_by_date_range(df: pd.DataFrame, start_date: Union[str, datetime], end_date: Union[str, datetime]) -> pd.DataFrame:
    """Filter dataframe by date range"""
    if 'date' not in df.columns:
        return df
    
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)
    
    return df[(df['date'] >= start_dt) & (df['date'] <= end_dt)]

# Test function
if __name__ == "__main__":
    # Test data loading
    print("Testing data loading...")
    all_data = load_all_data()
    summary = get_data_summary(all_data)
    
    print("\nData Loading Summary:")
    for name, stats in summary.items():
        print(f"{name}: {stats['status']} - {stats['rows']} rows, {stats['columns']} columns")
    
    print(f"\nAvailable countries: {get_available_countries()}")
    print(f"Available years: {get_available_years()}")
    print(f"Latest update: {get_latest_update_date()}")
    # Add these debugging functions to your data_loader.py

def check_data_quality(df, dataset_name=""):
    """
    Check basic data quality metrics for a DataFrame
    """
    if df is None or df.empty:
        return f"❌ {dataset_name}: DataFrame is empty or None"
    
    result = {
        'dataset': dataset_name,
        'rows': len(df),
        'columns': len(df.columns),
        'null_values': df.isnull().sum().sum(),
        'duplicate_rows': df.duplicated().sum(),
        'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024**2, 2)
    }
    
    return result

def validate_kpi_calculations(data_dict):
    """
    Validate that KPI calculations can run with provided data
    """
    validation_results = {}
    
    required_datasets = ['production', 'w_service', 's_service', 
                        'w_access', 's_access', 'finance']
    
    for dataset in required_datasets:
        if dataset in data_dict and data_dict[dataset] is not None and not data_dict[dataset].empty:
            validation_results[dataset] = {
                'status': '✅ Available',
                'shape': data_dict[dataset].shape,
                'columns': list(data_dict[dataset].columns)
            }
        else:
            validation_results[dataset] = {
                'status': '❌ Missing or Empty',
                'shape': None,
                'columns': []
            }
    
    return validation_results

def safe_data_loader(loader_function, *args, **kwargs):
    """
    Safely execute data loader functions with error handling
    """
    try:
        result = loader_function(*args, **kwargs)
        return result, None
    except Exception as e:
        return None, f"Error loading data: {str(e)}"

def kpi_calculation_wrapper(calculation_function, data, *args, **kwargs):
    """
    Safely execute KPI calculations with error handling
    """
    try:
        result = calculation_function(data, *args, **kwargs)
        return result, None
    except Exception as e:
        return None, f"Error in KPI calculation: {str(e)}"

def visualization_safe_mode(visualization_function, *args, **kwargs):
    """
    Safely create visualizations with error handling
    """
    try:
        result = visualization_function(*args, **kwargs)
        return result, None
    except Exception as e:
        return None, f"Error creating visualization: {str(e)}"