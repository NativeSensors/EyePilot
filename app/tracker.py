import cv2
import random
import numpy as np
import sklearn.linear_model as scireg
from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v3
from handGestures import Hand, HandFinder

from screeninfo import get_monitors

def euclidean_distance(point1, point2):
    return np.linalg.norm(point1 - point2)

class Tracker:

    PRECISION_LIMIT = 50
    PRECISION_STEP = 10
    ACCEPTANCE_RADIUS = 500
    CALIBRATION_RADIUS = 1000
    EYEGESTURES_CALIBRATION_THRESH = 850

    def __init__(self):

        self.cap = None
        self.monitor = list(filter(lambda monitor: monitor.is_primary == True ,get_monitors()))[0]
        self.gestures = EyeGestures_v3()
        x = np.arange(0, 1.1, 0.33)
        y = np.arange(0, 1.1, 0.33)

        xx, yy = np.meshgrid(x, y)

        calibration_map = np.column_stack([xx.ravel(), yy.ravel()])
        np.random.shuffle(calibration_map)
        self.gestures.uploadCalibrationMap(calibration_map,context="main")

        self.calibration = False

        ## hand tracker:
        self.handsFinder = HandFinder()
        self.hand = Hand(
            pinchStart  = self.pinch_activated,
            pinchActive = self.pinch_hold,
            pinchRelease= self.pinch_released)
        self.prev_cursor = [0,0]
        self.hand_x = 0
        self.hand_y = 0
        self.base_x = 0
        self.base_y = 0

        self.click = lambda x : None
        self.hold = lambda x : None
        self.release = lambda x : None

    def start(self):
        self.cap = VideoCapture(0)

    def loadModel(self, modelData):
        self.gestures.loadModel(modelData)

    def stop(self):
        if self.cap != None:
            self.cap.close()
            # why this works here but release do not works in lib
            self.cap.cap.release()

    def calibrationOn(self):
        self.calibration = True

    def calibrationOff(self):
        self.calibration = False

    def getNewRandomPoint(self):
        return np.array([random.random() * self.monitor.width,random.random() * self.monitor.height])

    def reset(self):
        self.gestures.reset()

    def pinch_activated(self,pos):
        pos = (self.base_x + self.hand_x, self.base_y + self.hand_y)
        self.click(pos)
        pass

    def pinch_hold(self,pos):
        pos = (self.base_x + self.hand_x, self.base_y + self.hand_y)
        self.hold(pos)
        pass

    def pinch_released(self,pos):
        pos = (self.base_x + self.hand_x, self.base_y + self.hand_y)
        self.release(pos)
        pass

    def step(self):
        _, frame = self.cap.read()

        event, cevent = self.gestures.step(frame,self.calibration,self.monitor.width,self.monitor.height,context="main")
        ret = self.hand.process(self.monitor.width,self.monitor.height,self.handsFinder.find(frame))

        if ret:
            cursor,_,_ = ret
            cursor[1] = cursor[2] * 1000
            dx,dy = cursor[0] - self.prev_cursor[0], cursor[1] - self.prev_cursor[1]
            self.prev_cursor[0], self.prev_cursor[1] = cursor[0], cursor[1]
            self.hand_x -= dx
            self.hand_y += dy
        else:
            self.hand_x = 0
            self.hand_y = 0
            self.base_x = 0
            self.base_y = 0

        return (event.point, cevent.point, event.blink, event.fixation, cevent.acceptance_radius, cevent.calibration_radius)

    def getHand(self,base_x,base_y,
                click = lambda _ : None,
                hold = lambda _ : None,
                release = lambda _ : None):
        self.click = click
        self.hold = hold
        self.release = release

        diff_base_x = abs(base_x - self.base_x)
        diff_base_y = abs(base_y - self.base_y)

        if diff_base_x + diff_base_y > 200:
            self.base_x = base_x
            self.base_y = base_y
            self.hand_x = 0
            self.hand_y = 0

        return (self.base_x + self.hand_x, self.base_y + self.hand_y)

