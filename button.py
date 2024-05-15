from PySide2.QtWidgets import QApplication, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy
from PySide2.QtCore import Qt
from dot import CircleWidget

class EyePilotButton(QPushButton):
    def __init__(self, text, id = None, signal=None, parent=None):
        super().__init__(text, parent)

        # Set the style
        button_style = """
            QPushButton {
                color: white;
                font-size: 25px;
                background-color: rgba(255, 255, 255, 0.0);
                width: 200px;
                height: 45px;
                max-width: 200px;
                margin-left: auto;
                margin-right: auto;
            }

            QPushButton:hover {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 rgba(56, 60, 79, 0.5), stop:1 rgba(56, 60, 79, 0.3));
                border-radius: 5px;
            }
        """

        self.text = text
        if id is None:
            self.id = text

        self.setStyleSheet(button_style)
        self.signal = signal
        self.clicked.connect(self.click)

    def click(self):

        if self.signal:
            self.signal()

    def addSignal(self,signal):
        self.signal = signal

    def getText(self):
        return self.text

    def getID(self):
        return self.id

class EyePilotButtonColorChoice(QPushButton):
    def __init__(self, text, id = None, signal=None, color = (45,45,45), parent=None):
        super().__init__(text,parent)
        self.text = text
        if id is None:
            self.id = text
        self.id = id
        # Set the style
        button_style = """
            QPushButton {
                color: white;
                font-size: 25px;
                background-color: rgba(255, 255, 255, 0.0);
                width: 300px;
                height: 100px;
                min-height: 100px;
                padding-left: 50px;
            }

            QPushButton:hover {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 rgba(56, 60, 79, 0.5), stop:1 rgba(56, 60, 79, 0.3));
                border-radius: 5px;
            }

        """

        self.setStyleSheet(button_style)
        self.signal = signal
        self.color = color

        self.model_dot = CircleWidget()
        layout_center  = self.geometry().center()
        self.model_dot.setPosition(10,25)
        self.model_dot.setColor(color[0],color[1],color[2])
        self.model_dot.setParent(self)
        self.clicked.connect(self.click)

    def click(self):
        if self.signal:
            self.signal(self.color)

    def addSignal(self,signal):
        self.signal = signal

    def getText(self):
        return self.text

    def getID(self):
        return self.id