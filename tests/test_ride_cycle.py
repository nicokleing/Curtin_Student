import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import unittest

from rides.base_ride import Ride
from rides.ride_visuals import RideVisuals


class DummyPatron:
    def __init__(self):
        self.current_ride = None

    def board_ride(self, ride):
        self.current_ride = ride

    def leave_ride(self):
        self.current_ride = None


class InstrumentedRide(Ride):
    def __init__(self, name, capacity, duration, bbox, **kwargs):
        super().__init__(name, capacity, duration, bbox, **kwargs)
        self.completed_cycles = 0
        self.total_boarded = 0

    def finish_cycle(self):
        self.total_boarded += len(self.riders)
        super().finish_cycle()
        self.completed_cycles += 1


class RideCycleTests(unittest.TestCase):
    def _dummy_queue(self, count):
        return [DummyPatron() for _ in range(count)]

    def test_state_cycle_and_capacity_respected(self):
        ride = Ride("TestRide", capacity=3, duration=2, bbox=(0, 0, 4, 3))
        ride.queue = self._dummy_queue(12)

        states = []
        max_riders = 0
        for t in range(60):
            ride.step_change(t)
            states.append(ride.state)
            max_riders = max(max_riders, len(ride.riders))

        self.assertIn("loading", states)
        self.assertIn("running", states)
        self.assertIn("unloading", states)

        allowed = {
            "idle": {"idle", "loading"},
            "loading": {"loading", "running"},
            "running": {"running", "unloading"},
            "unloading": {"unloading", "idle"},
        }
        for prev, curr in zip(states, states[1:]):
            self.assertIn(curr, allowed[prev])

        self.assertLessEqual(max_riders, ride.capacity)

    def test_loading_times_affect_throughput(self):
        fast = InstrumentedRide(
            "Fast", capacity=2, duration=4, bbox=(0, 0, 4, 3),
            loading_time=1, unloading_time=1,
        )
        slow = InstrumentedRide(
            "Slow", capacity=2, duration=4, bbox=(0, 0, 4, 3),
            loading_time=5, unloading_time=5,
        )

        fast.queue = self._dummy_queue(60)
        slow.queue = self._dummy_queue(60)

        for t in range(160):
            fast.step_change(t)
            slow.step_change(t)

        self.assertGreater(fast.completed_cycles, slow.completed_cycles)
        self.assertGreater(fast.total_boarded, slow.total_boarded)

    def test_queue_overlay_matches_length(self):
        ride = InstrumentedRide("Overlay", capacity=4, duration=3, bbox=(0, 0, 4, 3))
        ride.queue = self._dummy_queue(3)
        ride.riders = self._dummy_queue(1)

        fig, ax = plt.subplots()
        RideVisuals.draw_capacity_info(ride, ax)
        texts = [text.get_text() for text in ax.texts]
        self.assertTrue(any("Queue 3" in text for text in texts))

        ax.clear()
        ride.queue.pop()
        RideVisuals.draw_capacity_info(ride, ax)
        texts = [text.get_text() for text in ax.texts]
        self.assertTrue(any("Queue 2" in text for text in texts))
        plt.close(fig)


if __name__ == "__main__":
    unittest.main()
