from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseStrategy(ABC):
    """Abstract base class for all strategies."""

    def __init__(self):
        self.initialized = False

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the strategy. Called once before the start of the backtest/live."""
        pass

    @abstractmethod
    def feature_requirements(self) -> List[str]:
        """Return a list of feature keys required by the strategy."""
        pass

    @abstractmethod
    def filters(self) -> List[str]:
        """Return a list of filter names to be applied."""
        pass

    @abstractmethod
    def signal_weights(self) -> Dict[str, float]:
        """Return a mapping of signal names to their weights."""
        pass

    @abstractmethod
    def build_portfolio(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Given a dictionary of asset scores, return target portfolio weights."""
        pass

    def shutdown(self) -> None:
        """Clean up resources. Called after the end of the backtest/live."""
        pass
