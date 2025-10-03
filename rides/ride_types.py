# -*- coding: utf-8 -*-
"""Implementaciones específicas de atracciones: PirateShip y FerrisWheel."""

import math
import matplotlib.patches as patches
from .base_ride import Ride
from .ride_visuals import RideVisuals

class PirateShip(Ride):
    """Pirate ship ride with pendulum motion animation."""
    
    def __init__(self, name, capacity, duration, bbox):
        super().__init__(name, capacity, duration, bbox, ride_type="pirate")
        
    def plot(self, ax, t):
        """Visualización mejorada con cola y estados."""
        # Dibujar base (bbox, cola, capacidad)
        self._draw_bbox(ax)
        self._draw_queue(ax)
        self._draw_capacity_info(ax)
        
        # Dibujar péndulo específico del barco pirata
        self._draw_pirate_ship_animation(ax, t)
        
        # Nombre de la atracción
        ax.text(self.bbox[0], self.bbox[1] - 8, f"PIRATE {self.name}", 
               fontsize=9, ha='left', weight='bold')

    def _draw_pirate_ship_animation(self, ax, t):
        """Dibuja la animación específica del barco pirata."""
        cx, cy = self.center()
        
        # Animación diferente según estado
        if self.state == "running":
            amp = math.radians(50)  # Movimiento amplio cuando funciona
            line_color = "#f58518"
        elif self.state == "loading" or self.state == "unloading":
            amp = math.radians(15)  # Movimiento suave al cargar/descargar
            line_color = "#54a24b" if self.state == "loading" else "#e377c2"
        else:
            amp = math.radians(5)   # Movimiento mínimo cuando está idle
            line_color = "#4c78a8"
            
        theta = amp * math.sin(t / 8.0)
        length = min(self.bbox[2], self.bbox[3]) * 0.45
        x2 = cx + length * math.sin(theta)
        y2 = cy - length * math.cos(theta)
        
        # Dibujar péndulo con color según estado
        ax.plot([cx, x2], [cy, y2], lw=3, color=line_color)
        ax.plot([x2], [y2], marker="o", ms=8, color=line_color)

    def _draw_bbox(self, ax):
        """Dibuja el área base de la atracción."""
        RideVisuals.draw_bbox(self, ax)
        
    def _draw_queue(self, ax):
        """Dibuja la cola visual."""
        RideVisuals.draw_queue(self, ax)
        
    def _draw_capacity_info(self, ax):
        """Dibuja información de capacidad."""
        RideVisuals.draw_capacity_info(self, ax)


class FerrisWheel(Ride):
    """Ferris wheel ride with rotating cabins."""
    
    def __init__(self, name, capacity, duration, bbox, cabins=8):
        super().__init__(name, capacity, duration, bbox, ride_type="ferris")
        self.cabins = cabins

    def plot(self, ax, t):
        """Visualización mejorada con cola y estados."""
        # Dibujar base (bbox, cola, capacidad)
        self._draw_bbox(ax)
        self._draw_queue(ax)
        self._draw_capacity_info(ax)
        
        # Dibujar noria específica
        self._draw_ferris_wheel_animation(ax, t)
        
        # Nombre de la atracción  
        ax.text(self.bbox[0], self.bbox[1] - 8, f"FERRIS {self.name}", 
               fontsize=9, ha='left', weight='bold')

    def _draw_ferris_wheel_animation(self, ax, t):
        """Dibuja la animación específica de la noria."""
        cx, cy = self.center()
        radius = min(self.bbox[2], self.bbox[3]) * 0.45
        
        # Velocidad y color según estado
        if self.state == "running":
            omega = 0.05      # Velocidad normal
            circle_color = "#f58518"
            cabin_color = "#f58518"
        elif self.state == "loading" or self.state == "unloading":
            omega = 0.02      # Velocidad lenta para cargar/descargar
            circle_color = "#54a24b" if self.state == "loading" else "#e377c2"
            cabin_color = circle_color
        else:
            omega = 0.005     # Velocidad muy lenta cuando idle
            circle_color = "#4c78a8"
            cabin_color = "#999999"
            
        # Dibujar círculo principal con color según estado
        circ = patches.Circle((cx, cy), radius, fill=False, 
                             ec=circle_color, lw=2)
        ax.add_patch(circ)
        
        # Dibujar cabinas
        for k in range(self.cabins):
            ang = 2 * math.pi * k / self.cabins + omega * t
            x = cx + radius * math.cos(ang)
            y = cy + radius * math.sin(ang)
            
            # Cabinas más grandes si hay pasajeros
            cabin_size = 6 if len(self.riders) > k else 4
            ax.plot([x], [y], marker="s", ms=cabin_size, 
                   color=cabin_color, alpha=0.8)

    def _draw_bbox(self, ax):
        """Dibuja el área base de la atracción."""
        RideVisuals.draw_bbox(self, ax)
        
    def _draw_queue(self, ax):
        """Dibuja la cola visual."""
        RideVisuals.draw_queue(self, ax)
        
    def _draw_capacity_info(self, ax):
        """Dibuja información de capacidad."""
        RideVisuals.draw_capacity_info(self, ax)