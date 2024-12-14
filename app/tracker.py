import cv2
import random
import numpy as np
import sklearn.linear_model as scireg
from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v3

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
        self.gestures = EyeGestures_v2()
        x = np.arange(0, 1.1, 0.2)
        y = np.arange(0, 1.1, 0.2)

        xx, yy = np.meshgrid(x, y)

        calibration_map = np.column_stack([xx.ravel(), yy.ravel()])
        np.random.shuffle(calibration_map)
        self.gestures.uploadCalibrationMap(calibration_map,context="main")

        self.gestures.enableCNCalib()
        self.gestures.setClassicImpact(2)
        self.calibration = False

    def start(self):
        self.cap = VideoCapture(0)

    def saveModel(self):
        return self.gestures.saveModel()

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

    def setFixation(self,fix):
        self.gestures.setFixation(fix)

    def setClassicalImpact(self,CN):
        self.gestures.setClassicImpact(CN)

    def step(self):
        _, frame = self.cap.read()
        event, cevent = self.gestures.step(frame,self.calibration,self.monitor.width,self.monitor.height,context="main")

        return (event.point, cevent.point, event.blink, event.fixation, cevent.acceptance_radius, cevent.calibration_radius)
