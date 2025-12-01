# Dashboard Calculations and Data Sources Guide

## Table of Contents
1. [Overview Dashboard](#overview-dashboard)
2. [Production Domain](#production-domain)
3. [Service Domain](#service-domain)
4. [Access Domain](#access-domain)
5. [Finance Domain](#finance-domain)
6. [Data Sources](#data-sources)

---

## Overview Dashboard

**File:** `page_modules/overview.py`  
**Calculations File:** `utils/kpi_calculator.py` (function: `calculate_summary_kpis`)

### KPI Cards

#### 1. Total Households
- **Data Source:** `w_service.csv`
- **Column:** `households`
- **Calculation Location:** `utils/kpi_calculator.py` line 270-276
- **Formula:** 
  ```python
  total_households = w_service_latest_date['households'].sum()
  ```
- **Aggregation:** Sum of all households across latest date per zone

#### 2. Water Service Coverage
- **Data Source:** `w_access.csv` (latest year)
- **Columns:** `safely_managed`, `basic`, `popn_total`
- **Calculation Location:** `utils/kpi_calculator.py` line 278-285
- **Formula:**
  ```python
  coverage = ((safely_managed + basic) / popn_total) × 100
  ```
- **Benchmark:** 100% (universal coverage target)
- **Aggregation:** Sum of safely_managed + basic divided by total population

#### 3. Access Rate Growth (Year-over-Year)
- **Data Source:** `w_access.csv` (multi-year)
- **Columns:** `year`, `safely_managed`, `basic`, `popn_total`
- **Calculation Location:** `utils/kpi_calculator.py` line 163-200 (helper function)
- **Formula:**
  ```python
  # Calculate Access Coverage Ratio (ACR) per year
  ACR_year = (safely_managed + basic) / popn_total
  
  # Year-over-year growth
  growth = ((ACR_current - ACR_previous) / ACR_previous) × 100
  ```
- **Benchmark:** >0% (positive growth)

#### 4. Revenue Collection Efficiency
- **Data Source:** `all_fin_service.csv`
- **Columns:** `sewer_revenue` (collected), `sewer_billed`
- **Calculation Location:** `utils/kpi_calculator.py` line 37-45 (core function), line 295-302 (summary)
- **Formula:**
  ```python
  collection_efficiency = (total_revenue / total_billed) × 100
  ```
- **Benchmark:** ≥95%

#### 5. Cost Recovery Ratio (OCCR)
- **Data Source:** `all_fin_service.csv`
- **Columns:** `sewer_revenue`, `opex`
- **Calculation Location:** `utils/kpi_calculator.py` line 12-20 (core function), line 304-311 (summary)
- **Formula:**
  ```python
  cost_recovery_ratio = (total_revenue / total_opex) × 100
  ```
- **Benchmark:** ≥100% (revenues should cover operating costs)

#### 6. Operational Profit/Loss
- **Data Source:** `all_fin_service.csv`
- **Columns:** `sewer_revenue`, `opex`
- **Calculation Location:** `utils/kpi_calculator.py` line 313-321
- **Formula:**
  ```python
  operational_profit_loss = total_revenue - total_opex
  ```
- **Benchmark:** >0 (positive profit)

#### 7. Non-Revenue Water (NRW)
- **Data Sources:** 
  - `production.csv` (column: `production_m3`)
  - `w_service.csv` (column: `metered`)
- **Calculation Location:** `utils/kpi_calculator.py` line 23-34 (core function), line 323-331 (summary)
- **Formula:**
  ```python
  NRW = ((production_m3 - billed_volume) / production_m3) × 100
  # Note: Capped at 0% minimum (cannot be negative)
  ```
- **Benchmark:** ≤25%
- **Inverse Metric:** Lower is better

#### 8. Service Continuity
- **Data Source:** `production.csv`
- **Column:** `service_hours`
- **Calculation Location:** `utils/kpi_calculator.py` line 333-340
- **Formula:**
  ```python
  service_continuity = production['service_hours'].mean()
  ```
- **Benchmark:** 24 hours/day (continuous service)
- **Unit:** hrs/day

#### 9. Reported Complaints (Total)
- **Data Source:** `all_fin_service.csv`
- **Column:** `total_complaints`
- **Calculation Location:** `utils/kpi_calculator.py` line 203-228 (helper function), line 342-349
- **Formula:**
  ```python
  total_complaints = finance['total_complaints'].sum()
  ```
- **Benchmark:** None (reporting metric)

#### 10. Average Complaint Resolution Time
- **Data Source:** `all_national.csv`
- **Column:** `complaint_resolution`
- **Calculation Location:** `utils/kpi_calculator.py` line 220-226, line 351-357
- **Formula:**
  ```python
  avg_resolution_time = national['complaint_resolution'].mean()
  ```
- **Benchmark:** ≤5 days
- **Inverse Metric:** Lower is better

### AI-Generated Insights
- **Location:** `page_modules/overview.py` line 323-346
- **Function:** `get_ai_insights()` line 187-201
- **Data Used:** All 10 KPIs + country-level breakdown
- **Processing:** Uses Google Gemini API to generate descriptive and diagnostic insights based on current KPI values

---

## Production Domain

**File:** `page_modules/production.py`

### Key Metrics (Line 38-107)

#### 1. Total Production
- **Data Source:** `production.csv`
- **Column:** `production_m3`
- **Calculation Location:** Line 40-41
- **Formula:**
  ```python
  total_production_m3 = production_df['production_m3'].sum()
  total_production_million = total_production_m3 / 1_000_000
  ```
- **Unit:** Million m³

#### 2. Average Service Hours
- **Data Source:** `production.csv`
- **Column:** `service_hours`
- **Calculation Location:** Line 42
- **Formula:**
  ```python
  avg_service_hours = production_df['service_hours'].mean()
  ```
- **Benchmark:** 20 hrs/day (line 63)
- **Unit:** hrs/day

#### 3. Capacity Utilisation
- **Data Source:** `production.csv`
- **Column:** `production_m3` (aggregated by date)
- **Calculation Location:** Line 43-44
- **Formula:**
  ```python
  daily_totals = production_df.groupby('date')['production_m3'].sum()
  capacity_utilization = (daily_totals.mean() / daily_totals.max()) × 100
  ```
- **Unit:** %
- **Logic:** Average daily production as % of peak day

#### 4. Unit Production Cost
- **Data Sources:**
  - `all_fin_service.csv` (column: `opex`)
  - `production.csv` (column: `production_m3`)
- **Calculation Location:** Line 45-46
- **Formula:**
  ```python
  unit_cost = total_opex / total_production_m3
  ```
- **Unit:** LCU/m³ (Local Currency Units per cubic meter)

#### 5. Water Sources
- **Data Source:** `production.csv`
- **Column:** `source`
- **Calculation Location:** Line 47
- **Formula:**
  ```python
  unique_sources = production_df['source'].nunique()
  ```

#### 6. Daily Average Production
- **Data Source:** `production.csv`
- **Column:** `production_m3`
- **Calculation Location:** Line 48
- **Formula:**
  ```python
  daily_avg = daily_totals.mean()
  ```
- **Unit:** m³

#### 7. Non-Revenue Water
- **Data Sources:**
  - `production.csv` (column: `production_m3`)
  - `w_service.csv` (column: `metered`)
- **Calculation Location:** Line 49-50
- **Formula:**
  ```python
  nrw_pct = calculate_nrw(total_production_m3, metered_total)
  # Using core function from utils/kpi_calculator.py line 23-34
  ```

### Charts

#### Daily Production Trend (Line 113-133)
- **Data Source:** `production.csv`
- **Aggregation:** Daily sum of `production_m3`
- **Chart Type:** Line chart (Plotly)
- **X-axis:** `date`
- **Y-axis:** `production_m3`

#### Monthly Production by Country (Line 136-153)
- **Data Source:** `production.csv`
- **Aggregation:** Monthly sum by country
- **Chart Type:** Multi-line chart (Plotly)
- **Calculation:**
  ```python
  production_df['month_year'] = production_df['date'].dt.to_period('M').astype(str)
  monthly_by_country = production_df.groupby(['month_year', 'country']).agg({
      'production_m3': 'sum'
  })
  ```

#### Water Balance (Waterfall) (Line 155-174)
- **Data Sources:**
  - `production.csv` (total production)
  - `w_service.csv` (metered consumption)
- **Calculation:**
  ```python
  total_production = production_df['production_m3'].sum()
  metered_total = w_service_df['metered'].sum()
  nrw_volume = max(total_production - metered_total, 0)
  
  # Waterfall categories:
  # 1. Total Production (positive)
  # 2. Metered Consumption (negative)
  # 3. Non-Revenue Water (negative)
  ```

#### Service Hours by Country (Line 185-206)
- **Data Source:** `production.csv`
- **Column:** `service_hours`
- **Chart Type:** Horizontal bar chart
- **Aggregation:** Mean service hours per country
- **Reference Line:** 20 hrs/day benchmark

#### Service Hours Distribution (Line 209-226)
- **Data Source:** `production.csv`
- **Column:** `service_hours`
- **Chart Type:** Histogram
- **Bins:** 30

#### Top Water Sources (Line 242-256)
- **Data Source:** `production.csv`
- **Aggregation:** Sum of `production_m3` by `source`
- **Filter:** Top 10 sources
- **Chart Type:** Horizontal bar chart

#### Production by Source & Country (Sunburst) (Line 281-301)
- **Data Source:** `production.csv`
- **Aggregation:** Sum by country and source (top 5 per country)
- **Chart Type:** Sunburst chart
- **Hierarchy:** Country → Source → Production volume

#### Seasonal Production Pattern (Line 372-406)
- **Data Source:** `production.csv`
- **Calculation:**
  ```python
  production_df['month'] = production_df['date'].dt.month
  monthly_pattern = production_df.groupby('month').agg({
      'production_m3': 'mean'
  })
  ```
- **Chart Type:** Line chart with markers
- **Insights:** Identifies peak and low production months

---

## Service Domain

**File:** `page_modules/service.py`

### Key Metrics (Line 48-108)

#### 1. Water Quality (Chlorine)
- **Data Source:** `w_service.csv`
- **Columns:** `test_passed_chlorine`, `tests_conducted_chlorine`
- **Calculation Location:** Line 55-57
- **Formula:**
  ```python
  quality_rate = (tests_passed / tests_conducted) × 100
  # Uses: calculate_water_quality_compliance() from utils/kpi_calculator.py line 82-89
  ```
- **Benchmark:** ≥95%

#### 2. Water Quality (E.coli)
- **Data Source:** `w_service.csv`
- **Columns:** `tests_passed_ecoli`, `test_conducted_ecoli`
- **Calculation Location:** Line 70-72
- **Formula:**
  ```python
  ecoli_rate = (tests_passed / tests_conducted) × 100
  ```
- **Benchmark:** ≥95%

#### 3. Metering Ratio
- **Data Source:** `w_service.csv`
- **Columns:** `metered`, `total_consumption`
- **Calculation Location:** Line 85-87, using `utils/kpi_calculator.py` line 70-78
- **Formula:**
  ```python
  metering_rate = (metered / total_consumption) × 100
  ```
- **Benchmark:** ≥95%

#### 4. Complaint Resolution
- **Data Source:** `all_fin_service.csv`
- **Columns:** `resolved`, `complaints`
- **Calculation Location:** Line 100-102, using `utils/kpi_calculator.py` line 104-112
- **Formula:**
  ```python
  resolution_rate = (resolved / complaints) × 100
  ```
- **Target:** ≥90%

### Charts

#### Water Quality Compliance Trend (Line 116-128)
- **Data Source:** `w_service.csv`
- **Aggregation:** Daily/monthly by country
- **Columns:** Test passed and conducted for both chlorine and E.coli
- **Calculation:**
  ```python
  quality_trend['chlorine_rate'] = (test_passed / tests_conducted) × 100
  quality_trend['ecoli_rate'] = (tests_passed / tests_conducted) × 100
  ```

#### Compliance by Country (Line 130-146)
- **Data Source:** `w_service.csv`
- **Aggregation:** Sum by country
- **Two separate aggregations:**
  - Chlorine compliance by country
  - E.coli compliance by country

---

## Access Domain

**File:** `page_modules/access.py`

### Key Metrics (Line 36-80)

#### 1. Water - Safely Managed
- **Data Source:** `w_access.csv` (latest year)
- **Columns:** `safely_managed`, `popn_total`
- **Calculation Location:** Line 41-43
- **Formula:**
  ```python
  coverage_sm = (safely_managed / popn_total) × 100
  ```

#### 2. Water - Basic
- **Data Source:** `w_access.csv` (latest year)
- **Columns:** `basic`, `popn_total`
- **Calculation Location:** Line 52-54
- **Formula:**
  ```python
  coverage_basic = (basic / popn_total) × 100
  ```

#### 3. Sanitation - Safely Managed
- **Data Source:** `s_access.csv` (latest year)
- **Columns:** `safely_managed`, `popn_total`
- **Calculation Location:** Line 62-64
- **Formula:**
  ```python
  coverage_sm_s = (safely_managed / popn_total) × 100
  ```

#### 4. Sanitation - Basic
- **Data Source:** `s_access.csv` (latest year)
- **Columns:** `basic`, `popn_total`
- **Calculation Location:** Line 73-75
- **Formula:**
  ```python
  coverage_basic_s = (basic / popn_total) × 100
  ```

### Charts

#### JMP Service Ladder - Water (Line 85-125)
- **Data Source:** `w_access.csv` (latest year)
- **Columns:** `safely_managed`, `basic`, `limited`, `unimproved`, `surface_water`, `popn_total`
- **Aggregation:** Sum by country
- **Calculation:**
  ```python
  for each category:
      category_pct = (category_value / popn_total) × 100
  ```
- **Chart Type:** Stacked bar chart (100% scale)
- **Categories (bottom to top):**
  1. Safely Managed (green)
  2. Basic (blue/acceptable)
  3. Limited (yellow)
  4. Unimproved (red/poor)
  5. Surface Water (dark gray)

#### Water Coverage Trend (Line 128-135)
- **Data Source:** `w_access.csv` (multi-year)
- **Calculation:**
  ```python
  water_trend = w_access.groupby(['year', 'country']).agg({
      'safely_managed': 'sum',
      'basic': 'sum',
      'popn_total': 'sum'
  })
  coverage = ((safely_managed + basic) / popn_total) × 100
  ```
- **Chart Type:** Multi-line chart by country
- **Target Line:** 100% (universal coverage)

---

## Finance Domain

**File:** `page_modules/finance.py`

### Key Metrics (Line 42-124)

#### 1. Total Billed
- **Data Source:** `all_fin_service.csv`
- **Column:** `sewer_billed`
- **Calculation Location:** Line 45
- **Formula:**
  ```python
  total_billed = finance_df['sewer_billed'].sum()
  ```
- **Unit:** Local Currency (LCU)

#### 2. Revenue Collected
- **Data Source:** `all_fin_service.csv`
- **Column:** `sewer_revenue`
- **Calculation Location:** Line 46
- **Formula:**
  ```python
  total_revenue = finance_df['sewer_revenue'].sum()
  ```
- **Unit:** Local Currency (LCU)

#### 3. Collection Efficiency
- **Data Source:** `all_fin_service.csv`
- **Columns:** `sewer_revenue`, `sewer_billed`
- **Calculation Location:** Line 70, using `utils/kpi_calculator.py` line 37-45
- **Formula:**
  ```python
  collection_efficiency = (total_revenue / total_billed) × 100
  ```
- **Benchmark:** ≥95%

#### 4. OCCR (Operating Cost Coverage Ratio)
- **Data Source:** `all_fin_service.csv`
- **Columns:** `sewer_revenue`, `opex`
- **Calculation Location:** Line 81, using `utils/kpi_calculator.py` line 12-20
- **Formula:**
  ```python
  occr = (total_revenue / total_opex) × 100
  ```
- **Benchmark:** ≥110% (for sustainability with capital investment)

#### 5. Operating Expenses
- **Data Source:** `all_fin_service.csv`
- **Column:** `opex`
- **Calculation Location:** Line 47
- **Formula:**
  ```python
  total_opex = finance_df['opex'].sum()
  ```

#### 6. Operating Surplus/Deficit
- **Data Source:** `all_fin_service.csv`
- **Columns:** `sewer_revenue`, `opex`
- **Calculation Location:** Line 102
- **Formula:**
  ```python
  surplus_deficit = total_revenue - total_opex
  ```
- **Target:** Positive value (surplus)

#### 7. Uncollected Revenue
- **Data Source:** `all_fin_service.csv`
- **Columns:** `sewer_billed`, `sewer_revenue`
- **Calculation Location:** Line 48
- **Formula:**
  ```python
  uncollected = total_billed - total_revenue
  ```

#### 8. Total Staff
- **Data Source:** `all_fin_service.csv`
- **Columns:** `san_staff`, `w_staff`
- **Calculation Location:** Line 119
- **Formula:**
  ```python
  total_staff = san_staff.sum() + w_staff.sum()
  ```

### Charts

#### OCCR Performance Dashboard (Line 129-133)
- **Data Source:** `all_fin_service.csv`
- **Function:** `create_cost_recovery_dashboard()` from `utils/visualizations.py`
- **Components:** 2x2 subplot with:
  1. OCCR by country (bar chart)
  2. OCCR trend over time (line chart)
  3. Revenue vs OPEX comparison
  4. Distribution/status indicators

#### Financial Waterfall by Country (Line 136-149)
- **Data Source:** `all_fin_service.csv`
- **Calculation per country:**
  ```python
  1. Starting: Total Billed
  2. Subtract: Uncollected Revenue
  3. Result: Revenue Collected
  4. Subtract: OPEX
  5. Result: Surplus/Deficit
  ```
- **Chart Type:** Waterfall chart (2x2 subplots for 4 countries)

---

## Data Sources

### CSV Files (Located in `/Data/` directory)

#### 1. production.csv
- **Frequency:** Daily
- **Granularity:** By water source
- **Key Columns:**
  - `date_YYMMDD` → parsed to `date`
  - `country`
  - `source` (water extraction point)
  - `production_m3` (daily production volume)
  - `service_hours` (hours of service per day)
- **Data Loader:** `utils/data_loader.py` line 17-27
- **Used In:** Production domain, Overview (NRW), Finance (unit cost)

#### 2. w_service.csv
- **Frequency:** Monthly
- **Granularity:** By zone
- **Key Columns:**
  - `date_MMYY` → parsed to `date`
  - `country`
  - `zone`
  - `households` (total connections)
  - `metered` (metered consumption m³)
  - `total_consumption` (total consumption m³)
  - `test_passed_chlorine`, `tests_conducted_chlorine`
  - `tests_passed_ecoli`, `test_conducted_ecoli`
- **Data Loader:** `utils/data_loader.py` line 30-41
- **Used In:** Service domain, Overview (households, NRW, metering)

#### 3. s_service.csv
- **Frequency:** Monthly
- **Granularity:** By zone
- **Key Columns:**
  - `date_MMYY` → parsed to `date`
  - `country`
  - `zone`
  - Sanitation-specific service metrics
- **Data Loader:** `utils/data_loader.py` line 44-55
- **Used In:** Service domain (sanitation metrics)

#### 4. w_access.csv
- **Frequency:** Annual
- **Granularity:** By zone
- **Key Columns:**
  - `date_YY` → parsed to `date`
  - `country`
  - `zone`
  - `popn_total` (total population)
  - `safely_managed` (population with safely managed water)
  - `basic` (population with basic water)
  - `limited`, `unimproved`, `surface_water` (JMP ladder)
- **Data Loader:** `utils/data_loader.py` line 58-68
- **Used In:** Access domain, Overview (coverage, growth)

#### 5. s_access.csv
- **Frequency:** Annual
- **Granularity:** By zone
- **Key Columns:**
  - `date_YY` → parsed to `date`
  - `country`
  - `zone`
  - `popn_total`
  - `safely_managed` (sanitation)
  - `basic` (sanitation)
  - JMP sanitation ladder categories
- **Data Loader:** `utils/data_loader.py` line 71-81
- **Used In:** Access domain, Overview (sanitation coverage)

#### 6. all_fin_service.csv
- **Frequency:** Monthly
- **Granularity:** By city/utility
- **Key Columns:**
  - `date_MMYY` → parsed to `date`
  - `country`
  - `sewer_billed` (total billed amount)
  - `sewer_revenue` (total collected amount)
  - `opex` (operating expenditure)
  - `san_staff`, `w_staff` (staff numbers)
  - `complaints`, `resolved` (complaint data)
  - `total_complaints` (total reported)
- **Data Loader:** `utils/data_loader.py` line 84-95
- **Used In:** Finance domain, Overview (collection efficiency, cost recovery)

#### 7. all_national.csv
- **Frequency:** Annual
- **Granularity:** National/utility level
- **Key Columns:**
  - `date_YY` → parsed to `date`
  - `country`
  - `staff_cost` (total personnel costs)
  - `complaint_resolution` (average resolution time in days)
- **Data Loader:** `utils/data_loader.py` line 98-108
- **Used In:** Overview (resolution time), Finance (personnel cost ratio)

#### 8. billing.csv
- **Frequency:** Monthly
- **Granularity:** By customer
- **Key Columns:**
  - `date` (handles multiple formats: YYYY-MM-DD and DD-MM-YYYY)
  - `country`
  - `zone`
  - `customer_id`
  - `billed` (amount billed)
  - `paid` (amount paid)
  - `consumption_m3` (customer consumption)
- **Data Loader:** `utils/data_loader.py` line 112-146
- **Calculated Fields:**
  - `payment_ratio = paid / billed`
  - `unpaid_amount = billed - paid`
- **Used In:** Advanced finance analytics (customer segmentation, payment risk)

---

## Key Calculation Functions

### Location: `utils/kpi_calculator.py`

#### Core Calculation Functions (Used across domains):

1. **calculate_cost_recovery_ratio()** (line 12-20)
   - Formula: `(revenue / opex) × 100`

2. **calculate_nrw()** (line 23-34)
   - Formula: `((production - billed_volume) / production) × 100`
   - Capped at 0% minimum

3. **calculate_collection_efficiency()** (line 37-45)
   - Formula: `(total_collection / total_billing) × 100`

4. **calculate_water_coverage()** (line 48-56)
   - Formula: `((safely_managed + basic) / popn_total) × 100`

5. **calculate_sanitation_coverage()** (line 59-67)
   - Formula: `((safely_managed + basic) / popn_total) × 100`

6. **calculate_metering_ratio()** (line 70-78)
   - Formula: `(metered / total_consumption) × 100`

7. **calculate_water_quality_compliance()** (line 82-89)
   - Formula: `(tests_passed / tests_conducted) × 100`

8. **calculate_staff_productivity()** (line 92-100)
   - Formula: `(staff / connections) × 1000`
   - Returns: Staff per 1000 connections

9. **calculate_complaint_resolution_rate()** (line 104-112)
   - Formula: `(resolved / complaints) × 100`

10. **calculate_ww_treatment_rate()** (line 115-121)
    - Formula: `(ww_treated / ww_collected) × 100`

#### Advanced Helper Functions:

11. **calculate_access_rate_growth_yoy()** (line 163-200)
    - Calculates year-over-year access coverage growth
    - Groups by year, calculates ACR, then growth rate

12. **calculate_complaints_kpis()** (line 203-228)
    - Returns: (total_complaints, avg_resolution_time)

13. **calculate_summary_kpis()** (line 235-411)
    - Main function for Overview dashboard
    - Calculates all 10 KPIs plus additional metrics
    - Returns: Dictionary with values, benchmarks, units

14. **calculate_country_kpis()** (line 418-546)
    - Country-specific KPI calculation
    - Filters all data by country before calculation

#### Customer-Level Finance Functions (line 575-728):

15. **calculate_revenue_collection_efficiency_customer_level()** (line 577-607)
    - Uses `billing.csv` for granular RCE calculation

16. **identify_payment_risk_customers()** (line 610-643)
    - Segments customers: High Risk, Medium Risk, Low Risk
    - Based on payment ratio thresholds

17. **calculate_commercial_nrw()** (line 646-680)
    - Revenue losses due to non-payment

18. **calculate_physical_nrw()** (line 683-703)
    - Water lost through leaks, theft, meter errors

19. **get_payment_by_zone()** (line 706-728)
    - Geographic payment analysis

---

## Data Flow Summary

### From Raw CSV to Dashboard Visualization:

```
1. CSV File (Data/)
   ↓
2. Data Loader (utils/data_loader.py)
   - Parse dates
   - Standardize country names
   - Type conversions
   ↓
3. Session State Cache (app.py)
   - load_data_cached() - line 94-101
   - Stored in st.session_state.data
   ↓
4. Filter Application (utils/data_loader.py - apply_filters)
   - Country filter
   - Zone filter (where applicable)
   - Date range filter
   ↓
5. KPI Calculation (utils/kpi_calculator.py)
   - Aggregate data
   - Apply formulas
   - Compare to benchmarks
   ↓
6. Page Rendering (page_modules/)
   - overview.py
   - production.py
   - service.py
   - access.py
   - finance.py
   ↓
7. Visualization (Plotly charts)
   - Charts created using utils/visualizations.py helper functions
   - Displayed with st.plotly_chart()
```

---

## Benchmark Sources & Standards

All benchmarks are based on international water sector best practices:

- **NRW ≤25%**: World Bank / IWA standard for efficient water systems
- **Collection Efficiency ≥95%**: Industry best practice
- **Cost Recovery ≥100%**: Financial sustainability requirement
- **Service Hours = 24**: Continuous water supply (24/7)
- **Water Quality ≥95%**: WHO guidelines compliance
- **Complaint Resolution ≤5 days**: Customer service standard
- **Staff Productivity ≤7/1000**: IWA efficiency benchmark
- **Universal Coverage = 100%**: SDG 6 target

---

## Notes

1. **Caching:** All data loading functions use `@st.cache_data(ttl=3600)` decorator for 1-hour cache
2. **Multi-Country Support:** Financial metrics display currency warnings when multiple countries selected
3. **Date Parsing:** Handles multiple date formats across different CSV files
4. **Zero-Division Protection:** All percentage calculations include checks for zero denominators
5. **Latest Data Selection:** Access and coverage metrics use latest available year
6. **Inverse Metrics:** NRW and complaint resolution time use inverse coloring (lower is better)

---

**Last Updated:** December 2024  
**Dashboard Version:** See `utils/theme.py` for version number
