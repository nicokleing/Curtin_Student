#!/usr/bin/env python3
"""
Display Manager - Visualization Module  
====================================
Handles all matplotlib visualization, UI layout, and display management
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class DisplayManager:
    """
    Manages all visualization aspects of the simulation
    Handles matplotlib layout, drawing, and display updates
    """
    
    def __init__(self, engine):
        """Initialize display manager with simulation engine"""
        self.engine = engine
        self.show_stats = engine.show_stats
        
        # Matplotlib components
        self.fig = None
        self.ax_map = None
        self.ax_stats = None
        self.ax_controls = None
        
        # Controls manager
        self.controls = None
        
    def setup(self):
        """Setup matplotlib layout and controls"""
        # Create main figure with layout
        self._create_layout()
        
        # Setup controls - import here to avoid circular imports
        from interface.controls import ControlsManager
        self.controls = ControlsManager(self.engine, self.ax_controls, self.fig)
        self.controls.setup()
        
        # Configure window
        self.fig.canvas.manager.set_window_title('🎮 AdventureWorld - Controles Visuales')
        
        print("🎮 Controles visuales configurados - ¡Haz click en los botones!")
        
    def _create_layout(self):
        """Create matplotlib layout based on stats preference"""
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
        """Update display with current simulation state"""
        # Clear main map
        self.ax_map.clear()
        
        # Draw main simulation
        self._draw_map(state)
        
        # Update statistics if enabled
        if self.show_stats and self.ax_stats:
            self._draw_stats(state)
            
        # Update controls display
        if self.controls:
            self.controls.update_display(state)
            
        # Refresh display
        self.fig.canvas.draw_idle()
        
    def _draw_map(self, state):
        """Draw main simulation map"""
        terrain = state['terrain']
        patrons = state['patrons']
        rides = state['rides']
        time = state['time']
        step = state['step']
        paused = state['paused']
        speed = state['speed']
        
        # Setup map bounds
        self.ax_map.set_xlim(0, terrain.width)
        self.ax_map.set_ylim(0, terrain.height)
        
        # Draw terrain background
        terrain_map = np.array(terrain.grid)
        self.ax_map.imshow(terrain_map, cmap='terrain', alpha=0.5, 
                          extent=[0, terrain.width, 0, terrain.height], origin='lower')
        
        # Draw patrons first (background)
        for patron in patrons:
            self._draw_patron(patron)
            
        # Draw rides on top (foreground) - more visible
        for ride in rides:
            self._draw_ride(ride)
            
        # Title with current status
        status = "PAUSADO" if paused else f"EJECUTANDO A {speed}x"
        self.ax_map.set_title(f'🎢 AdventureWorld - Paso: {step} | {status}')
        
    def _draw_ride(self, ride):
        """Draw a single ride on the map"""
        x, y = ride.center()
        
        # Color based on state and ride type
        if 'pirate' in ride.name.lower():
            base_color = 'purple'
            symbol = '🏴‍☠️'
        elif 'ferris' in ride.name.lower() or 'noria' in ride.name.lower():
            base_color = 'cyan' 
            symbol = '🎡'
        else:
            base_color = 'magenta'
            symbol = '🎢'
            
        # Modify color based on state
        if ride.state == 'running':
            alpha = 1.0
            edge_color = 'red'
            edge_width = 3
        elif ride.state == 'loading':
            alpha = 0.8
            edge_color = 'orange'
            edge_width = 2
        else:  # idle
            alpha = 0.6
            edge_color = 'black' 
            edge_width = 1
        
        # Draw ride as large circle
        circle = patches.Circle((x, y), 1.5, facecolor=base_color, alpha=alpha, 
                               edgecolor=edge_color, linewidth=edge_width)
        self.ax_map.add_patch(circle)
        
        # Add ride name and info
        info = f"{ride.name}\n{ride.state}\n{len(ride.riders)}/{ride.capacity}"
        self.ax_map.text(x, y-2.5, info, ha='center', va='top', fontsize=8, 
                        weight='bold', color='white',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))
        
        # Add ride information
        info = f"{ride.name}\n{ride.state}\n{len(ride.riders)}/{ride.capacity}"
        self.ax_map.text(x, y-5, info, ha='center', va='top', fontsize=8, weight='bold')
        
        # Draw queue if present
        if hasattr(ride, 'queue') and ride.queue:
            queue_positions = [patron.position for patron in ride.queue[:5]]
            if queue_positions:
                queue_x, queue_y = zip(*queue_positions)
                self.ax_map.scatter(queue_x, queue_y, c='orange', s=20, alpha=0.7)
                
    def _draw_patron(self, patron):
        """Draw a single patron on the map"""
        # Color by patron type
        type_colors = {
            'aventurero': 'red',
            'familiar': 'blue', 
            'impaciente': 'orange',
            'explorador': 'green'
        }
        
        color = type_colors.get(patron.patron_type.value, 'gray')
        x, y = patron.position
        self.ax_map.scatter(x, y, c=color, s=15, alpha=0.8)
        
    def _draw_stats(self, state):
        """Draw statistics panel"""
        if not self.ax_stats:
            return
            
        self.ax_stats.clear()
        
        stats = state['statistics']
        
        # Current statistics
        stats_text = [
            f"👥 En atracciones: {stats['riders_now']}",
            f"⏳ En cola: {stats['queued_now']}", 
            f"🚪 Salieron: {stats['departed_total']}",
            f"🚶 Abandonos: {stats['abandoned_now']}",
            f"📊 Paso: {state['step']}"
        ]
        
        # Display as text
        for i, text in enumerate(stats_text):
            self.ax_stats.text(0.1, 0.8-i*0.15, text, fontsize=12, 
                             transform=self.ax_stats.transAxes)
            
        # Optional: Add simple line plots if there's history
        engine_stats = self.engine
        if len(engine_stats.riders_now) > 1:
            # Mini line plot of riders over time
            steps = range(len(engine_stats.riders_now))
            self.ax_stats.plot(steps, engine_stats.riders_now, 'r-', alpha=0.7, linewidth=2)
            self.ax_stats.set_ylabel('Riders', color='red')
            
        self.ax_stats.set_title('📊 Estadísticas en Vivo')
        
    def is_window_open(self):
        """Check if matplotlib window is still open"""
        return plt.fignum_exists(self.fig.number) if self.fig else False
        
    def pause_for_frame(self, paused):
        """Pause appropriately for frame rate control"""
        if paused:
            plt.pause(0.1)  # Longer pause when paused to reduce CPU usage
        else:
            plt.pause(0.01)  # Short pause for smooth animation
            
    def set_final_mode(self):
        """Configure display for final mode"""
        # Update title
        self.fig.suptitle('✅ Simulación Completada', fontsize=16, color='green')
        
        # Update controls for final mode
        if self.controls:
            self.controls.set_final_mode()
            
        print("\n🎮 Simulación finalizada - Usa ✅ OK para cerrar o 🔄 RESET para reiniciar")
        print("   O cierra la ventana manualmente")
        
    def wait_for_user_action(self):
        """Wait for user to close window or take action"""
        while self.engine.running and self.is_window_open():
            plt.pause(0.1)
            
    def cleanup(self):
        """Clean up matplotlib resources"""
        plt.close('all')