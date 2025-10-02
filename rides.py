
# -*- coding: utf-8 -*-
"""Rides (junior modular): Ride base + PirateShip + FerrisWheel."""
import math
import matplotlib.patches as patches
from queues import dequeue

class Ride:
    def __init__(self, name, capacity, duration, bbox):
        self.name = name
        self.capacity = capacity
        self.duration = duration
        self.bbox = bbox  # (x, y, w, h)

        self.state = "idle"      # idle|loading|running|unloading
        self.timer = 0
        self.queue = []          # lista de Patron
        self.riders = []         # lista de Patron

    def admit_riders(self):
        """Toma hasta 'capacity' personas desde la cola con dequeue."""
        free = self.capacity - len(self.riders)
        for _ in range(max(0, free)):
            p = dequeue(self)
            if p is None:
                break
            p.board_ride(self)
            self.riders.append(p)

    def finish_cycle(self):
        for p in list(self.riders):
            p.leave_ride()
        self.riders.clear()

    def step_change(self, t):
        if self.state == "idle":
            if self.queue and len(self.riders) < self.capacity:
                self.state = "loading"
                self.timer = 3
        elif self.state == "loading":
            if self.timer > 0:
                self.timer -= 1
            else:
                self.admit_riders()
                if self.riders:
                    self.state = "running"
                    self.timer = self.duration
                else:
                    self.state = "idle"
        elif self.state == "running":
            if self.timer > 0:
                self.timer -= 1
            else:
                self.state = "unloading"
                self.timer = 3
        elif self.state == "unloading":
            if self.timer > 0:
                self.timer -= 1
            else:
                self.finish_cycle()
                self.state = "idle"

    # --- dibujo ---
    def center(self):
        x, y, w, h = self.bbox
        return x + w / 2.0, y + h / 2.0

    def _draw_bbox(self, ax):
        x, y, w, h = self.bbox
        if self.state == "running":
            color = "#f58518"
        elif self.state == "loading":
            color = "#54a24b"
        else:
            color = "#4c78a8"
        rect = patches.Rectangle((x, y), w, h, fill=False, ec=color, lw=2)
        ax.add_patch(rect)

    def plot(self, ax, t):
        """Base: solo dibuja la caja si una subclase no sobreescribe."""
        self._draw_bbox(ax)


class PirateShip(Ride):
    """Barco pirata: se dibuja como un péndulo dentro de la caja."""
    def plot(self, ax, t):
        self._draw_bbox(ax)
        cx, cy = self.center()
        amp = math.radians(50) if self.state == "running" else math.radians(10)
        theta = amp * math.sin(t / 8.0)
        length = min(self.bbox[2], self.bbox[3]) * 0.45
        x2 = cx + length * math.sin(theta)
        y2 = cy - length * math.cos(theta)
        ax.plot([cx, x2], [cy, y2], lw=3)
        ax.plot([x2], [y2], marker="o")
        ax.text(self.bbox[0], self.bbox[1] + self.bbox[3] + 1, self.name, fontsize=8)


class FerrisWheel(Ride):
    """Rueda de la fortuna: círculo con cabinas rotando."""
    def __init__(self, name, capacity, duration, bbox, cabins=8):
        super().__init__(name, capacity, duration, bbox)
        self.cabins = cabins

    def plot(self, ax, t):
        self._draw_bbox(ax)
        cx, cy = self.center()
        radius = min(self.bbox[2], self.bbox[3]) * 0.45
        omega = 0.05 if self.state == "running" else 0.01
        circ = patches.Circle((cx, cy), radius, fill=False, ec="#999")
        ax.add_patch(circ)
        for k in range(self.cabins):
            ang = 2 * math.pi * k / self.cabins + omega * t
            x = cx + radius * math.cos(ang)
            y = cy + radius * math.sin(ang)
            ax.plot([x], [y], marker="s", ms=5)
        ax.text(self.bbox[0], self.bbox[1] + self.bbox[3] + 1, self.name, fontsize=8)
