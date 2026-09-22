import math


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

    hand_size = distance(wrist, hand[9])
    thumb_distance = distance(thumb_tip, index_mcp)

    return thumb_distance > hand_size * 0.45


def thumb_is_raised(hand):
    return hand[4].y < hand[3].y


def is_drawing_gesture(hand):
    return index_is_up(hand) and thumb_is_out(hand)


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


class GestureController:
    def __init__(
        self,
        commit_release_frames=3,
        open_palm_clear_frames=5
    ):
        self.was_drawing = False
        self.release_frames = 0
        self.open_palm_frames = 0

        self.commit_release_frames = commit_release_frames
        self.open_palm_clear_frames = open_palm_clear_frames

    def update(self, hand):
        if hand is None:
            self.release_frames = 0
            self.open_palm_frames = 0

            if self.was_drawing:
                self.release_frames += 1

                if self.release_frames >= self.commit_release_frames:
                    self.was_drawing = False
                    self.release_frames = 0
                    return "COMMIT"

            return "NONE"

        if is_open_palm(hand):
            self.open_palm_frames += 1

            if self.open_palm_frames >= self.open_palm_clear_frames:
                self.was_drawing = False
                self.release_frames = 0
                self.open_palm_frames = 0
                return "CLEAR"

        else:
            self.open_palm_frames = 0

        if is_drawing_gesture(hand):
            self.was_drawing = True
            self.release_frames = 0
            return "DRAW"

        if self.was_drawing:
            self.release_frames += 1

            if self.release_frames >= self.commit_release_frames:
                self.was_drawing = False
                self.release_frames = 0
                return "COMMIT"

            return "DRAW"

        return "IDLE"