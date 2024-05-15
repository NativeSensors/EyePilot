import sys
from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtGui import QPainter, QColor, QBrush, QPen, QIcon
from PySide2.QtCore import Qt, QTimer
import random

class CircleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("icon.png"))

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setGeometry(0, 0, 60, 60)

        self.setColor(35, 67, 154)

        self.to_y = self.x()
        self.to_x = self.y()

        # Start a timer to update the position periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(30)  # Update every second

    def update_position(self):
        # Randomly generate new position within the screen boundaries
        new_x = self.to_x
        new_y = self.to_y
        self.move(new_x, new_y)
        self.repaint()

    def setPosition(self,x,y):
        self.to_x = x
        self.to_y = y

    def setColor(self,r,g,b):
        self.brush_color = QColor(r,g,b, 50)
        self.pen_color = QColor(r, g, b)  # Red color for the border

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # brush_color = QColor(18, 34, 78, 50)  # Semi-transparent red color
        brush = QBrush(self.brush_color)
        painter.setBrush(brush)
        # Set the pen color and width
        pen_width = 2  # Width of the border
        pen = QPen(self.pen_color, pen_width)
        painter.setPen(pen)

        # Draw a circle
        diameter = 50
        painter.drawEllipse((self.width() - diameter) / 2, (self.height() - diameter) / 2, diameter, diameter)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CircleWidget()
    window.show()
    sys.exit(app.exec_())