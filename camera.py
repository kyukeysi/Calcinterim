import cv2


class Camera:
    def __init__(
        self,
        camera_index=0,
        width=1280,
        height=720,
        mirror=True
    ):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.mirror = mirror
        self.capture = None

    def open(self):
        self.capture = cv2.VideoCapture(self.camera_index)

        if not self.capture.isOpened():
            raise RuntimeError("Could not open webcam.")

        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

    def read(self):
        if self.capture is None:
            return None

        success, frame = self.capture.read()

        if not success:
            return None

        if self.mirror:
            frame = cv2.flip(frame, 1)

        return frame

    def release(self):
        if self.capture is not None:
            self.capture.release()
            self.capture = None

    def is_opened(self):
        return self.capture is not None and self.capture.isOpened()