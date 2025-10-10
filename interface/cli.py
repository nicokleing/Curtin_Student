"""Lightweight command line interface manager."""
import argparse
from pathlib import Path

from adventure.config.presets import PRESETS
from adventure.sim.autoplace import auto_place
from adventure.terrain import Terrain
from adventure.utils.io import build_rides, parse_rides_mix


class CLIManager:
    """Manage command line arguments and interactive configuration."""
    
    def __init__(self):
        self.parser = None
        
    def parse_arguments(self):
        """Parse command line arguments"""
        self.parser = argparse.ArgumentParser(
            description="AdventureWorld - junior modular",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            epilog="""
Examples:
  python3 adventureworld.py --mode simple --preset medium
  python3 adventureworld.py --mode advanced --config config.yaml
  python3 adventureworld.py --mode advanced --wizard
            """
        )

        add_arg = self.parser.add_argument

        add_arg(
            "--mode",
            choices=["simple", "advanced"],
            default="simple",
            help="Select simple presets or advanced options",
        )
        add_arg(
            "--preset",
            default="medium",
            choices=sorted(PRESETS.keys()),
            help="Preset to use when mode is simple",
        )
        add_arg(
            "--list-presets",
            action="store_true",
            help="Show preset details and exit",
        )
        add_arg(
            "--wizard",
            action="store_true",
            help="Launch guided advanced setup",
        )
        add_arg(
            "-i",
            "--interactive",
            action="store_true",
            help="Force GUI window without starting the wizard",
        )
        add_arg("--config", default=None, help="Full configuration YAML file")
        add_arg(
            "-f",
            "--map-csv",
            dest="map_csv",
            default=None,
            help="Map CSV (0=free,1=blocked)",
        )
        add_arg(
            "-r",
            "--rides-csv",
            dest="rides_csv",
            default=None,
            help="Simple rides CSV",
        )
        add_arg(
            "-p",
            "--patrons-csv",
            dest="patrons_csv",
            default=None,
            help="CSV with total number of patrons",
        )
        add_arg(
            "--map",
            dest="map_path",
            default=None,
            help="Override terrain CSV path (alias for --map-csv)",
        )
        add_arg(
            "--rides",
            dest="rides_mix",
            default=None,
            help="Comma list like pirate:2,ferris to auto-place rides",
        )
        add_arg(
            "--patrons",
            type=int,
            dest="patrons_override",
            default=None,
            help="Override total number of visitors",
        )
        add_arg(
            "--params",
            dest="params_csv",
            default=None,
            help="CSV with key,value overrides (steps, seed, patrons)",
        )
        add_arg(
            "--log",
            dest="log_path",
            default=None,
            help="Write run summary to this file",
        )
        add_arg("--steps", type=int, default=300, help="Simulation steps")
        add_arg(
            "--stats",
            action="store_true",
            help="Enable live statistics subplot",
        )
        add_arg(
            "--seed",
            type=int,
            default=None,
            help="Random seed (for reproducibility)",
        )
        add_arg(
            "--save-run",
            action="store_true",
            help="Export results (CSV, JSON, PNG) at the end",
        )
        add_arg(
            "--no-gui",
            action="store_true",
            help="Disable matplotlib window (batch mode)",
        )
        add_arg(
            "--gui",
            action="store_true",
            help="Force GUI even if disabled by defaults or other flags",
        )
        add_arg(
            "--kpi-buffer-size",
            type=int,
            default=240,
            help="Max samples to keep for KPI charts",
        )
        add_arg(
            "--kpi-warmup",
            type=int,
            default=5,
            help="Samples required before drawing charts",
        )
        add_arg(
            "--kpi-interval",
            type=float,
            default=0.0,
            help="Seconds to throttle KPI updates (0 = every frame)",
        )
        add_arg(
            "--kpi-style",
            default="default",
            choices=["default", "dark", "minimal", "colorblind"],
            help="Preset style for KPI charts",
        )
        add_arg(
            "--save-kpis",
            default=None,
            help="Directory to export KPI timeline data",
        )
        add_arg(
            "--sat-alpha",
            type=float,
            default=0.6,
            help="Weight applied to normalized wait pressure (0-5)",
        )
        add_arg(
            "--sat-beta",
            type=float,
            default=0.8,
            help="Weight applied to abandonment penalty (0-5)",
        )
        add_arg(
            "--sat-gamma",
            type=float,
            default=0.5,
            help="Weight applied to normalized overcrowding (0-5)",
        )
        add_arg(
            "--sat-ema",
            type=float,
            default=0.9,
            help="EMA smoothing factor for satisfaction line (0-0.99)",
        )
        add_arg("--no-summary", action="store_true", help=argparse.SUPPRESS)

        args = self.parser.parse_args()

        if getattr(args, "interactive", False):
            if getattr(args, "no_gui", False):
                print("Note: --interactive needs a window, ignoring --no-gui.")
                args.no_gui = False
            args.gui = True

        if getattr(args, "gui", False):
            args.no_gui = False

        if args.list_presets:
            self._print_presets()
            self.parser.exit(0)

        if args.mode == "simple" and (
            args.config or args.map_csv or args.rides_csv or args.patrons_csv
            or args.map_path or args.rides_mix or args.params_csv or args.patrons_override is not None
        ):
            print("Note: simple mode ignores advanced configuration flags.")

        self._validate_args(args)
        return args

    def _print_presets(self):
        print("Available presets:")
        for key, preset in PRESETS.items():
            rides = ", ".join(f"{r['type']} (cap {r['capacity']})" for r in preset["rides"])
            print(f"  - {key}: {preset['width']}x{preset['height']} with {preset['visitors']} visitors")
            print(f"    rides: {rides}")
    
    def interactive_setup(self):
        """Interactive configuration setup"""
        print("Interactive mode (press Enter to accept defaults)")
        try:
            width = self._prompt_int("Width", 100, minimum=20)
            height = self._prompt_int("Height", 70, minimum=20)
            n_rides = self._prompt_int("Rides", 2, minimum=1)
            num_patrons = self._prompt_int("Visitors", 60, minimum=1)
            use_autoplace = self._prompt_bool("Auto-place rides?", default=True)
        except (EOFError, KeyboardInterrupt):
            print("\nInput interrupted, using default values")
            width, height, n_rides, num_patrons = 100, 70, 2, 60
            use_autoplace = True

        terrain = Terrain.from_size(width, height)

        rides_params = []
        for i in range(n_rides):
            print(f"Ride #{i+1}")
            rtype = self._prompt_choice("Type", ["pirate", "ferris", "roller"], default="pirate")
            cap = self._prompt_int("Capacity", 12, minimum=1)
            dur = self._prompt_int("Duration", 40, minimum=1)
            rides_params.append({"type": rtype, "capacity": cap, "duration": dur})

        if use_autoplace:
            placed, warnings = auto_place(rides_params, terrain.width, terrain.height, min_gap=3)
            for msg in warnings:
                print(f"Warning: {msg}")
            if placed:
                rides_params = placed
            else:
                print("Not enough space for auto-placement. Switching to manual bounding boxes.")
                rides_params = self._manual_bbox_prompt(rides_params, terrain)
        else:
            rides_params = self._manual_bbox_prompt(rides_params, terrain)

        try:
            rides = build_rides(rides_params, terrain)
        except ValueError as err:
            print(f"Configuration error: {err}")
            raise
        return terrain, rides, num_patrons

    def _manual_bbox_prompt(self, rides, terrain):
        placed = []
        total = max(1, len(rides))
        usable_w = max(1, terrain.width - 2)
        usable_h = max(1, terrain.height - 2)
        base_w = max(1, min(usable_w, max(6, usable_w // max(1, total // 2 or 1))))
        base_h = max(1, min(usable_h, max(6, usable_h // max(1, total))))
        y_cursor = 1

        for idx, ride in enumerate(rides):
            print(f"Define area for ride #{idx+1} ({ride['type']})")
            default_x = 1
            default_y = min(y_cursor, max(1, terrain.height - base_h - 1))
            default_w = min(base_w, usable_w)
            default_h = min(base_h, usable_h)

            while True:
                try:
                    x = int(input(f"BBox x [{default_x}]: ") or default_x)
                    y = int(input(f"BBox y [{default_y}]: ") or default_y)
                    w = int(input(f"BBox width [{default_w}]: ") or default_w)
                    h = int(input(f"BBox height [{default_h}]: ") or default_h)
                except (ValueError, EOFError):
                    print("Invalid values. Try again.")
                    continue

                if self._bbox_fits(x, y, w, h, terrain):
                    placed.append({**ride, "bbox": (x, y, w, h)})
                    break
                print("Bounding box outside the map. Use smaller values or shift the position.")

            y_cursor += default_h + 1

        return placed

    def _bbox_fits(self, x, y, w, h, terrain):
        if w <= 0 or h <= 0:
            return False
        return 0 <= x and 0 <= y and (x + w) <= terrain.width and (y + h) <= terrain.height

    def _prompt_int(self, label, default, *, minimum=None, maximum=None):
        while True:
            raw = input(f"{label} [{default}]: ")
            if raw is None:
                raise EOFError
            text = raw.strip()
            if not text:
                value = default
            else:
                try:
                    value = int(text)
                except ValueError:
                    print("Please enter a whole number.")
                    continue
            if minimum is not None and value < minimum:
                print(f"Enter a value greater than or equal to {minimum}.")
                continue
            if maximum is not None and value > maximum:
                print(f"Enter a value less than or equal to {maximum}.")
                continue
            return value

    def _prompt_bool(self, label, *, default=True):
        suffix = "Y/n" if default else "y/N"
        while True:
            raw = input(f"{label} [{suffix}]: ")
            if raw is None:
                raise EOFError
            text = raw.strip().lower()
            if not text:
                return default
            if text in {"y", "yes"}:
                return True
            if text in {"n", "no"}:
                return False
            print("Please answer with y or n.")

    def _prompt_choice(self, label, options, *, default):
        options_lower = {opt.lower(): opt for opt in options}
        default_lower = default.lower()
        prompt_options = "/".join(options)
        while True:
            raw = input(f"{label} ({prompt_options}) [{default}]: ")
            if raw is None:
                raise EOFError
            text = raw.strip().lower()
            if not text:
                return default_lower
            if text in options_lower:
                return text
            print(f"Choose one of: {', '.join(options)}.")

    def _validate_args(self, args):
        errors = []
        if args.steps <= 0:
            errors.append("--steps must be greater than zero")
        if args.kpi_buffer_size <= 0:
            errors.append("--kpi-buffer-size must be greater than zero")
        if args.kpi_warmup < 0:
            errors.append("--kpi-warmup cannot be negative")
        if args.kpi_interval < 0:
            errors.append("--kpi-interval cannot be negative")
        if args.patrons_override is not None and args.patrons_override <= 0:
            errors.append("--patrons must be greater than zero")

        if args.rides_mix:
            try:
                parse_rides_mix(args.rides_mix)
            except ValueError as exc:
                errors.append(str(exc))

        if args.log_path:
            path = Path(args.log_path)
            if path.exists() and path.is_dir():
                errors.append("--log must target a file, not a directory")

        if errors:
            print("Argument errors:")
            for message in errors:
                print(f"  - {message}")
            parser = self.parser
            if parser is None:
                raise SystemExit(2)
            parser.exit(2)
