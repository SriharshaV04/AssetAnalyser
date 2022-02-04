from alpha_vantage.foreignexchange import ForeignExchange
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage import fundamentaldata
import matplotlib.pyplot as plt
# from twilio.rest import Client
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

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
            forex.append(fd)

    return forex

class dataModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(dataModel, self).__init__()
        self._data = data
        self.setHorizontalHeaderLabels(["stock"])

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])


if __name__ == '__main__':
    listStocks()

