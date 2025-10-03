# -*- coding: utf-8 -*-
"""Ejemplo de nueva atracción: Montaña Rusa (Roller Coaster)."""

import math
import matplotlib.patches as patches
from rides.base_ride import Ride
from rides.ride_visuals import RideVisuals

class RollerCoaster(Ride):
    """Roller coaster ride with track animation."""
    
    def __init__(self, name, capacity, duration, bbox):
        super().__init__(name, capacity, duration, bbox, ride_type="coaster")
        
    def plot(self, ax, t):
        """Visualización de montaña rusa con pista y vagones."""
        # Dibujar componentes base
        self._draw_bbox(ax)
        self._draw_queue(ax)
        self._draw_capacity_info(ax)
        
        # Dibujar animación específica de montaña rusa
        self._draw_coaster_animation(ax, t)
        
        # Nombre de la atracción
        ax.text(self.bbox[0], self.bbox[1] - 8, f"COASTER {self.name}", 
               fontsize=9, ha='left', weight='bold')

    def _draw_coaster_animation(self, ax, t):
        """Dibuja la pista y vagones en movimiento."""
        x, y, w, h = self.bbox
        
        # Dibujar pista en forma de óvalo
        track_color = "#2ca02c" if self.state == "running" else "#888888"
        
        # Pista principal (rectángulo redondeado)
        track_rect = patches.Rectangle((x+0.5, y+0.5), w-1, h-1, 
                                     fill=False, ec=track_color, lw=2)
        ax.add_patch(track_rect)
        
        # Si está funcionando, mostrar vagones en movimiento
        if self.state == "running" and self.riders:
            # Calcular posición del tren en la pista
            speed = 0.1 if self.state == "running" else 0.02
            progress = (t * speed) % 1.0
            
            # Posición en el óvalo de la pista
            if progress < 0.25:  # Lado superior
                train_x = x + 1 + (w-2) * (progress * 4)
                train_y = y + h - 0.5
            elif progress < 0.5:  # Lado derecho
                train_x = x + w - 0.5
                train_y = y + h - 1 - (h-2) * ((progress-0.25) * 4)
            elif progress < 0.75:  # Lado inferior
                train_x = x + w - 1 - (w-2) * ((progress-0.5) * 4)
                train_y = y + 0.5
            else:  # Lado izquierdo
                train_x = x + 0.5
                train_y = y + 1 + (h-2) * ((progress-0.75) * 4)
                
            # Dibujar vagón principal
            ax.plot([train_x], [train_y], marker='s', ms=8, 
                   color='#ff7f0e', markeredgecolor='black')
            
            # Dibujar vagones adicionales si hay más pasajeros
            for i in range(1, min(len(self.riders)//4 + 1, 3)):
                offset_x = train_x - i * 0.3 * math.cos(progress * 2 * math.pi)
                offset_y = train_y - i * 0.3 * math.sin(progress * 2 * math.pi)
                ax.plot([offset_x], [offset_y], marker='s', ms=6, 
                       color='#ff7f0e', alpha=0.8)

    def _draw_bbox(self, ax):
        """Dibuja el área base de la atracción."""
        RideVisuals.draw_bbox(self, ax)
        
    def _draw_queue(self, ax):
        """Dibuja la cola visual."""
        RideVisuals.draw_queue(self, ax)
        
    def _draw_capacity_info(self, ax):
        """Dibuja información de capacidad."""
        RideVisuals.draw_capacity_info(self, ax)