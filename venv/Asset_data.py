from alpha_vantage.foreignexchange import ForeignExchange
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage import fundamentaldata
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import mplfinance as mpf

# from twilio.rest import Client
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import pandas as pd
import numpy as np
import sys

API_KEY = "028O7T18U5LTKKQU"
ts = TimeSeries(key=API_KEY, output_format='pandas')

def listStocks():
    stocks = []
    with open("stocks.csv","r") as f:
        lines = f.readlines()
        for line in lines:
            stock_data = line.split(",")
            stock_data.pop() # removes the company
            stocks.append(stock_data)
    print(stocks)
    return stocks

def listForex():
    forex = []
    with open("forex_pairs.csv","r") as f:
        lines = f.readlines()
        for line in lines:
            forex_data = line.split(",")
            fd = []
            for unit in forex_data:
                fd.append(unit.strip('"'))
            fd[2] = fd[2][:-2] # Removing the new line character from the last each line
            forex.append(fd)

    return forex

def getStockPrice(ticker,tf):
    if tf == "1 day":
        data, metadata = ts.get_daily(symbol=ticker, outputsize='compact')
        return data
    elif tf == "1 hr":
        data, metadata = ts.get_intraday(symbol=ticker, interval="60min", outputsize='compact')
        return data
    else:
        data, metadata = ts.get_intraday(symbol=ticker, interval="5min", outputsize='compact')
        return data

class stock_data:

    def __init__(self, info):
        self.info = info

    def retrieve_data(self,ticker):
        self.stock = yf.Ticker(ticker)
        return self.stock.history("6mo")

    def create_graph(self):
        fig = mpf.figure(figsize=(9, 6), style='binance')
        if self.info["Volume"] == False:
            for i, asset in enumerate(self.info["Assets"]):
                ax = fig.add_subplot(2,3,i+1)
                df = self.retrieve_data(asset)
                mpf.plot(df, type='candle', ax=ax, axtitle=asset)
            return fig
        else:
            for i, asset in enumerate(self.info["Assets"]):
                ax = fig.add_subplot(2,3,i+1)
                vx = fig.add_subplot(3,3,i+4)
                df = self.retrieve_data(asset)
                mpf.plot(df, type='candle', ax=ax,volume=vx, axtitle=asset)
            return fig

