class StrokeManager:
    def __init__(self):
        self.points = []

    def begin(self, point):
        self.points = [point]

    def add_point(self, point):
        self.points.append(point)

    def is_empty(self):
        return len(self.points) == 0

    def finish(self):
        finished_stroke = self.points.copy()
        self.points.clear()
        return finished_stroke

    def clear(self):
        self.points.clear()

    def get_points(self):
        return self.points.copy()

    def point_count(self):
        return len(self.points)