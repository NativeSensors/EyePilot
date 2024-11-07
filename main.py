import pyautogui
import time
import sys
import os

from PySide2.QtWidgets import QDesktopWidget, QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedLayout, QFrame, QPushButton, QLabel, QScrollBar
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QIcon

from BlurWindow.blurWindow import GlobalBlur
from components import EyePilotButton, EyePilotSwitch, EyePilotButtonColorChoice, EyePilotScroll
from calibration import Calibration
from blur import Blur

from contextTracker import VisContext

from dot import CircleWidget
from contextMenu import ContextMenu

from pywinauto import Application
import pygetwindow as gw
import pyautogui
import win32gui
import win32api
import win32con

def is_window_transparent(hwnd):
    # Get the extended window styles
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)

    # Check for WS_EX_LAYERED and WS_EX_TRANSPARENT
    # is_layered = ex_style & win32con.WS_EX_LAYERED
    is_transparent = ex_style & win32con.WS_EX_TRANSPARENT

    return is_transparent != 0

from tracker import Tracker

import ctypes

class ModelSaver:

    def __init__(self):
        self.model_name = "calibration_model.mdl"
        self.path = "__tmp"

    def isModel(self):
        model_path = os.path.join(self.path, self.model_name)
        return os.path.exists(model_path)

    def getModel(self):
        if self.isModel():
            model_path = os.path.join(self.path, self.model_name)
            with open(model_path, 'rb') as model_file:
                model_data = model_file.read()
            return model_data
        else:
            return None

    def saveModel(self, model_data):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        model_path = os.path.join(self.path, self.model_name)
        with open(model_path, 'wb') as model_file:
            model_file.write(model_data)

    def rmModel(self):
        model_path = os.path.join(self.path, self.model_name)
        if os.path.exists(model_path):
            os.remove(model_path)