class ChartPage(QtWidgets.QWidget):
    def __init__(self, info):
        super().__init__()
        self.window_width, self.window_height = 1200, 800
        self.setMinimumSize(self.window_width, self.window_height)
        self.setWindowTitle("Stocks")

        self.info = info

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        self.canvas = FigureCanvas(mpf.figure(figsize=(16,9), style='binance'))
        layout.addWidget(self.canvas)
        self.label = QtWidgets.QLabel()
        layout.addWidget(self.label)
        self.create_graph()


    def retrieve_data(self,ticker):
        '''
        Uses the yahoo finance api to retrieve the price history over a 6 month period of a particular asset
        :param ticker: Asset identifier
        :return: pandas dataframe in the ohlc format along with a datetime index
        '''
        if self.info["Asset Type"] == "Stock":
            asset = yf.Ticker(ticker)
        elif self.info["Asset Type"] == "Cryptocurrency":
            ticker = ticker + "-USD"  # Ensures the ticker is in the correct format and in USD rather than for ex. GBP
            asset = yf.Ticker(ticker)
        if self.info["TimeFrame"] == "1 day":
            return asset.history(period="6mo",interval="1d")
        elif self.info["TimeFrame"] == "1 hr":
            return asset.history(period="5d",interval="1h")
        else:
            return asset.history(period="1d",interval="5m")

    def support(self, data):
        '''
        produces a resistance level which is lowest value with 5 candles either side
        :param data: pandas dataframe containing OHLC price data
        :return: Pandas dataframe in format
        '''
        periods = [10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000]
        dates = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        count = 0
        Times = []
        Prices = []
        dataframe = data["Low"]

        for i in range(len(dataframe)):
            currentLow = min(periods)
            print(dataframe[i])
            value = dataframe[i]
            periods.pop(0)
            periods.append(value)
            dates.pop(0)
            dates.append(dataframe.index[i])

            if currentLow <= min(periods):  # The value is greater than the current low and hence count is reset
                count += 1
            else:
                count = 0
                currentLow = value
                currentTime = dataframe.index[i]
            if count == 5:  # The current low is the lowest over a range of 10 candles and hence is a support value
                Times.append(currentTime)
                Prices.append(currentLow)
            else:
                Times.append(currentTime)
                Prices.append(np.nan)
        return self.create_df(Times, Prices)

    def resitance(self, data):
        '''
        produces a resistance level which is lowest value with 5 candles either side
        :param data: pandas dataframe containing OHLC price data
        :return: Pandas dataframe in format
        '''
        periods = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        dates = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        count = 0

        Times = []
        Prices = []
        dataframe = data["Low"]

        for i in range(len(dataframe)):
            currentHigh = max(periods)
            print(dataframe[i])
            value = dataframe[i]
            periods.pop(0)
            periods.append(value)
            dates.pop(0)
            dates.append(dataframe.index[i])
            currentTime = dataframe.index[i]

            if currentHigh <= max(periods):  # The value is greater than the current low and hence count is reset
                count += 1
            else:
                count = 0
                currentHigh = value
                currentTime = dataframe.index[i]
            if count == 5:  # The current low is the lowest over a range of 10 candles and hence is a support value
                Times.append(currentTime)
                Prices.append(currentHigh)
            else:
                Times.append(currentTime)
                Prices.append(np.nan)

        return self.create_df(Times, Prices)

    def create_df(self, times, prices):
        '''
        :param times: column
        :param prices: indices
        :return: Creates a pandas dataframe with a single column: pivots indexed by pandas datetime objects
        '''
        data = {"Pivots": prices}
        pivots = pd.DataFrame(data, index=[times])
        return pivots

    def plot_analysis(self, asset, ax):
        adplts = []
        if self.info["Support"] == True:
            data = self.retrieve_data(asset)
            lows = self.support(data)
            sup = mpf.make_addplot(lows["Pivots"],type="scatter", ax=ax)
            adplts.append(sup)

        if self.info["Resistance"] == True:
            data = self.retrieve_data(asset)
            highs = self.resitance(data)
            res = mpf.make_addplot(highs["Pivots"], type="scatter", ax=ax)
            adplts.append(res)

        return adplts


    def plot_price_volume(self):
        '''
        Plots the price and volume charts on the canvas for each asset chosen
        '''
        if self.info["Volume"] == False:
            for i, asset in enumerate(self.info["Assets"]):
                ax = self.canvas.figure.add_subplot(2,3,i+1)  # Places the price at top of the page in the 2x3 layout
                df = self.retrieve_data(asset)  # Asset price history pandas dataframe in OHLC format
                adplts = self.plot_analysis(asset,ax)  # Retrieves the support and resistance analysis if required
                mpf.plot(df, addplot=adplts, type='candle', ax=ax, axtitle=asset)
        else:
            for i, asset in enumerate(self.info["Assets"]):
                ax = self.canvas.figure.add_subplot(2,3,i+1)
                vx = self.canvas.figure.add_subplot(2,3,i+4)
                df = self.retrieve_data(asset)
                adplts = self.plot_analysis(asset, ax)  # Retrieves the support and resistance analysis if required
                mpf.plot(df, addplot=adplts, type='candle', ax=ax,volume=vx, axtitle=asset)


    def create_graph(self):
        '''
        Creates the graphs with all the required information
        '''
        self.plot_price_volume()
        self.canvas.draw()

if __name__ == '__main__':
    # listForex()
    # df = getStockPrice("TSLA", "1 day")
    # df.rename(columns={"1. open": "Open",
    #                    "2. high": "High",
    #                    "3. low": "Low",
    #                    "4. close": "Close"})
    # # print(df.shape)
    # print(df)
    # print(df.info())
    # mpf.plot(df, type='candle')
    # t = yf.Ticker("TSLA")
    # tsla = t.history('6mo')
    #
    # a = yf.Ticker("AAPL")
    # aapl = a.history('6mo')
    #
    # g = yf.Ticker("GOOG")
    # goog = g.history('6mo')
    #
    # fig = mpf.figure(figsize=(9, 6), style='yahoo')
    #
    # ax1 = fig.add_subplot(2, 3, 1)
    # ax2 = fig.add_subplot(2, 3, 2)
    # ax3 = fig.add_subplot(2, 3, 3)
    #
    # av1 = fig.add_subplot(3, 3, 7, sharex=ax1)
    # av2 = fig.add_subplot(3, 3, 8, sharex=ax1)
    # av3 = fig.add_subplot(3, 3, 9, sharex=ax3)
    #
    # mpf.plot(tsla, type='candle', ax=ax1, volume=av1, mav=(10, 20), axtitle='TSLA')
    # mpf.plot(goog, type='candle', ax=ax2, volume=av2, mav=(10, 20), axtitle='GOOG')
    # mpf.plot(aapl, type='candle', ax=ax3, volume=av3, mav=(10, 20), axtitle='aapl')
    # fig.show()

    app = QtWidgets.QApplication(sys.argv)
    info = {
        "Asset Type": "Stock",
        "Assets": ["ADM"],
        "Price": True,
        "Volume": False,
        "Support": True,
        "Resistance": True,
        "RSA": False,
        "Prediction": False,
        "TimeFrame": "1 day"
    }

    w = ChartPage(info)
    w.show()
    app.exec()


