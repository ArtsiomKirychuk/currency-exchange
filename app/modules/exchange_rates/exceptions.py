class ExchangeRateNotFoundError(Exception):
    def __init__(self, currency_abbreviation: str):
        self.currency_abbreviation = currency_abbreviation
        self.message=f"Exchange currency_abbreviation: {self.currency_abbreviation} not found."
        super().__init__(self.message)
