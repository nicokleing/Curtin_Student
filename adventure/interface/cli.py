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

        return parser
