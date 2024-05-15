import pygame
import cv2 
import random
import numpy as np
import sklearn.linear_model as scireg
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR,LinearSVR
from eyeGestures.utils import VideoCapture
from eyeGestures.eyegestures import EyeGestures

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

def getLandmarks(calibrate = False):

    ret, frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.flip(frame,1)
    # frame = cv2.resize(frame, (360, 640))

    cursor_x, cursor_y = 0, 0
    event = gestures.estimate(
        frame,
        "main",
        calibrate, # set calibration - switch to False to stop calibration
        screen_width,
        screen_height,
        0, 0, 0.8,10)

    cursor_x, cursor_y = event.point_screen[0],event.point_screen[1]
    l_eye_landmarks = event.l_eye.getLandmarks()
    r_eye_landmarks = event.r_eye.getLandmarks()

    curosrs = np.array([cursor_x,cursor_y]).reshape(1, 2)
    key_points = np.concatenate((curosrs,l_eye_landmarks,r_eye_landmarks))
    return key_points, np.array((cursor_x, cursor_y))


def euclidean_distance(point1, point2):
    # Calculate the squared differences for each dimension
    squared_diff = (point2 - point1) ** 2

    # Sum the squared differences along all dimensions
    sum_squared_diff = np.sum(squared_diff)

    # Take the square root of the sum to get the Euclidean distance
    distance = np.sqrt(sum_squared_diff)
    return distance