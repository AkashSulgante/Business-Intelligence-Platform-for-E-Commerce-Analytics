"""
KPI calculation module for the E-commerce BI platform.
Implements calculation of key performance indicators.
"""

import pandas as pd
import numpy as np
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List
from datetime import datetime, timedelta

# Initialize logger
logger = logging.getLogger("analysis.kpi_calculation")

def get_db_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Create a connection to the SQLite data warehouse.

    Args:
        db_path: Path to the SQLite database file. If None, uses default path.

    Returns:
        SQLite connection object
    """
    if db_path is None:
        # Default path relative to this file
        current_dir = Path(__file__).resolve().parent.parent
        db_path = current_dir / "data" / "warehouse" / "ecommerce_bi.db"

    # Ensure the directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Create connection
    conn = sqlite3.connect(db_path)
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def load_kpi_data(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Load data required for KPI calculations from the data warehouse.

    Args:
        conn: SQLite connection object

    Returns:
        DataFrame with fact and dimension data for KPI calculations
    """
    query = """
    SELECT
        s.sales_id,
        s.date_id,
        s.customer_id,
        s.product_id,
        s.order_id,
        s.payment_id,
        s.quantity,
        s.unit_price,
        s.total_price,
        s.profit,
        s.freight_value,
        d.date,
        d.day_of_week,
        d.month_name,
        d.quarter,
        d.year,
        c.customer_id as customer_dim_id,
        c.customer_segment,
        p.product_id as product_dim_id,
        p.product_category_name_english,
        o.order_id as order_dim_id,
        o.order_status,
        pt.payment_id as payment_dim_id,
        pt.payment_type,
        r.return_id as return_dim_id,
        r.return_reason,
        m.marketing_id as marketing_dim_id,
        m.channel,
        m.campaign_name
    FROM fact_sales s
    JOIN dim_date d ON s.date_id = d.date_id
    LEFT JOIN dim_customers c ON s.customer_id = c.customer_id
    LEFT JOIN dim_products p ON s.product_id = p.product_id
    LEFT JOIN dim_orders o ON s.order_id = o.order_id
    LEFT JOIN dim_payments pt ON s.payment_id = pt.payment_id
    LEFT JOIN dim_returns r ON s.return_id = r.return_id
    LEFT JOIN dim_marketing m ON s.marketing_id = m.marketing_id
    """

    df = pd.read_sql_query(query, conn)
    df['date'] = pd.to_datetime(df['date'])
    return df

def calculate_revenue_kpis(df: pd.DataFrame) -> dict:
    """
    Calculate revenue-related KPIs.

    Args:
        df: DataFrame with sales data

    Returns:
        Dictionary of revenue KPIs
    """
    kpis = {}

    # Total revenue
    kpis['total_revenue'] = df['total_price'].sum()
    kpis['total_profit'] = df['profit'].sum() if 'profit' in df.columns else 0.0
    kpis['total_orders'] = df['order_id'].nunique() if 'order_id' in df.columns else 0
    kpis['total_customers'] = df['customer_id'].nunique() if 'customer_id' in df.columns else 0

    # Revenue by time period
    if 'date' in df.columns:
        df_sorted = df.sort_values('date')
        daily_revenue = df_sorted.groupby(df_sorted['date'].dt.date)['total_price'].sum()
        kpis['average_daily_revenue'] = daily_revenue.mean()
        kpis['peak_daily_revenue'] = daily_revenue.max()
        kpis['lowest_daily_revenue'] = daily_revenue.min()

        # Monthly revenue
        monthly_revenue = df_sorted.groupby([df_sorted['date'].dt.year, df_sorted['date'].dt.month])['total_price'].sum()
        kpis['average_monthly_revenue'] = monthly_revenue.mean()
        if len(monthly_revenue) >= 2:
            # Calculate month-over-month growth
            latest_month = monthly_revenue.iloc[-1]
            previous_month = monthly_revenue.iloc[-2]
            if previous_month != 0:
                kpis['mom_revenue_growth'] = (latest_month - previous_month) / previous_month
            else:
                kpis['mom_revenue_growth'] = 0

        # Quarterly revenue
        quarterly_revenue = df_sorted.groupby([df_sorted['date'].dt.year, df_sorted['date'].dt.quarter])['total_price'].sum()
        kpis['average_quarterly_revenue'] = quarterly_revenue.mean()
        if len(quarterly_revenue) >= 2:
            # Calculate quarter-over-quarter growth
            latest_quarter = quarterly_revenue.iloc[-1]
            previous_quarter = quarterly_revenue.iloc[-2]
            if previous_quarter != 0:
                kpis['qoq_revenue_growth'] = (latest_quarter - previous_quarter) / previous_quarter
            else:
                kpis['qoq_revenue_growth'] = 0

        # Yearly revenue
        yearly_revenue = df_sorted.groupby(df_sorted['date'].dt.year)['total_price'].sum()
        kpis['average_yearly_revenue'] = yearly_revenue.mean()
        if len(yearly_revenue) >= 2:
            # Calculate year-over-year growth
            latest_year = yearly_revenue.iloc[-1]
            previous_year = yearly_revenue.iloc[-2]
            if previous_year != 0:
                kpis['yoy_revenue_growth'] = (latest_year - previous_year) / previous_year
            else:
                kpis['yoy_revenue_growth'] = 0

    return kpis

