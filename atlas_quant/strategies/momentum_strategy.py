from .base import BaseStrategy
from typing import List, Dict

class MomentumStrategy(BaseStrategy):
    """
    A simple momentum strategy that ranks stocks by a momentum score (e.g., RSI)
    and selects the top N stocks.
    """

    def __init__(self, momentum_feature: str = 'rsi_14', lookback_period: int = 14,
                 top_n: int = 10):
        super().__init__()
        self.momentum_feature = momentum_feature
        self.lookback_period = lookback_period
        self.top_n = top_n

    def initialize(self) -> None:
        # No initialization needed for this simple strategy
        self.initialized = True

    def feature_requirements(self) -> List[str]:
        # Requires the momentum feature
        return [self.momentum_feature]

    def filters(self) -> List[str]:
        # Example filters: price above minimum, volume above minimum
        return ['price_above_min', 'volume_above_min']

    def signal_weights(self) -> dict:
        # Only one signal: momentum
        return {self.momentum_feature: 1.0}

    def build_portfolio(self, scores: dict) -> dict:
        """
        Given scores (already filtered and weighted), select top_n stocks
        and assign equal weight.
        """
        # Sort by score descending
        sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        # Select top_n
        selected = sorted_items[:self.top_n]
        # Equal weight
        weight = 1.0 / len(selected) if selected else 0.0
        return {symbol: weight for symbol, _ in selected}
