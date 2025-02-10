import cv2
import mediapipe as mp
import math
import os
import time


class HandDetector:
    def __init__(self, mode=False, maxHands=2, detectionConf=0.5, trackConf=0.5):
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=mode,
            max_num_hands=maxHands,
            min_detection_confidence=detectionConf,
            min_tracking_confidence=trackConf
        )
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        img = cv2.flip(img, 1)
        self.results = self.hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if draw and self.results.multi_hand_landmarks:
            for hand in self.results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(img, hand, mp.solutions.hands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, draw=True):
        lmList = []
        if self.results.multi_hand_landmarks:
            for hand in self.results.multi_hand_landmarks:
                for id, lm in enumerate(hand.landmark):
                    if id in [4, 8]:  # Thumb tip (4) and index finger tip (8)
                        h, w, _ = img.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        lmList.append([id, cx, cy])
                        if draw:
                            cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
        return lmList


def set_volume_mac(volume):
    os.system(f"osascript -e 'set volume output volume {max(0, min(100, volume))}'")


cap = cv2.VideoCapture(0)
detector = HandDetector()

prev_time = 0  # For FPS calculation

while True:
    success, img = cap.read()
    if not success:
        break

    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    volume = 0  # Default volume level

    if len(lmList) == 2:
        x1, y1, x2, y2 = *lmList[0][1:], *lmList[1][1:]
        length = math.dist((x1, y1), (x2, y2))
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 5)

        if length < 50:
            cv2.circle(img, ((x1 + x2) // 2, (y1 + y2) // 2), 10, (0, 255, 0), cv2.FILLED)

        min_length = 8
        max_length = 180

        if length < min_length:
            volume = 0
        elif length > max_length:
            volume = 100
        else:
            volume = int(((length - min_length) / (max_length - min_length)) * 100)

        set_volume_mac(volume)

    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time


    cv2.putText(img, f"FPS: {int(fps)}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

    cv2.imshow("Hand Tracker", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
