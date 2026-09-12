import cv2
import numpy as np
import pyautogui
import time
from tracker import HandTracker
import config

# Defensive UI configurations
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.001


def run():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAM_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAM_H)

    tracker = HandTracker()

    prev_x, prev_y = 0, 0
    curr_x, curr_y = 0, 0
    prev_scroll_y = 0
    
    last_action_time = 0
    action_delay = 0.4
    is_dragging = False
    click_reset_ready = True  # Track click release states cleanly

    thumbs_up_start_time = 0
    right_click_fired = False

    last_seen_hand_time = time.time()
    debounce_delay = 0.4  

    mode_text = "INITIALIZING SYSTEM"

    cv2.namedWindow("AeroMouse Controller", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("AeroMouse Controller", cv2.WND_PROP_TOPMOST, 1)

    print("AeroMouse Active. Press 'q' in camera window to exit.")

    # ✅ PRODUCTION WRAPPER: Try-Finally block prevents mouse control lockouts on crash
    try:
        while cap.isOpened():
            success, img = cap.read()
            if not success:
                continue

            img = cv2.flip(img, 1)
            results = tracker.process_frame(img)

            if results.multi_hand_landmarks and len(results.multi_hand_landmarks) > 0:
                last_seen_hand_time = time.time()
                
                hand_lms = results.multi_hand_landmarks[0]
                tracker.mp_draw.draw_landmarks(img, hand_lms, tracker.mp_hands.HAND_CONNECTIONS)
                
                pixel_coords, lms = tracker.get_landmark_coords(hand_lms)
                fingers = tracker.detect_finger_states(lms)

                thumb_pt = pixel_coords[4]
                index_pt = pixel_coords[8]

                target_x = np.interp(
                    index_pt[0], 
                    (config.FRAME_REDUCTION, config.CAM_W - config.FRAME_REDUCTION), 
                    (0, config.SCREEN_W)
                )
                target_y = np.interp(
                    index_pt[1], 
                    (config.FRAME_REDUCTION, config.CAM_H - config.FRAME_REDUCTION), 
                    (0, config.SCREEN_H)
                )

                curr_x = prev_x + (target_x - prev_x) / config.SMOOTHING
                curr_y = prev_y + (target_y - prev_y) / config.SMOOTHING

                pinch_dist = tracker.euclidean_distance(index_pt, thumb_pt)

                is_palm_open = sum(fingers) >= 4  
                is_thumbs_up = (lms[4].y < lms[3].y and lms[4].y < lms[2].y) and (fingers[1:] ==[0,0,0,0])
                is_index_up = (fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0)
                is_three_fingers = (fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0)
                is_fist = sum(fingers) == 0

                # 1. PALM OPEN COMPLETELY -> STANDBY / NEUTRAL MODE
                if is_palm_open:
                    if is_dragging:
                        pyautogui.mouseUp()
                        is_dragging = False
                    mode_text = "STANDBY (PALM OPEN)"
                    prev_scroll_y = 0
                    prev_x, prev_y = curr_x, curr_y
                    thumbs_up_start_time = 0
                    right_click_fired = False
                    click_reset_ready = True

                # 2. PINCH -> PURE TEXT SELECTION / DRAGGING MODE
                elif pinch_dist < config.PINCH_THRESH:
                    cv2.circle(img, index_pt, 12, (0, 255, 0), cv2.FILLED)
                    cv2.circle(img, thumb_pt, 12, (0, 255, 0), cv2.FILLED)

                    if not is_dragging:
                        if time.time() - last_action_time > action_delay and click_reset_ready:
                            pyautogui.click()
                            last_action_time = time.time()
                            click_reset_ready = False  # Lock multi-clicks until hand releases pinch
                            mode_text = "LEFT CLICK"
                            is_dragging = True
                    else:
                        pyautogui.mouseDown()
                        pyautogui.moveTo(curr_x, curr_y)
                        mode_text = "SELECTING TEXT / DRAGGING"
                    prev_scroll_y = 0
                    prev_x, prev_y = curr_x, curr_y
                    thumbs_up_start_time = 0
                    right_click_fired = False

                # 3. THUMBS UP -> STABLE RIGHT CLICK HOLD WITH SINGLE-SHOT TRIGGER
                elif is_thumbs_up:
                    if is_dragging:
                        pyautogui.mouseUp()
                        is_dragging = False
                    prev_scroll_y = 0
                    click_reset_ready = True

                    if thumbs_up_start_time == 0:
                        thumbs_up_start_time = time.time()
                        mode_text = "HOLDING THUMBS UP..."
                    elif time.time() - thumbs_up_start_time >= 0.5:
                        if not right_click_fired:
                            pyautogui.rightClick()
                            right_click_fired = True
                            mode_text = "RIGHT CLICK FIRED"
                        else:
                            mode_text = "CONTEXT MENU ACTIVE (RELEASE HAND)"
                        cv2.circle(img, thumb_pt, 16, (0, 0, 255), cv2.FILLED)
                    else:
                        hold_progress = int((time.time() - thumbs_up_start_time) / 0.5 * 100)
                        mode_text = f"HOLDING... {hold_progress}%"
                        cv2.circle(img, thumb_pt, 10, (255, 100, 0), cv2.FILLED)

                # 4. THREE FINGERS -> SCROLLING MODE
                elif is_three_fingers:
                    if is_dragging:
                        pyautogui.mouseUp()
                        is_dragging = False
                    thumbs_up_start_time = 0
                    right_click_fired = False
                    click_reset_ready = True

                    if prev_scroll_y != 0:
                        diff = prev_scroll_y - index_pt[1]
                        if abs(diff) > 8:
                            pyautogui.scroll(int(diff * 4))
                            mode_text = "SCROLLING UP" if diff > 0 else "SCROLLING DOWN"
                    else:
                        mode_text = "SCROLL MODE READY"
                    prev_scroll_y = index_pt[1]

                # 5. ACTIVE INDEX FINGER TRACKING -> MOVE CURSOR
                elif is_index_up:
                    if is_dragging:
                        pyautogui.mouseUp()
                        is_dragging = False
                    thumbs_up_start_time = 0
                    right_click_fired = False
                    click_reset_ready = True

                    pyautogui.moveTo(curr_x, curr_y)
                    mode_text = "MOVING CURSOR"
                    prev_scroll_y = 0
                    prev_x, prev_y = curr_x, curr_y

                # 6. CLOSED FIST -> PAUSE / RELEASE
                elif is_fist:
                    if is_dragging:
                        pyautogui.mouseUp()
                        is_dragging = False
                    thumbs_up_start_time = 0
                    right_click_fired = False
                    click_reset_ready = True
                    mode_text = "PAUSED (FIST)"
                    prev_scroll_y = 0

                else:
                    prev_scroll_y = 0
                    thumbs_up_start_time = 0
                    right_click_fired = False
                    # Open palm reset path helper
                    if pinch_dist > config.PINCH_THRESH + 15:
                        click_reset_ready = True
                
                prev_x, prev_y = curr_x, curr_y
                
            else:
                if time.time() - last_seen_hand_time > debounce_delay:
                    if is_dragging:
                        pyautogui.mouseUp()
                        is_dragging = False
                    mode_text = "SEARCHING FOR HAND"
                    prev_scroll_y = 0
                    thumbs_up_start_time = 0
                    right_click_fired = False
                    click_reset_ready = True

            cv2.putText(img, f"Mode: {mode_text}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            cv2.imshow("AeroMouse Controller", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    # ✅ ALWAYS EXECUTE DETACH COOLDOWN ON SHUTDOWN
    finally:
        print("\n🔄 Running clean environment hardware detachment loops...")
        pyautogui.mouseUp()
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Hardware clean release successful. Safe exit.")


if __name__ == "__main__":
    run()
