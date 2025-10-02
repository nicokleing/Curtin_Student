
# -*- coding: utf-8 -*-
"""
Terrain (terreno/mapa) – versión junior modular
- Mapa grilla 0/1; paredes alrededor por defecto
- Spawns y exits simples
"""
import csv
import random
import matplotlib.patches as patches

class Terrain:
    def __init__(self, width, height, grid, spawns, exits):
        self.width = width
        self.height = height
        self.grid = grid
        self.spawn_points = spawns
        self.exit_points = exits

    @classmethod
    def from_size(cls, width, height):
        grid = []
        for y in range(height):
            row = []
            for x in range(width):
                if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                    row.append(1)  # pared
                else:
                    row.append(0)  # libre
            grid.append(row)
        spawns = [(1, height // 2), (width - 2, height // 3)]
        exits = [(width - 2, height - 2), (2, 2)]
        return cls(width, height, grid, spawns, exits)

    @classmethod
    def from_csv(cls, path):
        grid = []
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0].strip().startswith('#'):
                    continue
                if not row:
                    continue
                grid.append([int(v) for v in row])
        height = len(grid)
        width = len(grid[0]) if height > 0 else 0
        spawns = [(1, height // 2), (width - 2, height // 3)]
        exits = [(width - 2, height - 2), (2, 2)]
        return cls(width, height, grid, spawns, exits)

    def is_free_point(self, p):
        x = int(round(p[0])); y = int(round(p[1]))
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return False
        return self.grid[y][x] == 0

    def is_free_line(self, a, b):
        steps = 6
        for i in range(steps + 1):
            t = i / steps
            x = a[0] + (b[0] - a[0]) * t
            y = a[1] + (b[1] - a[1]) * t
            if not self.is_free_point((x, y)):
                return False
        return True

    def near_bbox(self, p, bbox, tol=0.5):
        x, y, w, h = bbox
        px, py = p
        return (x - tol) <= px <= (x + w + tol) and (y - tol) <= py <= (y + h + tol)

    def random_free_point(self):
        while True:
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if self.grid[y][x] == 0:
                return (x, y)

    def add_bbox_barrier(self, bbox):
        x, y, w, h = bbox
        for yy in range(max(0, y), min(self.height, y + h)):
            for xx in range(max(0, x), min(self.width, x + w)):
                self.grid[yy][xx] = 1

    def plot(self, ax):
        for yy in range(self.height):
            for xx in range(self.width):
                if self.grid[yy][xx] == 1:
                    rect = patches.Rectangle((xx - 0.5, yy - 0.5), 1, 1, fc="#eeeeee", ec="none")
                    ax.add_patch(rect)
        for sx, sy in self.spawn_points:
            ax.plot([sx], [sy], marker="^", ms=8)
        for ex, ey in self.exit_points:
            ax.plot([ex], [ey], marker="v", ms=8)