def calculate_profitability_kpis(df: pd.DataFrame) -> dict:
    """
    Calculate profitability-related KPIs.

    Args:
        df: DataFrame with sales data

    Returns:
        Dictionary of profitability KPIs
    """
    kpis = {}

    # Total profit
    kpis['total_profit'] = df['profit'].sum()

    # Profit margin
    total_revenue = df['total_price'].sum()
    if total_revenue != 0:
        kpis['profit_margin'] = kpis['total_profit'] / total_revenue
    else:
        kpis['profit_margin'] = 0

    # Average profit per order
    order_profit = df.groupby('order_id')['profit'].sum()
    kpis['average_profit_per_order'] = order_profit.mean()

    # Profit by product category
    if 'product_category_name_english' in df.columns:
        profit_by_category = df.groupby('product_category_name_english')['profit'].sum()
        kpis['profit_by_category'] = profit_by_category.to_dict()
        # Most profitable category
        if len(profit_by_category) > 0:
            kpis['most_profitable_category'] = profit_by_category.idxmax()
            kpis['most_profitable_category_value'] = profit_by_category.max()

    return kpis

def calculate_customer_kpis(df: pd.DataFrame) -> dict:
    """
    Calculate customer-related KPIs.

    Args:
        df: DataFrame with sales data

    Returns:
        Dictionary of customer KPIs
    """
    kpis = {}

    # Total customers
    kpis['total_customers'] = df['customer_id'].nunique()

    # New customers (customers with first purchase in period)
    if 'date' in df.columns:
        # For simplicity, we'll define new customers as those whose first purchase
        # is in the last 30 days of data
        cutoff_date = df['date'].max() - timedelta(days=30)
        first_purchase_dates = df.groupby('customer_id')['date'].min()
        new_customers = first_purchase_dates[first_purchase_dates >= cutoff_date]
        kpis['new_customers_last_30_days'] = len(new_customers)
        if kpis['total_customers'] > 0:
            kpis['new_customer_rate'] = len(new_customers) / kpis['total_customers']
        else:
            kpis['new_customer_rate'] = 0

    # Average order value (AOV)
    order_values = df.groupby('order_id')['total_price'].sum()
    kpis['average_order_value'] = order_values.mean()
    kpis['median_order_value'] = order_values.median()

    # Purchase frequency
    if 'date' in df.columns and kpis['total_customers'] > 0:
        # Calculate average number of orders per customer
        orders_per_customer = df.groupby('customer_id')['order_id'].nunique()
        kpis['average_orders_per_customer'] = orders_per_customer.mean()

        # Purchase frequency (orders per customer per month)
        date_range = df['date'].max() - df['date'].min()
        months = max(date_range.days / 30.0, 1)  # At least 1 month
        kpis['purchase_frequency_per_month'] = kpis['average_orders_per_customer'] / months

    # Repeat purchase rate
    if 'order_id' in df.columns:
        customers_with_multiple_orders = df.groupby('customer_id')['order_id'].nunique()
        repeat_customers = customers_with_multiple_orders[customers_with_multiple_orders > 1]
        if len(customers_with_multiple_orders) > 0:
            kpis['repeat_purchase_rate'] = len(repeat_customers) / len(customers_with_multiple_orders)
        else:
            kpis['repeat_purchase_rate'] = 0

    # Customer segmentation distribution
    if 'customer_segment' in df.columns:
        segment_dist = df['customer_segment'].value_counts(normalize=True)
        kpis['customer_segment_distribution'] = segment_dist.to_dict()

    return kpis

