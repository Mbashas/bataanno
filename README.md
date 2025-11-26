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
   - Customer payment behavior by zone
   - Payment risk dashboard (High/Medium/Low Risk customers)
   - Commercial vs. Physical NRW breakdown

### Enhanced Visual Experience
- **Professional Water-Themed Design**: Gradient backgrounds and modern UI
- **Country Flags & Icons**: Visual identifiers for Uganda (🇺🇬), Cameroon (🇨🇲), Malawi (🇲🇼), Lesotho (🇱🇸)
- **Zone-Level Analysis**: Detailed performance breakdown by geographic zones
- **Interactive Maps**: Choropleth maps for regional performance comparison
- **Responsive Design**: Optimized for utility managers' workflow

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd water_utility_dashboard
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

### Step 4: Set Up Data Files

Ensure all required CSV files are in the `Data/` directory:

```
Data/
├── production.csv          # 7,308 rows - Daily production data
├── w_service.csv           # 1,080 rows - Water service metrics
├── s_service.csv           # 1,080 rows - Sanitation service metrics
├── w_access.csv            # 90 rows - Water access indicators
├── s_access.csv            # 90 rows - Sanitation access indicators
├── finance.csv             # 240 rows - Financial performance
├── national.csv            # 20 rows - National accounts data
└── billing.csv             # 720,119 rows - Customer billing records
```

### Step 5: Add Visual Assets (Optional)

Create the assets directory for enhanced visuals:
```bash
mkdir -p assets/images assets/styles
```
Add water-themed background images and custom CSS for optimal visual experience.

## 🎯 Usage

### Running the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`

### Navigation Structure

1. **Landing Page (app.py)**: Executive overview with KPIs, maps, and country comparison
2. **Country Pages**: Detailed analysis for each country with tabbed interfaces:
   - **Tab 1 - Access**: Service coverage and equity analysis
   - **Tab 2 - Billing/Finance**: Revenue, collections, and financial sustainability
   - **Tab 3 - Production**: Water production and service hours
   - **Tab 4 - Service**: Water quality and operational metrics

### Quick Start Guide

1. **Start at Landing Page**: View overall KPIs and regional performance maps
2. **Explore Country Details**: Click country buttons for zone-level analysis
3. **Use Interactive Filters**: Filter by country, zone, and date ranges
4. **Export Insights**: Generate reports with actionable recommendations

## 📊 Updated Dashboard Structure

```
water_utility_dashboard/
├── app.py                          # Main landing page (Executive Overview)
├── pages/                          # Country-specific detailed analysis
│   ├── 1_🇺🇬_Uganda.py              # Uganda country page
│   ├── 2_🇨🇲_Cameroon.py            # Cameroon country page
│   ├── 3_🇲🇼_Malawi.py              # Malawi country page
│   └── 4_🇱🇸_Lesotho.py             # Lesotho country page
├── utils/                          # Utility modules
│   ├── data_loader.py              # Data loading, caching, and preprocessing
│   └── visualization.py            # Custom visualization functions
├── assets/                         # Visual assets
│   ├── images/
│   │   ├── background.jpg          # Water-themed background
│   │   └── logo.png               # Utility dashboard logo
│   └── styles/
│       └── custom.css             # Enhanced styling and themes
├── Data/                           # All CSV datasets
│   ├── production.csv              # Daily production records
│   ├── w_service.csv               # Water service metrics
│   ├── s_service.csv               # Sanitation service metrics
│   ├── w_access.csv                # Water access data
│   ├── s_access.csv                # Sanitation access data
│   ├── finance.csv                 # Financial performance
│   ├── national.csv                # National accounts
│   └── billing.csv                 # Customer billing data
├── requirements.txt                # Python dependencies
├── config.py                       # Configuration settings
└── README.md                       # This documentation
```

## 📁 Complete Data Requirements

### Dataset Specifications

#### 1. production.csv (7,308 rows)
- `date_YYMMDD`: Date in YYYY/MM/DD format
- `source`: Water extraction source name
- `production_m3`: Production volume in cubic meters
- `service_hours`: Hours of service per day
- `country`, `zone`: Geographic information
- `year`, `month`: Temporal dimensions

#### 2. w_service.csv (1,080 rows)
- `country`, `zone`, `date_MMYY`: Geographic and temporal data
- `customers`, `tests_chlorine`, `tests_ecoli`: Service metrics
- `tests_conducted_chlorine`, `test_conducted_ecoli`: Testing volume
- `test_passed_chlorine`, `tests_passed_ecoli`: Compliance results
- `w_supplied`, `total_consumption`, `metered`: Supply and consumption
- `ww_capacity`, `supply_hours`: Capacity and service levels

#### 3. s_service.csv (1,080 rows)
- `country`, `zone`, `date_MMYY`: Location and time
- `customers`, `sewer_connections`, `public_toilets`: Service infrastructure
- `workforce`, `f_workforce`: Staffing information
- `ww_collected`, `treatment_quality`, `ww_reused`: Sanitation metrics
- `w_supplied`, `hh_emptied`, `fs_treated`, `fs_reused`: Service delivery

#### 4. w_access.csv (90 rows)
- `country`, `zone`, `date_YY`: Geographic and annual data
- `safely_managed`, `access_rate`: JMP service ladder
- `basic`, `basic_pct`, `limited`, `limited_pct`: Service levels
- `unimproved`, `unimproved_pct`, `surface_water`, `surface_water_pct`: Access gaps
- `population`, `households`, `municipal_coverage`: Demographic coverage

