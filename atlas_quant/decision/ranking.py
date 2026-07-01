import pandas as pd
import numpy as np
from typing import Optional

class Ranker:
    """
    Ranks assets based on scores.
    """

    def __init__(self, method: str = 'desc', n: Optional[int] = None, ascending: bool = False):
        """
        Parameters
        ----------
        method : str
            Ranking method: 'desc' for descending (highest score rank 1), 'asc' for ascending.
            Alternatively, 'top_n' to select top N, 'percentile' to compute percentile rank.
        n : int, optional
            For 'top_n' method, the number of top ranks to select.
        ascending : bool
            If True, lower scores get better rank (rank 1). Only used if method is 'desc' or 'asc'.
        """
        self.method = method
        self.n = n
        self.ascending = ascending

    def rank(self, scores: pd.Series) -> pd.DataFrame:
        """
        Rank the scores.
        Returns a DataFrame with columns: 'score', 'rank'.
        If method: we'll compute rank using pandas rank.
        For 'top_n', we'll assign rank 1..n to top n and NaN to others.
        For 'percentile', we'll compute percentile rank (0-100).
        """
        # Copy to avoid modifying original
        scores_clean = scores.copy()
        # Remove NaN scores (failed filters) for ranking? We'll keep them as NaN and they will get NaN rank.
        if self.method == 'desc':
            # Rank descending: highest score gets rank 1
            ranks = scores_clean.rank(ascending=False, method='first')
        elif self.method == 'asc':
            ranks = scores_clean.rank(ascending=True, method='first')
        elif self.method == 'top_n':
            if self.n is None:
                raise ValueError("n must be specified for top_n method")
            # Get the top n indices
            top_n = scores_clean.nlargest(self.n).index
            ranks = pd.Series(np.nan, index=scores_clean.index)
            ranks.loc[top_n] = range(1, self.n + 1)
        elif self.method == 'percentile':
            # Compute percentile rank (0-100)
            ranks = scores_clean.rank(pct=True) * 100
        else:
            raise ValueError(f"Unknown ranking method: {self.method}")
        result = pd.DataFrame({'score': scores_clean, 'rank': ranks})
        return result
