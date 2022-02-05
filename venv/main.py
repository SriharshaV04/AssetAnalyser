import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit, QLabel,
    QStackedLayout,QPushButton, QTabWidget, QFormLayout, QTextEdit, QDialog, QStackedWidget, QHeaderView
)
from PyQt5.QtGui import QPalette, QColor, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QSize
from PyQt5 import uic
import sqlite3
from sql import create_database, get_database_connection, execute_query, print_tables
from sql import UserDatabase
import time
from Asset_data import dataModel, listStocks, listForex

app = QApplication(sys.argv)
CRYPTO_CURRENCIES = [['BTC',"Bitcoin"],["ETH","Ethereum"], ['LTC',"Litecoin"], ['EOS',""], ['XRP',"Ripple"], ['BCH',"Bitcoin Cash"],
                     ['DOGE',"Dogecoin"], ["ICP","Internet Computer"]]


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
                    widget.setCurrentIndex(MainPageIndex)
                    widget.resize(750,600)  # Sends the user into the main home page of the application
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

        self.cb_ass_choice.currentIndexChanged.connect(self.create_update_Table)
        self.b_display.clicked.connect(self.display)

        #Logout button to redirect the user back to the welcome page
        self.b_logout.clicked.connect(self.logout)

        self.create_update_Table()

    def create_update_Table(self):
        self.model = QStandardItemModel()
        asset_type = self.cb_ass_choice.currentText() # Retrieves the value from the comboBox
        if asset_type == "Stock":
            self.model.setHorizontalHeaderLabels(["Ticker","Name"])
            assets = listStocks() # loads the stocks the program will use from the stocks.csv
            self.c_pred.setEnabled(False)
        elif asset_type == "Forex":
            self.model.setHorizontalHeaderLabels(["Currency Pair", "From", "To"])
            assets = listForex()  # loads the forex pairs the program will use from the forex_pairs.csv
            self.c_pred.setEnabled(False)
        else:
            self.model.setHorizontalHeaderLabels(["Code", "Name"])
            assets = CRYPTO_CURRENCIES
            self.c_pred.setEnabled(True)

        for asset in assets:
            # adds the data to the model
            try:
                col1,col2,col3 = self.createRow(asset)
                self.model.appendRow([col1, col2, col3])
            except:
                col1, col2 = self.createRow(asset)
                self.model.appendRow([col1, col2])

        self.t_assets.setModel(self.model)

        self.filter_model = QSortFilterProxyModel()
        self.filter_model.setSourceModel(self.model)
        self.filter_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.filter_model.setFilterKeyColumn(-1)  # filters using all columns

        self.i_search.setPlaceholderText("Search")
        self.i_search.textChanged.connect(self.filter_model.setFilterRegExp)
        self.t_assets.setModel(self.filter_model)
        self.t_assets.setColumnWidth(1, 250)

    def createRow(self,data:list):
        col1 = QStandardItem()
        col1.setCheckable(True)
        col1.setText(data[0])

        col2 = QStandardItem()
        col2.setText(data[1])

        try:
            col3 = QStandardItem()
            col3.setText(data[2])
            return col1, col2, col3
        except: pass
        return col1, col2

    def logout(self):
        widget.setCurrentIndex(WelcomePageIndex)
        widget.resize(625,500)

    def display(self):
        self.assetsToDraw = []

        for row in range(self.model.rowCount()):
            if self.model.item(row,0).checkState() == Qt.Checked:
                self.assetsToDraw.append(self.model.item(row,0).text())

        if len(self.assetsToDraw) > 5:
            self.l_error.setText("Please select a maximum of 5 assets to view")
        elif len(self.assetsToDraw) == 0:
            self.l_error.setText("Please select at least 1 asset to view")
        else:
            self.l_error.setText("")

            info = {
                "Assets":self.assetsToDraw,
                "Price":self.c_price.checkState(),
                "Volume":self.c_volume.checkState(),
                "Support":self.c_support.checkState(),
                "Resistance":self.c_resistance.checkState(),
                "RSA":self.c_rsa.checkState(),
                "Prediction":self.c_pred.checkState(),
            }
            ChartPage(info)  # Creates the chart page using the info in the next phase


class ChartPage(QWidget):
    def __init__(self,info):
        pass



if __name__ == '__main__':
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
    widget.setGeometry(0,0,750,600)

    #Define the dimensions and title of window
    widget.setWindowTitle("Helptrader")
    # widget.setGeometry(450,250,625,500)

    widget.show()

    app.exec()
