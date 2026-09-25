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
    CAMERA_FPS,
    CAMERA_THREADED,
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
    Options:
      [1] EASY: Basic algebra & arithmetic
      [2] HARD: Alternative operations
      [3] INTEGRAL: Calculus & definite integrals
    """
    height, width = frame.shape[:2]

    # Semi-transparent dark card
    overlay = frame.copy()
    box_w = 720
    box_h = 425
    x1 = (width - box_w) // 2
    y1 = (height - box_h) // 2
    x2 = x1 + box_w
    y2 = y1 + box_h

    cv2.rectangle(overlay, (x1, y1), (x2, y2), (18, 20, 26), -1)
    cv2.addWeighted(overlay, 0.88, frame, 0.12, 0, frame)

    # Glowing Cyan border
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 215, 255), 2, cv2.LINE_AA)

    def center_text(text, y_pos, scale=0.8, color=(255, 255, 255), thickness=2):
        size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)[0]
        x = (width - size[0]) // 2
        cv2.putText(frame, text, (x, y_pos), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
        cv2.putText(frame, text, (x, y_pos), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)

    center_text("CHALLENGE MODE", y1 + 45, scale=1.05, color=(0, 215, 255), thickness=3)
    center_text("SELECT DIFFICULTY", y1 + 78, scale=0.68, color=(200, 240, 255), thickness=2)

    # Option 1: EASY
    center_text("[ 1 ]  EASY  -  Basic Algebra & Arithmetic", y1 + 130, scale=0.78, color=(100, 255, 130), thickness=2)
    center_text("Direct arithmetic evaluation (e.g., 4 x 5, 2 + 3, (2 + 3) x 4)", y1 + 155, scale=0.50, color=(180, 230, 190), thickness=1)

    # Option 2: HARD
    center_text("[ 2 ]  HARD  -  Alternative Operations", y1 + 205, scale=0.78, color=(80, 200, 255), thickness=2)
    center_text("Solve using a different operation (e.g., 2+2 -> use MULTIPLICATION or ())", y1 + 230, scale=0.50, color=(180, 220, 245), thickness=1)

    # Option 3: INTEGRAL
    center_text("[ 3 ]  INTEGRAL  -  Calculus & Definite Integrals", y1 + 280, scale=0.78, color=(255, 140, 100), thickness=2)
    center_text("Definite integrals with lower & upper bounds", y1 + 305, scale=0.50, color=(240, 190, 180), thickness=1)

    # Instructions
    center_text("Press [1], [2], or [3] on keyboard  (or draw 1, 2, or 3)", y1 + 365, scale=0.60, color=(255, 255, 255), thickness=2)
    center_text("Press [G] for Easy  |  Press [ESC] to Cancel", y1 + 395, scale=0.50, color=(160, 160, 160), thickness=1)


def draw_challenge_ui(
    frame,
    problem,
    time_remaining,
    challenge_score,
    numbers_entered,
    answer=None,
    result_text=None,
    wrong_answer=False,
    difficulty="easy",
    wrong_reason=None,
    total_elapsed=0.0,
    win_score=10,
    integral_step=0,
    integral_problem_data=None,
    integral_fa_submitted=None,
    integral_fb_submitted=None
):
    """
    Draws the challenge UI overlay directly onto the frame.
    Displays:
      1. Given (challenge problem + difficulty badge)
      2. Score
      3. Timer
      4. Rule / Constraint (if in Hard alternative operations mode)
      5. Numbers entered & verification status
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
    diff_lower = str(difficulty).lower()
    if diff_lower == "easy":
        diff_tag = " [EASY]"
        diff_color = (120, 255, 120)
    elif diff_lower == "hard":
        diff_tag = " [HARD]"
        diff_color = (80, 200, 255)
    else:
        diff_tag = " [INTEGRAL]"
        diff_color = (255, 140, 100)

    given_text = f"GIVEN{diff_tag}: {problem_display}"
    put_clean_text(
        given_text,
        (30, 45),
        scale=0.75,
        color=diff_color,
        thickness=2
    )

    # 2. SCORE  (e.g. "SCORE: 3/10")
    score_text = f"SCORE: {challenge_score}/{win_score}"
    put_clean_text(
        score_text,
        (width - 340, 45),
        scale=0.75,
        color=(180, 240, 255),
        thickness=2
    )

    # 3a. Per-question countdown timer
    time_seconds = int(time_remaining + 0.999)
    timer_text = f"Q:{time_seconds}s"
    if time_seconds > 30:
        timer_color = (255, 255, 255)
    elif time_seconds > 15:
        timer_color = (120, 220, 255)
    else:
        timer_color = (100, 100, 255)

    put_clean_text(
        timer_text,
        (width - 175, 45),
        scale=0.7,
        color=timer_color,
        thickness=2
    )

    # 3b. Total session stopwatch (counts up)
    total_mins = int(total_elapsed) // 60
    total_secs = int(total_elapsed) % 60
    total_cs   = int((total_elapsed % 1) * 100)
    total_text = f"{total_mins:02d}:{total_secs:02d}.{total_cs:02d}"
    put_clean_text(
        total_text,
        (width - 340, 80),
        scale=0.65,
        color=(255, 220, 100),
        thickness=2
    )

    # RULE / INSTRUCTION (for Hard mode alternative operations)
    instruction = problem.get("instruction") if problem else None

    if diff_lower == "integral" and integral_problem_data is not None and result_text is None:
        # --- Integral step-by-step guide ---
        pd = integral_problem_data
        a_str = str(pd["a"])
        b_str = str(pd["b"])
        fx_str = str(pd["antiderivative"])

        # Show F(x) antiderivative
        put_clean_text(
            f"F(x) = {fx_str}",
            (30, 80),
            scale=0.62,
            color=(255, 200, 80),
            thickness=2
        )

        # Step indicators
        step_labels = [
            f"STEP 1: Enter F({a_str})",
            f"STEP 2: Enter F({b_str})",
            f"STEP 3: Enter F({b_str}) - F({a_str})",
        ]
        step_colors_done  = (100, 255, 100)
        step_color_active = (255, 220, 60)
        step_color_idle   = (160, 160, 160)

        sy = 110
        for i, lbl in enumerate(step_labels):
            if i < integral_step:
                sc = step_colors_done
                prefix = "✓ "
                # show submitted value
                if i == 0 and integral_fa_submitted is not None:
                    lbl += f" = {integral_fa_submitted}"
                elif i == 1 and integral_fb_submitted is not None:
                    lbl += f" = {integral_fb_submitted}"
            elif i == integral_step:
                sc = step_color_active
                prefix = "► "
            else:
                sc = step_color_idle
                prefix = "  "
            put_clean_text(
                prefix + lbl,
                (30, sy),
                scale=0.58,
                color=sc,
                thickness=2
            )
            sy += 28

        entered_y = sy + 5

    elif instruction:
        put_clean_text(
            f"RULE: {instruction}",
            (30, 80),
            scale=0.65,
            color=(0, 225, 255),
            thickness=2
        )
        entered_y = 118
    else:
        entered_y = 85

    # 4. NUMBERS ENTERED
    if numbers_entered:
        entered_display = numbers_entered
        if answer is not None:
            entered_display += f" = {answer}"
    else:
        entered_display = "_"

    entered_text = f"ENTERED: {entered_display}"
    if wrong_answer and result_text is None:
        if wrong_reason:
            entered_text += f"  ({wrong_reason})"
        else:
            entered_text += "  (INCORRECT)"
        entered_color = (100, 140, 255)
    else:
        entered_color = (130, 255, 200)

    put_clean_text(
        entered_text,
        (30, entered_y),
        scale=0.75,
        color=entered_color,
        thickness=2
    )

    # Result notification in the center of the frame (no background box)
    if result_text is not None:
        if result_text == "COMPLETE":
            # Full-session victory banner
            t_mins = int(total_elapsed) // 60
            t_secs = int(total_elapsed) % 60
            t_cs   = int((total_elapsed % 1) * 100)
            time_str = f"{t_mins:02d}:{t_secs:02d}.{t_cs:02d}"

            # Dark translucent overlay so text pops
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (width, height), (0, 0, 0), -1)
            frame[:] = cv2.addWeighted(overlay, 0.55, frame, 0.45, 0)

            banner_text = "CHALLENGE COMPLETE!"
            banner_size = cv2.getTextSize(
                banner_text, cv2.FONT_HERSHEY_SIMPLEX, 1.9, 4
            )[0]
            put_clean_text(
                banner_text,
                ((width - banner_size[0]) // 2, height // 2 - 60),
                scale=1.9,
                color=(80, 255, 120),
                thickness=4
            )

            score_line = f"SCORE: {challenge_score}/{win_score}"
            score_sz = cv2.getTextSize(
                score_line, cv2.FONT_HERSHEY_SIMPLEX, 1.1, 2
            )[0]
            put_clean_text(
                score_line,
                ((width - score_sz[0]) // 2, height // 2 + 5),
                scale=1.1,
                color=(180, 240, 255),
                thickness=2
            )

            time_line = f"FINAL TIME: {time_str}"
            time_sz = cv2.getTextSize(
                time_line, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3
            )[0]
            put_clean_text(
                time_line,
                ((width - time_sz[0]) // 2, height // 2 + 65),
                scale=1.2,
                color=(255, 215, 80),
                thickness=3
            )

            hint_text = "Press ESC to exit"
            hint_sz = cv2.getTextSize(
                hint_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1
            )[0]
            put_clean_text(
                hint_text,
                ((width - hint_sz[0]) // 2, height // 2 + 115),
                scale=0.6,
                color=(200, 200, 200),
                thickness=1
            )

        elif result_text == "WIN":
            main_text = "CORRECT!"
            sub_text = f"+1 POINT! Score: {challenge_score}/{win_score}"
            main_color = (100, 255, 100)

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
        fps=CAMERA_FPS,
        mirror=MIRROR_CAMERA,
        threaded=CAMERA_THREADED
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
        challenge_wrong_reason = None
        # Total session stopwatch: records time.monotonic() when session starts,
        # None when no session is active.
        challenge_session_start = None
        challenge_session_elapsed = 0.0   # frozen once COMPLETE
        CHALLENGE_WIN_SCORE = 10

        # --- Integral challenge multi-step state ---
        # step 0 = player must enter F(a)
        # step 1 = player must enter F(b)
        # step 2 = player must enter F(b) - F(a)  (final answer)
        integral_challenge_step = 0
        integral_fa_submitted = None   # confirmed F(a) value (string)
        integral_fb_submitted = None   # confirmed F(b) value (string)
        # Precomputed values for the current integral challenge problem
        integral_problem_data = None   # dict: antiderivative, fa, fb, result

        # --- Audio setup (Avengers theme & sound effects) ---
        _sound_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "sound"
        )
        _avengers_path = os.path.join(_sound_dir, "Avengers.mp3")
        _correct_path = os.path.join(_sound_dir, "Correct_Sound.mp3")
        _wrong_path = os.path.join(_sound_dir, "Wrong_Sound.mp3")
        _swoosh_path = os.path.join(_sound_dir, "Swoosh_Sound.mp3")

        _music_loaded = False
        _correct_sound = None
        _wrong_sound = None
        _swoosh_sound = None

        if _PYGAME_AVAILABLE:
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()

                if os.path.exists(_avengers_path):
                    pygame.mixer.music.load(_avengers_path)
                    _music_loaded = True
                    print("Avengers theme loaded.")
                else:
                    print("Warning: sound/Avengers.mp3 not found.")

                if os.path.exists(_correct_path):
                    _correct_sound = pygame.mixer.Sound(_correct_path)
                    print("Correct sound effect loaded.")

                if os.path.exists(_wrong_path):
                    _wrong_sound = pygame.mixer.Sound(_wrong_path)
                    print("Wrong sound effect loaded.")

                if os.path.exists(_swoosh_path):
                    _swoosh_sound = pygame.mixer.Sound(_swoosh_path)
                    print("Swoosh sound effect loaded.")

            except Exception as _e:
                print(f"Audio init failed: {_e}")

        def play_challenge_music():
            if _PYGAME_AVAILABLE and _music_loaded:
                pygame.mixer.music.play(-1)

        def stop_challenge_music():
            if _PYGAME_AVAILABLE and _music_loaded:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()

        def play_correct_sound():
            if _PYGAME_AVAILABLE and _correct_sound is not None:
                _correct_sound.play()

        def play_wrong_sound():
            if _PYGAME_AVAILABLE and _wrong_sound is not None:
                _wrong_sound.play()

        def play_swoosh_sound():
            if _PYGAME_AVAILABLE and _swoosh_sound is not None:
                _swoosh_sound.play()

        def _compute_integral_problem_data(problem):
            """
            Given an integral challenge problem dict with keys:
              integrand, lower_bound, upper_bound, answer
            Precomputes (using sympy):
              antiderivative F(x), F(a)=F(lower), F(b)=F(upper), result=F(b)-F(a)
            Returns a dict or None on failure.
            """
            if problem is None or "integrand" not in problem:
                return None
            try:
                import sympy as sp
                from sympy.parsing.sympy_parser import (
                    parse_expr,
                    standard_transformations,
                    implicit_multiplication_application,
                )
                x = sp.Symbol("x")
                expr_str = (
                    str(problem["integrand"])
                    .replace("×", "*")
                    .replace("÷", "/")
                    .replace("^", "**")
                )
                trans = standard_transformations + (
                    implicit_multiplication_application,
                )
                integrand = parse_expr(
                    expr_str,
                    local_dict={"x": x},
                    transformations=trans,
                    evaluate=True
                )
                antiderivative = sp.simplify(sp.integrate(integrand, x))
                a = sp.sympify(problem["lower_bound"])
                b = sp.sympify(problem["upper_bound"])
                fa = sp.simplify(antiderivative.subs(x, a))
                fb = sp.simplify(antiderivative.subs(x, b))
                result = sp.simplify(fb - fa)
                return {
                    "antiderivative": antiderivative,
                    "a": a,
                    "b": b,
                    "fa": fa,
                    "fb": fb,
                    "result": result,
                }
            except Exception:
                return None

        def start_challenge_session(diff="easy"):
            nonlocal challenge_mode, challenge_selecting, challenge_difficulty
            nonlocal challenge_problem, challenge_result, challenge_result_time
            nonlocal challenge_wrong_answer, challenge_wrong_reason
            nonlocal integral_mode, training_mode, selected_training_symbol
            nonlocal answer, integral_steps, integral_bound_mode
            nonlocal challenge_session_start, challenge_session_elapsed
            nonlocal integral_challenge_step, integral_fa_submitted
            nonlocal integral_fb_submitted, integral_problem_data

            challenge_selecting = False
            challenge_mode = True
            challenge_difficulty = diff

            integral_mode = (challenge_difficulty == "integral")
            training_mode = False
            selected_training_symbol = None

            challenge_problem = get_random_problem(difficulty=challenge_difficulty)

            challenge_timer.reset()
            challenge_timer.set_duration(60)
            challenge_timer.start()

            challenge_result = None
            challenge_result_time = None
            challenge_wrong_answer = False
            challenge_wrong_reason = None

            # Reset score and start total stopwatch
            game_state.reset_challenge()
            game_state.start_challenge(challenge_problem)
            challenge_session_start = time.monotonic()
            challenge_session_elapsed = 0.0

            # Precompute F(a), F(b) for integral challenge
            integral_challenge_step = 0
            integral_fa_submitted = None
            integral_fb_submitted = None
            integral_problem_data = _compute_integral_problem_data(
                challenge_problem
            ) if challenge_difficulty == "integral" else None

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
            print(
                f"First to score {CHALLENGE_WIN_SCORE} wins!"
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
                    "Select difficulty: [1] Easy, [2] Hard, or [3] Integral"
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
                        elif token == "3":
                            start_challenge_session("integral")
                        else:
                            print(
                                f"Recognized '{token}'. "
                                "Draw '1' for Easy, '2' for Hard, or '3' for Integral."
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
                            play_swoosh_sound()
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
                                challenge_wrong_reason = None

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
                    challenge_wrong_reason = None

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
                            # --- Integral challenge multi-step submission ---
                            raw = math_engine.get_answer_text()
                            if raw is None:
                                print(
                                    "Could not evaluate: "
                                    f"{math_engine.get_display_expression()}"
                                )
                            else:
                                # Helper: check if user value == expected sympy value
                                def _int_step_ok(user_str, expected_sym):
                                    import sympy as _sp
                                    try:
                                        uv = _sp.sympify(str(user_str))
                                        return _sp.simplify(uv - expected_sym) == 0
                                    except Exception:
                                        return False

                                pd = integral_problem_data
                                if pd is None:
                                    # Fallback: no precomputed data, accept any evaluation
                                    answer = raw
                                    print(f"Answer submitted: {raw}")

                                elif integral_challenge_step == 0:
                                    # Step 1: expecting F(a)
                                    if _int_step_ok(raw, pd["fa"]):
                                        integral_fa_submitted = raw
                                        integral_challenge_step = 1
                                        math_engine.clear()
                                        game_state.clear_tokens()
                                        play_correct_sound()
                                        print(
                                            f"F({pd['a']}) = {raw} ✓  "
                                            "Now enter F(b)."
                                        )
                                    else:
                                        play_wrong_sound()
                                        challenge_wrong_answer = True
                                        challenge_wrong_reason = (
                                            f"F({pd['a']}) is wrong"
                                        )
                                        print(
                                            f"Incorrect F({pd['a']}). "
                                            f"Got {raw}, expected {pd['fa']}."
                                        )

                                elif integral_challenge_step == 1:
                                    # Step 2: expecting F(b)
                                    if _int_step_ok(raw, pd["fb"]):
                                        integral_fb_submitted = raw
                                        integral_challenge_step = 2
                                        math_engine.clear()
                                        game_state.clear_tokens()
                                        play_correct_sound()
                                        print(
                                            f"F({pd['b']}) = {raw} ✓  "
                                            "Now enter F(b) - F(a)."
                                        )
                                    else:
                                        play_wrong_sound()
                                        challenge_wrong_answer = True
                                        challenge_wrong_reason = (
                                            f"F({pd['b']}) is wrong"
                                        )
                                        print(
                                            f"Incorrect F({pd['b']}). "
                                            f"Got {raw}, expected {pd['fb']}."
                                        )

                                else:
                                    # Step 3: expecting F(b) - F(a) = final answer
                                    answer = raw
                                    print(
                                        f"Final answer submitted: "
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
                                # Check if player reached the win score
                                if game_state.challenge_score >= CHALLENGE_WIN_SCORE:
                                    # Session complete — stay in challenge_mode
                                    # so COMPLETE banner keeps rendering;
                                    # ESC exits.
                                    challenge_result = "COMPLETE"
                                    challenge_result_time = None  # don't auto-advance
                                    stop_challenge_music()
                                    play_correct_sound()
                                    print(
                                        f"CHALLENGE COMPLETE! "
                                        f"Final score: {game_state.challenge_score}/{CHALLENGE_WIN_SCORE} "
                                        f"in {challenge_session_elapsed:.2f}s"
                                    )

                                else:
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
                                    challenge_wrong_reason = None

                                    math_engine.clear()
                                    game_state.clear_tokens()

                                    lower_bound_tokens.clear()
                                    upper_bound_tokens.clear()

                                    integral_bound_mode = None

                                    answer = None
                                    integral_steps = None

                                    # Reset integral multi-step state
                                    integral_challenge_step = 0
                                    integral_fa_submitted = None
                                    integral_fb_submitted = None
                                    integral_problem_data = (
                                        _compute_integral_problem_data(
                                            challenge_problem
                                        )
                                        if challenge_difficulty == "integral"
                                        else None
                                    )

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
                                challenge_wrong_reason = None

                                challenge_timer.reset()
                                challenge_session_start = None

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
                    challenge_wrong_reason = None

                    challenge_timer.stop()

                    game_state.set_challenge_lose()
                    play_wrong_sound()

                    print(
                        "Time's up! Challenge failed."
                    )

                elif answer is not None:
                    user_expr = math_engine.get_display_expression()
                    if game_state.check_challenge_answer(
                        answer,
                        user_expression=user_expr
                    ):
                        challenge_result = "WIN"
                        challenge_result_time = (
                            time.monotonic()
                        )
                        challenge_wrong_answer = False
                        challenge_wrong_reason = None

                        challenge_timer.stop()

                        game_state.set_challenge_win()
                        # Freeze the session elapsed time immediately on win
                        if challenge_session_start is not None:
                            challenge_session_elapsed = (
                                time.monotonic() - challenge_session_start
                            )
                        play_correct_sound()

                        print(
                            "Correct! Challenge won! "
                            f"Score: {game_state.challenge_score}/{CHALLENGE_WIN_SCORE}"
                        )

                    else:
                        if not challenge_wrong_answer:
                            play_wrong_sound()
                            if game_state.last_check_reason == "MISSING_OP":
                                req_op = challenge_problem.get("required_op", "OPERATION") if challenge_problem else "OPERATION"
                                challenge_wrong_reason = f"MUST USE {req_op}"
                                print(
                                    f"Answer value matches, but must use {req_op}!"
                                )
                            else:
                                challenge_wrong_reason = "INCORRECT"
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
                    # Compute live total elapsed (frozen once COMPLETE)
                    if challenge_result == "COMPLETE":
                        _total_elapsed = challenge_session_elapsed
                    elif challenge_session_start is not None:
                        _total_elapsed = time.monotonic() - challenge_session_start
                    else:
                        _total_elapsed = 0.0
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
                        difficulty=challenge_difficulty,
                        wrong_reason=challenge_wrong_reason,
                        total_elapsed=_total_elapsed,
                        win_score=CHALLENGE_WIN_SCORE,
                        integral_step=integral_challenge_step,
                        integral_problem_data=integral_problem_data,
                        integral_fa_submitted=integral_fa_submitted,
                        integral_fb_submitted=integral_fb_submitted
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
                    challenge_session_start = None
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
                elif key == ord("3"):
                    start_challenge_session("integral")
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
                        "Press 1 for Easy, 2 for Hard (Alt Operations), or 3 for Integral."
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
                    challenge_wrong_answer = False
                    challenge_wrong_reason = None

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
                            # --- Integral challenge multi-step submission (keyboard) ---
                            raw = math_engine.get_answer_text()
                            if raw is None:
                                print(
                                    "Could not evaluate expression: "
                                    f"{math_engine.get_display_expression()}"
                                )
                            else:
                                def _int_step_ok_k(user_str, expected_sym):
                                    import sympy as _sp
                                    try:
                                        uv = _sp.sympify(str(user_str))
                                        return _sp.simplify(uv - expected_sym) == 0
                                    except Exception:
                                        return False

                                pd = integral_problem_data
                                if pd is None:
                                    answer = raw
                                    print(f"Answer submitted: {raw}")

                                elif integral_challenge_step == 0:
                                    if _int_step_ok_k(raw, pd["fa"]):
                                        integral_fa_submitted = raw
                                        integral_challenge_step = 1
                                        math_engine.clear()
                                        game_state.clear_tokens()
                                        play_correct_sound()
                                        print(
                                            f"F({pd['a']}) = {raw} ✓  "
                                            "Now enter F(b)."
                                        )
                                    else:
                                        play_wrong_sound()
                                        challenge_wrong_answer = True
                                        challenge_wrong_reason = (
                                            f"F({pd['a']}) is wrong"
                                        )
                                        print(
                                            f"Incorrect F({pd['a']}). "
                                            f"Got {raw}, expected {pd['fa']}."
                                        )

                                elif integral_challenge_step == 1:
                                    if _int_step_ok_k(raw, pd["fb"]):
                                        integral_fb_submitted = raw
                                        integral_challenge_step = 2
                                        math_engine.clear()
                                        game_state.clear_tokens()
                                        play_correct_sound()
                                        print(
                                            f"F({pd['b']}) = {raw} ✓  "
                                            "Now enter F(b) - F(a)."
                                        )
                                    else:
                                        play_wrong_sound()
                                        challenge_wrong_answer = True
                                        challenge_wrong_reason = (
                                            f"F({pd['b']}) is wrong"
                                        )
                                        print(
                                            f"Incorrect F({pd['b']}). "
                                            f"Got {raw}, expected {pd['fb']}."
                                        )

                                else:
                                    answer = raw
                                    print(
                                        f"Final answer submitted: "
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