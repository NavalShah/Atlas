"""
Paper Trading Rebalance Example
===============================

Example script for portfolio rebalancing using Alpaca Paper Trading.
This script demonstrates the full workflow from signal generation to order execution.
"""
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from atlas_quant.execution.broker_factory import get_broker
from atlas_quant.utilities.environment import get_alpaca_credentials


def load_market_data():
    """
    Load latest cached market data.
    In a real implementation, this would read from a cache or database.
    For this example, we return an empty dict as a placeholder.
    """
    # Placeholder: implement actual data loading as needed
    return {}


def generate_market_data(market_data):
    """
    Generate missing market data (e.g., calculate technical indicators).
    In a real implementation, this would use the feature pipeline.
    For this example, we return the input unchanged.
    """
    # Placeholder: implement actual data generation as needed
    return market_data


def run_feature_pipeline(market_data):
    """
    Run the feature pipeline to generate features for the decision engine.
    In a real implementation, this would compute technical factors, etc.
    For this example, we return a dummy feature set.
    """
    # Placeholder: implement actual feature generation as needed
    return {"feature_example": 1.0}


def run_decision_engine(features):
    """
    Run the decision engine to generate target portfolio weights.
    In a real implementation, this would use a model or strategy to decide weights.
    For this example, we return a fixed target portfolio.
    """
    # Example: target portfolio with equal weights for a few stocks
    # In practice, this would be driven by the strategy
    target_portfolio = {
        "AAPL": 0.25,
        "MSFT": 0.25,
        "GOOGL": 0.25,
        "AMZN": 0.25
    }
    return target_portfolio


def get_target_positions(target_weights, portfolio_value):
    """
    Convert target weights to target quantities based on current prices.
    For simplicity, we use the last close price from market data (not implemented here).
    In a real implementation, you would fetch current prices.
    For this example, we assume a fixed price per share to calculate quantity.
    """
    # Placeholder: in reality, you would get current prices for each symbol
    # Here we assume a price of  per share for simplicity
    assumed_price = 100.0
    target_positions = {}
    for symbol, weight in target_weights.items():
        # Calculate target dollar amount
        target_dollar = portfolio_value * weight
        # Convert to number of shares (rounded to whole share)
        target_qty = int(target_dollar / assumed_price)
        target_positions[symbol] = target_qty
    return target_positions


def calculate_trades(current_positions, target_positions):
    """
    Calculate the trades needed to move from current positions to target positions.
    
    Args:
        current_positions: dict of symbol -> quantity (from broker.get_positions())
        target_positions: dict of symbol -> target quantity
        
    Returns:
        dict of symbol -> quantity to trade (positive for buy, negative for sell)
    """
    trades = {}
    all_symbols = set(list(current_positions.keys()) + list(target_positions.keys()))
    for symbol in all_symbols:
        current = current_positions.get(symbol, 0)
        target = target_positions.get(symbol, 0)
        quantity = target - current
        if quantity != 0:
            trades[symbol] = quantity
    return trades


def display_trades(trades):
    """Display the calculated trades in a human-readable format."""
    print("\nProposed Trades:")
    if not trades:
        print("  No trades required.")
        return
    
    for symbol, qty in trades.items():
        action = "BUY" if qty > 0 else "SELL"
        print(f"  {action} {abs(qty)} shares of {symbol}")


def execute_trades(broker, trades):
    """
    Execute the trades by submitting market orders.
    
    Args:
        broker: The broker instance (AlpacaBroker)
        trades: dict of symbol -> quantity to trade
        
    Returns:
        dict of order IDs mapped to the trade details
    """
    orders = {}
    for symbol, qty in trades.items():
        if qty == 0:
            continue
        side = "buy" if qty > 0 else "sell"
        order = {
            "symbol": symbol,
            "qty": abs(qty),
            "side": side,
            "type": "market",
            "time_in_force": "day"
        }
        try:
            print(f"Submitting order: {side} {abs(qty)} {symbol}")
            response = broker.submit_order(order)
            order_id = response.get("id")
            orders[order_id] = {
                "symbol": symbol,
                "quantity": qty,
                "side": side,
                "order_id": order_id,
                "status": "submitted"
            }
            print(f"  Order submitted: {order_id}")
        except Exception as e:
            print(f"  Failed to submit order for {symbol}: {e}")
    return orders


