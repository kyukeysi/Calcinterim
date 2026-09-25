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
        self.last_check_reason = None

    def start_round(self, target_expression):
        self.status = GameStatus.PLAYING
        self.target_expression = target_expression
        self.player_tokens.clear()

    def start_challenge(self, problem):
        self.status = GameStatus.CHALLENGE
        self.challenge_problem = problem
        self.player_tokens.clear()
        self.last_check_reason = None

    def check_challenge_answer(
        self,
        user_answer,
        user_expression=None
    ):
        """
        Checks if the user's computed answer matches the challenge problem's expected
        answer. If the problem specifies required_symbols (e.g. for alternative operation mode),
        verifies that the user's expression used at least one of those required symbols.

        Returns True if the answer matches and satisfies all constraints.
        """
        self.last_check_reason = None

        if self.challenge_problem is None or user_answer is None:
            self.last_check_reason = "NO_ANSWER"
            return False

        # First, verify the mathematical value matches
        expected = self.challenge_problem["answer"]

        try:
            user_value = sp.sympify(user_answer)
            expected_value = sp.sympify(expected)

            difference = sp.simplify(
                user_value - expected_value
            )

            if difference != 0:
                self.last_check_reason = "WRONG_VALUE"
                return False

        except (
            sp.SympifyError,
            ValueError,
            TypeError
        ):
            self.last_check_reason = "PARSE_ERROR"
            return False

        # Check alternative operation requirement (e.g. must use multiplication)
        required_symbols = self.challenge_problem.get("required_symbols")
        required_op = self.challenge_problem.get("required_op")
        if required_symbols or required_op:
            expr_str = str(user_expression) if user_expression is not None else ""
            has_required_op = False

            if required_symbols:
                has_required_op = any(sym in expr_str for sym in required_symbols)

            # If required_op is MULTIPLICATION, check if parentheses form valid implicit multiplication
            # e.g., 5(2), (5)(2), 2(5), etc.
            if required_op == "MULTIPLICATION":
                if any(s in expr_str for s in ["*", "×", "x"]):
                    has_required_op = True
                elif "(" in expr_str or ")" in expr_str:
                    try:
                        from sympy.parsing.sympy_parser import (
                            parse_expr,
                            standard_transformations,
                            implicit_multiplication_application,
                        )
                        clean = (
                            expr_str
                            .replace("×", "*")
                            .replace("÷", "/")
                            .replace("^", "**")
                            .replace("²", "**2")
                        )
                        trans = standard_transformations + (
                            implicit_multiplication_application,
                        )
                        parsed_ast = parse_expr(clean, transformations=trans, evaluate=False)
                        has_required_op = any(
                            isinstance(node, sp.Mul)
                            for node in sp.preorder_traversal(parsed_ast)
                        )
                    except Exception:
                        has_required_op = True
                else:
                    has_required_op = False

            if not has_required_op:
                self.last_check_reason = "MISSING_OP"
                return False

        self.last_check_reason = "CORRECT"
        return True

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