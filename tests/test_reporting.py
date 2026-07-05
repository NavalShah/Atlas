"""
Tests for Execution Reporting Module
=====================================
"""
import unittest
import os
import json
import csv
import tempfile
from datetime import datetime
from atlas_quant.reporting.execution import (
    ExecutionReporter,
    ExecutionLogger,
    generate_all_reports
)


class TestExecutionReporter(unittest.TestCase):
    """Test execution reporting functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.reporter = ExecutionReporter()
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_create_report_directory(self):
        """Test creating a timestamped report directory."""
        report_dir = self.reporter.create_report_directory(self.temp_dir)
        
        self.assertTrue(os.path.exists(report_dir))
        self.assertIn(datetime.now().strftime("%Y%m%d"), report_dir)
    
    def test_generate_account_snapshot_json(self):
        """Test generating account snapshot JSON."""
        account_data = {
            "cash": 10000.0,
            "buying_power": 20000.0,
            "portfolio_value": 30000.0
        }
        positions_data = {
            "AAPL": {"qty": 100, "avg_fill_price": 150.0}
        }
        filepath = os.path.join(self.temp_dir, "account_snapshot.json")
        
        self.reporter.generate_account_snapshot_json(
            account_data, positions_data, filepath
        )
        
        self.assertTrue(os.path.exists(filepath))
        with open(filepath) as f:
            data = json.load(f)
        self.assertIn("account", data)
        self.assertIn("positions", data)
    
    def test_generate_orders_csv(self):
        """Test generating orders CSV."""
        orders = [
            {
                "order_id": "order_1",
                "symbol": "AAPL",
                "quantity": 100,
                "side": "buy",
                "status": "filled",
                "filled_quantity": 100,
                "average_fill_price": 150.0
            }
        ]
        filepath = os.path.join(self.temp_dir, "orders.csv")
        
        self.reporter.generate_orders_csv(orders, filepath)
        
        self.assertTrue(os.path.exists(filepath))
        with open(filepath) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["symbol"], "AAPL")
    
    def test_generate_fills_csv(self):
        """Test generating fills CSV."""
        orders = [
            {
                "order_id": "order_1",
                "symbol": "AAPL",
                "quantity": 100,
                "side": "buy",
                "filled_quantity": 100,
                "average_fill_price": 150.0
            },
            {
                "order_id": "order_2",
                "symbol": "MSFT",
                "quantity": 50,
                "side": "sell",
                "filled_quantity": 0,  # Not filled
                "average_fill_price": 0
            }
        ]
        filepath = os.path.join(self.temp_dir, "fills.csv")
        
        self.reporter.generate_fills_csv(orders, filepath)
        
        self.assertTrue(os.path.exists(filepath))
        with open(filepath) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        # Should only have 1 row (the filled order)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["symbol"], "AAPL")
    
    def test_generate_execution_report_json(self):
        """Test generating execution report JSON."""
        execution_data = {
            "timestamp": datetime.now().isoformat(),
            "orders_submitted": 2,
            "orders_filled": 1,
            "orders": []
        }
        filepath = os.path.join(self.temp_dir, "execution_report.json")
        
        self.reporter.generate_execution_report_json(
            execution_data, filepath
        )
        
        self.assertTrue(os.path.exists(filepath))
        with open(filepath) as f:
            data = json.load(f)
        self.assertEqual(data["orders_submitted"], 2)
    
    def test_generate_execution_report_html(self):
        """Test generating execution report HTML."""
        execution_data = {
            "timestamp": datetime.now().isoformat(),
            "orders": [
                {
                    "order_id": "order_1",
                    "symbol": "AAPL",
                    "side": "buy",
                    "quantity": 100,
                    "filled": True,
                    "details": {"status": "filled"}
                }
            ],
            "final_account": {"cash": 10000.0},
            "final_positions": {"AAPL": {"qty": 100, "avg_fill_price": 150.0}}
        }
        filepath = os.path.join(self.temp_dir, "execution_report.html")
        
        self.reporter.generate_execution_report_html(
            execution_data, filepath
        )
        
        self.assertTrue(os.path.exists(filepath))
        with open(filepath) as f:
            content = f.read()
        self.assertIn("Execution Report", content)
        self.assertIn("AAPL", content)


class TestExecutionLogger(unittest.TestCase):
    """Test execution logging."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = ExecutionLogger()
    
    def test_log_info(self):
        """Test logging info message."""
        self.logger.info("Test message")
        
        entries = self.logger.get_entries()
        self.assertEqual(len(entries), 1)
        self.assertIn("Test message", entries[0])
        self.assertIn("INFO", entries[0])
    
    def test_log_warning(self):
        """Test logging warning message."""
        self.logger.warning("Warning message")
        
        entries = self.logger.get_entries()
        self.assertEqual(len(entries), 1)
        self.assertIn("Warning message", entries[0])
        self.assertIn("WARNING", entries[0])
    
    def test_log_error(self):
        """Test logging error message."""
        self.logger.error("Error message")
        
        entries = self.logger.get_entries()
        self.assertEqual(len(entries), 1)
        self.assertIn("Error message", entries[0])
        self.assertIn("ERROR", entries[0])
    
    def test_multiple_entries(self):
        """Test logging multiple entries."""
        self.logger.info("Message 1")
        self.logger.warning("Message 2")
        self.logger.error("Message 3")
        
        entries = self.logger.get_entries()
        self.assertEqual(len(entries), 3)
    
    def test_entries_have_timestamp(self):
        """Test that log entries have timestamps."""
        self.logger.info("Test")
        entries = self.logger.get_entries()
        
        self.assertIn("T", entries[0])  # ISO format contains T


class TestGenerateAllReports(unittest.TestCase):
    """Test generating all report types together."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_generate_all_reports(self):
        """Test generating all report types."""
        execution_data = {
            "timestamp": datetime.now().isoformat(),
            "orders_submitted": 1,
            "orders_filled": 1,
            "orders": [],
            "final_account": {},
            "final_positions": {}
        }
        orders = []
        log_entries = ["Entry 1", "Entry 2"]
        account = {"cash": 10000.0}
        positions = {}
        
        generate_all_reports(
            self.temp_dir,
            execution_data,
            orders,
            log_entries,
            account,
            positions
        )
        
        # Check that all expected files were created
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "account_snapshot.json")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "execution_report.json")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "execution_report.html")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "execution_log.txt")))


if __name__ == '__main__':
    unittest.main()
