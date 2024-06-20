import pyautogui
import time
import sys
import os

from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedLayout, QFrame, QPushButton, QLabel, QScrollBar
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QIcon
import resources_rc  # Import the compiled resource file

from BlurWindow.blurWindow import GlobalBlur
from components import EyePilotButton, EyePilotButtonColorChoice, EyePilotScroll
from calibration import Calibration

from data_stoarge import Storage

from tracker import Tracker

class MyMainWindow(QMainWindow):

    def moveEvent(self, event) -> None:
        time.sleep(0.02)  # sleep for 20ms

    def resizeEvent(self, event) -> None:
        time.sleep(0.02)  # sleep for 20ms

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(":/icon.png"))

        name = "EyePather"
        self.setWindowTitle(name)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 800, 600)

        GlobalBlur(self.winId(),Dark=True,QWidget=self)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)

        # Create a frame to hold left side content
        left_frame = QFrame()
        main_layout.addWidget(left_frame, stretch=1)

        # Add a label to left frame (optional)
        label_left = QLabel(name)
        label_left.setStyleSheet("color: white; font-size: 40px;")
        label_left.setAlignment(Qt.AlignCenter)
        self.left_layout = QVBoxLayout()
        left_frame.setLayout(self.left_layout)
        self.left_layout.addWidget(label_left)

        # Create a frame to hold right side content
        self.right_frame = RightSideMenu()
        main_layout.addWidget(self.right_frame, stretch=1)

        self.right_frame.setSignal("Main","Start",signal=self.start)
        self.right_frame.setSignal("Stop","Stop",signal=self.stop)

        self.calibrationWidget = Calibration()
        self.calibrationWidget.setOnQuit(self.stop_calibration)

        # Start a timer to update the position periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.main_loop)
        self.timer.start(30)  # Update every second

        self.eyeTracker = Tracker()
        self.running = False
        self.calibrationON = False

        self.fix_start = time.time()

    def show_calibration(self):
        self.calibrationON = True
        self.eyeTracker.calibrationOn()
        self.calibrationWidget.show()

    def stop_calibration(self):
        self.calibrationON = False
        self.eyeTracker.calibrationOff()
        self.calibrationWidget.reset()

    def main_loop(self):
        fix_debounce = 1
        if self.running:
            point, calibration, blink, fix, acceptance_radius, calibration_radius = self.eyeTracker.step()

            if self.calibrationON:
                self.calibrationWidget.setPosition(calibration[0], calibration[1])
                self.calibrationWidget.setRadius(2*calibration_radius)
                self.calibrationWidget.setPositionFit(calibration[0], calibration[1])
                self.calibrationWidget.setRadiusFit(2*acceptance_radius)

            self.storage.append(point[0],point[1])

    def setFixation(self,fix):
        self.eyeTracker.setFixation(fix/10)

    def setImpact(self,impact):
        self.eyeTracker.setClassicalImpact(impact)

    def resetTracker(self):
        self.eyeTracker.reset()

    def start(self):
        self.eyeTracker.start()
        self.show_calibration()
        self.running = True
        self.right_frame.switchMenu(1)
        self.storage = Storage()

    def stop(self):
        self.running = False
        self.eyeTracker.stop()
        self.storage.post_process()
        self.eyeTracker = Tracker()
        self.right_frame.switchMenu(0)

    def closeEvent(self, event):
        # Call your function or perform cleanup here
        self.stop()
        # Call the base class closeEvent to ensure default behavior
        super().closeEvent(event)
        quit()

class RightSideMenu(QFrame):
    def __init__(self):
        super().__init__()

        self.menu_stack  = QStackedLayout()
        self.setLayout(self.menu_stack)
        self.setStyleSheet("background-color: rgba(26, 32, 48, 0.8);")

        self.mainMenu = MainMenu()
        self.stopMenu = StopMenu()

        self.__allMenus = {
            "Main" : self.mainMenu,
            "Stop" : self.stopMenu,
        }

        self.mainMenu.setSignal("Stop", lambda : self.switchMenu(0))

        self.menu_stack.addWidget(self.mainMenu)
        self.menu_stack.addWidget(self.stopMenu)
        self.menu_stack.setCurrentIndex(0)
        self.menus = 2


    def switchMenu(self,index):
        if self.menus <= index:
            return

        self.menu_stack.setCurrentIndex(index)

    def setSignal(self,menu_name,name,signal):
        self.__allMenus[menu_name].setSignal(name,signal)

class Menu(QFrame):

    def __init__(self):
        super().__init__()

        self.right_layout = QVBoxLayout()
        self.right_layout.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.setLayout(self.right_layout)

        self.right_buttons = []

    def setSignal(self,button_name, signal):
        buttons = [button for button in self.right_buttons if button.getID() == button_name]
        for button in buttons:
            button.addSignal(signal)

    def add_button(self,name,signal=None):
        tmp_layout = QHBoxLayout()
        tmp_layout.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.right_buttons.append(EyePilotButton(name,signal = signal))
        tmp_layout.addWidget(self.right_buttons[-1])
        self.right_layout.addLayout(tmp_layout)

    def add_custom(self,button):
        tmp_layout = QHBoxLayout()
        self.right_buttons.append(button)
        tmp_layout.addWidget(self.right_buttons[-1])
        self.right_layout.addLayout(tmp_layout)

class MainMenu(Menu):

    def __init__(self):
        super().__init__()

        self.add_button("Start")

class StopMenu(Menu):

    def __init__(self):
        super().__init__()

        self.add_button("Stop")



if __name__ == "__main__":
    # sys.stdout = open(os.devnull, 'w')

    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())
