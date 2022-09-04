from sqlite3 import Timestamp
from dotenv import load_dotenv
from Account import Account
from backtest import backtest
from findModel import remodel, find_best_model, print_line
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 30 minutes with 8 day gap returns 11.443%
# 30 minutes with 5 day gap returns 16.446%
# 30 minutes with 4 day gap returns 10.813%

# 60 minute with 20 day gap returns 10%

# new is 24% for 30 minute 5 day gap
BT_CURRENT_DATE = "2022-01-12T01:00:00Z"
START_DATE = (datetime.strptime(BT_CURRENT_DATE, "%Y-%m-%dT%H:%M:%SZ") - timedelta(days=5)
              ).strftime("%Y-%m-%dT%H:%M:%SZ")
END_DATE = "2022-01-30T01:00:00Z"
bt = backtest(100000, START_DATE)

load_dotenv()
myAccount = Account(
    key="PAPER_API_KEY", secretKey="PAPER_API_KEY_SECRET", endpoint="PAPER_API_ENDPOINT"
)

# creates and finds all of the models
best_model = find_best_model(myAccount, START_DATE, BT_CURRENT_DATE)
best_model.set_up_model()

last_value = best_model.get_last_value()
current_model_value = best_model.get_last_model_value()
predicted_next_value = best_model.make_next_value_prediction()

vwap = myAccount.getHourData(BT_CURRENT_DATE, END_DATE)
vwap = pd.DataFrame({"TimeStamp": vwap.index, "VWAP": vwap.values})
vwap["Time"] = np.arange(len(vwap.index))
vwap['TimeStamp'] = vwap['TimeStamp'].dt.tz_localize(None)

