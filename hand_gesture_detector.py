import cv2
import mediapipe as mp
import numpy as np
import time

# Gesture tracking variables
last_gesture = None
last_time = 0
gesture_count = 0
gesture_timeout = 1.0  # seconds to wait before interpreting

# Setup MediaPipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# Gesture classifier (very basic example)
def classify_gesture(landmarks):
    # Tip of each finger (thumb is special case)
    tips_ids = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb
    if landmarks[tips_ids[0]].x < landmarks[tips_ids[0] - 1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other 4 fingers
    for id in range(1, 5):
        if landmarks[tips_ids[id]].y < landmarks[tips_ids[id] - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    # Gesture rules
    if fingers == [0, 0, 0, 0, 0]:
        return "Fist"
    elif fingers == [1, 1, 1, 1, 1]:
        return "Open Palm"
    elif fingers == [0, 1, 1, 0, 0]:
        return "Peace"
    else:
        return "Unknown"

def trigger_action(count):
    if count == 1:
        print("▶️ Play/Pause")
    elif count == 2:
        print("⏭️ Next Song")
    elif count == 3:
        print("⏮️ Previous Song")
    else:
        print(f"✋ Unmapped gesture count: {count}")

# Start webcam
cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    current_time = time.time()

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            gesture = classify_gesture(hand_landmarks.landmark)

            if gesture == "Fist":
                if last_gesture != "Fist":
                    gesture_count += 1
                    last_time = current_time
                    print(f"Detected Fist {gesture_count}x")
                last_gesture = "Fist"
            else:
                last_gesture = gesture

    # If timeout passed, trigger action and reset
    if gesture_count > 0 and (current_time - last_time) > gesture_timeout:
        trigger_action(gesture_count)
        gesture_count = 0

    # Show on screen
    cv2.putText(frame, f'Fist Count: {gesture_count}', (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 100, 255), 2)
    cv2.imshow("Gesture Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()