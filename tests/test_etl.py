"""
Unit tests for the ETL pipeline components.
"""

import os
import sys
import tempfile
import unittest
import pandas as pd
import numpy as np
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from etl.utils import setup_logging, get_db_connection, clean_column_names, handle_missing_values, remove_duplicates
from etl.extract import extract_all
from etl.transform import transform_data
from etl.load import load_data, verify_data_load
from etl.pipeline import run_pipeline

class TestETLUtils(unittest.TestCase):
    """Test cases for ETL utility functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_df = pd.DataFrame({
            'Customer ID': [1, 2, 2, 3, 4],
            'Order Date': ['2023-01-01', '2023-01-02', '2023-01-02', '2023-01-03', '2023-01-04'],
            'Amount': [100.0, 50.0, 50.0, 75.0, None],
            'Product': ['A', 'B', 'B', 'C', 'D']
        })

    def test_clean_column_names(self):
        """Test column name cleaning function."""
        cleaned_df = clean_column_names(self.test_df)
        expected_columns = ['customer_id', 'order_date', 'amount', 'product']
        self.assertListEqual(list(cleaned_df.columns), expected_columns)

    def test_handle_missing_values(self):
        """Test missing value handling."""
        # Test with mean strategy
        df_filled = handle_missing_values(self.test_df.copy(), strategy='mean')
        # The amount column should have the missing value filled with mean of [100, 50, 50, 75] = 68.75
        self.assertEqual(df_filled.iloc[4]['Amount'], 68.75)

        # Test with drop strategy
        df_dropped = handle_missing_values(self.test_df.copy(), strategy='drop')
        self.assertEqual(len(df_dropped), 4)  # One row dropped

    def test_remove_duplicates(self):
        """Test duplicate removal."""
        df_no_dup = remove_duplicates(self.test_df.copy(), subset=['Customer ID', 'Order Date'])
        # Should remove the duplicate row for customer 2 on 2023-01-02
        self.assertEqual(len(df_no_dup), 4)

class TestETLPipeline(unittest.TestCase):
    """Test cases for the ETL pipeline."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test data
        self.temp_dir = Path(tempfile.mkdtemp())
        self.data_dir = self.temp_dir / "data"
        self.data_dir.mkdir()
        (self.data_dir / "raw").mkdir()
        (self.data_dir / "processed").mkdir()
        (self.data_dir / "warehouse").mkdir()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_extract_create_sample_data(self):
        """Test that we can create sample data for extraction."""
        # Create a simple CSV file for testing
        sample_data = """InvoiceNo,StockCode,Description,Quantity,InvoiceDate,UnitPrice,CustomerID,Country
536365,85123A,WHITE HANGING HEART T-LIGHT HOLDER,6,12/1/2010 8:26,2.55,17850,United Kingdom
536365,71053,WHITE METAL LANTERN,6,12/1/2010 8:26,3.39,17850,United Kingdom
536365,84406B,CREAM CUPID HEARTS COAT HANGER,8,12/1/2010 8:26,2.75,17850,United Kingdom
536365,84029G,KNITTED UNION FLAG HOT WATER BOTTLE,6,12/1/2010 8:26,3.39,17850,United Kingdom
536365,84029E,RED WOOLLY HOTTIE WHITE HAT.,6,12/1/2010 8:26,3.39,17850,United Kingdom"""

        sample_file = self.data_dir / "raw" / "online_retail_ii.csv"
        with open(sample_file, 'w') as f:
            f.write(sample_data)

        # Verify file was created
        self.assertTrue(sample_file.exists())

    def test_database_creation(self):
        """Test database connection and basic operations."""
        db_path = self.data_dir / "warehouse" / "test.db"
        conn = get_db_connection(db_path)

        # Create a simple table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            name TEXT,
            value REAL
        )
        """)

        # Insert test data
        conn.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ("test", 100.0))
        conn.commit()

        # Query the data
        result = conn.execute("SELECT * FROM test_table").fetchall()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "test")
        self.assertEqual(result[0][2], 100.0)

        conn.close()

if __name__ == '__main__':
    unittest.main()