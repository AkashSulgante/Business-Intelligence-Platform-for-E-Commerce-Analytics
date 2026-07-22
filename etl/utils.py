"""
Utility functions for the ETL pipeline.
Contains helper functions for logging, database connections, and common operations.
"""

import os
import sys
import logging
import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
WAREHOUSE_DIR = DATA_DIR / "warehouse"


def get_project_root() -> Path:
    """Return the project root directory for the ETL package."""
    return PROJECT_ROOT


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / f"etl_{datetime.now().strftime('%Y%m%d')}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger("etl_pipeline")
    return logger

def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Create a connection to the SQLite data warehouse.

    Args:
        db_path: Path to the SQLite database file. If None, uses default path.

    Returns:
        SQLite connection object
    """
    if db_path is None:
        db_path = WAREHOUSE_DIR / "ecommerce_warehouse.db"

    # Ensure the directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Create connection
    conn = sqlite3.connect(db_path)
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def execute_sql_script(conn: sqlite3.Connection, sql_file_path: str) -> None:
    """
    Execute a SQL script file against the database.

    Args:
        conn: SQLite connection object
        sql_file_path: Path to the SQL script file
    """
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    cursor = conn.cursor()
    # Split by semicolon and execute each statement
    statements = sql_script.split(';')
    for statement in statements:
        statement = statement.strip()
        if statement:
            try:
                cursor.execute(statement)
            except sqlite3.Error as e:
                # Some statements might fail (like DROP IF EXISTS on non-existent tables)
                # but we continue with the rest
                pass
    conn.commit()

def load_csv_to_dataframe(file_path: str, **kwargs) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame with error handling.

    Args:
        file_path: Path to the CSV file
        **kwargs: Additional arguments to pass to pd.read_csv

    Returns:
        pandas DataFrame
    """
    try:
        df = pd.read_csv(file_path, **kwargs)
        return df
    except Exception as e:
        raise Exception(f"Error loading CSV file {file_path}: {str(e)}")

def save_dataframe_to_csv(df: pd.DataFrame, file_path: str, index: bool = False) -> None:
    """
    Save a pandas DataFrame to a CSV file.

    Args:
        df: DataFrame to save
        file_path: Path where to save the CSV
        index: Whether to include the index column
    """
    # Ensure directory exists
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)

    try:
        df.to_csv(file_path, index=index)
    except Exception as e:
        raise Exception(f"Error saving DataFrame to CSV {file_path}: {str(e)}")

def validate_dataframe(df: pd.DataFrame, required_columns: list) -> bool:
    """
    Validate that a DataFrame contains all required columns.

    Args:
        df: DataFrame to validate
        required_columns: List of column names that must be present

    Returns:
        True if valid, False otherwise
    """
    if df is None or df.empty:
        return False

    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    return True

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean column names by converting to lowercase and replacing spaces with underscores.

    Args:
        df: DataFrame with column names to clean

    Returns:
        DataFrame with cleaned column names
    """
    df_copy = df.copy()
    df_copy.columns = [
        col.strip().lower().replace(' ', '_').replace('-', '_')
        for col in df_copy.columns
    ]
    return df_copy

def handle_missing_values(df: pd.DataFrame, strategy: str = 'mean') -> pd.DataFrame:
    """
    Handle missing values in a DataFrame.

    Args:
        df: DataFrame to process
        strategy: Strategy for filling missing values ('mean', 'median', 'mode', 'drop')

    Returns:
        DataFrame with missing values handled
    """
    df_copy = df.copy()

    if strategy == 'drop':
        return df_copy.dropna()

    numeric_columns = df_copy.select_dtypes(include=['number']).columns
    categorical_columns = df_copy.select_dtypes(include=['object']).columns

    if strategy == 'mean':
        df_copy[numeric_columns] = df_copy[numeric_columns].fillna(df_copy[numeric_columns].mean())
    elif strategy == 'median':
        df_copy[numeric_columns] = df_copy[numeric_columns].fillna(df_copy[numeric_columns].median())
    elif strategy == 'mode':
        for col in numeric_columns:
            df_copy[col] = df_copy[col].fillna(df_copy[col].mode()[0] if not df_copy[col].mode().empty else 0)
        for col in categorical_columns:
            df_copy[col] = df_copy[col].fillna(df_copy[col].mode()[0] if not df_copy[col].mode().empty else '')

    return df_copy

def remove_duplicates(df: pd.DataFrame, subset: Optional[list] = None) -> pd.DataFrame:
    """
    Remove duplicate rows from a DataFrame.

    Args:
        df: DataFrame to process
        subset: List of columns to consider for identifying duplicates. If None, consider all columns.

    Returns:
        DataFrame with duplicates removed
    """
    return df.drop_duplicates(subset=subset, keep='first')

def convert_data_types(df: pd.DataFrame, type_mapping: dict) -> pd.DataFrame:
    """
    Convert column data types according to a mapping.

    Args:
        df: DataFrame to convert
        type_mapping: Dictionary mapping column names to target data types

    Returns:
        DataFrame with converted data types
    """
    df_copy = df.copy()
    for col, dtype in type_mapping.items():
        if col in df_copy.columns:
            try:
                df_copy[col] = df_copy[col].astype(dtype)
            except Exception as e:
                raise ValueError(f"Error converting column {col} to {dtype}: {str(e)}")
    return df_copy