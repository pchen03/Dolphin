import os
import alpaca_trade_api as alpacaapi
from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
from datetime import datetime


class Account:
    account = None
    api = None

    def __init__(self, key, secretKey, endpoint) -> None:
        self.api = alpacaapi.REST(
            os.getenv(key),
            os.getenv(secretKey),
            os.getenv(endpoint),
        )
        self.account = self.api.get_account()

    def getMinuteData(self, startDate, endDate=datetime.today().strftime("%Y-%m-%d")):
        """Gets Minute Data for BTC and ETH"""
        bars = self.api.get_crypto_bars(
            "BTCUSD",
            start=startDate,
            end=endDate,
            timeframe=TimeFrame(1, TimeFrameUnit.Hour),
        ).df
        # print(BTCMinuteBars[BTCMinuteBars.exchange == "CBSE"])
        minuteBars = bars[bars.exchange == "CBSE"]["vwap"]

        return minuteBars

    def getHourData(self, startDate, endDate=datetime.today().strftime("%Y-%m-%d")):
        """Gets Hour Data for BTC and ETH"""
        bars = self.api.get_crypto_bars(
            "BTCUSD",
            start=startDate,
            end=endDate,
            timeframe=TimeFrame(30, TimeFrameUnit.Minute),
        ).df
        # print(BTCHourBars[BTCHourBars.exchange == "CBSE"])
        hourBars = bars[bars.exchange == "CBSE"]["vwap"]

        return hourBars

    def getDayData(self, startDate, endDate=datetime.today().strftime("%Y-%m-%d")):
        """Gets Day data for BTC and ETH"""
        bars = self.api.get_crypto_bars(
            "BTCUSD",
            start=startDate,
            end=endDate,
            timeframe=TimeFrame.Day,
        ).df
        # print(BTCDayBars[BTCDayBars.exchange == "CBSE"])
        dayBars = bars[bars.exchange == "CBSE"]["vwap"]

        return dayBars

    def getAllData(self, startDate, endDate=datetime.today().strftime("%Y-%m-%d")):
        """Gets all of the data in order of minute then hour and day"""
        return (
            self.getMinuteData(startDate, endDate),
            self.getHourData(startDate, endDate),
            self.getDayData(startDate, endDate),
        )

    def buy(
        self,
        symbol="ETHUSD",
        notional="0",
        qty="0",
        order_type="limit",
        limit_price="0",
        side="buy",
    ):
        """buy order"""
        if qty > 0:
            return self.api.submit_order(
                symbol=symbol,
                qty=qty,
                type=order_type,
                limit_price=limit_price,
                side=side,
            )
        else:
            return self.api.submit_order(
                symbol=symbol,
                notional=notional,
                type=order_type,
                limit_price=limit_price,
                side=side,
            )

    def sell(
        self,
        symbol="ETHUSD",
        notional="0",
        qty="0",
        order_type="limit",
        limit_price="0",
        side="sell",
    ):
        """sell order"""
        if qty > 0:
            return self.api.submit_order(
                symbol=symbol,
                qty=qty,
                type=order_type,
                limit_price=limit_price,
                side=side,
            )
        else:
            return self.api.submit_order(
                symbol=symbol,
                notional=notional,
                type=order_type,
                limit_price=limit_price,
                side=side,
            )

    def buyingPower(self):
        return self.account.buying_power

    def getPortfolio(self):
        return self.api.list_positions()

    def getPosition(self, symbol):
        return self.api.get_position(symbol)

    def printPortfolio(self):
        portfolio = self.api.list_positions()
        for position in portfolio:
            print("{} shares of {}".format(position.qty, position.symbol))
