"""Small harness to test ButtonRenderer without opening a window."""

from __future__ import annotations

import matplotlib

# Headless backend for CI
matplotlib.use("Agg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backend_bases import MouseEvent

from interface.renderers.button_renderer import ButtonRenderer


class DummyEngine:
    """Minimal engine stub for button tests."""

    def __init__(self, show_stats: bool = True):
        self.paused: bool = False
        self.speed_multiplier: int = 1
        self.show_stats: bool = show_stats
        self.reset_called: bool = False
        self.request_exit: bool = False

    def set_speed_multiplier(self, m: int):
        self.speed_multiplier = int(m)

    def reset(self):
        self.reset_called = True
        self.paused = False
        self.speed_multiplier = 1

    def toggle_stats(self):
        self.show_stats = not self.show_stats


class ButtonUITestRig:
    """Builds canvas + controls axes and dispatches synthetic clicks."""

    def __init__(self, size_hint: str = "medium", show_stats: bool = True):
        self.engine = DummyEngine(show_stats=show_stats)
        self.fig = Figure(figsize=(8, 3), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_axes((0.0, 0.0, 1.0, 1.0))
        self.renderer = ButtonRenderer(self.ax, size_hint=size_hint)
        self.layout()

    def layout(self):
        self.renderer.create_layout(self.engine)
        self.renderer.update_button_texts(self.engine)
        self.canvas.draw()

    def _button_center_pixels(self, name: str):
        info = self.renderer.buttons[name]
        cx, cy = info["text_pos"]  # axes coords (0..1)
        xpx, ypx = self.ax.transAxes.transform((cx, cy))
        return float(xpx), float(ypx)

    def click_raw_pixels(self, xpx: float, ypx: float) -> bool:
        """Send a synthetic click at raw pixel coords within the canvas."""
        evt = MouseEvent("button_press_event", self.canvas, int(xpx), int(ypx), button="down")
        evt.inaxes = self.ax
        for bname, info in self.renderer.buttons.items():
            rect = info["rect"]
            inside, _ = rect.contains(evt)
            if inside:
                # route through public click for consistent dispatch
                return self.click(bname)
        return False

    def click(self, name: str) -> bool:
        if name not in self.renderer.buttons:
            raise KeyError(f"button {name} not found")
        xpx, ypx = self._button_center_pixels(name)
        evt = MouseEvent("button_press_event", self.canvas, int(xpx), int(ypx), button="down")
        evt.inaxes = self.ax

        clicked = None
        for bname, info in self.renderer.buttons.items():
            rect = info["rect"]
            inside, _ = rect.contains(evt)
            if inside:
                clicked = bname
                break
        if not clicked:
            return False

        # Emulate dispatch (keep it minimal and in sync with labels)
        if clicked == "pause":
            self.engine.paused = not self.engine.paused
        elif clicked == "reset":
            self.engine.reset()
        elif clicked == "exit":
            self.engine.request_exit = True
        elif clicked in ("speed1", "speed5", "speed10"):
            m = 1 if clicked == "speed1" else 5 if clicked == "speed5" else 10
            self.engine.set_speed_multiplier(m)
        elif clicked == "stats":
            self.engine.toggle_stats()

        self.renderer.update_button_texts(self.engine)
        self.canvas.draw()
        return True

    def labels(self):
        return [t.get_text() for t in self.ax.texts]

    def button_bounds_pixels(self, name: str):
        """Return (x0, y0, x1, y1) bounds for a button rectangle in pixel coords."""
        if name not in self.renderer.buttons:
            raise KeyError(f"button {name} not found")
        rect = self.renderer.buttons[name]["rect"]
        bbox = rect.get_window_extent(self.canvas.get_renderer())
        return float(bbox.x0), float(bbox.y0), float(bbox.x1), float(bbox.y1)

    def resize_and_relayout(self, w: float = 9.0, h: float = 3.0):
        self.fig.set_size_inches(w, h)
        self.canvas.draw()
        # trigger the renderer's resize logic
        self.renderer._on_resize(None)
        self.canvas.draw()

    def has_button(self, name: str) -> bool:
        return name in self.renderer.buttons
