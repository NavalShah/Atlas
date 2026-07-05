"""
Alpaca Broker Base
==================

Base class for Alpaca broker implementations.
"""
from abc import ABC
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime

# Import the IBroker interface from the execution module
from atlas_quant.execution.broker import IBroker

# Import Alpaca SDK components
try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
    from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, StopLimitOrderRequest, GetOrdersRequest
    from alpaca.common.exceptions import APIError
except ImportError:
    # For development purposes, we'll raise a more informative error later
    TradingClient = None


class AlpacaBrokerBase(IBroker, ABC):
    """
    Base class for Alpaca broker implementations.
    Handles common functionality for connecting to Alpaca API.
    """
    
    def __init__(self, api_key: str, secret_key: str, base_url: str):
        """
        Initialize the Alpaca broker base.
        
        Args:
            api_key: Alpaca API key
            secret_key: Alpaca secret key
            base_url: Base URL for the API (paper or live)
        """
        if TradingClient is None:
            raise ImportError(
                "The alpaca-py package is not installed. "
                "Please install it using: pip install alpaca-py"
            )
        
        self._api_key = api_key
        self._secret_key = secret_key
        self._base_url = base_url
        self._client = None
        self._connected = False
    
    def connect(self) -> bool:
        """
        Connect to the Alpaca API by initializing the trading client.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self._client = TradingClient(
                api_key=self._api_key,
                secret_key=self._secret_key,
                paper=(self._base_url == "https://paper-api.alpaca.markets")
            )
            # Test the connection by getting the account
            self._client.get_account()
            self._connected = True
            return True
        except Exception as e:
            # Log the error (in a real implementation, use logging)
            print(f"Failed to connect to Alpaca: {e}")
            self._connected = False
            return False
    
    def disconnect(self) -> None:
        """
        Disconnect from the Alpaca API.
        Note: The TradingClient does not have an explicit disconnect method,
        so we just set the client to None and mark as disconnected.
        """
        self._client = None
        self._connected = False
    
    def _ensure_connected(self):
        """
        Helper method to ensure the client is connected.
        Raises an exception if not connected.
        """
        if not self._connected or self._client is None:
            raise RuntimeError("Broker is not connected. Call connect() first.")
    
    # IBroker interface methods
    def submit_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit an order to Alpaca.
        
        Args:
            order: Order details dictionary. Expected keys:
                - symbol: str
                - qty: float or int
                - side: 'buy' or 'sell'
                - type: 'market', 'limit', 'stop', 'stop_limit'
                - time_in_force: 'day', 'gtc', 'opg', 'cls', 'ioc', 'fok'
                - limit_price: float (required for limit and stop_limit)
                - stop_price: float (required for stop and stop_limit)
                
        Returns:
            Dict containing order submission details including order ID
        """
        self._ensure_connected()
        
        # Map order dictionary to Alpaca order request
        side = OrderSide.BUY if order["side"].lower() == "buy" else OrderSide.SELL
        
        # Determine time_in_force
        tif_str = order.get("time_in_force", "day").upper()
        try:
            time_in_force = TimeInForce[tif_str]
        except KeyError:
            raise ValueError(f"Invalid time_in_force: {tif_str}")
        
        # Create the appropriate order request based on type
        order_type = order.get("type", "market").lower()
        if order_type == "market":
            request = MarketOrderRequest(
                symbol=order["symbol"],
                qty=order["qty"],
                side=side,
                time_in_force=time_in_force
            )
        elif order_type == "limit":
            if "limit_price" not in order:
                raise ValueError("limit_price is required for limit orders")
            request = LimitOrderRequest(
                symbol=order["symbol"],
                qty=order["qty"],
                side=side,
                time_in_force=time_in_force,
                limit_price=order["limit_price"]
            )
        elif order_type == "stop":
            if "stop_price" not in order:
                raise ValueError("stop_price is required for stop orders")
            request = StopLimitOrderRequest(
                symbol=order["symbol"],
                qty=order["qty"],
                side=side,
                time_in_force=time_in_force,
                stop_price=order["stop_price"]
            )
        elif order_type == "stop_limit":
            if "stop_price" not in order or "limit_price" not in order:
                raise ValueError("stop_price and limit_price are required for stop_limit orders")
            request = StopLimitOrderRequest(
                symbol=order["symbol"],
                qty=order["qty"],
                side=side,
                time_in_force=time_in_force,
                stop_price=order["stop_price"],
                limit_price=order["limit_price"]
            )
        else:
            raise ValueError(f"Unsupported order type: {order_type}")
        
        # Submit the order
        try:
            response = self._client.submit_order(order_data=request)
            return dict(response)
        except APIError as e:
            # Re-raise as a more generic exception or handle as needed
            raise RuntimeError(f"Failed to submit order: {e}")
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order by its ID.
        
        Args:
            order_id: ID of the order to cancel
            
        Returns:
            bool: True if cancellation successful, False otherwise
        """
        self._ensure_connected()
        try:
            self._client.cancel_order(order_id)
            return True
        except Exception:
            return False
    
    def replace_order(self, order_id: str, new_order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replace an existing order with a new one.
        
        Args:
            order_id: ID of the order to replace
            new_order: New order details (same format as for submit_order)
            
        Returns:
            Dict containing replacement order details
        """
        self._ensure_connected()
        # Note: Alpaca API does not have a direct replace order endpoint.
        # We implement it as cancel then submit new order.
        # This is not atomic, but it's the best we can do with the current API.
        if not self.cancel_order(order_id):
            raise RuntimeError(f"Failed to cancel order {order_id} for replacement")
        return self.submit_order(new_order)
    
    def get_positions(self) -> Dict[str, Any]:
        """
        Get current positions from Alpaca.
        
        Returns:
            Dictionary of positions keyed by symbol
        """
        self._ensure_connected()
        positions = self._client.get_all_positions()
        return {pos.symbol: dict(pos) for pos in positions}
    
    def get_account(self) -> Dict[str, Any]:
        """
        Get account information from Alpaca.
        
        Returns:
            Dictionary containing account details
        """
        self._ensure_connected()
        account = self._client.get_account()
        return dict(account)
    
    def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get orders from Alpaca, optionally filtered by status.
        
        Args:
            status: Filter by order status (e.g., 'open', 'closed')
            
        Returns:
            List of order dictionaries
        """
        self._ensure_connected()
        params = {}
        if status:
            try:
                status_enum = QueryOrderStatus[status.upper()]
                params["status"] = status_enum
            except KeyError:
                raise ValueError(f"Invalid order status: {status}")
        
        request_params = GetOrdersRequest(**params)
        orders = self._client.get_orders(filter=request_params)
        return [dict(order) for order in orders]
    
    def get_market_data(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Get market data for specified symbols.
        Note: This method requires a separate data client which is not initialized here.
        For a complete implementation, you would need to initialize a StockHistoricalDataClient
        or CryptoHistoricalDataClient depending on the asset type.
        This placeholder returns empty DataFrames.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary mapping symbol to DataFrame of market data
        """
        # Placeholder implementation
        return {symbol: pd.DataFrame() for symbol in symbols}
    
    def is_market_open(self) -> bool:
        """
        Check if the market is currently open.
        
        Returns:
            bool: True if market is open, False otherwise
        """
        self._ensure_connected()
        clock = self._client.get_clock()
        return clock.is_open
    
    # Additional methods required by the specification (not in IBroker)
    def get_market_clock(self) -> Dict[str, Any]:
        """
        Get the current market clock from Alpaca.
        
        Returns:
            Dictionary containing clock details
        """
        self._ensure_connected()
        clock = self._client.get_clock()
        return dict(clock)
    
    def get_assets(self) -> List[Dict[str, Any]]:
        """
        Get all assets available on Alpaca.
        
        Returns:
            List of asset dictionaries
        """
        self._ensure_connected()
        assets = self._client.get_all_assets()
        return [dict(asset) for asset in assets]
