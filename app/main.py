import pyautogui
import time
import sys
import os

from PySide2.QtWidgets import QDesktopWidget, QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedLayout, QFrame, QPushButton, QLabel, QScrollBar
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QIcon
import resources_rc  # Import the compiled resource file

from BlurWindow.blurWindow import GlobalBlur
from components import EyePilotButton, EyePilotButtonColorChoice, EyePilotScroll, EyeToggleComponent
from calibration import Calibration
from contextMenu import ContextMenu

from contextTracker import VisContext

from blur import Blur
from dot import CircleWidget
from contextMenu import ContextMenu

from pywinauto import Application
import pygetwindow as gw
import pyautogui
import win32gui
import win32api
import win32con
import ctypes
import threading
import socket
import json

from tracker import Tracker

class MouseWatcher:

    ## To check if cursor is not moving
    def __init__(self):
        self.prev_cursor_pos = pyautogui.position()

    def isMoving(self):
        if self.prev_cursor_pos == pyautogui.position():
            return False
        else:
            self.prev_cursor_pos = pyautogui.position()
            return True
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

    def rmModel(self):
        model_path = os.path.join(self.path, self.model_name)
        if os.path.exists(model_path):
            os.remove(model_path)

def is_window_transparent(hwnd):
    # Get the extended window styles
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)

    # Check for WS_EX_LAYERED and WS_EX_TRANSPARENT
    # is_layered = ex_style & win32con.WS_EX_LAYERED
    is_transparent = ex_style & win32con.WS_EX_TRANSPARENT

    return is_transparent != 0

class EyeSocket:

    def __init__(self):
        self.HOST = '127.0.0.1'  # localhost
        self.PORT = 65432        # Port to listen on (use any free port > 1024)
        self.server_socket = None
        self.thread = threading.Thread(target=self.acceptIncoming)
        self.running = False
        self.clients = []

    def acceptIncoming(self):
        try:
            while self.running:
                client_socket, client_address = self.server_socket.accept()
                self.clients.append(client_socket, client_address)
        except Exception as e:
            print(f"Caught {e}")
            pass

    def open(self):
        # Create a UDP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((HOST, PORT))
        self.running = True

    def send(self,data : dict) -> None:
        if self.server_socket:
            message = json.dumps(data)
            for client_socket, client_address in self.clients:
                self.server_socket.sendto(message.encode(), client_address)

    def close(self,):
        self.running = False
        self.server_socket.close()
        self.server_socket = None


