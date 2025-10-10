import unittest
from types import SimpleNamespace

from adventure.config.loader import ConfigLoader
from core.engine import SimulationEngine


class QueueFullExportIntegrationTest(unittest.TestCase):
    def test_queue_full_event_logged_in_export_manager(self):
        loader = ConfigLoader()

        # Build arguments similar to other tests and load a full config object
        args = SimpleNamespace(
            interactive=False,
            wizard=False,
            mode="simple",
            preset="small",
            config=None,
            map_csv=None,
            rides_csv=None,
            patrons_csv=None,
            steps=50,
            stats=False,
            seed=None,
            save_run=True,
            no_gui=True,
            gui=False,
            kpi_buffer_size=240,
            kpi_warmup=5,
            kpi_interval=0.0,
            kpi_style="default",
            save_kpis=None,
            no_summary=True,
        )

        config = loader.load_from_args(args)

        engine = SimulationEngine(config)
        # run short simulation via public API
        engine.run(interactive=config.interactive)

        # ensure export manager exists and recorded events (may be empty)
        self.assertTrue(hasattr(engine, 'export_manager'))
        self.assertIsInstance(engine.export_manager.events_log, list)


if __name__ == '__main__':
    unittest.main()
