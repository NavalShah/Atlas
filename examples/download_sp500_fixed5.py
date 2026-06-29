"""
Example script to download S&P 500 data.
This script demonstrates how to use the MarketDataManager to get data for multiple tickers.
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path so we can import atlas_quant
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# Change working directory to project root (where config/ lives)
os.chdir(project_root)

from atlas_quant.data.manager import MarketDataManager

def main():
    manager = MarketDataManager()

    # Example: Download data for a few S&P 500 stocks
    tickers = [
        "AAPL",
        "MSFT",
        "NVDA",
        "GOOGL",
        "META",
    ]

    data = {}

    for ticker in tickers:
        print(f"Fetching data for {ticker}...")
        data[ticker] = manager.get_data(
            ticker=ticker,
            start="2015-01-01",
            end="2024-12-31",
        )
        print(f"Got {len(data[ticker])} rows for {ticker}")
        print(data[ticker].head())
        print("-" * 50)

if __name__ == "__main__":
    main()