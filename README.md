# Atlas Quant

## Phase 1 - Data Foundation

**Version:** 0.1.0

---

# Overview

Welcome to **Atlas Quant**, a modular quantitative research platform designed to support the entire lifecycle of quantitative investing:

* Historical data collection
* Data validation
* Feature engineering
* Signal generation
* Portfolio construction
* Risk management
* Backtesting
* Paper trading
* Eventually live trading

This project is intentionally being built in phases.

**Phase 1 focuses exclusively on building a production-quality data layer.**

No trading logic will be implemented during this phase. Before an algorithm can make intelligent decisions, it needs reliable, reproducible, and validated historical market data.

The goal is to build a data layer that the rest of the platform will depend on.

---

# Phase 1 Goals

By the end of Phase 1, the project should be capable of:

* Downloading historical OHLCV data
* Caching downloaded data locally
* Updating only missing market days
* Supporting an arbitrary list of stock tickers
* Validating downloaded data
* Detecting missing values
* Detecting duplicate rows
* Detecting out-of-order timestamps
* Saving data in a consistent format
* Loading cached data quickly
* Providing one clean API for the rest of the application

No other module should directly access Yahoo Finance or any external data source.

All market data must flow through a centralized manager.

---

# Design Philosophy

This project is intended to resemble a simplified institutional quantitative research platform.

The data layer should be:

* Modular
* Testable
* Well documented
* Easy to extend
* Independent of the strategy logic

The implementation should favor readability over cleverness.

Every public function should include:

* Type hints
* Google-style docstrings
* Logging
* Error handling

---

# Initial Technology Stack

Python 3.12+

Libraries:

* pandas
* numpy
* yfinance
* requests
* pydantic
* pyyaml
* tqdm
* rich
* loguru
* pytest

Optional (future):

* DuckDB
* Polars
* SQLAlchemy
* Parquet support

---

# Folder Structure

```
atlas_quant/

│
├── README.md
├── requirements.txt
├── pyproject.toml
├── .gitignore
│
├── config/
│     settings.yaml
│
├── data/
│     raw/
│     cache/
│
├── atlas_quant/
│
│     ├── __init__.py
│
│     ├── data/
│     │
│     │     downloader.py
│     │     loader.py
│     │     validator.py
│     │     cache.py
│     │     manager.py
│     │
│     ├── models/
│     │
│     │     market_data.py
│     │
│     ├── utilities/
│     │
│     │     logger.py
│     │     dates.py
│     │     filesystem.py
│     │
│     └── exceptions.py
│
├── tests/
│
│     test_downloader.py
│     test_loader.py
│     test_validator.py
│     test_cache.py
│
└── examples/
      download_sp500.py
```

---

# Responsibilities

## downloader.py

Responsible for:

* Downloading data from Yahoo Finance
* Downloading multiple tickers
* Handling retries
* Handling API failures
* Returning DataFrames

This module should never save files.

Downloading and persistence should remain separate responsibilities.

---

## loader.py

Responsible for:

* Reading cached data
* Reading CSV files
* Returning DataFrames
* Never downloading data

---

## cache.py

Responsible for:

* Saving data
* Loading cached files
* Determining whether cached data exists
* Updating only missing dates

---

## validator.py

Responsible for validating data.

Checks include:

* Missing rows

* Duplicate dates

* Duplicate index

* Missing OHLC values

* Missing volume

* Negative prices

* Negative volume

* Invalid timestamps

* Non-monotonic dates

* Empty DataFrames

Validation should return structured results rather than only raising exceptions.

---

## manager.py

This is the main interface.

Every future module should use only this class.

Example:

```python
manager = MarketDataManager()

data = manager.get_data(
    ticker="AAPL",
    start="2015-01-01",
    end="2024-12-31"
)
```

Internally it should:

1. Check cache

2. Determine missing dates

3. Download missing data

4. Validate data

5. Save cache

6. Return clean DataFrame

The caller should never know where the data came from.

---

# Configuration

Create:

```
config/settings.yaml
```

Example:

```yaml
data_provider: yahoo

cache_directory: data/cache/

default_start_date: 2010-01-01

auto_update: true

retry_attempts: 3

retry_delay_seconds: 5

log_level: INFO
```

No hardcoded paths should exist in the codebase.

---

# Logging

Use Loguru.

Every major action should generate informative logs.

Example:

```
INFO     Loading cached AAPL

INFO     Cache found

INFO     Missing 12 trading days

INFO     Downloading missing data

INFO     Validation passed

INFO     Cache updated

INFO     Returning DataFrame
```

---

# Data Format

Every DataFrame should have exactly these columns:

```
Date
Open
High
Low
Close
Adj Close
Volume
```

Requirements:

* Datetime index
* Ascending order
* No duplicates
* No missing values
* Float prices
* Integer volume

---

# Error Handling

Create custom exceptions.

Examples:

```
AtlasQuantError

DownloadError

ValidationError

CacheError

ConfigurationError
```

Avoid raising generic Exceptions whenever possible.

---

# Coding Standards

Each module begins with a header explaining:

* Purpose
* Responsibilities
* Inputs
* Outputs
* Dependencies

Every function should include:

* Type hints
* Google-style docstrings
* Inline comments explaining non-obvious logic

Avoid deeply nested conditionals by using early returns where appropriate.

---

# Unit Tests

Create tests for:

Downloader

* Valid ticker
* Invalid ticker
* Multiple tickers
* Retry logic

Validator

* Duplicate rows
* Missing values
* Negative prices
* Empty DataFrame

Cache

* Save
* Load
* Update
* Missing file

Manager

* Cache hit
* Cache miss
* Download + save
* Validation failure

Target at least 90% code coverage for Phase 1.

---

# Example Usage

```python
from atlas_quant.data.manager import MarketDataManager

manager = MarketDataManager()

tickers = [
    "AAPL",
    "MSFT",
    "NVDA",
    "GOOGL",
    "META",
]

data = {}

for ticker in tickers:
    data[ticker] = manager.get_data(
        ticker=ticker,
        start="2015-01-01",
        end="2024-12-31",
    )

print(data["AAPL"].tail())
```

---

# Definition of Done

Phase 1 is complete when all of the following are true:

* The project installs cleanly in a virtual environment.
* Configuration is loaded from YAML.
* Historical data can be downloaded for any valid ticker.
* Cached data is reused whenever possible.
* Only missing trading days are downloaded during updates.
* Data is validated before being returned.
* Invalid data produces meaningful errors.
* Logging clearly describes the workflow.
* Unit tests pass with high coverage.
* Example scripts execute successfully without code changes.
* No trading logic exists in the codebase yet.

Only after these criteria are met should development proceed to **Phase 2: Feature Engineering and Technical Indicators**, where the validated historical data becomes the foundation for calculating reusable financial indicators.
