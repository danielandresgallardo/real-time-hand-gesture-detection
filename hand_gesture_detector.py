import cv2
import mediapipe as mp
import numpy as np

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

# Start webcam
cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    if not success:
        break

    # Flip and convert
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Gesture classification
            gesture = classify_gesture(hand_landmarks.landmark)
            cv2.putText(frame, f'Gesture: {gesture}', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show video
    cv2.imshow("Hand Gesture Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()