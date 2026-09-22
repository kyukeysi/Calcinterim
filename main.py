import time

import cv2

from camera import Camera
from config import (
    CAMERA_HEIGHT,
    CAMERA_INDEX,
    CAMERA_WIDTH,
    COMMIT_RELEASE_FRAMES,
    MODEL_PATH,
    OPEN_PALM_CLEAR_FRAMES,
    PARTICLE_COUNT,
    MIRROR_CAMERA,
    SHOW_FPS,
    TRAIL_CORE_SIZE,
    TRAIL_GLOW_SIZE,
    TRAIL_MIDDLE_SIZE,
    WINDOW_NAME,
)
from drawing.glow import GlowRenderer
from drawing.particles import ParticleSystem
from drawing.stroke_manager import StrokeManager
from game.game_state import GameState
from gestures import GestureController
from hand_tracker import HandTracker
from calculator.math_engine import MathEngine
from recognition.recognizer import StrokeRecognizer
from ui.hud import HUD
from ui.spell_ring import SpellRing


def get_fingertip_position(hand, frame_width, frame_height):
    if hand is None:
        return None

    fingertip = hand[8]

    x = int(fingertip.x * frame_width)
    y = int(fingertip.y * frame_height)

    x = max(0, min(frame_width - 1, x))
    y = max(0, min(frame_height - 1, y))

    return x, y


def draw_fingertip(frame, position, drawing):
    if position is None:
        return

    x, y = position

    if drawing:
        cv2.circle(
            frame,
            (x, y),
            12,
            (0, 100, 255),
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
            8,
            (100, 100, 100),
            2,
            cv2.LINE_AA
        )


def draw_fps(frame, fps):
    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (20, 175),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (180, 180, 180),
        1,
        cv2.LINE_AA
    )


def draw_answer(frame, answer):
    if answer is None:
        return

    height, width = frame.shape[:2]

    cv2.putText(
        frame,
        "ANSWER:",
        (width - 350, height - 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 220, 120),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        str(answer),
        (width - 350, height - 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (180, 240, 255),
        3,
        cv2.LINE_AA
    )


def main():
    camera = Camera(
        camera_index=CAMERA_INDEX,
        width=CAMERA_WIDTH,
        height=CAMERA_HEIGHT,
        mirror=MIRROR_CAMERA
    )

    hand_tracker = None

    try:
        camera.open()

        hand_tracker = HandTracker(
            model_path=MODEL_PATH,
            num_hands=1
        )

        gesture_controller = GestureController(
            commit_release_frames=COMMIT_RELEASE_FRAMES,
            open_palm_clear_frames=OPEN_PALM_CLEAR_FRAMES
        )

        stroke_manager = StrokeManager()

        particle_system = ParticleSystem(
            particle_count=PARTICLE_COUNT
        )

        glow_renderer = GlowRenderer(
            width=CAMERA_WIDTH,
            height=CAMERA_HEIGHT,
            glow_size=TRAIL_GLOW_SIZE,
            middle_size=TRAIL_MIDDLE_SIZE,
            core_size=TRAIL_CORE_SIZE
        )

        recognizer = StrokeRecognizer()
        math_engine = MathEngine()
        game_state = GameState()

        hud = HUD()
        spell_ring = SpellRing()

        answer = None

        previous_timestamp = 0
        previous_time = time.monotonic()
        fps = 0.0

        while True:
            current_time = time.monotonic()

            delta_time = current_time - previous_time
            previous_time = current_time

            if delta_time > 0:
                current_fps = 1.0 / delta_time
                fps = (
                    current_fps
                    if fps == 0.0
                    else fps * 0.9 + current_fps * 0.1
                )

            frame = camera.read()

            if frame is None:
                print("Could not read frame from webcam.")
                break

            frame_height, frame_width = frame.shape[:2]

            timestamp_ms = int(current_time * 1000)

            if timestamp_ms <= previous_timestamp:
                timestamp_ms = previous_timestamp + 1

            previous_timestamp = timestamp_ms

            hand = hand_tracker.process(
                frame,
                timestamp_ms
            )

            fingertip_position = get_fingertip_position(
                hand,
                frame_width,
                frame_height
            )

            action = gesture_controller.update(hand)

            if action == "DRAW":
                if fingertip_position is not None:
                    if stroke_manager.is_empty():
                        stroke_manager.begin(
                            fingertip_position
                        )
                    else:
                        points = stroke_manager.get_points()

                        if points:
                            previous_point = points[-1]

                            glow_renderer.draw_spell_line(
                                previous_point,
                                fingertip_position
                            )

                        stroke_manager.add_point(
                            fingertip_position
                        )

                    particle_system.spawn(
                        fingertip_position[0],
                        fingertip_position[1]
                    )

                    spell_ring.set_visible(True)

            elif action == "COMMIT":
                if not stroke_manager.is_empty():
                    stroke = stroke_manager.finish()

                    token = recognizer.recognize(
                        stroke
                    )

                    if token is not None:
                        math_engine.add_token(token)
                        game_state.add_token(token)

                        answer = None

                        print(
                            f"Stroke committed: "
                            f"{len(stroke)} points -> "
                            f"token '{token}'"
                        )

                    glow_renderer.clear()

                spell_ring.set_visible(False)

            elif action == "CLEAR":
                stroke_manager.clear()
                glow_renderer.clear()
                particle_system.clear()
                math_engine.clear()
                game_state.clear_tokens()

                answer = None

                print("Current expression cleared.")

                spell_ring.set_visible(False)

            elif action == "IDLE":
                spell_ring.set_visible(False)

            particle_system.update()
            spell_ring.update(delta_time)

            frame = glow_renderer.render(frame)

            particle_system.draw(frame)

            spell_ring.draw(
                frame,
                fingertip_position
            )

            draw_fingertip(
                frame,
                fingertip_position,
                action == "DRAW"
            )

            hud.draw(
                frame,
                target_expression="",
                player_expression=math_engine.get_display_expression(),
                time_remaining=0.0,
                score=game_state.score,
                status="CALCULATOR"
            )

            hud.draw_instructions(frame)

            draw_answer(
                frame,
                answer
            )

            cv2.putText(
                frame,
                "ENTER = CALCULATE",
                (30, frame_height - 105),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 220, 120),
                1,
                cv2.LINE_AA
            )

            if SHOW_FPS:
                draw_fps(frame, fps)

            cv2.imshow(
                WINDOW_NAME,
                frame
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            if key == ord("c"):
                stroke_manager.clear()
                glow_renderer.clear()
                particle_system.clear()
                math_engine.clear()
                game_state.clear_tokens()

                answer = None

                spell_ring.set_visible(False)

                print("Current expression cleared.")

            if key == 13:
                answer = math_engine.get_answer_text()

                if answer is None:
                    print(
                        "Could not calculate expression:"
                        f" {math_engine.get_display_expression()}"
                    )
                else:
                    print(
                        f"{math_engine.get_display_expression()}"
                        f" = {answer}"
                    )

    except RuntimeError as error:
        print(f"Runtime error: {error}")

    finally:
        if hand_tracker is not None:
            hand_tracker.close()

        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()