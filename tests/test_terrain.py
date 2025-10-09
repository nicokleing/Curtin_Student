import unittest

from simulation.terrain import Terrain
from simulation.utils import build_rides


class DummyRide:
    def __init__(self, name, bbox):
        self.name = name
        self.capacity = 10
        self.duration = 30
        self.bbox = bbox


class TerrainPlacementTests(unittest.TestCase):
    def setUp(self):
        self.terrain = Terrain.from_definition(20, 12, obstacles=[], entrances=[(1, 1)], exits=[(18, 10)])

    def test_add_ride_rejects_overlapping_area(self):
        first = DummyRide("R1", (2, 2, 4, 3))
        second = DummyRide("R2", (3, 3, 4, 3))

        self.terrain.add_ride(first)
        with self.assertRaisesRegex(ValueError, "overlaps existing ride area"):
            self.terrain.add_ride(second)

    def test_add_ride_allows_tangent_edges(self):
        left = DummyRide("Left", (2, 2, 4, 3))
        right = DummyRide("Right", (6, 2, 4, 3))  # Touch at x = 6

        self.terrain.add_ride(left)
        # Should not raise
        self.terrain.add_ride(right)

    def test_add_ride_rejects_obstacle_cells(self):
        terrain = Terrain.from_definition(15, 10, obstacles=[(5, 5, 2, 2)])
        with self.assertRaisesRegex(ValueError, "collides with obstacle"):
            terrain.add_ride(DummyRide("R1", (4, 4, 3, 3)))

    def test_build_rides_rejects_overlapping_config(self):
        params = [
            {"type": "pirate", "capacity": 10, "duration": 40, "bbox": (2, 2, 4, 3)},
            {"type": "ferris", "capacity": 8, "duration": 60, "bbox": (3, 3, 4, 3)},
        ]
        terrain = Terrain.from_definition(25, 15)
        with self.assertRaises(ValueError):
            build_rides(params, terrain)

    def test_build_rides_accepts_valid_config(self):
        params = [
            {"type": "pirate", "capacity": 10, "duration": 40, "bbox": (2, 2, 4, 3)},
            {"type": "ferris", "capacity": 8, "duration": 60, "bbox": (8, 2, 4, 3)},
        ]
        terrain = Terrain.from_definition(25, 15)
        rides = build_rides(params, terrain)
        self.assertEqual(len(rides), 2)


if __name__ == "__main__":
    unittest.main()
