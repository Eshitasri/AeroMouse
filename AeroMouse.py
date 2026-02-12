#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# 1. Remove the current version
get_ipython().system('pip uninstall mediapipe -y')

# 2. Install the stable version you used for EchoSign
get_ipython().system('pip install mediapipe==0.10.11')


# In[1]:


import cv2
import mediapipe as mp
import pyautogui
import math
import numpy as np
import ctypes
import time

# --- 1. SYSTEM OPTIMIZATION ---
# This ensures that your hand-tracking coordinates map 1:1 to Windows 11 screen pixels
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# Failsafe: Moving your real mouse to any corner of the screen will kill the script
pyautogui.FAILSAFE = True
# Set pause to 0 to make the cursor movement feel instant and responsive
pyautogui.PAUSE = 0

# --- 2. MEDIAPIPE INITIALIZATION ---
# Using version 0.10.11 for stability in your environment
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,        # Set to False for real-time video stream processing
    max_num_hands=1,                # Track only one hand to save CPU resources
    min_detection_confidence=0.7,   # Threshold to avoid 'ghost' hand detections
    min_tracking_confidence=0.7     # Threshold to maintain stable tracking during movement
)
mp_draw = mp.solutions.drawing_utils

# --- 3. GLOBAL VARIABLES & STATE ---
screen_w, screen_h = pyautogui.size() # Get monitor resolution (e.g., 1920x1080)
cam_w, cam_h = 640, 480               # Set camera resolution
reduction = 100                       # Create a border to make reaching screen edges easier
smoothening = 5                       # Lower values = more jitter, higher = smoother/slower
plocX, plocY = 0, 0                   # Previous locations for the low-pass filter algorithm
pScrollY = 0                          # Previous vertical position to calculate scroll delta

# State flags: Used to handle transitions (e.g., don't click twice for one palm show)
left_clicked = False  # Track if the "Long Press" (Pinch) is currently held down
palm_clicked = False  # Track if the "Quick Click" (Palm) has already fired

cap = cv2.VideoCapture(0)
cap.set(3, cam_w)
cap.set(4, cam_h)

print("Virtual Mouse System Online. Press 'q' on the video window to stop.")

try:
    while True:
        success, img = cap.read()
        if not success: break
        
        # Mirror the image so that moving your hand right moves the cursor right
        img = cv2.flip(img, 1)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_img)
        
        # Visual Aid: Draw the active movement area box
        cv2.rectangle(img, (reduction, reduction), (cam_w - reduction, cam_h - reduction), (255, 0, 255), 2)

        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                # Draw hand connections for visual feedback
                mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)
                lms = hand_lms.landmark
                
                # Extract coordinates for Index (8) and Thumb (4) tips
                x8, y8 = int(lms[8].x * cam_w), int(lms[8].y * cam_h)
                x4, y4 = int(lms[4].x * cam_w), int(lms[4].y * cam_h)

                # --- GESTURE DETECTION (Array of 0s and 1s) ---
                fingers = []
                # Thumb: Horizontal check relative to its base
                fingers.append(1 if lms[4].x < lms[3].x else 0)
                # Others: Vertical check (tip above PIP joint)
                for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
                    fingers.append(1 if lms[tip].y < lms[pip].y else 0)

                total_fingers = sum(fingers)

                # --- PRIORITY 1: PALM QUICK CLICK (Select/Button press) ---
                # Fires once when all 5 fingers are detected
                if total_fingers == 5:
                    if not palm_clicked:
                        pyautogui.click()
                        print("EVENT: Palm Quick Click")
                        cv2.putText(img, "QUICK CLICK", (200, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
                        palm_clicked = True
                    pScrollY = 0 # Lock scrolling to prevent jumping
                
                # --- PRIORITY 2: SCROLLING (Exactly 3 Fingers) ---
                elif total_fingers == 3 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1:
                    palm_clicked = False 
                    if pScrollY != 0:
                        diff = y8 - pScrollY
                        pyautogui.scroll(-diff * 5) # Multiplier for scroll speed
                    pScrollY = y8
                    cv2.putText(img, "SCROLLING", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                
                else:
                    # Reset these states if the hand changes shape
                    pScrollY = 0 
                    palm_clicked = False
                    
                    # --- PRIORITY 3: CURSOR MOVEMENT (Movement active if Index is UP) ---
                    if fingers[1] == 1:
                        # Linear Interpolation: Map cam frame to screen resolution
                        fx = np.interp(x8, (reduction, cam_w - reduction), (0, screen_w))
                        fy = np.interp(y8, (reduction, cam_h - reduction), (0, screen_h))
                        
                        # Smoothing: Low-pass filter to dampen hand tremors
                        curr_x = plocX + (fx - plocX) / smoothening
                        curr_y = plocY + (fy - plocY) / smoothening
                        
                        pyautogui.moveTo(curr_x, curr_y)
                        plocX, plocY = curr_x, curr_y

                    # --- PRIORITY 4: PINCH LONG CLICK (Text Selection/Dragging) ---
                    # Calculate distance between Index (8) and Thumb (4)
                    dist = math.hypot(x8 - x4, y8 - y4)

                    # Triggered when fingers touch
                    if dist < 40:
                        if not left_clicked:
                            pyautogui.mouseDown(button='left') # Press and hold
                            left_clicked = True
                            print("EVENT: Long Press Start (Drag/Select)")
                        cv2.circle(img, (x8, y8), 15, (0, 255, 0), cv2.FILLED)
                        cv2.putText(img, "SELECTING", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # Triggered when fingers separate (Hysteresis included)
                    elif dist > 55:
                        if left_clicked:
                            pyautogui.mouseUp(button='left') # Release
                            left_clicked = False
                            print("EVENT: Long Press End")

        cv2.imshow("Virtual Mouse - NIT Patna", img)
        # Standard exit check: 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'): break
finally:
    # Safely release the camera for other apps to use
    cap.release()
    cv2.destroyAllWindows()
    print("System Standby.")


# In[ ]:





# In[ ]:




