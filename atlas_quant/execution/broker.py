"""Broker Interface
===================

Defines the IBroker interface that all broker implementations must follow.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime

class IBroker(ABC):
    """
    Abstract base class for broker implementations.
    All brokers must implement these methods.
    """
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to the broker.
        
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
            order: Order details dictionary
            
        Returns:
            Dict containing order submission details including order ID
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order.
        
        Args:
            order_id: ID of the order to cancel
            
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
            new_order: New order details
            
        Returns:
            Dict containing replacement order details
        """
        pass
    
    @abstractmethod
    def get_positions(self) -> Dict[str, Any]:
        """
        Get current positions.
        
        Returns:
            Dictionary of positions keyed by symbol
        """
        pass
    
    @abstractmethod
    def get_account(self) -> Dict[str, Any]:
        """
        Get account information.
        
        Returns:
            Dictionary containing account details
        """
        pass
    
    @abstractmethod
    def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get orders, optionally filtered by status.
        
        Args:
            status: Filter by order status (e.g., 'open', 'filled', 'cancelled')
            
        Returns:
            List of order dictionaries
        """
        pass
    
    @abstractmethod
    def get_market_data(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Get market data for specified symbols.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary mapping symbol to DataFrame of market data
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
