import os
import time

import cv2
import numpy as np
try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    _PYGAME_AVAILABLE = False
from PIL import Image, ImageDraw, ImageFont

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
from game.challenge_pool import get_random_problem
from game.game_state import GameState
from game.timer import GameTimer
from gestures import GestureController, CircleGestureDetector
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
    ord("("): "(",
    ord(")"): ")",
}


def get_fingertip_position(
    hand,
    frame_width,
    frame_height
):
    if hand is None:
        return None

    fingertip = hand[8]

    x = int(
        fingertip.x * frame_width
    )

    y = int(
        fingertip.y * frame_height
    )

    x = max(
        0,
        min(frame_width - 1, x)
    )

    y = max(
        0,
        min(frame_height - 1, y)
    )

    return x, y


def draw_fingertip(
    frame,
    position,
    drawing
):
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


def draw_fps(
    frame,
    fps
):
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


def find_unicode_font():
    candidates = [
        "C:/Windows/Fonts/seguisym.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/cambria.ttc",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]

    for path in candidates:
        if os.path.exists(path):
            return path

    return None


UNICODE_FONT_PATH = find_unicode_font()


def draw_unicode_text(
    frame,
    text,
    position,
    font_size,
    color,
    stroke_width=0
):
    if UNICODE_FONT_PATH is None:
        return False

    try:
        image = Image.fromarray(
            cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )
        )

        draw = ImageDraw.Draw(image)

        font = ImageFont.truetype(
            UNICODE_FONT_PATH,
            font_size
        )

        rgb_color = (
            color[2],
            color[1],
            color[0]
        )

        draw.text(
            position,
            text,
            font=font,
            fill=rgb_color,
            stroke_width=stroke_width,
            stroke_fill=rgb_color
        )

        frame[:] = cv2.cvtColor(
            np.array(image),
            cv2.COLOR_RGB2BGR
        )

        return True

    except Exception:
        return False


def format_math_expression(
    value
):
    if value is None:
        return ""

    text = str(value)

    text = text.replace(
        "**2",
        "²"
    )

    text = text.replace(
        "**3",
        "³"
    )

    text = text.replace(
        "**4",
        "⁴"
    )

    text = text.replace(
        "**5",
        "⁵"
    )

    text = text.replace(
        "**6",
        "⁶"
    )

    text = text.replace(
        "**7",
        "⁷"
    )

    text = text.replace(
        "**8",
        "⁸"
    )

    text = text.replace(
        "**9",
        "⁹"
    )

    text = text.replace(
        "*",
        ""
    )

    return text


