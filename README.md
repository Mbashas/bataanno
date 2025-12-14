# Multi-Country Water Services Performance Dashboard

**Comprehensive Water & Sanitation Analytics for Uganda, Cameroon, Lesotho, and Malawi**



A powerful Streamlit dashboard empowering utility managers with data-driven insights for operational efficiency, financial sustainability, service quality, and equitable access.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Default Credentials](#default-credentials)
- [Managing User Passwords](#managing-user-passwords)
- [Data Dictionary](#data-dictionary)
- [Key Performance Indicators](#key-performance-indicators)
- [Project Architecture](#project-architecture)
- [Deployment](#deployment)
- [Security Notes](#security-notes)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This dashboard enables water utility managers to monitor, analyze, and optimize water and sanitation service delivery across four African countries. It provides:

- **Real-time KPI monitoring** with industry benchmarks
- **AI-powered insights** using Google Gemini
- **Multi-currency support** (local currencies + USD conversion)
- **Role-based access** (Admin vs Country Managers)
- **Exportable reports** in PDF and CSV formats

### What can you do with this dashboard?

1. **Monitor Performance**: View key metrics like Non-Revenue Water (NRW), Cost Recovery Ratio, Service Coverage, and more
2. **Compare Countries**: Analyze performance across Uganda, Cameroon, Lesotho, and Malawi
3. **Identify Issues**: Spot underperforming zones, payment risks, and service gaps
4. **Generate Reports**: Export data and insights for stakeholder presentations
5. **Get AI Insights**: Ask the AI assistant questions about your data

---

## ✨ Features

### Five Analytical Domains

| Domain | Description | Key Metrics |
|--------|-------------|-------------|
| 📊 **Overview** | High-level KPI scorecard | 10 summary KPIs with benchmarks |
| 🏭 **Production** | Water production operations | Production volume, Service hours, NRW |
| 🚰 **Service** | Service quality metrics | Water quality, Complaints, Metering |
| 🌍 **Access** | Coverage and equity | JMP ladder, Zone coverage gaps |
| 💰 **Finance** | Financial sustainability | OCCR, Collection efficiency, Payment risk |
| 📋 **Reports** | Export and analysis | PDF/CSV exports, Custom reports |

### AI Features

- **AI Data Assistant**: Chat interface for data questions
- **Automated Insights**: AI-generated analysis per domain
- **Smart Recommendations**: Actionable suggestions based on KPIs

### Finance Domain Highlights

   - Operating Cost Coverage Ratio (OCCR)
   - Revenue collection efficiency
   - Financial waterfall analysis
- Customer payment behavior by zone
- Payment risk dashboard (High/Medium/Low Risk customers)
- Commercial vs. Physical NRW breakdown

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Google Gemini API key (optional, for AI features)

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd DASHADI

# 2. Create virtual environment
python -m venv .venv

# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure secrets (see Configuration section)

# 5. Run the dashboard
streamlit run app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`

### Configuration

1. **Copy the secrets template:**
```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

2. **Edit `.streamlit/secrets.toml`** with your values:
   ```toml
   GEMINI_API_KEY = "your_actual_api_key"
   ```

### Verify Data Files

Ensure all required CSV files are in the `Data/` directory:

```
Data/
├── production.csv
├── billing.csv          # 720K+ customer records
├── w_service.csv
├── s_service.csv
├── w_access.csv
├── s_access.csv
├── all_fin_service.csv
└── all_national.csv
```

---

## 🔐 Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Uganda Manager | `uganda_manager` | `uganda123` |
| Malawi Manager | `malawi_manager` | `malawi123` |
| Lesotho Manager | `lesotho_manager` | `lesotho123` |
| Cameroon Manager | `cameroon_manager` | `cameroon123` |



---

## 🔑 Managing User Passwords

User credentials are stored in `config/users.yaml` with bcrypt-hashed passwords. Here's how to change passwords or add new users:

### Step 1: Generate a Hashed Password

Run this command in your terminal (make sure your virtual environment is activated):

```bash
# Quick one-liner to generate a hashed password
python -c "import streamlit_authenticator as stauth; print(stauth.Hasher.hash('YOUR_NEW_PASSWORD'))"
```

**Example:**
```bash
# Generate hash for password "SecurePass2024"
python -c "import streamlit_authenticator as stauth; print(stauth.Hasher.hash('SecurePass2024'))"

# Output (example - yours will be different):
# $2b$12$xYz123AbCdEfGhIjKlMnOpQrStUvWxYz456789AbCdEfGhIjKlMn
```

### Step 2: Update the Users File

Edit `config/users.yaml` and replace the password hash:

```yaml
credentials:
  usernames:
    admin:
      name: Administrator
      password: $2b$12$YOUR_NEW_HASH_HERE
      email: admin@washboard.org
      role: admin
      country: null
```

### Step 3: Add a New User (Optional)

To add a new user, copy an existing user block and modify it:

```yaml
    new_user:
      name: New User Name
      password: $2b$12$GENERATED_HASH_HERE
      email: newuser@example.com
      role: country_manager  # or 'admin'
      country: Uganda  # Set to null for admin access to all countries
```

### User Roles

| Role | Access Level |
|------|--------------|
| `admin` | Full access to all countries, can navigate between country dashboards |
| `country_manager` | Access only to assigned country's data |

---

## 📖 Data Dictionary

### Data Sources (8 CSV Files)

| File | Frequency | Granularity | Records |
|------|-----------|-------------|---------|
| `production.csv` | Daily | Source | ~36K |
| `billing.csv` | Monthly | Customer | ~720K |
| `w_service.csv` | Monthly | Zone | ~1.5K |
| `s_service.csv` | Monthly | Zone | ~1.5K |
| `w_access.csv` | Annual | Zone | ~200 |
| `s_access.csv` | Annual | Zone | ~200 |
| `all_fin_service.csv` | Monthly | City | ~500 |
| `all_national.csv` | Annual | National | ~50 |

### Key Variables

#### Production Domain
| Variable | Type | Unit | Description |
|----------|------|------|-------------|
| `production_m3` | Float | m³ | Daily water production volume |
| `service_hours` | Float | hours/day | Hours of water supply per day |
| `source` | String | - | Water extraction source name |
| `date_YYMMDD` | Date | YYYY/MM/DD | Production date |

#### Water Service Domain
| Variable | Type | Unit | Description |
|----------|------|------|-------------|
| `households` | Integer | count | Number of households served |
| `metered` | Float | m³ | Metered water consumption |
| `total_consumption` | Float | m³ | Total estimated consumption |
| `tests_conducted_chlorine` | Integer | count | Chlorine tests conducted |
| `test_passed_chlorine` | Integer | count | Chlorine tests passed |

#### Access Domain (JMP Ladder)
| Variable | Type | Unit | Description |
|----------|------|------|-------------|
| `safely_managed` | Float | population | Population with safely managed access |
| `basic` | Float | population | Population with basic access |
| `limited` | Float | population | Population with limited access |
| `unimproved` | Float | population | Population with unimproved access |
| `popn_total` | Float | thousands | Total zone population |

#### Financial Domain
| Variable | Type | Unit | Description |
|----------|------|------|-------------|
| `sewer_billed` | Float | local currency | Total amount billed |
| `sewer_revenue` | Float | local currency | Total revenue collected |
| `opex` | Float | local currency | Operating expenditure |
| `complaints` | Integer | count | Customer complaints received |

#### Billing (Customer-Level)
| Variable | Type | Unit | Description |
|----------|------|------|-------------|
| `customer_id` | String | - | Unique customer identifier |
| `consumption_m3` | Float | m³ | Monthly water consumption |
| `billed` | Float | local currency | Amount billed |
| `paid` | Float | local currency | Amount paid |

---

## 📈 Key Performance Indicators

| KPI | Benchmark | Formula |
|-----|-----------|---------|
| **Water Coverage** | 100% | (Safely Managed + Basic) / Total Population × 100 |
| **Non-Revenue Water (NRW)** | ≤25% | (Production - Billed) / Production × 100 |
| **Cost Recovery Ratio** | ≥100% | Revenue / Operating Expenses × 100 |
| **Collection Efficiency** | ≥95% | Revenue Collected / Total Billed × 100 |
| **Service Continuity** | 24 hrs | Average service hours per day |
| **Water Quality Compliance** | ≥95% | Tests Passed / Tests Conducted × 100 |
| **Metering Ratio** | ≥95% | Metered / Total Consumption × 100 |
| **Staff Productivity** | ≤7 | Staff Count / Connections × 1000 |

---

## 🏗️ Project Architecture

```
DASHADI/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── config/
│   └── users.yaml           # User authentication config
├── Data/                    # CSV data files (8 files)
├── page_modules/            # Dashboard page components
│   ├── home.py             # Landing page
│   ├── overview.py         # KPI scorecard + AI chat
│   ├── production.py       # Production analytics
│   ├── service.py          # Service quality
│   ├── access.py           # Coverage analysis
│   ├── finance.py          # Financial metrics
│   └── reports.py          # Export functionality
├── utils/                   # Shared utilities
│   ├── data_loader.py      # Data loading + caching
│   ├── kpi_calculator.py   # KPI formulas
│   ├── visualizations.py   # Chart templates
│   ├── ai_insights.py      # Gemini AI integration
│   ├── currency_config.py  # Multi-currency support
│   └── theme.py            # Light/dark theme
├── assets/                  # Static assets (logos)
└── styles/                  # Custom CSS
```

### Technology Stack

- **Frontend Framework**: Streamlit 1.28+
- **Data Processing**: Pandas 2.0+, NumPy 1.24+
- **Visualization**: Plotly 5.17+
- **AI Integration**: Google Gemini API
- **Authentication**: streamlit-authenticator
- **Caching**: Streamlit's built-in caching (@st.cache_data)

---

## 🚀 Deployment

### Streamlit Cloud (Recommended)

1. **Push code to GitHub** (ensure secrets are NOT committed)

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set main file path: `app.py`

3. **Configure Secrets in Streamlit Cloud:**
   - Go to App Settings → Secrets
   - Add your secrets in TOML format:
   ```toml
   GEMINI_API_KEY = "your_api_key"
   ```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Optional | Google Gemini API key for AI features |

---

## 🔒 Security Notes

- **Never commit** `.streamlit/secrets.toml` or `.env` files
- **Rotate API keys** if accidentally exposed
- **Change default passwords** before production
- **Use HTTPS** in production deployments
---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

** For better water services in Africa**

*Last Updated: December 2025 |Version 1.0.0*
