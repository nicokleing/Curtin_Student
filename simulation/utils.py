
# -*- coding: utf-8 -*-
"""
Utilidades: lectura de CSVs simples, configuración YAML y construcción de rides.
"""
from rides import PirateShip, FerrisWheel

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("Warning: PyYAML not available. Install with: pip install pyyaml")

def read_rides_csv(path):
    """
    Formato simple por línea:
    tipo,capacidad,duracion,x,y,ancho,alto
    """
    rides = []
    if path is None:
        return rides
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) != 7:
                continue
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
    return rides

def read_patrons_csv(path):
    """
    Un solo número con la cantidad total de personas.
    """
    if path is None:
        return 60
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                return int(line)
            except ValueError:
                pass
    return 60

def load_config_yaml(path):
    """
    Carga configuración completa desde archivo YAML.
    
    Args:
        path (str): Ruta al archivo YAML de configuración
        
    Returns:
        dict: Configuración cargada o None si hay error
    """
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
    """
    Imprime la configuración final utilizada en la simulación.
    
    Args:
        terrain: Objeto Terrain con las dimensiones del parque
        rides: Lista de objetos Ride
        num_patrons: Número de visitantes
        steps: Pasos de simulación
        seed: Semilla aleatoria (None si no se usó)
        stats: Si se muestran estadísticas
        config_source: Fuente de la configuración ("default", "interactive", "yaml", "csv")
    """
    print("\n" + "="*50)
    print("📋 CONFIGURACIÓN FINAL UTILIZADA")
    print("="*50)
    print(f"🏗️  Fuente de configuración: {config_source}")
    print(f"🗺️  Dimensiones del parque: {terrain.width} x {terrain.height}")
    print(f"🎢 Número de atracciones: {len(rides)}")
    
    # Detalles de atracciones
    for i, ride in enumerate(rides, 1):
        ride_type = "🏴‍☠️ Barco Pirata" if isinstance(ride, PirateShip) else "🎡 Noria"
        print(f"   {i}. {ride_type} - Cap: {ride.capacity}, Duración: {ride.duration}")
    
    print(f"👥 Visitantes: {num_patrons}")
    print(f"⏱️  Pasos de simulación: {steps}")
    print(f"🎲 Semilla aleatoria: {seed if seed is not None else 'Aleatoria'}")
    print(f"📊 Estadísticas en vivo: {'✅ Sí' if stats else '❌ No'}")
    print("="*50 + "\n")


def build_rides(rides_params, terrain):
    """
    Crea instancias de rides según el dict de parámetros
    y marca sus bounding boxes como barreras en el terreno.
    """
    rides = []
    for i, rp in enumerate(rides_params):
        name = f"Ride{i+1}"
        rtype = rp["type"]
        if rtype.startswith("pir"):
            ride = PirateShip(name, rp["capacity"], rp["duration"], rp["bbox"])
        elif rtype.startswith("fer"):
            ride = FerrisWheel(name, rp["capacity"], rp["duration"], rp["bbox"], cabins=8)
        else:
            ride = PirateShip(name, rp["capacity"], rp["duration"], rp["bbox"])
        terrain.add_bbox_barrier(ride.bbox)
        rides.append(ride)
    return rides
