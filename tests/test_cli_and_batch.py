import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from scripts import adventureworld as adventureworld_script

from interface.cli import CLIManager
from config.loader import ConfigLoader


class CLIModeParsingTest(unittest.TestCase):
    def test_wizard_flag_sets_true(self):
        cli = CLIManager()
        test_args = [
            "adventureworld",
            "--mode", "advanced",
            "--wizard",
            "--steps", "50",
        ]
        with patch.object(sys, 'argv', test_args):
            args = cli.parse_arguments()
        self.assertTrue(args.wizard)
        self.assertEqual(args.steps, 50)

    def test_simple_mode_uses_preset_value(self):
        cli = CLIManager()
        test_args = [
            "adventureworld",
            "--mode", "simple",
            "--preset", "small",
        ]
        with patch.object(sys, 'argv', test_args):
            args = cli.parse_arguments()
        self.assertEqual(args.mode, "simple")
        self.assertEqual(args.preset, "small")

    def test_csv_shortcuts_populate_fields(self):
        cli = CLIManager()
        test_args = [
            "adventureworld",
            "--mode", "advanced",
            "-f", "data/map1.csv",
            "-r", "data/rides.csv",
            "-p", "data/patrons.csv",
            "--seed", "13",
            "--steps", "25"
        ]
        with patch.object(sys, 'argv', test_args):
            args = cli.parse_arguments()
        self.assertEqual(args.map_csv, "data/map1.csv")
        self.assertEqual(args.rides_csv, "data/rides.csv")
        self.assertEqual(args.patrons_csv, "data/patrons.csv")
        self.assertEqual(args.seed, 13)
        self.assertEqual(args.steps, 25)


class BatchSeedReproducibilityTest(unittest.TestCase):
    def _build_args(self, seed):
        return SimpleNamespace(
            interactive=False,
            wizard=False,
            mode="simple",
            preset="medium",
            config=None,
            map_csv=None,
            rides_csv=None,
            patrons_csv=None,
            steps=30,
            stats=False,
            seed=seed,
            save_run=False,
            no_gui=False,
            gui=False,
            kpi_buffer_size=240,
            kpi_warmup=5,
            kpi_interval=0.0,
            kpi_style="default",
            save_kpis=None,
            no_summary=True,
        )

    def test_same_seed_produces_same_initial_state(self):
        loader_a = ConfigLoader()
        config_a = loader_a.load_from_args(self._build_args(42))
        loader_b = ConfigLoader()
        config_b = loader_b.load_from_args(self._build_args(42))

        timers_a = [patron.timer for patron in config_a.patrons[:10]]
        timers_b = [patron.timer for patron in config_b.patrons[:10]]
        self.assertEqual(timers_a, timers_b)

    def test_different_seeds_change_initial_state(self):
        loader_a = ConfigLoader()
        config_a = loader_a.load_from_args(self._build_args(7))
        loader_b = ConfigLoader()
        config_b = loader_b.load_from_args(self._build_args(99))

        timers_a = [patron.timer for patron in config_a.patrons[:10]]
        timers_b = [patron.timer for patron in config_b.patrons[:10]]
        self.assertNotEqual(timers_a, timers_b)


class CLIGuiToggleIntegrationTest(unittest.TestCase):
    def test_default_arguments_run_interactive(self):
        test_args = [
            "adventureworld",
            "--mode", "simple",
            "--preset", "small",
            "--steps", "4",
            "--no-summary",
        ]
        with patch.object(sys, 'argv', test_args):
            with patch.object(adventureworld_script, "SimulationEngine") as mock_engine:
                mock_engine.return_value.run.return_value = None
                adventureworld_script.main()

        mock_engine.return_value.run.assert_called_once_with(interactive=True)
        config_passed = mock_engine.call_args[0][0]
        self.assertTrue(config_passed.interactive)
        self.assertFalse(config_passed.headless)

    def test_no_gui_flag_runs_headless(self):
        test_args = [
            "adventureworld",
            "--mode", "simple",
            "--preset", "small",
            "--steps", "4",
            "--no-gui",
            "--no-summary",
        ]
        with patch.object(sys, 'argv', test_args):
            with patch.object(adventureworld_script, "SimulationEngine") as mock_engine:
                mock_engine.return_value.run.return_value = None
                adventureworld_script.main()

        mock_engine.return_value.run.assert_called_once_with(interactive=False)
        config_passed = mock_engine.call_args[0][0]
        self.assertFalse(config_passed.interactive)
        self.assertTrue(config_passed.headless)


if __name__ == "__main__":
    unittest.main()
