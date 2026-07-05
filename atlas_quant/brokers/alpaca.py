"""
Alpaca Broker Implementation
============================

Concrete implementations of Alpaca broker for paper and live trading.
"""
import os
from typing import Optional

from .base import AlpacaBrokerBase


class AlpacaPaperBroker(AlpacaBrokerBase):
    """
    Alpaca broker for paper trading.
    """
    
    def __init__(self, api_key: str, secret_key: str, base_url: Optional[str] = None):
        """
        Initialize the Alpaca paper broker.
        
        Args:
            api_key: Alpaca API key
            secret_key: Alpaca secret key
            base_url: Base URL for the API. If None, uses the paper URL from environment or default.
        """
        if base_url is None:
            # Use the environment variable or default to paper URL
            base_url = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
        super().__init__(api_key, secret_key, base_url)


class AlpacaLiveBroker(AlpacaBrokerBase):
    """
    Alpaca broker for live trading.
    """
    
    def __init__(self, api_key: str, secret_key: str, base_url: Optional[str] = None):
        """
        Initialize the Alpaca live broker.
        
        Args:
            api_key: Alpaca API key
            secret_key: Alpaca secret key
            base_url: Base URL for the API. If None, uses the live URL from environment or default.
        """
        if base_url is None:
            # Use the environment variable or default to live URL
            base_url = os.getenv("ALPACA_BASE_URL", "https://api.alpaca.markets")
        super().__init__(api_key, secret_key, base_url)
