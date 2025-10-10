"""Configuration loader for arguments, YAML, CSV, and presets."""
import random
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, List, Sequence, Tuple

from adventure.config.presets import PRESETS
from adventure.patrons import Patron, PatronType
from adventure.sim.autoplace import auto_place
from adventure.terrain import Terrain
from adventure.utils.io import (
    build_rides,
    load_config_yaml,
    parse_rides_mix,
    print_final_config,
    read_params_csv,
    read_patrons_csv,
    read_rides_csv,
)

DEFAULT_MAP = Path("configs/map1.csv")
DEFAULT_RIDES = Path("configs/rides.csv")

def _coerce_point(raw_point: Sequence[int | float]) -> Tuple[int, int]:
    if len(raw_point) < 2:
        raise ValueError("Terrain points must provide at least two coordinates")
    return int(raw_point[0]), int(raw_point[1])


class ConfigLoader:
    """Load and manage configuration from various sources."""
    
    def __init__(self):
        pass
    
    def load_from_args(self, args, cli_manager=None):
        """Load configuration based on parsed arguments"""
        
        # Set random seed if provided
        if args.seed is not None:
            random.seed(args.seed)
            
        mode = getattr(args, "mode", "simple") or "simple"

        if mode == "simple" and not self._has_custom_inputs(args):
            terrain, rides, num_patrons = self._load_from_preset(getattr(args, "preset", "medium"))
            self.config_source = f"preset:{getattr(args, 'preset', 'medium')}"

        # Interactive wizard mode
        elif getattr(args, "wizard", False):
            if cli_manager:
                terrain, rides, num_patrons = cli_manager.interactive_setup()
                self.config_source = "wizard"
            else:
                raise ValueError("CLI manager required for wizard mode")
        
        # YAML configuration mode
        elif args.config:
            terrain, rides, num_patrons = self._load_from_yaml(args.config)
            self.config_source = "yaml"
        
        # Custom configuration via CSV overrides
        elif self._has_custom_inputs(args):
            terrain, rides, num_patrons = self._load_from_csv(args)
            self.config_source = "custom"
        
        # Default configuration
        else:
            terrain, rides, num_patrons = self._load_default_config()
            self.config_source = "default"
        
        params_overrides = read_params_csv(getattr(args, "params_csv", None))
        steps = self._resolve_int_override(params_overrides.get("steps"), getattr(args, "steps", 300), minimum=1, label="steps")
        seed = self._resolve_optional_int(params_overrides.get("seed"), getattr(args, "seed", None), label="seed")
        patrons_override = getattr(args, "patrons_override", None)
        if patrons_override is None and params_overrides.get("patrons"):
            patrons_override = self._resolve_int_override(
                params_overrides.get("patrons"), num_patrons, minimum=1, label="patrons"
            )

        if patrons_override is not None:
            num_patrons = patrons_override

        # Create configuration object
        config = SimpleNamespace()
        config.terrain = terrain
        # If rides is already a list of Ride objects, use it; otherwise build from data
        if rides and hasattr(rides[0], 'name'):  # Check if it's already Ride objects
            config.rides = rides
        else:
            config.rides = build_rides(rides, terrain)  # Convert ride data to ride objects

        # Store baseline state for resets once rides are placed
        if hasattr(config.terrain, 'capture_baseline'):
            config.terrain.capture_baseline()
        config.num_patrons = num_patrons
        config.steps = steps
        config.show_stats = args.stats
        config.seed = seed
        config.save_run = getattr(args, 'save_run', False)
        config.log_path = getattr(args, 'log_path', None)
        config.config_source = self.config_source

        force_headless = bool(getattr(args, 'no_gui', False))
        force_gui = bool(getattr(args, 'gui', False))

        if mode == "advanced" and getattr(args, "wizard", False):
            if force_headless:
                print("Wizard mode needs the window, ignoring --no-gui.")
            force_headless = False
            force_gui = True

        if force_gui:
            force_headless = False

        config.headless = force_headless

        config.kpi_buffer_size = max(1, getattr(args, 'kpi_buffer_size', 240))
        config.kpi_warmup = max(0, getattr(args, 'kpi_warmup', 5))
        config.kpi_interval = max(0.0, getattr(args, 'kpi_interval', 0.0))
        config.kpi_style = getattr(args, 'kpi_style', 'default') or 'default'
        save_kpis = getattr(args, 'save_kpis', None)
        config.save_kpis = save_kpis if save_kpis else None
        config.sat_alpha = max(0.0, float(getattr(args, 'sat_alpha', 0.6)))
        config.sat_beta = max(0.0, float(getattr(args, 'sat_beta', 0.8)))
        config.sat_gamma = max(0.0, float(getattr(args, 'sat_gamma', 0.5)))
        config.sat_ema = min(0.99, max(0.0, float(getattr(args, 'sat_ema', 0.9))))
        default_interactive = not config.headless
        if force_gui:
            default_interactive = True
        config.interactive = default_interactive

        if config.interactive:
            config.mode = 'interactive'
        elif config.headless:
            config.mode = 'headless'
        else:
            config.mode = 'batch'
        
        # Create patrons with Epic 2 diversity
        config.patrons = self._create_patrons(config.terrain, num_patrons)
        
        # Print final configuration
        if not getattr(args, 'no_summary', False):
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

    def _load_from_preset(self, preset_name):
        key = (preset_name or "medium").strip().lower()
        if key not in PRESETS:
            raise ValueError(f"Unknown preset '{preset_name}'")

        preset = PRESETS[key]
        terrain = Terrain.from_size(preset["width"], preset["height"])
        rides_params = [ride.copy() for ride in preset["rides"]]

        placed, warnings = auto_place(rides_params, terrain.width, terrain.height, min_gap=3)
        if warnings:
            for msg in warnings:
                print(f"Warning: {msg}")

        if not placed:
            raise ValueError("Unable to place rides for preset terrain size")

        return terrain, placed, preset["visitors"]
    
    def _load_from_yaml(self, file_path):
        """Load configuration from YAML file"""
        data = load_config_yaml(file_path)
        if data is None:
            raise ValueError(f"Failed to read configuration file: {file_path}")

        terrain_cfg = data.get('terrain', {})
        if not terrain_cfg:
            raise ValueError("YAML missing 'terrain' section")

        if 'grid' in terrain_cfg:
            raw_grid = terrain_cfg['grid']
            if not isinstance(raw_grid, list):
                raise ValueError("Terrain grid must be a list of rows")
            grid = [[int(cell) for cell in row] for row in raw_grid]
            if not grid:
                raise ValueError("Terrain grid is empty")
            width = len(grid[0])
            height = len(grid)
            if any(len(row) != width for row in grid):
                raise ValueError("Terrain grid rows must be the same length")
            spawns: List[Tuple[int, int]] = [
                _coerce_point(p) for p in terrain_cfg.get('entrances', [])
            ]
            exits: List[Tuple[int, int]] = [
                _coerce_point(p) for p in terrain_cfg.get('exits', [])
            ]
            terrain = Terrain(width, height, grid, spawns or None, exits or None)
        else:
            width = terrain_cfg.get('width')
            height = terrain_cfg.get('height')
            if width is None or height is None:
                raise ValueError("Terrain definition requires width and height")
            obstacles = [tuple(b) for b in terrain_cfg.get('obstacles', [])]
            spawns: List[Tuple[int, int]] = [
                _coerce_point(p) for p in terrain_cfg.get('entrances', [])
            ]
            exits: List[Tuple[int, int]] = [
                _coerce_point(p) for p in terrain_cfg.get('exits', [])
            ]
            border = terrain_cfg.get('border', True)
            terrain = Terrain.from_definition(
                width,
                height,
                obstacles=obstacles,
                entrances=spawns,
                exits=exits,
                border=border,
            )

        rides = []
        for ride_data in data.get('rides', []):
            rtype = ride_data.get('type') or ride_data.get('tipo')
            if not rtype:
                raise ValueError("Ride entry missing 'type'")
            capacity = int(ride_data.get('capacity', 20))
            duration = int(ride_data.get('duration', 120))
            if 'bbox' in ride_data:
                bbox_values = ride_data['bbox']
            else:
                position = ride_data.get('position', [0, 0])
                size = ride_data.get('size', [4, 3])
                bbox_values = [position[0], position[1], size[0], size[1]]
            bbox = tuple(int(v) for v in bbox_values)
            rides.append({
                "type": str(rtype).lower(),
                "capacity": capacity,
                "duration": duration,
                "bbox": bbox
            })

        num_patrons = int(data.get('num_patrons', 60))

        return terrain, rides, num_patrons
    
    def _load_from_csv(self, args):
        """Load configuration from CSV files"""
        
        # Load terrain
        map_candidate = getattr(args, "map_path", None) or getattr(args, "map_csv", None)
        terrain = self._safe_load_terrain(map_candidate)

        rides_blueprint = []
        rides_mix = getattr(args, "rides_mix", None)
        if rides_mix:
            try:
                rides_blueprint = parse_rides_mix(rides_mix)
            except ValueError as exc:
                print(f"Warning: {exc}. Falling back to CSV rides.")
                rides_blueprint = []

        if rides_blueprint:
            placed, warnings = auto_place(rides_blueprint, terrain.width, terrain.height, min_gap=3)
            for msg in warnings:
                print(f"Warning: {msg}")
            if placed:
                rides_data = placed
            else:
                fallback_layout = self._compact_place_rides(rides_blueprint, terrain)
                if fallback_layout:
                    print("Warning: Auto placement failed; using compact layout instead.")
                    rides_data = fallback_layout
                else:
                    print("Warning: Could not place rides from mix, using CSV data instead.")
                    rides_data = self._safe_read_rides(getattr(args, "rides_csv", None))
        else:
            rides_data = self._safe_read_rides(getattr(args, "rides_csv", None))

        rides = build_rides(rides_data, terrain)

        patrons_override = getattr(args, "patrons_override", None)
        if patrons_override is not None and patrons_override > 0:
            num_patrons = patrons_override
        else:
            num_patrons = read_patrons_csv(getattr(args, "patrons_csv", None))
            if num_patrons <= 0:
                print("Warning: Patrons CSV produced invalid count; using default 60.")
                num_patrons = 60

        return terrain, rides, num_patrons

    def _compact_place_rides(self, rides_blueprint, terrain):
        usable_width = max(0, terrain.width - 2)
        usable_height = max(0, terrain.height - 2)
        if usable_width <= 0 or usable_height <= 0:
            return []

        count = max(1, len(rides_blueprint))
        slot_width = max(2, usable_width // count)
        slot_width = min(slot_width, usable_width)
        slot_height = max(1, min(usable_height, 4))

        placed = []
        x = 1
        y = 1
        for ride in rides_blueprint:
            if x + slot_width > terrain.width - 1:
                x = 1
                y += slot_height + 1
            if y + slot_height > terrain.height - 1:
                return []
            ride_copy = ride.copy()
            ride_copy["bbox"] = (x, y, slot_width, slot_height)
            placed.append(ride_copy)
            x += slot_width + 1
        return placed
    
    def _load_default_config(self):
        """Load default configuration"""
        terrain = self._safe_load_terrain(None)
        rides_data = self._safe_read_rides(None)
        rides = build_rides(rides_data, terrain)
        num_patrons = read_patrons_csv(None)

        return terrain, rides, num_patrons
    
    def _create_patrons(self, terrain, num_patrons):
        """Create patrons with Epic 2 type diversity"""
        spawns = terrain.spawn_points
        exits = terrain.exit_points
        
        patrons = []
        for i in range(num_patrons):
            # Epic 2: Distribute patron types
            patron_type = self._assign_patron_type(i, num_patrons)
            patron = Patron(name=f"P{i:03d}", spawns=spawns, exits=exits, 
                          terrain=terrain, patron_type=patron_type)
            patrons.append(patron)
            
        return patrons
    
    def _assign_patron_type(self, i, total):
        """Assign patron type based on Epic 2 distribution"""
        # Epic 2 distribution: 25% each type
        type_index = i % 4
        patron_types = [PatronType.ADVENTURER, PatronType.FAMILY, 
                       PatronType.IMPATIENT, PatronType.EXPLORER]
        return patron_types[type_index]

    def _has_custom_inputs(self, args) -> bool:
        return any(
            getattr(args, field, None)
            for field in (
                "map_csv",
                "rides_csv",
                "patrons_csv",
                "map_path",
                "rides_mix",
                "params_csv",
            )
        ) or getattr(args, "patrons_override", None) is not None

    def _safe_load_terrain(self, path_candidate: str | None) -> Terrain:
        paths_to_try = []
        if path_candidate:
            paths_to_try.append(Path(path_candidate))
        paths_to_try.append(DEFAULT_MAP)

        for idx, candidate in enumerate(paths_to_try):
            try:
                return Terrain.from_csv(str(candidate))
            except FileNotFoundError:
                print(f"Warning: Map file not found: {candidate}")
            except Exception as exc:
                print(f"Warning: Unable to load map {candidate}: {exc}")
            if idx == 0:
                print("Using default map instead.")

        width, height = 100, 70
        print("Warning: Falling back to generated empty map.")
        return Terrain.from_size(width, height)

    def _safe_read_rides(self, path_candidate: str | None) -> List[Dict[str, int | str | Tuple[int, int, int, int]]]:
        paths_to_try = []
        if path_candidate:
            paths_to_try.append(Path(path_candidate))
        paths_to_try.append(DEFAULT_RIDES)

        for idx, candidate in enumerate(paths_to_try):
            data = read_rides_csv(str(candidate))
            if data:
                return data
            if idx == 0:
                print(f"Warning: Rides CSV empty or missing: {candidate}. Trying default rides.")

        print("Warning: Using built-in ride defaults.")
        return [
            {"type": "pirate", "capacity": 12, "duration": 30, "bbox": (5, 5, 20, 12)},
            {"type": "ferris", "capacity": 10, "duration": 35, "bbox": (30, 10, 18, 18)},
        ]

    def _resolve_int_override(self, value: str | None, current: int, *, minimum: int, label: str) -> int:
        if value is None:
            return current
        try:
            parsed = int(value)
        except ValueError:
            print(f"Warning: Invalid {label} value '{value}' in params file; keeping {current}.")
            return current
        if parsed < minimum:
            print(f"Warning: {label} must be at least {minimum}; keeping {current}.")
            return current
        return parsed

    def _resolve_optional_int(self, value: str | None, current: int | None, *, label: str) -> int | None:
        if value is None or value == "":
            return current
        try:
            return int(value)
        except ValueError:
            print(f"Warning: Invalid {label} value '{value}' in params file; keeping current setting.")
            return current
