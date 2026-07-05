"""
Test Alpaca Connection
======================

Example script to test the connection to Alpaca Paper Trading API.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from atlas_quant.execution.broker_factory import get_broker


def main():
    """Main function to test Alpaca connection."""
    print("Creating broker instance...")
    broker = get_broker()  # Uses ALPACA_ENV from environment, defaults to paper
    
    print("Connecting to Alpaca...")
    if not broker.connect():
        print("Failed to connect to Alpaca. Check your API keys and network connection.")
        return
    
    print("Connected successfully!")
    
    # Get account information
    account = broker.get_account()
    print("\nAccount Information:")
    print(f"  Account Number: {account.get('account_number', 'N/A')}")
    print(f"  Buying Power: ")
    print(f"  Cash: ")
    print(f"  Portfolio Value: ")
    
    # Get positions
    positions = broker.get_positions()
    print(f"\nCurrent Positions ({len(positions)}):")
    if positions:
        for symbol, pos in positions.items():
            print(f"  {symbol}: {float(pos.get('qty', 0)):,.4f} shares @ ")
    else:
        print("  No open positions")
    
    # Get open orders
    orders = broker.get_orders(status="open")
    print(f"\nOpen Orders ({len(orders)}):")
    if orders:
        for order in orders:
            print(f"  {order.get('id', 'N/A')}: {order.get('side', 'N/A')} {order.get('qty', 0)} {order.get('symbol', 'N/A')} @ {order.get('limit_price', 'market')}")
    else:
        print("  No open orders")
    
    # Get market status
    is_open = broker.is_market_open()
    print(f"\nMarket Status: {'OPEN' if is_open else 'CLOSED'}")
    
    # Get market clock (additional method)
    clock = broker.get_market_clock()
    print(f"  Next Open: {clock.get('next_open', 'N/A')}")
    print(f"  Next Close: {clock.get('next_close', 'N/A')}")
    
    # Disconnect
    print("\nDisconnecting...")
    broker.disconnect()
    print("Done.")


if __name__ == "__main__":
    main()
