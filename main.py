import time
import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QPushButton, QLabel, QToolBar
from PySide2.QtCore import Qt

from BlurWindow.blurWindow import GlobalBlur

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

        # Apply stylesheet to mimic system colors for title bar

        GlobalBlur(self.winId(),Dark=True,QWidget=self)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)

        # Create a frame to hold left side content
        left_frame = QFrame()
        main_layout.addWidget(left_frame, stretch=0)

        # Add a label to left frame (optional)
        label_left = QLabel("EyePilot")
        label_left.setStyleSheet("color: white; font-size: 40px;")
        label_left.setAlignment(Qt.AlignCenter)
        left_layout = QVBoxLayout()
        left_frame.setLayout(left_layout)
        left_layout.addWidget(label_left)

        # Create a frame to hold right side content
        right_frame = QFrame()
        main_layout.addWidget(right_frame, stretch=0)

        # Add buttons and options to the right frame
        button1 = QPushButton("Calibration")
        button2 = QPushButton("Settings")
        button3 = QPushButton("Some more text")

        button_style = """
            QPushButton {
                color: Black;
                font-size: 20px;
                background-color: rgba(255, 255, 255, 0.0);
                width: 200px;
            }

            QPushButton:hover {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 rgba(255, 255, 255, 0.5), stop:1 rgba(255, 255, 255, 0.3), stop:2 rgba(255, 255, 2, 0.0));
                border-radius: 5px;
            }
        """

        button1.setStyleSheet(button_style)
        button2.setStyleSheet(button_style)
        button3.setStyleSheet(button_style)

        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignCenter)
        right_frame.setStyleSheet("background-color: rgba(255, 255, 255, 0.2);")
        right_frame.setLayout(right_layout)
        right_layout.addWidget(button1)
        right_layout.addWidget(button2)
        right_layout.addWidget(button3)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())
