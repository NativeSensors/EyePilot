import sys
from PySide2.QtWidgets import QApplication, QWidget, QHBoxLayout
from PySide2.QtCore import Qt, QTimer

from BlurWindow.blurWindow import GlobalBlur
from components import EyePilotButton
from dot import CircleWidget

import random

class Calibration(QWidget):
    def __init__(self):
        super().__init__()
        self.onQuit = None

        # Set the window title
        self.setWindowTitle("Full Screen Widget")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 800, 600)

        main_layout = QHBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)  # Center align the items
        self.setLayout(main_layout)

        # Apply stylesheet to mimic system colors for title bar

        GlobalBlur(self.winId(),Dark=True,QWidget=self)

        main_layout.addWidget(EyePilotButton("Quit", signal = self.quit))
        self.setFullScreen()

        self.calibration_point = CircleWidget()
        self.calibration_point.setColor(255,0,0)
        self.calibration_point.show()
        self.calibration_point.setParent(self)

        self.point = CircleWidget()
        self.point.setColor(120,60,0)
        self.point.show()
        self.point.setParent(self)
        # main_layout.addWidget(self.calibration_point)
        # Set the window size to full screen

        self.max_points = 14
        self.point_counter = 0
        self.prev_x = 0
        self.prev_y = 0

    def reset(self):
        self.point_counter = 0

    def setFullScreen(self):
        # Get the primary screen
        screen = QApplication.primaryScreen()

        # Get the geometry of the screen
        screen_geometry = screen.geometry()

        # Set the size of the widget to match the screen size
        self.setGeometry(screen_geometry)

    def setPositionFit(self,x,y):
        self.calibration_point.setPosition(x,y)

    def setRadiusFit(self,r):
        self.calibration_point.setRadius(r)

    def setPosition(self,x,y):
        if x != self.prev_x or y != self.prev_y:
            self.prev_y = y
            self.prev_x = x
            self.point_counter += 1
            if self.point_counter > self.max_points:
                self.quit()
        self.point.setPosition(x,y)

    def setRadius(self,r):
        self.point.setRadius(r)

    def quit(self):
        if self.onQuit:
            self.onQuit()
        self.close()

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
