"""
Unit tests for dashboard and reporting components.
"""

import os
import sys
import tempfile
import unittest
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from reports.weekly_report_generator import DataExtractor, MetricsCalculator, ChartGenerator, ReportExporter, get_date_range

class TestReportingComponents(unittest.TestCase):
    """Test cases for reporting components."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test data
        self.temp_dir = Path(tempfile.mkdtemp())
        self.data_dir = self.temp_dir / "data"
        self.data_dir.mkdir()
        (self.data_dir / "warehouse").mkdir()
        self.db_path = self.data_dir / "warehouse" / "test.db"

        # Create a simple test database
        self._create_test_database()

        # Set up output directories
        self.output_dir = self.temp_dir / "output"
        self.output_dir.mkdir()
        self.charts_dir = self.output_dir / "charts"
        self.charts_dir.mkdir()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def _create_test_database(self):
        """Create a test database with sample data."""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute("""
        CREATE TABLE dim_date (
            date_id INTEGER PRIMARY KEY,
            date DATE NOT NULL,
            day INTEGER NOT NULL,
            month INTEGER NOT NULL,
            quarter INTEGER NOT NULL,
            year INTEGER NOT NULL,
            day_of_week INTEGER NOT NULL,
            day_name VARCHAR(10) NOT NULL,
            month_name VARCHAR(10) NOT NULL,
            is_weekend BOOLEAN NOT NULL,
            is_holiday BOOLEAN DEFAULT FALSE,
            season VARCHAR(20)
        )
        """)

        cursor.execute("""
        CREATE TABLE dim_customers (
            customer_id INTEGER PRIMARY KEY,
            customer_segment VARCHAR(20)
        )
        """)

        cursor.execute("""
        CREATE TABLE dim_products (
            product_id INTEGER PRIMARY KEY,
            product_category_name_english VARCHAR(50)
        )
        """)

        cursor.execute("""
        CREATE TABLE fact_sales (
            sales_id INTEGER PRIMARY KEY,
            date_id INTEGER,
            customer_id INTEGER,
            product_id INTEGER,
            order_id INTEGER,
            quantity INTEGER,
            unit_price REAL,
            total_price REAL,
            profit REAL,
            freight_value REAL,
            payment_id INTEGER,
            return_id INTEGER,
            marketing_id INTEGER,
            FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
            FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
            FOREIGN KEY (product_id) REFERENCES dim_products(product_id)
        )
        """)

        # Insert sample date data
        dates = [
            ('2023-01-01', 1, 1, 1, 2023, 0, 'Sunday', 'January', False, False, 'Winter'),
            ('2023-01-02', 2, 2, 1, 2023, 1, 'Monday', 'January', False, False, 'Winter'),
            ('2023-01-03', 3, 3, 1, 2023, 2, 'Tuesday', 'January', False, False, 'Winter'),
            ('2023-01-04', 4, 4, 1, 2023, 3, 'Wednesday', 'January', False, False, 'Winter'),
            ('2023-01-05', 5, 5, 1, 2023, 4, 'Thursday', 'January', False, False, 'Winter'),
        ]

        for date_id, (date_str, day, month, quarter, year, day_of_week, day_name, month_name, is_weekend, is_holiday, season) in enumerate(dates, start=1):
            cursor.execute("""
            INSERT INTO dim_date (date_id, date, day, month, quarter, year, day_of_week, day_name, month_name, is_weekend, is_holiday, season)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (date_id, date_str, day, month, quarter, year, day_of_week, day_name, month_name, is_weekend, is_holiday, season))

        cursor.execute("CREATE TABLE dim_orders (order_id INTEGER PRIMARY KEY, order_status TEXT)")
        cursor.execute("CREATE TABLE dim_payments (payment_id INTEGER PRIMARY KEY, payment_type TEXT)")
        cursor.execute("CREATE TABLE dim_returns (return_id INTEGER PRIMARY KEY, return_reason TEXT)")
        cursor.execute("CREATE TABLE dim_marketing (marketing_id INTEGER PRIMARY KEY, channel TEXT, campaign_name TEXT)")

        # Insert sample customer data
        cursor.execute("INSERT INTO dim_customers (customer_id, customer_segment) VALUES (1, 'Champions')")
        cursor.execute("INSERT INTO dim_customers (customer_id, customer_segment) VALUES (2, 'Loyal Customers')")
        cursor.execute("INSERT INTO dim_customers (customer_id, customer_segment) VALUES (3, 'At Risk')")

        # Insert sample product data
        cursor.execute("INSERT INTO dim_products (product_id, product_category_name_english) VALUES (1, 'Electronics')")
        cursor.execute("INSERT INTO dim_products (product_id, product_category_name_english) VALUES (2, 'Clothing')")
        cursor.execute("INSERT INTO dim_products (product_id, product_category_name_english) VALUES (3, 'Home & Garden')")

        # Insert sample sales data
        sales_data = [
            (1, 1, 1, 1, 101, 2, 10.0, 20.0, 5.0),
            (2, 1, 1, 2, 101, 1, 15.0, 15.0, 3.0),
            (3, 2, 2, 1, 102, 1, 25.0, 25.0, 6.0),
            (4, 3, 1, 3, 103, 3, 8.0, 24.0, 4.0),
            (5, 4, 2, 1, 104, 1, 30.0, 30.0, 7.0),
            (6, 5, 3, 2, 105, 2, 12.0, 24.0, 5.0),
        ]

        for sales_id, date_id, customer_id, product_id, order_id, quantity, unit_price, total_price, profit in sales_data:
            cursor.execute("""
            INSERT INTO fact_sales (sales_id, date_id, customer_id, product_id, order_id, quantity, unit_price, total_price, profit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (sales_id, date_id, customer_id, product_id, order_id, quantity, unit_price, total_price, profit))

        conn.commit()
        conn.close()

    def test_get_date_range(self):
        """Test date range calculation."""
        start_date, end_date = get_date_range(7)

        # Check that dates are in correct format
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            self.fail("Dates are not in YYYY-MM-DD format")

        # Check that end_date is yesterday
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        self.assertEqual(end_date, yesterday)

        # Check that start_date is 6 days before end_date (for 7-day range)
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        delta = end_dt - start_dt
        self.assertEqual(delta.days, 6)  # 7 days inclusive means 6 days difference

    def test_data_extractor(self):
        """Test data extraction from the test database."""
        extractor = DataExtractor(self.db_path)

        # Test connection
        conn = extractor.connect()
        self.assertIsNotNone(conn)

        # Test query execution
        df = extractor.execute_query("SELECT COUNT(*) as count FROM fact_sales")
        self.assertEqual(df.iloc[0]['count'], 6)

        # Test weekly data extraction (using a date range that includes our sample data)
        start_date = '2023-01-01'
        end_date = '2023-01-05'
        data = extractor.get_weekly_data(start_date, end_date)

        # Check that we got data
        self.assertIn('sales', data)
        self.assertGreater(len(data['sales']), 0)
        self.assertIn('customers', data)
        self.assertGreater(len(data['customers']), 0)

        extractor.disconnect()

    def test_metrics_calculator(self):
        """Test metrics calculation."""
        calculator = MetricsCalculator()

        # Create sample data similar to what would be extracted
        sample_data = {
            'sales': pd.DataFrame({
                'total_price': [100.0, 150.0, 200.0],
                'profit': [20.0, 30.0, 40.0],
                'order_id': [101, 102, 103],
                'customer_id': [1, 2, 3],
                'quantity': [2, 3, 1]
            }),
            'customers': pd.DataFrame({
                'customer_id': [1, 2, 3],
                'customer_segment': ['Champions', 'Loyal Customers', 'At Risk'],
                'order_count': [2, 1, 1],
                'total_spent': [250.0, 150.0, 200.0]
            }),
            'daily_trends': pd.DataFrame({
                'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
                'daily_revenue': [100.0, 150.0, 200.0],
                'daily_profit': [20.0, 30.0, 40.0],
                'daily_orders': [1, 1, 1],
                'daily_customers': [1, 1, 1]
            })
        }

        # Convert date strings to datetime for daily_trends
        sample_data['daily_trends']['date'] = pd.to_datetime(sample_data['daily_trends']['date'])

        # Calculate KPIs
        kpis = calculator.calculate_kpis(sample_data)

        # Check KPIs
        self.assertEqual(kpis['total_revenue'], 450.0)
        self.assertEqual(kpis['total_profit'], 90.0)
        self.assertEqual(kpis['total_orders'], 3)
        self.assertEqual(kpis['total_customers'], 3)
        self.assertAlmostEqual(kpis['avg_order_value'], 150.0, places=2)
        self.assertAlmostEqual(kpis['profit_margin'], 0.2, places=2)  # 90/450

        # Test insights generation
        insights = calculator.generate_insights(sample_data, kpis)
        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)

    def test_chart_generator(self):
        """Test chart generation."""
        chart_gen = ChartGenerator(self.charts_dir)

        # Create sample data for charts
        daily_df = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'daily_revenue': [100.0, 150.0, 200.0],
            'daily_profit': [20.0, 30.0, 40.0]
        })
        daily_df['date'] = pd.to_datetime(daily_df['date'])

        # Test revenue trend chart
        chart_path = chart_gen.create_revenue_trend_chart(daily_df)
        self.assertTrue(os.path.exists(chart_path))
        self.assertTrue(chart_path.endswith('.png'))

        # Test profit vs revenue chart
        chart_path = chart_gen.create_profit_vs_revenue_chart(daily_df)
        self.assertTrue(os.path.exists(chart_path))

        # Test sales by category chart
        products_df = pd.DataFrame({
            'product_category_name_english': ['Electronics', 'Clothing', 'Home & Garden'],
            'revenue': [100.0, 150.0, 200.0]
        })
        chart_path = chart_gen.create_sales_by_category_chart(products_df)
        self.assertTrue(os.path.exists(chart_path))

        # Test customer segments chart
        customers_df = pd.DataFrame({
            'customer_id': [1, 2, 3],
            'customer_segment': ['Champions', 'Loyal Customers', 'At Risk'],
            'order_count': [2, 1, 1],
            'total_spent': [250.0, 150.0, 200.0]
        })
        chart_path = chart_gen.create_customer_segments_chart(customers_df)
        self.assertTrue(os.path.exists(chart_path))

        # Test returns pie chart (empty data)
        returns_df = pd.DataFrame(columns=['return_reason', 'return_count'])
        chart_path = chart_gen.create_returns_pie_chart(returns_df)
        self.assertIsNone(chart_path)  # Should return None for empty data

        # Test marketing performance chart
        marketing_df = pd.DataFrame({
            'channel': ['Email', 'Social', 'Search'],
            'attributed_revenue': [100.0, 150.0, 200.0]
        })
        chart_path = chart_gen.create_marketing_performance_chart(marketing_df)
        self.assertTrue(os.path.exists(chart_path))

    def test_report_exporter(self):
        """Test report export functionality."""
        exporter = ReportExporter(self.output_dir)

        # Create sample data
        sample_data = {
            'sales': pd.DataFrame({
                'total_price': [100.0, 150.0, 200.0],
                'profit': [20.0, 30.0, 40.0],
                'order_id': [101, 102, 103],
                'customer_id': [1, 2, 3]
            }),
            'customers': pd.DataFrame({
                'customer_id': [1, 2, 3],
                'customer_segment': ['Champions', 'Loyal Customers', 'At Risk'],
                'order_count': [2, 1, 1],
                'total_spent': [250.0, 150.0, 200.0]
            })
        }

        sample_kpis = {
            'total_revenue': 450.0,
            'total_profit': 90.0,
            'total_orders': 3,
            'total_customers': 3,
            'avg_order_value': 150.0,
            'profit_margin': 0.2
        }

        sample_insights = [
            "Total revenue was $450.00 for the period.",
            "Profit margin is healthy at 20.0%.",
            "Customer segmentation shows Champions as the largest segment."
        ]

        sample_chart_paths = {
            'revenue_trend': str(self.charts_dir / 'revenue_trend.png'),
            'profit_vs_revenue': str(self.charts_dir / 'profit_vs_revenue.png')
        }
        # Create dummy chart files
        for path in sample_chart_paths.values():
            Path(path).touch()

        timestamp = "20230101_120000"

        # Test CSV export
        csv_path = exporter.export_to_csv(sample_data, sample_kpis, sample_insights, timestamp)
        self.assertTrue(os.path.exists(csv_path))
        self.assertTrue(csv_path.endswith('.csv'))

        # Test Excel export
        excel_path = exporter.export_to_excel(sample_data, sample_kpis, sample_insights, sample_chart_paths, timestamp)
        self.assertTrue(os.path.exists(excel_path))
        self.assertTrue(excel_path.endswith('.xlsx'))

        # Test PDF export
        pdf_path = exporter.export_to_pdf(sample_data, sample_kpis, sample_insights, sample_chart_paths, timestamp)
        self.assertTrue(os.path.exists(pdf_path))
        self.assertTrue(pdf_path.endswith('.pdf'))

if __name__ == '__main__':
    unittest.main()
