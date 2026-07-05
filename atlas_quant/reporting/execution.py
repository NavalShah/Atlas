"""
Execution Reporting
===================

Utilities for generating execution reports in various formats
(JSON, CSV, HTML) from execution data.
"""
import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ExecutionReporter:
    """
    Generates execution reports in multiple formats.
    """
    
    @staticmethod
    def create_report_directory(base_dir: str = "./reports") -> str:
        """
        Create a timestamped report directory.
        
        Args:
            base_dir: Base directory for reports
            
        Returns:
            Path to created directory
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = os.path.join(base_dir, datetime.now().strftime("%Y%m%d"), timestamp)
        os.makedirs(report_dir, exist_ok=True)
        logger.info(f"Created report directory: {report_dir}")
        return report_dir
    
    @staticmethod
    def generate_account_snapshot_json(
        account_data: Dict[str, Any],
        positions_data: Dict[str, Any],
        filepath: str
    ) -> None:
        """
        Generate account snapshot JSON report.
        
        Args:
            account_data: Account information dict
            positions_data: Positions dict
            filepath: Output file path
        """
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "account": account_data,
            "positions": positions_data
        }
        with open(filepath, 'w') as f:
            json.dump(snapshot, f, indent=2, default=str)
        logger.info(f"Account snapshot saved to: {filepath}")
    
    @staticmethod
    def generate_orders_csv(
        orders: List[Dict[str, Any]],
        filepath: str
    ) -> None:
        """
        Generate orders CSV report.
        
        Args:
            orders: List of order dictionaries
            filepath: Output file path
        """
        if not orders:
            logger.warning("No orders to write to CSV")
            return
        
        fieldnames = [
            "order_id", "symbol", "quantity", "side", "status",
            "filled_quantity", "average_fill_price", "timestamp", "filled_timestamp"
        ]
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for order in orders:
                # Filter order dict to include only known fieldnames
                row = {k: v for k, v in order.items() if k in fieldnames}
                writer.writerow(row)
        
        logger.info(f"Orders CSV saved to: {filepath}")
    
    @staticmethod
    def generate_fills_csv(
        orders: List[Dict[str, Any]],
        filepath: str
    ) -> None:
        """
        Generate fills CSV report (only filled orders).
        
        Args:
            orders: List of order dictionaries
            filepath: Output file path
        """
        filled_orders = [o for o in orders if o.get("filled_quantity", 0) > 0]
        
        if not filled_orders:
            logger.warning("No filled orders to write to CSV")
            return
        
        fieldnames = [
            "order_id", "symbol", "quantity", "side",
            "filled_quantity", "average_fill_price", "filled_timestamp"
        ]
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for order in filled_orders:
                row = {k: v for k, v in order.items() if k in fieldnames}
                writer.writerow(row)
        
        logger.info(f"Fills CSV saved to: {filepath}")
    
    @staticmethod
    def generate_execution_report_json(
        execution_data: Dict[str, Any],
        filepath: str
    ) -> None:
        """
        Generate comprehensive execution report as JSON.
        
        Args:
            execution_data: Dict containing execution details
            filepath: Output file path
        """
        with open(filepath, 'w') as f:
            json.dump(execution_data, f, indent=2, default=str)
        logger.info(f"Execution report saved to: {filepath}")
    
    @staticmethod
    def generate_execution_report_html(
        execution_data: Dict[str, Any],
        filepath: str
    ) -> None:
        """
        Generate HTML execution report.
        
        Args:
            execution_data: Dict containing execution details
            filepath: Output file path
        """
        timestamp = execution_data.get("timestamp", datetime.now().isoformat())
        orders = execution_data.get("orders", [])
        account = execution_data.get("final_account", {})
        positions = execution_data.get("final_positions", {})
        
        # Build orders table HTML
        orders_html = "<table border='1' cellpadding='5'><tr><th>Order ID</th><th>Symbol</th><th>Side</th><th>Quantity</th><th>Status</th><th>Filled</th></tr>"
        for order in orders:
            orders_html += f"<tr><td>{order.get('order_id', 'N/A')}</td><td>{order.get('symbol', 'N/A')}</td><td>{order.get('side', 'N/A')}</td><td>{order.get('quantity', 0)}</td><td>{order.get('filled', 'N/A')}</td><td>{order.get('details', {}).get('status', 'N/A')}</td></tr>"
        orders_html += "</table>"
        
        # Build positions table HTML
        positions_html = "<table border='1' cellpadding='5'><tr><th>Symbol</th><th>Quantity</th><th>Avg Price</th></tr>"
        if isinstance(positions, dict):
            for symbol, pos in positions.items():
                qty = pos.get('qty', 0) if isinstance(pos, dict) else 0
                avg_price = pos.get('avg_fill_price', 0) if isinstance(pos, dict) else 0
                positions_html += f"<tr><td>{symbol}</td><td>{qty}</td><td>${avg_price:.2f}</td></tr>"
        positions_html += "</table>"
        
        # Build account info
        account_html = "<ul>"
        for key, value in account.items():
            if isinstance(value, (int, float)):
                account_html += f"<li><b>{key}:</b> ${value:,.2f}</li>"
            else:
                account_html += f"<li><b>{key}:</b> {value}</li>"
        account_html += "</ul>"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Execution Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2 {{ color: #333; }}
                table {{ border-collapse: collapse; margin: 20px 0; }}
                table, th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
            </style>
        </head>
        <body>
            <h1>Execution Report</h1>
            <p><b>Timestamp:</b> {timestamp}</p>
            
            <h2>Account Information</h2>
            {account_html}
            
            <h2>Orders Executed</h2>
            {orders_html}
            
            <h2>Final Positions</h2>
            {positions_html}
        </body>
        </html>
        """
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        logger.info(f"HTML report saved to: {filepath}")
    
    @staticmethod
    def save_execution_log(
        log_entries: List[str],
        filepath: str
    ) -> None:
        """
        Save execution log entries to file.
        
        Args:
            log_entries: List of log entry strings
            filepath: Output file path
        """
        with open(filepath, 'w') as f:
            for entry in log_entries:
                f.write(entry + "\n")
        logger.info(f"Execution log saved to: {filepath}")


