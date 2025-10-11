# -*- coding: utf-8 -*-
"""Mouse event handler."""


class MouseHandler:
    """Handle all mouse events for the controls."""

    def __init__(self, engine, ax_controls, button_renderer):
        self.engine = engine
        self.ax_controls = ax_controls
        self.button_renderer = button_renderer

    def handle_click(self, event):
        """Handle mouse click events."""
        if event.inaxes is not self.ax_controls:
            return

        print(f"Click detected at ({event.xdata}, {event.ydata})")

        clicked = None
        for btn_name, info in self.button_renderer.buttons.items():
            rect = info.get("rect")
            if rect is None:
                continue
            contains, _ = rect.contains(event)
            if contains:
                clicked = btn_name
                break

        if not clicked:
            return

        print(f"Button clicked: {clicked}")
        self._handle_button_action(clicked)
        self.button_renderer.update_button_texts(self.engine)
        if self.ax_controls and self.ax_controls.figure:
            self.ax_controls.figure.canvas.draw_idle()

    def _handle_button_action(self, button_name):
        """Execute the action associated with a button click."""
        actions = {
            "pause": self.engine.toggle_pause,
            "reset": self.engine.reset_simulation,
            "exit": self.engine.exit_simulation,
            "speed1": lambda: self.engine.set_speed(1),
            "speed5": lambda: self.engine.set_speed(5),
            "speed10": lambda: self.engine.set_speed(10),
            "stats": self._toggle_stats,
        }

        action = actions.get(button_name)
        if action is not None:
            action()

    def _toggle_stats(self):
        """Toggle the statistics view (placeholder)."""
        print("Toggle statistics (placeholder functionality)")
