# -*- coding: utf-8 -*-
"""
Movement behavior for visitors.
================================
Handles basic pathfinding and navigation.
"""
import math
import random


class MovementBehavior:
    """Encapsulate visitor movement logic."""
    
    @staticmethod
    def at_target(position, target):
        """Check if the visitor is close to the target."""
        if target is None:
            return True
        dx = target[0] - position[0]
        dy = target[1] - position[1]
        return dx * dx + dy * dy < 0.9

    @staticmethod
    def step_towards(position, target, speed, terrain):
        """Move the visitor a step toward the target."""
        if target is None:
            return position
            
        px, py = position
        tx, ty = target
        vx = tx - px
        vy = ty - py
        dist = math.hypot(vx, vy)
        
        if dist < 1e-6:
            return position
            
        # Unit vector toward the target
        ux = vx / dist
        uy = vy / dist
        
        # Proposed new position
        nx = px + ux * speed
        ny = py + uy * speed
        
        # Check whether the path is clear
        if terrain.is_free_line((px, py), (nx, ny)):
            return (nx, ny)
        else:
            # Take a small detour to avoid obstacles
            angle = random.choice([-1, 1]) * math.pi / 6
            rx = ux * math.cos(angle) - uy * math.sin(angle)
            ry = ux * math.sin(angle) + uy * math.cos(angle)
            nx = px + rx * speed
            ny = py + ry * speed
            
            if terrain.is_free_point((nx, ny)):
                return (nx, ny)
            
        return position  # Could not move

    @staticmethod
    def find_nearby_rides(position, rides, max_distance=8.0):
        """Find nearby rides for this visitor."""
        nearby = []
        px, py = position
        
        for ride in rides:
            rx, ry = ride.center()
            distance = math.hypot(px - rx, py - ry)
            if distance <= max_distance:
                nearby.append((ride, distance))
                
        return [ride for ride, _ in sorted(nearby, key=lambda x: x[1])]
