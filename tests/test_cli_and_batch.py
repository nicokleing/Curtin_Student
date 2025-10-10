import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts import adventureworld as adventureworld_script

from adventure.config.loader import ConfigLoader
from adventure.ui.cli import CLIManager
from core.engine import SimulationEngine
from adventure.rides import SpinnerRide


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
            "-f", "configs/map1.csv",
            "-r", "configs/rides.csv",
            "-p", "configs/patrons.csv",
            "--seed", "13",
            "--steps", "25"
        ]
        with patch.object(sys, 'argv', test_args):
            args = cli.parse_arguments()
        self.assertEqual(args.map_csv, "configs/map1.csv")
        self.assertEqual(args.rides_csv, "configs/rides.csv")
        self.assertEqual(args.patrons_csv, "configs/patrons.csv")
        self.assertEqual(args.seed, 13)
        self.assertEqual(args.steps, 25)

    def test_rides_mix_and_patrons_override(self):
        cli = CLIManager()
        test_args = [
            "adventureworld",
            "--mode", "advanced",
            "--map", "configs/map1.csv",
            "--rides", "pirate:1,ferris:1,spinner:1",
            "--patrons", "45",
            "--steps", "18",
            "--no-gui",
            "--no-summary",
        ]
        with patch.object(sys, 'argv', test_args):
            args = cli.parse_arguments()

        loader = ConfigLoader()
        config = loader.load_from_args(args, cli)
        self.assertEqual(len(config.rides), 3)
        self.assertTrue(any(isinstance(ride, SpinnerRide) for ride in config.rides))
        self.assertEqual(config.num_patrons, 45)
        self.assertEqual(config.steps, 18)


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

    def test_params_csv_overrides_seed_and_steps(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as handle:
            handle.write("key,value\nsteps,12\nseed,5\n")
            params_path = handle.name

        cli = CLIManager()
        test_args = [
            "adventureworld",
            "--mode", "simple",
            "--preset", "small",
            "--params", params_path,
            "--no-summary",
        ]
        try:
            with patch.object(sys, 'argv', test_args):
                args = cli.parse_arguments()
            loader = ConfigLoader()
            config = loader.load_from_args(args, cli)
        finally:
            Path(params_path).unlink(missing_ok=True)

        self.assertEqual(config.steps, 12)
        self.assertEqual(config.seed, 5)


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

    def test_log_file_written_for_batch_run(self):
        cli = CLIManager()
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "run.log"
            test_args = [
                "adventureworld",
                "--preset", "small",
                "--steps", "5",
                "--no-gui",
                "--log", str(log_path),
                "--no-summary",
            ]
            with patch.object(sys, 'argv', test_args):
                args = cli.parse_arguments()

            loader = ConfigLoader()
            config = loader.load_from_args(args, cli)

            engine = SimulationEngine(config)
            engine.run(interactive=config.interactive)

            self.assertTrue(log_path.exists())
            contents = log_path.read_text(encoding="utf-8")
            self.assertIn("Steps requested: 5", contents)
            self.assertIn("Simulation completed", contents)


class CLIValidationTest(unittest.TestCase):
    def test_negative_patrons_trigger_exit(self):
        cli = CLIManager()
        test_args = [
            "adventureworld",
            "--patrons", "-3",
        ]
        with patch.object(sys, 'argv', test_args):
            with self.assertRaises(SystemExit):
                cli.parse_arguments()


if __name__ == "__main__":
    unittest.main()
