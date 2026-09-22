from enum import Enum

import sympy as sp


class GameStatus(Enum):
    READY = "READY"
    PLAYING = "PLAYING"
    VICTORY = "VICTORY"
    FAILED = "FAILED"
    CHALLENGE = "CHALLENGE"
    CHALLENGE_WIN = "CHALLENGE_WIN"
    CHALLENGE_LOSE = "CHALLENGE_LOSE"


class GameState:
    def __init__(self):
        self.status = GameStatus.READY

        self.target_expression = ""
        self.player_tokens = []

        self.score = 0

        self.challenge_problem = None
        self.challenge_score = 0

    def start_round(self, target_expression):
        self.status = GameStatus.PLAYING
        self.target_expression = target_expression
        self.player_tokens.clear()

    def start_challenge(self, problem):
        self.status = GameStatus.CHALLENGE
        self.challenge_problem = problem
        self.player_tokens.clear()

    def check_challenge_answer(
        self,
        user_answer
    ):
        """
        Checks if the user's computed answer
        matches the challenge problem's expected
        answer. Uses sympy simplify for robustness.

        Returns True if the answer matches.
        """

        if self.challenge_problem is None:
            return False

        if user_answer is None:
            return False

        expected = self.challenge_problem["answer"]

        try:
            user_value = sp.sympify(user_answer)
            expected_value = sp.sympify(expected)

            difference = sp.simplify(
                user_value - expected_value
            )

            return difference == 0

        except (
            sp.SympifyError,
            ValueError,
            TypeError
        ):
            return False

    def set_challenge_win(self):
        self.status = GameStatus.CHALLENGE_WIN
        self.challenge_score += 1

    def set_challenge_lose(self):
        self.status = GameStatus.CHALLENGE_LOSE

    def is_challenge(self):
        return self.status == GameStatus.CHALLENGE

    def is_challenge_win(self):
        return (
            self.status == GameStatus.CHALLENGE_WIN
        )

    def is_challenge_lose(self):
        return (
            self.status == GameStatus.CHALLENGE_LOSE
        )

    def is_challenge_active(self):
        return self.status in (
            GameStatus.CHALLENGE,
            GameStatus.CHALLENGE_WIN,
            GameStatus.CHALLENGE_LOSE,
        )

    def add_token(self, token):
        if self.status != GameStatus.PLAYING:
            return

        if token is None:
            return

        self.player_tokens.append(token)

    def remove_last_token(self):
        if self.player_tokens:
            return self.player_tokens.pop()

        return None

    def clear_tokens(self):
        self.player_tokens.clear()

    def get_player_expression(self):
        return "".join(self.player_tokens)

    def set_victory(self):
        self.status = GameStatus.VICTORY
        self.score += 1

    def set_failed(self):
        self.status = GameStatus.FAILED

    def reset(self):
        self.status = GameStatus.READY
        self.target_expression = ""
        self.player_tokens.clear()
        self.score = 0

    def reset_challenge(self):
        self.status = GameStatus.READY
        self.challenge_problem = None

    def is_playing(self):
        return self.status == GameStatus.PLAYING

    def is_victory(self):
        return self.status == GameStatus.VICTORY

    def is_failed(self):
        return self.status == GameStatus.FAILED