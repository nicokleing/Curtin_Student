"""Simple command line interface manager."""

import argparse

from adventure.config.presets import PRESETS


class CLIManager:
    """Parse the basic argument set for the simulator."""

    def __init__(self):
        self.parser = self._build_parser()

    def parse_arguments(self):
        """Parse arguments from sys.argv."""
        return self.parser.parse_args()

    def _build_parser(self):
        parser = argparse.ArgumentParser(description="AdventureWorld park simulator")

        parser.add_argument(
            "--preset",
            default="medium",
            choices=sorted(PRESETS.keys()),
            help="Select terrain and ride layout",
        )
        parser.add_argument(
            "--steps",
            type=int,
            default=300,
            help="Number of simulation steps",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=None,
            help="Random seed",
        )
        parser.add_argument(
            "--stats",
            action="store_true",
            help="Show live KPI subplot",
        )
        parser.add_argument(
            "--gui",
            action="store_true",
            help="Force GUI window",
        )
        parser.add_argument(
            "--no-gui",
            action="store_true",
            help="Disable GUI window",
        )
        parser.add_argument(
            "--save-run",
            action="store_true",
            help="Persist a full export of the simulation run",
        )
        parser.add_argument(
            "--log-path",
            type=str,
            default=None,
            help="Write a textual log to the given file path",
        )
        parser.add_argument(
            "--kpi-buffer-size",
            type=int,
            default=240,
            metavar="STEPS",
            help="Number of steps stored in the KPI rolling window",
        )
        parser.add_argument(
            "--kpi-warmup",
            type=int,
            default=5,
            metavar="STEPS",
            help="Steps ignored before KPI export starts",
        )
        parser.add_argument(
            "--kpi-interval",
            type=float,
            default=0.0,
            metavar="SECONDS",
            help="Seconds between KPI samples (interactive mode)",
        )
        parser.add_argument(
            "--kpi-style",
            type=str,
            default="default",
            help="Matplotlib style to use for KPI charts",
        )
        parser.add_argument(
            "--save-kpis",
            type=str,
            default=None,
            metavar="DIR",
            help="Directory where KPI CSV files should be written",
        )

        return parser
