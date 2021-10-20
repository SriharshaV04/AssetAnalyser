import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit, QLabel,
    QStackedLayout,QPushButton, QTabWidget, QFormLayout, QTextEdit, QDialog, QStackedWidget
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
from PyQt5 import uic
import sqlite3
from sql import create_database, get_database_connection, execute_query, print_tables
from sql import User

app = QApplication(sys.argv)

class WelcomePage(QMainWindow):
    def __init__(self):
        super(WelcomePage, self).__init__()
        uic.loadUi("p1-WelcomePage.ui", self)
        self.b_signUp.clicked.connect(self.openSignUp)

    def openSignUp(self):
        '''
        Switches tab to the sign up window
        '''
        nw = SignupScreen()
        widget.addWidget(nw)
        widget.setCurrentIndex(widget.currentIndex()+1)


class SignupScreen(QDialog):
    def __init__(self):
        super(SignupScreen, self).__init__()
        uic.loadUi("p1-SignUp.ui",self)
        self.i_pass.setEchoMode(QLineEdit.Password) # covers the text
        self.b_signUp.clicked.connect(self.signup)

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
        print(ability)

        valid = True
        if len(user) == 0 or len(pword) == 0 or len(phone) == 0:
            self.l_error.setText("Please input all fields")
            valid = False
        elif len(user) <
        elif len(phone) != 0 and len(phone) != 11:
            self.l_error.setText("Please enter a valid phone number.")
            valid = False
        elif len(pword) < 8:
            self.l_error.setText("Please enter a password of at least 8 characters in length")
            valid = False
        if valid:
            con = get_database_connection()
            create_database(con)
            # query = f'INSERT INTO users (username,password,phone) VALUES("{user}","{pword}","{phone}");'
            # execute_query(con,query)
            User(user,pword,phone,ability)


window = WelcomePage()
widget = QStackedWidget()
widget.addWidget(window)
widget.setWindowTitle("Helptrader")
widget.setFixedHeight(500)
widget.setFixedWidth(625)
widget.show()

app.exec()
