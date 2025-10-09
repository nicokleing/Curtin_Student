# -*- coding: utf-8 -*-
"""
Movement behavior for visitors.
================================
Handles grid-based pathfinding and navigation.
"""
import heapq
import math


class MovementBehavior:
    """Encapsulate visitor movement logic."""
    PATH_CACHE_LIMIT = 256
    _path_cache = {}

    @classmethod
    def clear_cache(cls, terrain=None):
        """Clear cached paths, optionally for a specific terrain."""
        if terrain is None:
            cls._path_cache.clear()
        else:
            cls._path_cache.pop(id(terrain), None)
    
    @staticmethod
    def at_target(position, target):
        """Check if the visitor is close to the target."""
        if target is None:
            return True
        dx = target[0] - position[0]
        dy = target[1] - position[1]
        return dx * dx + dy * dy < 0.9

    @classmethod
    def step_towards(cls, position, target, speed, terrain):
        """Move the visitor a step toward the target using A* pathfinding."""
        if target is None:
            return position, True

        start_cell = cls._to_cell(position)
        goal_cell = cls._to_cell(target)
        path = cls._find_path(start_cell, goal_cell, terrain)
        if not path:
            return position, False

        next_cell = path[1] if len(path) > 1 else path[0]
        dest = (next_cell[0] + 0.5, next_cell[1] + 0.5)

        px, py = position
        vx = dest[0] - px
        vy = dest[1] - py
        dist = math.hypot(vx, vy)

        if dist < 1e-6:
            return position, True

        step = min(speed, dist)
        nx = px + (vx / dist) * step
        ny = py + (vy / dist) * step

        new_position = (nx, ny)
        if not terrain.is_free_point(new_position):
            return position, False

        return new_position, True

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

    @classmethod
    def _find_path(cls, start, goal, terrain):
        cache = cls._path_cache.setdefault(id(terrain), {})
        key = (start, goal)
        if key in cache:
            return cache[key]

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: cls._heuristic(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                path = cls._reconstruct_path(came_from, current)
                cls._store_path(cache, key, path)
                return path

            for neighbour in cls._neighbours(current):
                if not cls._is_walkable(neighbour, terrain):
                    continue

                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get(neighbour, float("inf")):
                    came_from[neighbour] = current
                    g_score[neighbour] = tentative_g
                    f_score[neighbour] = tentative_g + cls._heuristic(neighbour, goal)
                    heapq.heappush(open_set, (f_score[neighbour], neighbour))

        cls._store_path(cache, key, None)
        return None

    @staticmethod
    def _store_path(cache, key, path):
        if len(cache) >= MovementBehavior.PATH_CACHE_LIMIT:
            cache.pop(next(iter(cache)))
        cache[key] = path

    @staticmethod
    def _heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def _to_cell(point):
        return (int(round(point[0])), int(round(point[1])))

    @staticmethod
    def _neighbours(cell):
        x, y = cell
        return [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
        ]

    @staticmethod
    def _is_walkable(cell, terrain):
        x, y = cell
        if x < 0 or y < 0 or x >= terrain.width or y >= terrain.height:
            return False
        try:
            return terrain.grid[y][x] == 0
        except IndexError:
            return False

    @staticmethod
    def _reconstruct_path(came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
