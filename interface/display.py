#!/usr/bin/env python3
"""
Display Manager - Visualization Module (Refactored)
==================================================
Manages all matplotlib visualization using specialized renderers
"""
import matplotlib.pyplot as plt
from .renderers import MapRenderer, StatsRenderer
from .controls import ControlsManager


class DisplayManager:
    """
    Manages all visualization aspects using specialized renderers.
    Uses composition to delegate specific rendering tasks.
    """
    
    def __init__(self, engine):
        """Initialize display manager with simulation engine."""
        self.engine = engine
        self.show_stats = engine.show_stats
        
        # Matplotlib components
        self.fig = None
        self.ax_map = None
        self.ax_stats = None
        self.ax_controls = None
        
        # Specialized renderers
        self.map_renderer = None
        self.stats_renderer = None
        self.controls = None
        
    def setup(self):
        """Setup matplotlib layout and initialize renderers."""
        # Create main figure with layout
        self._create_layout()
        
        # Initialize specialized renderers
        self.map_renderer = MapRenderer(self.ax_map)
        if self.ax_stats:
            self.stats_renderer = StatsRenderer(self.ax_stats)
        
        # Setup controls manager
        self.controls = ControlsManager(self.engine, self.ax_controls, self.fig)
        self.controls.setup()
        
        # Configure window
        self.fig.canvas.manager.set_window_title('AdventureWorld - Visual Controls')
        
        print("Visual controls configured - Click the buttons to control simulation!")
        
    def _create_layout(self):
        """Create matplotlib layout based on stats preference."""
        if self.show_stats:
            self.fig = plt.figure(figsize=(14, 8))
            # Main map (4/5 of height)
            self.ax_map = plt.subplot2grid((5, 2), (0, 0), rowspan=4, colspan=1)
            # Statistics (right side, 4/5 of height)
            self.ax_stats = plt.subplot2grid((5, 2), (0, 1), rowspan=4, colspan=1)
            # Controls (bottom, full width)
            self.ax_controls = plt.subplot2grid((5, 2), (4, 0), rowspan=1, colspan=2)
        else:
            self.fig = plt.figure(figsize=(10, 7))
            # Main map (4/5 of height)
            self.ax_map = plt.subplot2grid((5, 1), (0, 0), rowspan=4, colspan=1)
            self.ax_stats = None
            # Controls (bottom)
            self.ax_controls = plt.subplot2grid((5, 1), (4, 0), rowspan=1, colspan=1)
            
    def update(self, state):
        """Update display using specialized renderers."""
        # Render main map
        if self.map_renderer:
            self.map_renderer.render(state)
        
        # Render statistics if enabled
        if self.stats_renderer and self.show_stats:
            self.stats_renderer.render(state, self.engine)
            
        # Update controls display
        if self.controls:
            self.controls.update_display(state)
            
        # Refresh display
        self.fig.canvas.draw_idle()
        
    def is_window_open(self):
        """Check if matplotlib window is still open."""
        return plt.fignum_exists(self.fig.number) if self.fig else False
        
    def pause_for_frame(self, paused):
        """Pause appropriately for frame rate control."""
        if paused:
            plt.pause(0.1)  # Longer pause when paused to reduce CPU usage
        else:
            plt.pause(0.01)  # Short pause for smooth animation
            
    def set_final_mode(self):
        """Configure display for final mode."""
        # Update title
        self.fig.suptitle('✅ Simulación Completada', fontsize=16, color='green')
        
        # Update controls for final mode
        if self.controls:
            self.controls.set_final_mode()
            
        print("\nSimulation finished - Use OK to close or RESET to restart")
        print("   O cierra la ventana manualmente")
        
    def wait_for_user_action(self):
        """Wait for user to close window or take action."""
        while self.engine.running and self.is_window_open():
            plt.pause(0.1)
            
    def cleanup(self):
        """Clean up matplotlib resources."""
        plt.close('all')