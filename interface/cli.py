#!/usr/bin/env python3
"""
CLI Module - Command Line Interface Management
============================================
Handles argument parsing and interactive configuration
"""
import argparse
from simulation import Terrain, build_rides


class CLIManager:
    """Manages command line arguments and interactive setup"""
    
    def __init__(self):
        self.parser = None
        
    def parse_arguments(self):
        """Parse command line arguments"""
        self.parser = argparse.ArgumentParser(
            description="AdventureWorld - junior modular",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            epilog="""
Ejemplos de uso:
  python3 adventureworld.py                           # Configuración por defecto
  python3 adventureworld.py -i                       # Modo interactivo
  python3 adventureworld.py --config config.yaml     # Configuración desde YAML
  python3 adventureworld.py --rides-csv rides.csv --stats  # CSV + estadísticas
            """
        )
        
        self.parser.add_argument("-i", "--interactive", action="store_true", 
                               help="Modo interactivo")
        self.parser.add_argument("--config", default=None, 
                               help="Archivo YAML de configuración completa")
        self.parser.add_argument("--map-csv", default=None, 
                               help="CSV del mapa (0=libre,1=barrera)")
        self.parser.add_argument("--rides-csv", default=None, 
                               help="CSV simple de rides")
        self.parser.add_argument("--patrons-csv", default=None, 
                               help="CSV simple de número de personas")
        self.parser.add_argument("--steps", type=int, default=300, 
                               help="Pasos de simulación")
        self.parser.add_argument("--stats", action="store_true", 
                               help="Subplot de estadísticas en vivo")
        self.parser.add_argument("--seed", type=int, default=None, 
                               help="Semilla aleatoria (reproducible)")
        
        return self.parser.parse_args()
    
    def interactive_setup(self):
        """Interactive configuration setup"""
        print("Modo interactivo (Enter = default)")
        try:
            width = int(input("Ancho [100]: ") or 100)
            height = int(input("Alto [70]: ") or 70)
            n_rides = int(input("Rides [2]: ") or 2)
            num_patrons = int(input("Personas [60]: ") or 60)
        except (ValueError, EOFError, KeyboardInterrupt):
            print("\nInput interrupted, using default values")
            width, height, n_rides, num_patrons = 100, 70, 2, 60

        terrain = Terrain.from_size(width, height)

        rides_params = []
        for i in range(n_rides):
            print(f"Ride #{i+1}")
            rtype = (input("Tipo (pirate/ferris) [pirate]: ") or "pirate").strip().lower()
            cap = int(input("Capacidad [12]: ") or 12)
            dur = int(input("Duración [40]: ") or 40)
            x = int(input("BBox x [10]: ") or 10)
            y = int(input("BBox y [10]: ") or 10)
            w = int(input("BBox ancho [20]: ") or 20)
            h = int(input("BBox alto [12]: ") or 12)
            rides_params.append({
                "type": rtype, "capacity": cap, "duration": dur, "bbox": (x, y, w, h)
            })

        rides = build_rides(rides_params, terrain)
        return terrain, rides, num_patrons