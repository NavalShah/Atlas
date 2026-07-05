# Alpaca Integration - Quick Reference Guide

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements-alpaca.txt
```

### 2. Configure Environment
Create/update `.env` file:
```
ALPACA_ENV=paper
ALPACA_API_KEY=your_api_key
ALPACA_SECRET_KEY=your_secret_key
ALPACA_BASE_URL=https://paper-api.alpaca.markets
DRY_RUN=true
```

### 3. Test Connection
```bash
python examples/test_alpaca_connection.py
```

Expected output:
- Account Number
- Buying Power
- Cash Balance
- Portfolio Value
- Current Positions
- Open Orders
- Market Status

---

## Basic Usage

### Get a Broker Instance
```python
from atlas_quant.execution.broker_factory import get_broker

# Automatically uses ALPACA_ENV and credentials from .env
broker = get_broker()

# Or explicitly specify environment
broker = get_broker("paper")  # or "live"

# Connect
if broker.connect():
    print("Connected successfully")
else:
    print("Connection failed")
```

### Get Account Information
```python
account = broker.get_account()
print(f"Cash: ${account.get('cash')}")
print(f"Buying Power: ${account.get('buying_power')}")
print(f"Portfolio Value: ${account.get('portfolio_value')}")
```

### Get Current Positions
```python
positions = broker.get_positions()
for symbol, position in positions.items():
    qty = position.get('qty')
    price = position.get('avg_fill_price')
    print(f"{symbol}: {qty} @ ${price}")
```

### Submit an Order
```python
order = {
    "symbol": "AAPL",
    "qty": 10,
    "side": "buy",
    "type": "market",
    "time_in_force": "day"
}

response = broker.submit_order(order)
print(f"Order submitted: {response.get('id')}")
```

### Reconcile Portfolio
```python
from atlas_quant.utilities.reconciliation import PortfolioReconciler

reconciler = PortfolioReconciler(tolerance=0.01)

current = {"AAPL": 100, "MSFT": 50}
target = {"AAPL": 150, "MSFT": 25}

trades, summary = reconciler.reconcile(current, target)

print(f"Total trades: {summary['total_trades']}")
print(f"Buy trades: {summary['buy_trades']}")
print(f"Sell trades: {summary['sell_trades']}")

for trade in trades:
    print(f"{trade.side.upper()} {trade.quantity} {trade.symbol}")
```

### Generate Reports
```python
from atlas_quant.reporting.execution import generate_all_reports
from datetime import datetime
import os

report_dir = f"./reports/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
os.makedirs(report_dir, exist_ok=True)

execution_data = {
    "timestamp": datetime.now().isoformat(),
    "orders_submitted": 5,
    "orders_filled": 5,
    "orders": [...]
}

generate_all_reports(
    report_dir=report_dir,
    execution_data=execution_data,
    orders=[...],
    log_entries=[...],
    account={...},
    positions={...}
)

print(f"Reports generated in: {report_dir}")
```

---

## Full Execution Pipeline

See `examples/paper_rebalance.py` for complete workflow:

1. Load market data
2. Generate features
3. Run decision engine
4. Get current positions from broker
5. Reconcile with target portfolio
6. Generate trade orders
7. Execute trades (with dry-run support)
8. Generate execution reports

---

## Market Status

### Check if Market is Open
```python
is_open = broker.is_market_open()
print(f"Market {'open' if is_open else 'closed'}")
```

### Get Market Clock
```python
clock = broker.get_market_clock()
print(f"Is Open: {clock.get('is_open')}")
print(f"Next Open: {clock.get('next_open')}")
print(f"Next Close: {clock.get('next_close')}")
```

### Get Available Assets
```python
assets = broker.get_assets()
print(f"Total assets: {len(assets)}")
for asset in assets[:5]:
    print(f"  {asset.get('symbol')} - {asset.get('name')}")
