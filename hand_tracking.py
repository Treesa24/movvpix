import cv2
import mediapipe as mp

class FingerTracker:
    def __init__(self):
        # Using the legacy solutions API compatible with mediapipe==0.10.14
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

    def get_position(self, frame):
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Landmark 8 is the Index Finger Tip
                lm = hand_landmarks.landmark[8]
                return int(lm.x * w), int(lm.y * h)
        return None