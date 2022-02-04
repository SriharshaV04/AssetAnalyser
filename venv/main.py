import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit, QLabel,
    QStackedLayout,QPushButton, QTabWidget, QFormLayout, QTextEdit, QDialog, QStackedWidget, QHeaderView
)
from PyQt5.QtGui import QPalette, QColor, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5 import uic
import sqlite3
from sql import create_database, get_database_connection, execute_query, print_tables
from sql import UserDatabase
import time
from Asset_data import dataModel, listStocks, listForex

app = QApplication(sys.argv)

class WelcomePage(QMainWindow):
    def __init__(self):
        super(WelcomePage, self).__init__()
        uic.loadUi("p1-WelcomePage.ui", self)
        self.b_signUp.clicked.connect(self.openSignUp)
        self.b_LogIn.clicked.connect(self.openSignIn)

    def openSignUp(self):
        '''
        Switches tab to the sign up window
        '''
        widget.setCurrentIndex(SignUpIndex)

    def openSignIn(self):
        '''
        opens the SignIn window
        :return:
        '''
        widget.setCurrentIndex(SignInIndex)


class SignupScreen(QDialog):
    def __init__(self):
        super(SignupScreen, self).__init__()
        uic.loadUi("p1-SignUp.ui",self)
        self.i_pass.setEchoMode(QLineEdit.Password) # covers the text
        self.b_signUp.clicked.connect(self.signup)
        self.b_back.clicked.connect(self.back)
        self.i_phone.setPlaceholderText("07123456789")

    def signup(self):
        '''
        Adds a user to the database along with an encrypted password
        :return: None
        '''
        user = self.i_user.text()
        pword = self.i_pass.text()
        phone = str(self.i_phone.text())
        phone = phone.replace(" ","")  # removes spaces and white space in the user input
        print(phone)
        if self.r_standard.isChecked(): # Returns the status of the radiobuttons indicating user skill level
            ability = "Standard"
        elif self.r_advanced.isChecked():
            ability = "Advanced"

        valid = True
        if len(user) == 0 or len(pword) == 0:
            self.l_error.setText("Please input all required fields")
            valid = False
        elif len(phone) != 0:
            if phone[:2] != "07":
                self.l_error.setText("Please enter a valid phone number with area code:07")
                valid = False
            try:
                phone_value = int(phone)
                if phone_value < 7000000000 or phone_value > 8000000000:
                    # Checks that the phone number is 11 digits long
                    self.l_error.setText("Please enter a valid phone number.")
                    valid = False
            except:
                # if the int function fails, denotes that the user has inputted an invalid character in the phonenumber
                self.l_error.setText("Please enter a valid phone number: only numbers")
                valid = False
        if len(pword) < 8:
            self.l_error.setText("Please enter a password of at least 8 characters in length")
            valid = False
        if valid:
            #Add the new user to the database
            db = UserDatabase()
            db.add_user(user,pword,phone,ability)
            self.l_error.setText("Successfully made an account")
            self.l_error.setStyleSheet("color:cyan")

    def back(self):
        widget.setCurrentIndex(0) #Takes the user to the Welcome screen

