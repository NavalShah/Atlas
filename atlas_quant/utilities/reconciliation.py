"""
Portfolio Reconciliation
========================

Utilities for comparing current broker positions with target portfolio
and generating required orders to rebalance.
"""
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    """Represents a single trade to execute."""
    symbol: str
    quantity: float
    side: str  # 'buy' or 'sell'
    order_type: str = "market"
    time_in_force: str = "day"
    
    def to_order_dict(self) -> Dict[str, Any]:
        """Convert trade to order dictionary format for broker submission."""
        return {
            "symbol": self.symbol,
            "qty": abs(self.quantity),
            "side": self.side,
            "type": self.order_type,
            "time_in_force": self.time_in_force
        }


class PortfolioReconciler:
    """
    Reconciles target portfolio with current positions and generates trades.
    """
    
    def __init__(self, tolerance: float = 0.01):
        """
        Initialize the reconciler.
        
        Args:
            tolerance: Minimum quantity difference to trigger a trade (to avoid dust trades)
        """
        self.tolerance = tolerance
    
    def reconcile(
        self,
        current_positions: Dict[str, float],
        target_positions: Dict[str, float],
        prices: Dict[str, float] = None
    ) -> Tuple[List[Trade], Dict[str, Any]]:
        """
        Reconcile current positions with target and generate trades.
        
        Args:
            current_positions: Dict mapping symbol to current quantity
            target_positions: Dict mapping symbol to target quantity
            prices: Optional dict mapping symbol to current price (for reporting)
        
        Returns:
            Tuple of (list of Trade objects, reconciliation summary dict)
        """
        trades = []
        summary = {
            "total_trades": 0,
            "buy_trades": 0,
            "sell_trades": 0,
            "symbols_affected": [],
            "details": {}
        }
        
        # Get all symbols involved
        all_symbols = set(list(current_positions.keys()) + list(target_positions.keys()))
        
        for symbol in sorted(all_symbols):
            current_qty = current_positions.get(symbol, 0.0)
            target_qty = target_positions.get(symbol, 0.0)
            
            # Calculate required quantity change
            quantity_diff = target_qty - current_qty
            
            # Only trade if difference exceeds tolerance
            if abs(quantity_diff) <= self.tolerance:
                continue
            
            # Determine trade side and quantity
            if quantity_diff > 0:
                side = "buy"
                qty = quantity_diff
            else:
                side = "sell"
                qty = abs(quantity_diff)
            
            # Create trade
            trade = Trade(
                symbol=symbol,
                quantity=qty,
                side=side
            )
            trades.append(trade)
            
            # Update summary
            summary["total_trades"] += 1
            if side == "buy":
                summary["buy_trades"] += 1
            else:
                summary["sell_trades"] += 1
            summary["symbols_affected"].append(symbol)
            
            # Add details for this symbol
            summary["details"][symbol] = {
                "current": current_qty,
                "target": target_qty,
                "change": quantity_diff,
                "side": side,
                "quantity": qty,
                "price": prices.get(symbol) if prices else None
            }
        
        logger.info(f"Reconciliation complete: {summary['total_trades']} trades generated")
        return trades, summary
    
    def get_current_vs_target_table(
        self,
        current_positions: Dict[str, float],
        target_positions: Dict[str, float],
        prices: Dict[str, float] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate a table of current vs target positions for display.
        
        Args:
            current_positions: Current positions
            target_positions: Target positions
            prices: Optional current prices
            
        Returns:
            List of dicts with position comparison data
        """
        all_symbols = set(list(current_positions.keys()) + list(target_positions.keys()))
        rows = []
        
        for symbol in sorted(all_symbols):
            current = current_positions.get(symbol, 0.0)
            target = target_positions.get(symbol, 0.0)
            price = prices.get(symbol) if prices else None
            
            row = {
                "symbol": symbol,
                "current": current,
                "target": target,
                "difference": target - current,
                "price": price,
                "current_value": current * price if price else None,
                "target_value": target * price if price else None
            }
            rows.append(row)
        
        return rows


def convert_trades_to_orders(trades: List[Trade]) -> List[Dict[str, Any]]:
    """
    Convert Trade objects to order dictionaries for broker submission.
    
    Args:
        trades: List of Trade objects
        
    Returns:
        List of order dictionaries
    """
    return [trade.to_order_dict() for trade in trades]
