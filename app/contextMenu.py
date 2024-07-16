import sys
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide2.QtGui import QPainter, QColor, QBrush, QPen, QIcon
from PySide2.QtCore import Qt, QTimer
from  components import EyePilotButton

import time
import random
import resources_rc  # Import the compiled resource file
class ContextMenuBtn(QWidget):
    def __init__(self,text,x,y):
        super().__init__()
        self.setWindowIcon(QIcon(":/icon.png"))

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.btn = EyePilotButton(text,
                                fontColor = "rgba(200, 200, 200)",
                                color="rgba(41, 44, 51)",
                                colorHover1 = "rgba(41, 44, 51)",
                                colorHover2 = "rgba(41, 44, 51)",
                                width="700px",
                                max_width="900px",
                                height="90px",
                                border="1px solid rgba(100, 100, 100)",
                                border_radius="25px")
        self.layout.addWidget(self.btn)
        self.setLayout(self.layout)

        # self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.width = 200
        self.height = 100

        self.setGeometry(x, y, self.width, self.height)

        self.to_y = y
        self.to_x = x

    def setPosition(self,x,y):
        self.to_x = x - self.diameter/2
        self.to_y = y - self.diameter/2

    def setText(self,text):
        self.btn.setText(text)

    def setTransparency(self,transparency):
        self.transparency = transparency
        if self.transparency > 0:
            self.penWidth = 2
        elif self.transparency == 0:
            self.penWidth = 0
        else:
            self.penWidth = -1

        self.setColor(self.brush_color.red(),self.brush_color.green(),self.brush_color.blue())

class ContextMenu(QWidget):

    def __init__(self) -> None:
        self.btn1 = ContextMenuBtn("Lorem ipsum morem solem",100,100)
        self.btn2 = ContextMenuBtn("Lorem ipsum morem solem",150,300)
        self.btn3 = ContextMenuBtn("Lorem ipsum morem solem",200,500)
        self.btn4 = ContextMenuBtn("Lorem ipsum morem solem",300,700)

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
    menu = ContextMenu()

    menu.show()
    menu.setText("Text1","Text2","Text3","Text4")
    # for n in range(10):
    # menu.hide()
    menu.show()
    menu.setText("Text1","Text2","Text3","LOL4")

    sys.exit(app.exec_())