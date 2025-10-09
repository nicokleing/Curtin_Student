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
        if event.inaxes != self.ax_controls:
            return
            
        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return
            
        print(f"Click detected at ({x:.2f}, {y:.2f})")
        
        # Check which button was clicked
        for btn_name in self.button_renderer.buttons:
            area = self.button_renderer.get_button_area(btn_name)
            if area:
                x1, x2, y1, y2 = area
                if x1 <= x <= x2 and y1 <= y <= y2:
                    print(f"Button clicked: {btn_name}")
                    self._handle_button_action(btn_name)
                    break
                    
    def _handle_button_action(self, button_name):
        """Execute the action associated with a button click."""
        actions = {
            'pause': self.engine.toggle_pause,
            'reset': self.engine.reset_simulation,
            'exit': self.engine.exit_simulation,
            'speed1': lambda: self.engine.set_speed(1),
            'speed5': lambda: self.engine.set_speed(5),
            'speed10': lambda: self.engine.set_speed(10),
            'stats': self._toggle_stats
        }
        
        if button_name in actions:
            actions[button_name]()
            
    def _toggle_stats(self):
        """Toggle the statistics view (placeholder)."""
        print("Toggle statistics (placeholder functionality)")
