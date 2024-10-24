import sys
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PySide2.QtGui import QPainter, QColor, QBrush, QPen, QIcon, QPixmap
from PySide2.QtCore import Qt, QTimer
from  components import EyePilotButton
from PySide2.QtSvg import QSvgWidget

import time
import random
import resources_rc  # Import the compiled resource file
class ContextMenuBtn(QWidget):
    def __init__(self,text,x,y,radius=300,signal= lambda x : x):
        super().__init__()
        self.setWindowIcon(QIcon(":/icon.png"))

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.btn = EyePilotButton("",
                                fontColor = "rgba(200, 200, 200)",
                                color="rgba(150, 150, 150)",
                                colorHover1 = "rgba(150, 150, 150)",
                                colorHover2 = "rgba(150, 150, 150)",
                                width="150px",
                                max_width="900px",
                                height="150px",
                                border="1px solid rgba(100, 100, 100)",
                                border_radius="50%",
                                signal=signal)
        self.layout.addWidget(self.btn)
        self.setLayout(self.layout)

        # self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.x = x
        self.y = y
        self.width = 200
        self.height = 100
        self.radius = radius

        self.setGeometry(x, y, self.width, self.height)

        self.to_y = y
        self.to_x = x

    def setImage(self,path):
        self.btn.setImage(path)

    def setPosition(self,x,y):
        self.to_x = x - self.diameter/2
        self.to_y = y - self.diameter/2

    def setText(self,text):
        self.btn.setText(text)

    def setImage(self,path):
        self.btn.setImage(path)

    def setTransparency(self,transparency):
        self.transparency = transparency
        if self.transparency > 0:
            self.penWidth = 2
        elif self.transparency == 0:
            self.penWidth = 0
        else:
            self.penWidth = -1

        self.setColor(self.brush_color.red(),self.brush_color.green(),self.brush_color.blue())

    def changeColor(self,color):
        self.btn.updateColor(color)

class ContextMenu(QWidget):

    def __init__(self,
                screen_center,
                signal_1 = lambda x : x,
                signal_2 = lambda x : x,
                signal_3 = lambda x : x,
                signal_4 = lambda x : x) -> None:
        x = screen_center[0]
        y = screen_center[1]
        self.btn1 = ContextMenuBtn("Button 1",x-300,y+300, signal = signal_1)
        self.btn2 = ContextMenuBtn("Button 2",x-300,y-300, signal = signal_2)
        self.btn3 = ContextMenuBtn("Button 3",x+300,y+300, signal = signal_3)
        self.btn4 = ContextMenuBtn("Button 4",x+300,y-300, signal = signal_4)

        self.btn2.setImage(":/assets/mouse-duotone.svg")
        self.btn4.setImage(":/assets/mouse-right-click-duotone.svg")
        self.btn1.setImage(":/assets/x-circle.svg")
        self.btn3.setImage(":/assets/ellipsis-horizontal-circle-20-solid.svg")
        self.activated = False

    def execute(self, cursor):
        x = cursor[0]
        y = cursor[1]

        for btn in [self.btn1, self.btn2, self.btn3, self.btn4]:
            if (x - btn.x)**2 + (y - btn.y)**2  < (btn.radius)**2:
                btn.changeColor("rgba(160,100,0)")
                print("changing color")
            else:
                btn.changeColor("rgba(150,150,150)")

    def launch(self):
        self.activated = True
        self.show()

    def close(self):
        self.activated = False
        self.hide()

    def show(self):
        self.btn1.show()
        self.btn2.show()
        self.btn3.show()
        self.btn4.show()

    def hide(self):
        self.btn1.hide()
        self.btn2.hide()
        self.btn3.hide()
        self.btn4.hide()

    def setText(self,t1,t2,t3,t4):
        self.btn1.setText(t1)
        self.btn2.setText(t2)
        self.btn3.setText(t3)
        self.btn4.setText(t4)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    menu = ContextMenu([1250,600])

    menu.show()

    sys.exit(app.exec_())