import cv2
import mediapipe as mp
import numpy as np
import math
import random
import time


# ============================================================
# CONFIGURATION
# ============================================================

WINDOW_NAME = "Calcinterim - Air Drawing Prototype"

CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

MODEL_PATH = "hand_landmarker.task"

TRAIL_GLOW_SIZE = 14
TRAIL_MIDDLE_SIZE = 6
TRAIL_CORE_SIZE = 2

PARTICLE_COUNT = 3


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def distance(a, b):
    """Calculate the distance between two MediaPipe landmarks."""
    return math.hypot(a.x - b.x, a.y - b.y)


def index_is_up(hand):
    """Check if the index finger is pointing upward."""
    return hand[8].y < hand[6].y


def thumb_is_out(hand):
    """Check if the thumb is extended outward."""
    wrist = hand[0]
    thumb_tip = hand[4]
    index_mcp = hand[5]

    hand_size = distance(wrist, hand[9])
    thumb_distance = distance(thumb_tip, index_mcp)

    if hand_size == 0:
        return False

    return thumb_distance > hand_size * 0.45


def is_drawing_gesture(hand):
    """Detect the L/gun drawing gesture."""
    return index_is_up(hand) and thumb_is_out(hand)


def thumb_is_raised(hand):
    """Check if the thumb is currently raised."""
    return hand[4].y < hand[3].y


def is_open_palm(hand):
    """Detect an open palm."""
    fingers = [
        (8, 6),    # Index
        (12, 10),  # Middle
        (16, 14),  # Ring
        (20, 18)   # Pinky
    ]

    extended = 0

    for tip, pip in fingers:
        if hand[tip].y < hand[pip].y:
            extended += 1

    return extended >= 4


# ============================================================
# GESTURE CONTROLLER
# ============================================================

class GestureController:

    def __init__(self):
        self.was_drawing = False
        self.release_frames = 0

        self.commit_threshold = 3

        self.open_palm_frames = 0
        self.open_palm_threshold = 5

    def update(self, hand):
        """
        Return one of:

        DRAW
        COMMIT
        CLEAR
        IDLE
        NONE
        """

        if hand is None:
            self.was_drawing = False
            self.release_frames = 0
            self.open_palm_frames = 0
            return "NONE"

        # ----------------------------------------------------
        # Open palm detection
        # ----------------------------------------------------

        if is_open_palm(hand):
            self.open_palm_frames += 1

            if self.open_palm_frames >= self.open_palm_threshold:
                self.open_palm_frames = 0
                self.was_drawing = False
                self.release_frames = 0
                return "CLEAR"
        else:
            self.open_palm_frames = 0

        # ----------------------------------------------------
        # Drawing gesture
        # ----------------------------------------------------

        drawing = is_drawing_gesture(hand)

        if drawing:
            self.was_drawing = True
            self.release_frames = 0
            return "DRAW"

        # ----------------------------------------------------
        # Thumb release / stroke commit
        # ----------------------------------------------------

        if self.was_drawing:
            self.release_frames += 1

            if self.release_frames >= self.commit_threshold:
                self.was_drawing = False
                self.release_frames = 0
                return "COMMIT"

        return "IDLE"


# ============================================================
# STROKE MANAGER
# ============================================================

class StrokeManager:

    def __init__(self):
        self.points = []

    def begin(self):
        self.points = []

    def add_point(self, x, y):
        self.points.append((x, y))

    def is_empty(self):
        return len(self.points) == 0

    def finish(self):
        stroke = self.points.copy()
        self.points.clear()
        return stroke

    def clear(self):
        self.points.clear()


# ============================================================
# PARTICLE SYSTEM
# ============================================================

class Particle:

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

        self.vx = random.uniform(-2.5, 2.5)
        self.vy = random.uniform(-3.0, 1.0)

        self.life = random.randint(10, 25)
        self.max_life = self.life

        self.radius = random.randint(1, 3)

    def update(self):
        self.x += self.vx
        self.y += self.vy

        self.vy += 0.05

        self.life -= 1

    def is_alive(self):
        return self.life > 0


