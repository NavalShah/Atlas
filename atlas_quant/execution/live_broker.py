"""Live Broker
==============

Abstract base class for live broker implementations.
Specific broker implementations (e.g., Alpaca, Interactive Brokers) should inherit from this class.
"""
from .broker import IBroker
from abc import abstractmethod

class LiveBroker(IBroker):
    """
    Base class for live broker implementations.
    This class defines the interface for live brokers and should be subclassed
    for specific brokerages (e.g., AlpacaBroker, IBKRBroker).
    """
    
    def __init__(self):
        """Initialize the live broker."""
        # Initialize connection state and other common attributes
        self._connected = False
        # Subclasses should initialize their specific API clients here
    
    def connect(self) -> bool:
        """
        Connect to the broker.
        This method should be implemented by subclasses to establish a connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement connect()")
    
    def disconnect(self) -> None:
        """
        Disconnect from the broker.
        This method should be implemented by subclasses to close the connection.
        """
        raise NotImplementedError("Subclasses must implement disconnect()")
    
    # The following methods are inherited from IBroker and must be implemented by subclasses:
    # submit_order, cancel_order, replace_order, get_positions, get_account,
    # get_orders, get_market_data, is_market_open
