"""Build runtime configuration from presets and simple flags."""

import random
from types import SimpleNamespace
from typing import List

from adventure.config.presets import PRESETS
from adventure.patrons import Patron, PatronType
from adventure.sim.autoplace import auto_place
from adventure.terrain import Terrain
from adventure.utils.io import build_rides, print_final_config


class ConfigLoader:
    """Load configuration from presets with minimal overrides."""

    def load_from_args(self, args, cli_manager=None):
        """Read command line arguments and assemble the config namespace."""

        preset_name = getattr(args, "preset", "medium")
        terrain, rides_blueprint, num_patrons = self._load_from_preset(preset_name)
        self.config_source = f"preset:{preset_name}"

        seed = getattr(args, "seed", None)
        if seed is not None:
            random.seed(seed)

        steps = max(1, int(getattr(args, "steps", 300)))

        config = SimpleNamespace()
        config.terrain = terrain
        config.rides = build_rides(rides_blueprint, terrain)

        if hasattr(config.terrain, "capture_baseline"):
            config.terrain.capture_baseline()

        config.num_patrons = num_patrons
        config.patrons = self._create_patrons(terrain, num_patrons)
        config.steps = steps
        config.show_stats = bool(getattr(args, "stats", False))
        config.seed = seed
        config.save_run = bool(getattr(args, "save_run", False))
        config.log_path = getattr(args, "log_path", None)
        config.config_source = self.config_source

        force_headless = bool(getattr(args, "no_gui", False))
        if bool(getattr(args, "gui", False)):
            force_headless = False
        config.headless = force_headless
        config.interactive = not config.headless
        config.mode = "interactive" if config.interactive else "batch"

        config.kpi_buffer_size = max(1, int(getattr(args, "kpi_buffer_size", 240)))
        config.kpi_warmup = max(0, int(getattr(args, "kpi_warmup", 5)))
        config.kpi_interval = max(0.0, float(getattr(args, "kpi_interval", 0.0)))
        config.kpi_style = getattr(args, "kpi_style", "default") or "default"
        config.save_kpis = getattr(args, "save_kpis", None)
        config.sat_alpha = 0.6
        config.sat_beta = 0.8
        config.sat_gamma = 0.5
        config.sat_ema = 0.9

        print_final_config(
            config.terrain,
            config.rides,
            len(config.patrons),
            config.steps,
            config.seed,
            config.show_stats,
            self.config_source,
        )

        return config

    def _load_from_preset(self, preset_name: str):
        key = (preset_name or "medium").strip().lower()
        if key not in PRESETS:
            raise ValueError(f"Unknown preset '{preset_name}'")

        preset = PRESETS[key]
        terrain = Terrain.from_size(preset["width"], preset["height"])

        ride_templates = [ride.copy() for ride in preset["rides"]]
        placed, warnings = auto_place(ride_templates, terrain.width, terrain.height, min_gap=3)
        for message in warnings:
            print(f"Warning: {message}")

        if not placed:
            raise ValueError("Preset rides could not be placed on the terrain")

        return terrain, placed, preset["visitors"]

    def _create_patrons(self, terrain, num_patrons: int) -> List[Patron]:
        spawns = terrain.spawn_points
        exits = terrain.exit_points

        patrons: List[Patron] = []
        for index in range(num_patrons):
            patron_type = self._assign_patron_type(index)
            patron = Patron(
                name=f"P{index:03d}",
                spawns=spawns,
                exits=exits,
                terrain=terrain,
                patron_type=patron_type,
            )
            patrons.append(patron)
        return patrons

    def _assign_patron_type(self, index: int) -> PatronType:
        pattern = [
            PatronType.ADVENTURER,
            PatronType.FAMILY,
            PatronType.IMPATIENT,
            PatronType.EXPLORER,
        ]
        return pattern[index % len(pattern)]
