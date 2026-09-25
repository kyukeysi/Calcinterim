import threading
import time
import cv2


class Camera:
    def __init__(
        self,
        camera_index=0,
        width=1280,
        height=720,
        fps=30,
        mirror=True,
        threaded=True
    ):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps
        self.mirror = mirror
        self.threaded = threaded

        self.capture = None
        self.frame = None
        self.running = False
        self.lock = threading.Lock()
        self.thread = None

    def open(self):
        self.capture = cv2.VideoCapture(self.camera_index)

        if not self.capture.isOpened():
            raise RuntimeError("Could not open webcam.")

        # Request MJPG for high framerate capture if supported by hardware
        try:
            self.capture.set(
                cv2.CAP_PROP_FOURCC,
                cv2.VideoWriter_fourcc(*"MJPG")
            )
        except Exception:
            pass

        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        if self.fps:
            self.capture.set(cv2.CAP_PROP_FPS, self.fps)

        # Minimize driver buffer latency
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if self.threaded:
            # Warm up first frame
            success, initial_frame = self.capture.read()
            if success and initial_frame is not None:
                if self.mirror:
                    initial_frame = cv2.flip(initial_frame, 1)
                self.frame = initial_frame

            self.running = True
            self.thread = threading.Thread(
                target=self._capture_worker,
                daemon=True
            )
            self.thread.start()

    def _capture_worker(self):
        while self.running:
            if self.capture is None or not self.capture.isOpened():
                break

            success, frame = self.capture.read()
            if success and frame is not None:
                if self.mirror:
                    frame = cv2.flip(frame, 1)

                with self.lock:
                    self.frame = frame
            else:
                time.sleep(0.005)

    def read(self):
        if self.capture is None:
            return None

        if self.threaded:
            with self.lock:
                if self.frame is not None:
                    return self.frame.copy()
                return None
        else:
            success, frame = self.capture.read()
            if not success or frame is None:
                return None

            if self.mirror:
                frame = cv2.flip(frame, 1)

            return frame

    def release(self):
        self.running = False
        if self.thread is not None:
            self.thread.join(timeout=0.5)
            self.thread = None

        if self.capture is not None:
            self.capture.release()
            self.capture = None

    def is_opened(self):
        return self.capture is not None and self.capture.isOpened()