def calculate_product_kpis(df: pd.DataFrame) -> dict:
    """
    Calculate product-related KPIs.

    Args:
        df: DataFrame with sales data

    Returns:
        Dictionary of product KPIs
    """
    kpis = {}

    # Total products sold
    kpis['total_units_sold'] = df['quantity'].sum()

    # Number of unique products
    kpis['unique_products_sold'] = df['product_id'].nunique()

    # Top selling products by quantity
    if 'product_id' in df.columns and 'product_category_name_english' in df.columns:
        top_by_quantity = df.groupby(['product_id', 'product_category_name_english'])['quantity'].sum().sort_values(ascending=False)
        kpis['top_5_products_by_quantity'] = top_by_quantity.head(5).to_dict()

    # Top selling products by revenue
        top_by_revenue = df.groupby(['product_id', 'product_category_name_english'])['total_price'].sum().sort_values(ascending=False)
        kpis['top_5_products_by_revenue'] = top_by_revenue.head(5).to_dict()

    # Average units per transaction
    kpis['average_units_per_transaction'] = df['quantity'].mean()

    # Product return rate
    if 'return_id' in df.columns:
        total_transactions = df['sales_id'].nunique()
        returned_transactions = df['return_id'].notna().sum()
        if total_transactions > 0:
            kpis['product_return_rate'] = returned_transactions / total_transactions
        else:
            kpis['product_return_rate'] = 0

    # Inventory turnover (simplified - requires inventory data)
    # This would need inventory facts, but we can approximate with sales velocity
    if 'date' in df.columns:
        date_range = df['date'].max() - df['date'].min()
        days = max(date_range.days, 1)
        kpis['average_daily_units_sold'] = df['quantity'].sum() / days

    return kpis

def calculate_marketing_kpis(df: pd.DataFrame) -> dict:
    """
    Calculate marketing-related KPIs.

    Args:
        df: DataFrame with sales data

    Returns:
        Dictionary of marketing KPIs
    """
    kpis = {}

    # Marketing-attributed revenue
    if 'marketing_id' in df.columns and 'revenue_attributed' not in df.columns:
        # In a real scenario, we would have revenue_attributed in the fact table
        # For now, we'll estimate based on marketing_id presence
        marketing_sales = df[df['marketing_id'].notna()]
        kpis['marketing_attributed_sales_count'] = len(marketing_sales)
        kpis['marketing_attributed_revenue'] = marketing_sales['total_price'].sum()
        total_revenue = df['total_price'].sum()
        if total_revenue > 0:
            kpis['marketing_revenue_percentage'] = kpis['marketing_attributed_revenue'] / total_revenue
        else:
            kpis['marketing_revenue_percentage'] = 0

    # Marketing channel performance
    if 'channel' in df.columns and df['channel'].notna().any():
        channel_performance = df.groupby('channel').agg({
            'total_price': 'sum',
            'sales_id': 'nunique',
            'profit': 'sum'
        }).reset_index()
        channel_performance['revenue_per_sale'] = channel_performance['total_price'] / channel_performance['sales_id']
        kpis['channel_performance'] = channel_performance.set_index('channel').to_dict('index')

    # Campaign performance
    if 'campaign_name' in df.columns and df['campaign_name'].notna().any():
        campaign_performance = df.groupby('campaign_name').agg({
            'total_price': 'sum',
            'sales_id': 'nunique'
        }).reset_index()
        campaign_performance['revenue_per_sale'] = campaign_performance['total_price'] / campaign_performance['sales_id']
        kpis['campaign_performance'] = campaign_performance.set_index('campaign_name').to_dict('index')

    return kpis

