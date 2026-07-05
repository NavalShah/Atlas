"""
Environment Utilities
====================

Utilities for loading environment variables and configuration.
"""
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()  # takes environment variables from .env.


def get_env(key: str, default: Optional[str] = None) -> str:
    """Get environment variable or return default."""
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Environment variable {key} is not set")
    return value


def get_alpaca_credentials() -> dict:
    """Get Alpaca API credentials from environment variables."""
    return {
        "api_key": get_env("ALPACA_API_KEY"),
        "secret_key": get_env("ALPACA_SECRET_KEY"),
    }
