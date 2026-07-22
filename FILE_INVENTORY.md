# E-commerce BI Platform - File Inventory

This document lists all the files created in the repository for verification purposes.

## Root Directory
- README.md - Project overview and documentation
- .gitignore - Git ignore rules
- requirements.txt - Python dependencies
- LICENSE - MIT license
- CLAUDE.md - Claude Code guidelines
- demo.py - Demonstration script with sample data
- run_tests.py - Test runner script
- pyproject.toml - Pytest configuration

## ETL Pipeline (etl/)
- extract.py - Data extraction from sources
- transform.py - Data cleaning and transformation
- load.py - Loading data into SQLite warehouse
- pipeline.py - Main ETL orchestration
- utils.py - Shared utility functions
- __init__.pt - Package initializer

## Analysis Modules (analysis/)
- customer_segmentation.py - RFM analysis and clustering
- sales_forecasting.py - Time series forecasting models
- cohort_analysis.py - Customer cohort analysis
- retention_analysis.py - Customer retention and churn analysis
- kpi_calculation.py - Key performance indicator calculations
- __init__.py - Package initializer

## Dashboard Templates (dashboard/)
### Power BI (dashboard/PowerBI/)
- dashboard_documentation.md - Dashboard build instructions
- dax_measures.txt - DAX measures for calculated fields
- Ecommerce_BI_Template.pbit - Power BI template file

### Looker Studio (dashboard/LookerStudio/)
- looker_studio_documentation.md - Dashboard creation guide
- data_source_template.md - Data source configuration template
- looker_studio_documentation.md - Additional documentation

## Reports (reports/)
- weekly_report_generator.py - Automated weekly report generation
- weekly_report_generator.md - Report generator documentation
- output/ - Generated reports directory (created at runtime)

## Documentation (docs/)
- Architecture.md - System architecture description
- DataDictionary.md - Data warehouse schema reference
- BusinessRecommendations.md - Recommendation engine documentation

## Tests (tests/)
- test_etl.py - ETL pipeline tests
- test_analysis.py - Analysis module tests
- test_reporting.py - Reporting component tests
- __init__.py - Package initializer
- requirements.txt - Test-specific dependencies
- run_tests.py - Test execution script

## GitHub Actions (.github/workflows/)
- ci.yml - Continuous integration workflow

## Data Directories (created at runtime)
- data/raw/ - Raw downloaded data
- data/processed/ - Cleaned and transformed data
- data/warehouse/ - SQLite database file
- logs/ - Application logs
- reports/output/ - Generated reports
- reports/output/charts/ - Generated chart images

## Total Files: ~35 core code and documentation files