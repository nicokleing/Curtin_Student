# -*- coding: utf-8 -*-
"""Roller coaster ride with a simple track animation."""
from __future__ import annotations

import math

import matplotlib.patches as patches

from adventure.rides.base_ride import Ride
from adventure.rides.ride_visuals import RideVisuals


class RollerCoaster(Ride):
    """Roller coaster ride with track animation."""

    def __init__(self, name, capacity, duration, bbox):
        super().__init__(name, capacity, duration, bbox, ride_type="coaster")

    def plot(self, ax, step_index):
        self._draw_bbox(ax)
        self._draw_queue(ax)
        self._draw_capacity_info(ax)
        self._draw_coaster_animation(ax, step_index)
        ax.text(
            self.bbox[0],
            self.bbox[1] - 8,
            f"COASTER {self.name}",
            fontsize=9,
            ha="left",
            weight="bold",
        )

    def _draw_coaster_animation(self, ax, step_index):
        x, y, w, h = self.bbox
        track_color = "#2ca02c" if self.state == "running" else "#888888"
        track_rect = patches.Rectangle((x + 0.5, y + 0.5), w - 1, h - 1, fill=False, ec=track_color, lw=2)
        ax.add_patch(track_rect)

        if self.state == "running" and self.riders:
            speed = 0.1 if self.state == "running" else 0.02
            progress = (step_index * speed) % 1.0

            if progress < 0.25:
                train_x = x + 1 + (w - 2) * (progress * 4)
                train_y = y + h - 0.5
            elif progress < 0.5:
                train_x = x + w - 0.5
                train_y = y + h - 1 - (h - 2) * ((progress - 0.25) * 4)
            elif progress < 0.75:
                train_x = x + w - 1 - (w - 2) * ((progress - 0.5) * 4)
                train_y = y + 0.5
            else:
                train_x = x + 0.5
                train_y = y + 1 + (h - 2) * ((progress - 0.75) * 4)

            ax.plot([train_x], [train_y], marker="s", ms=8, color="#ff7f0e", markeredgecolor="black")

            for offset in range(1, min(len(self.riders) // 4 + 1, 3)):
                offset_x = train_x - offset * 0.3 * math.cos(progress * 2 * math.pi)
                offset_y = train_y - offset * 0.3 * math.sin(progress * 2 * math.pi)
                ax.plot([offset_x], [offset_y], marker="s", ms=6, color="#ff7f0e", alpha=0.8)

    def _draw_bbox(self, ax):
        RideVisuals.draw_bbox(self, ax)

    def _draw_queue(self, ax):
        RideVisuals.draw_queue(self, ax)

    def _draw_capacity_info(self, ax):
        RideVisuals.draw_capacity_info(self, ax)
