"""
Data transformation module for the E-commerce BI pipeline.
Handles cleaning, transformation, and preparation of data for loading into the data warehouse.
"""

import pandas as pd
import numpy as np
import re
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from .utils import setup_logging, handle_missing_values, remove_duplicates, clean_column_names, convert_data_types
except ImportError:  # pragma: no cover - allows running as python etl/transform.py
    from etl.utils import setup_logging, handle_missing_values, remove_duplicates, clean_column_names, convert_data_types

# Initialize logger
logger = setup_logging()

def clean_ecommerce_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and preprocess the raw e-commerce data.

    Args:
        df: Raw DataFrame from extraction

    Returns:
        Cleaned DataFrame
    """
    logger.info("Starting data cleaning process")
    df_clean = df.copy()

    # 1. Clean column names
    df_clean = clean_column_names(df_clean)
    logger.info("Column names cleaned")

    # 2. Remove duplicate rows
    initial_rows = len(df_clean)
    df_clean = remove_duplicates(df_clean)
    duplicates_removed = initial_rows - len(df_clean)
    logger.info(f"Removed {duplicates_removed} duplicate rows")

    # 3. Handle missing values
    # For numeric columns, we'll fill with 0 or median based on column
    # For categorical, we'll fill with 'Unknown' or mode
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    categorical_cols = df_clean.select_dtypes(include=['object']).columns

    # Fill numeric missing with 0 for quantities/prices, median for others
    for col in numeric_cols:
        if 'quantity' in col.lower() or 'price' in col.lower():
            df_clean[col] = df_clean[col].fillna(0)
        else:
            df_clean[col] = df_clean[col].fillna(df_clean[col].median() if not df_clean[col].isnull().all() else 0)

    # Fill categorical missing with 'Unknown'
    for col in categorical_cols:
        df_clean[col] = df_clean[col].fillna('Unknown')

    logger.info("Missing values handled")

    # 4. Filter invalid data
    # Remove rows with invalid dates (if invoice_date column exists)
    date_cols = [col for col in df_clean.columns if 'date' in col.lower()]
    for col in date_cols:
        try:
            df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
            # Drop rows where date conversion failed (NaT)
            null_dates = df_clean[col].isna()
            if null_dates.any():
                logger.warning(f"Dropping {null_dates.sum()} rows with invalid dates in {col}")
                df_clean = df_clean[~null_dates].copy()
        except Exception as e:
            logger.warning(f"Could not process date column {col}: {str(e)}")

    # 5. Handle negative prices and quantities
    # For unit_price and price columns, negative values are invalid
    price_cols = [col for col in df_clean.columns if 'price' in col.lower() and 'unit' in col.lower()]
    for col in price_cols:
        if col in df_clean.columns:
            negative_count = (df_clean[col] < 0).sum()
            if negative_count > 0:
                logger.warning(f"Setting {negative_count} negative values in {col} to 0")
                df_clean.loc[df_clean[col] < 0, col] = 0

    # Quantity should not be negative (returns might be negative, but we'll handle separately)
    qty_cols = [col for col in df_clean.columns if 'quantity' in col.lower()]
    for col in qty_cols:
        if col in df_clean.columns:
            # We'll allow negative for returns but log them
            negative_count = (df_clean[col] < 0).sum()
            if negative_count > 0:
                logger.info(f"Found {negative_count} negative quantity values (potential returns) in {col}")

    # 6. Standardize text fields
    text_cols = df_clean.select_dtypes(include=['object']).columns
    for col in text_cols:
        if col in df_clean.columns:
            # Strip whitespace
            df_clean[col] = df_clean[col].astype(str).str.strip()
            # Replace multiple spaces with single space
            df_clean[col] = df_clean[col].str.replace(r'\s+', ' ', regex=True)
            # Standardize country names (if country column exists)
            if 'country' in col.lower():
                df_clean[col] = df_clean[col].str.title()
                # Specific country mappings
                country_mapping = {
                    'Usa': 'United States',
                    'Uk': 'United Kingdom',
                    'Uae': 'United Arab Emirates'
                }
                for wrong, correct in country_mapping.items():
                    df_clean[col] = df_clean[col].str.replace(wrong, correct, regex=False)

    # 7. Validate email format (if email column exists)
    email_cols = [col for col in df_clean.columns if 'email' in col.lower()]
    for col in email_cols:
        if col in df_clean.columns:
            # Simple email regex
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            invalid_emails = ~df_clean[col].astype(str).str.match(email_pattern, na=False)
            invalid_count = invalid_emails.sum()
            if invalid_count > 0:
                logger.warning(f"Found {invalid_count} invalid email addresses in {col}")
                # Optionally, we could set invalid emails to empty or a placeholder
                # For now, we'll just log

    # 8. Calculate derived fields
    # If we have quantity and unit_price, calculate total_price
    if 'quantity' in df_clean.columns and 'unit_price' in df_clean.columns:
        # Ensure numeric types
        df_clean['quantity'] = pd.to_numeric(df_clean['quantity'], errors='coerce')
        df_clean['unit_price'] = pd.to_numeric(df_clean['unit_price'], errors='coerce')
        # Calculate total price
        df_clean['total_price'] = df_clean['quantity'] * df_clean['unit_price']
        logger.info("Calculated total_price column")

    # 9. Handle refunds/returns (if applicable)
    # In the Online Retail II dataset, returns are indicated by negative quantity
    # and 'C' in invoice number
    if 'invoice' in df_clean.columns:
        # Identify returns (invoices starting with 'C')
        return_invoices = df_clean['invoice'].astype(str).str.startswith('C')
        df_clean['is_return'] = return_invoices
        return_count = return_invoices.sum()
        logger.info(f"Identified {return_count} return transactions")

    # 10. Final data type conversions
    # Ensure appropriate data types for key columns
    type_conversions = {}
    if 'customer_id' in df_clean.columns:
        # CustomerID might be float due to NaNs, convert to Int64 (nullable integer)
        try:
            df_clean['customer_id'] = df_clean['customer_id'].astype('Int64')
        except:
            pass  # Keep as is if conversion fails

    if 'stock_code' in df_clean.columns:
        df_clean['stock_code'] = df_clean['stock_code'].astype(str)

    if 'description' in df_clean.columns:
        df_clean['description'] = df_clean['description'].astype(str)

    logger.info("Data cleaning completed")
    return df_clean

def create_dimension_tables(df_clean: pd.DataFrame) -> dict:
    """
    Create dimension tables from the cleaned fact data.

    Args:
        df_clean: Cleaned DataFrame

    Returns:
        Dictionary of dimension DataFrames
    """
    logger.info("Creating dimension tables")
    dimensions = {}

    # Date Dimension
    if 'invoice_date' in df_clean.columns:
        # Ensure datetime
        df_clean['invoice_date'] = pd.to_datetime(df_clean['invoice_date'])
        # Extract date components
        date_df = pd.DataFrame({
            'date': df_clean['invoice_date'].dt.date.unique()
        })
        date_df['date_id'] = range(1, len(date_df) + 1)
        date_df['date'] = pd.to_datetime(date_df['date'])
        date_df['day'] = date_df['date'].dt.day
        date_df['month'] = date_df['date'].dt.month
        date_df['quarter'] = date_df['date'].dt.quarter
        date_df['year'] = date_df['date'].dt.year
        date_df['day_of_week'] = date_df['date'].dt.dayofweek  # Monday=0
        date_df['day_name'] = date_df['date'].dt.day_name()
        date_df['month_name'] = date_df['date'].dt.month_name()
        date_df['is_weekend'] = date_df['day_of_week'].isin([5, 6])  # Sat, Sun
        date_df['is_holiday'] = False  # Simplified - could be enhanced with holiday calendar
        date_df['season'] = date_df['month'].map({
            12: 'Winter', 1: 'Winter', 2: 'Winter',
            3: 'Spring', 4: 'Spring', 5: 'Spring',
            6: 'Summer', 7: 'Summer', 8: 'Summer',
            9: 'Fall', 10: 'Fall', 11: 'Fall'
        })
        dimensions['date'] = date_df[['date_id', 'date', 'day', 'month', 'quarter', 'year',
                                     'day_of_week', 'day_name', 'month_name', 'is_weekend',
                                     'is_holiday', 'season']].copy()
        logger.info(f"Created date dimension with {len(dimensions['date'])} rows")

    # Customer Dimension
    if 'customer_id' in df_clean.columns:
        customer_df = df_clean[['customer_id']].dropna().drop_duplicates()
        # Olist customer identifiers are UUID-like strings, so preserve them as
        # business keys and generate the integer warehouse key required by the
        # star schema.
        customer_df['customer_unique_id'] = customer_df['customer_id'].astype(str)
        customer_df['customer_id'] = range(1, len(customer_df) + 1)
        # In a real scenario, we would enrich with customer details
        # For now, we'll add placeholder columns
        customer_df['customer_zip_code_prefix'] = None
        customer_df['customer_city'] = None
        customer_df['customer_state'] = None
        customer_df['customer_lifetime_value'] = 0.0
        customer_df['customer_segment'] = None
        customer_df['acquisition_date'] = None
        customer_df['is_active'] = True
        dimensions['customers'] = customer_df[['customer_id', 'customer_unique_id',
                                             'customer_zip_code_prefix', 'customer_city', 'customer_state',
                                             'customer_lifetime_value', 'customer_segment', 'acquisition_date',
                                             'is_active']].copy()
        logger.info(f"Created customer dimension with {len(dimensions['customers'])} rows")

    # Product Dimension
    if 'stock_code' in df_clean.columns and 'description' in df_clean.columns:
        product_df = df_clean[['stock_code', 'description']].dropna().drop_duplicates()
        product_df['product_id'] = range(1, len(product_df) + 1)
        # Add placeholder product attributes
        product_df['product_category_name'] = None
        product_df['product_category_name_english'] = None
        product_df['product_name_lenght'] = product_df['description'].str.len()
        product_df['product_description_lenght'] = product_df['description'].str.len()
        product_df['product_photos_qty'] = 1  # Default
        product_df['product_weight_g'] = None
        product_df['product_length_cm'] = None
        product_df['product_height_cm'] = None
        product_df['product_width_cm'] = None
        product_df['product_volume_liters'] = None
        product_df['product_category'] = None
        product_df['product_brand'] = None
        product_df['product_price'] = 0.0  # Will be updated from fact
        product_df['product_status'] = 'active'
        dimensions['products'] = product_df[['product_id', 'stock_code', 'description',
                                           'product_category_name', 'product_category_name_english',
                                           'product_name_lenght', 'product_description_lenght',
                                           'product_photos_qty', 'product_weight_g', 'product_length_cm',
                                           'product_height_cm', 'product_width_cm', 'product_volume_liters',
                                           'product_category', 'product_brand', 'product_price',
                                           'product_status']].copy()
        logger.info(f"Created product dimension with {len(dimensions['products'])} rows")

    # Order Dimension
    if 'invoice' in df_clean.columns:
        order_df = df_clean[['invoice']].dropna().drop_duplicates()
        order_df['order_id'] = range(1, len(order_df) + 1)
        # Add order status and dates (if available)
        order_df['order_status'] = 'Processed'  # Default
        order_df['order_purchase_timestamp'] = df_clean.groupby('invoice')['invoice_date'].min().values if 'invoice_date' in df_clean.columns else None
        order_df['order_approved_at'] = order_df['order_purchase_timestamp']  # Simplified
        order_df['order_delivered_carrier_date'] = order_df['order_purchase_timestamp']  # Simplified
        order_df['order_delivered_customer_date'] = order_df['order_purchase_timestamp']  # Simplified
        order_df['order_estimated_delivery_date'] = order_df['order_purchase_timestamp']  # Simplified
        order_df['order_status_category'] = order_df['order_status']
        dimensions['orders'] = order_df[['order_id', 'invoice', 'order_status',
                                       'order_purchase_timestamp', 'order_approved_at',
                                       'order_delivered_carrier_date', 'order_delivered_customer_date',
                                       'order_estimated_delivery_date', 'order_status_category']].copy()
        logger.info(f"Created order dimension with {len(dimensions['orders'])} rows")

    # Payment Dimension (simplified)
    # In real scenario, we would have payment details
    # For now, we'll create a generic payment type
    dimensions['payments'] = pd.DataFrame({
        'payment_id': [1, 2, 3],
        'payment_type': ['Credit Card', 'Bank Transfer', 'PayPal'],
        'payment_sequential': [1, 1, 1],
        'payment_installments': [1, 1, 1],
        'payment_value': [0.0, 0.0, 0.0]  # Will be updated from fact
    })
    logger.info("Created payment dimension with 3 rows")

    # Returns Dimension (if returns exist)
    if 'is_return' in df_clean.columns and df_clean['is_return'].any():
        returns_df = df_clean[df_clean['is_return'] == True][['invoice', 'stock_code']].dropna().drop_duplicates()
        if len(returns_df) > 0:
            returns_df['return_id'] = range(1, len(returns_df) + 1)
            returns_df['return_reason'] = 'Customer Return'  # Placeholder
            returns_df['return_origin'] = 'Domestic'
            returns_df['return_condition'] = 'Used'
            returns_df['return_shipping_cost'] = 0.0
            returns_df['return_refund_amount'] = 0.0  # Will be calculated from fact
            dimensions['returns'] = returns_df[['return_id', 'invoice', 'stock_code',
                                              'return_reason', 'return_origin', 'return_condition',
                                              'return_shipping_cost', 'return_refund_amount']].copy()
            logger.info(f"Created returns dimension with {len(dimensions['returns'])} rows")
        else:
            dimensions['returns'] = pd.DataFrame(columns=['return_id', 'invoice', 'stock_code',
                                                        'return_reason', 'return_origin', 'return_condition',
                                                        'return_shipping_cost', 'return_refund_amount'])
            logger.info("Created empty returns dimension")
    else:
        dimensions['returns'] = pd.DataFrame(columns=['return_id', 'invoice', 'stock_code',
                                                    'return_reason', 'return_origin', 'return_condition',
                                                    'return_shipping_cost', 'return_refund_amount'])
        logger.info("Created empty returns dimension (no returns detected)")

    # Marketing Dimension (placeholder - in real scenario would come from marketing data)
    dimensions['marketing'] = pd.DataFrame({
        'marketing_id': [1],
        'campaign_name': ['General Marketing'],
        'channel': ['Online'],
        'start_date': [pd.Timestamp('2020-01-01')],
        'end_date': [pd.Timestamp('2020-12-31')],
        'budget': [0.0],
        'impressions': [0],
        'clicks': [0],
        'conversions': [0],
        'revenue_attributed': [0.0]
    })
    logger.info("Created marketing dimension with 1 row")

    return dimensions

def create_fact_table(df_clean: pd.DataFrame, dimensions: dict) -> pd.DataFrame:
    """
    Create the fact table by joining cleaned data with dimension surrogate keys.

    Args:
        df_clean: Cleaned DataFrame
        dimensions: Dictionary of dimension DataFrames

    Returns:
        Fact table DataFrame ready for loading
    """
    logger.info("Creating fact table")
    fact_df = df_clean.copy()

    # Start with a copy of the cleaned data
    # We'll add surrogate keys by joining with dimension tables

    # Date key
    if 'date' in dimensions and 'invoice_date' in fact_df.columns:
        # Date dimension is day-grained, while source timestamps include a
        # time-of-day.  Normalize before joining so every transaction matches.
        fact_df['invoice_date'] = pd.to_datetime(fact_df['invoice_date']).dt.normalize()
        date_lookup = dimensions['date'][['date', 'date_id']].copy()
        date_lookup['date'] = pd.to_datetime(date_lookup['date'])
        fact_df = fact_df.merge(date_lookup, left_on='invoice_date', right_on='date', how='left')
        # The source may or may not already contain a ``date`` column.
        # Remove only the lookup column created by the merge.
        if 'date' in fact_df.columns:
            fact_df.drop(columns=['date'], inplace=True)
        fact_df.rename(columns={'date_x': 'invoice_date'}, inplace=True)

    # Customer key
    if 'customers' in dimensions and 'customer_id' in fact_df.columns:
        cust_lookup = dimensions['customers'][['customer_unique_id', 'customer_id']].rename(
            columns={'customer_unique_id': '_source_customer_id', 'customer_id': '_warehouse_customer_id'}
        )
        fact_df['customer_id'] = fact_df['customer_id'].astype(str)
        fact_df = fact_df.merge(cust_lookup, left_on='customer_id', right_on='_source_customer_id', how='left')
        fact_df.drop(columns=['customer_id', '_source_customer_id'], inplace=True)
        fact_df.rename(columns={'_warehouse_customer_id': 'customer_id'}, inplace=True)

    # Product key
    if 'products' in dimensions and 'stock_code' in fact_df.columns:
        prod_lookup = dimensions['products'][['stock_code', 'product_id']].rename(
            columns={'product_id': '_warehouse_product_id'}
        )
        fact_df = fact_df.merge(prod_lookup, on='stock_code', how='left')
        if 'product_id' in fact_df.columns:
            fact_df.drop(columns=['product_id'], inplace=True)
        fact_df.rename(columns={'_warehouse_product_id': 'product_id'}, inplace=True)

    # Order key
    if 'orders' in dimensions and 'invoice' in fact_df.columns:
        order_lookup = dimensions['orders'][['invoice', 'order_id']].rename(
            columns={'order_id': '_warehouse_order_id'}
        )
        fact_df = fact_df.merge(order_lookup, on='invoice', how='left')
        if 'order_id' in fact_df.columns:
            fact_df.drop(columns=['order_id'], inplace=True)
        fact_df.rename(columns={'_warehouse_order_id': 'order_id'}, inplace=True)

    # Payment key (default to first payment type for simplicity)
    if 'payments' in dimensions:
        # Assign payment_key = 1 (Credit Card) for all transactions
        fact_df['payment_id'] = 1

    # Return key
    if 'returns' in dimensions and 'is_return' in fact_df.columns and fact_df['is_return'].any():
        # For returns, we need to match by invoice and stock_code
        return_lookup = dimensions['returns'][['invoice', 'stock_code', 'return_id']].copy()
        fact_df = fact_df.merge(return_lookup, on=['invoice', 'stock_code'], how='left')
        # Fill non-return transactions with NULL
        fact_df['return_id'] = fact_df['return_id'].where(fact_df['is_return'] == True, None)
    else:
        fact_df['return_id'] = None

    # Marketing key (default to first marketing campaign)
    if 'marketing' in dimensions:
        fact_df['marketing_id'] = 1

    # Calculate financial measures
    if 'quantity' in fact_df.columns and 'unit_price' in fact_df.columns:
        fact_df['quantity'] = pd.to_numeric(fact_df['quantity'], errors='coerce')
        fact_df['unit_price'] = pd.to_numeric(fact_df['unit_price'], errors='coerce')
        fact_df['total_price'] = fact_df['quantity'] * fact_df['unit_price']

        # Profit calculation (simplified: 20% margin)
        fact_df['profit'] = fact_df['total_price'] * 0.2
        # For returns, profit would be negative
        if 'is_return' in fact_df.columns:
            fact_df.loc[fact_df['is_return'] == True, 'profit'] = -fact_df.loc[fact_df['is_return'] == True, 'total_price'] * 0.2

        # Freight value (placeholder)
        fact_df['freight_value'] = 0.0

    # Select and order final fact table columns
    fact_columns = [
        'sales_id',  # We'll generate this
        'date_id',
        'customer_id',
        'product_id',
        'order_id',
        'payment_id',
        'quantity',
        'unit_price',
        'total_price',
        'profit',
        'freight_value',
        'return_id',
        'marketing_id'
    ]

    # Add surrogate key for fact table
    fact_df['sales_id'] = range(1, len(fact_df) + 1)

    # Ensure we have all required columns
    for col in fact_columns:
        if col not in fact_df.columns:
            fact_df[col] = None

    # Reorder columns
    fact_df = fact_df[fact_columns]

    logger.info(f"Created fact table with {len(fact_df)} rows")
    return fact_df

def transform_data(raw_data: dict) -> dict:
    """
    Main transformation pipeline that processes raw data into star schema components.

    Args:
        raw_data: Dictionary of raw DataFrames from extraction

    Returns:
        Dictionary containing cleaned data, dimension tables, and fact table
    """
    logger.info("Starting data transformation process")

    # Process the main retail dataset
    if 'online_retail_ii' not in raw_data:
        raise ValueError("Required dataset 'online_retail_ii' not found in raw data")

    df_raw = raw_data['online_retail_ii']
    logger.info(f"Processing raw data with shape: {df_raw.shape}")

    # Step 1: Clean the data
    df_clean = clean_ecommerce_data(df_raw)
    logger.info(f"Data cleaning completed. Shape: {df_clean.shape}")

    # Step 2: Create dimension tables
    dimensions = create_dimension_tables(df_clean)

    # Step 3: Create fact table
    fact_table = create_fact_table(df_clean, dimensions)

    # Return all components
    result = {
        'cleaned_data': df_clean,
        'dimensions': dimensions,
        'fact_table': fact_table
    }

    logger.info("Data transformation completed successfully")
    return result

if __name__ == "__main__":
    # For testing - would normally be called from pipeline.py
    from .extract import extract_all, save_raw_data
    try:
        # Extract raw data
        raw_data = extract_all()
        # Save raw data
        for name, df in raw_data.items():
            save_raw_data(df, name)
        # Transform data
        result = transform_data(raw_data)
        # Save processed data
        processed_dir = Path(__file__).parent.parent.parent / "data" / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)
        # Save cleaned data
        save_dataframe_to_csv(result['cleaned_data'], processed_dir / "cleaned_data.csv")
        # Save dimensions
        for name, df in result['dimensions'].items():
            save_dataframe_to_csv(df, processed_dir / f"dim_{name}.csv")
        # Save fact table
        save_dataframe_to_csv(result['fact_table'], processed_dir / "fact_sales.csv")
        print("Transformation completed successfully")
    except Exception as e:
        logger.error(f"Transformation failed: {str(e)}")
        sys.exit(1)