class MyMainWindow(QMainWindow):

    def moveEvent(self, event) -> None:
        time.sleep(0.02)  # sleep for 20ms
        layout_center  = self.left_layout.geometry().center()
        self.tracker.setPosition(self.geometry().x() + 160, self.geometry().y() + 200)

    def resizeEvent(self, event) -> None:
        time.sleep(0.02)  # sleep for 20ms
        layout_center  = self.left_layout.geometry().center()
        self.tracker.setPosition(self.geometry().x() + 160, self.geometry().y() + 200)

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(":/icon.png"))

        self.setWindowTitle("EyePilot")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 800, 800)

        GlobalBlur(self.winId(),Dark=True,QWidget=self)

        self.windowName = "EyePilot"
        self.setWindowTitle(self.windowName)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)

        # Create a frame to hold left side content
        left_frame = QFrame()
        main_layout.addWidget(left_frame, stretch=1)

        # Add a label to left frame (optional)
        self.label_left = QLabel("EyePilot")
        self.label_left.setStyleSheet("color: white; font-size: 40px;")
        self.label_left.setAlignment(Qt.AlignCenter)
        self.left_layout = QVBoxLayout()
        left_frame.setLayout(self.left_layout)
        self.left_layout.addWidget(self.label_left)

        # Create a frame to hold right side content
        right_frame = RightSideMenu()
        main_layout.addWidget(right_frame, stretch=1)

        self.landing_spot = CircleWidget()
        layout_center  = self.left_layout.geometry().center()
        self.landing_spot.setPosition(layout_center.x() + 160, layout_center.y() + 200)
        self.landing_spot.setColor(102,102,102)
        self.landing_spot.setParent(self)

        self.tracker = CircleWidget("EyeGesturesCursor")
        layout_center  = self.left_layout.geometry().center()
        self.tracker.setPosition(self.geometry().x() + layout_center.x() + 150, self.geometry().y() + layout_center.y() + 200)
        self.tracker.setColor(100, 0, 255)
        # self.tracker.setTransparency(0)
        self.tracker.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.tracker.show()

        right_frame.setSignal("Customize","ColorChange",signal=self.changeTrackerColor)
        right_frame.setSignal("Main","Calibration",signal=self.show_calibration)
        right_frame.setSignal("Main","Start",signal=self.start)
        right_frame.setSignal("Settings","Reset Calibration",signal=self.resetTracker)
        right_frame.setSignal("Settings","Assistive [WiP]",signal=self.assistive_window)
        right_frame.setSignal("Settings","Move mouse on focus",signal=self.feature_mouse_move)
        right_frame.setSignal("Settings","Cursor OFF/ON",signal=self.feature_cursor)
        right_frame.setSignal("Settings","Window Focus",signal=self.feature_focus)
        right_frame.setSignal("Settings","Display Blur",signal=self.feature_blur)
        right_frame.setSignal("Settings","Port open [WiP]",signal=self.feature_port)

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

        self.calibration_iterator = 0
        self.calibration_max = 25
        self.prev_calibration_point = [0,0]
        self.calibrationWidget = Calibration()
        self.calibrationWidget.setOnQuit(self.stop_calibration)

        # Start a timer to update the position periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.main_loop)
        self.timer.start(30)  # Update every second

        self.eyeTracker = Tracker()
        self.running = False
        self.calibrationON = False

        self.vizContext = VisContext()
        # self.contextMenu = ContextMenu()

        self.model = ModelSaver()

        self.fix_start = time.time()

        self.contextMenu = ContextMenu(screen_center = [1250,650])

        self.fix_debounce = 51
        self.prev_cursor = pyautogui.position()
        self.fixation_threshold = 0.8

        self.feature_status_cursor = False
        self.feature_status_focus = False
        self.feature_status_blur = False
        self.feature_status_port = False
        self.feature_assistive_control = False
        self.feature_status_mouse_move = False

        self.sock = EyeSocket()

        # self.demo_start = time.time()
        # self.demo_duration_max = 2 * 60
        self.mouse = MouseWatcher()
        self.handTracker = CircleWidget("HandGesturesTracker")
        layout_center  = self.left_layout.geometry().center()
        self.handTracker.setPosition(self.geometry().x() + layout_center.x() + 150, self.geometry().y() + layout_center.y() + 200)
        self.handTracker.setColor(0, 125, 50)
        # self.tracker.setTransparency(0)
        self.handTracker.setWindowFlag(Qt.WindowStaysOnTopHint)


    def show_calibration(self):
        self.calibration_iterator = 0
        self.calibrationON = True
        self.eyeTracker.calibrationOn()
        self.calibrationWidget.show()

    def stop_calibration(self):
        self.calibrationON = False
        self.eyeTracker.calibrationOff()

    def changeTrackerColor(self,color):
        self.tracker.setColor(color[0],color[1],color[2])

    def onPress(self,pos):
        self.handTracker.setColor(125, 125, 125)

    def press(self,x,y):
        pyautogui.moveTo(x, y)
        pyautogui.mouseDown()
        pyautogui.mouseUp()

    def onRelease(self,pos):
        self.handTracker.setColor(0, 125, 50)
        self.press(pos[0],pos[1])

    #################### feature matrix

    def feature_mouse_move(self,status):
        self.feature_status_mouse_move = status

    def feature_cursor(self,status):
        if status:
            self.tracker.hide()
        else:
            self.tracker.show()

    def feature_focus(self,status):
        self.feature_status_focus = status

    def feature_blur(self,status):
        self.feature_status_blur = status

    def feature_port(self,status):
        self.feature_status_port = status
        if status:
            self.sock.open()
        else:
            self.sock.close()

    def assistive_window(self,status):
        self.feature_assistive_control = status


    ########################### Window switcher

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

    def blur_display(self,point):
        center_x = self.screen_geometry.width() // 2
        center_y = self.screen_geometry.height() // 2
        screen = QDesktopWidget().screenGeometry(0)
        if abs(point[0] - center_x) > (int(screen.width()*self.sensitivity)) or abs(point[1] - center_y) > (int(screen.height()*self.sensitivity)):
            blur_focus = False
            blur_duration = False
            if self.focus and (fix > 0.6):
                blur_focus = True
            if (time.time() - self.time_start) > self.duration_to_blur:
                blur_duration = True

            if (blur_focus or not self.focus) and blur_duration:
                self.blur_widget.show()
                if (time.time() - self.screenLockCounter > self.screenLockTimeLimit) and self.screenLock:
                    ctypes.windll.user32.LockWorkStation()
        else:
            self.time_start = time.time()
            self.blur_widget.quit()
            self.screenLockCounter = time.time()

            pass

    ##########################

    def updateMainLabel(self,title):
        self.label_left.setText(f"{title}")

    def main_loop(self):
        # if (time.time() - self.demo_start) > self.demo_duration_max:
        #     self.stop()
        #     self.close()
        #     return

        # time_left = self.demo_duration_max - (time.time() - self.demo_start)
        # self.updateMainLabel(f"EyeFocus\nDemo time left\n{int(time_left/60)}:{int(time_left%60)}")

        window_switch_on = False
        if self.running:

            point, calibration, blink, fix, acceptance_radius, calibration_radius = self.eyeTracker.step()

            self.tracker.setPosition(point[0], point[1])

            hand_x, hand_y = self.eyeTracker.getHand(
                point[0],
                point[1],
                click = self.onPress,
                release = self.onRelease
            )
            if int(hand_x) == int(point[0]) and int(hand_y) == int(point[1]):
                self.handTracker.hide()
            else:
                self.handTracker.show()
                self.handTracker.setPosition(
                    hand_x,
                    hand_y,
                )

            if self.calibrationON:
                self.calibrationWidget.setPosition(calibration[0], calibration[1])
                self.calibrationWidget.setRadius(2*calibration_radius)
                self.calibrationWidget.setPositionFit(calibration[0], calibration[1])
                self.calibrationWidget.setRadiusFit(2*acceptance_radius)
                if self.prev_calibration_point[0] != calibration[0] or self.prev_calibration_point[1] != calibration[1]:
                    self.calibration_iterator+=1
                    self.prev_calibration_point = calibration
                if self.calibration_iterator >= self.calibration_max:
                    self.calibrationWidget.quit()
                    print("self.calibrationWidget.quit()")
            else:
                if self.feature_assistive_control:
                    if fix > 0.8 and 1 < time.time() - self.fix_start:
                        self.fix_start = time.time()
                        self.contextMenu.launch([point[0], point[1]])
                        # self.vizContext.start()
                        # self.vizContext.setPosition(point[0], point[1])
                    elif not fix:
                        self.contextMenu.execute([point[0], point[1]])
                        if 1 < time.time() - self.fix_start:
                            self.contextMenu.click([point[0], point[1]])

                # this 0.3 check prevents from EyeGestures to take control over mouse
                if self.feature_status_focus and fix > 0.1 and not self.mouse.isMoving():
                    if self.fix_debounce > 20:
                        self.check_window(point)
                        self.fix_debounce = 0
                    else:
                        self.fix_debounce += 1

                if self.feature_status_blur:
                    if self.fix_debounce > 10:
                        self.blur_display(point)
                        self.fix_debounce = 0
                    else:
                        self.fix_debounce += 1

                fix_to_test = self.fixation_threshold if self.fixation_threshold > 0.3 else 0.3
                if self.feature_status_mouse_move and fix > fix_to_test:
                    pyautogui.moveTo(
                        x=point[0],
                        y=point[1]
                    )

                if self.feature_status_port:
                    print(self.feature_status_port)
                    payload = {
                        "x" : point[0],
                        "y" : point[1],
                        "blink" : blink,
                        "fixation" : fix,
                    }

                    self.sock.send(payload)


    def resetTracker(self):
        self.model.rmModel()
        self.eyeTracker.reset()

    def start(self):
        modelData = self.model.getModel()
        self.eyeTracker.start()
        if modelData is None:
            self.show_calibration()
        else:
            self.eyeTracker.loadModel(modelData)
        self.running = True

    def stop(self):
        self.running = False
        self.vizContext.close()
        self.eyeTracker.stop()
        self.tracker.close()

    def closeEvent(self, event):
        # Call your function or perform cleanup here
        self.stop()
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
        self.settings = Settings()
        self.customize = Customize()

        self.__allMenus = {
            "Main" : self.mainMenu,
            "Settings" : self.settings,
            "Customize" : self.customize
        }

        self.menu_stack.addWidget(self.mainMenu)
        self.menu_stack.addWidget(self.settings)
        self.menu_stack.addWidget(self.customize)
        self.menu_stack.setCurrentIndex(0)
        self.menus = 3

        self.mainMenu.setSignal("Settings", lambda : self.switchMenu(1))
        self.mainMenu.setSignal("Customize", lambda : self.switchMenu(2))

        self.settings.setSignal("Back", lambda : self.switchMenu(0))
        self.customize.setSignal("Back", lambda : self.switchMenu(0))


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

    def add_custom(self,button):
        tmp_layout = QHBoxLayout()
        self.right_buttons.append(button)
        tmp_layout.addWidget(self.right_buttons[-1])
        self.right_layout.addLayout(tmp_layout)

