"""Portfolio Tracker
==================

Tracks portfolio positions, cash, and performance.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class PortfolioTracker:
    """
    Tracks portfolio positions, cash, and performance metrics.
    """
    
    def __init__(self, initial_capital: float = 100000):
        """
        Initialize the portfolio tracker.
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}  # symbol -> {"shares": int, "avg_price": float}
        self.transaction_history = []
        self.daily_snapshots = []
    
    def update_from_execution(self, executions: List[Dict], current_date) -> None:
        """
        Update portfolio based on executed trades.
        """
        for execution in executions:
            symbol = execution["symbol"]
            action = execution["action"]
            quantity = execution["quantity"]
            price = execution["price"]
            commission = execution["commission"]
            
            # Update cash
            if action == "BUY":
                cost = quantity * price + commission
                self.cash -= cost
            else:  # SELL
                proceeds = quantity * price - commission
                self.cash += proceeds
            
            # Update positions
            if symbol not in self.positions:
                self.positions[symbol] = {"shares": 0, "avg_price": 0.0}
            
            if action == "BUY":
                # Add to position
                old_shares = self.positions[symbol]["shares"]
                old_avg_price = self.positions[symbol]["avg_price"]
                
                new_shares = old_shares + quantity
                if new_shares != 0:
                    new_avg_price = (old_shares * old_avg_price + quantity * price) / new_shares
                else:
                    new_avg_price = 0.0
                
                self.positions[symbol] = {
                    "shares": new_shares,
                    "avg_price": new_avg_price
                }
            else:  # SELL
                # Reduce position
                self.positions[symbol]["shares"] -= quantity
                # If position is closed, reset average price
                if self.positions[symbol]["shares"] == 0:
                    self.positions[symbol]["avg_price"] = 0.0
            
            # Record transaction
            self.transaction_history.append({
                "date": current_date,
                "symbol": symbol,
                "action": action,
                "quantity": quantity,
                "price": price,
                "commission": commission,
                "shares_after": self.positions[symbol]["shares"]
            })
    
    def update_market_values(self, market_data: Dict[str, pd.DataFrame], current_date) -> None:
        """
        Update position values based on current market prices.
        """
        # This would typically be called after market data is available
        # For now, we just note that prices have changed
        pass
    
    def get_current_weights(self) -> Dict[str, float]:
        """
        Get current portfolio weights.
        """
        # Simplified implementation
        total_value = self.get_total_value()
        weights = {}
        
        if total_value > 0:
            for symbol, position in self.positions.items():
                if position["shares"] > 0:
                    # In a real implementation, we would multiply shares by current price
                    # For now, we use a placeholder
                    weights[symbol] = 0.0
            
            # Cash weight
            weights["CASH"] = self.cash / total_value if total_value > 0 else 1.0
        
        return weights
    
    def get_total_value(self) -> float:
        """
        Calculate total portfolio value.
        """
        # Simplified - in reality would use current market prices
        return self.cash  # Placeholder
    
    def get_snapshot(self, current_date) -> Dict[str, Any]:
        """
        Get a snapshot of the portfolio at the current date.
        """
        return {
            "date": current_date,
            "cash": self.cash,
            "positions": self.positions.copy(),
            "total_value": self.get_total_value()
        }

