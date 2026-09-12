import os
import math
import urllib.request
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import config

MODEL_PATH = "hand_landmarker.task"
MODEL_URL = "https://googleapis.com"


class MpDrawAdapter:
    @staticmethod
    def draw_landmarks(img, hand_landmarks, connections=None):
        lms = hand_landmarks.landmark if hasattr(hand_landmarks, 'landmark') else hand_landmarks
        h, w, _ = img.shape

        if connections:
            for start_idx, end_idx in connections:
                pt1 = (int(lms[start_idx].x * w), int(lms[start_idx].y * h))
                pt2 = (int(lms[end_idx].x * w), int(lms[end_idx].y * h))
                cv2.line(img, pt1, pt2, (0, 255, 0), 2)

        for lm in lms:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(img, (cx, cy), 4, (0, 0, 255), -1)


class MpHandsAdapter:
    HAND_CONNECTIONS = [
        (0, 1), (1, 2), (2, 3), (3, 4),
        (0, 5), (5, 6), (6, 7), (7, 8),
        (5, 9), (9, 10), (10, 11), (11, 12),
        (9, 13), (13, 14), (14, 15), (15, 16),
        (13, 17), (17, 18), (18, 19), (19, 20),
        (0, 17)
    ]


class HandTracker:
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            print("Downloading MediaPipe Hand Landmarker model...")
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.mp_draw = MpDrawAdapter()
        self.mp_hands = MpHandsAdapter()

    def process_frame(self, img):
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self.detector.detect(mp_image)

        if hasattr(result, 'hand_landmarks') and result.hand_landmarks:
            result.multi_hand_landmarks = result.hand_landmarks
        else:
            result.multi_hand_landmarks = None
        return result

    def get_landmark_coords(self, hand_landmarks):
        # Explicitly ensure landmarks are accessible as a standard sequential list
        lms = list(hand_landmarks.landmark if hasattr(hand_landmarks, 'landmark') else hand_landmarks)
        lm_pixel_coords = []
        for lm in lms:
            cx, cy = int(lm.x * config.CAM_W), int(lm.y * config.CAM_H)
            lm_pixel_coords.append((cx, cy))
        return lm_pixel_coords, lms

    def detect_finger_states(self, lms):
        fingers = []
        # Robust relative thumb check: is the thumb tip wider than the index knuckle base?
        # Handles camera mirroring gracefully regardless of left/right hand identity
        if lms[4].x < lms[5].x:
            fingers.append(1)
        else:
            fingers.append(0)

        # Index, Middle, Ring, Pinky
        for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
            fingers.append(1 if lms[tip].y < lms[pip].y else 0)

        return fingers

    @staticmethod
    def euclidean_distance(pt1, pt2):
        return math.hypot(pt2[0] - pt1[0], pt2[1] - pt1[1])
