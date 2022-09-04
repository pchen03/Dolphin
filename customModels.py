import numpy as np
from scipy import signal
from kucoin.client import Client


def cubic_root(x, a, b):
    """cubic root model a * x ^1/3 + b"""
    return a * x**1 / 3 + b


def natural_exp(x, a, b, c):
    """natural exponential model, a * e^(b*x) + c"""
    return a * np.exp(b * x) + c


def root(x, a, b, c):
    """square root model (a * x + b)^1/2 + c"""
    return (a * x + b) ** 1 / 2 + c


class customModel:
    model_type = None
    predicted_y = 0
    model_params = 0
    x = 0
    y = 0
    y_predicted_std = 0
    degree = 0
    peak_x = 0
    peak_y = 0
    valley_x = 0
    valley_y = 0

    def __init__(self, pred, params, modelType, x, y) -> None:
        self.model_type = modelType
        self.predicted_y = pred
        self.model_params = params
        self.x = x
        self.y = y

        if modelType == "natural":
            self.degree = 1 / 2.718
        elif modelType == "cubicRoot":
            self.degree = 1 / 3
        else:
            self.degree = 1 / 2

        self.y_predicted_std = (
            np.var(np.abs(self.y.to_numpy() - self.predicted_y))
        ) ** 0.5

    def make_next_value_prediction(self):
        return 1

    def find_peaks_and_troughs(self, y):
        """Finds all the peaks and valleys for the specific model"""
        y_predicted = self.predicted_y
        y_predicted_std = self.y_predicted_std
        data_y = y.to_numpy()

        # Find peaks(max).
        peak_indexes = signal.argrelextrema(data_y, np.greater)
        peak_indexes = peak_indexes[0]

        # Find valleys(min).
        valley_indexes = signal.argrelextrema(data_y, np.less)
        valley_indexes = valley_indexes[0]

        # Plot peaks.
        peak_x = peak_indexes
        peak_y = data_y[peak_indexes]

        # Plot valleys.
        valley_x = valley_indexes
        valley_y = data_y[valley_indexes]

        avgPeak = 0
        divide = 0
        for ind, peak in enumerate(peak_y):
            avgPeak = avgPeak + \
                (peak - y_predicted[peak_x[ind]]) ** 2 / y_predicted_std
            #     print ((peak - y_predicted[peak_x[ind]])/y_predicted_std)
            divide = divide + (peak - y_predicted[peak_x[ind]])
        self.peak_std = (avgPeak / divide) ** (1 / self.degree)

        self.sell_value = (
            self.peak_std * self.y_predicted_std + self.make_next_value_prediction()
        )["VWAP"]

        avgValley = 0
        bdivide = 0
        for ind, valley in enumerate(valley_y):
            avgValley = (
                avgValley + (y_predicted[valley_x[ind]] -
                             valley) ** 2 / y_predicted_std
            )
            #     print ((peak - y_predicted[peak_x[ind]])/y_predicted_std)
            bdivide = bdivide + (y_predicted[valley_x[ind]] - valley)
        self.valley_std = (avgValley / bdivide) ** (1 / self.degree)

        self.buy_value = (
            self.valley_std * self.y_predicted_std + self.make_next_value_prediction()
        )["VWAP"]

        self.peak_x, self.peak_y, self.valley_x, self.valley_y = (
            peak_x,
            peak_y,
            valley_x,
            valley_y,
        )


# add to find model at the bottom of 2nd method

    # x = BTCHbars.loc[:, ["Time"]]
    # y = BTCHbars.loc[:, ["VWAP"]]

    # popt = curve_fit(natural_exp, x.to_numpy().flatten(), y.to_numpy().flatten())[0]
    # natExpPred = natural_exp(x, *popt)
    # all_r2.append(r2_score(y, natExpPred))
    # all_models.append(customModel(natExpPred, popt, "natural", x, y))

    # popt = curve_fit(cubic_root, x.to_numpy().flatten(), y.to_numpy().flatten())[0]
    # natExpPred = cubic_root(x, *popt)
    # all_r2.append(r2_score(y, natExpPred))
    # all_models.append(customModel(natExpPred, popt, "cubicRoot", x, y))

    # popt = curve_fit(root, x.to_numpy().flatten(), y.to_numpy().flatten())[0]
    # natExpPred = root(x, *popt)
    # all_r2.append(r2_score(y, natExpPred))
    # all_models.append(customModel(natExpPred, popt, "root", x, y))
