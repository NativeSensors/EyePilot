import sys
from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtGui import QPainter, QColor, QBrush, QPen, QIcon
from PySide2.QtCore import Qt, QTimer
import random
import resources_rc  # Import the compiled resource file

class CircleWidget(QWidget):
    def __init__(self,name="CircleWidget"):
        super().__init__()
        self.setWindowIcon(QIcon(":/icon.png"))

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setGeometry(0, 0, 60, 60)
        self.windowName = name
        self.setWindowTitle(self.windowName)


        self.diameter = 100
        self.transparency = 50
        self.penWidth = 2

        self.setColor(100, 0, 255)

        self.to_y = self.x()
        self.to_x = self.y()

        # Start a timer to update the position periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(30)  # Update every second

    def getWindowName(self):
        return self.windowName

    def update_position(self):
        # Randomly generate new position within the screen boundaries
        new_x = self.to_x
        new_y = self.to_y

        if self.geometry().width() != self.diameter + 10:
            self.setGeometry(0, 0, self.diameter + 10, self.diameter + 10)
        self.move(new_x, new_y)
        self.repaint()

    def setPosition(self,x,y):
        self.to_x = x - self.diameter/2
        self.to_y = y - self.diameter/2

    def setRadius(self,diameter):
        self.diameter = diameter

    def setColor(self,r,g,b):
        self.brush_color = QColor(r,g,b, self.transparency)
        self.pen_color = QColor(r, g, b)  # Red color for the border

    def setTransparency(self,transparency):
        self.transparency = transparency
        if self.transparency > 0:
            self.penWidth = 2
        elif self.transparency == 0:
            self.penWidth = 0
        else:
            self.penWidth = -1

        self.setColor(self.brush_color.red(),self.brush_color.green(),self.brush_color.blue())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # brush_color = QColor(18, 34, 78, 50)  # Semi-transparent red color
        brush = QBrush(self.brush_color)
        painter.setBrush(brush)
        # Set the pen color and width
        pen_width = self.penWidth  # Width of the border
        pen = QPen(self.pen_color, pen_width)
        painter.setPen(pen)

        # Draw a circle
        painter.drawEllipse((self.width() - self.diameter) / 2, (self.height() - self.diameter) / 2, self.diameter, self.diameter)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CircleWidget()
    window.show()
    sys.exit(app.exec_())