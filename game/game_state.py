from enum import Enum


class GameStatus(Enum):
    READY = "READY"
    PLAYING = "PLAYING"
    VICTORY = "VICTORY"
    FAILED = "FAILED"


class GameState:
    def __init__(self):
        self.status = GameStatus.READY

        self.target_expression = ""
        self.player_tokens = []

        self.score = 0

    def start_round(self, target_expression):
        self.status = GameStatus.PLAYING
        self.target_expression = target_expression
        self.player_tokens.clear()

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

    def is_playing(self):
        return self.status == GameStatus.PLAYING

    def is_victory(self):
        return self.status == GameStatus.VICTORY

    def is_failed(self):
        return self.status == GameStatus.FAILED