```

---

## Troubleshooting

### Connection Issues
- Check `.env` file exists and has correct API keys
- Verify `ALPACA_ENV` is set to 'paper' or 'live'
- Ensure network connectivity
- Check API key permissions on Alpaca dashboard

### Order Submission Issues
- Verify account has sufficient buying power
- Check market is open (use `is_market_open()`)
- Ensure symbol is tradable (check available assets)
- Verify order parameters are valid

### Tests Not Running
```bash
# Install test dependencies
pip install pytest

# Run specific test file
python -m unittest tests.test_reconciliation

# Run all tests
python -m unittest discover tests
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| ALPACA_ENV | Yes | paper | 'paper' or 'live' |
| ALPACA_API_KEY | Yes | - | Your Alpaca API key |
| ALPACA_SECRET_KEY | Yes | - | Your Alpaca secret key |
| ALPACA_BASE_URL | No | Auto | API endpoint URL |
| DRY_RUN | No | true | Don't submit orders if true |

---

## Order Types

### Market Order
```python
order = {
    "symbol": "AAPL",
    "qty": 100,
    "side": "buy",
    "type": "market",
    "time_in_force": "day"
}
```

### Limit Order
```python
order = {
    "symbol": "AAPL",
    "qty": 100,
    "side": "buy",
    "type": "limit",
    "limit_price": 150.00,
    "time_in_force": "day"
}
```

### Stop Order
```python
order = {
    "symbol": "AAPL",
    "qty": 100,
    "side": "sell",
    "type": "stop",
    "stop_price": 145.00,
    "time_in_force": "day"
}
```

### Stop-Limit Order
```python
order = {
    "symbol": "AAPL",
    "qty": 100,
    "side": "sell",
    "type": "stop_limit",
    "stop_price": 145.00,
    "limit_price": 144.50,
    "time_in_force": "day"
}
```

---

## Time in Force Options

- `day` - Order expires at end of trading day
- `gtc` - Good-til-canceled (remains active until filled or canceled)
- `opg` - Open on next market open
- `cls` - Close on market close
- `ioc` - Immediate or cancel
- `fok` - Fill or kill

---

## Reports Generated

When running with report generation enabled:

- `account_snapshot.json` - Account and position state
- `orders.csv` - All submitted orders
- `fills.csv` - Only filled/executed orders
- `execution_report.json` - Complete execution data
- `execution_report.html` - Formatted HTML report
- `execution_log.txt` - Timestamped execution log

---

## Switching Between Paper and Live Trading

### Change Environment
```bash
# Paper trading
export ALPACA_ENV=paper

# Live trading (be careful!)
export ALPACA_ENV=live
```

### Update API Credentials
```bash
export ALPACA_API_KEY=your_live_api_key
export ALPACA_SECRET_KEY=your_live_secret_key
export ALPACA_BASE_URL=https://api.alpaca.markets
```

### Run Code
No code changes needed! The factory automatically selects the correct broker.

```python
broker = get_broker()  # Will use live broker if ALPACA_ENV=live
```

---

## Best Practices

1. **Always test with paper trading first**
   - Set `ALPACA_ENV=paper` until fully confident

2. **Use dry-run mode before live execution**
   - Set `DRY_RUN=true` to test without submitting orders

3. **Monitor market hours**
   - Use `broker.is_market_open()` before trading
   - Check market clock for next open/close times

4. **Check reconciliation results**
   - Review proposed trades before execution
   - Look for unexpected large orders

5. **Save execution reports**
   - Always generate reports for audit trail
   - Review logs for any issues

6. **Use appropriate tolerance**
   - Set reconciliation tolerance to avoid dust trades
   - Default 0.01 shares usually works well

---

## Documentation

- **Main Integration Guide:** `ALPACA_INTEGRATION_SUMMARY.md`
- **Broker Interface:** `atlas_quant/execution/broker.py`
- **Example Connection:** `examples/test_alpaca_connection.py`
- **Example Rebalancing:** `examples/paper_rebalance.py`
- **Test Examples:** `tests/test_*.py`

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the example scripts
3. Check test files for usage examples
4. Review docstrings in source code
5. Consult Alpaca documentation: https://docs.alpaca.markets
