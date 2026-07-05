"""
Unit Test for Alpaca Broker
==========================
"""
import os
import unittest
from unittest.mock import patch, MagicMock

# Set environment variables
os.environ["ALPACA_API_KEY"] = "test_key"
os.environ["ALPACA_SECRET_KEY"] = "test_secret"

from alpaca.trading.client import TradingClient
from atlas_quant.brokers.alpaca import AlpacaPaperBroker


class TestAlpacaPaperBroker(unittest.TestCase):
    @patch('alpaca.trading.client.TradingClient')
    def setUp(self, mock_trading_client_class):
        """Set up test fixtures."""
        self.mock_trading_client = MagicMock()
        self.mock_trading_client_class.return_value = self.mock_trading_client
        
        self.broker = AlpacaPaperBroker(api_key="test_key", secret_key="test_secret")
        # Manually set the client since our __init__ doesn't actually set it in the mock
        self.broker._client = self.mock_trading_client
        self.broker._connected = True
        self.broker._connected = True
    
    def test_get_account(self):
        """Test getting account information."""
        # Mock the account response
        mock_account = MagicMock()
        mock_account.account_number = "ACC123"
        mock_account.cash = "10000.00"
        mock_account.buying_power = "20000.00"
        mock_account.portfolio_value = "30000.00"
        self.mock_trading_client.get_account.return_value = mock_account
        
        result = self.broker.get_account()
        
        self.assertEqual(result["account_number"], "ACC123")
        self.assertEqual(float(result["cash"]), 10000.00)
        self.assertEqual(float(result["buying_power"]), 20000.00)
        self.assertEqual(float(result["portfolio_value"]), 30000.00)
    
    def test_is_market_open(self):
        """Test checking if market is open."""
        # Mock the clock response
        mock_clock = MagicMock()
        mock_clock.is_open = True
        self.mock_trading_client.get_clock.return_value = mock_clock
        
        result = self.broker.is_market_open()
        
        self.assertTrue(result)
        self.mock_trading_client.get_clock.assert_called_once()
    
    def test_get_market_clock(self):
        """Test getting market clock."""
        # Mock the clock response
        mock_clock = MagicMock()
        mock_clock.is_open = True
        mock_clock.next_open = "2023-01-02T09:30:00-05:00"
        mock_clock.next_close = "2023-01-02T16:00:00-05:00"
        self.mock_trading_client.get_clock.return_value = mock_clock
        
        result = self.broker.get_market_clock()
        
        self.assertEqual(result["is_open"], True)
        self.assertEqual(result["next_open"], "2023-01-02T09:30:00-05:00")
        self.assertEqual(result["next_close"], "2023-01-02T16:00:00-05:00")
    
    def test_get_assets(self):
        """Test getting assets."""
        # Mock the assets response
        mock_asset1 = MagicMock()
        mock_asset1.symbol = "AAPL"
        mock_asset1.name = "Apple Inc."
        mock_asset1.exchange = "NASDAQ"
        mock_asset1.status = "active"
        mock_asset1.tradable = True
        
        mock_asset2 = MagicMock()
        mock_asset2.symbol = "MSFT"
        mock_asset2.name = "Microsoft Corporation"
        mock_asset2.exchange = "NASDAQ"
        mock_asset2.status = "active"
        mock_asset2.tradable = True
        
        self.mock_trading_client.get_all_assets.return_value = [mock_asset1, mock_asset2]
        
        result = self.broker.get_assets()
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["symbol"], "AAPL")
        self.assertEqual(result[0]["name"], "Apple Inc.")
        self.assertEqual(result[1]["symbol"], "MSFT")
        self.assertEqual(result[1]["name"], "Microsoft Corporation")


if __name__ == '__main__':
    unittest.main()
