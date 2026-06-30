# Metrics Analyzer
class MetricsAnalyzer:
    def __init__(self):
        pass
    
    def calculate_sharpe_ratio(self, returns, risk_free_rate=0.0):
        # Simplified Sharpe ratio calculation
        excess_returns = returns - risk_free_rate
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        return (excess_returns.mean() / returns.std()) * (252 ** 0.5)  # Annualized
    
    def calculate_sortino_ratio(self, returns, risk_free_rate=0.0, target_return=0.0):
        # Simplified Sortino ratio
        excess_returns = returns - target_return
        downside_returns = excess_returns[excess_returns < 0]
        if len(downside_returns) == 0:
            # If no downside returns, return a large number if positive excess returns
            if excess_returns.mean() > 0:
                return 999999.0  # Large number instead of infinity
            else:
                return 0.0
        downside_deviation = (downside_returns ** 2).mean() ** 0.5
        if downside_deviation == 0:
            return 0.0
        return (excess_returns.mean() / downside_deviation) * (252 ** 0.5)

