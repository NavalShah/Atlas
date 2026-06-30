import pandas as pd
import numpy as np
from typing import Optional

class PositionSizer:
    """
    Sizes positions based on risk objectives.
    """

    def __init__(self, method: str = 'equal_weight', max_position_size: Optional[float] = None,
                 risk_per_position: Optional[float] = None):
        """
        Parameters
        ----------
        method : str
            Sizing method: 'equal_weight', 'volatility_target', 'fixed_fraction'.
        max_position_size : float, optional
            Maximum weight allowed for any position (e.g., 0.05 for 5%).
        risk_per_position : float, optional
            Amount of risk (e.g., volatility) to allocate per position.
        '''
        self.method = method
        self.max_position_size = max_position_size
        self.risk_per_position = risk_per_position

    def size(self, weights: pd.Series, volatility: Optional[pd.Series] = None) -> pd.Series:
        """
        Adjust weights based on sizing method.
        Parameters
        ----------
        weights : pd.Series
            Initial weights (should sum to 1).
        volatility : pd.Series, optional
            Volatility for each asset (same index as weights). Required for volatility_target method.
        Returns
        -------
        pd.Series
            Adjusted weights.
        '''
        if self.method == 'equal_weight':
            # Already equal weight; just enforce max position size if needed
            sized = weights.copy()
        elif self.method == 'volatility_target':
            if volatility is None:
                raise ValueError("Volatility must be provided for volatility_target method")
            # Target volatility per position: we want each position to contribute equally to portfolio volatility.
            # Weight inversely proportional to volatility.
            inv_vol = 1.0 / volatility.replace(0, np.nan)
            sized = inv_vol / inv_vol.sum()
        elif self.method == 'fixed_fraction':
            if self.risk_per_position is None:
                raise ValueError("risk_per_position must be set for fixed_fraction method")
            # Not implemented fully; we'll just return equal weight for now.
            sized = weights.copy()
        else:
            raise ValueError(f"Unknown sizing method: {self.method}")

        # Apply max position size constraint
        if self.max_position_size is not None:
            sized = sized.clip(upper=self.max_position_size)
            # Renormalize
            sized = sized / sized.sum()
        return sized
