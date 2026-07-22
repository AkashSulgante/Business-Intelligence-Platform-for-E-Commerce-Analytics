"""
Data extraction module for the E-commerce BI pipeline.
Handles downloading and loading raw data from various sources.
"""

import os
import sys
import logging
import requests
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from .utils import setup_logging, get_db_connection, load_csv_to_dataframe, save_dataframe_to_csv, get_project_root
except ImportError:  # pragma: no cover - allows running as python etl/extract.py
    from etl.utils import setup_logging, get_db_connection, load_csv_to_dataframe, save_dataframe_to_csv, get_project_root

# Initialize logger
logger = setup_logging()

# Constants
DATA_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail%20II.xlsx"
RAW_DATA_DIR = get_project_root() / "data" / "raw"
EXPECTED_FILES = {
    "online_retail_ii": "online_retail_ii.xlsx"
}

def download_file(url: str, destination: Path) -> bool:
    """
    Download a file from a URL with progress reporting.

    Args:
        url: URL to download from
        destination: Path where to save the file

    Returns:
        True if download successful, False otherwise
    """
    try:
        # Ensure directory exists
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Send HTTP request
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()  # Raise exception for bad status codes

        # Get total file size if available
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte
        downloaded = 0

        # Write file in chunks
        with open(destination, 'wb') as file:
            for data in response.iter_content(block_size):
                downloaded += len(data)
                file.write(data)
                # Progress indicator (every 1MB)
                if total_size > 0 and downloaded % (1024 * 1024) < block_size:
                    percent = (downloaded / total_size) * 100
                    logger.info(f"Download progress: {percent:.1f}% ({downloaded}/{total_size} bytes)")

        logger.info(f"Download completed: {destination}")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download file from {url}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during download: {str(e)}")
        return False

def extract_online_retail_ii() -> pd.DataFrame:
    """
    Extract the Online Retail II dataset from the UCI repository or fall back to the
    local Olist CSV files included in the workspace.

    Returns:
        pandas DataFrame containing the raw data
    """
    file_name = EXPECTED_FILES["online_retail_ii"]
    file_path = RAW_DATA_DIR / file_name

    # Check if a local Excel file already exists
    if file_path.exists():
        logger.info(f"File already exists: {file_path}")
        try:
            df = pd.read_excel(file_path, sheet_name=None)
            if isinstance(df, dict):
                if len(df) == 1:
                    df = list(df.values())[0]
                else:
                    dfs = []
                    for sheet_name, sheet_df in df.items():
                        sheet_df['_source_sheet'] = sheet_name
                        dfs.append(sheet_df)
                    df = pd.concat(dfs, ignore_index=True)
            logger.info(f"Loaded existing file with shape: {df.shape}")
            return df
        except Exception as e:
            logger.warning(f"Could not read existing file, trying local fallback data: {str(e)}")

    # Try the remote download first
    logger.info(f"Downloading Online Retail II dataset from {DATA_URL}")
    success = download_file(DATA_URL, file_path)

    if success:
        try:
            logger.info(f"Loading Excel file: {file_path}")
            excel_data = pd.read_excel(file_path, sheet_name=None)
            if isinstance(excel_data, dict):
                expected_sheets = ['Year 2009-2010', 'Year 2010-2011']
                sheets_to_use = [sheet for sheet in expected_sheets if sheet in excel_data]
                if not sheets_to_use:
                    sheets_to_use = list(excel_data.keys())
                dfs = []
                for sheet_name in sheets_to_use:
                    df_sheet = excel_data[sheet_name]
                    df_sheet['_source_sheet'] = sheet_name
                    dfs.append(df_sheet)
                df = pd.concat(dfs, ignore_index=True)
            else:
                df = excel_data
            logger.info(f"Successfully loaded data with shape: {df.shape}")
            logger.info(f"Columns: {list(df.columns)}")
            return df
        except Exception as e:
            logger.warning(f"Could not read downloaded Excel file, using local fallback data: {str(e)}")

    # Fallback to the local Olist CSV files shipped with the project.
    local_files = [
        RAW_DATA_DIR / "olist_orders_dataset.csv",
        RAW_DATA_DIR / "olist_order_items_dataset.csv",
        RAW_DATA_DIR / "olist_customers_dataset.csv",
        RAW_DATA_DIR / "olist_products_dataset.csv",
    ]
    if all(path.exists() for path in local_files):
        logger.info("Using bundled local Olist CSV data as fallback")
        orders = pd.read_csv(local_files[0])
        items = pd.read_csv(local_files[1])
        customers = pd.read_csv(local_files[2])
        products = pd.read_csv(local_files[3])

        merged = orders.merge(items, on='order_id', how='left')
        merged = merged.merge(customers[['customer_id', 'customer_unique_id', 'customer_city', 'customer_state']], on='customer_id', how='left')
        merged = merged.merge(products[['product_id', 'product_name_lenght', 'product_description_lenght', 'product_photos_qty']], on='product_id', how='left')

        merged['invoice'] = merged['order_id'].astype(str)
        merged['invoice_date'] = pd.to_datetime(merged['order_purchase_timestamp'], errors='coerce')
        merged['quantity'] = 1
        merged['unit_price'] = pd.to_numeric(merged['price'], errors='coerce').fillna(0)
        merged['stock_code'] = merged['product_id'].astype(str)
        merged['description'] = merged['product_id'].astype(str)
        merged['country'] = merged.get('customer_state', 'Unknown').fillna('Unknown')
        logger.info(f"Loaded local fallback data with shape: {merged.shape}")
        return merged

    raise Exception(f"Failed to download dataset from {DATA_URL} and no local fallback data is available")

def extract_all() -> Dict[str, pd.DataFrame]:
    """
    Extract all required datasets for the E-commerce BI pipeline.

    Returns:
        Dictionary mapping dataset names to DataFrames
    """
    logger.info("Starting data extraction process")

    datasets = {}

    # Extract Online Retail II dataset
    try:
        df_retail = extract_online_retail_ii()
        datasets['online_retail_ii'] = df_retail
        logger.info("Online Retail II extraction completed successfully")
    except Exception as e:
        logger.error(f"Failed to extract Online Retail II dataset: {str(e)}")
        raise

    logger.info("Data extraction completed")
    return datasets

def save_raw_data(df: pd.DataFrame, dataset_name: str) -> None:
    """
    Save raw data to the raw data directory.

    Args:
        df: DataFrame to save
        dataset_name: Name of the dataset (used for filename)
    """
    file_path = RAW_DATA_DIR / f"{dataset_name}.csv"
    save_dataframe_to_csv(df, file_path)
    logger.info(f"Saved raw data to {file_path}")

if __name__ == "__main__":
    # When run directly, extract and save raw data
    try:
        datasets = extract_all()
        for name, df in datasets.items():
            save_raw_data(df, name)
        print("Extraction completed successfully")
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}")
        sys.exit(1)