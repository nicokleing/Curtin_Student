#!/usr/bin/env python3
"""
CLI module - command line interface.
=====================================
Handles argument parsing and interactive setup.
"""
import argparse
from simulation import Terrain, build_rides


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
  python3 adventureworld.py                           # Default configuration
  python3 adventureworld.py -i                       # Interactive mode
  python3 adventureworld.py --config config.yaml     # Load full YAML configuration
  python3 adventureworld.py --rides-csv rides.csv --stats  # CSV + live stats
            """
        )
        
        self.parser.add_argument("-i", "--interactive", action="store_true", 
                               help="Interactive mode")
        self.parser.add_argument("--config", default=None, 
                               help="Full configuration YAML file")
        self.parser.add_argument("--map-csv", default=None, 
                               help="Map CSV (0=free,1=blocked)")
        self.parser.add_argument("--rides-csv", default=None, 
                               help="Simple rides CSV")
        self.parser.add_argument("--patrons-csv", default=None, 
                               help="CSV with total number of patrons")
        self.parser.add_argument("--steps", type=int, default=300, 
                               help="Simulation steps")
        self.parser.add_argument("--stats", action="store_true", 
                               help="Enable live statistics subplot")
        self.parser.add_argument("--seed", type=int, default=None, 
                               help="Random seed (for reproducibility)")
        self.parser.add_argument("--save-run", action="store_true",
                               help="Export results (CSV, JSON, PNG) at the end")
        
        return self.parser.parse_args()
    
    def interactive_setup(self):
        """Interactive configuration setup"""
        print("Interactive mode (press Enter to accept defaults)")
        try:
            width = int(input("Width [100]: ") or 100)
            height = int(input("Height [70]: ") or 70)
            n_rides = int(input("Rides [2]: ") or 2)
            num_patrons = int(input("Visitors [60]: ") or 60)
        except (ValueError, EOFError, KeyboardInterrupt):
            print("\nInput interrupted, using default values")
            width, height, n_rides, num_patrons = 100, 70, 2, 60

        terrain = Terrain.from_size(width, height)

        rides_params = []
        for i in range(n_rides):
            print(f"Ride #{i+1}")
            rtype = (input("Type (pirate/ferris) [pirate]: ") or "pirate").strip().lower()
            cap = int(input("Capacity [12]: ") or 12)
            dur = int(input("Duration [40]: ") or 40)
            x = int(input("BBox x [10]: ") or 10)
            y = int(input("BBox y [10]: ") or 10)
            w = int(input("BBox width [20]: ") or 20)
            h = int(input("BBox height [12]: ") or 12)
            rides_params.append({
                "type": rtype, "capacity": cap, "duration": dur, "bbox": (x, y, w, h)
            })

        rides = build_rides(rides_params, terrain)
        return terrain, rides, num_patrons
