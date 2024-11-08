from PySide2.QtWidgets import QApplication, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QScrollBar, QLabel
from PySide2.QtGui import QPainter, QIcon, QPixmap
from PySide2.QtSvg import QSvgRenderer
from PySide2.QtCore import Qt, QSize

from dot import CircleWidget

class EyePilotComponent():

    def __init__(self, text, id = None):
        self.text = text
        if id is None:
            self.id = text
        else:
            self.id = id
        self.signal = None

    def addSignal(self,signal):
        self.signal = signal

    def getText(self):
        return self.text

    def getID(self):
        return self.id

class EyePilotButtonComponent(EyePilotComponent,QPushButton):

    def __init__(self, text, id = None, parent=None):
        super().__init__(text, id)
        super(EyePilotComponent, self).__init__(text, parent)

class ScrollBarWithText(QScrollBar):
    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text

    def update_text(self,text):
        self.text = text

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        font_metrics = painter.fontMetrics()
        text_width = font_metrics.width(self.text)
        text_height = font_metrics.height()

        # Calculate position to center the text
        x = (self.width() - text_width) // 2
        y = (self.height() + text_height) // 2

        # Draw the text
        painter.drawText(x, y, self.text)

class EyePilotScrollComponent(EyePilotComponent,QWidget):

    def __init__(self, text, id = None, parent=None):
        super().__init__(text, id)
        super(EyePilotComponent, self).__init__()


class EyePilotButton(EyePilotButtonComponent):
    def __init__(self, text, id = None, signal=None, parent=None,
                fontColor = "white",
                color = "rgba(255, 255, 255, 0.0)",
                colorHover1 = "rgba(56, 60, 79, 0.5)",
                colorHover2 = "rgba(56, 60, 79, 0.3)",
                width = "200px",
                height = "45px",
                max_width = "200px",
                border_radius = "5px",
                border = "0px solid #FF000000"):
        super().__init__(text, id, parent)

        self.fontColor = fontColor
        self.color = color
        self.colorHover1 = colorHover1
        self.colorHover2 = colorHover2
        self.width = width
        self.height = height
        self.max_width = max_width
        self.border_radius = border_radius
        self.border = border
        # Set the style
        button_style = f"""
            QPushButton {{
                color: {fontColor};
                font-size: 25px;
                background-color: {color};
                width: {width};
                height: {height};
                max-width: {max_width};
                margin-left: auto;
                margin-right: auto;
                border-radius: {border_radius};
                border: {border};
            }}

            QPushButton:hover {{
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 {colorHover1}, stop:1 {colorHover2});
                border-radius: {border_radius};
            }}
        """

        self.setStyleSheet(button_style)
        self.signal = signal
        self.clicked.connect(self.click)

    def setImage(self,image_path):
        svg_renderer = QSvgRenderer(image_path)
        pixmap = QPixmap(100, 100)  # Set size of the icon
        pixmap.fill(Qt.transparent) # Ensure transparency
        painter = QPainter(pixmap)
        svg_renderer.render(painter)
        painter.end()

        # Set the SVG as an icon
        icon = QIcon(pixmap)
        self.setIcon(icon)
        self.setIconSize(QSize(100, 100))

    def updateColor(self,color):
                # Set the style
        self.color = color
        button_style = f"""
            QPushButton {{
                color: {self.fontColor};
                font-size: 25px;
                background-color: {self.color};
                width: {self.width};
                height: {self.height};
                max-width: {self.max_width};
                margin-left: auto;
                margin-right: auto;
                border-radius: {self.border_radius};
                border: {self.border};
            }}

            QPushButton:hover {{
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 {self.colorHover1}, stop:1 {self.colorHover2});
                border-radius: {self.border_radius};
            }}
        """

        self.setStyleSheet(button_style)

    def update_text(self, new_text):
        self.setText(new_text)

    def click(self):
        if self.signal:
            self.signal()


