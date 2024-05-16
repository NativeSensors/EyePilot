import cv2
import random
import numpy as np
import sklearn.linear_model as scireg
from eyeGestures.utils import VideoCapture
from eyeGestures.eyegestures import EyeGestures

from screeninfo import get_monitors

class Calibrator:

    def __init__(self):
        self.X = []
        self.Y_y = []
        self.Y_x = []
        self.reg = None
        self.reg_x = scireg.Ridge(alpha=1.0)
        self.reg_y = scireg.Ridge(alpha=1.0)
        self.fitted = False

    def add(self,x,y,ref_point,fit_point):
        self.X.append(x.flatten())
        self.Y_y.append(y[1])
        self.Y_x.append(y[0])

        __tmp_X =np.array(self.X)
        __tmp_Y_y =np.array(self.Y_y)
        __tmp_Y_x =np.array(self.Y_x)

        self.reg_x.fit(__tmp_X,__tmp_Y_x)
        self.reg_y.fit(__tmp_X,__tmp_Y_y)
        self.fitted = True

    def predict(self,x):
        if self.fitted:
            x = x.flatten()
            x = x.reshape(1, -1)
            y_x = self.reg_x.predict(x)[0]
            y_y = self.reg_y.predict(x)[0]
            return np.array([y_x,y_y])
        else:
            return np.array([0.0,0.0])

    def unfit(self):
        self.fitted = False

def euclidean_distance(point1, point2):
    return np.linalg.norm(point1 - point2)

class Tracker:

    def __init__(self):

        self.clb = Calibrator()
        self.cap = None
        self.monitor = list(filter(lambda monitor: monitor.is_primary == True ,get_monitors()))[0]
        self.gestures = EyeGestures(285,115,80,15)

        self.calibration = False

        self.CN = 5

        self.trackerSignal = None
        self.fitSignal = None

        self.average_points = np.zeros((20,2))
        self.filled_points = 0
        self.calibrate_gestures = True
        self.fit_point = self.getNewRandomPoint()

        self.output_points = np.zeros((5,2))

        self.iterator = 0
        self.fix = 0.8

        self.precision_limit = 50
        self.precision_step = 15
        self.acceptance_radius = 200
        self.calibration_radius = 500
        # after corssing this thresh we are disabling classical calib
        self.eyegestures_calibration_threshold = 400

    def getLandmarks(self,calibrate = False):

        if self.cap:
            ret, frame = self.cap.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame,1)
            # frame = cv2.resize(frame, (360, 640))

            cursor_x, cursor_y = 0, 0
            event = self.gestures.estimate(
                frame,
                "main",
                calibrate, # set calibration - switch to False to stop calibration
                self.monitor.width,
                self.monitor.height,
                0, 0, self.fix,10)

            cursor_x, cursor_y = event.point_screen[0],event.point_screen[1]
            l_eye_landmarks = event.l_eye.getLandmarks()
            r_eye_landmarks = event.r_eye.getLandmarks()

            cursors = np.array([cursor_x,cursor_y]).reshape(1, 2)
            eye_events = np.array([event.blink,event.fixation]).reshape(1, 2)
            key_points = np.concatenate((cursors,l_eye_landmarks,r_eye_landmarks,eye_events))
            return key_points, np.array((cursor_x, cursor_y)), event.blink, event.fixation
        else:
            return None, None

    def increase_precision(self):
        if self.calibration_radius > self.precision_limit:
            self.calibration_radius -= self.precision_step
        if self.acceptance_radius > self.precision_limit:
            self.acceptance_radius -= self.precision_step

    def setClassicImpact(self,impact):
        self.CN = impact

    def start(self):
        self.cap = VideoCapture(0)

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
        self.acceptance_radius = 200
        self.calibration_radius = 500
        self.average_points = np.zeros((20,2))
        self.filled_points = 0
        self.clb.unfit()

    def setFixation(self,fix):
        self.fix = fix

    def setClassicalImpact(self,CN):
        self.CN = CN

    def step(self):
        self.calibrate_gestures = self.calibrate_gestures and self.calibration_radius > self.eyegestures_calibration_threshold
        key_points, classic_point, blink, fixated = self.getLandmarks(self.calibrate_gestures)

        margin = 30
        if classic_point[0] <= margin and self.calibration:
            self.calibrate_gestures = True
        elif classic_point[0] >= self.monitor.width - margin and self.calibration:
            self.calibrate_gestures = True
        elif classic_point[1] <= margin and self.calibration:
            self.calibrate_gestures = True
        elif classic_point[1] >= self.monitor.height - margin and self.calibration:
            self.calibrate_gestures = True
        else:
            self.calibrate_gestures = False

        y_point = self.clb.predict(key_points)
        self.average_points[1:,:] = self.average_points[:(self.average_points.shape[0] - 1),:]
        self.average_points[0,:] = y_point
        if self.filled_points < self.average_points.shape[0] and (y_point != np.array([0.0,0.0])).any():
            self.filled_points += 1

        averaged_point = (np.sum(self.average_points[:,:],axis=0) + (classic_point * self.CN))/(self.filled_points + self.CN)

        if self.calibration and (euclidean_distance(averaged_point,self.fit_point) < self.calibration_radius or self.filled_points < self.average_points.shape[0] * 10):
            self.clb.add(key_points,self.fit_point,classic_point,y_point)

        if euclidean_distance(averaged_point,self.fit_point) < self.acceptance_radius:
            self.iterator += 1
            if self.iterator > 10:
                self.iterator = 0
                self.fit_point = self.getNewRandomPoint()
                self.increase_precision()

        return (averaged_point, self.fit_point, blink, fixated >= self.fix, self.acceptance_radius, self.calibration_radius)
