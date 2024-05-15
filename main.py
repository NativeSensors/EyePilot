import time
import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedLayout, QFrame, QPushButton, QLabel, QToolBar
from PySide2.QtCore import Qt, QTimer

from BlurWindow.blurWindow import GlobalBlur
from button import EyePilotButton, EyePilotButtonColorChoice
from calibration import Calibration

from dot import CircleWidget

class MyMainWindow(QMainWindow):

    def moveEvent(self, event) -> None:
        time.sleep(0.02)  # sleep for 20ms

    def resizeEvent(self, event) -> None:
        time.sleep(0.02)  # sleep for 20ms

    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
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
        label_left = QLabel("EyePilot")
        label_left.setStyleSheet("color: white; font-size: 40px;")
        label_left.setAlignment(Qt.AlignCenter)
        left_layout = QVBoxLayout()
        left_frame.setLayout(left_layout)
        left_layout.addWidget(label_left)

        # Create a frame to hold right side content
        right_frame = RightSideMenu()
        main_layout.addWidget(right_frame, stretch=1)

        self.landing_spot = CircleWidget()
        layout_center  = left_layout.geometry().center()
        self.landing_spot.setPosition(layout_center.x() + 175, layout_center.y() + 200)
        self.landing_spot.setColor(102,102,102)
        self.landing_spot.setParent(self)

        self.tracker = CircleWidget()
        layout_center  = left_layout.geometry().center()
        self.tracker.setPosition(layout_center.x() + 175, layout_center.y() + 200)
        self.tracker.setColor(150,150,150)
        self.tracker.setParent(self)

        right_frame.setSignal("Customize","ColorChange",signal=self.changeTrackerColor)
        # Add buttons and options to the right frame

        # Start a timer to update the position periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.main_loop)
        self.timer.start(30)  # Update every second


    def changeTrackerColor(self,color):
        self.tracker.setColor(color[0],color[1],color[2])

    def main_loop(self):
        pass

class RightSideMenu(QFrame):
    def __init__(self):
        super().__init__()

        self.menu_stack  = QStackedLayout()
        self.setLayout(self.menu_stack)
        self.setStyleSheet("background-color: rgba(26, 32, 48, 0.8);")

        self.mainMenu = MainMenu()
        self.settings = Settings()
        self.customize = Customize()

        self.__allMenus = {
            "Main" : self.mainMenu,
            "Settings" : self.settings,
            "Customize" : self.customize
        }

        self.menu_stack.addWidget(self.mainMenu)
        self.menu_stack.addWidget(self.settings)
        self.menu_stack.addWidget(self.customize)
        self.menu_stack.setCurrentIndex(0)
        self.menus = 3

        self.mainMenu.setSignal("Settings", lambda : self.switchMenu(1))
        self.mainMenu.setSignal("Customize", lambda : self.switchMenu(2))

        self.settings.setSignal("Back", lambda : self.switchMenu(0))
        self.customize.setSignal("Back", lambda : self.switchMenu(0))


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
        tmp_layout.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.right_buttons.append(button)
        tmp_layout.addWidget(self.right_buttons[-1])
        self.right_layout.addLayout(tmp_layout)

class MainMenu(Menu):

    def __init__(self):
        super().__init__()

        self.calibrationWidget = Calibration()

        self.add_button("Start")
        self.add_button("Calibration",signal = self.show_calibration)
        self.add_button("Settings")
        self.add_button("Customize")

    def show_calibration(self):
        self.calibrationWidget.show()

class Settings(Menu):

    def __init__(self):
        super().__init__()

        self.calibrationWidget = Calibration()

        self.add_button("Back")
class Customize(Menu):

    def __init__(self):
        super().__init__()

        self.calibrationWidget = Calibration()

        DEEPSEA_BLUE = (10,50,150)
        STEEL_GREY = (150,150,150)
        CREAMY_ORANGE = (150,100,50)
        LEAFY_GREEN = (100,150,100)

        self.add_custom(EyePilotButtonColorChoice("DeepSea Blue", id = "ColorChange", color=DEEPSEA_BLUE))
        self.add_custom(EyePilotButtonColorChoice("Steel Grey",   id = "ColorChange", color=STEEL_GREY))
        self.add_custom(EyePilotButtonColorChoice("Creamy Orange",id = "ColorChange", color=CREAMY_ORANGE))
        self.add_custom(EyePilotButtonColorChoice("Leafy Green",  id = "ColorChange", color=LEAFY_GREEN))

        self.add_button("Back")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())
