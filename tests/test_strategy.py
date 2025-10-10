import unittest

from adventure.patrons.behaviors.decision_behavior import DecisionBehavior
from adventure.terrain import Terrain


class FakeRide:
    def __init__(self, name, ride_type, bbox, capacity=10, rating=0.6):
        self.name = name
        self.ride_type = ride_type
        self.bbox = bbox
        self.capacity = capacity
        self.duration = 60
        self.rating = rating
        self.queue = []

    def center(self):
        x, y, w, h = self.bbox
        return (x + w / 2.0, y + h / 2.0)


class StrategyTests(unittest.TestCase):
    def test_shorter_queue_preferred(self):
        terrain = Terrain.from_definition(20, 15, obstacles=[], entrances=[(1, 1)], exits=[(18, 13)])
        pos = (4.0, 4.0)

        short_queue = FakeRide("ShortQueue", "pirate", (8, 4, 3, 3), rating=0.8)
        short_queue.queue = [object(), object()]

        long_queue = FakeRide("LongQueue", "pirate", (10, 4, 3, 3), rating=0.8)
        long_queue.queue = [object() for _ in range(10)]

        prefs = {}
        short_score = DecisionBehavior.compute_ride_score(pos, short_queue, terrain, prefs)
        long_score = DecisionBehavior.compute_ride_score(pos, long_queue, terrain, prefs)

        self.assertGreater(short_score, long_score)


if __name__ == '__main__':
    unittest.main()
