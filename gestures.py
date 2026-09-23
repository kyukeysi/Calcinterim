from collections import deque
import math
import time


def distance(point_a, point_b):
    return math.hypot(
        point_a.x - point_b.x,
        point_a.y - point_b.y
    )


def index_is_up(hand):
    return hand[8].y < hand[6].y


def thumb_is_out(hand):
    wrist = hand[0]
    thumb_tip = hand[4]
    index_mcp = hand[5]

    hand_size = distance(
        wrist,
        hand[9]
    )

    thumb_distance = distance(
        thumb_tip,
        index_mcp
    )

    return thumb_distance > hand_size * 0.45


def thumb_is_raised(hand):
    return hand[4].y < hand[3].y


def is_drawing_gesture(hand):
    return (
        index_is_up(hand)
        and thumb_is_out(hand)
    )


def is_open_palm(hand):
    fingers_extended = 0

    finger_pairs = [
        (8, 6),
        (12, 10),
        (16, 14),
        (20, 18)
    ]

    for tip, pip in finger_pairs:
        if hand[tip].y < hand[pip].y:
            fingers_extended += 1

    return fingers_extended >= 4


def is_closed_fist(hand):
    """
    Detects a closed fist by checking whether
    the four main fingers are curled toward
    the palm.
    """

    finger_pairs = [
        (8, 6),
        (12, 10),
        (16, 14),
        (20, 18)
    ]

    folded_fingers = 0

    for tip, pip in finger_pairs:
        tip_to_wrist = distance(
            hand[tip],
            hand[0]
        )

        pip_to_wrist = distance(
            hand[pip],
            hand[0]
        )

        if tip_to_wrist < pip_to_wrist:
            folded_fingers += 1

    return folded_fingers >= 4


class GestureController:
    def __init__(
        self,
        commit_release_frames=3,
        open_palm_clear_frames=5,
        fist_hold_frames=5
    ):
        self.was_drawing = False
        self.release_frames = 0
        self.open_palm_frames = 0
        self.fist_frames = 0
        self.fist_fired = False

        self.commit_release_frames = (
            commit_release_frames
        )

        self.open_palm_clear_frames = (
            open_palm_clear_frames
        )

        self.fist_hold_frames = (
            fist_hold_frames
        )

    def update(self, hand):
        if hand is None:
            self.release_frames = 0
            self.open_palm_frames = 0
            self.fist_frames = 0
            self.fist_fired = False

            if self.was_drawing:
                self.release_frames += 1

                if (
                    self.release_frames
                    >= self.commit_release_frames
                ):
                    self.was_drawing = False
                    self.release_frames = 0

                    return "COMMIT"

            return "NONE"

        if is_open_palm(hand):
            self.open_palm_frames += 1
            self.fist_frames = 0
            self.fist_fired = False

            if (
                self.open_palm_frames
                >= self.open_palm_clear_frames
            ):
                self.was_drawing = False
                self.release_frames = 0
                self.open_palm_frames = 0

                return "CLEAR"

        else:
            self.open_palm_frames = 0

        if is_closed_fist(hand):
            self.fist_frames += 1
            self.was_drawing = False
            self.release_frames = 0

            if (
                not self.fist_fired
                and self.fist_frames
                >= self.fist_hold_frames
            ):
                self.fist_fired = True
                return "ENTER"

            return "FIST_HOLD"

        else:
            self.fist_frames = 0
            self.fist_fired = False

        if is_drawing_gesture(hand):
            self.was_drawing = True
            self.release_frames = 0

            return "DRAW"

        if self.was_drawing:
            self.release_frames += 1

            if (
                self.release_frames
                >= self.commit_release_frames
            ):
                self.was_drawing = False
                self.release_frames = 0

                return "COMMIT"

            return "DRAW"

        return "IDLE"


