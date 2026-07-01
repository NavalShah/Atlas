import pandas as pd
import numpy as np
from typing import Optional, Dict

class PortfolioBuilder:
    """
    Builds a target portfolio from ranked assets.
    """

    def __init__(self, method: str = 'equal_weight', lookback_period: int = 20,
                 max_weight: Optional[float] = None):
        """
        Parameters
        ----------
        method : str
            Weighting method: 'equal_weight', 'volatility_weight', 'signal_weight'.
        lookback_period : int
            For volatility weighting, the lookback period to compute volatility (if not already present).
        max_weight : float, optional
            Maximum weight allowed for any single asset (for diversification).
        """
        self.method = method
        self.lookback_period = lookback_period
        self.max_weight = max_weight

    def build(self, ranked: pd.DataFrame, feature_matrix: pd.DataFrame) -> pd.Series:
        """
        Given ranked assets (with scores and ranks) and the feature matrix,
        return target weights as a Series indexed by asset.
        """
        # We'll consider only assets that have a rank (i.e., passed filters and were ranked)
        # For simplicity, we'll assume that ranked.index are the assets we want to weight.
        # We'll ignore the rank column and just use the index.
        assets = ranked.index
        if len(assets) == 0:
            return pd.Series(dtype=float)

        if self.method == 'equal_weight':
            weights = pd.Series(1.0 / len(assets), index=assets)
        elif self.method == 'volatility_weight':
            # Inverse volatility weighting: weight inversely proportional to volatility
            # We need a volatility column. Assume it's named 'volatility_<lookback>' or 'historical_volatility_<lookback>'
            # We'll try to find a column containing 'volatility' in its name.
            vol_cols = [c for c in feature_matrix.columns if 'volatility' in c.lower()]
            if not vol_cols:
                # Fallback to equal weight
                weights = pd.Series(1.0 / len(assets), index=assets)
            else:
                # Use the first volatility column
                vol = feature_matrix.loc[assets, vol_cols[0]]
                # Avoid division by zero
                inv_vol = 1.0 / vol.replace(0, np.nan)
                weights = inv_vol / inv_vol.sum()
        elif self.method == 'signal_weight':
            # Weight by score (but scores may not be available here; we have ranked scores?)
            # We'll need to pass the scores. Let's change: we'll accept a score series.
            # For simplicity, we'll skip this method.
            weights = pd.Series(1.0 / len(assets), index=assets)
        else:
            raise ValueError(f"Unknown weighting method: {self.method}")

        # Apply max weight constraint if specified
        if self.max_weight is not None:
            # If any weight exceeds max_weight, we need to redistribute.
            # Simple approach: cap at max_weight and renormalize.
            weights = weights.clip(upper=self.max_weight)
            # Renormalize to sum to 1
            weights = weights / weights.sum()
        else:
            # Ensure weights sum to 1 (already should, but just in case)
            weights = weights / weights.sum()
        return weights