#### 5. s_access.csv (90 rows)
- `country`, `zone`, `date_YY`: Location and time
- `safely_managed`, `access_rate`: Sanitation access
- `basic`, `basic_pct`, `limited`, `limited_pct`: Service levels
- `unimproved`, `unimproved_pct`, `open_def`, `open_def_pct`: Access challenges
- `population`, `households`: Demographic data

#### 6. finance.csv (240 rows)
- `country`, `city`, `date_MMYY`: Geographic and temporal
- `sewer_length`, `complaints`, `resolved`, `blocks`: Infrastructure and service
- `sewer_billed`, `collection_rate`, `expenses`: Financial metrics
- `san_staff`, `w_staff`, `propoor_popn`: Staffing and equity

#### 7. national.csv (20 rows)
- `country`, `city`, `date_YY`: National level data
- `budget_allocated`, `san_allocation`, `water_investment`: Budget information
- `staff_cost`, `gdp`, `trained_staff`: Economic and HR metrics
- `complaint_resolution`, `registered_wtps`, `inspected_wtps`: Regulatory data
- `total_service_providers`, `licensed_service_providers`: Sector overview
- `asset_health`, `staff_training_budget`: System capacity

#### 8. billing.csv (720,119 rows)
- `customer_id`: Unique customer identifier
- `date`: Billing date
- `consumption_m3`: Water consumption volume
- `billed`, `paid`: Financial transactions
- `country`, `zone`, `source`: Geographic and system data
- `year`, `month`: Temporal dimensions

## 📈 Key Performance Indicators

### Executive Dashboard KPIs

| Category | KPI | Benchmark | Description |
|----------|-----|-----------|-------------|
| **Coverage** | Water Access Rate | ≥95% | Population with improved water sources |
| | Sanitation Access Rate | ≥95% | Population with improved sanitation |
| | Safely Managed Services | ≥80% | JMP highest service level |
| **Operations** | Water Production | Trend | Total m³ produced |
| | Service Hours | ≥20 hrs/day | Average daily supply |
| | Water Quality Compliance | ≥95% | Chlorine and E.coli tests passed |
| **Financial** | Collection Rate | ≥90% | Revenue collected vs billed |
| | Cost Recovery | ≥100% | Revenue vs operating expenses |
| | Metering Ratio | ≥85% | Consumption that is metered |

### Zone-Level Analysis
- **Zone Performance Ranking**: Top and bottom performing zones
- **Geographic Equity**: Access disparities across zones
- **Service Quality Variation**: Water quality and reliability by zone
- **Financial Performance**: Collection rates and revenue by zone

## 🏗️ Enhanced Technical Architecture

### Technology Stack

- **Frontend Framework**: Streamlit 1.28+
- **Data Processing**: Pandas 2.0+, NumPy 1.24+
- **Visualization**: Plotly 5.17+, Chart.js
- **Caching**: Streamlit's built-in caching (@st.cache_data)
- **Styling**: Custom CSS with water-themed design

### New Features

1. **Zone-Aware Analysis**: All visualizations now support zone-level drilling
2. **Enhanced Maps**: Interactive choropleth maps for regional comparison
3. **Country Flags**: Visual identifiers for better navigation
4. **Professional UI**: Gradient backgrounds, hover effects, modern cards
5. **Responsive Design**: Mobile-friendly interface for field use

### Performance Optimizations

- **Smart Caching**: Data loader with TTL caching for sub-3-second loads
- **Lazy Loading**: Visualizations load on demand
- **Data Validation**: Comprehensive data quality checks
- **Error Handling**: Graceful degradation for missing data

## 🎨 Design System

### Color Palette (Water-Themed)

- **Primary Blue** (#1f77b4): Water, trust, reliability
- **Success Green** (#2ecc71): Good performance, compliance
- **Warning Amber** (#f39c12): Needs attention, medium risk
- **Alert Red** (#e74c3c): Critical issues, poor performance
- **Purple Gradient**: KPI cards and highlights

### Typography

- **Headers**: Bold, gradient text for emphasis
- **Body**: Clean, readable fonts for data presentation
- **Metrics**: Large, clear numbers for quick scanning

## 🤝 Contributing

We welcome contributions from utility professionals and developers:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/zone-analysis`)
3. **Commit your changes** (`git commit -m 'Add enhanced zone visualization'`)
4. **Push to the branch** (`git push origin feature/zone-analysis`)
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 for Python code
- Use type hints for function signatures
- Add docstrings to all functions
- Test with sample data before submitting
- Update documentation for new features

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Support & Feedback

For technical support, data issues, or feature requests:

- **Utility Managers**: Contact your national water authority
- **Technical Issues**: Open an issue on GitHub repository
- **Feature Requests**: Use the GitHub discussions forum
- **Documentation**: In-app tooltips and help sections

## 🙏 Acknowledgments

- National Water Authorities of Uganda, Cameroon, Malawi, and Lesotho
- Utility managers and field staff providing operational data
- JMP (WHO/UNICEF Joint Monitoring Programme) for service ladder frameworks
- African Water Association for sector benchmarks and best practices

---

**💧 Built for Sustainable Water Services in Africa | Version 2.0 🚀**

*Last Updated: December 2024 | Enhanced with Zone-Level Analytics & Professional UI*