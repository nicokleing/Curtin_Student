import unittest
from types import SimpleNamespace

from simulation import Terrain, build_rides
from core.engine import SimulationEngine


class SimulationEngineControlsTest(unittest.TestCase):
    def _make_engine(self, steps=20):
        terrain = Terrain.from_size(20, 15)
        rides = build_rides([
            {"type": "pirate", "capacity": 2, "duration": 4, "bbox": (3, 3, 4, 3)}
        ], terrain)
        terrain.capture_baseline()
        config = SimpleNamespace(
            terrain=terrain,
            rides=rides,
            patrons=[],
            steps=steps,
            show_stats=False,
            save_run=False,
            interactive=False
        )
        return SimulationEngine(config)

    def test_pause_stops_tick_progress(self):
        engine = self._make_engine()
        engine.perform_tick()
        base_step = engine.current_step

        engine.toggle_pause()
        engine.perform_tick()
        self.assertEqual(engine.current_step, base_step)

        engine.toggle_pause()
        engine.perform_tick()
        self.assertGreater(engine.current_step, base_step)

    def test_reset_restores_initial_state(self):
        engine = self._make_engine()
        engine.perform_tick()
        engine.rides[0].queue.append(object())
        engine.riders_now.append(5)
        engine.queued_now.append(3)
        engine.departed_total.append(1)
        engine.abandoned_now.append(0)

        engine.reset_simulation()

        self.assertEqual(engine.current_step, 0)
        self.assertEqual(engine.time, 0)
        self.assertFalse(engine.paused)
        self.assertTrue(engine.running)
        self.assertEqual(engine.speed_multiplier, 1)
        self.assertEqual(len(engine.riders_now), 0)
        self.assertEqual(len(engine.queued_now), 0)
        self.assertEqual(len(engine.departed_total), 0)
        self.assertEqual(len(engine.abandoned_now), 0)
        self.assertEqual(len(engine.rides[0].queue), 0)
        self.assertEqual(len(engine.rides[0].riders), 0)
        self.assertEqual(
            engine.metrics_calculator.park_metrics['total_visitors'],
            len(engine.patrons)
        )

    def test_speed_multiplier_applies_multiple_steps(self):
        engine = self._make_engine()
        engine.set_speed(5)
        engine.perform_tick()
        self.assertEqual(engine.speed_multiplier, 5)
        self.assertEqual(engine.current_step, min(5, engine.steps))


if __name__ == "__main__":
    unittest.main()
