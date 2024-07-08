import sys
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide2.QtGui import QPainter, QColor, QBrush, QPen, QIcon
from PySide2.QtCore import Qt, QTimer
from  components import EyePilotButton

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

    def setTransparency(self,transparency):
        self.transparency = transparency
        if self.transparency > 0:
            self.penWidth = 2
        elif self.transparency == 0:
            self.penWidth = 0
        else:
            self.penWidth = -1

        self.setColor(self.brush_color.red(),self.brush_color.green(),self.brush_color.blue())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    btn1 = ContextMenuBtn("Lorem ipsum morem solem",100,100)
    btn1.show()
    btn2 = ContextMenuBtn("Lorem ipsum morem solem",150,300)
    btn2.show()
    btn3 = ContextMenuBtn("Lorem ipsum morem solem",200,500)
    btn3.show()
    btn4 = ContextMenuBtn("Lorem ipsum morem solem",300,700)
    btn4.show()
    sys.exit(app.exec_())