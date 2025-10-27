# 💧 Water & Sanitation Service Analytics Dashboard

A Streamlit multipage dashboard showcasing water and sanitation service performance across 4 African countries (Cameroon, Lesotho, Malawi, Uganda) from 2020-2024.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard
```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 📊 Dashboard Structure

### Main Page (Home)
- Multi-country overview and comparison
- Cross-country performance metrics
- E. Coli pass rate trends
- Featured insights summary

### Country Pages (with Advanced Filters)

Each country page includes interactive filters for:
- **Date Range** - Select specific time periods
- **Zones** - Filter by service zones
- **Years** - Multi-select year filtering
- **Custom Views** - Focus areas specific to each country

#### 🇨🇲 Cameroon (Yaounde)
- 4 tabs: Water Quality, Customer Service, Wastewater, Operations
- Wastewater treatment capacity analysis
- Faecal sludge reuse tracking
- Zone-based performance metrics

#### 🇱🇸 Lesotho
- Featured: Water quality testing gaps
- Urban vs Rural comparison
- Historical trends analysis
- Infrastructure & workforce metrics

#### 🇲🇼 Malawi (Lilongwe)
- Featured: Public toilet infrastructure crisis
- People per toilet tracking vs WHO guidelines
- Sanitation coverage analysis
- Zone performance comparison

#### 🇺🇬 Uganda (Kampala)
- Featured: Complaint resolution crisis
- High-density zone challenges
- Multi-zone radar charts
- Resolution efficiency heatmaps
- 4 zones: Rubaga, Central, Nakawa, Kawempe

## 📁 Files Structure

```
/Users/pro/ADI/
├── app.py                          # Main dashboard (home page)
├── service_data.csv                # Data file
├── requirements.txt                # Python dependencies
├── pages/
│   ├── 1_🇨🇲_Cameroon.py           # Cameroon analytics
│   ├── 2_🇱🇸_Lesotho.py            # Lesotho analytics
│   ├── 3_🇲🇼_Malawi.py             # Malawi analytics
│   └── 4_🇺🇬_Uganda.py             # Uganda analytics
├── service_data.ipynb              # Original analysis notebook
└── README.md                       # This file
```

## 📈 Key Features

### Interactive Filters
- Date range selection
- Multi-select zone filtering
- Year filtering
- Custom metric views

### Visualizations
- Time-series trends
- Zone comparisons
- Heatmaps
- Radar charts
- Multi-axis charts
- Stacked area charts

### Key Performance Indicators
- E. Coli pass rates
- Chlorine test execution & pass rates
- Complaint resolution efficiency
- Resolution time tracking
- Wastewater capacity utilization
- Metering coverage
- Non-revenue water (NRW)
- Workforce productivity
- Public toilet access ratios

## 🎯 Featured Insights

1. **Water Quality Testing Gaps** (Lesotho)
   - Execution rates below 90% target
   - Urban vs rural disparities

2. **Complaint Resolution Crisis** (Kampala, Uganda)
   - Resolution time exceeds 22 days
   - Nakawa zone shows highest rates

3. **Wastewater Capacity Underutilization** (Yaounde, Cameroon)
   - Treatment plants below capacity
   - Revenue opportunities through reuse

4. **Public Toilet Infrastructure** (Lilongwe, Malawi)
   - People per toilet exceeds WHO guidelines
   - Critical infrastructure gaps

## 🔧 Requirements

- Python 3.8+
- Streamlit >= 1.28.0
- Pandas >= 2.0.0
- Plotly >= 5.14.0
- NumPy >= 1.24.0

## 💡 Usage Tips

1. **Navigate** using the sidebar to select countries
2. **Filter data** using the sidebar controls on each country page
3. **Hover over charts** for detailed information
4. **Compare zones** using the multi-select filters
5. **Export data** from the detailed data tables at the bottom of each page

## 📊 Data Coverage

- **Countries**: 4 (Cameroon, Lesotho, Malawi, Uganda)
- **Cities**: Yaounde, Maseru, Lilongwe, Kampala
- **Time Period**: 2020-2024
- **Records**: 1,080+ monthly observations
- **Metrics**: 30+ indicators across water quality, customer service, wastewater, and operations
