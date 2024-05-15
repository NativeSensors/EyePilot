import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, QColorDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Color Palette Editor")
        
        self.button = QPushButton("Select Color", self)
        self.button.clicked.connect(self.openColorDialog)
        self.setCentralWidget(self.button)

    def openColorDialog(self):
        color = QColorDialog.getColor()
        if color.isValid():
            print("Selected color:", color.name())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