def calculate_operational_kpis(df: pd.DataFrame) -> dict:
    """
    Calculate operational-related KPIs.

    Args:
        df: DataFrame with sales data

    Returns:
        Dictionary of operational KPIs
    """
    kpis = {}

    # Order status distribution
    if 'order_status' in df.columns:
        order_status_dist = df['order_status'].value_counts(normalize=True)
        kpis['order_status_distribution'] = order_status_dist.to_dict()

    # Shipping costs
    if 'freight_value' in df.columns:
        kpis['average_shipping_cost_per_order'] = df.groupby('order_id')['freight_value'].sum().mean()
        kpis['total_shipping_cost'] = df['freight_value'].sum()
        total_revenue = df['total_price'].sum()
        if total_revenue > 0:
            kpis['shipping_cost_as_percentage_of_revenue'] = kpis['total_shipping_cost'] / total_revenue
        else:
            kpis['shipping_cost_as_percentage_of_revenue'] = 0

    # Payment method distribution
    if 'payment_type' in df.columns:
        payment_dist = df['payment_type'].value_counts(normalize=True)
        kpis['payment_method_distribution'] = payment_dist.to_dict()

    # Return analysis
    if 'return_reason' in df.columns and df['return_reason'].notna().any():
        return_reasons = df[df['return_reason'].notna()]['return_reason'].value_counts()
        kpis['top_return_reasons'] = return_reasons.head(5).to_dict()

    return kpis

def calculate_all_kpis(df: Optional[pd.DataFrame] = None,
                      conn: Optional[sqlite3.Connection] = None) -> dict:
    """
    Calculate all KPIs and return them in a structured format.

    Args:
        df: Optional DataFrame with sales data. If None, will load from database.
        conn: Optional SQLite connection. If None, will create a new connection.

    Returns:
        Dictionary containing all KPIs organized by category
    """
    # Manage database connection
    conn_provided = conn is not None
    if conn is None:
        conn = get_db_connection()

    try:
        # Load data if not provided
        if df is None:
            df = load_kpi_data(conn)
            logger.info(f"Loaded {len(df)} sales records for KPI calculation")

        if len(df) == 0:
            logger.warning("No data available for KPI calculation")
            return {}

        # Calculate KPIs by category
        revenue_kpis = calculate_revenue_kpis(df)
        profitability_kpis = calculate_profitability_kpis(df)
        customer_kpis = calculate_customer_kpis(df)
        product_kpis = calculate_product_kpis(df)
        marketing_kpis = calculate_marketing_kpis(df)
        operational_kpis = calculate_operational_kpis(df)

        # Combine all KPIs
        all_kpis = {
            'revenue': revenue_kpis,
            'profitability': profitability_kpis,
            'customer': customer_kpis,
            'product': product_kpis,
            'marketing': marketing_kpis,
            'operational': operational_kpis,
            'calculation_timestamp': datetime.now().isoformat(),
            'data_period': {
                'start_date': df['date'].min().isoformat() if 'date' in df.columns and len(df) > 0 else None,
                'end_date': df['date'].max().isoformat() if 'date' in df.columns and len(df) > 0 else None,
                'total_records': len(df)
            }
        }

        logger.info("KPI calculation completed successfully")
        return all_kpis

    except Exception as e:
        logger.error(f"Error calculating KPIs: {str(e)}")
        raise
    finally:
        # Close connection if we created it
        if not conn_provided:
            conn.close()

