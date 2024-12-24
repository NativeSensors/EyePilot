import cv2
import numpy as np
import mediapipe as mp


class HandFinder:

    def __init__(self, static_image_mode=True, max_num_hands=1):
        self.mp_hands = mp.solutions.hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def find(self, image):
        try:
            hand_results = self.mp_hands.process(
                cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            return hand_results
        except Exception as e:
            print(f"Exception in HandFinder: {e}")
            return None

class Hand:

    def __init__(self,pinchStart = None, pinchActive = None, pinchRelease = None):
        self.landmarks = []
        self.isBuilt = False
        self.pinchStart = pinchStart
        self.pinchActive = pinchActive
        self.pinchRelease = pinchRelease
        self.activated = False

    def getLandmarks(self):
        return self.landmarks

    def check(self):
        return self.isBuilt

    def _landmarks(self, landmarks):
        __hand_landmarks = []
        for landmark in landmarks.landmark:
            __hand_landmarks.append((
                landmark.x * self.image_w,
                landmark.y * self.image_h,
                landmark.z))
        return np.array(__hand_landmarks)

    def process(self, canvas_w, canvas_h, hand):
        try:
            self.image_h, self.image_w = canvas_h, canvas_w
            if hand.multi_hand_landmarks:
                for landmark in hand.multi_hand_landmarks:
                    self.landmarks = self._landmarks(landmark)
            else:
                self.landmarks = None
            print(f"self.landmarks: {self.landmarks}")
        except Exception as e:
            print(f"Exception in Hand process: {e}")
            return None

        if type(self.landmarks) is np.ndarray:
            if not None and len(self.getLandmarks()) > 5:
                thumb = Thumb(self.getLandmarks()[:5])
                finger1 = Finger(self.getLandmarks()[5:10])
                # finger2 = Finger(self.getLandmarks()[10:15])
                # finger3 = Finger(self.getLandmarks()[15:20])
                # finger4 = Finger(self.getLandmarks()[20:25])
                pointed = finger1.point(thumb.getPointer(),15000)
                cursor = self.getLandmarks()[4]
                if len(pointed) > 0:
                    if not self.activated:
                        if self.pinchStart:
                            self.pinchStart(cursor)
                        self.activated = True
                    elif self.pinchActive:
                        self.pinchActive(cursor)
                else:
                    if self.activated:
                        if self.pinchRelease:
                            self.pinchRelease(cursor)
                        self.activated = False

                return (cursor,thumb,finger1)

        return None

class Thumb:

    def __init__(self,points):
        self.points = points
        if len(self.points) > 0: 
            self.pointer = points[-1]
        else:
            self.pointer = []

    def getPointer(self):
        return self.pointer

class Finger:

    def __init__(self,points):
        self.points = points

    def point(self,pointer,distance=2500):
        for point in self.points:
            # print((point[0] - pointer[0])**2 + (point[1] - pointer[1])**2 + (point[2] - pointer[2])**2)
            if distance > ((point[0] - pointer[0])**2 + (point[1] - pointer[1])**2 + (point[2] - pointer[2])**2):
                return point
        return []