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


TRAINABLE_SYMBOLS = {
    ord("0"): "0",
    ord("1"): "1",
    ord("2"): "2",
    ord("3"): "3",
    ord("4"): "4",
    ord("5"): "5",
    ord("6"): "6",
    ord("7"): "7",
    ord("8"): "8",
    ord("9"): "9",
    ord("+"): "+",
    ord("-"): "-",
    ord("*"): "×",
    ord("/"): "÷",
    ord("x"): "x",
    ord("^"): "^",
}


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
        (20, 205),
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
        "ANSWER",
        (45, height - 165),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 220, 120),
        2,
        cv2.LINE_AA
    )

    answer_text = str(answer)

    cv2.putText(
        frame,
        answer_text,
        (45, height - 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.6,
        (180, 240, 255),
        3,
        cv2.LINE_AA
    )


def draw_training_ui(
    frame,
    selected_symbol,
    template_count
):
    height, width = frame.shape[:2]

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (15, 15),
        (width - 15, 170),
        (20, 20, 35),
        -1
    )

    frame[:] = cv2.addWeighted(
        overlay,
        0.85,
        frame,
        0.15,
        0
    )

    cv2.putText(
        frame,
        "TRAINING MODE",
        (35, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (180, 240, 255),
        2,
        cv2.LINE_AA
    )

    if selected_symbol is None:
        selected_text = "NONE"
    else:
        selected_text = selected_symbol

    cv2.putText(
        frame,
        f"TRAINING: {selected_text}",
        (35, 85),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (255, 220, 120),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        f"SAVED EXAMPLES: {template_count}",
        (35, 115),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (200, 200, 200),
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "0-9 = NUMBER   +/- = OPERATOR   * = MULTIPLY   / = DIVIDE",
        (35, height - 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        (200, 200, 200),
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "X = VARIABLE   ^ = POWER",
        (35, height - 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        (180, 240, 255),
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "DRAW = SAVE   BACKSPACE = DELETE LAST   D = DELETE ALL",
        (35, height - 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        (255, 220, 120),
        1,
        cv2.LINE_AA
    )


def draw_calculator_ui(
    frame,
    expression,
    answer,
    integral_mode,
    lower_bound,
    upper_bound,
    bound_mode
):
    height, width = frame.shape[:2]

    overlay = frame.copy()

    panel_height = 285 if integral_mode else 245

    cv2.rectangle(
        overlay,
        (15, 15),
        (width - 15, panel_height),
        (20, 20, 35),
        -1
    )

    frame[:] = cv2.addWeighted(
        overlay,
        0.85,
        frame,
        0.15,
        0
    )

    if integral_mode:
        title = "INTEGRAL MODE"
        title_color = (255, 210, 130)
    else:
        title = "CALCULATOR"
        title_color = (180, 240, 255)

    cv2.putText(
        frame,
        title,
        (35, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        title_color,
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "EXPRESSION",
        (35, 82),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        (180, 180, 180),
        1,
        cv2.LINE_AA
    )

    expression_text = (
        expression
        if expression
        else "DRAW A NUMBER OR OPERATOR"
    )

    if integral_mode:
        lower_text = (
            lower_bound
            if lower_bound
            else "?"
        )

        upper_text = (
            upper_bound
            if upper_bound
            else "?"
        )

        expression_text = (
            f"INT [{lower_text},{upper_text}] "
            f"{expression_text}"
        )

    expression_size = 1.05

    if len(expression_text) > 30:
        expression_size = 0.72
    elif len(expression_text) > 22:
        expression_size = 0.88
    elif len(expression_text) > 15:
        expression_size = 0.98

    cv2.putText(
        frame,
        expression_text,
        (35, 130),
        cv2.FONT_HERSHEY_SIMPLEX,
        expression_size,
        (255, 255, 255),
        3,
        cv2.LINE_AA
    )

    if integral_mode:
        bound_text = (
            "LOWER = A"
            if bound_mode == "lower"
            else "UPPER = B"
            if bound_mode == "upper"
            else "A = LOWER    B = UPPER"
        )

        cv2.putText(
            frame,
            bound_text,
            (35, 165),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 220, 120),
            1,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            "DRAW NUMBERS AFTER A/B TO SET THE BOUNDS",
            (35, 195),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (200, 200, 200),
            1,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            "ENTER = INTEGRATE    C = CLEAR    I = EXIT INTEGRAL",
            (35, 225),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (255, 220, 120),
            1,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            "BACKSPACE = DELETE LAST",
            (35, 250),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (200, 200, 200),
            1,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            "ANSWER",
            (35, 278),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            (255, 220, 120),
            1,
            cv2.LINE_AA
        )

        if answer is None:
            answer_text = "—"
        else:
            answer_text = str(answer)

        answer_size = 1.2

        if len(answer_text) > 18:
            answer_size = 0.9
        elif len(answer_text) > 12:
            answer_size = 1.05

        cv2.putText(
            frame,
            answer_text,
            (190, 278),
            cv2.FONT_HERSHEY_SIMPLEX,
            answer_size,
            (180, 240, 255),
            2,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            "T = TRAINING MODE",
            (35, height - 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            "Q = QUIT",
            (35, height - 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 220, 120),
            1,
            cv2.LINE_AA
        )

        return

    cv2.putText(
        frame,
        "ANSWER",
        (35, 165),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        (255, 220, 120),
        1,
        cv2.LINE_AA
    )

    if answer is None:
        answer_text = "—"
    else:
        answer_text = str(answer)

    answer_size = 1.35

    if len(answer_text) > 18:
        answer_size = 0.9
    elif len(answer_text) > 12:
        answer_size = 1.1

    cv2.putText(
        frame,
        answer_text,
        (35, 215),
        cv2.FONT_HERSHEY_SIMPLEX,
        answer_size,
        (180, 240, 255),
        3,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "T = TRAINING MODE    I = INTEGRAL MODE",
        (35, height - 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (200, 200, 200),
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "BACKSPACE = DELETE LAST    ENTER = CALCULATE    C = CLEAR    Q = QUIT",
        (35, height - 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 220, 120),
        1,
        cv2.LINE_AA
    )


def parse_bound(bound_text):
    if not bound_text:
        return None

    try:
        return int(bound_text)
    except ValueError:
        pass

    try:
        return float(bound_text)
    except ValueError:
        return None


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

        training_mode = False
        selected_training_symbol = None

        integral_mode = False
        integral_bound_mode = None
        lower_bound_tokens = []
        upper_bound_tokens = []

        previous_timestamp = 0
        previous_time = time.monotonic()
        fps = 0.0

        while True:
            current_time = time.monotonic()

            delta_time = (
                current_time
                - previous_time
            )

            previous_time = current_time

            if delta_time > 0:
                current_fps = 1.0 / delta_time

                fps = (
                    current_fps
                    if fps == 0.0
                    else fps * 0.9
                    + current_fps * 0.1
                )

            frame = camera.read()

            if frame is None:
                print(
                    "Could not read frame from webcam."
                )
                break

            frame_height, frame_width = frame.shape[:2]

            timestamp_ms = int(
                current_time * 1000
            )

            if timestamp_ms <= previous_timestamp:
                timestamp_ms = (
                    previous_timestamp + 1
                )

            previous_timestamp = timestamp_ms

            hand = hand_tracker.process(
                frame,
                timestamp_ms
            )

            fingertip_position = (
                get_fingertip_position(
                    hand,
                    frame_width,
                    frame_height
                )
            )

            action = gesture_controller.update(
                hand
            )

            if action == "DRAW":
                if fingertip_position is not None:
                    if stroke_manager.is_empty():
                        stroke_manager.begin(
                            fingertip_position
                        )
                    else:
                        points = (
                            stroke_manager.get_points()
                        )

                        if points:
                            previous_point = (
                                points[-1]
                            )

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

                    spell_ring.set_visible(
                        True
                    )

            elif action == "COMMIT":
                if not stroke_manager.is_empty():
                    stroke = (
                        stroke_manager.finish()
                    )

                    if training_mode:
                        if selected_training_symbol is not None:
                            saved = (
                                recognizer.add_template(
                                    selected_training_symbol,
                                    stroke
                                )
                            )

                            if saved:
                                count = (
                                    recognizer
                                    .get_user_template_count(
                                        selected_training_symbol
                                    )
                                )

                                print(
                                    "Training saved: "
                                    f"'{selected_training_symbol}' "
                                    f"example #{count}"
                                )
                            else:
                                print(
                                    "Training stroke "
                                    "was too short."
                                )

                        else:
                            print(
                                "Select a symbol "
                                "before drawing."
                            )

                    else:
                        token = (
                            recognizer.recognize(
                                stroke
                            )
                        )

                        if token is not None:
                            if (
                                integral_mode
                                and integral_bound_mode == "lower"
                            ):
                                lower_bound_tokens.append(
                                    token
                                )

                                print(
                                    "Lower bound token: "
                                    f"'{token}'"
                                )

                            elif (
                                integral_mode
                                and integral_bound_mode == "upper"
                            ):
                                upper_bound_tokens.append(
                                    token
                                )

                                print(
                                    "Upper bound token: "
                                    f"'{token}'"
                                )

                            else:
                                math_engine.add_token(
                                    token
                                )

                                game_state.add_token(
                                    token
                                )

                                answer = None

                                print(
                                    "Stroke committed: "
                                    f"{len(stroke)} points "
                                    f"-> token '{token}'"
                                )

                        else:
                            print(
                                "Stroke could not "
                                "be recognized."
                            )

                    glow_renderer.clear()

                spell_ring.set_visible(
                    False
                )

            elif action == "CLEAR":
                stroke_manager.clear()
                glow_renderer.clear()
                particle_system.clear()

                if not training_mode:
                    math_engine.clear()
                    game_state.clear_tokens()

                    lower_bound_tokens.clear()
                    upper_bound_tokens.clear()
                    integral_bound_mode = None

                    answer = None

                spell_ring.set_visible(
                    False
                )

                print(
                    "Current stroke cleared."
                )

            elif action == "IDLE":
                spell_ring.set_visible(
                    False
                )

            particle_system.update()

            spell_ring.update(
                delta_time
            )

            frame = glow_renderer.render(
                frame
            )

            particle_system.draw(
                frame
            )

            spell_ring.draw(
                frame,
                fingertip_position
            )

            draw_fingertip(
                frame,
                fingertip_position,
                action == "DRAW"
            )

            if training_mode:
                draw_training_ui(
                    frame,
                    selected_training_symbol,
                    (
                        recognizer
                        .get_user_template_count(
                            selected_training_symbol
                        )
                        if selected_training_symbol
                        else 0
                    )
                )

            else:
                lower_bound_text = "".join(
                    lower_bound_tokens
                )

                upper_bound_text = "".join(
                    upper_bound_tokens
                )

                draw_calculator_ui(
                    frame,
                    math_engine.get_display_expression(),
                    answer,
                    integral_mode,
                    lower_bound_text,
                    upper_bound_text,
                    integral_bound_mode
                )

            if SHOW_FPS:
                draw_fps(
                    frame,
                    fps
                )

            cv2.imshow(
                WINDOW_NAME,
                frame
            )

            key = (
                cv2.waitKey(1)
                & 0xFF
            )

            if key == ord("q"):
                break

            if key == 27:
                if training_mode:
                    training_mode = False
                    selected_training_symbol = None

                    stroke_manager.clear()
                    glow_renderer.clear()
                    particle_system.clear()

                    print(
                        "Exited training mode."
                    )

                elif integral_mode:
                    integral_mode = False
                    integral_bound_mode = None

                    lower_bound_tokens.clear()
                    upper_bound_tokens.clear()

                    answer = None

                    stroke_manager.clear()
                    glow_renderer.clear()
                    particle_system.clear()

                    print(
                        "Exited integral mode."
                    )

                else:
                    break

            if key == ord("t"):
                training_mode = not training_mode
                selected_training_symbol = None

                integral_mode = False
                integral_bound_mode = None

                lower_bound_tokens.clear()
                upper_bound_tokens.clear()

                stroke_manager.clear()
                glow_renderer.clear()
                particle_system.clear()

                if training_mode:
                    print(
                        "Entered training mode."
                    )
                    print(
                        "Press a symbol key "
                        "before drawing it."
                    )
                else:
                    print(
                        "Exited training mode."
                    )

            if training_mode:
                if key in TRAINABLE_SYMBOLS:
                    selected_training_symbol = (
                        TRAINABLE_SYMBOLS[key]
                    )

                    count = (
                        recognizer
                        .get_user_template_count(
                            selected_training_symbol
                        )
                    )

                    print(
                        "Selected training symbol: "
                        f"'{selected_training_symbol}' "
                        f"({count} saved examples)"
                    )

                elif key == 8:
                    if selected_training_symbol is None:
                        print(
                            "Select a symbol before "
                            "deleting a training example."
                        )
                    else:
                        deleted = (
                            recognizer.delete_last_template(
                                selected_training_symbol
                            )
                        )

                        if deleted:
                            count = (
                                recognizer
                                .get_user_template_count(
                                    selected_training_symbol
                                )
                            )

                            print(
                                "Deleted last training "
                                f"example for "
                                f"'{selected_training_symbol}'. "
                                f"{count} remaining."
                            )
                        else:
                            print(
                                "No saved training examples "
                                f"for '{selected_training_symbol}'."
                            )

                elif key == ord("d"):
                    if selected_training_symbol is None:
                        print(
                            "Select a symbol before "
                            "deleting training examples."
                        )
                    else:
                        count = (
                            recognizer
                            .get_user_template_count(
                                selected_training_symbol
                            )
                        )

                        if count > 0:
                            recognizer.clear_user_templates(
                                selected_training_symbol
                            )

                            print(
                                "Deleted all "
                                f"{count} training examples "
                                f"for '{selected_training_symbol}'."
                            )
                        else:
                            print(
                                "No saved training examples "
                                f"for '{selected_training_symbol}'."
                            )

                continue

            if key == ord("i"):
                integral_mode = not integral_mode
                integral_bound_mode = None

                lower_bound_tokens.clear()
                upper_bound_tokens.clear()

                answer = None

                stroke_manager.clear()
                glow_renderer.clear()
                particle_system.clear()

                if integral_mode:
                    print(
                        "Entered integral mode."
                    )
                    print(
                        "Draw the integrand normally."
                    )
                    print(
                        "Press A for lower bound."
                    )
                    print(
                        "Press B for upper bound."
                    )
                    print(
                        "Press ENTER to integrate."
                    )
                else:
                    print(
                        "Exited integral mode."
                    )

            if integral_mode:
                if key == ord("a"):
                    integral_bound_mode = "lower"
                    print(
                        "Lower bound selected."
                    )

                elif key == ord("b"):
                    integral_bound_mode = "upper"
                    print(
                        "Upper bound selected."
                    )

                elif key == 8:
                    if integral_bound_mode == "lower":
                        if lower_bound_tokens:
                            removed = (
                                lower_bound_tokens.pop()
                            )

                            print(
                                "Deleted lower bound token: "
                                f"'{removed}'"
                            )
                        else:
                            print(
                                "Lower bound is empty."
                            )

                    elif integral_bound_mode == "upper":
                        if upper_bound_tokens:
                            removed = (
                                upper_bound_tokens.pop()
                            )

                            print(
                                "Deleted upper bound token: "
                                f"'{removed}'"
                            )
                        else:
                            print(
                                "Upper bound is empty."
                            )

                    else:
                        removed_token = (
                            math_engine.remove_last_token()
                        )

                        if removed_token is not None:
                            game_state.remove_last_token()
                            answer = None

                            print(
                                "Deleted last token: "
                                f"'{removed_token}'"
                            )
                        else:
                            print(
                                "No tokens to delete."
                            )

                elif key == ord("c"):
                    stroke_manager.clear()
                    glow_renderer.clear()
                    particle_system.clear()

                    math_engine.clear()
                    game_state.clear_tokens()

                    lower_bound_tokens.clear()
                    upper_bound_tokens.clear()

                    integral_bound_mode = None
                    answer = None

                    spell_ring.set_visible(
                        False
                    )

                    print(
                        "Integral expression cleared."
                    )

                elif key == 13:
                    lower_bound_text = "".join(
                        lower_bound_tokens
                    )

                    upper_bound_text = "".join(
                        upper_bound_tokens
                    )

                    if (
                        lower_bound_text
                        and upper_bound_text
                    ):
                        lower_value = parse_bound(
                            lower_bound_text
                        )

                        upper_value = parse_bound(
                            upper_bound_text
                        )

                        if (
                            lower_value is None
                            or upper_value is None
                        ):
                            answer = None

                            print(
                                "Bounds must be numbers."
                            )

                        else:
                            answer = (
                                math_engine
                                .get_definite_integral_text(
                                    lower_value,
                                    upper_value
                                )
                            )

                            if answer is None:
                                print(
                                    "Could not calculate "
                                    "definite integral:"
                                    f" {math_engine.get_display_expression()}"
                                )
                            else:
                                print(
                                    f"Integral from "
                                    f"{lower_value} to "
                                    f"{upper_value} of "
                                    f"{math_engine.get_display_expression()}"
                                    f" = {answer}"
                                )

                    else:
                        answer = (
                            math_engine
                            .get_integral_text()
                        )

                        if answer is None:
                            print(
                                "Could not calculate "
                                "integral:"
                                f" {math_engine.get_display_expression()}"
                            )
                        else:
                            print(
                                f"Integral of "
                                f"{math_engine.get_display_expression()}"
                                f" = {answer}"
                            )

                continue

            if key == 8:
                removed_token = (
                    math_engine.remove_last_token()
                )

                if removed_token is not None:
                    game_state.remove_last_token()
                    answer = None

                    print(
                        "Deleted last token: "
                        f"'{removed_token}'"
                    )
                else:
                    print(
                        "No tokens to delete."
                    )

            if key == ord("c"):
                stroke_manager.clear()
                glow_renderer.clear()
                particle_system.clear()
                math_engine.clear()
                game_state.clear_tokens()

                answer = None

                spell_ring.set_visible(
                    False
                )

                print(
                    "Current expression cleared."
                )

            if key == 13:
                answer = (
                    math_engine
                    .get_answer_text()
                )

                if answer is None:
                    print(
                        "Could not calculate "
                        "expression:"
                        f" {math_engine.get_display_expression()}"
                    )
                else:
                    print(
                        f"{math_engine.get_display_expression()}"
                        f" = {answer}"
                    )

    except RuntimeError as error:
        print(
            f"Runtime error: {error}"
        )

    finally:
        if hand_tracker is not None:
            hand_tracker.close()

        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()