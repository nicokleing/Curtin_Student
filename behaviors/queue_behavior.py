# -*- coding: utf-8 -*-
"""
Queue behavior for visitors.
============================
Handles patience and queue abandonment logic.
"""
from models.patron_types import PatronType


class QueueBehavior:
    """Encapsulate queue-related behavior."""
    
    @staticmethod
    def should_join_queue(ride, patron_type):
        """Decide whether a visitor should join a queue."""
        queue_length = len(ride.queue)
        
        # Different tolerance per type
        if patron_type == PatronType.IMPATIENT and queue_length > 3:
            return False
        elif patron_type == PatronType.ADVENTURER and queue_length > 8:
            return False
        elif patron_type == PatronType.FAMILY and queue_length > 6:
            return False
        elif patron_type == PatronType.EXPLORER and queue_length > 5:
            return False
            
        return True
    
    @staticmethod
    def process_queue_patience(patron, current_time, rides):
        """Handle patience while the visitor is in the queue."""
        patron.patience -= 1
        
        # Find current ride in the queue
        current_ride = None
        for ride in rides:
            if patron in ride.queue:
                current_ride = ride
                break
                
        if current_ride is None:
            return "roaming"  # No longer queued
            
        # Check if the visitor should leave due to impatience
        queue_position = current_ride.queue.index(patron) + 1
        
        # Factors that impact the abandonment decision
        patience_factor = patron.patience / patron.max_patience
        queue_factor = min(queue_position / 10.0, 0.5)  # Penalize long queues
        
        abandon_threshold = 0.1 + queue_factor  # Between 10% and 60%
        
        if patience_factor < abandon_threshold:
            QueueBehavior.abandon_queue(patron, current_ride)
            return "roaming"
            
        return "queueing"  # Stay in queue
    
    @staticmethod
    def abandon_queue(patron, ride):
        """Leave a ride queue."""
        if patron in ride.queue:
            ride.queue.remove(patron)
            
        patron.abandoned_queues += 1
        patron.state = "roaming"
        
        # Abandonment message includes type for quick debugging
        type_msg = patron.patron_type.value
        print(f"{patron.name} ({type_msg}) left {ride.name} queue due to impatience!")
        
        # Recover some patience after leaving
        patron.patience = min(patron.max_patience, patron.patience + 5)
