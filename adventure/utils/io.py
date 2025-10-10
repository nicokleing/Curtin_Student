# -*- coding: utf-8 -*-
"""Utilities for CSV reading, YAML config loading and ride construction."""
from __future__ import annotations

import csv
from typing import Any, Dict, Iterable, List, Optional

from adventure.rides import FerrisWheel, PirateShip, SpinnerRide
from adventure.rides.roller_coaster import RollerCoaster
from adventure.patrons.patron_types import RIDE_CATEGORY_MAP

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:  # pragma: no cover - handled gracefully at runtime
    YAML_AVAILABLE = False
    print("Warning: PyYAML not available. Install with: pip install pyyaml")


RIDE_RATINGS = {
    "pirate": 0.8,
    "ferris": 0.6,
    "coaster": 0.9,
    "spinner": 0.7,
}

DEFAULT_RIDE_TEMPLATES = {
    "pirate": {"capacity": 12, "duration": 30},
    "ferris": {"capacity": 10, "duration": 35},
    "roller": {"capacity": 16, "duration": 32},
    "spinner": {"capacity": 14, "duration": 28},
}

RIDE_TYPE_ALIASES = {
    "coaster": "roller",
    "spinner": "spinner",
    "hurricane": "spinner",
}


def parse_rides_mix(raw: Optional[str]) -> List[Dict[str, Any]]:
    """Parse ride mix string like "pirate:2,ferris" into ride parameter dicts."""
    if raw is None:
        return []

    tokens = [segment.strip() for segment in str(raw).split(",") if segment.strip()]
    if not tokens:
        raise ValueError("Ride mix cannot be empty")

    rides: List[Dict[str, Any]] = []
    for token in tokens:
        parts = token.split(":")
        if len(parts) == 1:
            ride_key = parts[0].strip().lower()
            count = 1
        elif len(parts) == 2:
            ride_key = parts[0].strip().lower()
            try:
                count = int(parts[1])
            except ValueError as exc:
                raise ValueError(f"Invalid ride count in '{token}': {exc}") from exc
        else:
            raise ValueError("Use type or type:count format for --rides")

        ride_key = RIDE_TYPE_ALIASES.get(ride_key, ride_key)
        if ride_key not in DEFAULT_RIDE_TEMPLATES:
            valid_types = ", ".join(sorted(DEFAULT_RIDE_TEMPLATES))
            raise ValueError(f"Unknown ride type '{ride_key}'. Valid: {valid_types}")
        if count <= 0:
            raise ValueError("Ride counts must be positive")

        template = DEFAULT_RIDE_TEMPLATES[ride_key]
        for _ in range(count):
            rides.append(
                {
                    "type": ride_key,
                    "capacity": template["capacity"],
                    "duration": template["duration"],
                }
            )

    return rides


