import math


class StrokeRecognizer:
    def __init__(self):
        self.symbols = {
            "0": self._is_zero,
            "1": self._is_one,
            "2": self._is_two,
            "3": self._is_three,
            "4": self._is_four,
            "5": self._is_five,
            "6": self._is_six,
            "7": self._is_seven,
            "8": self._is_eight,
            "9": self._is_nine,
            "+": self._is_plus,
            "-": self._is_minus,
            "×": self._is_multiply,
            "÷": self._is_divide,
        }

    def recognize(self, stroke):
        if not stroke or len(stroke) < 5:
            return None

        points = self._normalize(stroke)

        if not points:
            return None

        features = self._get_features(points)

        candidates = []

        for symbol, detector in self.symbols.items():
            score = detector(features)

            if score is not None:
                candidates.append((score, symbol))

        if not candidates:
            return None

        candidates.sort(
            key=lambda candidate: candidate[0],
            reverse=True
        )

        return candidates[0][1]

    def _normalize(self, stroke):
        if not stroke:
            return []

        min_x = min(point[0] for point in stroke)
        max_x = max(point[0] for point in stroke)

        min_y = min(point[1] for point in stroke)
        max_y = max(point[1] for point in stroke)

        width = max_x - min_x
        height = max_y - min_y

        if width == 0 and height == 0:
            return []

        scale = max(width, height)

        normalized = []

        for x, y in stroke:
            normalized.append(
                (
                    (x - min_x) / scale,
                    (y - min_y) / scale
                )
            )

        return normalized

    def _get_features(self, points):
        min_x = min(point[0] for point in points)
        max_x = max(point[0] for point in points)

        min_y = min(point[1] for point in points)
        max_y = max(point[1] for point in points)

        width = max_x - min_x
        height = max_y - min_y

        path_length = 0.0

        for index in range(1, len(points)):
            x1, y1 = points[index - 1]
            x2, y2 = points[index]

            path_length += math.hypot(
                x2 - x1,
                y2 - y1
            )

        start_x, start_y = points[0]
        end_x, end_y = points[-1]

        start_end_distance = math.hypot(
            end_x - start_x,
            end_y - start_y
        )

        return {
            "points": points,
            "width": width,
            "height": height,
            "path_length": path_length,
            "start_end_distance": start_end_distance,
            "start": points[0],
            "end": points[-1],
        }

    def _score_range(self, value, minimum, maximum):
        if minimum <= value <= maximum:
            return 1.0

        if value < minimum:
            difference = minimum - value
        else:
            difference = value - maximum

        return max(0.0, 1.0 - difference * 3.0)

    def _is_zero(self, features):
        points = features["points"]

        if len(points) < 10:
            return None

        closedness = features["start_end_distance"]

        if closedness > 0.35:
            return None

        if features["height"] < 0.45:
            return None

        score = 0.0

        score += self._score_range(
            features["width"],
            0.45,
            1.0
        ) * 0.3

        score += self._score_range(
            features["height"],
            0.65,
            1.0
        ) * 0.3

        score += max(
            0.0,
            1.0 - closedness * 2.5
        ) * 0.4

        return score

    def _is_one(self, features):
        points = features["points"]

        if len(points) < 5:
            return None

        width = features["width"]
        height = features["height"]

        if height < 0.55:
            return None

        if width > 0.55:
            return None

        return self._score_range(
            width,
            0.0,
            0.35
        ) * 0.4 + self._score_range(
            height,
            0.65,
            1.0
        ) * 0.6

    def _is_two(self, features):
        points = features["points"]

        if len(points) < 8:
            return None

        if features["height"] < 0.5:
            return None

        start_x, start_y = features["start"]
        end_x, end_y = features["end"]

        if end_x < 0.2:
            return None

        if end_y < 0.65:
            return None

        return 0.7

    def _is_three(self, features):
        if features["height"] < 0.5:
            return None

        start_x, start_y = features["start"]
        end_x, end_y = features["end"]

        if start_x > 0.5:
            return None

        if end_x > 0.6:
            return None

        return 0.65

    def _is_four(self, features):
        points = features["points"]

        if len(points) < 8:
            return None

        if features["height"] < 0.5:
            return None

        if features["width"] < 0.25:
            return None

        return 0.65

    def _is_five(self, features):
        if features["height"] < 0.5:
            return None

        start_x, start_y = features["start"]

        if start_y > 0.35:
            return None

        return 0.6

    def _is_six(self, features):
        if features["height"] < 0.5:
            return None

        if features["width"] < 0.35:
            return None

        return 0.55

    def _is_seven(self, features):
        if features["height"] < 0.5:
            return None

        start_x, start_y = features["start"]

        if start_y > 0.3:
            return None

        return 0.6

    def _is_eight(self, features):
        points = features["points"]

        if len(points) < 12:
            return None

        if features["start_end_distance"] > 0.4:
            return None

        if features["height"] < 0.5:
            return None

        return 0.65

    def _is_nine(self, features):
        if features["height"] < 0.5:
            return None

        if features["width"] < 0.3:
            return None

        return 0.5

    def _is_plus(self, features):
        if features["width"] < 0.35:
            return None

        if features["height"] < 0.35:
            return None

        if features["width"] > 1.0:
            return None

        if features["height"] > 1.0:
            return None

        return 0.75

    def _is_minus(self, features):
        if features["width"] < 0.45:
            return None

        if features["height"] > 0.35:
            return None

        return 0.85

    def _is_multiply(self, features):
        if features["width"] < 0.3:
            return None

        if features["height"] < 0.3:
            return None

        start_x, start_y = features["start"]
        end_x, end_y = features["end"]

        if abs(start_x - end_x) < 0.2:
            return None

        return 0.7

    def _is_divide(self, features):
        if features["width"] < 0.3:
            return None

        if features["height"] > 0.5:
            return None

        return 0.65