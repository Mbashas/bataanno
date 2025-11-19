"""
Data Loading and Preprocessing Module
Handles loading all CSV files and preparing data for analysis
"""

import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path
from datetime import datetime

# Data directory path
DATA_DIR = Path(__file__).parent.parent / "Data"


@st.cache_data(ttl=3600)
def load_production_data():
    """Load and preprocess production data (daily, by source)"""
    df = pd.read_csv(DATA_DIR / "production.csv")
    
    # Parse dates
    df['date'] = pd.to_datetime(df['date_YYMMDD'], format='%Y/%m/%d', errors='coerce')
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['country'] = df['country'].str.strip().str.title()
    
    return df


@st.cache_data(ttl=3600)
def load_w_service_data():
    """Load and preprocess water service data (monthly, by zone)"""
    df = pd.read_csv(DATA_DIR / "w_service.csv")
    
    # Parse dates (format: Jan/20)
    df['date'] = pd.to_datetime(df['date_MMYY'], format='%b/%y', errors='coerce')
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['country'] = df['country'].str.strip().str.title()
    
    return df


@st.cache_data(ttl=3600)
def load_s_service_data():
    """Load and preprocess sanitation service data (monthly, by zone)"""
    df = pd.read_csv(DATA_DIR / "s_service.csv")
    
    # Parse dates (format: Jan/20)
    df['date'] = pd.to_datetime(df['date_MMYY'], format='%b/%y', errors='coerce')
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['country'] = df['country'].str.strip().str.title()
    
    return df


@st.cache_data(ttl=3600)
def load_w_access_data():
    """Load and preprocess water access data (annual, by zone)"""
    df = pd.read_csv(DATA_DIR / "w_access.csv")
    
    # Parse dates (format: 2020)
    df['date'] = pd.to_datetime(df['date_YY'], format='%Y', errors='coerce')
    df['year'] = df['date'].dt.year
    df['country'] = df['country'].str.strip().str.title()
    
    return df


@st.cache_data(ttl=3600)
def load_s_access_data():
    """Load and preprocess sanitation access data (annual, by zone)"""
    df = pd.read_csv(DATA_DIR / "s_access.csv")
    
    # Parse dates (format: 2020)
    df['date'] = pd.to_datetime(df['date_YY'], format='%Y', errors='coerce')
    df['year'] = df['date'].dt.year
    df['country'] = df['country'].str.strip().str.title()
    
    return df


@st.cache_data(ttl=3600)
def load_finance_data():
    """Load and preprocess financial service data (monthly, by city)"""
    df = pd.read_csv(DATA_DIR / "all_fin_service.csv")
    
    # Parse dates (format: Jan/20)
    df['date'] = pd.to_datetime(df['date_MMYY'], format='%b/%y', errors='coerce')
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['country'] = df['country'].str.strip().str.title()
    
    return df


@st.cache_data(ttl=3600)
def load_national_data():
    """Load and preprocess national accounts data (annual)"""
    df = pd.read_csv(DATA_DIR / "all_national.csv")
    
    # Parse dates (format: 2020)
    df['date'] = pd.to_datetime(df['date_YY'], format='%Y', errors='coerce')
    df['year'] = df['date'].dt.year
    df['country'] = df['country'].str.strip().str.title()
    
    return df


@st.cache_data(ttl=3600)
def load_billing_data():
    """Load and preprocess customer billing data (monthly, by customer)"""
    # Load with low_memory=False to handle mixed types in large file
    df = pd.read_csv(DATA_DIR / "billing.csv", low_memory=False)
    
    # Parse dates - handle multiple formats (Uganda uses DD-MM-YYYY, others use YYYY-MM-DD)
    # Store original date strings before parsing
    original_dates = df['date'].copy()
    
    # First try the standard format
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
    
    # For rows that failed to parse (Uganda data), try the alternative format
    failed_mask = df['date'].isna()
    if failed_mask.any():
        df.loc[failed_mask, 'date'] = pd.to_datetime(
            original_dates[failed_mask], 
            format='%d-%m-%Y', 
            errors='coerce'
        )
    
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['country'] = df['country'].str.strip().str.title()
    
    # Ensure numeric columns are properly typed
    df['billed'] = pd.to_numeric(df['billed'], errors='coerce')
    df['paid'] = pd.to_numeric(df['paid'], errors='coerce')
    df['consumption_m3'] = pd.to_numeric(df['consumption_m3'], errors='coerce')
    
    # Add calculated fields for convenience (with zero-division protection)
    df['payment_ratio'] = np.where(df['billed'] != 0, df['paid'] / df['billed'], 0)
    df['unpaid_amount'] = df['billed'] - df['paid']
    
    return df


def load_all_data():
    """Load all datasets at once (8 datasets including billing.csv)"""
    return {
        'production': load_production_data(),
        'w_service': load_w_service_data(),
        's_service': load_s_service_data(),
        'w_access': load_w_access_data(),
        's_access': load_s_access_data(),
        'finance': load_finance_data(),
        'national': load_national_data(),
        'billing': load_billing_data()
    }


def apply_filters(data, countries=None, zones=None, date_range=None):
    """
    Apply country, zone, and date filters across all domain datasets.

    Args:
        data (dict): Dictionary of dataframes keyed by domain name.
        countries (list[str] | None): Countries to include.
        zones (list[str] | None): Zones to include (for zone-based datasets).
        date_range (tuple | list | None): (start_date, end_date) bounds.

    Returns:
        dict: Filtered dataframes keyed by domain name.
        
    Note:
        Production data uses 'source' field, not 'zone', so zone filters are not applied to it.
        Only country and date filters are applied to production data.
    """
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

        # Apply zone filter (but NOT to production data which uses 'source' instead)
        # Production data should only be filtered by country and date
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


def filter_by_country(df, countries):
    """Filter dataframe by selected countries"""
    if not countries:
        return df
    return df[df['country'].isin(countries)]


def filter_by_date_range(df, start_date, end_date):
    """Filter dataframe by date range"""
    if 'date' not in df.columns:
        return df
    return df[(df['date'] >= pd.to_datetime(start_date)) & 
              (df['date'] <= pd.to_datetime(end_date))]


def get_latest_update_date():
    """Get the latest data update date from production data"""
    df = load_production_data()
    return df['date'].max().strftime('%B %d, %Y')


def get_available_countries():
    """Get list of available countries in the dataset"""
    df = load_production_data()
    return sorted(df['country'].unique().tolist())


def get_available_years():
    """Get list of available years in the dataset"""
    df = load_production_data()
    return sorted(df['year'].unique().tolist())

