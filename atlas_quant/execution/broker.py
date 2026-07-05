"""
Broker Interface
================

Abstract base class defining the broker interface for Atlas Quant.
All broker implementations must implement this interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import pandas as pd


class IBroker(ABC):
    """
    Abstract base class for broker implementations.
    
    Defines the interface that all brokers (paper, live, simulation) must implement.
    This ensures consistent interactions with different broker backends.
    """
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to the broker.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """
        Disconnect from the broker.
        """
        pass
    
    @abstractmethod
    def submit_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit an order to the broker.
        
        Args:
            order: Order details dictionary containing:
                - symbol: str (e.g., 'AAPL')
                - qty: float or int (number of shares)
                - side: str ('buy' or 'sell')
                - type: str ('market', 'limit', 'stop', 'stop_limit')
                - time_in_force: str (optional, defaults to 'day')
                - limit_price: float (required for limit and stop_limit orders)
                - stop_price: float (required for stop and stop_limit orders)
        
        Returns:
            Dict containing order submission response with at minimum:
                - id or order_id: unique identifier for the order
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an open order.
        
        Args:
            order_id: Unique identifier of the order to cancel
            
        Returns:
            bool: True if cancellation successful, False otherwise
        """
        pass
    
    @abstractmethod
    def replace_order(self, order_id: str, new_order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replace an existing order with a new one.
        
        Args:
            order_id: ID of the order to replace
            new_order: New order details (same format as submit_order)
            
        Returns:
            Dict containing the new order details
        """
        pass
    
    @abstractmethod
    def get_positions(self) -> Dict[str, Any]:
        """
        Get current open positions.
        
        Returns:
            Dict mapping symbol to position details:
                {
                    'AAPL': {
                        'symbol': 'AAPL',
                        'qty': 100.0,
                        'avg_fill_price': 150.25,
                        'side': 'long',
                        ...
                    },
                    ...
                }
        """
        pass
    
    @abstractmethod
    def get_account(self) -> Dict[str, Any]:
        """
        Get account information.
        
        Returns:
            Dict containing account details such as:
                - buying_power: available funds for trading
                - cash: current cash balance
                - portfolio_value: total account value
                - equity: equity in the account
        """
        pass
    
    @abstractmethod
    def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get orders, optionally filtered by status.
        
        Args:
            status: Optional filter for order status ('open', 'closed', 'filled', 'cancelled', etc.)
            
        Returns:
            List of order dictionaries
        """
        pass
    
    @abstractmethod
    def is_market_open(self) -> bool:
        """
        Check if the market is currently open.
        
        Returns:
            bool: True if market is open, False otherwise
        """
        pass
    
    @abstractmethod
    def get_market_clock(self) -> Dict[str, Any]:
        """
        Get the current market clock information.
        
        Returns:
            Dict containing market clock details such as:
                - is_open: bool
                - timestamp: current timestamp
                - next_open: when market opens next
                - next_close: when market closes next
        """
        pass
    
    @abstractmethod
    def get_assets(self) -> List[Dict[str, Any]]:
        """
        Get list of available assets/symbols.
        
        Returns:
            List of asset dictionaries containing symbol and details
        """
        pass
