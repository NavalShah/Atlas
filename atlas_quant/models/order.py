class Order:
    """
    Represents an order to buy or sell a security.
    '''
    def __init__(self, ticker: str, action: str, quantity: float, price: Optional[float] = None):
        self.ticker = ticker
        self.action = action.upper()  # 'BUY' or 'SELL'
        self.quantity = quantity
        self.price = price
    @property
    def value(self):
        if self.price is None:
            return None
        return self.quantity * self.price
