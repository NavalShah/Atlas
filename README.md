# Atlas Quant

A modular quantitative research platform for loading, caching, validating, and analyzing market data.

## Features

- **Data Loading**: Load OHLCV data from CSV files with automatic datetime parsing.
- **Caching**: Transparent CSV-based caching system to avoid re-downloading data.
- **Validation**: Comprehensive validation of market data (OHLCV) including checks for missing values, negative prices, illogical price relationships, duplicate dates, and non‑monotic index.
- **Utilities**:
  - Date utilities (parsing, date ranges, weekday checks, trading days).
  - Filesystem helpers (directory creation, file size, globbing).
  - Logging configuration via Loguru with console and file output.
- **Market Data Model**: `MarketData` class provides convenient properties for OHLCV series and date ranges.
- **Configuration**: YAML‑based configuration (`config/settings.yaml`) for data provider, cache directory, default dates, retry behavior, and log level.
- **Testing**: A test suite built with `pytest`.

## Installation

### Prerequisites

- Python 3.8 or higher
- `pip` (or your preferred Python package manager)

### Install from source

```bash
# Clone the repository
git clone https://github.com/yourusername/atlas-quant.git
cd atlas-quant

# Install the package in development mode (recommended for development)
pip install -e .

# Or install as a regular package
pip install .
```

This will install the package and its dependencies listed in `pyproject.toml`:

- pandas
- numpy
- yfinance
- requests
- pydantic
- pyyaml
- tqdm
- rich
- loguru
- pytest

## Quick Start

```python
import pandas as pd
from atlas_quant.data.loader import load_csv, load_cached_ticker
from atlas_quant.data.cache import save_data, load_cached_data, update_cache
from atlas_quant.data.validator import validate_market_data
from atlas_quant.models.market_data import MarketData
from atlas_quant.utilities.dates import date_range, is_weekday
from atlas_quant.utilities.filesystem import ensure_dir
from atlas_quant.utilities.logger import setup_logger
from pathlib import Path

# Initialize logger
setup_logger("INFO")

# Ensure cache directory exists
cache_dir = ensure_dir("data/cache")

# 1. Load raw CSV data
csv_path = Path("data/raw/AAPL.csv")
df_raw = load_csv(csv_path)

# 2. Validate the loaded data
errors = validate_market_data(df_raw)
if errors:
    print("Validation errors:", errors)
else:
    print("Data is valid")

# 3. Cache the data
save_data("AAPL", df_raw, cache_dir)

# 4. Later, load from cache
df_cached = load_cached_data("AAPL", cache_dir)

# 5. Update cache with new data (e.g., from an API)
# new_df = ...  # fetch new OHLCV data
# updated_df = update_cache("AAPL", new_df, cache_dir)

# 6. Wrap in MarketData for convenient access
market_data = MarketData(df_cached, ticker="AAPL")
print(f"Ticker: {market_data.ticker}")
print(f"Date range: {market_data.date_range}")
print(f"Close prices:\n{market_data.close.head()}")

# 7. Utility example: get list of weekdays
weekdays = date_range("2024-01-01", "2024-01-31")
print(f"Weekdays in Jan 2024: {[d.strftime('%Y-%m-%d') for d in weekdays if is_weekday(d)]}")
```

## Module Overview

### `atlas_quant.data.loader`
- `load_csv(file_path)`: Load OHLCV data from a CSV file.
- `load_cached_ticker(ticker, cache_dir)`: Load cached data for a ticker (returns empty DataFrame if missing).

### `atlas_quant.data.cache`
- `save_data(ticker, data, cache_dir)`: Save a DataFrame to CSV cache.
- `load_cached_data(ticker, cache_dir)`: Load cached data for a ticker.
- `cache_exists(ticker, cache_dir)`: Check if a cache file exists.
- `get_cached_date_range(ticker, cache_dir)`: Get the date range of cached data.
- `update_cache(ticker, new_data, cache_dir)`: Merge new data with existing cache (avoiding duplicates).

### `atlas_quant.data.validator`
- `validate_market_data(df)`: Returns a list of validation error strings (empty if valid). Checks:
  - Non‑empty DataFrame
  - DateTimeIndex
  - No duplicate dates
  - Monotonically increasing index
  - Presence and completeness of OHLCV columns
  - No missing or negative values
  - Logical price relationships (High ≥ Low, High ≥ Open/Close, Low ≤ Open/Close)

### `atlas_quant.models.market_data`
- `MarketData`: Wrapper around a pandas DataFrame with OHLCV columns.
  - Properties: `open`, `high`, `low`, `close`, `volume`, `date_range`.
  - Methods: `to_dict()`, `from_dict()`.

### `atlas_quant.utilities.dates`
- `parse_date(date_str)`: Convert `"YYYY‑MM‑DD"` to `pd.Timestamp`.
- `date_range(start, end=None)`: Generate a `DatetimeIndex` of dates.
- `is_weekday(date)`: Check if a date is a weekday.
- `get_trading_days(start, end=None)`: List of weekdays between two dates (ignores holidays).

### `atlas_quant.utilities.filesystem`
- `ensure_dir(path)`: Create a directory if it does not exist.
- `get_file_size(path)`: Return file size in bytes.
- `list_files(directory, pattern="*")`: List files matching a glob pattern.

### `atlas_quant.utilities.logger`
- `setup_logger(level="INFO")`: Configure Loguru with console and file output (`logs/atlas_quant.log`).

### Configuration (`config/settings.yaml`)
```yaml
data_provider: yahoo          # Data provider identifier (used by downstream modules)
cache_directory: data/cache/  # Directory where CSV caches are stored
default_start_date: 2010-01-01 # Default start date for data requests
auto_update: true             # Whether to automatically update stale caches
retry_attempts: 3             # Number of retry attempts for failed requests
retry_delay_seconds: 5        # Delay between retries (seconds)
log_level: INFO               # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
```

## Testing

Run the test suite with `pytest`:

```bash
pytest
```

Tests are located in the `tests/` directory and cover the loader, cache, and validator modules.

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/awesome-feature`).
3. Commit your changes (`git commit -am 'Add awesome feature'`).
4. Push to the branch (`git push origin feature/awesome-feature`).
5. Open a Pull Request.

Please ensure that new code is accompanied by appropriate unit tests and follows the existing code style.

## License

This project is currently **unlicensed**. If you plan to use or distribute this code, please contact the author to clarify licensing terms.

## Acknowledgements

- Built with [Loguru](https://github.com/Delgan/loguru) for logging.
- Uses [pandas](https://pandas.pydata.org/) for data manipulation.
- Configuration via [PyYAML](https://pyyaml.org/).

---

*Happy quantitative research!*