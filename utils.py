
# -*- coding: utf-8 -*-
"""
Utilidades: lectura de CSVs simples y construcción de rides.
"""
from rides import PirateShip, FerrisWheel

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
