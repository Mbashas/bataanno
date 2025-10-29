# 💧 African Water & Sanitation Regulatory Dashboard

An interactive multi-country dashboard designed for water sector regulators, policymakers, and government officials to monitor compliance, track performance trends, and identify service delivery gaps across 4 African countries (Cameroon, Lesotho, Malawi, Uganda) from 2020-2024.

**Track progress toward SDG 6 targets** • **Benchmark performance** • **Identify intervention priorities**

## 👥 Target Users

### Water Sector Regulators
- Monitor utility compliance with standards
- Track performance trends across jurisdictions
- Identify utilities requiring intervention
- Benchmark against national and international targets

### County & Regional Governments
- Assess service delivery gaps by region
- Compare performance across different areas
- Inform budget allocation decisions
- Support policy reforms with data-driven insights

### Policymakers & Development Partners
- Track progress toward SDG 6 (Clean Water & Sanitation)
- Identify investment priorities
- Monitor sector-wide trends
- Evaluate policy impact

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

### Landing Page (Regulatory Overview)

The landing page answers three critical questions for decision-makers:

#### 1. **WHERE ARE WE?** — Current State
- 6 high-level KPI cards with sector-wide performance
- Population served, NRW, water coverage, quality compliance
- Color-coded performance indicators (🟢 🟡 🔴)
- Real-time benchmarking against WHO and SDG targets

#### 2. **WHAT NEEDS ATTENTION?** — Actionable Insights
- Critical gaps alert system
- High NRW zones requiring leak detection programs
- Low coverage areas needing infrastructure investment
- Water quality concerns requiring treatment improvements
- Specific, prioritized intervention recommendations

#### 3. **HOW ARE WE DOING?** — Progress & Trends
- Interactive country comparison visualizations
- Performance across Service, Production, Access, and Finance domains
- Year-over-year trend analysis with benchmark lines
- Geographic performance overview with color-coded indicators

**Interactive Filters:**
- Multi-select country filter
- Time period slider (2020-2024)
- Dynamic metric selector (NRW, coverage, quality, etc.)

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

#### Service Domain
- Complaint resolution efficiency & response time
- Customer service quality metrics
- Service continuity and reliability

#### Production Domain
- Water supply vs. consumption patterns
- Non-revenue water (NRW) percentage
- Production efficiency and capacity utilization

#### Access Domain
- Water coverage (metered connections %)
- Sanitation coverage (sewer connections)
- Public toilet access ratios vs. WHO guidelines
- Population served estimates

#### Finance Domain (Proxies)
- NRW as financial loss indicator
- Service efficiency metrics
- Operational productivity measures

#### Quality & Compliance
- E. Coli test pass rates (WHO target: >95%)
- Chlorine test execution & pass rates
- Wastewater treatment coverage
- Regulatory compliance tracking

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

## 📏 Performance Benchmarks

The dashboard uses the following internationally recognized benchmarks:

| Metric | Benchmark | Source | Performance Coding |
|--------|-----------|--------|-------------------|
| **E. Coli Pass Rate** | ≥ 95% | WHO | 🟢 ≥95% • 🟡 80-95% • 🔴 <80% |
| **Non-Revenue Water (NRW)** | ≤ 25% | IWA Best Practice | 🟢 ≤25% • 🟡 25-35% • 🔴 >35% |
| **Water Coverage** | ≥ 80% | SDG 6 Target | 🟢 ≥80% • 🟡 60-80% • 🔴 <60% |
| **Chlorine Testing Execution** | ≥ 90% | National Standards | 🟢 ≥90% • 🟡 70-90% • 🔴 <70% |
| **Wastewater Treatment** | ≥ 80% | SDG 6.3 | 🟢 ≥80% • 🟡 60-80% • 🔴 <60% |

## 🔗 Related Documentation

- **DASHBOARD_FEATURES.md** - Detailed technical documentation of landing page features
- **service_data.ipynb** - Original data analysis notebook

## 📝 License

This project is open source and available for use by water sector stakeholders, researchers, and development organizations.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests to improve the dashboard.

## 📧 Contact

For questions about the data, methodology, or dashboard features, please open an issue on the repository.