# should only have one position open at a time
while BT_CURRENT_DATE != END_DATE:
    print_line("Checking for trades...")
    # remodel if the data deviates too far from our model
    print_line("Account Total " + str(bt.account_total))

    if (
        last_value >= best_model.max_value_allowed
    ):
        # if len(myAccount.api.list_positions()) != 0 and myAccount.getPortfolio()[0].side != "long":
        if bt.crypto_count < 0:
            bt.close_short(last_value)
            # close all short positions here
            print_line("Should close all short positions here")

        (
            best_model,
            current_value,
            current_model_value,
            predicted_next_value,
        ) = remodel(myAccount, START_DATE, BT_CURRENT_DATE)
    elif last_value <= best_model.min_value_allowed:
        # if len(myAccount.api.list_positions()) != 0 and myAccount.getPortfolio()[0].side == "long":
        if bt.crypto_count > 0:
            # myAccount.api.close_position(symbol="BTCUSD")
            bt.sell(last_value)
            print_line("Should close all long positions here")

        (
            best_model,
            current_value,
            current_model_value,
            predicted_next_value,
        ) = remodel(myAccount, START_DATE, BT_CURRENT_DATE)
    print("last valune, min, max", last_value,
          best_model.min_value_allowed, best_model.max_value_allowed)

    # positive slope
    if predicted_next_value > current_model_value:
        print_line("In Uptrend")

        if last_value <= best_model.buy_value:
            # issue buy order or close all short positions
            # if len(myAccount.api.list_positions()) == 0:
            if bt.crypto_count == 0:
                # myAccount.api.submit_order(
                #     symbol="BTCUSD",
                #     notional=float(myAccount.account.equity) * 0.95,
                #     side="buy",
                # )
                bt.buy(last_value)
                print_line("Buying BTC now, new Account Total: " + str(bt.account_total) +
                           " Total crypto: " + str(bt.crypto_count) + " At Price: " + str(last_value))

            else:
                # position = myAccount.getPortfolio()[0]
                # if position.side != "long":
                if bt.crypto_count < 0:
                    # if there are short positions close all of them here and take long position
                    # myAccount.api.close_position(symbol="BTCUSD")
                    bt.close_short(last_value)
                    # myAccount.api.submit_order(
                    #     symbol="BTCUSD",
                    #     notional=float(myAccount.account.equity) * 0.95,
                    #     side="buy",
                    # )
                    bt.buy(last_value)
                    print_line(
                        "Closing all Short positions and Buying BTC now")

    # negative slopes
    elif predicted_next_value < current_model_value:
        print_line("In Downtrend")
        if last_value >= best_model.sell_value:
            # issue sell order or close all long positionspositions
            # if len(myAccount.api.list_positions()) == 0:
            if bt.crypto_count == 0:
                # can't really do anythin or short right now TODO
                # myAccount.sell(notional=myAccount.account.equity)
                bt.short(last_value)
                print_line("Suppose to short but can't short" + str(bt.account_total) +
                           " Total crypto: " + str(bt.crypto_count) + " At Price: " + str(last_value))
            else:
                # if position.side != "short":
                if bt.crypto_count > 0:
                    # if there are any long positions close them and take a short position
                    print_line("Selling everything now")
                    # myAccount.api.close_position(symbol="BTCUSD")
                    bt.sell(last_value)
                    bt.short(last_value)
    else:
        print_line("No good trades found")

    print_line("Account Total: " + str(bt.account_total) +
               " Total crypto: " + str(bt.crypto_count) +
               " Account Total: " + str(bt.crypto_count * last_value) +
               " Price:" + str(last_value) +
               " Date: " + BT_CURRENT_DATE)
    # print_line("Finished modeling, waiting 1 hour for next model")

    date = datetime.strptime(BT_CURRENT_DATE, "%Y-%m-%dT%H:%M:%SZ")
    next_y = vwap.loc[vwap["TimeStamp"] == date]["VWAP"].iloc[0]
    print(next_y)
    best_model.y = pd.concat([best_model.y, pd.DataFrame(
        {"VWAP": [next_y]})], ignore_index=True)

    current_model_value = best_model.predict_at_n(
        len(best_model.y))
    predicted_model_next_value = best_model.predict_at_n(
        len(best_model.y)-1)
    best_model.predicted_y = np.append(
        best_model.predicted_y, predicted_model_next_value)
    best_model.set_up_model()

    last_value = best_model.get_last_value()

    # time.sleep(3600)
    BT_CURRENT_DATE = (datetime.strptime(BT_CURRENT_DATE, "%Y-%m-%dT%H:%M:%SZ") + timedelta(minutes=30)
                       ).strftime("%Y-%m-%dT%H:%M:%SZ")
    START_DATE = (datetime.strptime(BT_CURRENT_DATE, "%Y-%m-%dT%H:%M:%SZ") - timedelta(days=5)
                  ).strftime("%Y-%m-%dT%H:%M:%SZ")

    # updates the new x, y, and predicted y values for our model
    # print_line("5 Minutes has past, getting new model values")
    # BTCHbars = myAccount.getHourData(START_DATE, BT_CURRENT_DATE)
    # BTCHbars = pd.DataFrame(
    #     {"TimeStamp": BTCHbars.index, "VWAP": BTCHbars.values})
    # BTCHbars["Time"] = np.arange(len(BTCHbars.index))
    # print_line("Updating new model values \n \n")

# TODO Fix this up because this does not work:
# This is overwriting x and y with completely new and preset lengths the new data frames
# however all methods that depend on that length will not work well
    # best_model.x = pd.concat([best_model.x, pd.DataFrame(
    #     {"Time": [len(best_model.x)]})], ignore_index=True)
    # best_model.y = pd.concat([best_model.y, pd.DataFrame(
    #     {"VWAP": [BTCHbars.iloc[len(BTCHbars)-1]["VWAP"]]})], ignore_index=True)
    # best_model.predicted_y = np.append(
    #     best_model.predicted_y, best_model.make_next_value_prediction()
    # )

    # best_model.set_up_model()
    # last_value = best_model.get_last_value()
    # current_model_value = best_model.get_last_model_value()
    # predicted_next_value = best_model.make_next_value_prediction()


print_line("Account Total: " + str(bt.account_total) +
           " Total crypto: " + str(bt.crypto_count) +
           " Account Total: " + str((bt.crypto_count * last_value) + bt.account_total * 2) +
           " Date: " + BT_CURRENT_DATE)

# TODO list

# 1.) Clean up code
# 2.) Try to see if stop loss orders can be placed after order is executed to minimize losses
# 3.) some kind of new exiting strategy where we can take even more profit ( still thinking on this one )
