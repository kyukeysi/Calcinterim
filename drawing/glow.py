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
        self.has_content = False
        self.bbox = None

    def clear(self):
        if self.has_content:
            if self.bbox is not None:
                x1, y1, x2, y2 = self.bbox
                self.trail[y1:y2, x1:x2] = 0
            else:
                self.trail.fill(0)
            self.has_content = False
            self.bbox = None

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

        self.has_content = True
        pad = self.glow_size + 16
        x_min = max(0, min(x1, x2) - pad)
        y_min = max(0, min(y1, y2) - pad)
        x_max = min(self.width, max(x1, x2) + pad)
        y_max = min(self.height, max(y1, y2) + pad)

        if self.bbox is None:
            self.bbox = [x_min, y_min, x_max, y_max]
        else:
            self.bbox[0] = min(self.bbox[0], x_min)
            self.bbox[1] = min(self.bbox[1], y_min)
            self.bbox[2] = max(self.bbox[2], x_max)
            self.bbox[3] = max(self.bbox[3], y_max)

    def render(self, frame):
        if not self.has_content or self.bbox is None:
            return frame

        x1, y1, x2, y2 = self.bbox
        if x2 <= x1 or y2 <= y1:
            return frame

        roi_trail = self.trail[y1:y2, x1:x2]
        roi_frame = frame[y1:y2, x1:x2]

        trail_bgr = roi_trail[:, :, :3]
        small = cv2.resize(trail_bgr, (0, 0), fx=0.5, fy=0.5, interpolation=cv2.INTER_LINEAR)
        blurred_small = cv2.GaussianBlur(small, (0, 0), 6)
        blurred = cv2.resize(blurred_small, (roi_trail.shape[1], roi_trail.shape[0]), interpolation=cv2.INTER_LINEAR)

        alpha = (roi_trail[:, :, 3].astype(np.uint16) * 140) >> 8
        alpha = alpha[:, :, None]
        inv_alpha = 255 - alpha

        blended = ((roi_frame.astype(np.uint16) * inv_alpha + blurred.astype(np.uint16) * alpha) >> 8).astype(np.uint8)

        result = frame.copy()
        result[y1:y2, x1:x2] = blended
        return result