#!/usr/bin/env python3
"""
Controls Manager - User Input Module (Refactored)
================================================
Handles all user controls using specialized event handlers and renderers
"""
from .events import MouseHandler, KeyboardHandler
from .renderers import ButtonRenderer


class ControlsManager:
    """
    Manages all user interaction controls using specialized handlers.
    Uses composition to separate rendering and event handling.
    """
    
    def __init__(self, engine, ax_controls, fig):
        """Initialize controls manager."""
        self.engine = engine
        self.ax_controls = ax_controls
        self.fig = fig
        
        # Specialized handlers
        self.button_renderer = ButtonRenderer(ax_controls)
        self.mouse_handler = MouseHandler(engine, ax_controls, self.button_renderer)
        self.keyboard_handler = KeyboardHandler(engine)
        
    def setup(self):
        """Setup visual controls and event handlers."""
        # Create button layout
        self.button_renderer.create_layout(self.engine)
        
        # Connect event handlers
        self._connect_events()
        
        # Show initial controls help
        self.keyboard_handler._show_controls_help()
        
        # Update initial button states
        self.button_renderer.update_button_texts(self.engine)
        
    def _connect_events(self):
        """Connect mouse and keyboard event handlers."""
        if self.fig:
            self.fig.canvas.mpl_connect('button_press_event', self._on_click)
            self.fig.canvas.mpl_connect('key_press_event', self._on_key_press)
            
    def _on_click(self, event):
        """Delegate mouse click events to mouse handler."""
        self.mouse_handler.handle_click(event)
        
        # Update button display after action
        self.button_renderer.update_button_texts(self.engine)
        if self.fig:
            self.fig.canvas.draw_idle()
            
    def _on_key_press(self, event):
        """Delegate keyboard events to keyboard handler."""
        self.keyboard_handler.handle_key_press(event)
        
        # Update button display after action
        self.button_renderer.update_button_texts(self.engine)
        if self.fig:
            self.fig.canvas.draw_idle()
            
    def update_display(self, state):
        """Update control display based on simulation state."""
        self.button_renderer.update_button_texts(self.engine)
        
    def set_final_mode(self):
        """Set controls for final mode."""
        # Update button appearance for final mode
        self.button_renderer.set_final_mode()
        
        # Update button texts
        self.button_renderer.update_button_texts(self.engine)
        
        # Force refresh
        if self.fig:
            self.fig.canvas.draw_idle()