class CircleGestureDetector:
    """
    Detects continuous circular hand movement in the air.
    Triggers when the cumulative revolutions in a consistent direction
    exceed target_revolutions (default: 4.0, i.e., > 4 full circles).
    """

    def __init__(
        self,
        target_revolutions=4.0,
        min_radius=25,
        max_inactivity=1.2,
        history_len=120,
        cooldown=2.0
    ):
        self.target_revolutions = target_revolutions
        self.min_radius = min_radius
        self.max_inactivity = max_inactivity
        self.history_len = history_len
        self.cooldown = cooldown

        self.points = deque(maxlen=history_len)
        self.total_angle = 0.0
        self.last_angle = None
        self.last_point_time = 0.0
        self.last_trigger_time = 0.0
        self.center = None
        self.current_radius = 0.0

    def reset(self):
        self.points.clear()
        self.total_angle = 0.0
        self.last_angle = None
        self.center = None
        self.current_radius = 0.0

    def update(self, point, current_time=None):
        if current_time is None:
            current_time = time.monotonic()

        if current_time - self.last_trigger_time < self.cooldown:
            return False, {
                "revolutions": 0.0,
                "progress": 0.0,
                "center": None,
                "radius": 0.0,
                "direction": None
            }

        if point is None:
            if current_time - self.last_point_time > self.max_inactivity:
                self.reset()
            revs = abs(self.total_angle) / (2.0 * math.pi)
            return False, {
                "revolutions": revs,
                "progress": min(1.0, revs / self.target_revolutions),
                "center": self.center,
                "radius": self.current_radius,
                "direction": "CW" if self.total_angle < 0 else ("CCW" if self.total_angle > 0 else None)
            }

        if self.points and (current_time - self.last_point_time > self.max_inactivity):
            self.reset()

        self.last_point_time = current_time
        px, py = point

        if self.points:
            last_x, last_y, _ = self.points[-1]
            if math.hypot(px - last_x, py - last_y) < 3.0:
                revs = abs(self.total_angle) / (2.0 * math.pi)
                return False, {
                    "revolutions": revs,
                    "progress": min(1.0, revs / self.target_revolutions),
                    "center": self.center,
                    "radius": self.current_radius,
                    "direction": "CW" if self.total_angle < 0 else ("CCW" if self.total_angle > 0 else None)
                }

        self.points.append((px, py, current_time))

        if len(self.points) < 8:
            return False, {
                "revolutions": 0.0,
                "progress": 0.0,
                "center": None,
                "radius": 0.0,
                "direction": None
            }

        recent_pts = [p for p in self.points if current_time - p[2] <= 2.0]
        if len(recent_pts) < 6:
            recent_pts = list(self.points)

        xs = [p[0] for p in recent_pts]
        ys = [p[1] for p in recent_pts]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        w = max_x - min_x
        h = max_y - min_y

        cx = (min_x + max_x) / 2.0
        cy = (min_y + max_y) / 2.0
        self.center = (int(cx), int(cy))

        avg_radius = (w + h) / 4.0
        self.current_radius = avg_radius

        aspect = (w / h) if h > 0 else 0
        if avg_radius < self.min_radius or aspect < 0.35 or aspect > 2.85:
            self.total_angle *= 0.95
            self.last_angle = None
            revs = abs(self.total_angle) / (2.0 * math.pi)
            return False, {
                "revolutions": revs,
                "progress": min(1.0, revs / self.target_revolutions),
                "center": self.center,
                "radius": self.current_radius,
                "direction": None
            }

        current_angle = math.atan2(py - cy, px - cx)

        if self.last_angle is not None:
            dtheta = current_angle - self.last_angle
            dtheta = (dtheta + math.pi) % (2.0 * math.pi) - math.pi

            if abs(dtheta) < math.pi * 0.6:
                if abs(self.total_angle) > math.pi * 0.5:
                    existing_sign = 1 if self.total_angle > 0 else -1
                    delta_sign = 1 if dtheta > 0 else -1
                    if existing_sign != delta_sign and abs(dtheta) > 0.15:
                        self.total_angle *= 0.85
                    else:
                        self.total_angle += dtheta
                else:
                    self.total_angle += dtheta

        self.last_angle = current_angle

        revolutions = abs(self.total_angle) / (2.0 * math.pi)
        progress = min(1.0, revolutions / self.target_revolutions)
        direction = "CW" if self.total_angle < 0 else ("CCW" if self.total_angle > 0 else None)

        triggered = False
        if revolutions > self.target_revolutions:
            triggered = True
            self.last_trigger_time = current_time
            self.reset()

        return triggered, {
            "revolutions": revolutions,
            "progress": progress,
            "center": self.center,
            "radius": self.current_radius,
            "direction": direction
        }