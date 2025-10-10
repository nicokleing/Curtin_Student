#!/usr/bin/env python3
"""Configuration loader for arguments, YAML, CSV, and presets."""
import random
from types import SimpleNamespace
from interface.presets import PRESETS
from simulation import Terrain, read_rides_csv, read_patrons_csv, build_rides, load_config_yaml, print_final_config
from simulation.autoplace import auto_place
from models import PatronType, Patron


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

        if mode == "simple":
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
        
        # CSV configuration mode  
        elif args.map_csv or args.rides_csv or args.patrons_csv:
            terrain, rides, num_patrons = self._load_from_csv(args)
            self.config_source = "csv"
        
        # Default configuration
        else:
            terrain, rides, num_patrons = self._load_default_config()
            self.config_source = "default"
        
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
        config.steps = args.steps
        config.show_stats = args.stats
        config.seed = args.seed
        config.save_run = getattr(args, 'save_run', False)

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
            spawns = [tuple(int(v) for v in p) for p in terrain_cfg.get('entrances', [])]
            exits = [tuple(int(v) for v in p) for p in terrain_cfg.get('exits', [])]
            terrain = Terrain(width, height, grid, spawns or None, exits or None)
        else:
            width = terrain_cfg.get('width')
            height = terrain_cfg.get('height')
            if width is None or height is None:
                raise ValueError("Terrain definition requires width and height")
            obstacles = [tuple(b) for b in terrain_cfg.get('obstacles', [])]
            spawns = [tuple(int(v) for v in p) for p in terrain_cfg.get('entrances', [])]
            exits = [tuple(int(v) for v in p) for p in terrain_cfg.get('exits', [])]
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
        if args.map_csv:
            terrain = Terrain.from_csv(args.map_csv)
        else:
            terrain = Terrain.from_csv('data/map1.csv')  # Default
            
        # Load rides
        if args.rides_csv:
            rides_data = read_rides_csv(args.rides_csv)
        else:
            rides_data = read_rides_csv('data/rides.csv')  # Default
            
        rides = build_rides(rides_data, terrain)
        
        # Load patrons count
        if args.patrons_csv:
            num_patrons = read_patrons_csv(args.patrons_csv)
        else:
            num_patrons = 60  # Default
            
        return terrain, rides, num_patrons
    
    def _load_default_config(self):
        """Load default configuration"""
        terrain = Terrain.from_csv('data/map1.csv')
        rides_data = read_rides_csv('data/rides.csv') 
        rides = build_rides(rides_data, terrain)
        num_patrons = 60
        
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
