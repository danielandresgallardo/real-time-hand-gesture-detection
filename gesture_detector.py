import cv2
import mediapipe as mp
import time
import math

def run_gesture_detection(queue, stop_event):
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Hand Gesture", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Hand Gesture", 480, 360)

    last_gesture = None
    last_time = 0
    gesture_count = 0
    gesture_timeout = 1.0

    open_palm_duration = 0
    in_command_mode = False

    def classify_gesture(landmarks):
        tips_ids = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        fingers = []
        if landmarks[tips_ids[0]].x < landmarks[tips_ids[0] - 1].x:
            fingers.append(1)
        else:
            fingers.append(0)
        for id in range(1, 5):
            if landmarks[tips_ids[id]].y < landmarks[tips_ids[id] - 2].y:
                fingers.append(1)
            else:
                fingers.append(0)
        if fingers == [0, 0, 0, 0, 0]:
            return "Fist"
        elif fingers == [1, 1, 1, 1, 1]:
            return "Open Palm"
        elif fingers == [0, 1, 0, 0, 0]:
            return "Index Point"
        else:
            return "Unknown"

    def trigger_action(count):
        print(f"Gesture: {count} → sending to HUD")
        queue.put(count)

    while not stop_event.is_set():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)
        current_time = time.time()

        gesture = "Unknown"

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                gesture = classify_gesture(hand_landmarks.landmark)

                if gesture == "Index Point":
                    index_tip = hand_landmarks.landmark[8]  # Index finger tip
                    x = int(index_tip.x * 463)
                    y = int(index_tip.y * 260)
                    queue.put(("cursor", x, y))

                if not in_command_mode:
                    if gesture == "Open Palm":
                        open_palm_duration += 1
                    else:
                        open_palm_duration = 0
                    if open_palm_duration >= 30:
                        in_command_mode = True
                        print("Palm detected. Waiting for command...")
                        open_palm_duration = 0
                elif in_command_mode:
                    if gesture == "Fist":
                        if last_gesture != "Fist":
                            gesture_count += 1
                            last_time = current_time
                            print(f"Detected Fist {gesture_count}x")
                        last_gesture = "Fist"
                    else:
                        last_gesture = gesture

        if in_command_mode and gesture_count > 0 and (current_time - last_time) > gesture_timeout:
            trigger_action(gesture_count)
            gesture_count = 0
            in_command_mode = False
            open_palm_duration = 0
            print("Returning to palm check mode")

        if not in_command_mode:
            cv2.putText(frame, "Show open palm for 1s to begin", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        else:
            cv2.putText(frame, "Waiting for command...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("Hand Gesture", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            stop_event.set()
            break

    cap.release()
    cv2.destroyAllWindows()