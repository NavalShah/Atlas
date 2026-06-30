import pandas as pd
import numpy as np
from .signals import SIGNAL_FUNCTIONS
from .filters import FILTER_FUNCTIONS

class ScoreCalculator:
    """
    Computes composite scores for assets based on signals and filters.
    """

    def __init__(self, signal_weights: dict, filters: list):
        """
        Parameters
        ----------
        signal_weights : dict
            Mapping from signal name to weight. The signal name must be a key in SIGNAL_FUNCTIONS.
        filters : list of str
            List of filter names to apply. Each must be a key in FILTER_FUNCTIONS.
        """
        self.signal_weights = signal_weights
        self.filters = filters
        # Validate
        for name in signal_weights:
            if name not in SIGNAL_FUNCTIONS:
                raise ValueError(f"Signal '{name}' not found in available signals.")
        for f in filters:
            if f not in FILTER_FUNCTIONS:
                raise ValueError(f"Filter '{f}' not found in available filters.")

    def _apply_filters(self, feature_matrix: pd.DataFrame) -> pd.Series:
        """
        Apply all filters and return a boolean mask (True for passing).
        """
        if not self.filters:
            return pd.Series(True, index=feature_matrix.index)
        mask = pd.Series(True, index=feature_matrix.index)
        for f_name in self.filters:
            func = FILTER_FUNCTIONS[f_name]
            # Call the filter function with default parameters (we'll need to pass config later)
            # For now, we assume the function can be called with just the feature matrix.
            # We'll need to inspect the function signature and pass default args.
            # To keep it simple, we'll assume the functions have been defined with sensible defaults.
            f_mask = func(feature_matrix)
            mask = mask & f_mask
        return mask

    def compute_scores(self, feature_matrix: pd.DataFrame) -> pd.Series:
        """
        Compute composite scores for each asset.
        Returns a Series indexed by the same index as feature_matrix, with scores.
        Assets that do not pass filters will have score NaN.
        """
        # Apply filters
        mask = self._apply_filters(feature_matrix)
        # Initialize scores as zero
        scores = pd.Series(0.0, index=feature_matrix.index)
        # For each signal, compute and add weighted contribution
        for signal_name, weight in self.signal_weights.items():
            func = SIGNAL_FUNCTIONS[signal_name]
            # Some signal functions need extra parameters (e.g., raw_feature needs feature_name).
            # We'll handle special cases.
            if signal_name == 'raw_feature':
                # We'll skip because we don't know which feature.
                # In practice, the strategy should not use raw_feature without specifying the feature.
                continue
            # For other functions, we call with the feature matrix and let them use their defaults.
            # We'll need to pass the feature matrix only; the functions we defined accept only feature_matrix.
            # However, some of our signal functions have optional parameters (e.g., trend_signal).
            # We'll call them with just the feature matrix; they will use their default parameters.
            signal_series = func(feature_matrix)
            scores += weight * signal_series
        # Apply mask: set scores of failed filters to NaN
        scores = scores.where(mask, np.nan)
        return scores
