# -*- coding: utf-8 -*-
"""Keyboard event handler."""

class KeyboardHandler:
    """Handle all keyboard events for the controls."""
    
    def __init__(self, engine):
        self.engine = engine
        
    def handle_key_press(self, event):
        """Handle a key press event."""
        key_actions = {
            ' ': self.engine.toggle_pause,    # Spacebar
            '1': lambda: self.engine.set_speed(1),
            '5': lambda: self.engine.set_speed(5),
            '0': lambda: self.engine.set_speed(10),
            'r': self.engine.reset_simulation,
            'q': self.engine.exit_simulation,
            'h': self._show_controls_help
        }
        
        if event.key in key_actions:
            print(f"Key pressed: {event.key}")
            key_actions[event.key]()
            
    def _show_controls_help(self):
        """Show a keyboard and mouse help summary."""
        print("\n" + "="*60)
        print("SIMULATION CONTROLS")
        print("="*60)
        print("MOUSE CONTROLS:")
        print("   PAUSE/PLAY - Pause/Resume simulation")
        print("   1x  - Normal speed")
        print("   5x  - Fast speed") 
        print("   10x - Very fast speed")
        print("   STATS - Toggle statistics")
        print("   RESET - Restart simulation")
        print("   EXIT  - Exit")
        print()
        print("KEYBOARD CONTROLS (alternative):")
        print("   SPACE    - Pause/Resume")
        print("   1,5,0    - Change speed")
        print("   R        - Restart")
        print("   Q        - Quit")
        print("   H        - Show this help")
        print("="*60)