class ParticleSystem:

    def __init__(self):
        self.particles = []

    def spawn(self, x, y, amount=PARTICLE_COUNT):
        for _ in range(amount):
            self.particles.append(Particle(x, y))

    def update(self):
        for particle in self.particles:
            particle.update()

        self.particles = [
            particle
            for particle in self.particles
            if particle.is_alive()
        ]

    def draw(self, frame):
        for particle in self.particles:

            life_ratio = particle.life / particle.max_life

            radius = max(
                1,
                int(particle.radius * life_ratio)
            )

            x = int(particle.x)
            y = int(particle.y)

            if (
                0 <= x < frame.shape[1]
                and 0 <= y < frame.shape[0]
            ):
                cv2.circle(
                    frame,
                    (x, y),
                    radius,
                    (0, 180, 255),
                    -1,
                    cv2.LINE_AA
                )


# ============================================================
# GLOW / SPELL TRAIL RENDERER
# ============================================================

class GlowRenderer:

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.trail = np.zeros(
            (height, width, 3),
            dtype=np.uint8
        )

    def clear(self):
        self.trail[:] = 0

    def draw_spell_line(self, p1, p2):
        """
        Draw multiple layers to create a magical energy trail.
        """

        # Wide orange glow
        cv2.line(
            self.trail,
            p1,
            p2,
            (0, 80, 255),
            TRAIL_GLOW_SIZE,
            cv2.LINE_AA
        )

        # Bright orange middle
        cv2.line(
            self.trail,
            p1,
            p2,
            (0, 160, 255),
            TRAIL_MIDDLE_SIZE,
            cv2.LINE_AA
        )

        # Bright core
        cv2.line(
            self.trail,
            p1,
            p2,
            (180, 240, 255),
            TRAIL_CORE_SIZE,
            cv2.LINE_AA
        )

    def render(self, frame):
        """
        Composite the magical trail onto the camera frame.
        """

        glow = cv2.GaussianBlur(
            self.trail,
            (0, 0),
            12
        )

        result = cv2.addWeighted(
            frame,
            1.0,
            glow,
            1.8,
            0
        )

        result = cv2.addWeighted(
            result,
            1.0,
            self.trail,
            1.0,
            0
        )

        return result


# ============================================================
# TEMPORARY RECOGNIZER
# ============================================================

class StrokeRecognizer:

    def recognize(self, stroke):
        """
        Temporary recognizer for Milestone 1.

        Real handwriting recognition will be implemented
        in a later milestone.
        """

        if not stroke:
            return None

        # Temporary placeholder token.
        return "3"


# ============================================================
# MEDIAPIPE HAND TRACKER
# ============================================================

class HandTracker:

    def __init__(self, model_path):

        self.base_options = mp.tasks.BaseOptions(
            model_asset_path=model_path
        )

        self.options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=self.base_options,
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.landmarker = (
            mp.tasks.vision.HandLandmarker
            .create_from_options(self.options)
        )

    def process(self, frame, timestamp_ms):

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        result = self.landmarker.detect_for_video(
            mp_image,
            timestamp_ms
        )

        if not result.hand_landmarks:
            return None

        return result.hand_landmarks[0]

    def close(self):
        self.landmarker.close()


# ============================================================
# UI
# ============================================================

