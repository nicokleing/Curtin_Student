import unittest
from collections import deque
from types import SimpleNamespace

from adventure.terrain import Terrain
from adventure.utils.io import build_rides
from core.engine import SimulationEngine


class SatisfactionMetricsTest(unittest.TestCase):
    def _make_engine(self):
        terrain = Terrain.from_size(20, 15)
        rides = build_rides([
            {"type": "pirate", "capacity": 4, "duration": 5, "bbox": (3, 3, 4, 3)}
        ], terrain)
        terrain.capture_baseline()
        config = SimpleNamespace(
            terrain=terrain,
            rides=rides,
            patrons=[],
            steps=60,
            show_stats=False,
            save_run=False,
            interactive=False,
            headless=True,
            kpi_buffer_size=32,
            kpi_warmup=2,
            kpi_interval=0.0,
            kpi_style='default',
            sat_alpha=1.0,
            sat_beta=1.0,
            sat_gamma=1.0,
            sat_ema=0.5
        )
        return SimulationEngine(config)

    def test_satisfaction_formula_and_ema(self):
        engine = self._make_engine()
        engine._reset_stat_buffers()
        engine._queue_history = deque(maxlen=engine.kpi_buffer_size)
        engine._active_history = deque(maxlen=engine.kpi_buffer_size)
        engine._prev_abandoned_total = 0
        engine.metrics_calculator.update_live_satisfaction(100.0)

        # Baseline: empty queues, no abandons
        ride = engine.rides[0]
        ride.queue = []
        ride.riders = []
        engine.patrons = [SimpleNamespace(state='roaming', abandoned_queues=0) for _ in range(10)]
        engine._update_statistics()
        baseline = engine.satisfaction_now[-1]
        self.assertGreaterEqual(baseline, 90.0)

        # Stress: heavy queues, multiple abandons
        ride.queue = [object() for _ in range(20)]
        ride.riders = [object() for _ in range(ride.capacity)]
        engine.patrons = [SimpleNamespace(state='queueing', abandoned_queues=1) for _ in range(8)]
        engine.patrons += [SimpleNamespace(state='left', abandoned_queues=2) for _ in range(4)]
        engine._update_statistics()
        stressed = engine.satisfaction_now[-1]
        ema = engine.satisfaction_ema[-1]

        self.assertLess(stressed, baseline)
        self.assertLessEqual(ema, baseline)
        self.assertGreater(ema, stressed)
        self.assertGreaterEqual(stressed, 0.0)
        self.assertLessEqual(stressed, 100.0)
        self.assertAlmostEqual(engine.metrics_calculator.get_current_satisfaction(), round(stressed, 2), places=2)

        timeline = engine._collect_timeline_data()
        self.assertIsNotNone(timeline)
        timeline = timeline or {}
        self.assertIn('satisfaction_now', timeline)
        summary = engine._build_satisfaction_summary()
        self.assertEqual(summary['total_samples'], len(engine.satisfaction_now))


if __name__ == '__main__':
    unittest.main()
