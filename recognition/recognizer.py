import json
import math
import os


class StrokeRecognizer:
    def __init__(
        self,
        template_file="recognition/user_templates.json"
    ):
        self.sample_count = 32
        self.template_file = template_file

        self.symbols = [
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "+",
            "-",
            "×",
            "÷",
        ]

        self.templates = {
            "0": [
                (0.50, 0.00),
                (0.25, 0.08),
                (0.08, 0.30),
                (0.00, 0.50),
                (0.08, 0.72),
                (0.25, 0.92),
                (0.50, 1.00),
                (0.75, 0.92),
                (0.92, 0.72),
                (1.00, 0.50),
                (0.92, 0.30),
                (0.75, 0.08),
                (0.50, 0.00),
            ],
            "1": [
                (0.35, 0.18),
                (0.50, 0.00),
                (0.50, 1.00),
            ],
            "2": [
                (0.10, 0.18),
                (0.25, 0.05),
                (0.55, 0.00),
                (0.85, 0.08),
                (1.00, 0.25),
                (0.90, 0.42),
                (0.70, 0.58),
                (0.50, 0.72),
                (0.25, 0.88),
                (0.05, 1.00),
                (1.00, 1.00),
            ],
            "3": [
                (0.10, 0.08),
                (0.40, 0.00),
                (0.75, 0.05),
                (0.95, 0.20),
                (0.75, 0.40),
                (0.50, 0.50),
                (0.75, 0.55),
                (0.95, 0.75),
                (0.75, 0.95),
                (0.40, 1.00),
                (0.10, 0.92),
            ],
            "4": [
                (0.75, 1.00),
                (0.75, 0.00),
                (0.05, 0.65),
                (1.00, 0.65),
            ],
            "5": [
                (0.95, 0.05),
                (0.15, 0.05),
                (0.10, 0.45),
                (0.55, 0.40),
                (0.85, 0.50),
                (0.90, 0.75),
                (0.70, 0.95),
                (0.40, 1.00),
                (0.10, 0.90),
            ],
            "6": [
                (0.85, 0.05),
                (0.55, 0.00),
                (0.30, 0.15),
                (0.12, 0.45),
                (0.10, 0.75),
                (0.30, 0.95),
                (0.60, 1.00),
                (0.85, 0.85),
                (0.82, 0.60),
                (0.60, 0.48),
                (0.25, 0.55),
            ],
            "7": [
                (0.05, 0.05),
                (0.95, 0.05),
                (0.60, 0.40),
                (0.40, 1.00),
            ],
            "8": [
                (0.50, 0.50),
                (0.25, 0.40),
                (0.15, 0.20),
                (0.25, 0.05),
                (0.50, 0.00),
                (0.75, 0.05),
                (0.85, 0.20),
                (0.75, 0.40),
                (0.50, 0.50),
                (0.25, 0.60),
                (0.15, 0.80),
                (0.25, 0.95),
                (0.50, 1.00),
                (0.75, 0.95),
                (0.85, 0.80),
                (0.75, 0.60),
                (0.50, 0.50),
            ],
            "9": [
                (0.75, 0.55),
                (0.45, 0.60),
                (0.20, 0.45),
                (0.15, 0.20),
                (0.30, 0.05),
                (0.60, 0.00),
                (0.85, 0.15),
                (0.90, 0.45),
                (0.75, 0.75),
                (0.55, 1.00),
            ],
            "+": [
                (0.50, 0.05),
                (0.50, 0.95),
                (0.05, 0.50),
                (0.95, 0.50),
            ],
            "-": [
                (0.05, 0.50),
                (0.95, 0.50),
            ],
            "×": [
                (0.10, 0.10),
                (0.90, 0.90),
                (0.50, 0.50),
                (0.90, 0.10),
                (0.10, 0.90),
            ],
            "÷": [
                (0.05, 0.50),
                (0.95, 0.50),
            ],
        }

        self.templates = {
            symbol: self._resample(
                self._normalize_points(points)
            )
            for symbol, points in self.templates.items()
        }

        self.user_templates = {
            symbol: []
            for symbol in self.symbols
        }

        self.load_user_templates()

    def recognize(self, stroke):
        if not stroke or len(stroke) < 8:
            return None

        points = self._convert_points(stroke)

        if not points:
            return None

        normalized = self._normalize_points(points)

        if not normalized:
            return None

        resampled = self._resample(normalized)

        if not resampled:
            return None

        best_symbol = None
        best_score = float("inf")

        for symbol in self.symbols:
            templates = self.user_templates[symbol]

            if templates:
                for template in templates:
                    score = self._distance(
                        resampled,
                        template
                    )

                    if score < best_score:
                        best_score = score
                        best_symbol = symbol

            else:
                template = self.templates[symbol]

                score = self._distance(
                    resampled,
                    template
                )

                if score < best_score:
                    best_score = score
                    best_symbol = symbol

        confidence = self._calculate_confidence(
            best_score
        )

        if confidence < 0.48:
            return None

        return best_symbol

    def add_template(self, symbol, stroke):
        if symbol not in self.symbols:
            raise ValueError(
                f"Unsupported symbol: {symbol}"
            )

        if not stroke:
            return False

        points = self._convert_points(stroke)

        if len(points) < 8:
            return False

        normalized = self._normalize_points(points)

        if not normalized:
            return False

        resampled = self._resample(normalized)

        if not resampled:
            return False

        self.user_templates[symbol].append(
            resampled
        )

        self.save_user_templates()

        return True

    def clear_user_templates(self, symbol=None):
        if symbol is None:
            for current_symbol in self.symbols:
                self.user_templates[current_symbol] = []
        else:
            if symbol not in self.symbols:
                raise ValueError(
                    f"Unsupported symbol: {symbol}"
                )

            self.user_templates[symbol] = []

        self.save_user_templates()

    def get_user_template_count(self, symbol=None):
        if symbol is None:
            return sum(
                len(templates)
                for templates in self.user_templates.values()
            )

        if symbol not in self.symbols:
            return 0

        return len(
            self.user_templates[symbol]
        )

    def save_user_templates(self):
        directory = os.path.dirname(
            self.template_file
        )

        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )

        data = {}

        for symbol, templates in self.user_templates.items():
            data[symbol] = [
                [
                    [float(x), float(y)]
                    for x, y in template
                ]
                for template in templates
            ]

        with open(
            self.template_file,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                data,
                file,
                indent=2
            )

    def load_user_templates(self):
        if not os.path.exists(
            self.template_file
        ):
            return

        try:
            with open(
                self.template_file,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

        except (
            OSError,
            json.JSONDecodeError
        ):
            return

        for symbol in self.symbols:
            templates = data.get(
                symbol,
                []
            )

            if not isinstance(
                templates,
                list
            ):
                continue

            loaded_templates = []

            for template in templates:
                try:
                    points = [
                        (
                            float(point[0]),
                            float(point[1])
                        )
                        for point in template
                    ]

                    if len(points) >= self.sample_count:
                        loaded_templates.append(
                            points[:self.sample_count]
                        )

                except (
                    TypeError,
                    ValueError,
                    IndexError
                ):
                    continue

            self.user_templates[symbol] = (
                loaded_templates
            )

    def _convert_points(self, stroke):
        points = []

        for point in stroke:
            if len(point) < 2:
                continue

            try:
                x = float(point[0])
                y = float(point[1])

            except (
                TypeError,
                ValueError
            ):
                continue

            points.append(
                (x, y)
            )

        return points

    def _normalize_points(self, points):
        if not points:
            return []

        min_x = min(
            point[0]
            for point in points
        )

        max_x = max(
            point[0]
            for point in points
        )

        min_y = min(
            point[1]
            for point in points
        )

        max_y = max(
            point[1]
            for point in points
        )

        width = max_x - min_x
        height = max_y - min_y

        if width == 0 and height == 0:
            return []

        scale = max(
            width,
            height
        )

        normalized = []

        for x, y in points:
            normalized.append(
                (
                    (x - min_x) / scale,
                    (y - min_y) / scale
                )
            )

        return normalized

    def _resample(self, points):
        if not points:
            return []

        if len(points) == 1:
            return points * self.sample_count

        total_length = 0.0

        for index in range(1, len(points)):
            total_length += self._point_distance(
                points[index - 1],
                points[index]
            )

        if total_length == 0:
            return (
                points[:1]
                * self.sample_count
            )

        interval = total_length / (
            self.sample_count - 1
        )

        result = [
            points[0]
        ]

        previous = points[0]
        distance_since_last = 0.0

        index = 1

        while index < len(points):
            current = points[index]

            segment_length = (
                self._point_distance(
                    previous,
                    current
                )
            )

            if (
                distance_since_last
                + segment_length
                >= interval
            ):
                remaining = (
                    interval
                    - distance_since_last
                )

                if segment_length == 0:
                    ratio = 0.0
                else:
                    ratio = (
                        remaining
                        / segment_length
                    )

                new_x = (
                    previous[0]
                    + ratio
                    * (
                        current[0]
                        - previous[0]
                    )
                )

                new_y = (
                    previous[1]
                    + ratio
                    * (
                        current[1]
                        - previous[1]
                    )
                )

                new_point = (
                    new_x,
                    new_y
                )

                result.append(
                    new_point
                )

                previous = new_point
                distance_since_last = 0.0

            else:
                distance_since_last += (
                    segment_length
                )

                previous = current
                index += 1

        while len(result) < self.sample_count:
            result.append(
                points[-1]
            )

        return result[
            :self.sample_count
        ]

    def _point_distance(
        self,
        point_a,
        point_b
    ):
        return math.hypot(
            point_b[0] - point_a[0],
            point_b[1] - point_a[1]
        )

    def _distance(
        self,
        points_a,
        points_b
    ):
        if not points_a or not points_b:
            return float("inf")

        count = min(
            len(points_a),
            len(points_b)
        )

        total = 0.0

        for index in range(count):
            total += self._point_distance(
                points_a[index],
                points_b[index]
            )

        return total / count

    def _calculate_confidence(
        self,
        distance
    ):
        return max(
            0.0,
            1.0 - distance * 2.2
        )