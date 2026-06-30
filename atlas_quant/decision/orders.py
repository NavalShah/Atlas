import pandas as pd
import numpy as np

def compute_orders(current_weights: pd.Series,
                   target_weights: pd.Series,
                   portfolio_value: Optional[float] = None,
                   min_trade_size: float = 0.001) -> pd.DataFrame:
    """
    Generate order recommendations to move from current weights to target weights.
    Parameters
    ----------
    current_weights : pd.Series
        Current portfolio weights (index=ticker, value=weight). Must sum to 1.
    target_weights : pd.Series
        Target portfolio weights (index=ticker, value=weight). Must sum to 1.
    portfolio_value : float, optional
        Total portfolio value in currency. If provided, order sizes will be in currency units.
        If not provided, order sizes will be in weight units.
    min_trade_size : float
        Minimum weight change to consider for trading (to avoid tiny trades).
    Returns
    -------
    pd.DataFrame
        Columns: ['ticker', 'action', 'weight_change', 'dollars'] (if portfolio_value given)
        or ['ticker', 'action', 'weight_change'].
    """
    # Align the two series (union of indices)
    all_tickers = set(current_weights.index) | set(target_weights.index)
    curr = current_weights.reindex(list(all_tickers), fill_value=0.0)
    targ = target_weights.reindex(list(all_tickers), fill_value=0.0)

    # Compute difference
    diff = targ - curr  # positive means we need to buy, negative means sell

    # Filter out small changes
    mask = np.abs(diff) >= min_trade_size
    diff = diff[mask]

    # Determine action
    actions = np.where(diff > 0, 'BUY', 'SELL')

    # Build DataFrame
    orders = pd.DataFrame({
        'ticker': diff.index,
        'weight_change': np.abs(diff),
        'action': actions
    })
    # Sort by absolute weight change descending
    orders = orders.sort_values('weight_change', ascending=False)

    if portfolio_value is not None:
        # Convert weight change to dollar amount
        orders['dollars'] = orders['weight_change'] * portfolio_value
        # Optionally, we can also compute shares if we have price, but we don't.
    return orders