class MyMainWindow(QMainWindow):

    def moveEvent(self, event) -> None:
        time.sleep(0.02)  # sleep for 20ms
        layout_center  = self.left_layout.geometry().center()
        self.tracker.setPosition(self.geometry().x() + 200, self.geometry().y() + 200)

    def resizeEvent(self, event) -> None:
        time.sleep(0.02)  # sleep for 20ms
        layout_center  = self.left_layout.geometry().center()
        self.tracker.setPosition(self.geometry().x() + 200, self.geometry().y() + 200)

    def __init__(self):
        super().__init__()
        # Determine the base path for the embedded files
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS  # Path to the folder where PyInstaller unpacks the files
        else:
            base_path = os.path.dirname(__file__)  # Path to the current directory

        # Construct the full path to the embedded image
        image_path = os.path.join(base_path, 'icon.png')
        self.setWindowIcon(QIcon(image_path))

        self.windowName = "EyeGesturesLab"
        self.setWindowTitle(self.windowName)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 800, 600)

        GlobalBlur(self.winId(),Dark=True,QWidget=self)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)

        # Create a frame to hold left side content
        left_frame = QFrame()
        main_layout.addWidget(left_frame, stretch=1)

        # Add a label to left frame (optional)
        self.label_left = QLabel("EyeGestures\nLAB")
        self.label_left.setStyleSheet("color: white; font-size: 40px;")
        self.label_left.setAlignment(Qt.AlignCenter)
        self.left_layout = QVBoxLayout()
        left_frame.setLayout(self.left_layout)
        self.left_layout.addWidget(self.label_left)

        # Create a frame to hold right side content
        right_frame = RightSideMenu()
        main_layout.addWidget(right_frame, stretch=1)

        self.tracker = CircleWidget("EyeGesturesCursor")
        layout_center  = self.left_layout.geometry().center()
        self.tracker.setPosition(self.geometry().x() + layout_center.x() + 200, self.geometry().y() + layout_center.y() + 200)
        self.tracker.setColor(150,0,100)
        self.tracker.setTransparency(0.5)
        self.tracker.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.tracker.show()

        # right_frame.setSignal("Customize","ColorChange",signal=self.changeTrackerColor)
        # right_frame.setSignal("Main","Calibration",signal=self.show_calibration)
        right_frame.setSignal("Main","Start",signal=self.start)
        right_frame.setSignal("Advanced","Enable focus",signal=self.switchFocus)
        right_frame.setSignal("Advanced","Enable Screen Lock",signal=self.switchScreenLock)
        right_frame.setSignal("Advanced","ScreenLockSeconds",signal=self.setScreenLockDuration)
        right_frame.setSignal("Advanced","Seconds",signal=self.setDuration)
        right_frame.setSignal("Advanced","Sensitivity",signal=self.setSensitivity)

        self.calibrationWidget = Calibration()
        self.calibrationWidget.setOnQuit(self.stop_calibration)

        # Start a timer to update the position periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.main_loop)
        self.timer.start(30)  # Update every second

        self.eyeTracker = Tracker()
        self.running = False
        self.calibrationON = False

        # self.vizContext = VisContext()
        # self.contextMenu = ContextMenu()

        self.model = ModelSaver()

        self.fix_start = time.time()

        desktop = QDesktopWidget()
        self.screen_geometry = desktop.screenGeometry(desktop.primaryScreen())

        self.calibration_points = 0
        self.prev_point = None
        self.blur_widget = Blur()
        self.blur_widget.setOnQuit(self.stop)

        self.time_start = time.time()
        self.duration_to_blur = 0

        self.focus = False
        self.screenLock = False
        self.screenLockCounter = time.time()
        self.screenLockTimeLimit = 15
        self.sensitivity = 1

        self.demo_start = time.time()
        self.demo_duration_max = 2 * 60
        self.fix_debounce = 51

        self.prev_cursor = pyautogui.position()


    def updateMainLabel(self,title):
        self.label_left.setText(f"{title}")

    def show_calibration(self):
        self.calibration_points = 0
        self.prev_point = None
        self.calibrationON = True
        self.eyeTracker.calibrationOn()
        self.calibrationWidget.show()
        self.tracker.show()

    def stop_calibration(self):
        modelData = self.eyeTracker.saveModel()
        # self.model.saveModel(modelData)

        self.calibrationON = False
        self.eyeTracker.calibrationOff()

    def changeTrackerColor(self,color):
        self.tracker.setColor(color[0],color[1],color[2])

    def press(self,x,y):
        pyautogui.moveTo(x, y)
        pyautogui.mouseDown()
        pyautogui.mouseUp()

    def get_circle_widget_handle(self):
        def enum_handler(hwnd, handles):
            if win32gui.IsWindowVisible(hwnd) and self.tracker.getWindowName() in win32gui.GetWindowText(hwnd):
                handles.append(hwnd)
        handles = []
        win32gui.EnumWindows(enum_handler, handles)
        return handles[0] if handles else None

    def get_handle(self):
        def enum_handler(hwnd, handles):
            if win32gui.IsWindowVisible(hwnd) and self.windowName in win32gui.GetWindowText(hwnd):
                handles.append(hwnd)
        handles = []
        win32gui.EnumWindows(enum_handler, handles)
        return handles[0] if handles else None

    def check_window(self,point):
        x = point[0]
        y = point[1]
        # Get all windows
        windows = gw.getAllWindows()

        cursor_handle = self.get_circle_widget_handle()

        # Iterate through all windows to find the one under the coordinates
        current_foreground = win32gui.GetForegroundWindow()
        ctypes.windll.user32.SetForegroundWindow(self.get_handle())
        ctypes.windll.user32.SetActiveWindow(self.get_handle())

        print(f"current_foreground {current_foreground}")
        for window in windows:
            if cursor_handle != window._hWnd and window.left <= x <= window.right and window.top <= y <= window.bottom:
                print(win32gui.IsWindowVisible(window._hWnd), not win32gui.IsIconic(window._hWnd))

                if not is_window_transparent(window._hWnd) and win32gui.IsWindowVisible(window._hWnd) and not win32gui.IsIconic(window._hWnd):
                    # Click near the center of the window to focus it
                    ctypes.windll.user32.SetForegroundWindow(window._hWnd)
                    ctypes.windll.user32.SetActiveWindow(window._hWnd)
                    app = Application().connect(handle=window._hWnd)
                    app.top_window().set_focus()  # Ensure the correct window is focused
                    print(f"seting foreground for {window}")
                    return True
        return False

    def main_loop(self):
        # if (time.time() - self.demo_start) > self.demo_duration_max:
        #     self.stop(None)
        #     self.close()
        #     return

        # time_left = self.demo_duration_max - (time.time() - self.demo_start)
        # self.updateMainLabel(f"EyeFocus\nDemo time left\n{int(time_left/60)}:{int(time_left%60)}")
        new_cursor = pyautogui.position()
        if self.prev_cursor.x != new_cursor.x or self.prev_cursor.y != new_cursor.y:
            self.prev_cursor = new_cursor
            self.fix_debounce = 0
            time.sleep(0.1)
        elif self.running:
            point, calibration, blink, fix, acceptance_radius, calibration_radius = self.eyeTracker.step()

            self.tracker.setPosition(point[0], point[1])

            if self.prev_point == None:
                self.prev_point = (calibration[0], calibration[1])
                self.calibration_points += 1

            if self.calibrationON:
                self.calibrationWidget.setPosition(calibration[0], calibration[1])
                self.calibrationWidget.setRadius(2*calibration_radius)
                self.calibrationWidget.setPositionFit(calibration[0], calibration[1])
                self.calibrationWidget.setRadiusFit(2*acceptance_radius)

                if self.prev_point[0] != calibration[0] and self.prev_point[1] != calibration[1]:
                    self.prev_point = (calibration[0], calibration[1])
                    self.calibration_points += 1

                if self.calibration_points >= 10:
                    self.calibrationWidget.quit()
                    # self.tracker.close()
            else:
                if self.fix_debounce > 100:
                    self.check_window(point)
                    self.fix_debounce = 0
                else:
                    self.fix_debounce += 1

    def switchFocus(self,button):
        self.focus = not self.focus
        if self.focus:
            button.update_text("Disable focus")
        else:
            button.update_text("Enable focus")

    def switchScreenLock(self,button):
        self.screenLock = not self.screenLock
        if self.screenLock:
            button.update_text("Disable Screen Lock")
        else:
            button.update_text("Enable Screen Lock")

    def setFixation(self,fix):
        self.eyeTracker.setFixation(fix/10)

    def setDuration(self,duration):
        self.duration_to_blur = duration

    def setScreenLockDuration(self,duration):
        self.screenLockTimeLimit = duration

    def setSensitivity(self,sensitivity):
        self.sensitivity = sensitivity

    def resetTracker(self):
        self.model.rmModel()
        self.eyeTracker.reset()

    def start(self,element):
        modelData = self.model.getModel()
        self.eyeTracker.start()
        # if modelData is None:
        self.show_calibration()
        # else:
        #     self.eyeTracker.loadModel(modelData)
        self.running = True

    def stop(self,element):
        self.running = False
        self.eyeTracker.stop()
        self.tracker.close()

    def closeEvent(self, event):
        # Call your function or perform cleanup here
        self.stop(None)
        # Call the base class closeEvent to ensure default behavior
        super().closeEvent(event)
        quit()