class LogIn(QDialog):

    def __init__(self):
        '''
        Loads up the LogIn page
        '''
        super(LogIn, self).__init__()
        uic.loadUi("p2-SignIn.ui",self)
        self.b_noAccount.clicked.connect(self.noAccount)
        self.b_SignIn.clicked.connect(self.SignIn)
        self.i_pass.setEchoMode(QLineEdit.Password) # covers the text
        self.c_showPword.stateChanged.connect(self.showPass)  #Tracks changes to the state of the checkbox

    def showPass(self, state):
        '''
        Hides or reveals the user input text into the password widget depending on state of checkbox
        If checked - contents shown
        :param state: State of the checkbox given by the connect function
        '''
        if state == Qt.Checked:
            self.i_pass.setEchoMode(QLineEdit.Normal)
        else:
            self.i_pass.setEchoMode(QLineEdit.Password) # covers the text

    def noAccount(self):
        '''
        Changes the stacked widget index to the sign Up page
        '''
        widget.setCurrentIndex(SignUpIndex)

    def SignIn(self):
        '''
        Verifies the user's credentials in logging in.
        :return:
        '''
        user = self.i_user.text()
        pword = self.i_pass.text()

        if len(user) == 0 or len(pword) == 0:
            self.l_error.setText("Please input all fields")

        else:
            db = UserDatabase()
            x = db.find_user(user)  # Searches the database using the search parameter: user
            if x != None:  # if the username is found and an account with that username exists verify the password
                result_pass = x[2]  # The second index of the tuple returned contains the password
                if result_pass == pword:
                    print("login successful")
                    self.l_error.setText("Login Successful")
                    self.l_error.setStyleSheet("color: cyan”")
                    widget.setCurrentIndex(MainPageIndex)  # Sends the user into the main home page of the application
                else:
                    self.l_error.setText("Incorrect Password")
            else:
                self.l_error.setText("Username not found")

class HomePage(QDialog):

    def __init__(self):
        '''
        Loads up the LogIn page
        '''
        super(HomePage, self).__init__()
        uic.loadUi("p3-HomePage.ui",self)
        stockData = listStocks()
        self.cb_ass_choice.currentIndexChanged.connect(self.assetChange)

        #Logout button to redirect the user back to the welcome page
        self.b_logout.clicked.connect(self.logout)

        self.createTable()
        self.t_assets.setModel(self.model)

        self.filter_model = QSortFilterProxyModel()
        self.filter_model.setSourceModel(self.model)
        self.filter_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.filter_model.setFilterKeyColumn(-1)  # filters using all columns

        self.i_search.setPlaceholderText("Search")
        self.i_search.textChanged.connect(self.filter_model.setFilterRegExp)
        self.t_assets.setModel(self.filter_model)
        # self.t_assets.resizeColumnToContents(1)
        self.t_assets.setColumnWidth(1,250)

        
    def load_assets(self,asset_type):
        if asset_type == "Stocks":
            assets = listStocks()
        elif asset_type == "Forex":
            assets = listForex()

        try:
            self.model = dataModel(assets)  # creates a custom QAbstractModel using the data of stock

            self.filter_model = QSortFilterProxyModel()
            self.filter_model.setSourceModel(self.model)
            self.filter_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
            self.filter_model.setFilterKeyColumn(-1)

            self.i_search.textChanged.connect(self.filter_model.setFilterRegExp)
            self.t_assets.setModel(self.filter_model)
        except: pass

    def createTable(self):
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Ticker","Name"])
        assets = listStocks()
        for asset in assets:
            col1, col2 = self.createRow(asset)
            self.model.appendRow([col1, col2])

    def createRow(self,data:list):
        col1 = QStandardItem()
        col1.setCheckable(True)
        col1.setText(data[0])

        col2 = QStandardItem()
        col2.setText(data[1])
        return col1, col2

    def logout(self):
        widget.setCurrentIndex(WelcomePageIndex)

    def assetChange(self):
        '''
        Sets the model to stock, crypto or forex lists depending on the user's requirement
        '''
        asset_choice = self.cb_ass_choice.currentText()
        self.load_assets(asset_choice)







window = WelcomePage()
widget = QStackedWidget()
widget.addWidget(window)
WelcomePageIndex = 0

#Add all the pages to the stack widget
nw = SignupScreen()
widget.addWidget(nw)
SignUpIndex = 1 # index location of widget in the stacked widget for easy access

nw = LogIn()
widget.addWidget(nw)
SignInIndex = 2

nw = HomePage()
widget.addWidget(nw)
MainPageIndex = 3
widget.setCurrentIndex(MainPageIndex)

#Define the dimensions and title of window
widget.setWindowTitle("Helptrader")
widget.setFixedHeight(500)
widget.setFixedWidth(625)
widget.show()

app.exec()
