# particle.py

from pygame import gfxdraw
from statistics import mean
import random


# CLASSES
# PARTICLES
class BaseParticle:
    def __init__(self, position: tuple or list, velocity: tuple or list, color: int or tuple or list, alpha: int):
        self.position = list(position)
        self.velocity = list(velocity)

        self.progress = 0
        self.twisted_progress = 1 - self.progress

        self.alive = True

        # color
        if isinstance(color, int):
            self.color = [color, color, color, alpha]
        elif isinstance(color, tuple) or isinstance(color, list):
            if len(color) == 3:
                self.color = [color[0], color[1], color[2], alpha]
            else: self.color = list(color)
        self.start_color = self.color
        self.alpha = self.color[3]
        for i in range(len(self.color)):
            self.color[i] = int(self.color[i])

    @staticmethod
    def get_progress(start_size: float or tuple or list, size: float or tuple or list):
        try:
            if isinstance(size, tuple) or isinstance(start_size, list):
                return 1 - (mean(list(size)) / mean(list(start_size)))
            else:
                return 1 - (float(size) / float(start_size))
        except ZeroDivisionError:
            return 0

    def update(self, start_size: float, size: float, delta_time: float = 1, gravity: float = 0):
        # manipulate positions
        self.position[0] += self.velocity[0] * delta_time
        self.position[1] += self.velocity[1] * delta_time
        self.velocity[1] += gravity

        # set color
        self.color = list(self.color)
        if len(self.color) < 4:
            self.color.append(self.alpha)
        else:
            self.color[3] = self.alpha
        for i in range(len(self.color)):
            self.color[i] = int(self.color[i])

        # get progress of particle
        self.progress = self.get_progress(start_size, size)
        self.twisted_progress = 1 - self.progress


class Circle(BaseParticle):
    def __init__(self, position, velocity, size: float, delta_size: float, color, alpha: int = 255, antialiasing: bool = False):
        super().__init__(position, velocity, color, alpha)

        # radius
        self.size = size
        self.start_size = self.size
        self.delta_radius = delta_size

        # antialiasing
        self.antialiasing = antialiasing

    def update(self, start_size: float, size: float, delta_time: float = 1, gravity: float = 0):
        super().update(start_size=start_size, size=size, delta_time=delta_time, gravity=gravity)

        if self.alive: self.size -= self.delta_radius  # decrease radius
        if self.size <= 0: self.alive = False  # check if alive

    def draw(self, surface):
        if self.alive:
            if self.antialiasing:
                gfxdraw.aacircle(surface, int(self.position[0]), int(self.position[1]), int(self.size), self.color)
            gfxdraw.filled_circle(surface, int(self.position[0]), int(self.position[1]), int(self.size), self.color)


class Rect(BaseParticle):
    def __init__(self, position, velocity, size: float or tuple or list, delta_size: float or tuple or list, color, alpha):
        super().__init__(position, velocity, color, alpha)

        # size
        if isinstance(size, float) or isinstance(size, int):
            self.size = [size, size]
        else:
            self.size = list(size)
        self.start_size = self.size
        self.delta_size = delta_size

    def update(self, start_size: float, size: float, delta_time: float = 1, gravity: float = 0):
        super().update(delta_time, gravity)

        # decrease size
        if self.alive:
            if isinstance(self.delta_size, float):
                self.size[0] -= self.delta_size
                self.size[1] -= self.delta_size
            elif isinstance(self.delta_size, tuple) or isinstance(self.delta_size, list):
                self.size[0] -= self.delta_size[0]
                self.size[1] -= self.delta_size[1]

        if self.size[0] <= 0 or self.size[1] <= 0:
            self.alive = False

    def draw(self, surface):
        if self.alive:
            gfxdraw.box(surface, (self.position[0] - self.size[0] / 2, self.position[1] - self.size[1] / 2,
                                  self.size[0], self.size[1]), self.color)


# PARTICLE SYSTEM
class ParticleSystem:
    def __init__(self, remove_particle_if_not_alive: bool = False):
        # options
        self.remove_particle_if_not_alive = remove_particle_if_not_alive

        # particles
        self.particles = []

        self.alive = True

    def create(self, particle: BaseParticle):
        self.particles.append(particle)

    def update(self, delta_time: float = 1, gravity: float = 0):
        random.seed()

        if len(self.particles) > 0: self.alive = True

        removes = []
        if not self.remove_particle_if_not_alive: alive = True

        for particle in self.particles:
            particle.update(start_size=particle.start_size, size=particle.size, delta_time=delta_time, gravity=gravity)
            if self.remove_particle_if_not_alive:
                if not particle.alive:
                    removes.append(particle)

        if self.remove_particle_if_not_alive:
            for i in range(len(removes)):
                self.particles.remove(removes[i])
        else:
            for particle in self.particles:
                if not particle.alive:
                    alive = False
                else:
                    alive = True
                    break
            if not alive:
                self.particles.clear()
                self.alive = False

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)