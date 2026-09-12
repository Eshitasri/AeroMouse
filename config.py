import pyautogui

# Camera resolution
CAM_W = 640
CAM_H = 480

# Screen resolution
SCREEN_W, SCREEN_H = pyautogui.size()

# Frame margin (pixels inside camera edge to reach screen corners easily)
FRAME_REDUCTION = 130

# Smoothing factor for cursor movement (higher = smoother, lower = faster)
SMOOTHING = 5

# Distance thresholds in pixels
CLICK_THRESH = 35
PINCH_THRESH = 30

# MediaPipe confidence thresholds
MIN_DETECTION_CONF = 0.7
MIN_TRACKING_CONF = 0.7