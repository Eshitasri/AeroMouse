#!/usr/bin/env python
# coding: utf-8

# In[2]:


# 1. Remove the current version
get_ipython().system('pip uninstall mediapipe -y')

# 2. Install the stable version you used for EchoSign
get_ipython().system('pip install mediapipe==0.10.11')


# In[ ]:


import cv2
import mediapipe as mp
import pyautogui
import math
import numpy as np
import ctypes
import time
last_right_click=0

# --- 1. SYSTEM OPTIMIZATION ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

# --- 2. MEDIAPIPE INITIALIZATION ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

# --- 3. GLOBAL VARIABLES ---
screen_w, screen_h = pyautogui.size()
cam_w, cam_h = 640, 480
reduction = 40
smoothening = 5

plocX, plocY = 0, 0
pScrollY = 0

left_clicked = False
palm_clicked = False

pTime = 0

# --- CAMERA ---
cap = cv2.VideoCapture(0)
cap.set(3, cam_w)
cap.set(4, cam_h)

print("AeroMouse Online. Press 'q' to quit.")

try:

    # ---------------- MAIN LOOP ----------------
    while True:

        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_img)

        # Draw movement box
        cv2.rectangle(img, (reduction, reduction),
                      (cam_w - reduction, cam_h - reduction),
                      (255, 0, 255), 2)

        if results.multi_hand_landmarks:

            for hand_lms in results.multi_hand_landmarks:

                mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)

                lms = hand_lms.landmark

                # fingertip coordinates
                x8, y8 = int(lms[8].x * cam_w), int(lms[8].y * cam_h)
                x4, y4 = int(lms[4].x * cam_w), int(lms[4].y * cam_h)

                cv2.circle(img,(x8,y8),10,(255,0,255),cv2.FILLED)

                # -------- FINGER STATE DETECTION --------
                fingers = []

                fingers.append(1 if lms[4].x < lms[3].x else 0)

                for tip, pip in [(8,6),(12,10),(16,14),(20,18)]:
                    fingers.append(1 if lms[tip].y < lms[pip].y else 0)

                total_fingers = sum(fingers)

                # -------- 1. PALM CLICK --------
                if total_fingers == 5:

                    if not palm_clicked:
                        pyautogui.click()
                        print("EVENT: Palm Click")

                        cv2.putText(img,"QUICK CLICK",(200,50),
                                    cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),3)

                        palm_clicked = True

                    pScrollY = 0

                    #---------------RIGHT Click-----------
                                    
                elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:

                    if time.time() - last_right_click > 0.5:
                        pyautogui.rightClick()
                        last_right_click = time.time()
    
                    cv2.putText(img,"RIGHT CLICK",(200,150),
                    cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),3)

                # -------- 2. SCROLL --------
                elif total_fingers == 3 and fingers[1] and fingers[2] and fingers[3]:

                    palm_clicked = False

                    if pScrollY != 0:
                        diff = y8 - pScrollY
                        pyautogui.scroll(-diff * 5)

                    pScrollY = y8

                    cv2.putText(img,"SCROLLING",(20,50),
                                cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2)


                # -------- OTHER MODES --------
                else:

                    palm_clicked = False
                    pScrollY = 0

                    # -------- CURSOR MOVE --------
                    if fingers[1] == 1:

                        fx = np.interp(x8,(reduction,cam_w-reduction),(0,screen_w))
                        fy = np.interp(y8,(reduction,cam_h-reduction),(0,screen_h))

                        curr_x = plocX + (fx - plocX)/smoothening
                        curr_y = plocY + (fy - plocY)/smoothening

                        pyautogui.moveTo(curr_x,curr_y)

                        plocX, plocY = curr_x, curr_y


                    # -------- PINCH DRAG --------
                    dist = math.hypot(x8 - x4, y8 - y4)

                    if dist < 40:

                        if not left_clicked:
                            pyautogui.mouseDown(button='left')
                            left_clicked = True
                            print("EVENT: Drag Start")

                        cv2.circle(img,(x8,y8),15,(0,255,0),cv2.FILLED)

                        cv2.putText(img,"SELECTING",(200,100),
                                    cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)


                    elif dist > 55:

                        if left_clicked:
                            pyautogui.mouseUp(button='left')
                            left_clicked = False
                            print("EVENT: Drag End")


        # -------- FPS COUNTER --------
        cTime = time.time()
        fps = 1/(cTime - pTime) if (cTime - pTime) != 0 else 0
        pTime = cTime

        cv2.putText(img,f'FPS: {int(fps)}',(20,40),
                    cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)

        # -------- DISPLAY --------
        cv2.imshow("AeroMouse", img)
        cv2.setWindowProperty("AeroMouse", cv2.WND_PROP_TOPMOST, 1)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


finally:

    cap.release()
    cv2.destroyAllWindows()
    print("System Standby.")











