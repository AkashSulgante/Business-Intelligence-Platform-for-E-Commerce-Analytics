# E-commerce BI Platform - Claude Code Guidelines

## Project Overview
This is an end-to-end Business Intelligence platform for an e-commerce company. The platform includes data extraction, transformation, loading, analysis, visualization, and automated reporting.

## Development Guidelines

### Code Style
- Follow PEP8 for Python code
- Use type hints for function signatures
- Write docstrings for all public functions and classes
- Keep functions focused and under 50 lines when possible
- Use descriptive variable and function names

### SQL Guidelines
- Use uppercase for SQL keywords
- Use snake_case for table and column names
- Comment complex queries
- Use aliases for table names in joins
- Format queries for readability

### Git Practices
- Commit frequently with descriptive messages
- Pull before pushing to avoid conflicts
- Use feature branches for new features
- Tag releases with version numbers

### Testing
- Write unit tests for new functionality
- Run tests before committing
- Maintain at least 80% test coverage for critical paths
- Test edge cases and error conditions

### Documentation
- Update README.md for major changes
- Keep docstrings updated
- Document complex business logic
- Create examples in docstrings when helpful

### Performance Considerations
- Use vectorized pandas operations when possible
- Avoid iterating over DataFrames row by row
- Use appropriate database indexes
- Consider chunking for large data loads

## Common Tasks

### Running the Full Pipeline
```bash
python etl/pipeline.py
```

### Running Specific Stages
```bash
python etl/pipeline.py extract
python etl/pipeline.py transform
python etl/pipeline.py load
```

### Running Analyses
```bash
python -m analysis.customer_segmentation
python -m analysis.sales_forecasting
python -m analysis.cohort_analysis
python -m analysis.retention_analysis
python -m analysis.kpi_calculation
```

### Generating Reports
```bash
python reports/weekly_report_generator.py
```

### Running Tests
```bash
python tests/run_tests.py
```

### Running Specific Test Modules
```bash
python tests/run_tests.py test_etl
python tests/run_tests.py test_analysis
python tests/run_tests.py test_reporting
```

## Project Structure Reference
- `etl/` - Extract, Transform, Load pipelines
- `analysis/` - Analytical models and insights
- `dashboard/` - Power BI and Looker Studio templates
- `reports/` - Automated reporting scripts
- `docs/` - Documentation files
- `tests/` - Unit and integration tests
- `data/` - Raw, processed, and warehouse data

## Environment Variables
- `LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- Other configuration should be in config files or passed as arguments

## Troubleshooting
- Check logs in the `logs/` directory for detailed error information
- Verify database connections and file permissions
- Ensure all required Python packages are installed
- For memory issues, consider processing data in chunks