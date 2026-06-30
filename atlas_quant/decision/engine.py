import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from .filters import FILTER_FUNCTIONS
from .signals import SIGNAL_FUNCTIONS
from .scoring import ScoreCalculator
from .ranking import Ranker
from .portfolio import PortfolioBuilder
from .sizing import PositionSizer
from .orders import compute_orders

class DecisionEngine:
    """
    Main engine that takes a feature matrix and produces investment decisions.
    """

    def __init__(self, strategy=None,
                 signal_weights: Optional[Dict[str, float]] = None,
                 filters: Optional[list] = None,
                 ranking_method: str = 'desc',
                 ranking_n: Optional[int] = None,
                 portfolio_method: str = 'equal_weight',
                 portfolio_max_weight: Optional[float] = None,
                 sizing_method: str = 'equal_weight',
                 sizing_max_position_size: Optional[float] = None,
                 sizing_risk_per_position: Optional[float] = None):
        """
        Initialize the decision engine.
        You can either provide a strategy object (which must implement the BaseStrategy interface)
        or provide the components directly.
        If a strategy is provided, it will override the component parameters.
        """
        if strategy is not None:
            self.strategy = strategy
            # Extract from strategy
            self.signal_weights = strategy.signal_weights()
            self.filters = strategy.filters()
            # We'll need to get ranking and portfolio parameters from strategy? Not in base.
            # We'll assume the strategy does not specify these; we'll use defaults.
            # For simplicity, we'll ignore strategy-specific ranking/portfolio settings.
            # In a more advanced design, the strategy could return these.
        else:
            self.strategy = None
            self.signal_weights = signal_weights or {}
            self.filters = filters or []
        self.ranking_method = ranking_method
        self.ranking_n = ranking_n
        self.portfolio_method = product_method
        self.portfolio_max_weight = portfolio_max_weight
        self.sizing_method = sizing_method
        self.sizing_max_position_size = sizing_max_position_size
        self.sizing_risk_per_position = sizing_risk_per_position

        # Initialize sub-components
        self.score_calculator = ScoreCalculator(self.signal_weights, self.filters)
        self.ranker = Ranker(method=self.ranking_method, n=self.ranking_n)
        self.portfolio_builder = PortfolioBuilder(method=self.portfolio_method,
                                                  max_weight=self.portfolio_max_weight)
        self.position_sizer = PositionSizer(method=self.sizing_method,
                                            max_position_size=self.sizing_max_position_size,
                                            risk_per_position=self.sizing_risk_per_position)

    def process(self, feature_matrix: pd.DataFrame,
                current_weights: Optional[pd.Series] = None) -> Dict[str, Any]:
        """
        Process the feature matrix and return a dictionary with:
          - filtered_assets: boolean mask of assets that passed filters
          - scores: composite scores (after filtering)
          - ranked: DataFrame with score and rank
          - target_weights: portfolio weights before sizing
          - sized_weights: portfolio weights after sizing
          - orders: DataFrame of order recommendations (if current_weights provided)
        """
        # 1. Apply filters and compute scores
        scores = self.score_calculator.compute_scores(feature_matrix)
        # 2. Rank the scores (only consider those that passed filters, i.e., non-NaN scores)
        ranked_df = self.ranker.rank(scores)
        # 3. Build target portfolio from ranked assets
        # We'll pass the ranked DataFrame (which includes score and rank) and the feature matrix
        target_weights = self.portfolio_builder.build(ranked_df, feature_matrix)
        # 4. Apply position sizing
        # For sizing, we may need volatility. We'll try to extract a volatility column.
        # We'll look for a column with 'volatility' or 'atr' in the name.
        vol_cols = [c for c in feature_matrix.columns if 'volatility' in c.lower() or 'atr' in c.lower()]
        volatility = None
        if vol_cols:
            # Use the first volatility column
            volatility = feature_matrix[vol_cols[0]]
        sized_weights = self.position_sizer.size(target_weights, volatility)
        # 5. Generate orders if current_weights provided
        orders = None
        if current_weights is not None:
            # Ensure both series have the same index (union)
            all_indices = sorted(set(current_weights.index).union(set(sized_weights.index)))
            cur = current_weights.reindex(all_indices).fillna(0.0)
            targ = sized_weights.reindex(all_indices).fillna(0.0)
            orders = compute_orders(cur, targ)  # We'll need to import generate_orders
        return {
            'scores': scores,
            'ranked': ranked_df,
            'target_weights': target_weights,
            'sized_weights': sized_weights,
            'orders': orders
        }



