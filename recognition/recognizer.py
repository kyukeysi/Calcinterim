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

            if score is not None and score > 0:
                candidates.append((score, symbol))

        if not candidates:
            return None

        candidates.sort(
            key=lambda candidate: candidate[0],
            reverse=True
        )

        best_score, best_symbol = candidates[0]

        if best_score < 0.55:
            return None

        return best_symbol

    def _normalize(self, stroke):
        min_x = min(point[0] for point in stroke)
        max_x = max(point[0] for point in stroke)

        min_y = min(point[1] for point in stroke)
        max_y = max(point[1] for point in stroke)

        width = max_x - min_x
        height = max_y - min_y

        if width == 0 and height == 0:
            return []

        scale = max(width, height)

        return [
            (
                (x - min_x) / scale,
                (y - min_y) / scale
            )
            for x, y in stroke
        ]

    def _get_features(self, points):
        min_x = min(point[0] for point in points)
        max_x = max(point[0] for point in points)

        min_y = min(point[1] for point in points)
        max_y = max(point[1] for point in points)

        width = max_x - min_x
        height = max_y - min_y

        path_length = 0.0
        directions = []

        for index in range(1, len(points)):
            x1, y1 = points[index - 1]
            x2, y2 = points[index]

            dx = x2 - x1
            dy = y2 - y1

            distance = math.hypot(dx, dy)

            path_length += distance

            if distance > 0.015:
                directions.append(
                    math.atan2(dy, dx)
                )

        start_x, start_y = points[0]
        end_x, end_y = points[-1]

        start_end_distance = math.hypot(
            end_x - start_x,
            end_y - start_y
        )

        direction_changes = self._count_direction_changes(
            directions
        )

        horizontal_length = 0.0
        vertical_length = 0.0

        for index in range(1, len(points)):
            x1, y1 = points[index - 1]
            x2, y2 = points[index]

            dx = abs(x2 - x1)
            dy = abs(y2 - y1)

            horizontal_length += dx
            vertical_length += dy

        return {
            "points": points,
            "width": width,
            "height": height,
            "path_length": path_length,
            "start_end_distance": start_end_distance,
            "direction_changes": direction_changes,
            "horizontal_length": horizontal_length,
            "vertical_length": vertical_length,
            "start": points[0],
            "end": points[-1],
        }

    def _count_direction_changes(self, directions):
        if len(directions) < 3:
            return 0

        changes = 0

        previous_direction = directions[0]

        for direction in directions[1:]:
            difference = abs(
                direction - previous_direction
            )

            if difference > math.pi:
                difference = math.tau - difference

            if difference > math.radians(35):
                changes += 1

            previous_direction = direction

        return changes

    def _score_range(self, value, minimum, maximum):
        if minimum <= value <= maximum:
            return 1.0

        if value < minimum:
            difference = minimum - value
        else:
            difference = value - maximum

        return max(
            0.0,
            1.0 - difference * 3.0
        )

    def _is_zero(self, features):
        if features["start_end_distance"] > 0.25:
            return None

        if features["height"] < 0.55:
            return None

        if features["width"] < 0.35:
            return None

        if features["path_length"] < 1.0:
            return None

        return (
            self._score_range(
                features["width"],
                0.45,
                1.0
            ) * 0.3
            +
            self._score_range(
                features["height"],
                0.65,
                1.0
            ) * 0.3
            +
            max(
                0.0,
                1.0 - features["start_end_distance"] * 3
            ) * 0.4
        )

    def _is_one(self, features):
        if features["height"] < 0.6:
            return None

        if features["width"] > 0.45:
            return None

        if features["vertical_length"] < 0.55:
            return None

        if features["direction_changes"] > 5:
            return None

        return (
            self._score_range(
                features["width"],
                0.0,
                0.3
            ) * 0.35
            +
            self._score_range(
                features["height"],
                0.65,
                1.0
            ) * 0.45
            +
            self._score_range(
                features["vertical_length"],
                0.55,
                1.2
            ) * 0.2
        )

    def _is_two(self, features):
        points = features["points"]

        if features["height"] < 0.55:
            return None

        if features["width"] < 0.45:
            return None

        if len(points) < 8:
            return None

        start_x, start_y = features["start"]
        end_x, end_y = features["end"]

        if start_y > 0.35:
            return None

        if end_y < 0.65:
            return None

        if features["direction_changes"] < 2:
            return None

        return 0.72

    def _is_three(self, features):
        if features["height"] < 0.55:
            return None

        if features["width"] < 0.4:
            return None

        if features["direction_changes"] < 2:
            return None

        start_x, start_y = features["start"]

        if start_y > 0.35:
            return None

        return 0.68

    def _is_four(self, features):
        if features["height"] < 0.55:
            return None

        if features["width"] < 0.35:
            return None

        if features["direction_changes"] < 1:
            return None

        return 0.67

    def _is_five(self, features):
        if features["height"] < 0.55:
            return None

        if features["width"] < 0.4:
            return None

        start_x, start_y = features["start"]

        if start_y > 0.3:
            return None

        if features["direction_changes"] < 2:
            return None

        return 0.65

    def _is_six(self, features):
        if features["height"] < 0.55:
            return None

        if features["width"] < 0.4:
            return None

        if features["direction_changes"] < 2:
            return None

        return 0.62

    def _is_seven(self, features):
        if features["height"] < 0.55:
            return None

        if features["width"] < 0.4:
            return None

        start_x, start_y = features["start"]

        if start_y > 0.3:
            return None

        if features["direction_changes"] < 1:
            return None

        return 0.65

    def _is_eight(self, features):
        if features["height"] < 0.55:
            return None

        if features["width"] < 0.4:
            return None

        if features["start_end_distance"] > 0.3:
            return None

        if features["direction_changes"] < 3:
            return None

        return 0.7

    def _is_nine(self, features):
        if features["height"] < 0.55:
            return None

        if features["width"] < 0.4:
            return None

        if features["direction_changes"] < 2:
            return None

        start_y = features["start"][1]

        if start_y > 0.4:
            return None

        return 0.62

    def _is_plus(self, features):
        if features["width"] < 0.35:
            return None

        if features["height"] < 0.35:
            return None

        if features["width"] > 0.85:
            return None

        if features["height"] > 0.85:
            return None

        if features["direction_changes"] < 1:
            return None

        horizontal = features["horizontal_length"]
        vertical = features["vertical_length"]

        if horizontal < 0.25:
            return None

        if vertical < 0.25:
            return None

        ratio = min(horizontal, vertical) / max(
            horizontal,
            vertical
        )

        return 0.55 + ratio * 0.4

    def _is_minus(self, features):
        if features["width"] < 0.45:
            return None

        if features["height"] > 0.25:
            return None

        if features["horizontal_length"] < 0.4:
            return None

        return 0.9

    def _is_multiply(self, features):
        if features["width"] < 0.35:
            return None

        if features["height"] < 0.35:
            return None

        if features["direction_changes"] < 1:
            return None

        start_x, start_y = features["start"]
        end_x, end_y = features["end"]

        if abs(start_x - end_x) < 0.15:
            return None

        if abs(start_y - end_y) < 0.15:
            return None

        return 0.7

    def _is_divide(self, features):
        if features["width"] < 0.4:
            return None

        if features["height"] > 0.3:
            return None

        if features["horizontal_length"] < 0.4:
            return None

        return 0.7