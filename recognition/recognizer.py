class StrokeRecognizer:
    def __init__(self):
        self.default_token = "3"

    def recognize(self, stroke):
        if not stroke:
            return None

        return self.default_token