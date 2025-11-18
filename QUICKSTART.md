# 🚀 Quick Start Guide

Get your Water Services Dashboard up and running in 5 minutes!

## ⚡ Fast Setup

### 1. Install Dependencies (1 minute)

```bash
# Navigate to the project directory
cd DASHADI

# Install required packages
pip install -r requirements.txt
```

### 2. Verify Data Files (1 minute)

Make sure these files are in your `Data/` folder:

- ✅ `production.csv`
- ✅ `w_service.csv`
- ✅ `s_service.csv`
- ✅ `w_access.csv`
- ✅ `s_access.csv`
- ✅ `all_fin_service.csv`
- ✅ `all_national.csv`

### 3. Launch Dashboard (1 minute)

```bash
streamlit run app.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`

## 🎯 First Time Using the Dashboard?

### Step-by-Step Walkthrough

**1. Start at Home Page (🏠)**
   - See high-level KPIs for all countries
   - Review summary metrics
   - Click on domain cards to navigate

**2. Explore Overview Dashboard (📊)**
   - View KPI scorecard with benchmarks
   - Compare performance across countries
   - Identify top performers and areas needing attention

**3. Dive into Domains**
   - **Production (🏭)**: Check water production and service hours
   - **Service (🚰)**: Monitor water quality and complaints
   - **Access (🌍)**: Analyze coverage gaps and equity
   - **Finance (💰)**: Review OCCR and financial sustainability

**4. Generate Reports (📋)**
   - Get actionable recommendations
   - Export data for further analysis
   - Create custom reports

### 🔧 Using Filters

**Sidebar Filters:**
- **Countries**: Select one or more countries to focus on
- **Date Range**: Choose the time period for analysis

Filters apply to all pages automatically!

## 🆘 Troubleshooting

### Dashboard won't start?

```bash
# Check if Streamlit is installed
streamlit --version

# If not installed
pip install streamlit>=1.28.0
```

### Data not loading?

1. Verify CSV files are in `Data/` directory
2. Check file names match exactly (case-sensitive)
3. Ensure CSV files have correct column headers

### Performance issues?

- **First load is slow**: Data caching happens on first load (normal)
- **Subsequent loads**: Should be fast (<3 seconds)
- **Clear cache**: Refresh the page or restart the app

### Import errors?

```bash
# Ensure you're in the DASHADI directory
pwd  # Should show /path/to/DASHADI

# Check Python path
python -c "import sys; print(sys.path)"
```

## 📚 Common Tasks

### Export Data to Excel

1. Go to **Reports** page
2. Click **Export Data** button
3. Select data type (Performance, Production, Finance)
4. Download CSV file

### Compare Countries

1. Use **Overview Dashboard**
2. View the cross-country comparison table
3. Check the radar chart for multi-dimensional view

### Find Priority Zones

1. Go to **Access Domain**
2. Scroll to "Zone-Level Access Analysis"
3. Review "Zones with Lowest Coverage" chart

### Check Financial Health

1. Go to **Finance Domain**
2. Review OCCR dashboard (target: ≥110%)
3. Check waterfall charts for each country

## 💡 Tips & Tricks

### Keyboard Shortcuts
- `Ctrl/Cmd + R`: Refresh page
- `Ctrl/Cmd + F`: Search within page

### Best Practices
1. **Start Broad**: Begin with Overview, then drill down
2. **Use Filters**: Focus on specific countries/periods
3. **Export Data**: Download raw data for offline analysis
4. **Check Benchmarks**: Green = good, Red = needs attention

### Understanding KPI Colors
- 🟢 **Green**: Meeting or exceeding benchmark
- 🟠 **Amber**: Acceptable but below target
- 🔴 **Red**: Needs immediate attention

## 🎓 Learning Path

**Week 1: Familiarization**
- Explore all pages
- Understand KPI definitions
- Review your country's data

**Week 2: Analysis**
- Compare with sector benchmarks
- Identify 3-5 priority areas
- Review historical trends

**Week 3: Action Planning**
- Generate reports
- Share insights with team
- Develop action plans

**Ongoing: Monitoring**
- Weekly KPI reviews
- Monthly trend analysis
- Quarterly strategic reviews

## 📞 Need Help?

- **Documentation**: See README.md for detailed info
- **Support**: dashboard@washservices.org
- **Tutorials**: In-app tooltips (hover over ℹ️ icons)

## ⚙️ Advanced Configuration

### Custom Port

```bash
streamlit run app.py --server.port 8502
```

### Headless Mode (Server Deployment)

```bash
streamlit run app.py --server.headless true
```

### Enable CORS (API Access)

```bash
streamlit run app.py --server.enableCORS false
```

---

**Happy Analyzing! 🌊💧**

*Making data-driven decisions for better water services*

