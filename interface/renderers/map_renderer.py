# -*- coding: utf-8 -*-
"""Renderizador del mapa principal de la simulación."""

import numpy as np
import matplotlib.patches as patches

class MapRenderer:
    """Renderiza el mapa principal con terreno, visitantes y atracciones."""
    
    def __init__(self, ax_map):
        self.ax_map = ax_map
        
    def render(self, state):
        """Renderiza el mapa completo."""
        terrain = state['terrain']
        patrons = state['patrons']
        rides = state['rides']
        time = state['time']
        step = state['step']
        paused = state['paused']
        speed = state['speed']
        
        # Clear and setup map bounds
        self.ax_map.clear()
        self.ax_map.set_xlim(0, terrain.width)
        self.ax_map.set_ylim(0, terrain.height)
        
        # Draw terrain background
        self._draw_terrain(terrain)
        
        # Draw simulation elements (patrons first, then rides for visibility)
        self._draw_patrons(patrons)
        self._draw_rides(rides)
        
        # Update title with current status
        status = "PAUSADO" if paused else f"EJECUTANDO A {speed}x"
        self.ax_map.set_title(f'🎢 AdventureWorld - Paso: {step} | {status}')
        
    def _draw_terrain(self, terrain):
        """Dibuja el fondo del terreno."""
        terrain_map = np.array(terrain.grid)
        self.ax_map.imshow(terrain_map, cmap='terrain', alpha=0.5, 
                          extent=[0, terrain.width, 0, terrain.height], origin='lower')
    
    def _draw_patrons(self, patrons):
        """Dibuja todos los visitantes."""
        for patron in patrons:
            self._draw_patron(patron)
            
    def _draw_patron(self, patron):
        """Dibuja un visitante individual."""
        type_colors = {
            'aventurero': 'red',
            'familiar': 'blue', 
            'impaciente': 'orange',
            'explorador': 'green'
        }
        
        color = type_colors.get(patron.patron_type.value, 'gray')
        x, y = patron.position
        self.ax_map.scatter(x, y, c=color, s=15, alpha=0.8)
        
    def _draw_rides(self, rides):
        """Dibuja todas las atracciones."""
        for ride in rides:
            self._draw_ride(ride)
            
    def _draw_ride(self, ride):
        """Dibuja una atracción individual."""
        x, y = ride.center()
        
        # Determinar color y símbolo por tipo de atracción
        if 'pirate' in ride.name.lower():
            base_color = 'purple'
            symbol = '🏴‍☠️'
        elif 'ferris' in ride.name.lower() or 'noria' in ride.name.lower():
            base_color = 'cyan' 
            symbol = '🎡'
        else:
            base_color = 'magenta'
            symbol = '🎢'
            
        # Modificar apariencia según estado
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
        
        # Dibujar atracción como círculo grande
        circle = patches.Circle((x, y), 1.5, facecolor=base_color, alpha=alpha, 
                               edgecolor=edge_color, linewidth=edge_width)
        self.ax_map.add_patch(circle)
        
        # Información de la atracción
        info = f"{ride.name}\n{ride.state}\n{len(ride.riders)}/{ride.capacity}"
        self.ax_map.text(x, y-2.5, info, ha='center', va='top', fontsize=8, 
                        weight='bold', color='white',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))
        
        # Dibujar cola si está presente
        self._draw_ride_queue(ride)
        
    def _draw_ride_queue(self, ride):
        """Dibuja la cola de una atracción si existe."""
        if hasattr(ride, 'queue') and ride.queue:
            queue_positions = [patron.position for patron in ride.queue[:5]]
            if queue_positions:
                queue_x, queue_y = zip(*queue_positions)
                self.ax_map.scatter(queue_x, queue_y, c='orange', s=20, alpha=0.7)