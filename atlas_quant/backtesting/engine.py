"""(Backtesting Engine
==================

Main orchestrator for the backtesting simulation.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from atlas_quant.data.manager import MarketDataManager
from atlas_quant.execution.paper_broker import PaperBroker

logger = logging.getLogger(__name__)

class BacktestEngine:
    """
    Main backtesting engine that orchestrates the simulation pipeline.
    """

    def __init__(self,
                 start_date: str,
                 end_date: str,
                 initial_capital: float = 100000,
                 rebalance_frequency: str = "weekly",
                 benchmark_symbol: str = "SPY"):
        """
        Initialize the backtesting engine.
        """
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.initial_capital = initial_capital
        self.rebalance_frequency = rebalance_frequency
        self.benchmark_symbol = benchmark_symbol

        # Initialize components
        self.data_manager = MarketDataManager()
        self.broker = PaperBroker()
        self.results = {}
        self.daily_snapshots = []
        self.trade_history = []
        self.equity_curve = []

        # Connect broker
        self.broker.connect()

        # Load benchmark data for comparison
        try:
            self.benchmark_data = self.data_manager.get_data(
                ticker=self.benchmark_symbol,
                start=self.start_date.strftime('%Y-%m-%d'),
                end=self.end_date.strftime('%Y-%m-%d')
            )
        except Exception as e:
            logger.warning(f"Could not load benchmark data for {self.benchmark_symbol}: {e}")
            self.benchmark_data = pd.DataFrame()

    def run(self,
            symbols: List[str],
            decision_engine: object,
            data_loader: callable = None) -> Dict[str, Any]:
        """
        Run the backtest simulation.

        Args:
            symbols: List of stock symbols to trade
            decision_engine: Strategy/engine that generates trading signals
            data_loader: Optional custom data loader function (defaults to internal data manager)

        Returns:
            Dictionary containing backtest results and performance metrics
        """
        logger.info(f"Starting backtest from {self.start_date} to {self.end_date}")
        logger.info(f"Initial capital: ${self.initial_capital:,.2f}")
        logger.info(f"Trading symbols: {symbols}")

        # Load historical data for all symbols
        market_data = {}
        for symbol in symbols:
            try:
                data = self.data_manager.get_data(
                    ticker=symbol,
                    start=self.start_date.strftime('%Y-%m-%d'),
                    end=self.end_date.strftime('%Y-%m-%d')
                )
                if not data.empty:
                    market_data[symbol] = data
                    logger.info(f"Loaded {len(data)} rows for {symbol}")
                else:
                    logger.warning(f"No data loaded for {symbol}")
            except Exception as e:
                logger.error(f"Failed to load data for {symbol}: {e}")
                continue

        if not market_data:
            raise ValueError("No market data loaded for any symbols")

        # Get all unique dates across all symbols, sorted
        all_dates = set()
        for data in market_data.values():
            all_dates.update(data.index)
        trading_dates = sorted([d for d in all_dates
                               if self.start_date <= d <= self.end_date])

        logger.info(f"Backtesting over {len(trading_dates)} trading days")

        # Initialize tracking variables
        equity_curve = []
        daily_returns = []

        # Main backtest loop - iterate through each trading day
        for current_date in trading_dates:
            logger.debug(f"Processing date: {current_date}")

            # Prepare data up to current date for feature calculation
            historical_data = {}
            for symbol, data in market_data.items():
                # Get data up to and including current date
                hist_data = data.loc[:current_date]
                if len(hist_data) > 0:
                    historical_data[symbol] = hist_data

            # Skip if we don't have enough data for any symbol
            if len(historical_data) < len(symbols) * 0.8:  # Allow some missing data
                continue

            # Update broker with current market data
            for symbol, data in historical_data.items():
                self.broker.update_market_data(symbol, data)

            # Calculate features for each symbol
            featured_data = {}
            for symbol, data in historical_data.items():
                try:
                    # Use data_loader if provided, otherwise use default feature processing
                    if data_loader:
                        featured = data_loader(data)
                    else:
                        # Default: calculate basic features needed by strategy
                        featured = self._calculate_default_features(data)
                    featured_data[symbol] = featured
                except Exception as e:
                    logger.warning(f"Failed to calculate features for {symbol}: {e}")
                    # Use raw data as fallback
                    featured_data[symbol] = data

            # Build a feature matrix for the current date (symbols as rows, features as columns)
            # We need the latest feature values for each symbol
            latest_features = {}
            for symbol, df in featured_data.items():
                if len(df) > 0:
                    latest_features[symbol] = df.iloc[-1]  # Get the most recent row
                # If no data, we skip this symbol for today

            # Skip if we have no data for any symbol
            if not latest_features:
                continue

            # Convert to DataFrame: index=symbol, columns=feature names
            feature_matrix = pd.DataFrame(latest_features).T

            # Generate signals from decision engine/strategy
            try:
                if hasattr(decision_engine, 'process'):
                    # Decision engine interface
                    signal_result = decision_engine.process(feature_matrix)
                    signals = signal_result.get('target_weights', {})
                elif hasattr(decision_engine, 'generate_signals'):
                    # Strategy interface
                    signals = decision_engine.generate_signals(feature_matrix)
                else:
                    # Fallback: equal weight
                    symbols_with_data = list(latest_features.keys())
                    signals = {symbol: 1.0/len(symbols_with_data) for symbol in symbols_with_data}

                # Convert Series to dict if necessary
                if isinstance(signals, pd.Series):
                    signals = signals.to_dict()

                # Normalize signals to weights
                total_signal = sum(abs(v) for v in signals.values()) if signals else 0
                if total_signal > 0:
                    weights = {k: v/total_signal for k, v in signals.items()}
                else:
                    symbols_with_data = list(latest_features.keys())
                    weights = {symbol: 1.0/len(symbols_with_data) for symbol in symbols_with_data}

            except Exception as e:
                logger.warning(f"Failed to generate signals: {e}")
                symbols_with_data = list(latest_features.keys())
                weights = {symbol: 1.0/len(symbols_with_data) for symbol in symbols_with_data}

            # Execute trades based on weights (simplified - in practice would check rebalance frequency)
            self._execute_trades(weights, featured_data, current_date)

            # Record daily snapshot
            portfolio_value = self._calculate_portfolio_value(featured_data)
            equity_curve.append({
                'date': current_date,
                'portfolio_value': portfolio_value,
                'cash': self.broker.account.get('cash', 0),
                'positions_value': portfolio_value - self.broker.account.get('cash', 0)
            })

            # Calculate daily return
            if len(equity_curve) > 1:
                prev_value = equity_curve[-2]['portfolio_value']
                curr_value = equity_curve[-1]['portfolio_value']
                daily_return = (curr_value - prev_value) / prev_value if prev_value != 0 else 0
                daily_returns.append(daily_return)
            else:
                daily_returns.append(0.0)

        # Calculate final performance metrics
        results = self._calculate_performance_metrics(equity_curve, daily_returns)

        # Store results
        self.results = results
        self.equity_curve = equity_curve

        logger.info("Backtest completed successfully")
        return results

    def _calculate_default_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate default technical indicators for a security."""
        df = data.copy()

        # Calculate basic features that strategies might need
        # SMA 20, 50, 200
        df['sma_20'] = df['Close'].rolling(window=20).mean()
        df['sma_50'] = df['Close'].rolling(window=50).mean()
        df['sma_200'] = df['Close'].rolling(window=200).mean()

        # RSI 14
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df['rsi_14'] = 100 - (100 / (1 + rs))

        return df

    def _execute_trades(self, target_weights: Dict[str, float],
                       featured_data: Dict[str, pd.DataFrame],
                       current_date: pd.Timestamp):
        """Execute trades to reach target portfolio weights."""
        # Get current prices
        current_prices = {}
        for symbol, data in featured_data.items():
            if len(data) > 0:
                current_prices[symbol] = data['Close'].iloc[-1]

        # Get current positions and cash
        current_positions = self.broker.get_positions()
        account = self.broker.get_account()
        cash = account.get('cash', 0)

        # Calculate current value of each position
        current_values = {}
        total_position_value = 0
        for symbol, price in current_prices.items():
            quantity = current_positions.get(symbol, {}).get('quantity', 0)
            value = quantity * price
            current_values[symbol] = value
            total_position_value += value

        # Total portfolio value (cash + positions)
        total_value = cash + total_position_value

        # If we have no value, nothing to do
        if total_value == 0:
            return

        # For each target symbol, calculate the target value and trade the difference
        for symbol, target_weight in target_weights.items():
            if symbol not in current_prices:
                continue

            # Target value for this symbol
            target_value = target_weight * total_value

            # Current value of this symbol
            current_value = current_values.get(symbol, 0)

            # Difference in value
            value_diff = target_value - current_value

            # Only trade if the difference is significant (e.g., 1% of total value)
            if abs(value_diff) > 0.01 * total_value:
                # Calculate quantity to trade
                price = current_prices[symbol]
                if price == 0:
                    continue  # Avoid division by zero
                quantity_to_trade = value_diff / price

                # Create order
                order = {
                    'symbol': symbol,
                    'quantity': abs(quantity_to_trade),
                    'side': 'buy' if quantity_to_trade > 0 else 'sell',
                    'order_type': 'market'
                }

                try:
                    # Execute trade
                    result = self.broker.submit_order(order)
                    logger.debug(f"Executed {order['side']} order for {symbol}: {result}")

                    # Record trade
                    self.trade_history.append({
                        'date': current_date,
                        'symbol': symbol,
                        'side': order['side'],
                        'quantity': abs(quantity_to_trade),
                        'price': price,
                        'value': value_diff,
                        'order_id': result.get('order_id', 'unknown')
                    })
                except Exception as e:
                    logger.error(f"Failed to execute trade for {symbol}: {e}")

    def _calculate_portfolio_value(self, featured_data: Dict[str, pd.DataFrame]) -> float:
        """Calculate total portfolio value."""
        positions_value = 0
        positions = self.broker.get_positions()

        for symbol, position in positions.items():
            if symbol in featured_data and len(featured_data[symbol]) > 0:
                price = featured_data[symbol]['Close'].iloc[-1]
                quantity = position.get('quantity', 0)
                positions_value += price * quantity

        cash = self.broker.account.get('cash', 0)
        return positions_value + cash

    def _calculate_performance_metrics(self, equity_curve: List[Dict],
                                     daily_returns: List[float]) -> Dict[str, Any]:
        """Calculate performance metrics from equity curve."""
        if not equity_curve or len(equity_curve) < 2:
            return {
                "status": "completed",
                "message": "Insufficient data for performance calculation",
                "total_return": 0.0,
                "annualized_return": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "volatility": 0.0,
                "final_value": self.initial_capital,
                "start_date": self.start_date.strftime('%Y-%m-%d') if hasattr(self, 'start_date') else "",
                "end_date": self.end_date.strftime('%Y-%m-%d') if hasattr(self, 'end_date') else "",
                "initial_capital": self.initial_capital,
                "annualized_volatility": 0.0,
                "win_rate": 0.0,
                "benchmark_return": 0.0,
                "excess_return": 0.0,
                "total_trades": 0,
                "equity_curve": equity_curve,
                "trade_history": self.trade_history,
                "daily_returns": daily_returns
            }

        # Extract values
        values = [point['portfolio_value'] for point in equity_curve]
        dates = [point['date'] for point in equity_curve]

        # Basic returns
        initial_value = values[0]
        final_value = values[-1]
        total_return = (final_value - initial_value) / initial_value

        # Annualized return (assuming 252 trading days per year)
        trading_days = len(values)
        years = trading_days / 252.0
        if years > 0:
            annualized_return = (1 + total_return) ** (1/years) - 1
        else:
            annualized_return = 0.0

        # Volatility and Sharpe ratio (assuming 0% risk-free rate)
        if len(daily_returns) > 1:
            returns_series = pd.Series(daily_returns)
            volatility = returns_series.std() * np.sqrt(252)  # Annualized
            sharpe_ratio = (returns_series.mean() * 252) / volatility if volatility != 0 else 0
        else:
            volatility = 0.0
            sharpe_ratio = 0.0

        # Maximum drawdown
        peak = values[0]
        max_drawdown = 0.0
        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        # Win rate
        winning_days = sum(1 for r in daily_returns if r > 0)
        total_days = len(daily_returns)
        win_rate = winning_days / total_days if total_days > 0 else 0.0

        # Benchmark comparison (if available)
        benchmark_return = 0.0
        if hasattr(self, 'benchmark_data') and not self.benchmark_data.empty:
            try:
                benchmark_start = self.benchmark_data['Close'].iloc[0]
                benchmark_end = self.benchmark_data['Close'].iloc[-1]
                benchmark_return = (benchmark_end - benchmark_start) / benchmark_start
            except:
                benchmark_return = 0.0

        return {
            "status": "completed",
            "start_date": self.start_date.strftime('%Y-%m-%d'),
            "end_date": self.end_date.strftime('%Y-%m-%d'),
            "initial_capital": self.initial_capital,
            "final_value": final_value,
            "total_return": total_return,
            "annualized_return": annualized_return,
            "annualized_volatility": volatility,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "win_rate": win_rate,
            "benchmark_return": benchmark_return,
            "excess_return": total_return - benchmark_return,
            "total_trades": len(self.trade_history),
            "equity_curve": equity_curve,
            "trade_history": self.trade_history,
            "daily_returns": daily_returns
        }

