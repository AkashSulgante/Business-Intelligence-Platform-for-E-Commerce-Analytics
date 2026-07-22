# Looker Studio Data Source Configuration Template

This file provides a template for setting up data sources in Looker Studio for the E-commerce BI platform.

## Data Source Configuration

When setting up your data source in Looker Studio, use the following configuration based on your chosen connection method:

### Option 1: Google Sheets Connection (Recommended)
If you're using exported CSV data in Google Sheets:

1. **Spreadsheet URL**: [Your Google Sheet URL containing the exported tables]
2. **Worksheet**: Select the appropriate sheet for each table
3. **First Row as Header**: ✓ Checked
4. **Include Hidden Fields**: □ Unchecked (unless needed)

### Option 2: Database Connection (Cloud SQL, etc.)
If connecting directly to a database:

1. **Connection Type**: [PostgreSQL/MySQL/etc. based on your database]
2. **Host**: [Your database host]
3. **Port**: [Standard port: 5432 for PostgreSQL, 3306 for MySQL]
4. **Database Name**: [Your database name]
5. **Username**: [Database username]
6. **Password**: [Database password]
7. **SSL**: [Configure as required by your provider]

### Required Tables
Create separate data sources for each of these tables, or use custom queries to join them:

1. **fact_sales** - Main fact table with transaction data
2. **dim_date** - Date dimension for time intelligence
3. **dim_customers** - Customer demographic and segmentation data
4. **dim_products** - Product information and categorization
5. **dim_orders** - Order status and details
6. **dim_payments** - Payment method information
7. **dim_returns** - Return and refund data
8. **dim_marketing** - Marketing campaign and spend data

### Field Types & Aggregation
For each field in your data source, set the appropriate:

**Type**:
- Text: For IDs, names, descriptions, categories
- Number: For quantities, prices, amounts, counts
- Date/Time: For date fields
- Boolean: For true/false fields
- Geo: For geographic fields (if available)
- Currency: For monetary amounts (if supported)

**Aggregation**:
- Sum: For additive metrics (revenue, profit, quantity, etc.)
- Average: For rates, ratios, averages
- Count: For counting distinct values
- Count Distinct: For unique counts (customers, orders, products)
- None: For dimensions and IDs

### Recommended Field Configurations

#### fact_sales Table
- sales_id: Text, None
- date_id: Number, None (use date dimension instead)
- customer_id: Text, None
- product_id: Text, None
- order_id: Text, None
- payment_id: Text, None
- quantity: Number, Sum
- unit_price: Number, Average
- total_price: Number, Sum (Primary revenue metric)
- profit: Number, Sum (Primary profit metric)
- freight_value: Number, Sum
- return_id: Text, None
- marketing_id: Text, None

#### dim_date Table
- date_id: Number, None
- date: Date, None (Primary date field)
- day: Number, None
- month: Number, None
- quarter: Number, None
- year: Number, None
- day_of_week: Number, None
- day_name: Text, None
- month_name: Text, None
- is_weekend: Boolean, None
- is_holiday: Boolean, None
- season: Text, None

#### dim_customers Table
- customer_id: Text, None
- customer_unique_id: Text, None
- customer_zip_code_prefix: Number, None
- customer_city: Text, None
- customer_state: Text, None
- customer_lifetime_value: Number, Average
- customer_segment: Text, None
- acquisition_date: Date, None
- is_active: Boolean, None

#### dim_products Table
- product_id: Text, None
- product_category_name: Text, None
- product_category_name_english: Text, None
- product_name_lenght: Number, Average
- product_description_lenght: Number, Average
- product_photos_qty: Number, Average
- product_weight_g: Number, Average
- product_length_cm: Number, Average
- product_height_cm: Number, Average
- product_width_cm: Number, Average
- product_volume_liters: Number, Average
- product_category: Text, None
- product_brand: Text, None
- product_price: Number, Average
- product_status: Text, None

### Data Freshness Settings
Set appropriate refresh rates based on your data update frequency:
- Near real-time: Every 15 minutes (if supported)
- Hourly: For frequently updated operational data
- Daily: For most business reporting
- Weekly: For slower-changing dimensional data

### Authentication & Sharing
- Use service accounts for automated refresh
- Set appropriate viewing/editing permissions
- Consider using community connectors if native support is lacking
- Document credentials securely (never share in plain text)

## Troubleshooting Common Issues

### "Data temporarily unavailable"
- Check connection credentials
- Verify database/server is accessible
- Confirm network/firewall settings allow connections
- Try refreshing the connection

### Incorrect aggregations
- Verify field types are set correctly
- Check that aggregation settings match intended usage
- Look for unexpected null values affecting calculations

### Missing fields
- Confirm all required columns are included in your SELECT/query
- Check for typos in field names
- Ensure data source refresh has completed

### Performance issues
- Apply filters at the data source level
- Use extracts or cached data where appropriate
- Limit date ranges in default views
- Consider pre-aggregating large fact tables

## Template Sharing
To share your configured data source as a template:
1. Configure your data source completely
2. In the data source settings, look for "Shareable link" or "Make copyable" options
3. Enable sharing and distribute the link
4. Recipients can then create their own copy with the same configuration

## Maintenance
Regularly check:
- Connection status and credentials
- Data freshness and last refresh time
- Schema changes in source database
- Performance metrics and optimize as needed
- Security permissions and access logs

For the most current information on data source capabilities and limitations, refer to the official Looker Studio documentation:

https://support.google.com/datastudio/answer/6370388