#!/usr/bin/env python3
"""
Display Manager - Rendering Module
===================================
Matplotlib-based display control with specialized renderers.
"""
import time
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import gridspec

matplotlib.rcParams['font.family'] = 'DejaVu Sans'
# NOTE: forcing a standard font keeps matplotlib from whining about missing emoji glyphs.
from .renderers import MapRenderer, StatsRenderer
from .controls import ControlsManager


class DisplayManager:
    """
    Coordinate the visualization pipeline with specialized renderers.
    Uses composition to delegate rendering responsibilities.
    """
    
    def __init__(self, engine):
        """Initialize display manager with simulation engine."""
        self.engine = engine
        self.show_stats = engine.show_stats
        self.kpi_options = {
            'max_history': getattr(engine, 'kpi_buffer_size', 240),
            'warmup': getattr(engine, 'kpi_warmup', 5),
            'refresh_interval': getattr(engine, 'kpi_interval', 0.0),
            'style': getattr(engine, 'kpi_style', 'default')
        }
        
        # Matplotlib components
        self.fig = None
        self.ax_map = None
        self.ax_stats = None
        self.ax_controls = None
        
        # Specialized renderers
        self.map_renderer = None
        self.stats_renderer = None
        self.controls = None
        refresh_hint = float(self.kpi_options.get('refresh_interval', 0.0) or 0.0)
        base_delay = refresh_hint if refresh_hint > 0 else 0.05
        self._min_frame_delay = max(0.01, base_delay)
        self._last_draw = 0.0
        
    def setup(self):
        """Setup matplotlib layout and initialize renderers."""
        # Create main figure with layout
        self._create_layout()
        
        # Initialize specialized renderers
        self.map_renderer = MapRenderer(self.ax_map)
        if self.ax_stats:
            self.stats_renderer = StatsRenderer(self.ax_stats, **self.kpi_options)
        
        # Setup controls manager
        self.controls = ControlsManager(self.engine, self.ax_controls, self.fig)
        self.controls.setup()
        
        # Configure window
        if self.fig and self.fig.canvas:
            manager = getattr(self.fig.canvas, "manager", None)
            if manager:
                manager.set_window_title('AdventureWorld - Visual Controls')
        
        print("Visual controls configured - Click the buttons to control simulation!")
        
    def _create_layout(self):
        """Create matplotlib layout based on stats preference."""
        if self.show_stats:
            self.fig = plt.figure(figsize=(14, 8))
            gs = self.fig.add_gridspec(5, 2, height_ratios=[2.5, 2.5, 2.5, 2.5, 1.0],
                                        width_ratios=[3.0, 2.0], wspace=0.4, hspace=0.6)

            # Main map uses left column, top four rows
            self.ax_map = self.fig.add_subplot(gs[:4, 0])

            # Statistics column split into three mini-axes
            stats_spec = gs[:4, 1].subgridspec(3, 1, hspace=0.4)
            self.ax_stats = [self.fig.add_subplot(stats_spec[i, 0]) for i in range(3)]

            # Controls span bottom row across both columns
            self.ax_controls = self.fig.add_subplot(gs[4, :])
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
        if self.fig and self.fig.canvas:
            self.fig.canvas.draw_idle()
        self._last_draw = time.monotonic()
        
    def is_window_open(self):
        """Check if matplotlib window is still open."""
        return plt.fignum_exists(self.fig.number) if self.fig else False
        
    def pause_for_frame(self, paused):
        """Pause appropriately for frame rate control."""
        if paused:
            plt.pause(max(0.1, self._min_frame_delay))  # Longer pause when paused to reduce CPU usage
        else:
            plt.pause(self._min_frame_delay)
            
    def set_final_mode(self):
        """Configure display for final mode."""
        # Update title
        if self.fig:
            self.fig.suptitle('Simulation Complete', fontsize=16, color='green')
        
        # Update controls for final mode
        if self.controls:
            self.controls.set_final_mode()
            
        print("\nSimulation finished - Use OK to close or RESET to restart")
        print("   Or close the window manually")
        
    def wait_for_user_action(self):
        """Wait for user to close window or take action."""
        while self.engine.running and self.is_window_open():
            plt.pause(0.1)
            
    def cleanup(self):
        """Clean up matplotlib resources."""
        try:
            plt.close('all')
        except Exception:
            # NOTE: TkAgg can raise TclError if window already destroyed by OS.
            pass
