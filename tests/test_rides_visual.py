"""Quick visual tests for the ride plots."""

import os
import sys
import math
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Ensure the project root is on sys.path when the test is run directly.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

OUTPUT_DIR = Path(__file__).parent / "visual_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def test_pirate_ship_visual():
    """Draw basic pirate ship states."""
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))

    # Simulate different states
    states = [
        ("idle", 0, "Pirate Ship - Idle"),
        ("loading", 0, "Pirate Ship - Loading"),
        ("running", 45, "Pirate Ship - Moving"),
    ]

    for ax, (state, step_counter, title) in zip([ax1, ax2, ax3], states):
        x, y = 5, 3

        # Calculate swing angle
        if state == "running":
            angle = math.sin(step_counter * 0.3) * 20
        else:
            angle = 0

        # Choose colors per state
        if state == "running":
            color = "#8B4513"
            alpha = 1.0
        elif state == "loading":
            color = "#CD853F"
            alpha = 0.9
        else:
            color = "#A0522D"
            alpha = 0.7

        # Draw the ship hull
        ellipse = patches.Ellipse(
            (x, y),
            3,
            1.5,
            angle=angle,
            facecolor=color,
            alpha=alpha,
            edgecolor="black",
            linewidth=2,
        )
        ax.add_patch(ellipse)

        # Draw mast
        mast_x = x + 0.5 * math.cos(math.radians(angle)) if state == "running" else x + 0.5
        mast_y = y
        ax.plot([mast_x, mast_x], [mast_y - 0.5, mast_y + 1.5], "k-", linewidth=3)

        # Flag when running to highlight motion
        if state == "running":
            ax.text(mast_x + 0.2, mast_y + 1.2, "PIRATE", fontsize=10)

        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.set_aspect("equal")

    plt.tight_layout()
    plt.savefig(str(OUTPUT_DIR / "test_pirate_visual.png"), dpi=150, bbox_inches="tight")
    # NOTE: skip plt.show() to avoid FigureCanvasAgg warning during tests


def test_ferris_wheel_visual():
    """Draw basic ferris wheel states."""
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))

    # Simulate different states
    states = [
        ("idle", 0, "Ferris Wheel - Idle"),
        ("loading", 0, "Ferris Wheel - Loading"),
        ("running", 36, "Ferris Wheel - Spinning"),
    ]

    for ax, (state, step_counter, title) in zip([ax1, ax2, ax3], states):
        x, y = 5, 3

        # Calculate rotation
        if state == "running":
            rotation = step_counter * 10
        else:
            rotation = 0

        # Choose colors per state
        if state == "running":
            color = "#FF6347"
            alpha = 1.0
        elif state == "loading":
            color = "#FFA500"
            alpha = 0.9
        else:
            color = "#FF8C00"
            alpha = 0.7

        # Draw main wheel
        wheel = patches.Circle(
            (x, y),
            1.8,
            facecolor=color,
            alpha=alpha,
            edgecolor="darkred",
            linewidth=3,
        )
        ax.add_patch(wheel)

        # Draw spokes
        for i in range(8):
            angle = math.radians(i * 45 + rotation)
            x_end = x + 1.6 * math.cos(angle)
            y_end = y + 1.6 * math.sin(angle)
            ax.plot([x, x_end], [y, y_end], "darkred", linewidth=2)

        # Draw passenger cabins
        for i in range(6):
            angle = math.radians(i * 60 + rotation)
            cab_x = x + 1.4 * math.cos(angle)
            cab_y = y + 1.4 * math.sin(angle)
            cabin = patches.Rectangle(
                (cab_x - 0.15, cab_y - 0.1),
                0.3,
                0.2,
                facecolor="yellow",
                edgecolor="black",
                linewidth=1,
            )
            ax.add_patch(cabin)

        # Label when running to show motion
        if state == "running":
            ax.text(x, y + 2.5, "FERRIS", fontsize=12, ha="center")

        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.set_aspect("equal")

    plt.tight_layout()
    plt.savefig(str(OUTPUT_DIR / "test_ferris_visual.png"), dpi=150, bbox_inches="tight")
    # NOTE: skip plt.show() to avoid FigureCanvasAgg warning during tests
if __name__ == "__main__":
    print("Generating ride visual tests...")
    print("Testing Pirate Ship...")
    test_pirate_ship_visual()
    print("Testing Ferris Wheel...")
    test_ferris_wheel_visual()
    print("Visual tests complete.")
    print(f"Check {OUTPUT_DIR / 'test_pirate_visual.png'} and {OUTPUT_DIR / 'test_ferris_visual.png'}")