class MainMenu(Menu):

    def __init__(self):
        super().__init__()

        self.add_button("Start")
        self.add_button("Calibration")
        self.add_button("Settings")
        self.add_button("Customize")

class Settings(Menu):

    def __init__(self):
        super().__init__()

        self.add_custom(EyeToggleComponent("Assistive [WiP]"))
        self.add_custom(EyeToggleComponent("Move mouse on focus"))
        self.add_custom(EyeToggleComponent("Cursor OFF/ON"))
        self.add_custom(EyeToggleComponent("Window Focus"))
        self.add_custom(EyeToggleComponent("Display Blur"))
        self.add_custom(EyeToggleComponent("Port open"))
        self.calibrationWidget = Calibration()

        self.add_button("Reset Calibration")
        self.add_button("Back")

class Customize(Menu):

    def __init__(self):
        super().__init__()

        self.calibrationWidget = Calibration()

        DEEPSEA_BLUE = (10,50,150)
        STEEL_GREY = (150,150,150)
        CREAMY_ORANGE = (150,100,50)
        LEAFY_GREEN = (100,150,100)

        self.add_custom(EyePilotButtonColorChoice("DeepSea Blue", id = "ColorChange", color=DEEPSEA_BLUE))
        self.add_custom(EyePilotButtonColorChoice("Steel Grey",   id = "ColorChange", color=STEEL_GREY))
        self.add_custom(EyePilotButtonColorChoice("Creamy Orange",id = "ColorChange", color=CREAMY_ORANGE))
        self.add_custom(EyePilotButtonColorChoice("Leafy Green",  id = "ColorChange", color=LEAFY_GREEN))

        self.add_button("Back")

if __name__ == "__main__":
    # sys.stdout = open(os.devnull, 'w')

    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())
