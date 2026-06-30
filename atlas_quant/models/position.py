class Position:
    """
    Represents a position in a single asset.
    '''
    def __init__(self, ticker: str, quantity: float, price: float):
        self.ticker = ticker
        self.quantity = quantity  # number of shares
        self.price = price        # current price per share
    @property
    def market_value(self):
        return self.quantity * self.price
