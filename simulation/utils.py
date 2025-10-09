
# -*- coding: utf-8 -*-
"""Utilities for CSV reading, YAML config loading and ride construction."""
from rides import PirateShip, FerrisWheel

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("Warning: PyYAML not available. Install with: pip install pyyaml")

def read_rides_csv(path):
    """Read rides CSV: type,capacity,duration,x,y,width,height per line."""
    rides = []
    if path is None:
        return rides
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            line_num = 0
            for line in f:
                line_num += 1
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                parts = line.split(",")
                if len(parts) != 7:
                    print(f"Error: Line {line_num} in {path} has {len(parts)} fields, expected 7")
                    print(f"Expected format: type,capacity,duration,x,y,width,height")
                    continue
                
                try:
                    rtype = parts[0].strip().lower()
                    capacity = int(parts[1])
                    duration = int(parts[2])
                    x = int(parts[3]); y = int(parts[4])
                    w = int(parts[5]); h = int(parts[6])
                    rides.append({
                        "type": rtype,
                        "capacity": capacity,
                        "duration": duration,
                        "bbox": (x, y, w, h),
                    })
                except ValueError as e:
                    print(f"Error: Invalid numeric value on line {line_num} in {path}: {e}")
                    continue
                    
    except FileNotFoundError:
        print(f"Error: Rides CSV file not found: {path}")
        return []
    except Exception as e:
        print(f"Error reading rides CSV file {path}: {e}")
        return []
        
    return rides

def read_patrons_csv(path):
    """Read patrons CSV: single integer with total number of patrons."""
    if path is None:
        return 60
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            line_num = 0
            for line in f:
                line_num += 1
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    return int(line)
                except ValueError:
                    print(f"Error: Invalid number format on line {line_num} in {path}: '{line}'")
                    print(f"Expected: A single integer representing number of patrons")
                    continue
        print(f"Warning: No valid patron count found in {path}, using default: 60")
        return 60
        
    except FileNotFoundError:
        print(f"Error: Patrons CSV file not found: {path}")
        return 60
    except Exception as e:
        print(f"Error reading patrons CSV file {path}: {e}")
        return 60

def load_config_yaml(path):
    """Load configuration from a YAML file and return it as a dict."""
    if not YAML_AVAILABLE:
        print("Error: PyYAML requerido para cargar archivos YAML")
        print("Instala con: pip install pyyaml")
        return None
        
    if path is None:
        return None
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de configuración: {path}")
        return None
    except yaml.YAMLError as e:
        print(f"Error parseando YAML: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado cargando configuración: {e}")
        return None


def print_final_config(terrain, rides, num_patrons, steps, seed, stats, config_source="default"):
    """Print the final configuration used for the simulation."""
    print("\n" + "="*50)
    print("FINAL CONFIGURATION USED")
    print("="*50)
    print(f"Configuration source: {config_source}")
    print(f"Park dimensions: {terrain.width} x {terrain.height}")
    print(f"Number of rides: {len(rides)}")
    
    # Detalles de atracciones
    for i, ride in enumerate(rides, 1):
        ride_type = "Pirate Ship" if isinstance(ride, PirateShip) else "Ferris Wheel"
        print(f"   {i}. {ride_type} - Capacity: {ride.capacity}, Duration: {ride.duration}")
    
    print(f"Visitors: {num_patrons}")
    print(f"Simulation steps: {steps}")
    print(f"Random seed: {seed if seed is not None else 'Random'}")
    print(f"Live statistics: {'Yes' if stats else 'No'}")
    print("="*50 + "\n")


def build_rides(rides_params, terrain):
    """Create ride instances from params and mark their bounding boxes on the terrain."""
    from rides.roller_coaster import RollerCoaster
    
    rides = []
    for i, rp in enumerate(rides_params):
        name = f"Ride{i+1}"
        rtype = rp["type"]
        if rtype.startswith("pir"):
            ride = PirateShip(name, rp["capacity"], rp["duration"], rp["bbox"])
        elif rtype.startswith("fer"):
            ride = FerrisWheel(name, rp["capacity"], rp["duration"], rp["bbox"], cabins=8)
        elif rtype.startswith("coast") or rtype.startswith("roller"):
            ride = RollerCoaster(name, rp["capacity"], rp["duration"], rp["bbox"])
        else:
            ride = PirateShip(name, rp["capacity"], rp["duration"], rp["bbox"])
        terrain.add_bbox_barrier(ride.bbox)
        rides.append(ride)
    return rides
