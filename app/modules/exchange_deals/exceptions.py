class ExchangeDealNotFoundError(Exception):
    pass


class InvalidDealStatusError(Exception):
    def __init__(self):
        self.message = "The deal is no longer valid."
        super().__init__(self.message)


class DealExpiredError(Exception):
    pass