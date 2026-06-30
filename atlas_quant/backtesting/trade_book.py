"""Trade Book
============

Records all executed trades for analysis and reporting.
"""
import pandas as pd
from typing import Dict, List, Any
import logging
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class TradeRecord:
    """
    Represents a single trade execution.
    """
    trade_id: str
    timestamp: datetime
    symbol: str
    action: str  # BUY or SELL
    quantity: float
    price: float
    commission: float
    slippage: float
    total_cost: float
    strategy: str = ""
    reason: str = ""

class TradeBook:
    """
    Records and manages all executed trades.
    """
    
    def __init__(self):
        """
        Initialize the trade book.
        """
        self.trades: List[TradeRecord] = []
        self._trade_counter = 0
    
    def add_trade(self, 
                  execution: Dict[str, Any],
                  strategy: str = "",
                  reason: str = "") -> TradeRecord:
        """
        Add a trade to the book.
        """
        self._trade_counter += 1
        trade_id = f"TRADE_{self._trade_counter:06d}"
        
        trade = TradeRecord(
            trade_id=trade_id,
            timestamp=execution.get("date", datetime.now()),
            symbol=execution["symbol"],
            action=execution["action"],
            quantity=execution["quantity"],
            price=execution["price"],
            commission=execution.get("commission", 0.0),
            slippage=execution.get("slippage", 0.0),
            total_cost=execution.get("total_cost", 0.0),
            strategy=strategy,
            reason=reason
        )
        
        self.trades.append(trade)
        return trade
    
    def get_trades(self, 
                   symbol: str = None,
                   start_date: datetime = None,
                   end_date: datetime = None) -> List[TradeRecord]:
        """
        Get trades filtered by symbol and/or date range.
        """
        filtered_trades = self.trades
        
        if symbol:
            filtered_trades = [t for t in filtered_trades if t.symbol == symbol]
        
        if start_date:
            filtered_trades = [t for t in filtered_trades if t.timestamp >= start_date]
        
        if end_date:
            filtered_trades = [t for t in filtered_trades if t.timestamp <= end_date]
        
        return filtered_trades
    
    def get_trade_count(self) -> int:
        """
        Get total number of trades recorded.
        """
        return len(self.trades)
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert trades to a pandas DataFrame for analysis.
        """
        if not self.trades:
            return pd.DataFrame()
        
        data = []
        for trade in self.trades:
            data.append({
                "trade_id": trade.trade_id,
                "timestamp": trade.timestamp,
                "symbol": trade.symbol,
                "action": trade.action,
                "quantity": trade.quantity,
                "price": trade.price,
                "commission": trade.commission,
                "slippage": trade.slippage,
                "total_cost": trade.total_cost,
                "strategy": trade.strategy,
                "reason": trade.reason
            })
        
        return pd.DataFrame(data)

