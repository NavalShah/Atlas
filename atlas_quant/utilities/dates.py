"""Date and time utilities."""

import pandas as pd
from datetime import datetime, timedelta
from typing import Union, List


def parse_date(date_str: str) -> pd.Timestamp:
    """Parse date string to Timestamp.

    Args:
        date_str: Date string in YYYY-MM-DD format.

    Returns:
        Timestamp.
    """
    return pd.Timestamp(date_str)


def date_range(start: str, end: str = None) -> pd.DatetimeIndex:
    """Generate a range of dates.

    Args:
        start: Start date in YYYY-MM-DD format.
        end: End date in YYYY-MM-DD format. If None, uses today.

    Returns:
        DatetimeIndex of dates.
    """
    start_ts = parse_date(start)
    end_ts = parse_date(end) if end else pd.Timestamp.now()
    return pd.date_range(start=start_ts, end=end_ts, freq="D")


def is_weekday(date: Union[str, pd.Timestamp]) -> bool:
    """Check if a date is a weekday (Monday-Friday).

    Args:
        date: Date string or Timestamp.

    Returns:
        True if weekday, False otherwise.
    """
    ts = pd.Timestamp(date)
    return ts.weekday() < 5  # Monday=0, Sunday=6


def get_trading_days(start: str, end: str = None) -> List[pd.Timestamp]:
    """Get list of trading days (weekdays) between start and end.

    Note: This does not account for market holidays.

    Args:
        start: Start date in YYYY-MM-DD format.
        end: End date in YYYY-MM-DD format. If None, uses today.

    Returns:
        List of Timestamps for weekdays.
    """
    date_idx = date_range(start, end)
    return [d for d in date_idx if is_weekday(d)]
