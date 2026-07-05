"""
Tests for Portfolio Reconciliation Module
==========================================
"""
import unittest
from atlas_quant.utilities.reconciliation import (
    Trade,
    PortfolioReconciler,
    convert_trades_to_orders
)


class TestTrade(unittest.TestCase):
    """Test Trade dataclass."""
    
    def test_trade_creation(self):
        """Test creating a trade."""
        trade = Trade(symbol="AAPL", quantity=100, side="buy")
        self.assertEqual(trade.symbol, "AAPL")
        self.assertEqual(trade.quantity, 100)
        self.assertEqual(trade.side, "buy")
    
    def test_trade_to_order_dict(self):
        """Test converting trade to order dictionary."""
        trade = Trade(symbol="AAPL", quantity=100, side="buy")
        order = trade.to_order_dict()
        
        self.assertEqual(order["symbol"], "AAPL")
        self.assertEqual(order["qty"], 100)
        self.assertEqual(order["side"], "buy")
        self.assertEqual(order["type"], "market")


class TestPortfolioReconciler(unittest.TestCase):
    """Test portfolio reconciliation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reconciler = PortfolioReconciler(tolerance=0.01)
    
    def test_reconcile_simple_buy(self):
        """Test reconciliation requiring a buy."""
        current = {"AAPL": 0}
        target = {"AAPL": 100}
        
        trades, summary = self.reconciler.reconcile(current, target)
        
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0].symbol, "AAPL")
        self.assertEqual(trades[0].quantity, 100)
        self.assertEqual(trades[0].side, "buy")
        self.assertEqual(summary["total_trades"], 1)
        self.assertEqual(summary["buy_trades"], 1)
        self.assertEqual(summary["sell_trades"], 0)
    
    def test_reconcile_simple_sell(self):
        """Test reconciliation requiring a sell."""
        current = {"AAPL": 100}
        target = {"AAPL": 50}
        
        trades, summary = self.reconciler.reconcile(current, target)
        
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0].symbol, "AAPL")
        self.assertEqual(trades[0].quantity, 50)
        self.assertEqual(trades[0].side, "sell")
    
    def test_reconcile_multiple_positions(self):
        """Test reconciliation with multiple positions."""
        current = {
            "AAPL": 100,
            "MSFT": 50,
            "GOOGL": 0
        }
        target = {
            "AAPL": 150,
            "MSFT": 25,
            "GOOGL": 100
        }
        
        trades, summary = self.reconciler.reconcile(current, target)
        
        self.assertEqual(len(trades), 3)
        self.assertEqual(summary["total_trades"], 3)
        self.assertEqual(summary["buy_trades"], 2)  # AAPL and GOOGL
        self.assertEqual(summary["sell_trades"], 1)  # MSFT
    
    def test_reconcile_with_tolerance(self):
        """Test that trades below tolerance are not generated."""
        current = {"AAPL": 100}
        target = {"AAPL": 100.005}  # Below 0.01 tolerance
        
        trades, summary = self.reconciler.reconcile(current, target)
        
        self.assertEqual(len(trades), 0)
    
    def test_reconcile_close_position(self):
        """Test reconciliation that closes a position."""
        current = {"AAPL": 100}
        target = {"AAPL": 0}
        
        trades, summary = self.reconciler.reconcile(current, target)
        
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0].side, "sell")
        self.assertEqual(trades[0].quantity, 100)
    
    def test_get_current_vs_target_table(self):
        """Test generating comparison table."""
        current = {"AAPL": 100}
        target = {"AAPL": 150}
        prices = {"AAPL": 150.0}
        
        table = self.reconciler.get_current_vs_target_table(
            current, target, prices
        )
        
        self.assertEqual(len(table), 1)
        self.assertEqual(table[0]["symbol"], "AAPL")
        self.assertEqual(table[0]["current"], 100)
        self.assertEqual(table[0]["target"], 150)
        self.assertEqual(table[0]["difference"], 50)
        self.assertEqual(table[0]["price"], 150.0)


class TestConvertTradesToOrders(unittest.TestCase):
    """Test trade to order conversion."""
    
    def test_convert_single_trade(self):
        """Test converting single trade to order."""
        trade = Trade(symbol="AAPL", quantity=100, side="buy")
        orders = convert_trades_to_orders([trade])
        
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0]["symbol"], "AAPL")
        self.assertEqual(orders[0]["qty"], 100)
        self.assertEqual(orders[0]["side"], "buy")
    
    def test_convert_multiple_trades(self):
        """Test converting multiple trades to orders."""
        trades = [
            Trade(symbol="AAPL", quantity=100, side="buy"),
            Trade(symbol="MSFT", quantity=50, side="sell")
        ]
        orders = convert_trades_to_orders(trades)
        
        self.assertEqual(len(orders), 2)
        self.assertEqual(orders[0]["symbol"], "AAPL")
        self.assertEqual(orders[1]["symbol"], "MSFT")


if __name__ == '__main__':
    unittest.main()
