# 🌊 Multi-Country Water Services Performance Dashboard

A comprehensive Streamlit dashboard for analyzing water and sanitation service performance across **Uganda**, **Cameroon**, **Lesotho**, and **Malawi**. Built to empower utility managers with data-driven insights for operational efficiency, financial sustainability, service quality, and equitable access.

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Dashboard Structure](#dashboard-structure)
- [Data Requirements](#data-requirements)
- [Key Performance Indicators](#key-performance-indicators)
- [Technical Architecture](#technical-architecture)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### Four Analytical Domains

1. **🏭 Production Domain**
   - Daily production volume tracking
   - Service hours analysis by source
   - Production capacity utilization
   - Seasonal pattern identification

2. **🚰 Service Domain**
   - Water quality compliance (Chlorine & E.coli)
   - Metering ratio analysis
   - Complaint resolution tracking
   - Wastewater treatment performance

3. **🌍 Access Domain**
   - JMP Service Ladder visualization
   - Urban vs rural coverage gaps
   - Zone-level access analysis
   - Equity and underserved population identification

4. **💰 Finance Domain**
   - Operating Cost Coverage Ratio (OCCR)
   - Revenue collection efficiency
   - Financial waterfall analysis
   - Cost structure and staffing metrics

### Four Types of Insights

- **Descriptive**: What happened? (Current state KPIs)
- **Diagnostic**: Why did it happen? (Root cause analysis)
- **Predictive**: What will happen? (Trend projections)
- **Prescriptive**: What should be done? (Actionable recommendations)

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd DASHADI
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Data Files

Ensure all required CSV files are in the `Data/` directory:

```
Data/
├── production.csv
├── w_service.csv
├── s_service.csv
├── w_access.csv
├── s_access.csv
├── all_fin_service.csv
└── all_national.csv
```

## 🎯 Usage

### Running the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`

### Navigation

1. **Sidebar Navigation**: Use the radio buttons to switch between domains
2. **Filters**: Select countries and date ranges in the sidebar
3. **Interactive Charts**: Hover over visualizations for detailed information
4. **Export Data**: Visit the Reports page to download CSV files

### Quick Start Guide

1. Start at the **Home** page to see overall KPIs
2. Navigate to **Overview Dashboard** for cross-country comparison
3. Dive into specific domains (Production, Service, Access, Finance) for detailed analysis
4. Generate **Reports** with actionable recommendations

## 📊 Dashboard Structure

```
DASHADI/
├── app.py                      # Main application file
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── Data/                       # Data directory (CSV files)
│   ├── production.csv
│   ├── w_service.csv
│   ├── s_service.csv
│   ├── w_access.csv
│   ├── s_access.csv
│   ├── all_fin_service.csv
│   └── all_national.csv
├── utils/                      # Utility modules
│   ├── data_loader.py         # Data loading and caching
│   ├── kpi_calculator.py      # KPI calculation formulas
│   └── visualizations.py      # Reusable chart functions
└── page_modules/               # Page modules
    ├── home.py                # Landing page
    ├── overview.py            # Overview dashboard
    ├── production.py          # Production domain
    ├── service.py             # Service domain
    ├── access.py              # Access domain
    ├── finance.py             # Finance domain
    └── reports.py             # Reports and exports
```

## 📁 Data Requirements

### File Formats

All data files should be in CSV format with the following structures:

#### 1. production.csv (Daily, by source)
- `date_YYMMDD`: Date in YYYY/MM/DD format
- `source`: Water extraction source name
- `production_m3`: Production volume in cubic meters
- `service_hours`: Hours of service per day
- `country`: Country name

#### 2. w_service.csv (Monthly, by zone)
- `country`, `zone`, `date_MMYY` (MMM/YY format)
- `households`, `tests_chlorine`, `tests_ecoli`
- `tests_conducted_chlorine`, `test_conducted_ecoli`
- `test_passed_chlorine`, `tests_passed_ecoli`
- `w_supplied`, `total_consumption`, `metered`
- `ww_capacity`

#### 3. s_service.csv (Monthly, by zone)
- `country`, `zone`, `date_MMYY`
- `households`, `sewer_connections`, `public_toilets`
- `workforce`, `f_workforce`
- `ww_collected`, `ww_treated`, `ww_reused`
- `w_supplied`, `hh_emptied`, `fs_treated`, `fs_reused`

#### 4. w_access.csv (Annual, by zone)
- `country`, `zone`, `date_YY` (YYYY format)
- `safely_managed`, `safely_managed_pct`
- `basic`, `basic_pct`
- `limited`, `limited_pct`
- `unimproved`, `unimproved_pct`
- `surface_water`, `surface_water_pct`
- `popn_total`, `households`, `municipal_coverage`

#### 5. s_access.csv (Annual, by zone)
- `country`, `zone`, `date_YY`
- `safely_managed`, `safely_managed_pct`
- `basic`, `basic_pct`
- `limited`, `limited_pct`
- `unimproved`, `unimproved_pct`
- `open_def`, `open_def_pct`
- `popn_total`, `households`

#### 6. all_fin_service.csv (Monthly, by city)
- `country`, `city`, `date_MMYY`
- `sewer_length`, `complaints`, `resolved`, `blocks`
- `sewer_billed`, `sewer_revenue`, `opex`
- `san_staff`, `w_staff`, `propoor_popn`

#### 7. all_national.csv (Annual, national accounts)
- `country`, `city`, `date_YY`
- `budget_allocated`, `san_allocation`, `wat_allocation`
- `staff_cost`, `water_resources`, `trained_staff`
- `complaint_resolution`, `registered_wtps`, `inspected_wtps`
- `total_service_providers`, `licensed_service_providers`
- `asset_health`, `staff_training_budget`

## 📈 Key Performance Indicators

### Sector Benchmarks

| KPI | Benchmark | Formula |
|-----|-----------|---------|
| Water Coverage | 100% | (Safely Managed + Basic) / Total Population × 100 |
| Sanitation Coverage | 100% | (Safely Managed + Basic) / Total Population × 100 |
| Non-Revenue Water (NRW) | ≤25% | (Production - Billed Volume) / Production × 100 |
| Water Quality Compliance | ≥95% | Tests Passed / Tests Conducted × 100 |
| Service Hours | ≥20 hrs/day | Average hours of supply per day |
| Revenue Collection Efficiency | ≥95% | Revenue Collected / Total Billed × 100 |
| OCCR | ≥110% | Revenue / Operating Expenses × 100 |
| Metering Ratio | ≥95% | Metered Consumption / Total Consumption × 100 |
| Staff Productivity | ≤7 staff/1000 connections | Staff Count / Connections × 1000 |

## 🏗️ Technical Architecture

### Technology Stack

- **Frontend Framework**: Streamlit 1.28+
- **Data Processing**: Pandas 2.0+, NumPy 1.24+
- **Visualization**: Plotly 5.17+
- **Caching**: Streamlit's built-in caching (@st.cache_data)

### Design Principles

1. **KISS Principle**: Simple, intuitive interfaces for non-technical users
2. **Modular Architecture**: Separated concerns (data, calculations, visualizations, pages)
3. **Performance Optimization**: Aggressive caching for sub-3-second load times
4. **Accessibility**: Color-blind friendly palettes, clear labels, tooltips

### Color Palette (Color-Blind Friendly)

- 🟢 Green (#2ecc71): Good performance
- 🟠 Amber (#f39c12): Acceptable performance
- 🔴 Red (#e74c3c): Poor performance / needs attention
- 🔵 Blue (#3498db): Primary color
- 🟣 Purple (#9b59b6): Secondary color

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/YourFeature`)
3. **Commit your changes** (`git commit -m 'Add YourFeature'`)
4. **Push to the branch** (`git push origin feature/YourFeature`)
5. **Open a Pull Request**

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Support

For questions, issues, or feature requests:

- **Email**: dashboard@washservices.org
- **Issues**: Open an issue on GitHub
- **Documentation**: See inline help tooltips in the dashboard

## 🙏 Acknowledgments

- Data sources from national water utilities
- JMP (WHO/UNICEF Joint Monitoring Programme) for access indicators
- Utility managers across Uganda, Cameroon, Lesotho, and Malawi

---

**Built with ❤️ for better water services in Africa**

Last Updated: November 2024 | Version 1.0.0

