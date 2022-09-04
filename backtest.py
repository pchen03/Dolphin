import backtrader as bt


class backtest:
    account_total = 0
    current_date = ""
    crypto_count = 0

    def __init__(self, startingCapital, currentDate) -> None:
        self.account_total = startingCapital
        self.current_date = currentDate
        self.crypto_count = 0

    def buy(self, price):
        self.crypto_count = self.account_total / price
        self.account_total = 0

    def sell(self, price):
        self.account_total = abs(self.crypto_count * price)
        self.crypto_count = 0

    def short(self, price):
        self.crypto_count = -1 * self.account_total / price

    def close_short(self, price):
        self.account_total = 2 * self.account_total + self.crypto_count * price
        self.crypto_count = 0
