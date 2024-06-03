from IconMatch.IconMatch import ScreenScanner
from dot import CircleWidget
from PySide2.QtCore import Qt, QTimer

import threading
import numpy as np
import time

class VisContext:

    def __init__(self,before = lambda : None ,after = lambda : None):
        self.before = before
        self.after = after

        self.dot = CircleWidget()
        self.dot.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.dot.show()
        self.cursorTracker = CursorTracker(self.before_scan,self.after_scan)

    def before_scan(self):
        self.before()

    def after_scan(self):
        self.after()

    def setPosition(self,x,y):
        closest_x, closest_y = self.cursorTracker.getClosestObject(x,y)
        self.dot.setPosition(closest_x, closest_y)
        return (closest_x, closest_y)

    def start(self):
        self.dot.show()
        self.cursorTracker.start()

    def close(self):
        self.cursorTracker.close()
        self.dot.close()

class CursorTracker:

    def __init__(self,before_scan = lambda : None,after_scan = lambda : None):
        self.update_delay = 0.5 # ms
        self.last_x = 0
        self.last_y = 0
        self.window_h = 1000
        self.window_w = 1000
        self.scanner = ScreenScanner()
        rectangles = self.scanner.scan(bbox = (0,0,self.window_w,self.window_h))

        self.DSB = DynamicSpatialBuckets()
        self.DSB.loadData(rectangles)

        self.time_start = time.time()

        # Start a timer to update the position periodically
        self.closest_rectangle = (0,0)

        self.before_scan = before_scan
        self.after_scan = after_scan

    def start(self):
        if self.stop:
            self.stop = False
            threading.Timer(0.5,self.__background_loop).start()

    def close(self):
        self.stop = True

    def __background_loop(self):
        self.rescan(self.last_x-self.window_w/2,self.last_y-self.window_h/2,self.window_w,self.window_h)
        if not self.stop:
            threading.Timer(0.5,self.__background_loop).start()


    def rescan(self,x,y,w,h):
        rectangles = self.scanner.scan((x,y,x+w,y+h))
        self.DSB = DynamicSpatialBuckets()
        self.DSB.loadData(rectangles)

    def getClosestObject(self,x,y):

        self.last_x = x
        self.last_y = y

        rectangles = self.DSB.getBucket([x,y])
        closest_distance = 9999
        closest_rectangle = None

        for rectangle in rectangles:
            center_x = rectangle[0] + rectangle[2]/2
            center_y = rectangle[1] + rectangle[3]/2
            distance = np.linalg.norm(np.array([center_x,center_y]) - np.array([x,y]))
            if distance < closest_distance:
                closest_distance = distance
                closest_rectangle = rectangle
        if closest_rectangle and self.update_delay < (time.time() - self.time_start):
            self.time_start = time.time()
            self.closest_rectangle = (closest_rectangle[0],closest_rectangle[1])
        return self.closest_rectangle


class DynamicSpatialBuckets:

    def __init__(self):

        self.buckets = [[]]
        self.step = 500

    def loadData(self,rectangles):

        for rectangle in rectangles:
            center_x = rectangle[0] + rectangle[2]/2
            center_y = rectangle[1] + rectangle[3]/2

            index_x = int(center_x/self.step)
            index_y = int(center_y/self.step)

            while(index_x >= len(self.buckets)):
                self.buckets.append([])

            while(index_y >= len(self.buckets[index_x])):
                self.buckets[index_x].append([])

            self.buckets[index_x][index_y].append(rectangle)

    def getBucket(self,point):

        index_x = int(point[0]/self.step)
        index_y = int(point[1]/self.step)

        ret_bucket = []
        if len(self.buckets) > index_x and len(self.buckets[index_x]) > index_y:
            ret_bucket = self.buckets[index_x][index_y]

        return ret_bucket