"""Paper Broker
==============

Implements a paper trading broker for simulated live trading.
"""
from .broker import IBroker
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

class PaperBroker(IBroker):
    """
    Paper broker that simulates order execution without real money.
    """
    
    def __init__(self):
        """Initialize the paper broker."""
        self.connected = False
        self.orders = {}  # order_id -> order details
        self.positions = {}  # symbol -> {quantity, average_price}
        self.account = {
            "cash": 100000.0,  # Starting paper money
            "buying_power": 100000.0,
            "equity": 100000.0,
            "last_equity": 100000.0
        }
        # Simple price store for simulation
        self.price_data = {}  # symbol -> DataFrame with historical data
    
    def connect(self) -> bool:
        """
        Connect to the paper trading environment.
        In this simulation, we just set connected to True.
        """
        self.connected = True
        logger.info("Paper broker connected.")
        return True
    
    def disconnect(self) -> None:
        """
        Disconnect from the paper trading environment.
        """
        self.connected = False
        logger.info("Paper broker disconnected.")
    
    def submit_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit an order to be simulated.
        
        Args:
            order: Dictionary containing order details (symbol, quantity, side, order_type, etc.)
            
        Returns:
            Dictionary with order submission details including generated order ID
        """
        if not self.connected:
            raise Exception("Broker not connected")
        
        # Generate an order ID
        order_id = str(uuid.uuid4())
        
        # Store the order
        self.orders[order_id] = {
            "order_id": order_id,
            "symbol": order["symbol"],
            "quantity": order["quantity"],
            "side": order["side"],  # "buy" or "sell"
            "order_type": order.get("order_type", "market"),
            "status": "submitted",
            "timestamp": datetime.now(),
            "filled_quantity": 0,
            "average_fill_price": 0.0
        }
        
        # For market orders, we simulate immediate fill
        if order.get("order_type", "market").lower() == "market":
            self._fill_order(order_id)
        
        logger.info(f"Order submitted: {order_id} for {order['symbol']} {order['side']} {order['quantity']}")
        
        return {
            "order_id": order_id,
            "status": "submitted",
            "message": "Order submitted successfully"
        }
    
    def _fill_order(self, order_id: str) -> None:
        """
        Internal method to simulate filling an order.
        """
        order = self.orders[order_id]
        symbol = order["symbol"]
        quantity = order["quantity"]
        side = order["side"]
        
        # Get current price for the symbol (simplified)
        current_price = self._get_current_price(symbol)
        
        # Update order
        order["status"] = "filled"
        order["filled_quantity"] = quantity
        order["average_fill_price"] = current_price
        order["filled_timestamp"] = datetime.now()
        
        # Update position
        if symbol not in self.positions:
            self.positions[symbol] = {"quantity": 0, "average_price": 0.0}
        
        if side.lower() == "buy":
            # Buy increases position
            pos = self.positions[symbol]
            total_cost = pos["quantity"] * pos["average_price"] + quantity * current_price
            new_quantity = pos["quantity"] + quantity
            if new_quantity != 0:
                new_avg_price = total_cost / new_quantity
            else:
                new_avg_price = 0.0
            pos["quantity"] = new_quantity
            pos["average_price"] = new_avg_price
            
            # Update account
            cost = quantity * current_price
            self.account["cash"] -= cost
            self.account["buying_power"] -= cost
        else:  # sell
            # Sell decreases position
            pos = self.positions[symbol]
            # Calculate realized P&L (simplified)
            cost_basis = quantity * pos["average_price"]
            sale_proceeds = quantity * current_price
            realized_pl = sale_proceeds - cost_basis
            
            new_quantity = pos["quantity"] - quantity
            if new_quantity != 0:
                # Average price remains the same for remaining shares
                new_avg_price = pos["average_price"]
            else:
                new_avg_price = 0.0
            
            pos["quantity"] = new_quantity
            pos["average_price"] = new_avg_price
            
            # Update account
            proceeds = quantity * current_price
            self.account["cash"] += proceeds
            self.account["buying_power"] += proceeds
            # In a real system, we would also update realized P&L in account
        
        # Update equity
        self._update_equity()
        
        logger.info(f"Order filled: {order_id} at {current_price}")
    
    def _get_current_price(self, symbol: str) -> float:
        """
        Get the current price for a symbol.
        In a real implementation, this would come from a market data feed.
        For simulation, we return the last close price if available, or a default.
        """
        if symbol in self.price_data and len(self.price_data[symbol]) > 0:
            return self.price_data[symbol]["Close"].iloc[-1]
        else:
            # Return a default price if no data available
            return 100.0  # Placeholder
    
    def _update_equity(self) -> None:
        """
        Update account equity based on current positions and cash.
        """
        positions_value = 0.0
        for symbol, position in self.positions.items():
            current_price = self._get_current_price(symbol)
            positions_value += position["quantity"] * current_price
        
        self.account["equity"] = self.account["cash"] + positions_value
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order.
        
        Args:
            order_id: ID of the order to cancel
            
        Returns:
            bool: True if cancellation successful, False otherwise
        """
        if not self.connected:
            return False
        
        if order_id in self.orders:
            order = self.orders[order_id]
            if order["status"] in ["submitted", "pending"]:
                order["status"] = "cancelled"
                order["cancelled_timestamp"] = datetime.now()
                logger.info(f"Order cancelled: {order_id}")
                return True
        return False
    
    def replace_order(self, order_id: str, new_order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replace an existing order with a new one.
        
        Args:
            order_id: ID of the order to replace
            new_order: New order details
            
        Returns:
            Dict containing replacement order details
        """
        # Cancel the old order
        if self.cancel_order(order_id):
            # Submit the new order
            new_order_response = self.submit_order(new_order)
            # Link the new order to the old one for tracking
            new_order_response["replaced_order_id"] = order_id
            return new_order_response
        else:
            raise Exception(f"Could not replace order {order_id}: order not found or not cancellable")
    
    def get_positions(self) -> Dict[str, Any]:
        """
        Get current positions.
        
        Returns:
            Dictionary of positions keyed by symbol
        """
        return self.positions.copy()
    
    def get_account(self) -> Dict[str, Any]:
        """
        Get account information.
        
        Returns:
            Dictionary containing account details
        """
        return self.account.copy()
    
    def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get orders, optionally filtered by status.
        
        Args:
            status: Filter by order status (e.g., 'open', 'filled', 'cancelled')
            
        Returns:
            List of order dictionaries
        """
        if status is None:
            return list(self.orders.values())
        else:
            return [order for order in self.orders.values() if order["status"] == status]
    
    def get_market_data(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Get market data for specified symbols.
        In this paper broker, we return the stored price data.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary mapping symbol to DataFrame of market data
        """
        result = {}
        for symbol in symbols:
            if symbol in self.price_data:
                result[symbol] = self.price_data[symbol].copy()
            else:
                # Return an empty DataFrame with expected columns
                result[symbol] = pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])
        return result
    
    def update_market_data(self, symbol: str, data: pd.DataFrame) -> None:
        """
        Update the price data for a symbol.
        This would be called by a market data feed.
        
        Args:
            symbol: Stock symbol
            data: DataFrame with market data (must have columns: Open, High, Low, Close, Volume)
        """
        self.price_data[symbol] = data
    
    def is_market_open(self) -> bool:
        """
        Check if the market is currently open.
        For simplicity, we assume market is open during weekdays 9:30-16:00 EST.
        This is a simplified implementation.
        """
        now = datetime.now()
        # Simplified: assume market is open Monday-Friday 9:30-16:00
        if now.weekday() >= 5:  # Saturday=5, Sunday=6
            return False
        
        # Convert to time for comparison
        current_time = now.time()
        market_open = datetime.strptime("09:30", "%H:%M").time()
        market_close = datetime.strptime("16:00", "%H:%M").time()
        
        return market_open <= current_time <= market_close
