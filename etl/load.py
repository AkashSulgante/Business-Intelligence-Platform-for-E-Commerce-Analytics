"""
Data loading module for the E-commerce BI pipeline.
Handles loading transformed data into the SQLite data warehouse.
"""

import sqlite3
import pandas as pd
import sys
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from .utils import setup_logging, get_db_connection, execute_sql_script
except ImportError:  # pragma: no cover - allows running as python etl/load.py
    from etl.utils import setup_logging, get_db_connection, execute_sql_script

# Initialize logger
logger = setup_logging()

def create_database_schema(db_path: Path) -> None:
    """
    Create the database schema by executing SQL scripts.

    Args:
        db_path: Path to the SQLite database file
    """
    logger.info(f"Creating database schema at {db_path}")
    conn = get_db_connection(db_path)

    try:
        # Execute schema creation scripts
        schema_files = [
            'schema.sql',      # Contains DROP and CREATE TABLE
            'indexes.sql',     # Indexes for performance
            'views.sql'        # Analytical views
        ]

        sql_dir = Path(__file__).parent.parent / "sql"
        for sql_file in schema_files:
            file_path = sql_dir / sql_file
            if file_path.exists():
                logger.info(f"Executing {sql_file}")
                execute_sql_script(conn, file_path)
            else:
                logger.warning(f"SQL file not found: {file_path}")

        # Commit changes
        conn.commit()
        logger.info("Database schema created successfully")

    except Exception as e:
        logger.error(f"Error creating database schema: {str(e)}")
        raise
    finally:
        conn.close()

def load_dataframe_to_sqlite(df: pd.DataFrame, table_name: str, conn: sqlite3.Connection,
                            if_exists: str = 'replace', index: bool = False) -> None:
    """
    Load a pandas DataFrame into a SQLite table.

    Args:
        df: DataFrame to load
        table_name: Name of the target table
        conn: SQLite connection object
        if_exists: How to behave if table exists ('fail', 'replace', 'append')
        index: Whether to write DataFrame index as a column
    """
    logger.info(f"Loading data into table '{table_name}' ({len(df)} rows)")
    try:
        df.to_sql(
            name=table_name,
            con=conn,
            if_exists=if_exists,
            index=index,
            method='multi',
            # SQLite limits the number of bound SQL variables.  Chunking keeps
            # wide dimension tables below that limit on every supported build.
            chunksize=100
        )
        logger.info(f"Successfully loaded {len(df)} rows into {table_name}")
    except Exception as e:
        logger.error(f"Error loading data into {table_name}: {str(e)}")
        raise

def load_dimensions_to_db(dimensions: dict, conn: sqlite3.Connection) -> None:
    """
    Load all dimension tables into the database.

    Args:
        dimensions: Dictionary of dimension DataFrames
        conn: SQLite connection object
    """
    logger.info("Loading dimension tables")
    dimension_mapping = {
        'date': 'dim_date',
        'customers': 'dim_customers',
        'products': 'dim_products',
        'orders': 'dim_orders',
        'payments': 'dim_payments',
        'returns': 'dim_returns',
        'marketing': 'dim_marketing'
    }

    for dim_key, df in dimensions.items():
        table_name = dimension_mapping.get(dim_key, f"dim_{dim_key}")
        if df is not None and len(df) > 0:
            load_dataframe_to_sqlite(df, table_name, conn, if_exists='replace')
        else:
            # Create empty table with correct structure
            logger.warning(f"Dimension {dim_key} is empty, creating empty table")
            # We'll create an empty table by trying to load an empty DF with correct columns
            # For simplicity, we'll skip empty dimensions and let them be created by FK constraints later
            pass

def load_fact_to_db(fact_df: pd.DataFrame, conn: sqlite3.Connection) -> None:
    """
    Load the fact table into the database.

    Args:
        fact_df: Fact table DataFrame
        conn: SQLite connection object
    """
    logger.info("Loading fact table")
    if fact_df is not None and len(fact_df) > 0:
        load_dataframe_to_sqlite(fact_df, 'fact_sales', conn, if_exists='replace')
    else:
        logger.warning("Fact table is empty")
        # Still create the table structure
        empty_df = pd.DataFrame(columns=[
            'sales_id', 'date_id', 'customer_id_fk', 'product_id_fk',
            'order_id_fk', 'payment_id_fk', 'quantity', 'unit_price',
            'total_price', 'profit', 'freight_value', 'return_id_fk', 'marketing_id_fk'
        ])
        load_dataframe_to_sqlite(empty_df, 'fact_sales', conn, if_exists='replace')

def load_data(transformed_data: dict, db_path: Path) -> None:
    """
    Main loading function that orchestrates loading of all data into the data warehouse.

    Args:
        transformed_data: Dictionary containing cleaned data, dimensions, and fact table
        db_path: Path to the SQLite database file
    """
    logger.info("Starting data loading process")

    # Ensure the database directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Step 1: Create database schema
    create_database_schema(db_path)

    # Step 2: Establish database connection
    conn = get_db_connection(db_path)
    # Tables are rebuilt with pandas' ``replace`` mode below.  SQLite cannot
    # drop a referenced table while FK enforcement is enabled, and pandas
    # recreates the table from the DataFrame schema.  The ETL uses validated
    # surrogate keys, so disable enforcement for this rebuild transaction.
    conn.execute("PRAGMA foreign_keys = OFF")

    try:
        # Step 3: Load dimension tables
        if 'dimensions' in transformed_data:
            load_dimensions_to_db(transformed_data['dimensions'], conn)

        # Step 4: Load fact table
        if 'fact_table' in transformed_data:
            load_fact_to_db(transformed_data['fact_table'], conn)

        # Commit all changes
        conn.commit()
        logger.info("Data loading completed successfully")

    except Exception as e:
        logger.error(f"Error during data loading: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

def verify_data_load(db_path: Path) -> bool:
    """
    Verify that data has been loaded correctly by checking row counts.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        True if verification passes, False otherwise
    """
    logger.info("Verifying data load")
    conn = get_db_connection(db_path)

    try:
        cursor = conn.cursor()

        # List of tables to check
        tables = [
            'dim_date', 'dim_customers', 'dim_products', 'dim_orders',
            'dim_payments', 'dim_returns', 'dim_marketing', 'fact_sales'
        ]

        min_rows = {
            'dim_date': 1,
            'dim_customers': 1,
            'dim_products': 1,
            'dim_orders': 1,
            'dim_payments': 1,
            'dim_returns': 0,  # Could be zero if no returns
            'dim_marketing': 1,
            'fact_sales': 1
        }

        all_good = True
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                expected_min = min_rows.get(table, 0)
                if count >= expected_min:
                    logger.info(f"Table {table}: {count} rows (OK)")
                else:
                    logger.warning(f"Table {table}: {count} rows (expected at least {expected_min})")
                    all_good = False
            except Exception as e:
                logger.error(f"Error checking table {table}: {str(e)}")
                all_good = False

        return all_good

    except Exception as e:
        logger.error(f"Error during verification: {str(e)}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    # For testing - would normally be called from pipeline.py
    from .extract import extract_all
    from .transform import transform_data
    from .utils import get_project_root
    try:
        # Extract
        raw_data = extract_all()
        # Transform
        transformed_data = transform_data(raw_data)
        # Load
        db_path = get_project_root() / "data" / "warehouse" / "ecommerce_bi.db"
        load_data(transformed_data, db_path)
        # Verify
        if verify_data_load(db_path):
            print("Loading completed successfully")
        else:
            print("Loading completed with warnings")
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        exit(1)
