# Weekly Report Generator for E-commerce BI Platform

This script automatically generates comprehensive weekly executive reports in multiple formats (PDF, Excel, CSV) with key performance indicators, insights, and business recommendations.

## Features

- Automated data extraction from the SQLite data warehouse
- Multi-format report generation (PDF, Excel, CSV)
- Executive summary with key metrics
- Visual charts and graphs
- Business insights and recommendations
- Configurable date ranges
- Professional formatting and layout
- Error handling and logging

## Requirements

- Python 3.7+
- Required packages: pandas, numpy, sqlite3, matplotlib, seaborn, reportlab, openpyxl, jinja2, weasyprint or pdfkit
- Access to the ecommerce_bi.db SQLite database

## Installation

```bash
pip install pandas numpy matplotlib seaborn reportlab openpyxl jinja2 weasyprint
```

## Usage

```bash
# Generate report for the last week
python weekly_report_generator.py

# Generate report for a specific date range
python weekly_report_generator.py --start-date 2023-01-01 --end-date 2023-01-07

# Generate report in specific format only
python weekly_report_generator.py --format pdf
```

## Output Files

The script generates the following files in the `reports/output/` directory:

- `weekly_report_[timestamp].pdf` - Comprehensive PDF report
- `weekly_report_[timestamp].xlsx` - Excel workbook with multiple sheets
- `weekly_report_[timestamp]_executive_summary.csv` - CSV summary of key metrics
- `charts/` - Directory containing individual chart images

## Report Sections

1. **Executive Overview**
   - Key performance indicators (KPIs)
   - Week-over-week changes
   - Highlights and areas of concern

2. **Sales Performance**
   - Revenue trends
   - Top selling products
   - Sales by category
   - Geographic distribution

3. **Customer Insights**
   - Customer acquisition and retention
   - Segmentation performance
   - Lifetime value trends
   - Purchase frequency analysis

4. **Product Analysis**
   - Inventory turnover
   - Product performance rankings
   - Seasonal trends
   - Stock levels

5. **Marketing Effectiveness**
   - Campaign ROI
   - Channel performance
   - Conversion metrics
   - Cost analysis

6. **Financial Summary**
   - Profit and loss statement
   - Margin analysis
   - Cost breakdown
   - Cash flow indicators

7. **Operational Metrics**
   - Order fulfillment
   - Return rates
   - Shipping performance
   - Payment method usage

8. **Business Recommendations**
   - Data-driven action items
   - Prioritized initiatives
   - Risk mitigation strategies
   - Opportunity identification

## Configuration

Edit the `config.yaml` file to customize:
- Report title and branding
- Color scheme and styling
- Data source connection details
- Output directory paths
- Chart dimensions and quality
- Email distribution list (if enabled)
- Custom metrics and calculations

## Extending the Report

To add new sections:
1. Create a new method in the `ReportGenerator` class
2. Add the method to the report generation sequence
3. Define any new queries or calculations needed
4. Create corresponding visualization methods
5. Update the template if using HTML/CSS approach

## Dependencies

The script requires the following Python packages:
- pandas: Data manipulation and analysis
- numpy: Numerical operations
- matplotlib & seaborn: Visualization creation
- reportlab: PDF generation
- openpyxl: Excel file creation
- jinja2: Template rendering
- weasyprint or pdfkit: HTML to PDF conversion (optional)

## Schedule Automation

To run this report automatically on a weekly basis:

### Using cron (Linux/Mac)
```bash
# Edit crontab
crontab -e

# Add line to run every Monday at 8 AM
0 8 * * 1 /usr/bin/python3 /path/to/weekly_report_generator.py
```

### Using Task Scheduler (Windows)
1. Create a basic task
2. Set trigger: Weekly, every Monday at 8:00 AM
3. Set action: Start a program
4. Program: python
5. Arguments: /path/to/weekly_report_generator.py
6. Set start in: /path/to/script/directory

## Customization

### Changing Date Ranges
Modify the `get_date_range()` function to change how the reporting period is determined.

### Adding New Metrics
1. Add SQL queries to the `DataExtractor` class
2. Create calculation methods in the `MetricsCalculator` class
3. Add visualization methods in the `ChartGenerator` class
4. Update the report template to include the new section

### Changing Output Formats
To add new formats:
1. Implement the format in the `ReportExporter` class
2. Add format selection to the argument parser
3. Update the main generation loop

## Security Considerations

- Never hardcode database passwords
- Use environment variables or secure credential stores
- Restrict file system permissions on output directories
- Sanitize any user inputs if extending for web use
- Consider encrypting sensitive reports

## Logging

The script uses Python's logging module with output to:
- Console (INFO level and above)
- File: `logs/report_generator_[timestamp].log` (DEBUG level and above)

## Version History

- v1.0.0: Initial release with core functionality
- v1.1.0: Added email distribution capability
- v1.2.0: Improved chart formatting and template system
- v1.3.0: Added support for custom metrics and calculations