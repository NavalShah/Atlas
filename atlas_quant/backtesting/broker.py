"""Simulated Broker
=================

Handles order execution simulation.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class SimulatedBroker:
    """
    Simulated broker for order execution.
    Supports market orders with next-open execution.
    """
    
    def __init__(self, 
                 commission: float = 1.0,
                 slippage: float = 0.001):
        """
        Initialize the simulated broker.
        """
        self.commission = commission
        self.slippage = slippage
    
    def execute_orders(self, 
                      orders: List[Dict],
                      market_data: Dict[str, pd.DataFrame],
                      current_date) -> List[Dict]:
        """
        Execute orders with simulated broker.
        """
        executions = []
        
        for order in orders:
            symbol = order["symbol"]
            if symbol not in market_data:
                continue
                
            # Get execution price (simplified)
            price_data = market_data[symbol]
            if len(price_data) == 0:
                continue
                
            # Use close price as fill price (simplified)
            fill_price = price_data["Close"].iloc[-1]
            
            # Apply slippage
            if order["action"] == "BUY":
                fill_price *= (1 + self.slippage)
            else:  # SELL
                fill_price *= (1 - self.slippage)
            
            # Calculate shares (simplified - assuming weight-based ordering)
            # In reality, this would need portfolio value
            shares = 100  # Placeholder
            
            execution = {
                "symbol": symbol,
                "date": current_date,
                "action": order["action"],
                "quantity": shares,
                "price": fill_price,
                "commission": self.commission,
                "slippage": self.slippage * fill_price * shares,
                "total_cost": shares * fill_price + self.commission,
                "order_id": f"{symbol}_{len(executions)}"
            }
            
            executions.append(execution)
        
        return executions

