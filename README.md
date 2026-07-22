# End-to-End Business Intelligence Platform for an E-commerce Company

## Project Overview
This project implements a complete end-to-end Business Intelligence (BI) platform for an e-commerce company using only free and open-source tools. The platform covers the entire data lifecycle from data extraction to visualization and automated reporting.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Dataset](#dataset)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Dashboard](#dashboard)
- [Automated Reporting](#automated-reports)
- [Business Recommendations](#business-recommendations)
- [CI/CD Pipeline](#cicd-pipeline)
- [Testing](#testing)
- [License](#license)

## Features
- **Data Extraction**: Automated extraction from public e-commerce datasets
- **Data Warehouse**: SQLite-based data warehouse with star schema
- **ETL Pipeline**: Modular Python ETL pipeline with data validation
- **Analytical Modeling**: Customer segmentation, sales forecasting, cohort analysis, retention analysis
- **KPI Calculation**: Automated calculation of key business metrics
- **Interactive Dashboard**: Power BI/Looker Studio dashboard templates
- **Automated Reporting**: Weekly executive report generation
- **Business Recommendations**: Data-driven actionable insights
- **CI/CD**: GitHub Actions for automated testing and validation
- **Documentation**: Complete documentation including data dictionary and architecture

## Tech Stack
- **Language**: Python 3.9+
- **Libraries**: pandas, numpy, scikit-learn, statsmodels, matplotlib, seaborn, plotly
- **Database**: SQLite (lightweight, file-based, zero-configuration)
- **ETL**: Custom Python ETL pipeline
- **Dashboard**: Power BI Desktop (Free) or Looker Studio (Free)
- **Automation**: GitHub Actions
- **Version Control**: Git & GitHub
- **Documentation**: Markdown

## Dataset
We use the **Online Retail II Dataset** from the UCI Machine Learning Repository:
- **Source**: https://archive.ics.uci.edu/ml/datasets/Online+Retail+II
- **Description**: Online retail transactions from a UK-based registered non-store online retail from 01/12/2009 to 09/12/2011
- **Size**: ~1GB (2010-2011 year)
- **Features**: 8 attributes including InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country

Alternative datasets (if preferred):
- Brazilian E-Commerce Public Dataset (Olist) - Kaggle
- Instacart Market Basket Dataset - Kaggle

## Project Structure
```
ecommerce_bi_platform/
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
├── data/
│   ├── raw/              # Raw data as received from sources
│   ├── processed/        # Cleaned and transformed data
│   └── warehouse/        # Data warehouse (SQLite database)
├── sql/
│   ├── schema.sql        # Database schema definition
│   ├── create_tables.sql # Table creation scripts
│   ├── views.sql         # Analytical views
│   ├── stored_queries.sql# Reusable SQL queries
│   └── indexes.sql       # Database indexes for performance
├── etl/
│   ├── extract.py        # Data extraction logic
│   ├── transform.py      # Data transformation logic
│   ├── load.py           # Data loading to warehouse
│   ├── pipeline.py       # Main ETL pipeline orchestrator
│   └── utils.py          # Helper functions
├── analysis/
│   ├── customer_segmentation.py   # RFM, K-means clustering
│   ├── sales_forecasting.py       # Time series forecasting (ARIMA, Prophet)
│   ├── cohort_analysis.py         # Cohret analysis for retention
│   ├── retention_analysis.py      # Customer retention metrics
│   └── kpi_calculation.py         # Key Performance Indicators calculation
├── dashboard/
│   ├── PowerBI/               # Power BI template (.pbit) and documentation
│   └── LookerStudio/          # Looker Studio report template and datasource config
├── reports/
│   ├── weekly_report_generator.py # Automated weekly report generation
│   └── sample_reports/        # Sample generated reports
├── notebooks/                 # Jupyter notebooks for exploratory analysis
├── tests/                     # Unit and integration tests
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI/CD pipeline
├── docs/
│   ├── Architecture.md        # System architecture documentation
│   ├── DataDictionary.md      # Data dictionary and schema documentation
│   └── BusinessRecommendations.md # Data-driven business recommendations
└── assets/                    # Images, logos, and other static assets
```

## Setup Instructions

### 1. Prerequisites
- Python 3.9 or higher
- Git
- [Power BI Desktop (Free)](https://powerbi.microsoft.com/desktop/) OR [Looker Studio](https://datastudio.google.com/) (Free)
- GitHub account (for CI/CD)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/ecommerce_bi_platform.git
cd ecommerce_bi_platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks (optional)
pre-commit install
```

### 3. Data Acquisition
The ETL pipeline will automatically download the Online Retail II dataset from the UCI repository during the extraction phase.

### 4. Running the ETL Pipeline
```bash
# Initialize the data warehouse and run the full ETL pipeline
python etl/pipeline.py

# Or run individual components:
python etl/extract.py   # Download and save raw data
python etl/transform.py # Clean and transform data
python etl/load.py      # Load data into SQLite warehouse
```

### 5. Running Analyses
```bash
# Run all analyses
python -m analysis.customer_segmentation
python -m analysis.sales_forecasting
python -m analysis.cohort_analysis
python -m analysis.retention_analysis
python -m analysis.kpi_calculation

# Or run the analysis runner (if implemented)
python -m analysis.run_all
```

### 6. Generating Reports
```bash
# Generate weekly executive report
python reports/weekly_report_generator.py
```

### 7. Launching the Dashboard
- **Power BI**: Open `dashboard/PowerBI/Ecommerce_BI_Template.pbit` in Power BI Desktop
- **Looker Studio**: Use the datasource configuration in `dashboard/LookerStudio/datasource_config.json`

## Usage
1. First time setup: Run the complete ETL pipeline (`python etl/pipeline.py`)
2. Schedule regular updates: Use the GitHub Actions workflow or set up a local cron job
3. Explore analyses: Run individual analysis scripts or Jupyter notebooks
4. Generate reports: Run the weekly report generator
5. Explore insights: Open the dashboard and interact with the visualizations

## Dashboard
The dashboard provides interactive visualizations for:
- Executive Summary (Revenue, Orders, Customers, Growth)
- Sales Trends (Daily, Weekly, Monthly, Yearly)
- Customer Analysis (RFM Segmentation, Lifetime Value, Retention)
- Product Analysis (Top Sellers, Category Performance, Inventory)
- Geographic Analysis (Sales by Country, City)
- Return Analysis (Return Rates, Reasons)
- Marketing Campaign Performance
- Forecast vs Actual Comparison

## Automated Reports
The `weekly_report_generator.py` script generates:
- Executive summary PDF with key metrics and trends
- Customer insights segment analysis
- Product performance report
- Geographic performance breakdown
- Actionable business recommendations
- Automated email distribution (configurable)

## Business Recommendations
See [docs/BusinessRecommendations.md](docs/BusinessRecommendations.md) for:
- Customer segmentation strategies
- Inventory optimization recommendations
- Pricing strategy suggestions
- Marketing campaign improvements
- Customer retention initiatives
- Geographic expansion opportunities

## CI/CD Pipeline
The project includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that:
- Runs on every push and pull request
- Installs dependencies
- Runs the ETL pipeline with a sample dataset
- Executes all analysis scripts
- Runs unit and integration tests
- Validates dashboard datasource connections
- Generates and validates a sample report
- Deploys documentation to GitHub Pages (optional)

## Testing
Run the test suite:
```bash
pytest tests/
```

Test coverage includes:
- ETL pipeline components
- Data validation functions
- Analysis module functions
- Report generation functions
- Database schema validation

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- UCI Machine Learning Repository for the Online Retail II dataset
- Open-source community for pandas, numpy, scikit-learn, matplotlib, seaborn, plotly
- Microsoft for Power BI Desktop (Free)
- Google for Looker Studio (Free)
- GitHub for GitHub Actions

---
**Ready for your data science, data engineering, BI analyst, or analytics engineer portfolio!**
This project demonstrates end-to-end BI platform development skills highly valued in the industry.