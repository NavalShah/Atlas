"""
Comprehensive Unit Tests for Alpaca Broker Integration
========================================================

Tests for AlpacaPaperBroker, AlpacaLiveBroker, and the broker factory.
All Alpaca SDK calls are mocked to avoid network dependencies.
"""
import os
import unittest
from unittest.mock import patch, MagicMock, call
from datetime import datetime

# Set environment variables before importing
os.environ["ALPACA_API_KEY"] = "test_key"
os.environ["ALPACA_SECRET_KEY"] = "test_secret"
os.environ["ALPACA_BASE_URL"] = "https://paper-api.alpaca.markets"

from atlas_quant.execution.broker_factory import get_broker
from atlas_quant.brokers import AlpacaPaperBroker, AlpacaLiveBroker
from atlas_quant.utilities.environment import get_alpaca_credentials


class TestAlpacaCredentials(unittest.TestCase):
    """Test environment variable loading."""
    
    def test_get_alpaca_credentials(self):
        """Test retrieving Alpaca credentials from environment."""
        creds = get_alpaca_credentials()
        self.assertEqual(creds["api_key"], "test_key")
        self.assertEqual(creds["secret_key"], "test_secret")


class TestBrokerFactory(unittest.TestCase):
    """Test the broker factory."""
    
    @patch.dict(os.environ, {"ALPACA_ENV": "paper"})
    def test_factory_returns_paper_broker(self):
        """Test that factory returns paper broker when ALPACA_ENV=paper."""
        broker = get_broker("paper")
        self.assertIsInstance(broker, AlpacaPaperBroker)
    
    @patch.dict(os.environ, {"ALPACA_ENV": "live"})
    def test_factory_returns_live_broker(self):
        """Test that factory returns live broker when ALPACA_ENV=live."""
        broker = get_broker("live")
        self.assertIsInstance(broker, AlpacaLiveBroker)
    
    def test_factory_raises_on_invalid_env(self):
        """Test that factory raises on unsupported environment."""
        with self.assertRaises(ValueError):
            get_broker("invalid_env")


class TestAlpacaBrokerConnection(unittest.TestCase):
    """Test broker connection management."""
    
    @patch('atlas_quant.brokers.base.TradingClient')
    def test_connect_success(self, mock_trading_client_class):
        """Test successful connection to broker."""
        mock_client = MagicMock()
        mock_client.get_account.return_value = MagicMock()
        mock_trading_client_class.return_value = mock_client
        
        broker = AlpacaPaperBroker(api_key="test_key", secret_key="test_secret")
        result = broker.connect()
        
        self.assertTrue(result)
        self.assertTrue(broker._connected)


class TestAlpacaBrokerAccountMethods(unittest.TestCase):
    """Test account-related broker methods."""
    
    @patch('atlas_quant.brokers.base.TradingClient')
    def setUp(self, mock_trading_client_class):
        """Set up test fixtures."""
        self.mock_client = MagicMock()
        self.mock_client.get_account.return_value = MagicMock()
        mock_trading_client_class.return_value = self.mock_client
        
        self.broker = AlpacaPaperBroker(api_key="test_key", secret_key="test_secret")
        self.broker.connect()
    
    def test_get_account(self):
        """Test getting account information."""
        mock_account = MagicMock()
        mock_account.account_number = "ACC123"
        self.mock_client.get_account.return_value = mock_account
        
        result = self.broker.get_account()
        self.mock_client.get_account.assert_called()
    
    def test_is_market_open(self):
        """Test checking if market is open."""
        mock_clock = MagicMock()
        mock_clock.is_open = True
        self.mock_client.get_clock.return_value = mock_clock
        
        result = self.broker.is_market_open()
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
