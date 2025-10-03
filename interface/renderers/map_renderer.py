# -*- coding: utf-8 -*-
"""Renderizador del mapa principal de la simulación."""

import math
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
        """Dibuja una atracción individual con animaciones."""
        x, y = ride.center()
        
        # Determinar tipo de atracción
        ride_type = self._get_ride_type(ride)
        
        # Dibujar según el tipo
        if ride_type == 'pirate':
            self._draw_pirate_ship(ride, x, y)
        elif ride_type == 'ferris':
            self._draw_ferris_wheel(ride, x, y)
        else:
            self._draw_generic_ride(ride, x, y)
        
        # Información de la atracción
        info = f"{ride.name}\n{ride.state}\n{len(ride.riders)}/{ride.capacity}"
        self.ax_map.text(x, y-2.5, info, ha='center', va='top', fontsize=8, 
                        weight='bold', color='white',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))
        
        # Dibujar cola si está presente
        self._draw_ride_queue(ride)
    
    def _get_ride_type(self, ride):
        """Determina el tipo de atracción basado en el tipo y el nombre."""
        # Priorizar el campo ride_type si existe
        if hasattr(ride, 'ride_type'):
            ride_type = ride.ride_type.lower()
            if 'pirate' in ride_type:
                return 'pirate'
            elif 'ferris' in ride_type:
                return 'ferris'
        
        # Fallback al nombre si no hay ride_type
        name_lower = ride.name.lower()
        if 'pirate' in name_lower or 'barco' in name_lower:
            return 'pirate'
        elif 'ferris' in name_lower or 'noria' in name_lower or 'rueda' in name_lower:
            return 'ferris'
        else:
            return 'generic'
    
    def _draw_pirate_ship(self, ride, x, y):
        """Dibuja el barco pirata con animación de balanceo."""
        # Calcular ángulo de balanceo basado en el estado
        if ride.state == 'running':
            # Animación de balanceo - usar el step para crear movimiento
            angle = math.sin(getattr(ride, 'step_counter', 0) * 0.3) * 20  # Balanceo de ±20 grados
        else:
            angle = 0
        
        # Colores según estado
        if ride.state == 'running':
            color = '#8B4513'  # Marrón oscuro para activo
            alpha = 1.0
        elif ride.state == 'loading':
            color = '#CD853F'  # Marrón claro para cargando
            alpha = 0.9
        else:
            color = '#A0522D'  # Marrón medio para inactivo
            alpha = 0.7
        
        # Dibujar el barco como una elipse inclinada
        from matplotlib.transforms import Affine2D
        ellipse = patches.Ellipse((x, y), 3, 1.5, angle=angle, 
                                 facecolor=color, alpha=alpha, 
                                 edgecolor='black', linewidth=2)
        self.ax_map.add_patch(ellipse)
        
        # Dibujar mástil
        mast_x = x + 0.5 * math.cos(math.radians(angle)) if ride.state == 'running' else x + 0.5
        mast_y = y
        self.ax_map.plot([mast_x, mast_x], [mast_y-0.5, mast_y+1.5], 'k-', linewidth=3)
        
        # Bandera pirata si está funcionando
        if ride.state == 'running':
            self.ax_map.text(mast_x+0.2, mast_y+1.2, '🏴‍☠️', fontsize=12)
    
    def _draw_ferris_wheel(self, ride, x, y):
        """Dibuja la rueda de la fortuna con animación de rotación."""
        # Calcular rotación basada en el estado
        if ride.state == 'running':
            rotation = getattr(ride, 'step_counter', 0) * 10  # Rotación continua
        else:
            rotation = 0
        
        # Colores según estado
        if ride.state == 'running':
            color = '#FF6347'  # Rojo tomate para activo
            alpha = 1.0
        elif ride.state == 'loading':
            color = '#FFA500'  # Naranja para cargando  
            alpha = 0.9
        else:
            color = '#FF8C00'  # Naranja oscuro para inactivo
            alpha = 0.7
        
        # Dibujar rueda principal
        wheel = patches.Circle((x, y), 1.8, facecolor=color, alpha=alpha,
                              edgecolor='darkred', linewidth=3)
        self.ax_map.add_patch(wheel)
        
        # Dibujar radios de la rueda
        for i in range(8):  # 8 radios
            angle = math.radians(i * 45 + rotation)
            x_end = x + 1.6 * math.cos(angle)
            y_end = y + 1.6 * math.sin(angle)
            self.ax_map.plot([x, x_end], [y, y_end], 'darkred', linewidth=2)
        
        # Dibujar cabinas de pasajeros
        for i in range(6):  # 6 cabinas
            angle = math.radians(i * 60 + rotation)
            cab_x = x + 1.4 * math.cos(angle)
            cab_y = y + 1.4 * math.sin(angle)
            cabin = patches.Rectangle((cab_x-0.15, cab_y-0.1), 0.3, 0.2,
                                    facecolor='yellow', edgecolor='black', linewidth=1)
            self.ax_map.add_patch(cabin)
        
        # Símbolo de rueda si está funcionando
        if ride.state == 'running':
            self.ax_map.text(x, y+2.5, '🎡', fontsize=16, ha='center')
    
    def _draw_generic_ride(self, ride, x, y):
        """Dibuja una atracción genérica."""
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
        circle = patches.Circle((x, y), 1.5, facecolor='magenta', alpha=alpha, 
                               edgecolor=edge_color, linewidth=edge_width)
        self.ax_map.add_patch(circle)
        
        self.ax_map.text(x, y, '🎢', fontsize=16, ha='center', va='center')
        
    def _draw_ride_queue(self, ride):
        """Dibuja la cola de una atracción si existe."""
        if hasattr(ride, 'queue') and ride.queue:
            queue_positions = [patron.position for patron in ride.queue[:5]]
            if queue_positions:
                queue_x, queue_y = zip(*queue_positions)
                self.ax_map.scatter(queue_x, queue_y, c='orange', s=20, alpha=0.7)