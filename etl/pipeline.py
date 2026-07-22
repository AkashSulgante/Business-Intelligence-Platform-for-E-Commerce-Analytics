"""
Main ETL pipeline for the E-commerce Business Intelligence platform.
Orchestrates the extraction, transformation, and loading processes.
"""

import sys
import logging
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from .extract import extract_all, save_raw_data
    from .transform import transform_data
    from .load import load_data, verify_data_load
    from .utils import setup_logging, get_project_root
except ImportError:  # pragma: no cover - allows running as python etl/pipeline.py
    from etl.extract import extract_all, save_raw_data
    from etl.transform import transform_data
    from etl.load import load_data, verify_data_load
    from etl.utils import setup_logging, get_project_root

# Initialize logger
logger = setup_logging()

def run_pipeline() -> bool:
    """
    Execute the complete ETL pipeline.

    Returns:
        True if pipeline completed successfully, False otherwise
    """
    logger.info("=" * 50)
    logger.info("Starting E-Commerce BI ETL Pipeline")
    logger.info("=" * 50)

    try:
        # Step 1: Extract
        logger.info("Step 1: Data Extraction")
        raw_data = extract_all()

        # Save raw data for audit
        logger.info("Saving raw data to disk")
        for name, df in raw_data.items():
            save_raw_data(df, name)
            logger.info(f"Saved raw dataset '{name}' with shape {df.shape}")

        # Step 2: Transform
        logger.info("Step 2: Data Transformation")
        transformed_data = transform_data(raw_data)
        logger.info("Transformation completed")

        # Optional: Save processed data for inspection
        processed_dir = get_project_root() / "data" / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Saving processed data to {processed_dir}")

        # Save cleaned data
        save_raw_data(transformed_data['cleaned_data'], "cleaned_data")
        # Save dimensions
        for dim_name, df in transformed_data['dimensions'].items():
            save_raw_data(df, f"dim_{dim_name}")
        # Save fact table
        save_raw_data(transformed_data['fact_table'], "fact_sales")

        # Step 3: Load
        logger.info("Step 3: Data Loading")
        db_path = get_project_root() / "data" / "warehouse" / "ecommerce_bi.db"
        load_data(transformed_data, db_path)

        # Step 4: Verify
        logger.info("Step 4: Verification")
        if verify_data_load(db_path):
            logger.info("Data verification passed")
        else:
            logger.warning("Data verification completed with warnings")

        logger.info("=" * 50)
        logger.info("ETL Pipeline completed successfully!")
        logger.info("=" * 50)
        return True

    except Exception as e:
        logger.error(f"ETL Pipeline failed: {str(e)}")
        logger.exception("Full traceback:")
        return False

def run_extract_only() -> bool:
    """
    Run only the extraction phase.

    Returns:
        True if extraction completed successfully, False otherwise
    """
    logger.info("Running extraction only")
    try:
        raw_data = extract_all()
        for name, df in raw_data.items():
            save_raw_data(df, name)
        logger.info("Extraction completed successfully")
        return True
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}")
        return False

def run_transform_only() -> bool:
    """
    Run only the transformation phase (requires extracted data).

    Returns:
        True if transformation completed successfully, False otherwise
    """
    logger.info("Running transformation only")
    try:
        # Load raw data from files
        raw_data = {}
        raw_dir = get_project_root() / "data" / "raw"
        for file_path in raw_dir.glob("*.csv"):
            # Assuming files were saved as CSV by extract step
            name = file_path.stem
            df = pd.read_csv(file_path)
            raw_data[name] = df

        if not raw_data:
            # Try to extract if no files found
            logger.warning("No raw data files found, running extraction first")
            raw_data = extract_all()
            for name, df in raw_data.items():
                save_raw_data(df, name)

        transformed_data = transform_data(raw_data)
        # Save processed data
        processed_dir = get_project_root() / "data" / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)
        save_raw_data(transformed_data['cleaned_data'], "cleaned_data")
        for dim_name, df in transformed_data['dimensions'].items():
            save_raw_data(df, f"dim_{dim_name}")
        save_raw_data(transformed_data['fact_table'], "fact_sales")
        logger.info("Transformation completed successfully")
        return True
    except Exception as e:
        logger.error(f"Transformation failed: {str(e)}")
        return False

def run_load_only() -> bool:
    """
    Run only the loading phase (requires transformed data).

    Returns:
        True if loading completed successfully, False otherwise
    """
    logger.info("Running loading only")
    try:
        # Load processed data from files
        processed_dir = get_project_root() / "data" / "processed"
        if not processed_dir.exists():
            raise FileNotFoundError(f"Processed data directory not found: {processed_dir}")

        # Load cleaned data
        cleaned_data = pd.read_csv(processed_dir / "cleaned_data.csv")

        # Load dimensions
        dimensions = {}
        for dim_file in processed_dir.glob("dim_*.csv"):
            dim_name = dim_file.stem.replace("dim_", "")
            dimensions[dim_name] = pd.read_csv(dim_file)

        # Load fact table
        fact_table = pd.read_csv(processed_dir / "fact_sales.csv")

        transformed_data = {
            'cleaned_data': cleaned_data,
            'dimensions': dimensions,
            'fact_table': fact_table
        }

        # Load to database
        db_path = get_project_root() / "data" / "warehouse" / "ecommerce_bi.db"
        load_data(transformed_data, db_path)

        # Verify
        if verify_data_load(db_path):
            logger.info("Load verification passed")
        else:
            logger.warning("Load verification completed with warnings")

        logger.info("Loading completed successfully")
        return True
    except Exception as e:
        logger.error(f"Loading failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Allow running specific stages via command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "extract":
            success = run_extract_only()
        elif mode == "transform":
            success = run_transform_only()
        elif mode == "load":
            success = run_load_only()
        elif mode == "verify":
            db_path = get_project_root() / "data" / "warehouse" / "ecommerce_bi.db"
            success = verify_data_load(db_path)
        else:
            logger.error(f"Unknown mode: {mode}. Use: extract, transform, load, or verify")
            success = False
    else:
        # Run full pipeline
        success = run_pipeline()

    sys.exit(0 if success else 1)