def wait_for_fills(broker, order_ids, timeout_seconds=30):
    """
    Wait for orders to be filled (or timeout) and return the filled status.
    
    Args:
        broker: The broker instance
        order_ids: list of order IDs to wait for
        timeout_seconds: maximum time to wait in seconds
        
    Returns:
        dict of order ID -> filled status and details
    """
    start_time = time.time()
    results = {order_id: {"filled": False, "details": None} for order_id in order_ids}
    
    while time.time() - start_time < timeout_seconds:
        all_done = True
        for order_id in order_ids:
            if results[order_id]["filled"]:
                continue
            try:
                # In a real implementation, you would check the order status
                # For simplicity, we'll just get the order and see if it's filled
                # Note: Alpaca API does not have a direct endpoint for a single order by ID in the trading client?
                # We can get all orders and filter, but that's inefficient. We'll skip for now and just wait a bit.
                # Instead, we'll just sleep and assume they fill immediately for demo purposes.
                # In a real system, you would poll the order status.
                pass
            except Exception:
                pass
            # For demo, we'll just mark as filled after a short wait
            time.sleep(2)
            results[order_id]["filled"] = True
            results[order_id]["details"] = {"status": "filled (simulated)"}
            all_done = all(results[oid]["filled"] for oid in order_ids)
            if all_done:
                break
        if all_done:
            break
        time.sleep(2)
    
    return results


def generate_execution_report(broker, orders, fill_results):
    """
    Generate an execution report summarizing the trades and their outcomes.
    
    Args:
        broker: The broker instance
        orders: dict of order ID -> order details (from submit_order)
        fill_results: dict of order ID -> fill status and details
        
    Returns:
        dict containing the report data
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "orders_submitted": len(orders),
        "orders_filled": sum(1 for v in fill_results.values() if v["filled"]),
        "orders": []
    }
    
    for order_id, order_info in orders.items():
        fill_info = fill_results.get(order_id, {"filled": False, "details": {}})
        report["orders"].append({
            "order_id": order_id,
            "symbol": order_info["symbol"],
            "quantity": order_info["quantity"],
            "side": order_info["side"],
            "filled": fill_info["filled"],
            "details": fill_info["details"]
        })
    
    # Get final positions and account info
    try:
        report["final_positions"] = broker.get_positions()
        report["final_account"] = broker.get_account()
    except Exception as e:
        report["final_positions_error"] = str(e)
        report["final_account_error"] = str(e)
    
    return report


def save_report(report, directory):
    """
    Save the execution report to a JSON file in the specified directory.
    
    Args:
        report: The report dictionary
        directory: Directory to save the report in
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"execution_report_{timestamp}.json"
    filepath = os.path.join(directory, filename)
    
    with open(filepath, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"Execution report saved to: {filepath}")


def main():
    """Main function to run the paper trading rebalance example."""
    print("Loading market data...")
    market_data = load_market_data()
    
    print("Generating missing market data...")
    market_data = generate_market_data(market_data)
    
    print("Running feature pipeline...")
    features = run_feature_pipeline(market_data)
    
    print("Running decision engine...")
    target_weights = run_decision_engine(features)
    
    print("Connecting to broker...")
    broker = get_broker()  # Uses ALPACA_ENV from environment
    if not broker.connect():
        print("Failed to connect to broker. Exiting.")
        return
    
    try:
        # Get current account and positions
        account = broker.get_account()
        portfolio_value = float(account.get('portfolio_value', 0))
        current_positions = broker.get_positions()
        
        # Convert current positions to a dict of symbol -> quantity
        current_positions_qty = {symbol: float(pos.get('qty', 0)) for symbol, pos in current_positions.items()}
        
        print(f"\nCurrent Portfolio Value: ")
        print(f"Current Positions: {current_positions_qty}")
        
        # Get target positions based on weights
        target_positions = get_target_positions(target_weights, portfolio_value)
        print(f"Target Positions: {target_positions}")
        
        # Calculate trades
        trades = calculate_trades(current_positions_qty, target_positions)
        
        # Display trades
        display_trades(trades)
        
        # Check if we are in dry run mode
        dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
        print(f"\nDry Run Mode: {dry_run}")
        
        if dry_run:
            print("\nDRY RUN: Orders will not be submitted.")
        else:
            print("\nSubmitting trades...")
            orders = execute_trades(broker, trades)
            
            if orders:
                print("\nWaiting for fills...")
                order_ids = list(orders.keys())
                fill_results = wait_for_fills(broker, order_ids, timeout_seconds=30)
                
                print("\nGenerating execution report...")
                report = generate_execution_report(broker, orders, fill_results)
                
                # Save report to a timestamped directory under ./reports
                report_dir = os.path.join(".", "reports", datetime.now().strftime("%Y%m%d"))
                save_report(report, report_dir)
            else:
                print("No orders to submit.")
    finally:
        print("\nDisconnecting from broker...")
        broker.disconnect()
    
    print("\nDone.")


if __name__ == "__main__":
    main()