def format_kpi_results(kpis: dict) -> str:
    """
    Format KPI results into a readable string.

    Args:
        kpis: Dictionary of KPIs from calculate_all_kpis()

    Returns:
        Formatted string with KPI results
    """
    if not kpis:
        return "No KPI data available."

    output = []
    output.append("KPI CALCULATION REPORT")
    output.append("=" * 50)
    output.append(f"Calculation Time: {kpis.get('calculation_timestamp', 'N/A')}")
    output.append("")

    # Data period info
    period_info = kpis.get('data_period', {})
    if period_info.get('start_date') and period_info.get('end_date'):
        output.append(f"Data Period: {period_info['start_date']} to {period_info['end_date']}")
        output.append(f"Total Records: {period_info.get('total_records', 0)}")
    output.append("")

    # Revenue KPIs
    output.append("REVENUE KPIs:")
    output.append("-" * 30)
    revenue = kpis.get('revenue', {})
    for kpi, value in revenue.items():
        if isinstance(value, float):
            if 'growth' in kpi or 'margin' in kpi or 'rate' in kpi:
                output.append(f"{kpi}: {value:.2%}")
            elif 'revenue' in kpi:
                output.append(f"{kpi}: ${value:,.2f}")
            else:
                output.append(f"{kpi}: {value:,.2f}")
        else:
            output.append(f"{kpi}: {value}")
    output.append("")

    # Profitability KPIs
    output.append("PROFITABILITY KPIs:")
    output.append("-" * 30)
    profit = kpis.get('profitability', {})
    for kpi, value in profit.items():
        if isinstance(value, float):
            if 'margin' in kpi or 'growth' in kpi:
                output.append(f"{kpi}: {value:.2%}")
            elif 'profit' in kpi:
                output.append(f"{kpi}: ${value:,.2f}")
            else:
                output.append(f"{kpi}: {value:,.2f}")
        else:
            output.append(f"{kpi}: {value}")
    output.append("")

    # Customer KPIs
    output.append("CUSTOMER KPIs:")
    output.append("-" * 30)
    customer = kpis.get('customer', {})
    for kpi, value in customer.items():
        if isinstance(value, float):
            if 'rate' in kpi or 'frequency' in kpi:
                output.append(f"{kpi}: {value:.2%}")
            elif 'value' in kpi or 'value' in kpi:
                output.append(f"{kpi}: ${value:,.2f}")
            else:
                output.append(f"{kpi}: {value:,.2f}")
        else:
            output.append(f"{kpi}: {value}")
    output.append("")

    # Product KPIs
    output.append("PRODUCT KPIs:")
    output.append("-" * 30)
    product = kpis.get('product', {})
    for kpi, value in product.items():
        if isinstance(value, float):
            if 'rate' in kpi:
                output.append(f"{kpi}: {value:.2%}")
            elif 'value' in kpi or 'cost' in kpi:
                output.append(f"{kpi}: ${value:,.2f}")
            else:
                output.append(f"{kpi}: {value:,.2f}")
        else:
            output.append(f"{kpi}: {value}")
    output.append("")

    # Marketing KPIs
    output.append("MARKETING KPIs:")
    output.append("-" * 30)
    marketing = kpis.get('marketing', {})
    for kpi, value in marketing.items():
        if isinstance(value, float):
            if 'rate' in kpi or 'percentage' in kpi:
                output.append(f"{kpi}: {value:.2%}")
            elif 'revenue' in kpi or 'sales' in kpi:
                output.append(f"{kpi}: ${value:,.2f}")
            else:
                output.append(f"{kpi}: {value:,.2f}")
        else:
            output.append(f"{kpi}: {value}")
    output.append("")

    # Operational KPIs
    output.append("OPERATIONAL KPIs:")
    output.append("-" * 30)
    operational = kpis.get('operational', {})
    for kpi, value in operational.items():
        if isinstance(value, float):
            if 'rate' in kpi or 'percentage' in kpi:
                output.append(f"{kpi}: {value:.2%}")
            elif 'cost' in kpi:
                output.append(f"{kpi}: ${value:,.2f}")
            else:
                output.append(f"{kpi}: {value:,.2f}")
        else:
            output.append(f"{kpi}: {value}")
    output.append("")

    return "\n".join(output)

if __name__ == "__main__":
    # When run directly, calculate and print KPIs
    try:
        kpis = calculate_all_kpis()
        print("\nKPI Calculation Complete!")
        if kpis:
            print(f"Data Period: {kpis.get('data_period', {}).get('start_date', 'N/A')} to {kpis.get('data_period', {}).get('end_date', 'N/A')}")
            print(f"Total Records: {kpis.get('data_period', {}).get('total_records', 0)}")

            # Print formatted results
            print("\n" + format_kpi_results(kpis))
        else:
            print("No KPI data available.")

    except Exception as e:
        print(f"Error calculating KPIs: {e}")
        exit(1)
