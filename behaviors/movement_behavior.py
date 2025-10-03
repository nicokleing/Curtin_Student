# -*- coding: utf-8 -*-
"""
Comportamiento de Movimiento para Visitantes
==========================================
Maneja la lógica de pathfinding y navegación
"""
import math
import random


class MovementBehavior:
    """Encapsula la lógica de movimiento de visitantes"""
    
    @staticmethod
    def at_target(position, target):
        """Verifica si el visitante está cerca del objetivo"""
        if target is None:
            return True
        dx = target[0] - position[0]
        dy = target[1] - position[1]
        return dx * dx + dy * dy < 0.9

    @staticmethod
    def step_towards(position, target, speed, terrain):
        """Mueve al visitante un paso hacia el objetivo"""
        if target is None:
            return position
            
        px, py = position
        tx, ty = target
        vx = tx - px
        vy = ty - py
        dist = math.hypot(vx, vy)
        
        if dist < 1e-6:
            return position
            
        # Vector unitario hacia el objetivo
        ux = vx / dist
        uy = vy / dist
        
        # Nueva posición propuesta
        nx = px + ux * speed
        ny = py + uy * speed
        
        # Verificar si el camino está libre
        if terrain.is_free_line((px, py), (nx, ny)):
            return (nx, ny)
        else:
            # Pequeño rodeo para evitar obstáculos
            angle = random.choice([-1, 1]) * math.pi / 6
            rx = ux * math.cos(angle) - uy * math.sin(angle)
            ry = ux * math.sin(angle) + uy * math.cos(angle)
            nx = px + rx * speed
            ny = py + ry * speed
            
            if terrain.is_free_point((nx, ny)):
                return (nx, ny)
            
        return position  # No se pudo mover

    @staticmethod
    def find_nearby_rides(position, rides, max_distance=8.0):
        """Encuentra atracciones cercanas al visitante"""
        nearby = []
        px, py = position
        
        for ride in rides:
            rx, ry = ride.center()
            distance = math.hypot(px - rx, py - ry)
            if distance <= max_distance:
                nearby.append((ride, distance))
                
        return [ride for ride, _ in sorted(nearby, key=lambda x: x[1])]