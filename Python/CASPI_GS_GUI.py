# For GUI 
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtCore import QThread, pyqtSignal, QObject, QTimer
import pyqtgraph as pg
from random import randint
import os
import os.path
import sys

# For Arduino-Python Communcation over Serial
import socket
import time

# Data
import numpy as np
from queue import Queue
import datetime


#HOST = '10.40.6.128' # Enter IP or Hostname of your server
#PORT = 12345 # Pick an open Port (1000+ recommended), must match the server port

#HOST = '169.254.170.79'
HOST = '10.40.10.227'
PORT = 12345
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        ui_path = os.path.dirname(os.path.abspath(__file__)) # obtain file path
        uic.loadUi(os.path.join(ui_path, 'CASPI_GS.ui'), self)
        self.show() # Show the GUI

        # Initial Values
        self.command = "N"
        self.motor_speed = 0
        self.switchButtonStates(False)

        # Slider options
        self.motor_speed_slider.setMinimum(0)
        self.motor_speed_slider.setMaximum(100)
        self.motor_speed_slider.setTickInterval(10)

        self.motor_speed_slider.valueChanged.connect(self.slider_changed)

        # Rover Status Labels
        self.roverconnection_status.setStyleSheet("background-color: rgb(0, 255, 0); font: 10pt Verdana; font-weight: 600;")
        self.roverconnection_status.setAlignment(QtCore.Qt.AlignCenter)
        self.roverconnection_status.setText("Disconnected")

        self.roverdirection_status.setStyleSheet("background-color: rgb(0, 255, 0); font: 10pt Verdana; font-weight: 600;")
        self.roverdirection_status.setAlignment(QtCore.Qt.AlignCenter)
        self.roverdirection_status.setText("Not Moving")

        self.roverspeed_status.setStyleSheet("background-color: rgb(0, 255, 0); font: 10pt Verdana; font-weight: 600;")
        self.roverspeed_status.setAlignment(QtCore.Qt.AlignCenter)
        self.roverspeed_status.setText("0% Duty Cycle")

        self.roverdrill_status.setStyleSheet("background-color: rgb(0, 255, 0); font: 10pt Verdana; font-weight: 600;")
        self.roverdrill_status.setAlignment(QtCore.Qt.AlignCenter)
        self.roverdrill_status.setText("Not Deployed")

        # Button hover color change + background color change
        self.connect_button.setStyleSheet("QPushButton" "{" "background-color: rgb(255, 0, 0);" "}" 
                                         "QPushButton::hover""{""background-color : lightgreen;""}")
        self.stop_button.setStyleSheet("QPushButton" "{" "background-color: rgb(255, 0, 0);" "}" 
                                         "QPushButton::hover""{""background-color : lightgreen;""}")
        self.clearText_button.setStyleSheet("QPushButton" "{" "background-color: rgb(255, 255, 0);" "}" 
                                         "QPushButton::hover""{""background-color : lightgreen;""}")
        
        self.forward_pushbutton.setStyleSheet("QPushButton" "{" "background-color:  rgb(121, 121, 121);" "}" 
                                         "QPushButton::hover""{""background-color : lightgreen;""}")
        self.backwards_pushbutton.setStyleSheet("QPushButton" "{" "background-color:  rgb(121, 121, 121);" "}" 
                                         "QPushButton::hover""{""background-color : lightgreen;""}")
        self.left_pushbutton.setStyleSheet("QPushButton" "{" "background-color:  rgb(121, 121, 121);" "}" 
                                         "QPushButton::hover""{""background-color : lightgreen;""}")
        self.right_pushbutton.setStyleSheet("QPushButton" "{" "background-color:  rgb(121, 121, 121);" "}" 
                                         "QPushButton::hover""{""background-color : lightgreen;""}")
        self.drilldown_pushbutton.setStyleSheet("QPushButton" "{" "background-color:  rgb(121, 121, 121);" "}" 
                                         "QPushButton::hover""{""background-color : lightgreen;""}")
        self.drillup_pushbutton.setStyleSheet("QPushButton" "{" "background-color:  rgb(121, 121, 121);" "}" 
                                         "QPushButton::hover""{""background-color : lightgreen;""}")
        self.engagedrill_pushbutton.setStyleSheet("QPushButton" "{" "background-color:  rgb(121, 121, 121);" "}" 
                                         "QPushButton::hover""{""background-color : lightgreen;""}")

        # Timer to do holding buttons
        self.counter = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timeout)

        # Connect main buttons press to actions
        self.forward_pushbutton.pressed.connect(self.forward_pushbutton_action)
        self.forward_pushbutton.pressed.connect(self.on_press)
        self.forward_pushbutton.released.connect(self.on_release)

        self.backwards_pushbutton.pressed.connect(self.backwards_pushbutton_action)
        self.backwards_pushbutton.pressed.connect(self.on_press)
        self.backwards_pushbutton.released.connect(self.on_release)

        self.left_pushbutton.pressed.connect(self.left_pushbutton_action)
        self.left_pushbutton.pressed.connect(self.on_press)
        self.left_pushbutton.released.connect(self.on_release)

        self.right_pushbutton.pressed.connect(self.right_pushbutton_action)
        self.right_pushbutton.pressed.connect(self.on_press)
        self.right_pushbutton.released.connect(self.on_release)

        self.drilldown_pushbutton.pressed.connect(self.drilldown_pushbutton_action)
        self.drilldown_pushbutton.pressed.connect(self.on_press)
        self.drilldown_pushbutton.released.connect(self.on_release)

        self.drillup_pushbutton.pressed.connect(self.drillup_pushbutton_action)
        self.drillup_pushbutton.pressed.connect(self.on_press)
        self.drillup_pushbutton.released.connect(self.on_release)

        self.engagedrill_pushbutton.pressed.connect(self.engagedrill_pushbutton_action)
        self.engagedrill_pushbutton.pressed.connect(self.on_press)
        self.engagedrill_pushbutton.released.connect(self.on_release)

        # Connect basic buttons press to actions
        self.connect_button.clicked.connect(self.start_buttion_action)
        self.stop_button.clicked.connect(self.stop_buttion_action)
        self.clearText_button.clicked.connect(self.clearText_button_action)

    def switchButtonStates(self,ButtonsEnableState):
        # Disable buttons at first (except connect button)
        self.forward_pushbutton.setEnabled(ButtonsEnableState)
        self.backwards_pushbutton.setEnabled(ButtonsEnableState)
        self.left_pushbutton.setEnabled(ButtonsEnableState)
        self.right_pushbutton.setEnabled(ButtonsEnableState)
        self.drilldown_pushbutton.setEnabled(ButtonsEnableState)
        self.drillup_pushbutton.setEnabled(ButtonsEnableState)
        self.engagedrill_pushbutton.setEnabled(ButtonsEnableState)

        if(ButtonsEnableState):
            self.forward_pushbutton.setStyleSheet("QPushButton" "{" "background-color:  rgb(0, 0, 255);" "}" 
                                         "QPushButton::hover""{""background-color : lightgreen;""}")
            self.backwards_pushbutton.setStyleSheet("QPushButton" "{" "background-color:  rgb(0, 0, 255);" "}" 
                                            "QPushButton::hover""{""background-color : lightgreen;""}")
            self.left_pushbutton.setStyleSheet("QPushButton" "{" "background-color:  rgb(0, 0, 255);" "}" 
                                            "QPushButton::hover""{""background-color : lightgreen;""}")
            self.right_pushbutton.setStyleSheet("QPushButton" "{" "background-color:  rgb(0, 0, 255);" "}" 
                                            "QPushButton::hover""{""background-color : lightgreen;""}")
            self.drilldown_pushbutton.setStyleSheet("QPushButton" "{" "background-color:  rgb(0, 0, 255);" "}" 
                                            "QPushButton::hover""{""background-color : lightgreen;""}")
            self.drillup_pushbutton.setStyleSheet("QPushButton" "{" "background-color:  rgb(0, 0, 255);" "}" 
                                            "QPushButton::hover""{""background-color : lightgreen;""}")
            self.engagedrill_pushbutton.setStyleSheet("QPushButton" "{" "background-color:  rgb(0, 0, 255);" "}" 
                                            "QPushButton::hover""{""background-color : lightgreen;""}")
        else:
            self.forward_pushbutton.setStyleSheet("QPushButton" "{" "background-color:  rgb(121, 121, 121);" "}" 
                                         "QPushButton::hover""{""background-color : lightgreen;""}")
            self.backwards_pushbutton.setStyleSheet("QPushButton" "{" "background-color:  rgb(121, 121, 121);" "}" 
                                            "QPushButton::hover""{""background-color : lightgreen;""}")
            self.left_pushbutton.setStyleSheet("QPushButton" "{" "background-color:  rgb(121, 121, 121);" "}" 
                                            "QPushButton::hover""{""background-color : lightgreen;""}")
            self.right_pushbutton.setStyleSheet("QPushButton" "{" "background-color:  rgb(121, 121, 121);" "}" 
                                            "QPushButton::hover""{""background-color : lightgreen;""}")
            self.drilldown_pushbutton.setStyleSheet("QPushButton" "{" "background-color:  rgb(121, 121, 121);" "}" 
                                            "QPushButton::hover""{""background-color : lightgreen;""}")
            self.drillup_pushbutton.setStyleSheet("QPushButton" "{" "background-color:  rgb(121, 121, 121);" "}" 
                                            "QPushButton::hover""{""background-color : lightgreen;""}")
            self.engagedrill_pushbutton.setStyleSheet("QPushButton" "{" "background-color:  rgb(121, 121, 121);" "}" 
                                            "QPushButton::hover""{""background-color : lightgreen;""}")


    def on_timeout(self):
        s.send(str.encode(self.command))
        self.reply = s.recv(1024)
        print(self.command)
        print(self.reply)

    def on_press(self):
        self.timer.start(200)

    def on_release(self):
        self.command = "S,{}".format(0)
        s.send(str.encode(self.command))
        self.timer.stop()

    def slider_changed(self):
        self.motor_speed = self.motor_speed_slider.value()
        self.roverspeed_status.setText("{0:0.0f} % Duty Cycle".format(float(self.motor_speed)))

    def forward_pushbutton_action(self):
        print("forwards!")
        self.command = "F,{}".format(self.motor_speed)
        print(self.command)

    def backwards_pushbutton_action(self):
        print("backwards!")
        self.command = "B,{}".format(self.motor_speed)
        print(self.command)

    def left_pushbutton_action(self):
        print("left!")
        self.command = "L,{}".format(self.motor_speed)
        print(self.command)

    def right_pushbutton_action(self):
        print("right!")
        self.command = "R,{}".format(self.motor_speed)
        print(self.command)

    def drilldown_pushbutton_action(self):
        print("drill down!")
        self.command = "DA,{}".format(0)
        print(self.command)

    def drillup_pushbutton_action(self):
        print("drill up!")
        self.command = "UA,{}".format(0)
        print(self.command)

    def engagedrill_pushbutton_action(self):
        print("engaging drill!")
        self.command = "D,{}".format(0)
        print(self.command)

    def start_buttion_action(self):
        print("Connecting to Pi")
        try:
            s.connect((HOST,PORT))
            print("Connected to Seb-Pi")
            self.switchButtonStates(True)

        except Exception as e:
            print(e)
            self.switchButtonStates(False)

    def stop_buttion_action(self):
        print("Stopping gui")
        self.switchButtonStates(False)
        self.command = "Q,{}".format(0)
        s.send(str.encode(self.command))

    def clearText_button_action(self):
        print("clearing terminal")



if __name__ == "__main__":
    # Makes sure graphs don't get fucked by screen resolutions
    #QtWidgets.QApplication.setAttribute(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QtWidgets.QApplication(sys.argv)
    window = Ui()   
    sys.exit(app.exec_())