class ExecutionLogger:
    """
    Logs execution details for reporting and debugging.
    """
    
    def __init__(self):
        """Initialize execution logger."""
        self.entries: List[str] = []
    
    def log(self, message: str, level: str = "INFO") -> None:
        """
        Log an entry with timestamp and level.
        
        Args:
            message: Log message
            level: Log level (INFO, WARNING, ERROR, etc.)
        """
        timestamp = datetime.now().isoformat()
        entry = f"[{timestamp}] [{level}] {message}"
        self.entries.append(entry)
        logger.log(getattr(logging, level, logging.INFO), message)
    
    def info(self, message: str) -> None:
        """Log info level message."""
        self.log(message, "INFO")
    
    def warning(self, message: str) -> None:
        """Log warning level message."""
        self.log(message, "WARNING")
    
    def error(self, message: str) -> None:
        """Log error level message."""
        self.log(message, "ERROR")
    
    def get_entries(self) -> List[str]:
        """Get all log entries."""
        return self.entries.copy()


def generate_all_reports(
    report_dir: str,
    execution_data: Dict[str, Any],
    orders: List[Dict[str, Any]],
    log_entries: List[str],
    account: Dict[str, Any],
    positions: Dict[str, Any]
) -> None:
    """
    Generate all report types in the specified directory.
    
    Args:
        report_dir: Directory to save reports
        execution_data: Overall execution data
        orders: List of order details
        log_entries: List of log entries
        account: Account information
        positions: Positions information
    """
    reporter = ExecutionReporter()
    
    # Account snapshot
    reporter.generate_account_snapshot_json(
        account,
        positions,
        os.path.join(report_dir, "account_snapshot.json")
    )
    
    # Orders CSV
    reporter.generate_orders_csv(
        orders,
        os.path.join(report_dir, "orders.csv")
    )
    
    # Fills CSV
    reporter.generate_fills_csv(
        orders,
        os.path.join(report_dir, "fills.csv")
    )
    
    # Execution report JSON
    reporter.generate_execution_report_json(
        execution_data,
        os.path.join(report_dir, "execution_report.json")
    )
    
    # Execution report HTML
    reporter.generate_execution_report_html(
        execution_data,
        os.path.join(report_dir, "execution_report.html")
    )
    
    # Execution log
    reporter.save_execution_log(
        log_entries,
        os.path.join(report_dir, "execution_log.txt")
    )
    
    logger.info(f"All reports generated in: {report_dir}")
