class Portfolio:
    """
    Represents a portfolio of positions.
    '''
    def __init__(self):
        self.positions = {}  # ticker -> Position
        self.cash = 0.0

    def add_position(self, position):
        self.positions[position.ticker] = position

    def remove_position(self, ticker):
        if ticker in self.positions:
            del self.positions[ticker]

    def get_position(self, ticker):
        return self.positions.get(ticker)

    def total_value(self):
        return self.cash + sum(pos.market_value for pos in self.positions.values())
