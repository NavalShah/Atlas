"""Returns
=========

Calculates various return metrics.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class ReturnsAnalyzer:
    """
    Analyzes return patterns and characteristics.
    """
    
    def __init__(self):
        """
        Initialize the returns analyzer.
        """
        pass
    
    def calculate_simple_returns(self, 
                                prices: pd.Series) -> pd.Series:
        """
        Calculate simple (arithmetic) returns.
        """
        return prices.pct_change()
    
    def calculate_log_returns(self, 
                             prices: pd.Series) -> pd.Series:
        """
        Calculate logarithmic returns.
        """
        return np.log(prices / prices.shift(1))
    
    def calculate_total_return(self, 
                              prices: pd.Series) -> float:
        """
        Calculate total return over the entire period.
        """
        if len(prices) < 2:
            return 0.0
        return (prices.iloc[-1] / prices.iloc[0]) - 1
    
    def calculate_period_returns(self, 
                                returns: pd.Series,
                                period: str = "M") -> pd.Series:
        """
        Calculate returns aggregated by period (daily, weekly, monthly, etc.).
        """
        # Resample to specified period and calculate compound return
        return (1 + returns).resample(period).prod() - 1
    
    def calculate_win_rate(self, 
                          returns: pd.Series) -> float:
        """
        Calculate the percentage of positive returns.
        """
        if len(returns) == 0:
            return 0.0
        positive_returns = (returns > 0).sum()
        return positive_returns / len(returns)
    
    def calculate_avg_win_loss(self, 
                              returns: pd.Series) -> Dict[str, float]:
        """
        Calculate average winning and losing trades.
        """
        wins = returns[returns > 0]
        losses = returns[returns < 0]
        
        avg_win = wins.mean() if len(wins) > 0 else 0.0
        avg_loss = abs(losses.mean()) if len(losses) > 0 else 0.0
        
        # Handle division by zero
        if avg_loss > 0:
            win_loss_ratio = avg_win / avg_loss
        else:
            # Use a large number instead of infinity
            win_loss_ratio = 999999.0
        
        return {
            "average_win": avg_win,
            "average_loss": avg_loss,
            "win_loss_ratio": win_loss_ratio
        }

