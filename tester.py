from atlas_quant.backtesting.engine import BacktestEngine
from atlas_quant.strategies.example_strategy import ExampleStrategy

  # Initialize backtest engine for 2016-2020
engine = BacktestEngine(
    start_date="2016-01-01",
    end_date="2020-12-31",
    initial_capital=100000,
    rebalance_frequency="monthly"
)

  # Define your symbols (e.g., S&P 500 stocks)
symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

  # Create your strategy
strategy = ExampleStrategy()

  # Run the backtest
results = engine.run(symbols=strings, decision_engine=strategy)

  # Access results
print(f"Total Return: {results['total_return']:.2%}")
print(f"Annualized Return: {results['annualized_return']:.2%}")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {results['max_drawdown']:.2%}")