def draw_integral_expression(
    frame,
    expression,
    lower_bound,
    upper_bound
):
    """
    Draws a visual definite-integral expression.

    Example:

        3
        ∫ 8x dx
        1
    """

    if not expression:
        expression = "DRAW FUNCTION"

    x = 35
    y = 91

    symbol_drawn = draw_unicode_text(
        frame,
        "∫",
        (x, y - 18),
        58,
        (255, 255, 255)
    )

    if not symbol_drawn:
        cv2.putText(
            frame,
            "S",
            (x + 8, y + 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

    if lower_bound:
        cv2.putText(
            frame,
            str(lower_bound),
            (x + 8, y + 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (255, 220, 120),
            1,
            cv2.LINE_AA
        )

    if upper_bound:
        cv2.putText(
            frame,
            str(upper_bound),
            (x + 8, y - 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (255, 220, 120),
            1,
            cv2.LINE_AA
        )

    cv2.putText(
        frame,
        expression,
        (x + 65, y + 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.05,
        (255, 255, 255),
        3,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "dx",
        (x + 65, y + 62),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (200, 200, 200),
        1,
        cv2.LINE_AA
    )


def draw_answer(
    frame,
    answer
):
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

    answer_text = format_math_expression(
        answer
    )

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


def draw_integral_steps(
    frame,
    steps,
    answer
):
    height, width = frame.shape[:2]

    if steps is None:
        return

    overlay = frame.copy()

    panel_top = 245
    panel_bottom = height - 105

    cv2.rectangle(
        overlay,
        (15, panel_top),
        (width - 15, panel_bottom),
        (15, 15, 30),
        -1
    )

    frame[:] = cv2.addWeighted(
        overlay,
        0.88,
        frame,
        0.12,
        0
    )

    cv2.putText(
        frame,
        "CALCULUS STEPS",
        (35, panel_top + 32),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.58,
        (255, 220, 120),
        1,
        cv2.LINE_AA
    )

    integrand = format_math_expression(
        steps["integrand"]
    )

    antiderivative = format_math_expression(
        steps["antiderivative"]
    )

    lower_bound = steps["lower_bound"]
    upper_bound = steps["upper_bound"]

    lower_result = format_math_expression(
        steps["lower_result"]
    )

    upper_result = format_math_expression(
        steps["upper_result"]
    )

    result = format_math_expression(
        steps["result"]
    )

    cv2.putText(
        frame,
        f"f(x) = {integrand}",
        (35, panel_top + 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.58,
        (220, 220, 220),
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "ANTIDERIVATIVE",
        (35, panel_top + 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        (180, 180, 180),
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        f"F(x) = {antiderivative} + C",
        (35, panel_top + 128),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.62,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "DEFINITE INTEGRAL",
        (35, panel_top + 163),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        (180, 180, 180),
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        f"F({upper_bound}) - F({lower_bound})",
        (35, panel_top + 193),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.68,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        f"{upper_result} - {lower_result}",
        (35, panel_top + 225),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.62,
        (220, 220, 220),
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        f"= {result}",
        (35, panel_top + 258),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.82,
        (180, 240, 255),
        2,
        cv2.LINE_AA
    )

    if answer is not None:
        cv2.putText(
            frame,
            "FINAL ANSWER",
            (width - 250, panel_top + 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (255, 220, 120),
            1,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            format_math_expression(answer),
            (width - 250, panel_top + 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (180, 240, 255),
            3,
            cv2.LINE_AA
        )


def draw_difficulty_select_ui(frame):
    """
    Renders an interactive difficulty selection screen for Challenge Mode.
    """
    height, width = frame.shape[:2]

    # Semi-transparent dark card
    overlay = frame.copy()
    box_w = 700
    box_h = 360
    x1 = (width - box_w) // 2
    y1 = (height - box_h) // 2
    x2 = x1 + box_w
    y2 = y1 + box_h

    cv2.rectangle(overlay, (x1, y1), (x2, y2), (18, 20, 26), -1)
    cv2.addWeighted(overlay, 0.88, frame, 0.12, 0, frame)

    # Glowing Cyan / Gold border
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 215, 255), 2, cv2.LINE_AA)

    def center_text(text, y_pos, scale=0.8, color=(255, 255, 255), thickness=2):
        size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)[0]
        x = (width - size[0]) // 2
        cv2.putText(frame, text, (x, y_pos), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
        cv2.putText(frame, text, (x, y_pos), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)

    center_text("CHALLENGE MODE", y1 + 50, scale=1.1, color=(0, 215, 255), thickness=3)
    center_text("SELECT DIFFICULTY", y1 + 88, scale=0.7, color=(200, 240, 255), thickness=2)

    # Option 1: EASY
    center_text("[ 1 ]  EASY  -  Basic Algebra & Arithmetic", y1 + 145, scale=0.82, color=(100, 255, 130), thickness=2)
    center_text("Addition, subtraction, multiplication, exponents & parentheses", y1 + 172, scale=0.52, color=(180, 230, 190), thickness=1)

    # Option 2: HARD
    center_text("[ 2 ]  HARD  -  Calculus & Definite Integrals", y1 + 225, scale=0.82, color=(100, 140, 255), thickness=2)
    center_text("Integrals with lower & upper bounds", y1 + 252, scale=0.52, color=(190, 190, 240), thickness=1)

    # Instructions
    center_text("Press [1] or [2] on keyboard  (or draw 1 or 2)", y1 + 305, scale=0.62, color=(255, 255, 255), thickness=2)
    center_text("Press [G] for Easy  |  Press [ESC] to Cancel", y1 + 333, scale=0.52, color=(160, 160, 160), thickness=1)


def draw_challenge_ui(
    frame,
    problem,
    time_remaining,
    challenge_score,
    numbers_entered,
    answer=None,
    result_text=None,
    wrong_answer=False,
    difficulty="easy"
):
    """
    Draws the minimal integral challenge UI overlay directly onto the frame.
    Displays:
      1. Given (the challenge problem + difficulty badge)
      2. Score
      3. Timer
      4. Numbers entered
    No background color or rectangle is rendered behind the text.
    """
    height, width = frame.shape[:2]

    def put_clean_text(text, pos, scale=0.75, color=(255, 255, 255), thickness=2):
        cv2.putText(
            frame,
            text,
            pos,
            cv2.FONT_HERSHEY_SIMPLEX,
            scale,
            (0, 0, 0),
            thickness + 2,
            cv2.LINE_AA
        )
        cv2.putText(
            frame,
            text,
            pos,
            cv2.FONT_HERSHEY_SIMPLEX,
            scale,
            color,
            thickness,
            cv2.LINE_AA
        )

    # 1. GIVEN + DIFFICULTY BADGE
    problem_display = problem["display"] if problem else "-"
    diff_tag = " [EASY]" if difficulty == "easy" else " [HARD]"
    diff_color = (120, 255, 120) if difficulty == "easy" else (100, 150, 255)
    given_text = f"GIVEN{diff_tag}: {problem_display}"
    put_clean_text(
        given_text,
        (30, 45),
        scale=0.75,
        color=diff_color,
        thickness=2
    )

    # 2. SCORE
    score_text = f"SCORE: {challenge_score}"
    put_clean_text(
        score_text,
        (width - 320, 45),
        scale=0.75,
        color=(180, 240, 255),
        thickness=2
    )

    # 3. TIMER
    time_seconds = int(time_remaining + 0.999)
    timer_text = f"TIME: {time_seconds}s"
    if time_seconds > 30:
        timer_color = (255, 255, 255)
    elif time_seconds > 15:
        timer_color = (120, 220, 255)
    else:
        timer_color = (100, 100, 255)

    put_clean_text(
        timer_text,
        (width - 150, 45),
        scale=0.75,
        color=timer_color,
        thickness=2
    )

    # 4. NUMBERS ENTERED
    if numbers_entered:
        entered_display = numbers_entered
        if answer is not None:
            entered_display += f" = {answer}"
    else:
        entered_display = "_"

    entered_text = f"ENTERED: {entered_display}"
    if wrong_answer and result_text is None:
        entered_text += "  (INCORRECT)"
        entered_color = (100, 140, 255)
    else:
        entered_color = (130, 255, 200)

    put_clean_text(
        entered_text,
        (30, 85),
        scale=0.75,
        color=entered_color,
        thickness=2
    )

    # Result notification in the center of the frame (no background box)
    if result_text is not None:
        if result_text == "WIN":
            main_text = "CORRECT!"
            sub_text = f"+1 POINT! Score: {challenge_score}"
            main_color = (100, 255, 100)
        else:
            main_text = "TIME'S UP!"
            ans_str = problem["answer"] if problem else "?"
            sub_text = f"Expected answer: {ans_str}"
            main_color = (80, 80, 255)

        main_size = cv2.getTextSize(
            main_text,
            cv2.FONT_HERSHEY_SIMPLEX,
            1.8,
            3
        )[0]
        main_x = (width - main_size[0]) // 2
        main_y = height // 2 - 10

        put_clean_text(
            main_text,
            (main_x, main_y),
            scale=1.8,
            color=main_color,
            thickness=3
        )

        sub_size = cv2.getTextSize(
            sub_text,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.85,
            2
        )[0]
        sub_x = (width - sub_size[0]) // 2
        sub_y = main_y + 45

        put_clean_text(
            sub_text,
            (sub_x, sub_y),
            scale=0.85,
            color=(240, 240, 240),
            thickness=2
        )


def draw_calculator_ui(
    frame,
    expression,
    answer,
    integral_mode,
    lower_bound,
    upper_bound,
    bound_mode,
    integral_steps
):
    height, width = frame.shape[:2]

    if integral_mode:
        panel_height = 225
    else:
        panel_height = 245

    overlay = frame.copy()

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

    if integral_mode:
        cv2.putText(
            frame,
            "INTEGRAND",
            (35, 82),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            (180, 180, 180),
            1,
            cv2.LINE_AA
        )

        draw_integral_expression(
            frame,
            expression,
            lower_bound,
            upper_bound
        )

        if bound_mode == "lower":
            status = "DRAW LOWER BOUND  A"
            status_color = (255, 220, 120)
        elif bound_mode == "upper":
            status = "DRAW UPPER BOUND  B"
            status_color = (255, 220, 120)
        elif lower_bound and upper_bound:
            status = "BOUNDS READY  -> PRESS ENTER"
            status_color = (180, 240, 255)
        elif expression:
            status = "PRESS A = LOWER   B = UPPER"
            status_color = (200, 200, 200)
        else:
            status = "DRAW THE FUNCTION FIRST"
            status_color = (200, 200, 200)

        cv2.putText(
            frame,
            status,
            (35, 165),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            status_color,
            1,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            "1. DRAW FUNCTION   2. A = LOWER   3. B = UPPER",
            (35, 190),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (200, 200, 200),
            1,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            "ENTER = SOLVE   C = CLEAR   I = EXIT",
            (35, 215),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (255, 220, 120),
            1,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            "BACKSPACE = DELETE LAST",
            (400, 215),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (200, 200, 200),
            1,
            cv2.LINE_AA
        )

        if integral_steps is not None:
            draw_integral_steps(
                frame,
                integral_steps,
                answer
            )
        else:
            cv2.putText(
                frame,
                "RESULT",
                (35, height - 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                (180, 180, 180),
                1,
                cv2.LINE_AA
            )

            if answer is None:
                answer_text = "—"
            else:
                answer_text = format_math_expression(
                    answer
                )

            cv2.putText(
                frame,
                answer_text,
                (130, height - 73),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.72,
                (180, 240, 255),
                2,
                cv2.LINE_AA
            )

            cv2.putText(
                frame,
                "T = TRAINING MODE",
                (35, height - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                (200, 200, 200),
                1,
                cv2.LINE_AA
            )

            cv2.putText(
                frame,
                "Q = QUIT",
                (230, height - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                (255, 220, 120),
                1,
                cv2.LINE_AA
            )

        return

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
        answer_text = format_math_expression(
            answer
        )

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


def parse_bound(
    bound_text
):
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


def clear_visuals(
    stroke_manager,
    glow_renderer,
    particle_system,
    spell_ring
):
    stroke_manager.clear()
    glow_renderer.clear()
    particle_system.clear()
    spell_ring.set_visible(False)


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
        integral_steps = None

        training_mode = False
        selected_training_symbol = None

        integral_mode = False
        integral_bound_mode = None

        lower_bound_tokens = []
        upper_bound_tokens = []

        challenge_mode = False
        challenge_selecting = False
        challenge_difficulty = "easy"
        challenge_timer = GameTimer(
            duration=60
        )
        challenge_problem = None
        challenge_result = None
        challenge_result_time = None
        challenge_wrong_answer = False

        # --- Audio setup (Avengers theme for Challenge Mode) ---
        _sound_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "sound"
        )
        _avengers_path = os.path.join(
            _sound_dir, "Avengers.mp3"
        )
        _music_loaded = False
        if _PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                if os.path.exists(_avengers_path):
                    pygame.mixer.music.load(_avengers_path)
                    _music_loaded = True
                    print("Avengers theme loaded.")
                else:
                    print(
                        "Warning: sound/Avengers.mp3 not found."
                    )
            except Exception as _e:
                print(f"Audio init failed: {_e}")

        def play_challenge_music():
            if _PYGAME_AVAILABLE and _music_loaded:
                pygame.mixer.music.play(-1)

        def stop_challenge_music():
            if _PYGAME_AVAILABLE and _music_loaded:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()

        def start_challenge_session(diff="easy"):
            nonlocal challenge_mode, challenge_selecting, challenge_difficulty
            nonlocal challenge_problem, challenge_result, challenge_result_time, challenge_wrong_answer
            nonlocal integral_mode, training_mode, selected_training_symbol
            nonlocal answer, integral_steps, integral_bound_mode

            challenge_selecting = False
            challenge_mode = True
            challenge_difficulty = diff

            integral_mode = (challenge_difficulty == "hard")
            training_mode = False
            selected_training_symbol = None

            challenge_problem = get_random_problem(difficulty=challenge_difficulty)
            game_state.start_challenge(challenge_problem)

            challenge_timer.reset()
            challenge_timer.set_duration(60)
            challenge_timer.start()

            challenge_result = None
            challenge_result_time = None
            challenge_wrong_answer = False

            math_engine.clear()
            game_state.clear_tokens()

            lower_bound_tokens.clear()
            upper_bound_tokens.clear()
            integral_bound_mode = None

            answer = None
            integral_steps = None

            clear_visuals(
                stroke_manager,
                glow_renderer,
                particle_system,
                spell_ring
            )

            play_challenge_music()

            print(
                f"Started {challenge_difficulty.upper()} Challenge Mode!"
            )
            print(
                f"Problem: {challenge_problem['display']}"
            )
            print(
                f"Solve it within {challenge_timer.duration} seconds!"
            )

        # --- Circle gesture detector (> 4 circles to enter challenge) ---
        circle_detector = CircleGestureDetector(
            target_revolutions=4.0,
            min_radius=25,
            cooldown=2.0
        )

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

            frame_height, frame_width = (
                frame.shape[:2]
            )

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

            # --- Circle gesture detection for Challenge Mode ---
            _hand_center_pos = None
            if hand is not None:
                _hx = int(
                    hand[9].x * frame_width
                )
                _hy = int(
                    hand[9].y * frame_height
                )
                _hand_center_pos = (_hx, _hy)

            _circle_triggered, _circle_info = (
                circle_detector.update(
                    _hand_center_pos,
                    current_time
                )
            )

            if _circle_triggered and not challenge_mode and not challenge_selecting:
                challenge_selecting = True
                clear_visuals(
                    stroke_manager,
                    glow_renderer,
                    particle_system,
                    spell_ring
                )
                print(
                    "Circle gesture detected! "
                    "Challenge selection opened. "
                    "Select difficulty: [1] Easy or [2] Hard"
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

                    if challenge_selecting:
                        token = (
                            recognizer.recognize(
                                stroke
                            )
                        )
                        if token == "1":
                            start_challenge_session("easy")
                        elif token == "2":
                            start_challenge_session("hard")
                        else:
                            print(
                                f"Recognized '{token}'. "
                                "Draw '1' for Easy or '2' for Hard."
                            )

                    elif training_mode:
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
                                and integral_bound_mode
                                == "lower"
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
                                and integral_bound_mode
                                == "upper"
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
                                integral_steps = None
                                challenge_wrong_answer = False

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
                    integral_steps = None
                    challenge_wrong_answer = False

                spell_ring.set_visible(
                    False
                )

                print(
                    "Current stroke cleared."
                )

            elif action == "ENTER":
                if not training_mode:
                    if integral_mode:
                        lower_bound_text = "".join(
                            lower_bound_tokens
                        )

                        upper_bound_text = "".join(
                            upper_bound_tokens
                        )

                        if not math_engine.get_display_expression():
                            answer = None
                            integral_steps = None

                            print(
                                "Draw a function first."
                            )

                        elif challenge_mode and not lower_bound_text and not upper_bound_text:
                            answer = (
                                math_engine
                                .get_answer_text()
                            )

                            if answer is None:
                                print(
                                    "Could not evaluate expression: "
                                    f"{math_engine.get_display_expression()}"
                                )
                            else:
                                print(
                                    "Challenge answer submitted: "
                                    f"{math_engine.get_display_expression()} = {answer}"
                                )

                        elif not lower_bound_text:
                            answer = None
                            integral_steps = None

                            print(
                                "Lower bound is missing. "
                                "Press A and draw it."
                            )

                        elif not upper_bound_text:
                            answer = None
                            integral_steps = None

                            print(
                                "Upper bound is missing. "
                                "Press B and draw it."
                            )

                        else:
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
                                integral_steps = None

                                print(
                                    "Bounds must be numbers."
                                )

                            else:
                                steps = (
                                    math_engine
                                    .get_definite_integral_steps(
                                        lower_value,
                                        upper_value
                                    )
                                )

                                if steps is None:
                                    answer = None
                                    integral_steps = None

                                    print(
                                        "Could not calculate "
                                        "definite integral:"
                                        f" {math_engine.get_display_expression()}"
                                    )

                                else:
                                    integral_steps = steps

                                    answer = (
                                        steps["result"]
                                    )

                                    print(
                                        "Definite integral solved."
                                    )

                                    print(
                                        "Antiderivative: "
                                        f"{steps['antiderivative']}"
                                    )

                                    print(
                                        f"F({upper_value}) - "
                                        f"F({lower_value}) = "
                                        f"{steps['upper_result']} - "
                                        f"{steps['lower_result']}"
                                    )

                                    print(
                                        f"Answer = "
                                        f"{steps['result']}"
                                    )

                    else:
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

            elif action == "IDLE":
                spell_ring.set_visible(
                    False
                )

            # --- Draw circle progress badge when charging ---
            if (
                not challenge_mode
                and _circle_info["progress"] > 0.05
                and _circle_info["center"] is not None
            ):
                _prog = _circle_info["progress"]
                _revs = _circle_info["revolutions"]
                _cx, _cy = _circle_info["center"]
                _rad = max(30, int(_circle_info["radius"] * 0.6))

                # Glowing background circle
                _badge_color = (
                    int(50 + 205 * _prog),
                    int(200 * (1 - _prog)),
                    int(255 * _prog)
                )
                cv2.circle(
                    frame,
                    (_cx, _cy),
                    _rad + 6,
                    (20, 20, 20),
                    -1,
                    cv2.LINE_AA
                )
                # Progress arc
                _arc_angle = int(360 * _prog)
                cv2.ellipse(
                    frame,
                    (_cx, _cy),
                    (_rad, _rad),
                    -90,
                    0,
                    _arc_angle,
                    _badge_color,
                    4,
                    cv2.LINE_AA
                )
                # Outer ring
                cv2.circle(
                    frame,
                    (_cx, _cy),
                    _rad + 6,
                    _badge_color,
                    2,
                    cv2.LINE_AA
                )
                # Revolution counter text
                _rev_txt = f"{min(4, int(_revs + 0.1))}/4"
                _ts = cv2.getTextSize(
                    _rev_txt,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    2
                )[0]
                cv2.putText(
                    frame,
                    _rev_txt,
                    (
                        _cx - _ts[0] // 2,
                        _cy + _ts[1] // 2
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA
                )
                # Label below
                _lbl = "PORTAL CHARGE"
                _ls = cv2.getTextSize(
                    _lbl,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    1
                )[0]
                cv2.putText(
                    frame,
                    _lbl,
                    (
                        _cx - _ls[0] // 2,
                        _cy + _rad + 22
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    _badge_color,
                    1,
                    cv2.LINE_AA
                )

            if challenge_mode:
                if challenge_result is not None:
                    if challenge_result_time is not None:
                        elapsed = (
                            time.monotonic()
                            - challenge_result_time
                        )

                        if elapsed >= 3.0:
                            if (
                                challenge_result
                                == "WIN"
                            ):
                                challenge_problem = (
                                    get_random_problem(
                                        difficulty=challenge_difficulty,
                                        exclude=(
                                            challenge_problem
                                        )
                                    )
                                )

                                game_state.start_challenge(
                                    challenge_problem
                                )

                                challenge_timer.reset()
                                challenge_timer.set_duration(
                                    60
                                )
                                challenge_timer.start()

                                challenge_result = None
                                challenge_result_time = (
                                    None
                                )
                                challenge_wrong_answer = False

                                math_engine.clear()
                                game_state.clear_tokens()

                                lower_bound_tokens.clear()
                                upper_bound_tokens.clear()

                                integral_bound_mode = None

                                answer = None
                                integral_steps = None

                                clear_visuals(
                                    stroke_manager,
                                    glow_renderer,
                                    particle_system,
                                    spell_ring
                                )

                                print(
                                    "New challenge! "
                                    f"{challenge_problem['display']}"
                                )

                            else:
                                challenge_mode = False
                                stop_challenge_music()
                                challenge_result = None
                                challenge_result_time = (
                                    None
                                )
                                challenge_wrong_answer = False

                                challenge_timer.reset()

                                game_state.reset_challenge()

                                print(
                                    "Challenge ended. "
                                    "Back to integral mode."
                                )

                elif (
                    challenge_timer.is_expired()
                ):
                    challenge_result = "LOSE"
                    challenge_result_time = (
                        time.monotonic()
                    )
                    challenge_wrong_answer = False

                    challenge_timer.stop()

                    game_state.set_challenge_lose()

                    print(
                        "Time's up! Challenge failed."
                    )

                elif answer is not None:
                    if game_state.check_challenge_answer(
                        answer
                    ):
                        challenge_result = "WIN"
                        challenge_result_time = (
                            time.monotonic()
                        )
                        challenge_wrong_answer = False

                        challenge_timer.stop()

                        game_state.set_challenge_win()

                        print(
                            "Correct! Challenge won! "
                            f"Score: {game_state.challenge_score}"
                        )

                    else:
                        challenge_wrong_answer = True

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

                if challenge_selecting:
                    draw_difficulty_select_ui(frame)
                elif challenge_mode:
                    draw_challenge_ui(
                        frame,
                        challenge_problem,
                        (
                            challenge_timer
                            .get_remaining()
                        ),
                        game_state.challenge_score,
                        math_engine.get_display_expression(),
                        answer,
                        challenge_result,
                        challenge_wrong_answer,
                        difficulty=challenge_difficulty
                    )
                else:
                    draw_calculator_ui(
                        frame,
                        math_engine.get_display_expression(),
                        answer,
                        integral_mode,
                        lower_bound_text,
                        upper_bound_text,
                        integral_bound_mode,
                        integral_steps
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
                if challenge_selecting:
                    challenge_selecting = False
                    print(
                        "Exited challenge difficulty selection."
                    )

                elif challenge_mode:
                    challenge_mode = False
                    stop_challenge_music()
                    challenge_result = None
                    challenge_result_time = None
                    challenge_problem = None
                    challenge_timer.reset()
                    game_state.reset_challenge()

                    clear_visuals(
                        stroke_manager,
                        glow_renderer,
                        particle_system,
                        spell_ring
                    )

                    print(
                        "Exited challenge mode."
                    )

                elif training_mode:
                    training_mode = False
                    selected_training_symbol = None

                    clear_visuals(
                        stroke_manager,
                        glow_renderer,
                        particle_system,
                        spell_ring
                    )

                    print(
                        "Exited training mode."
                    )

                elif integral_mode:
                    integral_mode = False
                    integral_bound_mode = None

                    lower_bound_tokens.clear()
                    upper_bound_tokens.clear()

                    answer = None
                    integral_steps = None

                    clear_visuals(
                        stroke_manager,
                        glow_renderer,
                        particle_system,
                        spell_ring
                    )

                    print(
                        "Exited integral mode."
                    )

                else:
                    break

            if challenge_selecting:
                if key == ord("1"):
                    start_challenge_session("easy")
                    continue
                elif key == ord("2"):
                    start_challenge_session("hard")
                    continue
                elif key == ord("g"):
                    start_challenge_session("easy")
                    continue
                elif key == ord("c"):
                    challenge_selecting = False
                    print("Cancelled challenge selection.")
                    continue

            if key == ord("t"):
                challenge_selecting = False
                training_mode = not training_mode
                selected_training_symbol = None

                if challenge_mode:
                    challenge_mode = False
                    stop_challenge_music()
                    challenge_result = None
                    challenge_result_time = None
                    challenge_problem = None
                    challenge_timer.reset()
                    game_state.reset_challenge()

                integral_mode = False
                integral_bound_mode = None

                lower_bound_tokens.clear()
                upper_bound_tokens.clear()

                answer = None
                integral_steps = None

                clear_visuals(
                    stroke_manager,
                    glow_renderer,
                    particle_system,
                    spell_ring
                )

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

            if key == ord("g"):
                if not challenge_mode and not challenge_selecting:
                    challenge_selecting = True
                    print(
                        "Challenge difficulty selection opened. "
                        "Press 1 for Easy (Algebra) or 2 for Hard (Calculus)."
                    )
                elif challenge_selecting:
                    start_challenge_session("easy")
                else:
                    challenge_problem = get_random_problem(
                        difficulty=challenge_difficulty,
                        exclude=challenge_problem
                    )
                    game_state.start_challenge(
                        challenge_problem
                    )

                    challenge_timer.reset()
                    challenge_timer.set_duration(60)
                    challenge_timer.start()

                    challenge_result = None
                    challenge_result_time = None

                    math_engine.clear()
                    game_state.clear_tokens()

                    lower_bound_tokens.clear()
                    upper_bound_tokens.clear()
                    integral_bound_mode = None

                    answer = None
                    integral_steps = None

                    clear_visuals(
                        stroke_manager,
                        glow_renderer,
                        particle_system,
                        spell_ring
                    )

                    print(
                        f"New {challenge_difficulty.upper()} challenge: "
                        f"{challenge_problem['display']}"
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

                if not integral_mode and challenge_mode:
                    challenge_mode = False
                    stop_challenge_music()
                    challenge_result = None
                    challenge_result_time = None
                    challenge_problem = None
                    challenge_timer.reset()
                    game_state.reset_challenge()

                integral_bound_mode = None

                lower_bound_tokens.clear()
                upper_bound_tokens.clear()

                answer = None
                integral_steps = None

                clear_visuals(
                    stroke_manager,
                    glow_renderer,
                    particle_system,
                    spell_ring
                )

                if integral_mode:
                    print(
                        "Entered integral mode."
                    )

                    print(
                        "Draw the function first."
                    )

                    print(
                        "Press A, then draw the "
                        "lower bound."
                    )

                    print(
                        "Press B, then draw the "
                        "upper bound."
                    )

                    print(
                        "Press ENTER (or hold FIST) "
                        "to solve."
                    )

                    print(
                        "Press G to start an "
                        "Integral Challenge!"
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

                            answer = None
                            integral_steps = None

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

                            answer = None
                            integral_steps = None

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
                            integral_steps = None

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
                    integral_steps = None
                    challenge_wrong_answer = False

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

                    if not math_engine.get_display_expression():
                        answer = None
                        integral_steps = None

                        print(
                            "Draw a function first."
                        )

                    elif challenge_mode and not lower_bound_text and not upper_bound_text:
                        answer = (
                            math_engine
                            .get_answer_text()
                        )

                        if answer is None:
                            print(
                                "Could not evaluate expression: "
                                f"{math_engine.get_display_expression()}"
                            )
                        else:
                            print(
                                "Challenge answer submitted: "
                                f"{math_engine.get_display_expression()} = {answer}"
                            )

                    elif not lower_bound_text:
                        answer = None
                        integral_steps = None

                        print(
                            "Lower bound is missing. "
                            "Press A and draw it."
                        )

                    elif not upper_bound_text:
                        answer = None
                        integral_steps = None

                        print(
                            "Upper bound is missing. "
                            "Press B and draw it."
                        )

                    else:
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
                            integral_steps = None

                            print(
                                "Bounds must be numbers."
                            )

                        else:
                            steps = (
                                math_engine
                                .get_definite_integral_steps(
                                    lower_value,
                                    upper_value
                                )
                            )

                            if steps is None:
                                answer = None
                                integral_steps = None

                                print(
                                    "Could not calculate "
                                    "definite integral:"
                                    f" {math_engine.get_display_expression()}"
                                )

                            else:
                                integral_steps = steps

                                answer = (
                                    steps["result"]
                                )

                                print(
                                    "Definite integral solved."
                                )

                                print(
                                    "Antiderivative: "
                                    f"{steps['antiderivative']}"
                                )

                                print(
                                    f"F({upper_value}) - "
                                    f"F({lower_value}) = "
                                    f"{steps['upper_result']} - "
                                    f"{steps['lower_result']}"
                                )

                                print(
                                    f"Answer = "
                                    f"{steps['result']}"
                                )

                continue

            if key == 8:
                removed_token = (
                    math_engine.remove_last_token()
                )

                if removed_token is not None:
                    game_state.remove_last_token()

                    answer = None
                    integral_steps = None

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
                integral_steps = None

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

        if _PYGAME_AVAILABLE:
            try:
                pygame.mixer.quit()
            except Exception:
                pass


if __name__ == "__main__":
    main()