def draw_status(frame, gesture, stroke_points):
    """Draw basic debugging information."""

    cv2.putText(
        frame,
        "CALCINTERIM",
        (30, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (180, 220, 255),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        f"Gesture: {gesture}",
        (30, 85),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        f"Stroke points: {stroke_points}",
        (30, 115),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "L/Gun gesture = DRAW",
        (30, frame.shape[0] - 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (220, 220, 220),
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "Lower thumb = COMMIT | Open palm = CLEAR | Q = QUIT",
        (30, frame.shape[0] - 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (220, 220, 220),
        1,
        cv2.LINE_AA
    )


def draw_fingertip(frame, x, y, drawing):
    """Draw a cursor around the index fingertip."""

    if drawing:
        cv2.circle(
            frame,
            (x, y),
            12,
            (0, 180, 255),
            2,
            cv2.LINE_AA
        )

        cv2.circle(
            frame,
            (x, y),
            4,
            (180, 240, 255),
            -1,
            cv2.LINE_AA
        )

    else:
        cv2.circle(
            frame,
            (x, y),
            7,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("Starting Calcinterim...")
    print("Press Q to quit.")

    # --------------------------------------------------------
    # Webcam
    # --------------------------------------------------------

    camera = cv2.VideoCapture(0)

    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        CAMERA_WIDTH
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        CAMERA_HEIGHT
    )

    if not camera.isOpened():
        print("ERROR: Could not open webcam.")
        return

    # --------------------------------------------------------
    # Systems
    # --------------------------------------------------------

    try:
        hand_tracker = HandTracker(MODEL_PATH)
    except Exception as error:
        print("ERROR: Could not initialize MediaPipe.")
        print(error)

        camera.release()
        return

    gesture_controller = GestureController()

    stroke_manager = StrokeManager()

    particle_system = ParticleSystem()

    recognizer = StrokeRecognizer()

    glow_renderer = GlowRenderer(
        CAMERA_WIDTH,
        CAMERA_HEIGHT
    )

    # --------------------------------------------------------
    # Timing
    # --------------------------------------------------------

    start_time = time.monotonic()

    last_timestamp_ms = -1

    # --------------------------------------------------------
    # Main loop
    # --------------------------------------------------------

    while True:

        success, frame = camera.read()

        if not success:
            print("ERROR: Could not read webcam frame.")
            break

        # Mirror the webcam for natural movement.
        frame = cv2.flip(frame, 1)

        height, width = frame.shape[:2]

        # Timestamp for MediaPipe VIDEO mode.
        timestamp_ms = int(
            (time.monotonic() - start_time) * 1000
        )

        if timestamp_ms <= last_timestamp_ms:
            timestamp_ms = last_timestamp_ms + 1

        last_timestamp_ms = timestamp_ms

        # ----------------------------------------------------
        # Hand tracking
        # ----------------------------------------------------

        try:
            hand = hand_tracker.process(
                frame,
                timestamp_ms
            )
        except Exception as error:
            print("MediaPipe processing error:")
            print(error)
            break

        # ----------------------------------------------------
        # Gesture processing
        # ----------------------------------------------------

        gesture = gesture_controller.update(hand)

        # ----------------------------------------------------
        # Hand / fingertip
        # ----------------------------------------------------

        fingertip_x = None
        fingertip_y = None

        if hand is not None:

            fingertip = hand[8]

            fingertip_x = int(
                fingertip.x * width
            )

            fingertip_y = int(
                fingertip.y * height
            )

            fingertip_x = max(
                0,
                min(width - 1, fingertip_x)
            )

            fingertip_y = max(
                0,
                min(height - 1, fingertip_y)
            )

        # ----------------------------------------------------
        # Drawing
        # ----------------------------------------------------

        if (
            gesture == "DRAW"
            and fingertip_x is not None
            and fingertip_y is not None
        ):

            if stroke_manager.is_empty():
                stroke_manager.begin()

            previous_point = None

            if len(stroke_manager.points) > 0:
                previous_point = (
                    stroke_manager.points[-1]
                )

            current_point = (
                fingertip_x,
                fingertip_y
            )

            stroke_manager.add_point(
                fingertip_x,
                fingertip_y
            )

            if previous_point is not None:

                glow_renderer.draw_spell_line(
                    previous_point,
                    current_point
                )

            particle_system.spawn(
                fingertip_x,
                fingertip_y
            )

        # ----------------------------------------------------
        # Commit
        # ----------------------------------------------------

        elif gesture == "COMMIT":

            if not stroke_manager.is_empty():

                completed_stroke = (
                    stroke_manager.finish()
                )

                token = recognizer.recognize(
                    completed_stroke
                )

                print(
                    f"Stroke committed: "
                    f"{len(completed_stroke)} points "
                    f"-> token '{token}'"
                )

        # ----------------------------------------------------
        # Clear
        # ----------------------------------------------------

        elif gesture == "CLEAR":

            stroke_manager.clear()

            glow_renderer.clear()

            print("Current stroke cleared.")

        # ----------------------------------------------------
        # Particle update
        # ----------------------------------------------------

        particle_system.update()

        # ----------------------------------------------------
        # Render glow
        # ----------------------------------------------------

        frame = glow_renderer.render(frame)

        # ----------------------------------------------------
        # Render particles
        # ----------------------------------------------------

        particle_system.draw(frame)

        # ----------------------------------------------------
        # Fingertip cursor
        # ----------------------------------------------------

        if (
            fingertip_x is not None
            and fingertip_y is not None
        ):

            draw_fingertip(
                frame,
                fingertip_x,
                fingertip_y,
                gesture == "DRAW"
            )

        # ----------------------------------------------------
        # UI
        # ----------------------------------------------------

        draw_status(
            frame,
            gesture,
            len(stroke_manager.points)
        )

        # ----------------------------------------------------
        # Display
        # ----------------------------------------------------

        cv2.imshow(
            WINDOW_NAME,
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    # ========================================================
    # CLEANUP
    # ========================================================

    print("Closing Calcinterim...")

    hand_tracker.close()

    camera.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()