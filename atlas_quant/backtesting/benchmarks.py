# Benchmark Analyzer
class BenchmarkAnalyzer:
    def __init__(self, benchmark_symbol="SPY"):
        self.benchmark_symbol = benchmark_symbol
    
    def calculate_relative_return(self, portfolio_returns, benchmark_returns):
        # Calculate excess return
        return portfolio_returns - benchmark_returns
    
    def calculate_tracking_error(self, portfolio_returns, benchmark_returns):
        # Tracking error = std dev of excess returns
        excess_returns = self.calculate_relative_return(portfolio_returns, benchmark_returns)
        return excess_returns.std() * (252 ** 0.5)  # Annualized
    
    def calculate_information_ratio(self, portfolio_returns, benchmark_returns):
        # Information ratio = active return / tracking error
        excess_returns = self.calculate_relative_return(portfolio_returns, benchmark_returns)
        if extra_returns.std() == 0:
            return 0.0
        return (excess_returns.mean() / excess_returns.std()) * (252 ** 0.5)

