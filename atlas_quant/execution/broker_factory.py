"""
Broker Factory
==============

Factory for creating broker instances based on environment configuration.
"""
import os
from typing import Optional

from atlas_quant.utilities.environment import get_alpaca_credentials
from atlas_quant.brokers import AlpacaPaperBroker, AlpacaLiveBroker


def get_broker(env: Optional[str] = None) -> object:
    """
    Get a broker instance based on the environment.
    
    Args:
        env: The environment ('paper', 'live', etc.). If None, reads from ALPACA_ENV environment variable.
             Defaults to 'paper' if not set.
             
    Returns:
        An instance of a broker class (AlpacaPaperBroker or AlpacaLiveBroker).
        
    Raises:
        ValueError: If the environment is not supported.
    """
    if env is None:
        env = os.getenv("ALPACA_ENV", "paper").lower()
    
    # Get credentials from environment
    credentials = get_alpaca_credentials()
    api_key = credentials["api_key"]
    secret_key = credentials["secret_key"]
    
    if env == "paper":
        return AlpacaPaperBroker(api_key=api_key, secret_key=secret_key)
    elif env == "live":
        return AlpacaLiveBroker(api_key=api_key, secret_key=secret_key)
    else:
        raise ValueError(f"Unsupported environment: {env}. Supported values are 'paper' and 'live'.")
