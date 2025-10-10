# -*- coding: utf-8 -*-
"""Specific ride implementations: PirateShip and FerrisWheel."""
from __future__ import annotations

import math

import matplotlib.patches as patches

from adventure.rides.base_ride import Ride
from adventure.rides.ride_visuals import RideVisuals


class PirateShip(Ride):
    """Pirate ship ride with pendulum animation."""

    def __init__(self, name, capacity, duration, bbox):
        super().__init__(name, capacity, duration, bbox, ride_type="pirate")

    def plot(self, ax, step_index):
        self._draw_bbox(ax)
        self._draw_queue(ax)
        self._draw_capacity_info(ax)
        self._draw_pirate_ship_animation(ax, step_index)
        ax.text(
            self.bbox[0],
            self.bbox[1] - 8,
            f"PIRATE {self.name}",
            fontsize=9,
            ha="left",
            weight="bold",
        )

    def _draw_pirate_ship_animation(self, ax, step_index):
        cx, cy = self.center()
        if self.state == "running":
            amplitude = math.radians(50)
            line_color = "#f58518"
        elif self.state in {"loading", "unloading"}:
            amplitude = math.radians(15)
            line_color = "#54a24b" if self.state == "loading" else "#e377c2"
        else:
            amplitude = math.radians(5)
            line_color = "#4c78a8"

        theta = amplitude * math.sin(step_index / 8.0)
        length = min(self.bbox[2], self.bbox[3]) * 0.45
        x2 = cx + length * math.sin(theta)
        y2 = cy - length * math.cos(theta)

        ax.plot([cx, x2], [cy, y2], lw=3, color=line_color)
        ax.plot([x2], [y2], marker="o", ms=8, color=line_color)

    def _draw_bbox(self, ax):
        RideVisuals.draw_bbox(self, ax)

    def _draw_queue(self, ax):
        RideVisuals.draw_queue(self, ax)

    def _draw_capacity_info(self, ax):
        RideVisuals.draw_capacity_info(self, ax)


class FerrisWheel(Ride):
    """Ferris wheel ride with rotating cabins."""

    def __init__(self, name, capacity, duration, bbox, cabins=8):
        super().__init__(name, capacity, duration, bbox, ride_type="ferris")
        self.cabins = cabins

    def plot(self, ax, step_index):
        self._draw_bbox(ax)
        self._draw_queue(ax)
        self._draw_capacity_info(ax)
        self._draw_ferris_wheel_animation(ax, step_index)
        ax.text(
            self.bbox[0],
            self.bbox[1] - 8,
            f"FERRIS {self.name}",
            fontsize=9,
            ha="left",
            weight="bold",
        )

    def _draw_ferris_wheel_animation(self, ax, step_index):
        cx, cy = self.center()
        radius = min(self.bbox[2], self.bbox[3]) * 0.45
        if self.state == "running":
            omega = 0.05
            circle_color = "#f58518"
            cabin_color = "#f58518"
        elif self.state in {"loading", "unloading"}:
            omega = 0.02
            circle_color = "#54a24b" if self.state == "loading" else "#e377c2"
            cabin_color = circle_color
        else:
            omega = 0.005
            circle_color = "#4c78a8"
            cabin_color = "#999999"

        circle = patches.Circle((cx, cy), radius, fill=False, ec=circle_color, lw=2)
        ax.add_patch(circle)

        for index in range(self.cabins):
            angle = 2 * math.pi * index / self.cabins + omega * step_index
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            cabin_size = 6 if len(self.riders) > index else 4
            ax.plot([x], [y], marker="s", ms=cabin_size, color=cabin_color, alpha=0.8)

    def _draw_bbox(self, ax):
        RideVisuals.draw_bbox(self, ax)

    def _draw_queue(self, ax):
        RideVisuals.draw_queue(self, ax)

    def _draw_capacity_info(self, ax):
        RideVisuals.draw_capacity_info(self, ax)


class SpinnerRide(Ride):
    """Spinner ride with rotating arms and pods."""

    def __init__(self, name, capacity, duration, bbox, arms=4):
        super().__init__(name, capacity, duration, bbox, ride_type="spinner")
        self.arms = max(3, arms)

    def plot(self, ax, step_index):
        self._draw_bbox(ax)
        self._draw_queue(ax)
        self._draw_capacity_info(ax)
        self._draw_spinner_animation(ax, step_index)
        ax.text(
            self.bbox[0],
            self.bbox[1] - 8,
            f"SPINNER {self.name}",
            fontsize=9,
            ha="left",
            weight="bold",
        )

    def _draw_spinner_animation(self, ax, step_index):
        cx, cy = self.center()
        radius = min(self.bbox[2], self.bbox[3]) * 0.4
        inner_radius = radius * 0.35
        if self.state == "running":
            omega = 0.12
            arm_color = "#ff9f1c"
            pod_color = "#ff9f1c"
        elif self.state in {"loading", "unloading"}:
            omega = 0.05
            arm_color = "#2ca02c" if self.state == "loading" else "#d62728"
            pod_color = arm_color
        else:
            omega = 0.01
            arm_color = "#4c78a8"
            pod_color = "#999999"

        ax.add_patch(patches.Circle((cx, cy), inner_radius, fill=False, ec=arm_color, lw=2))

        for index in range(self.arms):
            angle = 2 * math.pi * index / self.arms + omega * step_index
            x2 = cx + radius * math.cos(angle)
            y2 = cy + radius * math.sin(angle)
            ax.plot([cx, x2], [cy, y2], lw=2, color=arm_color, alpha=0.8)
            pod_size = 6 if len(self.riders) > index else 5
            ax.plot([x2], [y2], marker="o", ms=pod_size, color=pod_color, alpha=0.9)

    def _draw_bbox(self, ax):
        RideVisuals.draw_bbox(self, ax)

    def _draw_queue(self, ax):
        RideVisuals.draw_queue(self, ax)

    def _draw_capacity_info(self, ax):
        RideVisuals.draw_capacity_info(self, ax)
