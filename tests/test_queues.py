import unittest

from collections import deque

from adventure.rides.base_ride import Ride


class DummyPatron:
    def __init__(self, pid):
        self.id = pid


class QueueCapacityTests(unittest.TestCase):
    def test_enqueue_respects_queue_limit(self):
        r = Ride("Tst", capacity=2, duration=10, bbox=(0, 0, 4, 3))
        r.queue_limit = 2
        p1 = DummyPatron("p1")
        p2 = DummyPatron("p2")
        p3 = DummyPatron("p3")
        self.assertTrue(r.enqueue(p1))
        self.assertTrue(r.enqueue(p2))
        # now full
        self.assertFalse(r.enqueue(p3))
        # internal queue size stays at 2
        self.assertEqual(len(r.queue), 2)


if __name__ == "__main__":
    unittest.main()
