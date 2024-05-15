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

    def add(self,x,y,ref_point,fit_point):
        self.X.append(x.flatten())
        self.Y_y.append(y[1])
        self.Y_x.append(y[0])

        __tmp_X =np.array(self.X)
        __tmp_Y_y =np.array(self.Y_y)
        __tmp_Y_x =np.array(self.Y_x)

        self.reg_x.fit(__tmp_X,__tmp_Y_x)
        self.reg_y.fit(__tmp_X,__tmp_Y_y)

    def predict(self,x):
        x = x.flatten()
        x = x.reshape(1, -1)
        y_x = self.reg_x.predict(x)[0]
        y_y = self.reg_y.predict(x)[0]
        return np.array([y_x,y_y])


def euclidean_distance(point1, point2):
    # Calculate the squared differences for each dimension
    squared_diff = (point2 - point1) ** 2

    # Sum the squared differences along all dimensions
    sum_squared_diff = np.sum(squared_diff)

    # Take the square root of the sum to get the Euclidean distance
    distance = np.sqrt(sum_squared_diff)
    return distance

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
        self.calibrate_gestures = True
        self.fit_point = self.getNewRandomPoint()

        self.iterator = 0

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
                0, 0, 0.8,10)

            cursor_x, cursor_y = event.point_screen[0],event.point_screen[1]
            l_eye_landmarks = event.l_eye.getLandmarks()
            r_eye_landmarks = event.r_eye.getLandmarks()

            cursors = np.array([cursor_x,cursor_y]).reshape(1, 2)
            key_points = np.concatenate((cursors,l_eye_landmarks,r_eye_landmarks))
            return key_points, np.array((cursor_x, cursor_y))
        else:
            return None, None

    def setClassicImpact(self,impact):
        self.CN = impact

    def start(self):
        self.cap = VideoCapture(0)

        key_points, classic_point = self.getLandmarks()
        self.clb.add(key_points,self.fit_point,classic_point,self.fit_point)

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

    def step(self):
        key_points, classic_point = self.getLandmarks(self.calibrate_gestures)
        if classic_point[0] <= 10:
            self.calibrate_gestures = True
        elif classic_point[0] >= self.monitor.width - 10:
            self.calibrate_gestures = True
        elif classic_point[1] <= 10:
            self.calibrate_gestures = True
        elif classic_point[1] >= self.monitor.height - 10:
            self.calibrate_gestures = True
        else:
            self.calibrate_gestures = False

        y_point = self.clb.predict(key_points)
        self.average_points[1:,:] = self.average_points[:(self.average_points.shape[0] - 1),:]
        self.average_points[0,:] = y_point

        averaged_point = (np.sum(self.average_points[:,:],axis=0) + (classic_point * self.CN))/(self.average_points.shape[0] + 1 * self.CN)

        if self.calibration:
            self.clb.add(key_points,self.fit_point,classic_point,y_point)

        if euclidean_distance(averaged_point,self.fit_point) < 200:
            self.iterator += 1
            if self.iterator > 10:
                self.iterator = 0
                self.fit_point = self.getNewRandomPoint()

        return (averaged_point, self.fit_point)
