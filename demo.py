#!/usr/bin/env python3
"""
Demo script to run the ETL pipeline with sample data.
This creates sample data and runs the complete ETL process.
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from etl.extract import extract_all
from etl.transform import transform_data
from etl.load import load_data, verify_data_load
from etl.pipeline import run_pipeline
from etl.utils import setup_logging, get_project_root

def create_sample_data():
    """Create sample data for demonstration."""
    # Create data directories
    project_root = get_project_root()
    raw_dir = project_root / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Create sample CSV data (similar to Online Retail II)
    sample_data = """InvoiceNo,StockCode,Description,Quantity,InvoiceDate,UnitPrice,CustomerID,Country
536365,85123A,WHITE HANGING HEART T-LIGHT HOLDER,6,12/1/2010 8:26,2.55,17850,United Kingdom
536365,71053,WHITE METAL LANTERN,6,12/1/2010 8:26,3.39,17850,United Kingdom
536365,84406B,CREAM CUPID HEARTS COAT HANGER,8,12/1/2010 8:26,2.75,17850,United Kingdom
536365,84029G,KNITTED UNION FLAG HOT WATER BOTTLE,6,12/1/2010 8:26,3.39,17850,United Kingdom
536365,84029E,RED WOOLLY HOTTIE WHITE HAT.,6,12/1/2010 8:26,3.39,17850,United Kingdom
536366,22492,REGENCY CAKESTAND 3 TIER,8,12/1/2010 8:28,2.55,17850,United Kingdom
536366,22493,REGENCY CAKESTAND TIER,4,12/1/2010 8:28,3.39,17850,United Kingdom
536366,22494,RETROSPOT TEAPOT,1,12/1/2010 8:28,2.75,17850,United Kingdom
536366,22495,RETROSPOT MILK JUG,1,12/1/2010 8:28,2.75,17850,United Kingdom
536366,22496,RETROSPOT SUGAR BOX,1,12/1/2010 8:28,2.75,17850,United Kingdom
536367,85099B,SET OF 3 CAKE TINS PANTRY DESIGN,2,12/1/2010 8:34,3.29,17850,United Kingdom
536367,22693,ROSES REGENCY TEACUP AND SAUCER,6,12/1/2010 8:34,3.39,17850,United Kingdom
536367,22694,ROSES REGENCY TEACUP ONLY,6,12/1/2010 8:34,2.75,17850,United Kingdom
536367,22695,ROSES REGENCY SAUCER,6,1,6,12/1/2010 8:34,2.75,17850,United Kingdom
536368,22745,SET OF 36 TWISTTAGS PLASTIC,1,12/1/2010 8:34,1.25,17850,United Kingdom
536368,22746,SET OF 144 TWISTTAGS PAPER,1,12/1/2010 8:34,1.25,17850,United Kingdom
536368,22747,EXTRA STRONG MAGNETS,1,12/1/2010 8:34,0.65,17850,United Kingdom
536368,22748,PEBBLES,1,12/1/2010 8:34,0.69,17850,United Kingdom
536368,22749,KNITTED UNION FLAG WOOL,1,12/1/2010 8:34,1.65,17850,United Kingdom
536369,12003G,GREEN REGENCY TEACUP AND SAUCER,2,12/1/2010 8:38,2.75,17850,United Kingdom
536369,12003H,GREEN REGENCY TEACUP ONLY,2,12/1/2010 8:38,1.50,17850,United Kingdom
536369,12003I,GREEN REGENCY SAUCER,2,12/1/2010 8:38,1.25,17850,United Kingdom
536370,22752,PARTY BUNTING,2,12/1/2010 8:40,1.85,17850,United Kingdom
536370,22753,ROUND SNACK BOXES SET OF4,4,12/1/2010 8:40,2.32,17850,United Kingdom
"""

    # Save sample data
    sample_file = raw_dir / "online_retail_ii.csv"
    with open(sample_file, 'w') as f:
        f.write(sample_data)

    print(f"Sample data created at: {sample_file}")
    return sample_file

def main():
    """Run the ETL pipeline with sample data."""
    print("=" * 60)
    print("E-COMMERCE BI PLATFORM - ETL PIPELINE DEMO")
    print("=" * 60)

    # Setup logging
    logger = setup_logging("INFO")
    logger.info("Starting ETL pipeline demo")

    # Create sample data
    print("\n1. Creating sample data...")
    sample_file = create_sample_data()

    # Run the ETL pipeline
    print("\n2. Running ETL pipeline...")
    try:
        success = run_pipeline()

        if success:
            print("\n3. ETL pipeline completed successfully!")

            # Verify the data was loaded
            from etl.load import verify_data_load
            db_path = get_project_root() / "data" / "warehouse" / "ecommerce_bi.db"
            if verify_data_load(db_path):
                print("4. Data verification passed!")
            else:
                print("4. Data verification completed with warnings.")

            print("\n5. Next steps:")
            print("   - Run analysis modules: python -m analysis.customer_segmentation")
            print("   - Generate weekly report: python reports/weekly_report_generator.py")
            print("   - Explore the generated data in the data/warehouse/ecommerce_bi.db database")

        else:
            print("\n3. ETL pipeline failed!")
            return 1

    except Exception as e:
        print(f"\n3. ETL pipeline failed with error: {e}")
        return 1

    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())