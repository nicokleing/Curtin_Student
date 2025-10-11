import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from adventure.config.loader import ConfigLoader
from adventure.interface.cli import CLIManager


class CLIArgumentTests(unittest.TestCase):
    def test_defaults_are_applied(self):
        cli = CLIManager()
        with patch.object(sys, "argv", ["adventureworld"]):
            args = cli.parse_arguments()
        self.assertEqual(args.preset, "medium")
        self.assertEqual(args.steps, 300)
        self.assertIsNone(args.seed)
        self.assertFalse(args.stats)

    def test_custom_flags_override_defaults(self):
        cli = CLIManager()
        test_args = [
            "adventureworld",
            "--preset",
            "small",
            "--steps",
            "120",
            "--seed",
            "10",
            "--stats",
            "--no-gui",
        ]
        with patch.object(sys, "argv", test_args):
            args = cli.parse_arguments()
        self.assertEqual(args.preset, "small")
        self.assertEqual(args.steps, 120)
        self.assertEqual(args.seed, 10)
        self.assertTrue(args.stats)
        self.assertTrue(args.no_gui)


class ConfigLoaderTests(unittest.TestCase):
    def _simple_args(self, **overrides):
        data = {
            "preset": "medium",
            "steps": 50,
            "seed": 42,
            "stats": False,
            "gui": False,
            "no_gui": False,
        }
        data.update(overrides)
        return SimpleNamespace(**data)

    def test_seed_controls_initial_patron_timers(self):
        loader_a = ConfigLoader()
        loader_b = ConfigLoader()

        config_a = loader_a.load_from_args(self._simple_args(seed=99))
        config_b = loader_b.load_from_args(self._simple_args(seed=99))
        self.assertEqual(
            [patron.timer for patron in config_a.patrons[:8]],
            [patron.timer for patron in config_b.patrons[:8]],
        )

        config_c = loader_a.load_from_args(self._simple_args(seed=11))
        self.assertNotEqual(
            [patron.timer for patron in config_a.patrons[:8]],
            [patron.timer for patron in config_c.patrons[:8]],
        )

    def test_steps_clamped_to_minimum(self):
        loader = ConfigLoader()
        config = loader.load_from_args(self._simple_args(steps=-5))
        self.assertEqual(config.steps, 1)

    def test_gui_flags_set_headless_mode(self):
        loader = ConfigLoader()
        config = loader.load_from_args(self._simple_args(gui=True, no_gui=False))
        self.assertTrue(config.interactive)
        self.assertFalse(config.headless)

        config_headless = loader.load_from_args(self._simple_args(gui=False, no_gui=True))
        self.assertFalse(config_headless.interactive)
        self.assertTrue(config_headless.headless)

    def test_preset_controls_patron_count(self):
        loader = ConfigLoader()
        config_small = loader.load_from_args(self._simple_args(preset="small"))
        config_large = loader.load_from_args(self._simple_args(preset="large"))
        self.assertNotEqual(config_small.num_patrons, config_large.num_patrons)
        self.assertGreater(len(config_large.rides), len(config_small.rides))


if __name__ == "__main__":
    unittest.main()
