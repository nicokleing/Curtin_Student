import random
import unittest

from adventure.patrons import Patron, PatronType, DEFAULT_CATEGORY_WEIGHTS
from adventure.patrons.behaviors.decision_behavior import DecisionBehavior
from adventure.patrons.behaviors.movement_behavior import MovementBehavior
from adventure.patrons.behaviors.queue_behavior import QueueBehavior
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
        self.riders = []
        self.category = None

    def center(self):
        x, y, w, h = self.bbox
        return (x + w / 2.0, y + h / 2.0)


class PatronBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.terrain = Terrain.from_definition(20, 15, obstacles=[], entrances=[(1, 1)], exits=[(18, 13)])

    def test_patron_leaves_park_when_exit_triggered(self):
        patron = Patron("P1", [(1, 1)], [(18, 13)], self.terrain, patron_type=PatronType.FAMILY)
        patron.timer = 1
        patron.speed = 1.5

        patron.step_change(0, [])
        self.assertEqual(patron.state, "roaming")

        patron.target = patron.exits[0]
        original_random = random.random
        random.random = lambda: 0.0
        try:
            for tick in range(60):
                patron.step_change(tick + 1, [])
                if patron.state == "left":
                    break
        finally:
            random.random = original_random

        self.assertEqual(patron.state, "left")

    def test_category_preferences_influence_scores(self):
        family_pref = DEFAULT_CATEGORY_WEIGHTS[PatronType.FAMILY].copy()
        adventurer_pref = DEFAULT_CATEGORY_WEIGHTS[PatronType.ADVENTURER].copy()

        family_ride = FakeRide("FamilyRide", "ferris", (6, 6, 3, 3), rating=0.65)
        thrill_ride = FakeRide("ThrillRide", "coaster", (12, 6, 3, 3), rating=0.85)

        pos = (3.0, 3.0)
        family_score_family = DecisionBehavior.compute_ride_score(pos, family_ride, self.terrain, family_pref)
        thrill_score_family = DecisionBehavior.compute_ride_score(pos, thrill_ride, self.terrain, family_pref)
        self.assertGreater(family_score_family, thrill_score_family)

        family_score_adv = DecisionBehavior.compute_ride_score(pos, family_ride, self.terrain, adventurer_pref)
        thrill_score_adv = DecisionBehavior.compute_ride_score(pos, thrill_ride, self.terrain, adventurer_pref)
        self.assertGreater(thrill_score_adv, family_score_adv)

    def test_queue_penalty_prefers_shorter_line(self):
        prefs = DEFAULT_CATEGORY_WEIGHTS[PatronType.IMPATIENT].copy()
        near_pos = (4.0, 4.0)

        short_queue = FakeRide("ShortQueue", "pirate", (8, 4, 3, 3), rating=0.8)
        short_queue.queue = [object(), object()]

        long_queue = FakeRide("LongQueue", "pirate", (10, 4, 3, 3), rating=0.8)
        long_queue.queue = [object() for _ in range(10)]

        short_score = DecisionBehavior.compute_ride_score(near_pos, short_queue, self.terrain, prefs)
        long_score = DecisionBehavior.compute_ride_score(near_pos, long_queue, self.terrain, prefs)
        self.assertGreater(short_score, long_score)

    def test_abandon_event_records_details(self):
        patron = Patron("P2", [(1, 1)], [(18, 13)], self.terrain, patron_type=PatronType.IMPATIENT)
        patron.state = "queueing"
        patron.patience = 1

        ride = FakeRide("QueueRide", "pirate", (8, 6, 3, 3), rating=0.8)
        ride.queue = [patron, object(), object()]

        new_state = QueueBehavior.process_queue_patience(patron, current_time=7, rides=[ride])
        self.assertEqual(new_state, "roaming")
        event = patron.last_abandon_event
        if event is None:
            self.fail("Expected abandon event to be recorded")
        self.assertEqual(event["ride_id"], ride.name)
        self.assertEqual(event["time"], 7)
        self.assertEqual(event["queue_len"], 3)
        self.assertEqual(event["patience_at_leave"], 0)

    def test_queue_and_ride_references_update(self):
        patron = Patron("P5", [(1, 1)], [(18, 13)], self.terrain, patron_type=PatronType.ADVENTURER)
        ride = FakeRide("RefRide", "pirate", (8, 6, 3, 3), rating=0.8)

        patron._join_queue(ride, current_time=5)
        self.assertIs(patron.queue_ref, ride)
        self.assertEqual(patron.state, "queueing")

        if patron in ride.queue:
            ride.queue.remove(patron)
        patron.board_ride(ride)
        self.assertIsNone(patron.queue_ref)
        self.assertIs(patron.ride_ref, ride)

        patron.leave_ride()
        self.assertIsNone(patron.ride_ref)
        self.assertEqual(patron.state, "roaming")

        patron._join_queue(ride, current_time=12)
        QueueBehavior.abandon_queue(patron, ride, current_time=14, queue_length=len(ride.queue))
        self.assertIsNone(patron.queue_ref)

    def test_pathfinding_detects_blocked_route(self):
        blocked = Terrain.from_definition(12, 8, obstacles=[(5, 0, 1, 8)], entrances=[(1, 1)], exits=[(10, 6)])
        patron = Patron("P3", [(1, 1)], [(10, 6)], blocked, patron_type=PatronType.ADVENTURER)
        patron.state = "roaming"
        patron.position = (2.0, 2.0)
        patron.target = (9.0, 2.0)
        patron.speed = 1.0

        patron._step_towards()
        self.assertIsNone(patron.target)
        self.assertAlmostEqual(patron.position[0], 2.0)

    def test_pathfinding_uses_opening(self):
        obstacles = [(5, 0, 1, 3), (5, 4, 1, 4)]  # Gap at y = 3
        terrain = Terrain.from_definition(12, 8, obstacles=obstacles, entrances=[(1, 1)], exits=[(10, 6)])
        patron = Patron("P4", [(1, 1)], [(10, 6)], terrain, patron_type=PatronType.EXPLORER)
        patron.state = "roaming"
        patron.position = (2.0, 3.0)
        patron.target = (9.0, 3.0)
        patron.speed = 1.0

        for _ in range(20):
            patron._step_towards()
            if MovementBehavior.at_target(patron.position, patron.target):
                break
        self.assertTrue(MovementBehavior.at_target(patron.position, patron.target))


if __name__ == "__main__":
    unittest.main()