class RightSideMenu(QFrame):
    def __init__(self):
        super().__init__()

        self.menu_stack  = QStackedLayout()
        self.setLayout(self.menu_stack)
        self.setStyleSheet("background-color: rgba(26, 32, 48, 0.8);")

        self.mainMenu = MainMenu()
        self.advanced = Advanced()
        # self.customize = Customize()

        self.__allMenus = {
            "Main" : self.mainMenu,
            "Advanced" : self.advanced,
            # "Customize" : self.customize
        }

        self.menu_stack.addWidget(self.mainMenu)
        self.menu_stack.addWidget(self.advanced)
        # self.menu_stack.addWidget(self.customize)
        self.menu_stack.setCurrentIndex(0)
        self.menus = 2

        self.mainMenu.setSignal("Advanced", lambda _ : self.switchMenu(1))
        self.advanced.setSignal("Back", lambda _ : self.switchMenu(0))


    def switchMenu(self,index):
        if self.menus <= index:
            return

        self.menu_stack.setCurrentIndex(index)

    def setSignal(self,menu_name,name,signal):
        self.__allMenus[menu_name].setSignal(name,signal)

class Menu(QFrame):

    def __init__(self):
        super().__init__()

        self.right_layout = QVBoxLayout()
        self.right_layout.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.setLayout(self.right_layout)

        self.right_buttons = []

    def setSignal(self,button_name, signal):
        buttons = [button for button in self.right_buttons if button.getID() == button_name]
        for button in buttons:
            button.addSignal(signal)

    def add_button(self,name,signal=None):
        tmp_layout = QHBoxLayout()
        tmp_layout.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.right_buttons.append(EyePilotButton(name,signal = signal))
        tmp_layout.addWidget(self.right_buttons[-1])
        self.right_layout.addLayout(tmp_layout)

    def add_switch(self,name,signal=None):
        tmp_layout = QHBoxLayout()
        tmp_layout.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.right_buttons.append(EyePilotSwitch(name,signal = signal))
        tmp_layout.addWidget(self.right_buttons[-1])
        self.right_layout.addLayout(tmp_layout)

    def add_custom(self,button):
        tmp_layout = QHBoxLayout()
        self.right_buttons.append(button)
        tmp_layout.addWidget(self.right_buttons[-1])
        self.right_layout.addLayout(tmp_layout)

class MainMenu(Menu):

    def __init__(self):
        super().__init__()

        self.add_button("Start")
        self.add_button("Advanced")

class Advanced(Menu):

    def __init__(self):
        super().__init__()

        self.add_button("Enable focus")
        self.add_button("Enable Screen Lock")
        self.add_custom(EyePilotScroll("Screen lock [s]","ScreenLockSeconds",init=15, start=0, end=60))
        self.add_custom(EyePilotScroll("Duration to blur [s]","Seconds",init=0,start=0, end=60))
        self.add_custom(EyePilotScroll("Sensitivity","Sensitivity",init=1,start=1, end=10))
        self.add_button("Back")


if __name__ == "__main__":
    # sys.stdout = open(os.devnull, 'w')

    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())