class EyePilotButton(EyePilotButtonComponent):
    def __init__(self, text, id = None, signal=None, parent=None,
                fontColor = "white",
                color = "rgba(255, 255, 255, 0.0)",
                colorHover1 = "rgba(56, 60, 79, 0.5)",
                colorHover2 = "rgba(56, 60, 79, 0.3)",
                width = "200px",
                height = "45px",
                max_width = "200px",
                border_radius = "5px",
                border = "0px solid #FF000000"):
        super().__init__(text, id, parent)

        self.fontColor = fontColor
        self.color = color
        self.colorHover1 = colorHover1
        self.colorHover2 = colorHover2
        self.width = width
        self.height = height
        self.max_width = max_width
        self.border_radius = border_radius
        self.border = border
        # Set the style
        button_style = f"""
            QPushButton {{
                color: {fontColor};
                font-size: 25px;
                background-color: {color};
                width: {width};
                height: {height};
                max-width: {max_width};
                margin-left: auto;
                margin-right: auto;
                border-radius: {border_radius};
                border: {border};
            }}

            QPushButton:hover {{
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 {colorHover1}, stop:1 {colorHover2});
                border-radius: {border_radius};
            }}
        """

        self.setStyleSheet(button_style)
        self.signal = signal
        self.clicked.connect(self.click)

    def setImage(self,image_path):
        svg_renderer = QSvgRenderer(image_path)
        pixmap = QPixmap(100, 100)  # Set size of the icon
        pixmap.fill(Qt.transparent) # Ensure transparency
        painter = QPainter(pixmap)
        svg_renderer.render(painter)
        painter.end()

        # Set the SVG as an icon
        icon = QIcon(pixmap)
        self.setIcon(icon)
        self.setIconSize(QSize(100, 100))

    def updateColor(self,color):
                # Set the style
        self.color = color
        button_style = f"""
            QPushButton {{
                color: {self.fontColor};
                font-size: 25px;
                background-color: {self.color};
                width: {self.width};
                height: {self.height};
                max-width: {self.max_width};
                margin-left: auto;
                margin-right: auto;
                border-radius: {self.border_radius};
                border: {self.border};
            }}

            QPushButton:hover {{
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 {self.colorHover1}, stop:1 {self.colorHover2});
                border-radius: {self.border_radius};
            }}
        """

        self.setStyleSheet(button_style)

    def update_text(self, new_text):
        self.setText(new_text)

    def click(self):
        if self.signal:
            self.signal()

class EyePilotButtonColorChoice(EyePilotButtonComponent):
    def __init__(self, text, id = None, signal=None, color = (45,45,45), parent=None):
        super().__init__(text,id,parent)

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
        self.model_dot.setPosition(50,50)
        self.model_dot.setColor(color[0],color[1],color[2])
        self.model_dot.setParent(self)
        self.clicked.connect(self.click)

    def click(self):
        if self.signal:
            self.signal(self.color)


class EyePilotScroll(EyePilotScrollComponent):
    def __init__(self, text, id = None, signal=None, start=1, init=1, end=10, parent=None):
        super().__init__(text,id,parent)

        # Set the style
        scroll_styele = """
            QScrollBar {
                color: black;
                font-size: 25px;
                min-height: 60px;
                background-color: rgba(255, 255, 255, 0.0);

            }

            QScrollBar:horizontal {
                background: white;
                height: 15px;
                margin: 0px 40px 0 40px;
            }

            QScrollBar::add-line:horizontal {
                background: white;
                width: 40px;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
                subcontrol-position: right;
                subcontrol-origin: margin;
            }

            QScrollBar::sub-line:horizontal {
                background: white;
                width: 40px;
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
                subcontrol-position: left;
                subcontrol-origin: margin;
            }

            QScrollBar::handle:horizontal {
                background: rgba(56, 60, 79, 0.5);
                min-width: 20px;
            }
            QScrollBar::left-arrow:horizontal {
                min-width: 40px;
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
                background: rgba(150,10,10, 0.2);
            }
            QScrollBar::right-arrow:horizontal {
                min-width: 40px;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
                background: rgba(10,50,150, 0.2);
            }

            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """
        label_style = """
            QLabel {
                color: white;
                font-size: 25px;
                margin-left: auto;
                margin-right: auto;
            }
        """
        main_layout = QHBoxLayout(self)
        v_container = QWidget()
        self.layout = QVBoxLayout(v_container)

        self.label = QLabel(self.text)
        self.label.setStyleSheet(label_style)

        self.scrollbar = ScrollBarWithText(f"{init}")
        self.scrollbar.setMinimum(start)
        self.scrollbar.setMaximum(end)
        self.scrollbar.setValue(init)
        self.scrollbar.setOrientation(Qt.Horizontal)  # Vertical orientation
        self.scrollbar.valueChanged.connect(self.on_change)

        self.scrollbar.setStyleSheet(scroll_styele)


        self.layout.addWidget(self.label)
        self.layout.addWidget(self.scrollbar)
        # self.setLayout(self.layout)
        main_layout.addWidget(v_container)


    def on_change(self,value):
        if self.signal:
            self.signal(value)
        self.scrollbar.update_text(f"{value}")