def read_rides_csv(path: Optional[str]) -> List[Dict[str, Any]]:
    """Read rides CSV: type,capacity,duration,x,y,width,height per line."""
    rides: List[Dict[str, Any]] = []
    if path is None:
        return rides

    try:
        with open(path, "r", encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split(",")
                if len(parts) != 7:
                    print(
                        f"Error: Line {line_number} in {path} has {len(parts)} fields, expected 7"
                    )
                    print("Expected format: type,capacity,duration,x,y,width,height")
                    continue

                try:
                    ride_type = parts[0].strip().lower()
                    capacity = int(parts[1])
                    duration = int(parts[2])
                    x = int(parts[3])
                    y = int(parts[4])
                    width = int(parts[5])
                    height = int(parts[6])
                    rides.append(
                        {
                            "type": ride_type,
                            "capacity": capacity,
                            "duration": duration,
                            "bbox": (x, y, width, height),
                        }
                    )
                except ValueError as exc:
                    print(
                        f"Error: Invalid numeric value on line {line_number} in {path}: {exc}"
                    )
                    continue

    except FileNotFoundError:
        print(f"Error: Rides CSV file not found: {path}")
        return []
    except Exception as exc:  # pragma: no cover
        print(f"Error reading rides CSV file {path}: {exc}")
        return []

    return rides


def read_patrons_csv(path: Optional[str]) -> int:
    """Read patrons CSV: single integer with total number of patrons."""
    if path is None:
        return 60

    try:
        with open(path, "r", encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    return int(line)
                except ValueError:
                    print(
                        f"Error: Invalid number format on line {line_number} in {path}: '{line}'"
                    )
                    print("Expected: A single integer representing number of patrons")
                    continue
        print(f"Warning: No valid patron count found in {path}, using default: 60")
        return 60

    except FileNotFoundError:
        print(f"Error: Patrons CSV file not found: {path}")
        return 60
    except Exception as exc:  # pragma: no cover
        print(f"Error reading patrons CSV file {path}: {exc}")
        return 60


def read_params_csv(path: Optional[str]) -> Dict[str, str]:
    """Read key,value overrides from a CSV file."""
    overrides: Dict[str, str] = {}
    if path is None:
        return overrides

    try:
        with open(path, newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or {"key", "value"} - set(reader.fieldnames):
                print(f"Warning: Params CSV must contain 'key' and 'value' columns: {path}")
                return overrides
            for row in reader:
                key = (row.get("key") or "").strip().lower()
                value = (row.get("value") or "").strip()
                if key:
                    overrides[key] = value
    except FileNotFoundError:
        print(f"Warning: Params CSV file not found: {path}")
    except Exception as exc:
        print(f"Warning: Error reading params CSV {path}: {exc}")

    return overrides


def load_config_yaml(path: Optional[str]) -> Optional[Dict[str, Any]]:
    """Load configuration from a YAML file and return it as a dict."""
    if not YAML_AVAILABLE:
        print("Error: PyYAML is required to load YAML files")
        print("Install with: pip install pyyaml")
        return None

    if path is None:
        return None

    try:
        with open(path, "r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file not found: {path}")
        return None
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML: {exc}")
        return None
    except Exception as exc:  # pragma: no cover
        print(f"Unexpected error loading configuration: {exc}")
        return None


def print_final_config(
    terrain,
    rides,
    num_patrons,
    steps,
    seed,
    show_stats,
    config_source="default",
) -> None:
    """Print the final configuration used for the simulation."""
    print("\n" + "=" * 50)
    print("FINAL CONFIGURATION USED")
    print("=" * 50)
    print(f"Configuration source: {config_source}")
    print(f"Park dimensions: {terrain.width} x {terrain.height}")
    print(f"Number of rides: {len(rides)}")

    for index, ride in enumerate(rides, start=1):
        if isinstance(ride, PirateShip):
            ride_type = "Pirate Ship"
        elif isinstance(ride, FerrisWheel):
            ride_type = "Ferris Wheel"
        elif isinstance(ride, RollerCoaster):
            ride_type = "Roller Coaster"
        else:
            ride_type = ride.__class__.__name__
        print(
            f"   {index}. {ride_type} - Capacity: {ride.capacity}, Duration: {ride.duration}"
        )

    print(f"Visitors: {num_patrons}")
    print(f"Simulation steps: {steps}")
    print(f"Random seed: {seed if seed is not None else 'Random'}")
    print(f"Live statistics: {'Yes' if show_stats else 'No'}")
    print("=" * 50 + "\n")


def build_rides(rides_params: Iterable[Dict[str, Any]], terrain) -> List[Any]:
    """Create ride instances from params and mark their bounding boxes."""
    rides: List[Any] = []
    for index, params in enumerate(rides_params):
        name = f"Ride{index + 1}"
        ride_type = params["type"]
        capacity = params["capacity"]
        duration = params["duration"]
        bbox = params["bbox"]
        if ride_type.startswith("pir"):
            ride = PirateShip(name, capacity, duration, bbox)
        elif ride_type.startswith("fer"):
            ride = FerrisWheel(name, capacity, duration, bbox, cabins=8)
        elif ride_type.startswith("spin"):
            ride = SpinnerRide(name, capacity, duration, bbox)
        elif ride_type.startswith("coast") or ride_type.startswith("roller"):
            ride = RollerCoaster(name, capacity, duration, bbox)
        else:
            ride = PirateShip(name, capacity, duration, bbox)
        ride.rating = RIDE_RATINGS.get(ride.ride_type, 0.6)
        setattr(ride, "category", RIDE_CATEGORY_MAP.get(ride.ride_type))
        # allow optional per-ride queue capacity from params (None = infinite)
        try:
            ride.queue_limit = params.get("queue_limit", None)
        except Exception:
            # params may be a mapping-like object; ignore if not present
            ride.queue_limit = None
        try:
            terrain.add_ride(ride)
        except ValueError as exc:
            raise ValueError(f"Cannot place ride {name}: {exc}") from exc
        rides.append(ride)
    return rides
