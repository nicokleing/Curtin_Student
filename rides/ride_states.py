# -*- coding: utf-8 -*-
"""Estados y temporización de atracciones."""

from enum import Enum

class RideState(Enum):
    """Estados posibles de una atracción."""
    IDLE = "idle"
    LOADING = "loading" 
    RUNNING = "running"
    UNLOADING = "unloading"

class RideTimer:
    """Maneja temporización y transiciones de estado de atracciones."""
    
    def __init__(self, ride):
        self.ride = ride
        self.timer = 0
        self.loading_phase = 0
        self.unloading_phase = 0
        
    def get_loading_time(self):
        """Tiempo de carga basado en tipo de atracción."""
        if self.ride.ride_type == "pirate":
            return 4  # Barco pirata requiere más tiempo para asegurar pasajeros
        elif self.ride.ride_type == "ferris":
            return 6  # Noria requiere más tiempo por múltiples cabinas
        return 3  # Tiempo por defecto
        
    def get_unloading_time(self):
        """Tiempo de descarga basado en tipo de atracción."""
        if self.ride.ride_type == "pirate":
            return 3  # Descarga más rápida del barco
        elif self.ride.ride_type == "ferris":
            return 5  # Noria requiere parar en cada cabina
        return 2  # Tiempo por defecto

    def update(self, current_time):
        """Actualiza el timer y maneja transiciones de estado."""
        self.ride.current_time = current_time
        
        if self.timer > 0:
            self.timer -= 1
            return False  # No hay cambio de estado
        return True  # Timer completado, permitir transición

    def start_loading(self):
        """Inicia fase de carga."""
        self.timer = self.get_loading_time()
        self.loading_phase = 0
        
    def start_running(self):
        """Inicia fase de funcionamiento."""
        self.timer = self.ride.duration
        
    def start_unloading(self):
        """Inicia fase de descarga."""
        self.timer = self.get_unloading_time()
        self.unloading_phase = 0