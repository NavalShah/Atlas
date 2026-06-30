from .base import BaseStrategy
from typing import List, Dict

class ExampleStrategy(BaseStrategy):
    """
    An example strategy that uses momentum and trend filters.
    """

    def __init__(self):
        super().__init__()
        self.initialized = False

    def initialize(self) -> None:
        # Initialize any resources needed
        self.initialized = True

    def feature_requirements(self) -> List[str]:
        # This strategy needs RSI and SMA 50 and SMA 200
        return ['rsi_14', 'sma_50', 'sma_200']

    def filters(self) -> List[str]:
        # Use price above 200-day MA and volume above minimum
        return ['above_200_ma', 'volume_above_min']

    def signal_weights(self) -> Dict[str, float]:
        # Weight the RSI as momentum signal
        return {'rsi_14': 1.0}

    def build_portfolio(self, scores: dict) -> dict:
        # Simple: select top 2 stocks and equal weight
        # scores is a dict of ticker -> score (already filtered and scored)
        # Sort by score descending
        sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        # Take top 2
        top_n = sorted_items[:2]
        weight = 1.0 / len(top_n) if top_n else 0.0
        return {ticker: weight for ticker, _ in top_n}

    def shutdown(self) -> None:
        # Clean up resources
        pass
