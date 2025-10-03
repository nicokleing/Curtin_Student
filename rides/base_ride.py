# -*- coding: utf-8 -*-
"""Clase base para todas las atracciones."""

import matplotlib.patches as patches
from .ride_states import RideState, RideTimer

# Simple queue implementation
def dequeue(ride):
    """Remove and return first patron from ride queue."""
    if ride.queue:
        return ride.queue.pop(0)
    return None

class Ride:
    """Clase base para todas las atracciones del parque."""
    
    def __init__(self, name, capacity, duration, bbox, ride_type="generic"):
        self.name = name
        self.capacity = capacity
        self.duration = duration
        self.bbox = bbox  # (x, y, w, h)
        self.ride_type = ride_type

        self.state = RideState.IDLE.value
        self.queue = []          # lista de Patron
        self.riders = []         # lista de Patron
        self.current_time = 0

        # Componente de temporización
        self.timer_manager = RideTimer(self)
        
        # Contador para animaciones
        self.step_counter = 0

    def admit_riders(self):
        """Toma hasta 'capacity' personas desde la cola con dequeue."""
        free = self.capacity - len(self.riders)
        for _ in range(max(0, free)):
            p = dequeue(self)
            if p is None:
                break
            p.board_ride(self)
            self.riders.append(p)

    def finish_cycle(self):
        """Finalizar ciclo - descargar visitantes restantes si quedan."""
        for p in list(self.riders):
            p.leave_ride()
        self.riders.clear()

    def step_change(self, t):
        """Maneja cambios de estado por paso de tiempo."""
        if not self.timer_manager.update(t):
            # Timer aún corriendo, procesar animaciones progresivas
            if self.state == RideState.LOADING.value:
                self._progressive_loading()
            elif self.state == RideState.UNLOADING.value:
                self._progressive_unloading()
            return

        # Timer completado, manejar transiciones de estado
        if self.state == RideState.IDLE.value:
            if self.queue and len(self.riders) < self.capacity:
                self.state = RideState.LOADING.value
                self.timer_manager.start_loading()
                
        elif self.state == RideState.LOADING.value:
            self.admit_riders()  # Cargar visitantes restantes
            if self.riders:
                self.state = RideState.RUNNING.value
                self.timer_manager.start_running()
                print(f"Ride {self.name} starting with {len(self.riders)}/{self.capacity} passengers")
            else:
                self.state = RideState.IDLE.value
                
        elif self.state == RideState.RUNNING.value:
            self.state = RideState.UNLOADING.value
            self.timer_manager.start_unloading()
            print(f"Ride {self.name} ending cycle, unloading passengers...")
                
        elif self.state == RideState.UNLOADING.value:
            self.finish_cycle()
            self.state = RideState.IDLE.value
            print(f"Ride {self.name} ready for new passengers")

    def _progressive_loading(self):
        """Carga gradual de visitantes durante LOADING."""
        self.timer_manager.loading_phase += 1
        if self.timer_manager.loading_phase % 2 == 0 and self.queue:
            free_space = self.capacity - len(self.riders)
            if free_space > 0 and self.queue:
                p = dequeue(self)
                if p:
                    p.board_ride(self)
                    self.riders.append(p)
                        
    def _progressive_unloading(self):
        """Descarga gradual de visitantes durante UNLOADING."""
        self.timer_manager.unloading_phase += 1
        if self.timer_manager.unloading_phase % 2 == 0 and self.riders:
            if len(self.riders) > 0:
                rider = self.riders.pop(0)
                rider.leave_ride()

    def center(self):
        """Obtiene el centro de la atracción."""
        x, y, w, h = self.bbox
        return x + w / 2.0, y + h / 2.0

    def plot(self, ax, t):
        """Base: dibuja la caja y la cola si una subclase no sobreescribe."""
        self._draw_bbox(ax)
        self._draw_queue(ax)
        self._draw_capacity_info(ax)

    def _draw_bbox(self):
        """Dibuja el área base de la atracción - implementar en subclases."""
        raise NotImplementedError("Subclases deben implementar _draw_bbox")
        
    def _draw_queue(self, ax):
        """Dibuja la cola visual - implementar en subclases."""
        raise NotImplementedError("Subclases deben implementar _draw_queue")
        
    def _draw_capacity_info(self, ax):
        """Dibuja información de capacidad - implementar en subclases.""" 
        raise NotImplementedError("Subclases deben implementar _draw_capacity_info")