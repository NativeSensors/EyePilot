import sys
from PySide2.QtWidgets import QDesktopWidget, QApplication, QWidget, QHBoxLayout
from PySide2.QtCore import Qt, QTimer

from BlurWindow.blurWindow import GlobalBlur
from components import EyePilotButton
from dot import CircleWidget

import random

class BlurPerScreen(QWidget):

    def __init__(self, screen):
        super().__init__()
        self.onQuit = None
        self.onQuitBtnSig = None
        self.screen = screen

        # Set the window title
        self.setWindowTitle("Full Screen Widget")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(self.screen.geometry())

        main_layout = QHBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)  # Center align the items
        self.setLayout(main_layout)

        # Apply stylesheet to mimic system colors for title bar

        GlobalBlur(self.winId(),Dark=True,QWidget=self)

        main_layout.addWidget(EyePilotButton("Quit", signal = self.__onQuitBtnWrapper))
        self.setFullScreen()

        # main_layout.addWidget(self.calibration_point)
        # Set the window size to full screen

    def setFullScreen(self):
        self.setGeometry(self.screen.geometry())
        # Initialize total geometry

    def quit(self):
        if self.onQuit:
            self.onQuit()
        self.close()

    def setOnQuit(self,signal):
        self.onQuit = signal

    def __onQuitBtnWrapper(self,element):
        if self.onQuitBtnSig:
            self.onQuitBtnSig(self)
        self.quit()

    def setOnQuitBtn(self,signal):
        self.onQuitBtnSig = signal


class Blur():
    def __init__(self):
        self.onQuit = None
        self.screens_blurs = []
        self.displaying = False

    def show(self):
        if not self.displaying:
            self.displaying = True
            self.setFullScreen()

    def setFullScreen(self):
        # Get the primary screen
        screens = QApplication.screens()
        # num_screens = desktop.screenCount()
        self.screens_blurs = []
        for screen in screens:
            bps = BlurPerScreen(screen)
            bps.setOnQuitBtn(self.onQuit)
            bps.setOnQuit(self.quit)
            self.screens_blurs.append(bps)

        for screen in self.screens_blurs:
            screen.setFullScreen()
            screen.show()


    def quit(self,*args, **kwargs):
        if self.displaying:
            for screen in self.screens_blurs:
                try:
                    screen.quit()
                except:
                    pass

            self.displaying = False

    def setOnQuit(self,signal):
        self.onQuit = signal

if __name__ == "__main__":
    # Create the application
    app = QApplication(sys.argv)

    # Create and show the full screen widget
    widget = Calibration()
    widget.show()

    # Start the event loop
    sys.exit(app.exec_())
