
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AdventureWorld - versión junior modular
- CLI simple (-i / --map-csv --rides-csv --patrons-csv)
- Crea terreno, rides y patrons
- Corre la simulación y dibuja
"""
import argparse
import random
import matplotlib.pyplot as plt

from terrain import Terrain
from patrons import Patron
from utils import read_rides_csv, read_patrons_csv, build_rides, load_config_yaml, print_final_config


def parse_args():
    parser = argparse.ArgumentParser(
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
    parser.add_argument("-i", "--interactive", action="store_true", help="Modo interactivo")
    parser.add_argument("--config", default=None, help="Archivo YAML de configuración completa")
    parser.add_argument("--map-csv", default=None, help="CSV del mapa (0=libre,1=barrera)")
    parser.add_argument("--rides-csv", default=None, help="CSV simple de rides")
    parser.add_argument("--patrons-csv", default=None, help="CSV simple de número de personas")
    parser.add_argument("--steps", type=int, default=300, help="Pasos de simulación")
    parser.add_argument("--stats", action="store_true", help="Subplot de estadísticas en vivo")
    parser.add_argument("--seed", type=int, default=None, help="Semilla aleatoria (reproducible)")
    return parser.parse_args()


def interactive_setup():
    """Pide datos por consola y devuelve (terrain, rides, num_patrons)."""
    print("Modo interactivo (Enter = default)")
    try:
        width = int(input("Ancho [100]: ") or 100)
        height = int(input("Alto [70]: ") or 70)
        n_rides = int(input("Rides [2]: ") or 2)
        num_patrons = int(input("Personas [60]: ") or 60)
    except ValueError:
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


class Simulation:
    """Simulación simple: actualiza rides y personas y dibuja."""
    def __init__(self, terrain, rides, num_patrons, steps, show_stats):
        self.terrain = terrain
        self.rides = rides
        self.steps = steps
        self.show_stats = show_stats

        spawns = terrain.spawn_points
        exits = terrain.exit_points

        self.patrons = [Patron(name=f"P{i:03d}", spawns=spawns, exits=exits, terrain=terrain)
                        for i in range(num_patrons)]

        if show_stats:
            self.fig = plt.figure(figsize=(10, 6))
            self.ax_map = self.fig.add_subplot(1, 2, 1)
            self.ax_stats = self.fig.add_subplot(1, 2, 2)
        else:
            self.fig, self.ax_map = plt.subplots(figsize=(8, 6))
            self.ax_stats = None

        self.riders_now = []
        self.queued_now = []
        self.departed_total = []
        self.time = 0

    def step(self):
        for ride in self.rides:
            ride.step_change(self.time)
        for p in self.patrons:
            p.step_change(self.time, self.rides)

        riders = sum(len(r.riders) for r in self.rides)
        queued = sum(len(r.queue) for r in self.rides)
        departed = sum(1 for p in self.patrons if p.state == "left")
        self.riders_now.append(riders)
        self.queued_now.append(queued)
        self.departed_total.append(departed)
        self.time += 1

    def draw(self):
        self.ax_map.clear()
        self.ax_map.set_xlim(-1, self.terrain.width + 1)
        self.ax_map.set_ylim(-1, self.terrain.height + 1)
        self.ax_map.set_aspect("equal")
        self.ax_map.set_title("AdventureWorld Park (junior modular)")
        self.ax_map.grid(True, alpha=0.2)

        self.terrain.plot(self.ax_map)
        for ride in self.rides:
            ride.plot(self.ax_map, self.time)
        for p in self.patrons:
            p.plot(self.ax_map)

        if self.ax_stats is not None:
            self.ax_stats.clear()
            self.ax_stats.set_title("Live Stats")
            self.ax_stats.set_xlabel("timestep")
            self.ax_stats.plot(self.riders_now, label="riding")
            self.ax_stats.plot(self.queued_now, label="queueing")
            self.ax_stats.plot(self.departed_total, label="departed")
            self.ax_stats.legend(loc="upper left")
            self.ax_stats.grid(True, alpha=0.3)

        plt.pause(0.001)

    def run(self):
        for _ in range(self.steps):
            self.step()
            self.draw()
        print("Fin de la simulación. Cierra la ventana para salir.")
        plt.show()


if __name__ == "__main__":
    args = parse_args()
    
    # Configurar semilla aleatoria si se especifica
    if args.seed is not None:
        random.seed(args.seed)

    # Determinar fuente de configuración y cargar parámetros
    config_source = "default"
    
    if args.config:
        # Prioridad 1: Configuración YAML
        config = load_config_yaml(args.config)
        if config:
            config_source = "yaml"
            
            # Configuración del parque
            park_config = config.get('park', {})
            terrain = Terrain.from_size(
                park_config.get('width', 100), 
                park_config.get('height', 70)
            )
            
            # Configuración de atracciones
            rides_params = []
            for ride_config in config.get('rides', []):
                rides_params.append({
                    'type': ride_config.get('type', 'pirate'),
                    'capacity': ride_config.get('capacity', 12),
                    'duration': ride_config.get('duration', 40),
                    'bbox': tuple(ride_config.get('bbox', [10, 10, 20, 12]))
                })
            
            # Si no hay rides en YAML, usar defaults
            if not rides_params:
                rides_params = [
                    {"type": "pirate", "capacity": 12, "duration": 40, "bbox": (10, 10, 20, 12)},
                    {"type": "ferris", "capacity": 20, "duration": 70, "bbox": (45, 15, 20, 20)},
                ]
            
            rides = build_rides(rides_params, terrain)
            
            # Configuración de visitantes
            num_patrons = config.get('patrons', {}).get('count', 60)
            
            # Configuración de simulación (los argumentos CLI tienen precedencia)
            simulation_config = config.get('simulation', {})
            steps = args.steps if args.steps != 300 else simulation_config.get('steps', 300)
            stats = args.stats or simulation_config.get('stats', False)
            seed = args.seed if args.seed is not None else simulation_config.get('seed', None)
            
            # Aplicar semilla si viene del YAML y no se especificó en CLI
            if seed is not None and args.seed is None:
                random.seed(seed)
        else:
            # Si falla la carga de YAML, usar configuración por defecto
            print("Usando configuración por defecto debido a errores en YAML...")
            config_source = "default"
            terrain = Terrain.from_size(100, 70)
            rides_params = [
                {"type": "pirate", "capacity": 12, "duration": 40, "bbox": (10, 10, 20, 12)},
                {"type": "ferris", "capacity": 20, "duration": 70, "bbox": (45, 15, 20, 20)},
            ]
            rides = build_rides(rides_params, terrain)
            num_patrons = 60
            steps = args.steps
            stats = args.stats
            seed = args.seed
    
    elif args.interactive:
        # Prioridad 2: Modo interactivo
        config_source = "interactive"
        terrain, rides, num_patrons = interactive_setup()
        steps = args.steps
        stats = args.stats 
        seed = args.seed
        
    else:
        # Prioridad 3: Archivos CSV individuales o defaults
        if args.rides_csv or args.patrons_csv or args.map_csv:
            config_source = "csv"
        else:
            config_source = "default"
            
        terrain = Terrain.from_csv(args.map_csv) if args.map_csv else Terrain.from_size(100, 70)
        rides_params = read_rides_csv(args.rides_csv) if args.rides_csv else [
            {"type": "pirate", "capacity": 12, "duration": 40, "bbox": (10, 10, 20, 12)},
            {"type": "ferris", "capacity": 20, "duration": 70, "bbox": (45, 15, 20, 20)},
        ]
        rides = build_rides(rides_params, terrain)
        num_patrons = read_patrons_csv(args.patrons_csv) if args.patrons_csv else 60
        steps = args.steps
        stats = args.stats
        seed = args.seed

    # Imprimir configuración final utilizada
    print_final_config(terrain, rides, num_patrons, steps, seed, stats, config_source)

    # Ejecutar simulación
    sim = Simulation(terrain, rides, num_patrons, steps=steps, show_stats=stats)
    sim.run()
