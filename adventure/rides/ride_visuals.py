# -*- coding: utf-8 -*-
"""Ride visualization and rendering helpers."""
from __future__ import annotations

import matplotlib.patches as patches


class RideVisuals:
    """Handle all ride visualization tasks."""

    @staticmethod
    def draw_bbox(ride, ax):
        x, y, w, h = ride.bbox
        state_colors = {
            "idle": "#4c78a8",
            "loading": "#54a24b",
            "running": "#f58518",
            "unloading": "#e377c2",
        }
        color = state_colors.get(ride.state, "#7f7f7f")
        rect = patches.Rectangle((x, y), w, h, fill=False, ec=color, lw=3)
        ax.add_patch(rect)
        state_text = ride.state.upper()
        ax.text(
            x + w / 2,
            y - 2,
            state_text,
            ha="center",
            va="top",
            fontsize=8,
            color=color,
            weight="bold",
        )

    @staticmethod
    def draw_queue(ride, ax):
        if not ride.queue:
            return

        x, y, w, h = ride.bbox
        queue_start_x = x + w + 2
        queue_start_y = y + h / 2

        for index, patron in enumerate(ride.queue):
            patron_x = queue_start_x
            patron_y = queue_start_y + index * 0.8
            patron_color = RideVisuals._get_patron_queue_color(patron)
            ax.plot([patron_x], [patron_y], marker="o", ms=4, color=patron_color, alpha=0.8)
            if index < 10:
                ax.text(
                    patron_x + 0.3,
                    patron_y,
                    f"{index + 1}",
                    fontsize=6,
                    va="center",
                    alpha=0.7,
                )

        if len(ride.queue) > 1:
            queue_end_y = queue_start_y + (len(ride.queue) - 1) * 0.8
            ax.plot(
                [queue_start_x - 0.2, queue_start_x - 0.2],
                [queue_start_y - 0.2, queue_end_y + 0.2],
                "k--",
                alpha=0.3,
                lw=1,
            )

    @staticmethod
    def _get_patron_queue_color(patron):
        if hasattr(patron, "patron_type"):
            type_colors = {
                "adventurer": "#d62728",
                "family": "#2ca02c",
                "impatient": "#ff7f0e",
                "explorer": "#1f77b4",
            }
            return type_colors.get(patron.patron_type.value, "#7f7f7f")
        return "#ff7f0e"

    @staticmethod
    def draw_capacity_info(ride, ax):
        x, y, w, h = ride.bbox
        current_riders = len(ride.riders)
        queue_length = len(ride.queue)
        info_text = f"RIDE {current_riders}/{ride.capacity} | Queue {queue_length}"
        if ride.state in {"loading", "running", "unloading"} and hasattr(
            ride.timer_manager, "timer"
        ):
            if ride.state == "loading":
                info_text += f" | Loading ({ride.timer_manager.timer}s)"
            elif ride.state == "running":
                info_text += f" | RUNNING ({ride.timer_manager.timer}s)"
            elif ride.state == "unloading":
                info_text += f" | Unloading ({ride.timer_manager.timer}s)"

        state_bg_colors = {
            "idle": "lightblue",
            "loading": "lightgreen",
            "running": "orange",
            "unloading": "pink",
        }
        bg_color = state_bg_colors.get(ride.state, "white")
        ax.text(
            x + w / 2,
            y + h + 6,
            info_text,
            ha="center",
            va="bottom",
            fontsize=8,
            bbox=dict(boxstyle="round,pad=0.3", facecolor=bg_color, alpha=0.9, edgecolor="gray"),
        )
