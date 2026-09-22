import cv2


class HUD:
    def __init__(self):
        self.title = "CALCINTERIM"

    def draw(
        self,
        frame,
        target_expression,
        player_expression,
        time_remaining,
        score,
        status
    ):
        height, width = frame.shape[:2]

        overlay = frame.copy()

        cv2.rectangle(
            overlay,
            (20, 20),
            (width - 20, 145),
            (0, 0, 0),
            -1
        )

        frame[:] = cv2.addWeighted(
            overlay,
            0.45,
            frame,
            0.55,
            0
        )

        cv2.putText(
            frame,
            self.title,
            (40, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 180, 255),
            2,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            f"TARGET: {target_expression}",
            (40, 95),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 220, 120),
            2,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            f"CAST: {player_expression}",
            (40, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            f"TIME: {time_remaining:05.1f}",
            (width - 230, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            f"SCORE: {score}",
            (width - 230, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            f"STATUS: {status}",
            (width - 230, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (200, 200, 200),
            1,
            cv2.LINE_AA
        )

    def draw_instructions(self, frame):
        height = frame.shape[0]

        cv2.putText(
            frame,
            "Index + thumb out = DRAW",
            (30, height - 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 220, 120),
            2,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            "Release thumb = COMMIT   |   Open palm = CLEAR",
            (30, height - 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (220, 220, 220),
            1,
            cv2.LINE_AA
        )