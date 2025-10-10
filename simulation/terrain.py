
# -*- coding: utf-8 -*-
"""Terrain helpers for the simulation grid."""
import csv
import random
import matplotlib.patches as patches

class Terrain:
    def __init__(self, width, height, grid, spawns=None, exits=None):
        self.width = width
        self.height = height
        self.grid = [list(row) for row in grid]
        self.spawn_points = list(spawns) if spawns else []
        self.exit_points = list(exits) if exits else []
        self._ride_bboxes = []  # Track placed ride bounding boxes for collision checks
        self._baseline_grid = None
        self._baseline_spawns = None
        self._baseline_exits = None
        self._baseline_bboxes = None

        if not self.spawn_points and self.width > 2 and self.height > 2:
            self.spawn_points = [(1, self.height // 2)]
        if not self.exit_points and self.width > 2 and self.height > 2:
            self.exit_points = [(self.width - 2, self.height - 2)]

    @classmethod
    def from_size(cls, width, height):
        grid = []
        for y in range(height):
            row = []
            for x in range(width):
                if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                    row.append(1)  # wall
                else:
                    row.append(0)  # open
            grid.append(row)
        spawns = [(1, height // 2), (width - 2, height // 3)]
        exits = [(width - 2, height - 2), (2, 2)]
        return cls(width, height, grid, spawns, exits)

    @classmethod
    def from_csv(cls, path, *, spawns=None, exits=None):
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

        default_spawns = [(1, height // 2), (width - 2, height // 3)] if height and width else []
        default_exits = [(width - 2, height - 2), (2, 2)] if height and width else []

        spawns = spawns or default_spawns
        exits = exits or default_exits
        return cls(width, height, grid, spawns, exits)

    @classmethod
    def from_definition(cls, width, height, *, obstacles=None, entrances=None, exits=None, border=True):
        grid = []
        for y in range(height):
            row = []
            for x in range(width):
                if border and (x == 0 or y == 0 or x == width - 1 or y == height - 1):
                    row.append(1)
                else:
                    row.append(0)
            grid.append(row)

        terrain = cls(width, height, grid, entrances or [], exits or [])

        for bbox in obstacles or []:
            terrain.add_bbox_barrier(tuple(int(v) for v in bbox))

        return terrain

    def is_free_point(self, p):
        x = int(p[0]); y = int(p[1])
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
        for xx, yy in self._cells_for_bbox(bbox):
            if 0 <= yy < self.height and 0 <= xx < self.width:
                self.grid[yy][xx] = 1

    def add_ride(self, ride, *, allow_tangent=True):
        """Check axis-aligned overlap before placing the ride."""
        bbox = ride.bbox

        if not self._bbox_inside(bbox):
            raise ValueError(f"Ride {ride.name} is out of terrain bounds: {bbox}")

        for other in self._ride_bboxes:
            if self._bbox_intersects(bbox, other, allow_tangent=allow_tangent):
                raise ValueError(
                    f"Ride {ride.name} overlaps existing ride area: {bbox} vs {other}"
                )

        for xx, yy in self._cells_for_bbox(bbox):
            if not (0 <= yy < self.height and 0 <= xx < self.width):
                raise ValueError(f"Ride {ride.name} extends outside the terrain grid: {bbox}")
            if self.grid[yy][xx] == 1:
                raise ValueError(
                    f"Ride {ride.name} collides with obstacle at cell ({xx}, {yy})"
                )

        self._ride_bboxes.append(bbox)
        self.add_bbox_barrier(bbox)

    def capture_baseline(self):
        """Store the current grid layout so resets can restore it."""
        self._baseline_grid = [row[:] for row in self.grid]
        self._baseline_spawns = list(self.spawn_points)
        self._baseline_exits = list(self.exit_points)
        self._baseline_bboxes = [tuple(b) for b in self._ride_bboxes]

    def reset(self):
        """Restore the saved layout after a simulation reset."""
        if self._baseline_grid is None:
            self.capture_baseline()
            return
        self.grid = [row[:] for row in self._baseline_grid]
        self.spawn_points = list(self._baseline_spawns or [])
        self.exit_points = list(self._baseline_exits or [])
        bboxes = self._baseline_bboxes or []
        self._ride_bboxes = [tuple(b) for b in bboxes]

    def _bbox_inside(self, bbox):
        x, y, w, h = bbox
        return 0 <= x and 0 <= y and (x + w) <= self.width and (y + h) <= self.height

    def _bbox_intersects(self, a, b, *, allow_tangent=True):
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        if allow_tangent:
            return not (ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay)
        else:
            return not (ax + aw < bx or bx + bw < ax or ay + ah < by or by + bh < ay)

    def _cells_for_bbox(self, bbox):
        x, y, w, h = bbox
        for yy in range(int(y), int(y + h)):
            for xx in range(int(x), int(x + w)):
                yield xx, yy

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
