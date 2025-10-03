
# -*- coding: utf-8 -*-
"""
Patrons (personas) – ÉPICA 2 COMPLETA: Sistema Avanzado de Visitantes
- Estados: spawning → roaming → queueing → riding → leaving → left
- Preferencias individuales por tipo de visitante
- Sistema de paciencia y abandono de colas
- Pathfinding mejorado con navegación inteligente
"""
import math
import random
from enum import Enum

class PatronType(Enum):
    """Tipos de visitantes con diferentes comportamientos"""
    AVENTURERO = "aventurero"    # Prefiere rides emocionantes, alta paciencia
    FAMILIAR = "familiar"        # Prefiere rides seguros, paciencia media
    IMPACIENTE = "impaciente"    # Baja paciencia, abandona colas rápido
    EXPLORADOR = "explorador"    # Le gusta probar de todo, paciencia variable

class RidePreference(Enum):
    """Preferencias por tipos de atracciones"""
    PIRATE = "pirate"   # Barco pirata - emocionante
    FERRIS = "ferris"   # Noria - tranquila y familiar

class Patron:
    def __init__(self, name, spawns, exits, terrain, patron_type=None):
        self.name = name
        self.spawns = spawns
        self.exits = exits
        self.terrain = terrain

        # 🎯 ÉPICA 2: Sistema de tipos y preferencias
        self.patron_type = patron_type or random.choice(list(PatronType))
        self._setup_patron_characteristics()

        self.state = "spawning"
        self.position = (0.0, 0.0)
        self.target = None
        self.timer = random.randint(3, 8)  # Spawn aleatorio más realista
        self.current_ride = None
        
        # 🎯 ÉPICA 2: Sistema de paciencia y abandono
        self.queue_start_time = 0
        self.total_queue_time = 0
        self.rides_completed = 0
        self.abandoned_queues = 0
        
    def _setup_patron_characteristics(self):
        """Configura características según el tipo de visitante"""
        if self.patron_type == PatronType.AVENTURERO:
            self.speed = random.uniform(1.0, 1.4)
            self.max_patience = random.randint(80, 150)  # Alta paciencia
            self.ride_preferences = {
                RidePreference.PIRATE: 0.7,   # 70% probabilidad de elegir pirate
                RidePreference.FERRIS: 0.3    # 30% probabilidad de elegir ferris
            }
            
        elif self.patron_type == PatronType.FAMILIAR:
            self.speed = random.uniform(0.8, 1.2)
            self.max_patience = random.randint(50, 90)   # Paciencia media
            self.ride_preferences = {
                RidePreference.PIRATE: 0.2,   # 20% probabilidad de elegir pirate
                RidePreference.FERRIS: 0.8    # 80% probabilidad de elegir ferris
            }
            
        elif self.patron_type == PatronType.IMPACIENTE:
            self.speed = random.uniform(1.2, 1.6)
            self.max_patience = random.randint(20, 40)   # Baja paciencia
            self.ride_preferences = {
                RidePreference.PIRATE: 0.5,   # Igual probabilidad
                RidePreference.FERRIS: 0.5
            }
            
        elif self.patron_type == PatronType.EXPLORADOR:
            self.speed = random.uniform(0.9, 1.3)
            self.max_patience = random.randint(60, 100)  # Paciencia variable
            self.ride_preferences = {
                RidePreference.PIRATE: 0.6,   # Ligera preferencia por aventura
                RidePreference.FERRIS: 0.4
            }
            
        self.patience = self.max_patience

    def _choose_target(self, rides):
        """🎯 ÉPICA 2: Elección inteligente basada en preferencias"""
        if not rides or random.random() < 0.3:  # 30% chance de explorar libremente
            self.target = self.terrain.random_free_point()
            return
            
        # Filtrar rides por preferencia del visitante
        preferred_rides = []
        other_rides = []
        
        for ride in rides:
            ride_type = RidePreference(ride.ride_type)
            preference_score = self.ride_preferences.get(ride_type, 0.1)
            
            # Considerar también el tamaño de la cola
            queue_length = len(ride.queue)
            queue_penalty = min(queue_length * 0.1, 0.5)  # Penalizar colas largas
            
            final_score = preference_score - queue_penalty
            
            if final_score > 0.4:  # Umbral para rides "atractivos"
                preferred_rides.append((ride, final_score))
            else:
                other_rides.append((ride, final_score))
        
        # Elegir ride con sistema de probabilidad ponderada
        target_rides = preferred_rides if preferred_rides else other_rides
        
        if target_rides:
            # Ordenar por score y elegir uno de los top 3
            target_rides.sort(key=lambda x: x[1], reverse=True)
            top_rides = target_rides[:min(3, len(target_rides))]
            chosen_ride = random.choice(top_rides)[0]
            
            x, y, w, h = chosen_ride.bbox
            self.target = (x + w / 2.0, y + h + 1.5)
        else:
            self.target = self.terrain.random_free_point()

    def _at_target(self):
        if self.target is None:
            return True
        dx = self.target[0] - self.position[0]
        dy = self.target[1] - self.position[1]
        return dx * dx + dy * dy < 0.9

    def _step_towards(self):
        if self.target is None:
            return
        px, py = self.position
        tx, ty = self.target
        vx = tx - px
        vy = ty - py
        dist = math.hypot(vx, vy)
        if dist < 1e-6:
            return
        ux = vx / dist
        uy = vy / dist
        nx = px + ux * self.speed
        ny = py + uy * self.speed
        if self.terrain.is_free_line((px, py), (nx, ny)):
            self.position = (nx, ny)
        else:
            # pequeño rodeo
            angle = random.choice([-1, 1]) * math.pi / 6
            rx = ux * math.cos(angle) - uy * math.sin(angle)
            ry = ux * math.sin(angle) + uy * math.cos(angle)
            nx = px + rx * self.speed
            ny = py + ry * self.speed
            if self.terrain.is_free_point((nx, ny)):
                self.position = (nx, ny)

    def board_ride(self, ride):
        """Visitante aborda la atracción"""
        self.state = "riding"
        self.current_ride = ride
        self.target = None
        
        # Registrar estadísticas de cola
        if hasattr(self, 'queue_start_time'):
            queue_time = ride.current_time - self.queue_start_time if hasattr(ride, 'current_time') else 0
            self.total_queue_time += queue_time

    def leave_ride(self):
        """Visitante sale de la atracción"""
        self.current_ride = None
        self.rides_completed += 1
        
        # Restaurar paciencia parcialmente después de completar un ride
        patience_restore = self.max_patience * 0.3
        self.patience = min(self.max_patience, self.patience + patience_restore)
        
        # Decisión de salir del parque basada en tipo de visitante
        exit_probability = self._calculate_exit_probability()
        
        if random.random() < exit_probability:
            self.state = "leaving"
            self.target = random.choice(self.exits)
        else:
            self.state = "roaming"
            self._choose_target([])
            
    def _calculate_exit_probability(self):
        """Calcula probabilidad de salir basada en características del visitante"""
        base_probability = 0.15
        
        # Ajustar por tipo de visitante
        if self.patron_type == PatronType.IMPACIENTE:
            base_probability += 0.1  # Más probable que se vaya
        elif self.patron_type == PatronType.EXPLORADOR:
            base_probability -= 0.05  # Menos probable que se vaya
            
        # Ajustar por número de rides completados
        if self.rides_completed >= 3:
            base_probability += 0.2
        elif self.rides_completed >= 5:
            base_probability += 0.4
            
        # Ajustar por paciencia actual
        patience_factor = (self.max_patience - self.patience) / self.max_patience
        base_probability += patience_factor * 0.3
        
        return min(0.8, max(0.05, base_probability))  # Entre 5% y 80%
    
    def abandon_queue(self, ride):
        """🎯 ÉPICA 2: Lógica de abandono de cola por impaciencia"""
        if self in ride.queue:
            ride.queue.remove(self)
            
        self.abandoned_queues += 1
        self.state = "roaming"
        
        # Penalizar paciencia después de abandonar
        self.patience *= 0.7  # Reduce paciencia para futuras colas
        
        print(f"🚶 {self.name} ({self.patron_type.value}) abandonó la cola de {ride.ride_type} por impaciencia!")
        
        # Decidir siguiente acción
        if self.patience < self.max_patience * 0.2:  # Muy impaciente
            if random.random() < 0.4:  # 40% chance de irse del parque
                self.state = "leaving"
                self.target = random.choice(self.exits)
                return
                
        self._choose_target([])

    def step_change(self, t, rides):
        """🎯 ÉPICA 2: Loop principal mejorado con sistema de paciencia"""
        
        if self.state == "spawning":
            if self.timer > 0:
                self.timer -= 1
            else:
                self.position = random.choice(self.spawns)
                self.state = "roaming"
                self._choose_target(rides)
            return

        if self.state == "left":
            return

        if self.state == "riding":
            return

        if self.state == "queueing":
            # 🎯 ÉPICA 2: Sistema de abandono por impaciencia
            self._process_queue_patience(t, rides)
            return

        if self._at_target():
            if self.state == "leaving":
                self.state = "left"
                return
                
            # ¿hay ride cerca?
            near = self._find_nearby_rides(rides)
            
            if near:
                chosen_ride = self._choose_best_nearby_ride(near)
                if chosen_ride and self._should_join_queue(chosen_ride):
                    chosen_ride.queue.append(self)
                    self.state = "queueing"
                    self.queue_start_time = t
                    return
                    
            # elegir nuevo objetivo si no hay rides apropiados
            self._choose_target(rides)
        else:
            self._step_towards()
            
    def _process_queue_patience(self, current_time, rides):
        """Procesa la paciencia mientras está en cola"""
        self.patience -= 1
        
        # Encontrar el ride actual en la cola
        current_ride = None
        for ride in rides:
            if self in ride.queue:
                current_ride = ride
                break
                
        if current_ride is None:
            self.state = "roaming"
            return
            
        # Verificar si debe abandonar por impaciencia
        queue_position = ride.queue.index(self) + 1
        estimated_wait = queue_position * 2  # Estimación simple
        
        # Factors que afectan la decisión de abandonar
        patience_factor = self.patience / self.max_patience
        queue_factor = min(queue_position / 10.0, 0.5)  # Penalizar colas largas
        
        abandon_threshold = 0.1 + queue_factor  # Entre 10% y 60%
        
        if patience_factor < abandon_threshold:
            self.abandon_queue(current_ride)
            
    def _find_nearby_rides(self, rides):
        """Encuentra rides cerca de la posición actual"""
        near = []
        for r in rides:
            if self.terrain.near_bbox(self.position, r.bbox, tol=1.2):
                near.append(r)
        return near
        
    def _choose_best_nearby_ride(self, nearby_rides):
        """Elige el mejor ride de los cercanos basado en preferencias"""
        if not nearby_rides:
            return None
            
        scored_rides = []
        for ride in nearby_rides:
            ride_type = RidePreference(ride.ride_type)
            preference_score = self.ride_preferences.get(ride_type, 0.1)
            
            queue_length = len(ride.queue)
            queue_penalty = min(queue_length * 0.15, 0.6)
            
            final_score = preference_score - queue_penalty
            scored_rides.append((ride, final_score))
            
        # Elegir el ride con mejor score
        if scored_rides:
            scored_rides.sort(key=lambda x: x[1], reverse=True)
            return scored_rides[0][0]
        return None
        
    def _should_join_queue(self, ride):
        """Decide si debe unirse a la cola basado en paciencia y preferencias"""
        queue_length = len(ride.queue)
        
        # No unirse si la cola es demasiado larga para su paciencia
        max_acceptable_queue = self.patience // 10
        
        if queue_length > max_acceptable_queue:
            return False
            
        # Visitantes impacientes son más selectivos
        if self.patron_type == PatronType.IMPACIENTE and queue_length > 3:
            return False
            
        return True

    def plot(self, ax):
        """🎯 ÉPICA 2: Visualización mejorada con tipos de visitantes"""
        if self.state == "left":
            return
            
        # Colores por estado
        state_colors = {
            "roaming": "#1f77b4",
            "queueing": "#ff7f0e", 
            "riding": "#2ca02c",
            "leaving": "#d62728",
            "spawning": "#9467bd",
        }
        
        # Marcadores por tipo de visitante
        type_markers = {
            PatronType.AVENTURERO: "^",      # Triángulo - aventurero
            PatronType.FAMILIAR: "s",        # Cuadrado - familiar
            PatronType.IMPACIENTE: "D",      # Diamante - impaciente
            PatronType.EXPLORADOR: "o",      # Círculo - explorador
        }
        
        color = state_colors.get(self.state, "#7f7f7f")
        marker = type_markers.get(self.patron_type, ".")
        
        # Tamaño basado en paciencia (más grande = más paciente)
        patience_ratio = self.patience / self.max_patience
        size = 4 + patience_ratio * 4  # Entre 4 y 8
        
        ax.plot([self.position[0]], [self.position[1]], 
                marker=marker, ms=size, color=color, 
                alpha=0.7 + patience_ratio * 0.3)  # Transparencia basada en paciencia
                
    def get_status_info(self):
        """Retorna información detallada del visitante para debug/estadísticas"""
        return {
            "name": self.name,
            "type": self.patron_type.value,
            "state": self.state,
            "patience": f"{self.patience}/{self.max_patience}",
            "rides_completed": self.rides_completed,
            "queues_abandoned": self.abandoned_queues,
            "total_queue_time": self.total_queue_time,
            "position": f"({self.position[0]:.1f}, {self.position[1]:.1f})"
        }
