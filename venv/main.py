import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit, QLabel,
    QStackedLayout,QPushButton, QTabWidget, QFormLayout, QTextEdit, QDialog, QStackedWidget
)
from PyQt5.QtGui import QPalette, QColor, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5 import uic
import sqlite3
from sql import create_database, get_database_connection, execute_query, print_tables
from sql import UserDatabase
import time

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

    def signup(self):
        '''
        Adds a user to the database along with an encrypted password
        :return: None
        '''
        user = self.i_user.text()
        pword = self.i_pass.text()
        phone = self.i_phone.text()
        if self.r_standard.isChecked():
            ability = "Standard"
        elif self.r_advanced.isChecked():
            ability = "Advanced"

        valid = True
        if len(user) == 0 or len(pword) == 0 or len(phone) == 0:
            self.l_error.setText("Please input all fields")
            valid = False
        elif len(phone) != 0 and len(phone) != 11:
            self.l_error.setText("Please enter a valid phone number.")
            valid = False
        elif len(pword) < 8:
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
        widget.setCurrentIndex(SignUpIndex)

    def SignIn(self):
        user = self.i_user.text()
        pword = self.i_pass.text()

        if len(user) == 0 or len(pword) == 0:
            self.l_error.setText("Please input all fields")

        else:
            db = UserDatabase()
            x = db.find_user(user)  # Searches the database using the search parameter: user
            print(x)
            if x != None:  # if the username is found and an account with that username exists verify the password
                result_pass = x[2]  # The second index of the tuple returned contains the password
                if result_pass == pword:
                    print("login successful")
                    self.l_error.setText("Login Successful")
                    self.l_error.setStyleSheet("color: cyan”")
                    time.sleep(4)
                    widget.setCurrentIndex(MainPageIndex)
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
        testData = ("Tesla","Apple","Meta","Walmart","Nio","Alphabet")

        model = QStandardItemModel(len(testData),1)
        # model.setHorizontalHeaderItem()

        for i in range(len(testData)):
            item = QStandardItem(testData[i])
            model.setItem(i,0,item)

        filter_model = QSortFilterProxyModel()
        filter_model.setSourceModel(model)
        filter_model.setFilterCaseSensitivity(Qt.CaseInsensitive)

        self.i_search.textChanged.connect(filter_model.setFilterRegExp)
        self.t_assets.setModel(filter_model)


window = WelcomePage()
widget = QStackedWidget()
widget.addWidget(window)

#Add all the pages to the stack widget
nw = SignupScreen()
widget.addWidget(nw)
SignUpIndex = 1

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

# def hash_djb2(s):
#     hash = 5381
#     for x in s:
#         hash = (( hash << 5) + hash) + ord(x)
#     return hash & 0xFFFFFFFF
