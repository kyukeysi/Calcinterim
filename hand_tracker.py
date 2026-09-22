import cv2
import mediapipe as mp


class HandTracker:
    def __init__(self, model_path, num_hands=1):
        self.model_path = model_path

        self.base_options = mp.tasks.BaseOptions(
            model_asset_path=model_path
        )

        self.options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=self.base_options,
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=num_hands,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.landmarker = mp.tasks.vision.HandLandmarker.create_from_options(
            self.options
        )

    def process(self, frame, timestamp_ms):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        result = self.landmarker.detect_for_video(
            image,
            timestamp_ms
        )

        if not result.hand_landmarks:
            return None

        return result.hand_landmarks[0]

    def close(self):
        self.landmarker.close()