from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PySide2.QtCore import QPropertyAnimation, QPoint, Qt
from PySide2.QtGui import QPainter, QColor

class ToggleButton(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the main toggle button's appearance
        self.length = 100
        self.radius = 30
        self.setFixedSize(self.length, self.radius)

        # Create the dot that will move on toggle
        self.dot = QPushButton(self)
        self.dot.setFixedSize(self.radius - 2, self.radius-2)
        self.dot.setStyleSheet("background-color: #ff0064; border-radius: 14px;")
        self.dot.move(2, 1)  # Initial position on the left

        # Make the dot transparent to mouse events
        self.dot.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        # Initialize the toggle state
        self.is_toggled = False

        # Set up animation for moving the dot
        self.animation = QPropertyAnimation(self.dot, b"pos")
        self.animation.setDuration(200)  # Animation duration (200 ms)

    def paintEvent(self, event):
        """Override the paint event to draw a background rail."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Set color based on toggle state
        rail_color = QColor("#6400fa") if self.is_toggled else QColor("lightgray")
        painter.setBrush(rail_color)

        # Draw the rail (background rectangle with rounded corners)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 15, 15)

    def mousePressEvent(self, event):
        """Override the mouse press event to toggle the switch."""
        # Toggle the state
        self.is_toggled = not self.is_toggled

        # Determine start and end positions for the dot animation
        if self.is_toggled:
            end_pos = QPoint(self.length-self.radius, 1)  # Move to the right
        else:
            end_pos = QPoint(2, 1)  # Move to the left

        # Animate the dot's position
        self.animation.setEndValue(end_pos)
        self.animation.start()

        # Trigger repaint to update the rail color
        self.update()

    def status(self):
        return self.is_toggled

class ToggleButtonDemo(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the main layout for the demo
        layout = QVBoxLayout()

        # Create two custom toggle buttons
        self.toggle_button_1 = ToggleButton()
        self.toggle_button_2 = ToggleButton()

        # Add the toggle buttons to the layout
        layout.addWidget(self.toggle_button_1)
        layout.addWidget(self.toggle_button_2)

        # Set layout and window title
        self.setLayout(layout)
        self.setWindowTitle("Animated Toggle Buttons with Moving Dot and Rail")


# Run the application
if __name__ == "__main__":
    app = QApplication([])
    window = ToggleButtonDemo()
    window.show()
    app.exec_()
