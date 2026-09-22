import math

import cv2


class SpellRing:
    def __init__(self):
        self.angle = 0.0
        self.radius = 55
        self.visible = False

    def update(self, delta_time):
        self.angle += 90.0 * delta_time

        if self.angle >= 360.0:
            self.angle -= 360.0

    def set_visible(self, visible):
        self.visible = visible

    def draw(self, frame, center):
        if not self.visible or center is None:
            return

        x, y = int(center[0]), int(center[1])

        cv2.circle(
            frame,
            (x, y),
            self.radius,
            (0, 90, 255),
            2,
            cv2.LINE_AA
        )

        cv2.circle(
            frame,
            (x, y),
            self.radius - 10,
            (0, 160, 255),
            1,
            cv2.LINE_AA
        )

        for offset in (0, 90, 180, 270):
            angle = math.radians(self.angle + offset)

            start_x = int(
                x + math.cos(angle) * (self.radius - 8)
            )
            start_y = int(
                y + math.sin(angle) * (self.radius - 8)
            )

            end_x = int(
                x + math.cos(angle) * (self.radius + 8)
            )
            end_y = int(
                y + math.sin(angle) * (self.radius + 8)
            )

            cv2.line(
                frame,
                (start_x, start_y),
                (end_x, end_y),
                (180, 220, 255),
                2,
                cv2.LINE_AA
            )