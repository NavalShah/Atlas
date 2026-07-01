#!/usr/bin/env python3
"""
Simple test script to demonstrate the backtesting engine
"""

import sys
import os
from pathlib import Path

# Add the project root to sys.path so that atlas_quant can be imported
project_root = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(project_root))

from atlas_quant.backtesting.engine import BacktestEngine
from atlas_quant.strategies.example_strategy import ExampleStrategy
from atlas_quant.decision.engine import DecisionEngine

def main():
    print("Testing Backtest Engine with Example Strategy and Decision Engine")
    print("=" * 60)

    # Define backtest parameters
    start_date = "2016-01-01"
    end_date = "2016-12-31"  # Just test 1 year for speed
    initial_capital = 100000

    # Define symbols to trade (using a few major stocks for testing)
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN"]

    # Create strategy
    strategy = ExampleStrategy()

    # Create decision engine using the strategy
    decision_engine = DecisionEngine(strategy=strategy)

    # Create backtest engine
    engine = BacktestEngine(
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
        rebalance_frequency="monthly",
        benchmark_symbol="SPY"
    )

    # Run backtest
    print(f"Running backtest from {start_date} to {end_date}")
    print(f"Initial capital: ${initial_capital:,.2f}")
    print(f"Symbols: {', '.join(symbols)}")
    print(f"Strategy: {type(strategy).__name__}")
    print(f"Decision Engine: {type(decision_engine).__name__}")
    print()

    try:
        results = engine.run(symbols=symbols, decision_engine=decision_engine)

        # Display results
        print("BACKTEST RESULTS")
        print("=" * 60)
        print(f"Status: {results['status']}")
        print(f"Period: {results['start_date']} to {results['end_date']}")
        print(f"Initial Capital: ${results['initial_capital']:,.2f}")
        print(f"Final Value: ${results['final_value']:,.2f}")
        print(f"Total Return: {results['total_return']:.2%}")
        print(f"Annualized Return: {results['annualized_return']:.2%}")
        print(f"Annualized Volatility: {results['annualized_volatility']:.2%}")
        print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: {results['max_drawdown']:.2%}")
        print(f"Win Rate: {results['win_rate']:.2%}")
        print(f"Benchmark Return: {results['benchmark_return']:.2%}")
        print(f"Excess Return: {results['excess_return']:.2%}")
        print(f"Total Trades: {results['total_trades']}")

        if results['total_trades'] > 0:
            print("\nRecent Trades:")
            for trade in results['trade_history'][-5:]:  # Show last 5 trades
                print(f"  {trade['date'].strftime('%Y-%m-%d')}: {trade['side'].upper()} {trade['quantity']:.0f} {trade['symbol']} @ ${trade['price']:.2f}")

    except Exception as e:
        print(f"Error running backtest: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())