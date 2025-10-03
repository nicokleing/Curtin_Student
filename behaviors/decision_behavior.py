# -*- coding: utf-8 -*-
"""
Comportamiento de Toma de Decisiones para Visitantes
==================================================
Maneja la lógica de elección de objetivos y atracciones
"""
import random
from models.patron_types import RidePreference


class DecisionBehavior:
    """Encapsula la lógica de toma de decisiones de visitantes"""
    
    @staticmethod
    def choose_target(position, rides, terrain, ride_preferences):
        """Elige un objetivo inteligente basado en preferencias"""
        if not rides or random.random() < 0.3:  # 30% chance de explorar libremente
            return terrain.random_free_point()
            
        # Filtrar rides por preferencia del visitante
        preferred_rides = []
        other_rides = []
        
        for ride in rides:
            ride_type = RidePreference(ride.ride_type)
            preference_score = ride_preferences.get(ride_type, 0.1)
            
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
            return (x + w / 2.0, y + h + 1.5)
        else:
            return terrain.random_free_point()

    @staticmethod
    def choose_best_nearby_ride(nearby_rides, ride_preferences):
        """Elige la mejor atracción de las cercanas"""
        if not nearby_rides:
            return None
            
        scored_rides = []
        for ride in nearby_rides:
            ride_type = RidePreference(ride.ride_type)
            preference = ride_preferences.get(ride_type, 0.1)
            queue_penalty = len(ride.queue) * 0.1
            score = preference - queue_penalty
            scored_rides.append((ride, score))
        
        # Elegir el ride con mejor score
        best_ride = max(scored_rides, key=lambda x: x[1])
        return best_ride[0] if best_ride[1] > 0.2 else None

    @staticmethod
    def calculate_exit_probability(rides_completed, patron_type):
        """Calcula probabilidad de salir del parque"""
        from models.patron_types import PatronType
        
        if patron_type == PatronType.IMPACIENTE:
            if rides_completed >= 3:
                return 0.6  # 60% chance de irse
            elif rides_completed >= 5:
                return 0.9  # 90% chance de irse
        elif patron_type == PatronType.EXPLORADOR:
            if rides_completed >= 4:
                return 0.3  # 30% chance de irse
            elif rides_completed >= 6:
                return 0.7  # 70% chance de irse
        else:  # AVENTURERO, FAMILIAR
            if rides_completed >= 4:
                return 0.4  # 40% chance de irse
            elif rides_completed >= 6:
                return 0.8  # 80% chance de irse
                
        return 0.1  # Probabilidad base baja