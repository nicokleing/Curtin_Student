
# -*- coding: utf-8 -*-
"""
Patrons (personas) – versión junior modular
- Estados: spawning → roaming → queueing → riding → leaving → left
- Caminan hacia objetivo (punto libre o ride cercano con menor cola)
"""
import math
import random

class Patron:
    def __init__(self, name, spawns, exits, terrain):
        self.name = name
        self.spawns = spawns
        self.exits = exits
        self.terrain = terrain

        self.state = "spawning"
        self.position = (0.0, 0.0)
        self.target = None
        self.timer = 5      # no se mueve 5 pasos
        self.current_ride = None
        self.speed = 1.2

    def _choose_target(self, rides):
        if (not rides) or (random.random() < 0.5):
            self.target = self.terrain.random_free_point()
            return
        # ride con menos cola
        best = None
        best_q = None
        for r in rides:
            q = len(r.queue)
            if best_q is None or q < best_q:
                best_q = q
                best = r
        if best is not None:
            x, y, w, h = best.bbox
            self.target = (x + w / 2.0, y + h + 1.5)
        else:
            self.target = self.terrain.random_free_point()

    def _at_target(self):
        if self.target is None:
            return True
        dx = self.target[0] - self.position[0]
        dy = self.target[1] - self.position[1]
        return dx * dx + dy * dy < 0.9

    def _step_towards(self):
        if self.target is None:
            return
        px, py = self.position
        tx, ty = self.target
        vx = tx - px
        vy = ty - py
        dist = math.hypot(vx, vy)
        if dist < 1e-6:
            return
        ux = vx / dist
        uy = vy / dist
        nx = px + ux * self.speed
        ny = py + uy * self.speed
        if self.terrain.is_free_line((px, py), (nx, ny)):
            self.position = (nx, ny)
        else:
            # pequeño rodeo
            angle = random.choice([-1, 1]) * math.pi / 6
            rx = ux * math.cos(angle) - uy * math.sin(angle)
            ry = ux * math.sin(angle) + uy * math.cos(angle)
            nx = px + rx * self.speed
            ny = py + ry * self.speed
            if self.terrain.is_free_point((nx, ny)):
                self.position = (nx, ny)

    def board_ride(self, ride):
        self.state = "riding"
        self.current_ride = ride
        self.target = None

    def leave_ride(self):
        self.current_ride = None
        if random.random() < 0.15:
            self.state = "leaving"
            self.target = random.choice(self.exits)
        else:
            self.state = "roaming"
            self._choose_target([])

    def step_change(self, t, rides):
        if self.state == "spawning":
            if self.timer > 0:
                self.timer -= 1
            else:
                self.position = random.choice(self.spawns)
                self.state = "roaming"
                self._choose_target(rides)
            return

        if self.state == "left":
            return

        if self.state == "riding":
            return

        if self.state == "queueing":
            return

        if self._at_target():
            if self.state == "leaving":
                self.state = "left"
                return
            # ¿hay ride cerca?
            near = []
            for r in rides:
                if self.terrain.near_bbox(self.position, r.bbox, tol=1.2):
                    near.append(r)
            if near:
                best = None
                best_q = None
                for r in near:
                    q = len(r.queue)
                    if best_q is None or q < best_q:
                        best_q = q
                        best = r
                best.queue.append(self)
                self.state = "queueing"
                return
            # elegir nuevo objetivo
            self._choose_target(rides)
        else:
            self._step_towards()

    def plot(self, ax):
        if self.state == "left":
            return
        colors = {
            "roaming": "#1f77b4",
            "queueing": "#ff7f0e",
            "riding": "#2ca02c",
            "leaving": "#d62728",
            "spawning": "#9467bd",
        }
        color = colors.get(self.state, "#7f7f7f")
        ax.plot([self.position[0]], [self.position[1]], marker=".", ms=6, color=color)
