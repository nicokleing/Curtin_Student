import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from interface.cli import CLIManager
from config.loader import ConfigLoader


class CLIModeParsingTest(unittest.TestCase):
    def test_interactive_flag_sets_true(self):
        cli = CLIManager()
        test_args = ["adventureworld", "-i", "--steps", "50"]
        with patch.object(sys, 'argv', test_args):
            args = cli.parse_arguments()
        self.assertTrue(args.interactive)
        self.assertEqual(args.steps, 50)

    def test_csv_shortcuts_populate_fields(self):
        cli = CLIManager()
        test_args = [
            "adventureworld",
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
            config=None,
            map_csv=None,
            rides_csv=None,
            patrons_csv=None,
            steps=30,
            stats=False,
            seed=seed,
            save_run=False
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


if __name__ == "__main__":
    unittest.main()
