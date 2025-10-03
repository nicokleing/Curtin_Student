# -*- coding: utf-8 -*-
"""
Comportamiento de Colas para Visitantes
=====================================
Maneja la lógica de paciencia y abandono de colas
"""
import random
from models.patron_types import PatronType


class QueueBehavior:
    """Encapsula la lógica de comportamiento en colas"""
    
    @staticmethod
    def should_join_queue(ride, patron_type):
        """Decide si el visitante debe unirse a una cola"""
        queue_length = len(ride.queue)
        
        # Diferentes tolerancias por tipo
        if patron_type == PatronType.IMPACIENTE and queue_length > 3:
            return False
        elif patron_type == PatronType.AVENTURERO and queue_length > 8:
            return False
        elif patron_type == PatronType.FAMILIAR and queue_length > 6:
            return False
        elif patron_type == PatronType.EXPLORADOR and queue_length > 5:
            return False
            
        return True
    
    @staticmethod
    def process_queue_patience(patron, current_time, rides):
        """Procesa la paciencia mientras está en cola"""
        patron.patience -= 1
        
        # Encontrar el ride actual en la cola
        current_ride = None
        for ride in rides:
            if patron in ride.queue:
                current_ride = ride
                break
                
        if current_ride is None:
            return "roaming"  # Ya no está en cola
            
        # Verificar si debe abandonar por impaciencia
        queue_position = current_ride.queue.index(patron) + 1
        
        # Factores que afectan la decisión de abandonar
        patience_factor = patron.patience / patron.max_patience
        queue_factor = min(queue_position / 10.0, 0.5)  # Penalizar colas largas
        
        abandon_threshold = 0.1 + queue_factor  # Entre 10% y 60%
        
        if patience_factor < abandon_threshold:
            QueueBehavior.abandon_queue(patron, current_ride)
            return "roaming"
            
        return "queueing"  # Continúa en cola
    
    @staticmethod
    def abandon_queue(patron, ride):
        """Abandona la cola de una atracción"""
        if patron in ride.queue:
            ride.queue.remove(patron)
            
        patron.abandoned_queues += 1
        patron.state = "roaming"
        
        # Mensaje de abandono por tipo
        type_msg = patron.patron_type.value
        print(f"{patron.name} ({type_msg}) left {ride.name} queue due to impatience!")
        
        # Regenerar paciencia parcialmente tras abandono
        patron.patience = min(patron.max_patience, patron.patience + 5)