import math
import random

import cv2


class Particle:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.0, 4.0)

        self.velocity_x = math.cos(angle) * speed
        self.velocity_y = math.sin(angle) * speed

        self.life = random.randint(12, 28)
        self.max_life = self.life
        self.radius = random.randint(1, 3)

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

        self.velocity_x *= 0.98
        self.velocity_y *= 0.98

        self.life -= 1

    def is_alive(self):
        return self.life > 0

    def draw(self, frame):
        if not self.is_alive():
            return

        alpha = self.life / self.max_life

        radius = max(1, int(self.radius * alpha))

        color = (
            255,
            int(180 * alpha),
            int(40 + 180 * alpha)
        )

        cv2.circle(
            frame,
            (int(self.x), int(self.y)),
            radius,
            color,
            -1
        )


class ParticleSystem:
    def __init__(self, particle_count=3):
        self.particles = []
        self.particle_count = particle_count

    def spawn(self, x, y):
        for _ in range(self.particle_count):
            self.particles.append(
                Particle(x, y)
            )

    def update(self):
        for particle in self.particles:
            particle.update()

        self.particles = [
            particle
            for particle in self.particles
            if particle.is_alive()
        ]

    def draw(self, frame):
        for particle in self.particles:
            particle.draw(frame)

    def clear(self):
        self.particles.clear()