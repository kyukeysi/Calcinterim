import cv2
import numpy as np


class GlowRenderer:
    def __init__(
        self,
        width=1280,
        height=720,
        glow_size=14,
        middle_size=6,
        core_size=2
    ):
        self.width = width
        self.height = height

        self.glow_size = glow_size
        self.middle_size = middle_size
        self.core_size = core_size

        self.trail = np.zeros(
            (height, width, 4),
            dtype=np.uint8
        )

    def clear(self):
        self.trail.fill(0)

    def draw_spell_line(self, point_a, point_b):
        x1, y1 = int(point_a[0]), int(point_a[1])
        x2, y2 = int(point_b[0]), int(point_b[1])

        cv2.line(
            self.trail,
            (x1, y1),
            (x2, y2),
            (0, 80, 255, 180),
            self.glow_size,
            cv2.LINE_AA
        )

        cv2.line(
            self.trail,
            (x1, y1),
            (x2, y2),
            (0, 160, 255, 230),
            self.middle_size,
            cv2.LINE_AA
        )

        cv2.line(
            self.trail,
            (x1, y1),
            (x2, y2),
            (180, 240, 255, 255),
            self.core_size,
            cv2.LINE_AA
        )

    def render(self, frame):
        glow_layer = self.trail[:, :, :3]

        blurred = cv2.GaussianBlur(
            glow_layer,
            (0, 0),
            12
        )

        alpha = self.trail[:, :, 3].astype(np.float32) / 255.0

        alpha = alpha[:, :, np.newaxis]

        frame_float = frame.astype(np.float32)
        glow_float = blurred.astype(np.float32)

        result = (
            frame_float * (1.0 - alpha * 0.55)
            + glow_float * (alpha * 0.55)
        )

        result = np.clip(result, 0, 255).astype(np.uint8)

        return result