# -*- coding: utf-8 -*-
"""
Decision behavior for visitors.
================================
Handles target selection and ride choices.
"""
import random
from models.patron_types import PatronType, RidePreference


class DecisionBehavior:
    """Encapsulate visitor decision-making logic."""
    
    @staticmethod
    def choose_target(position, rides, terrain, ride_preferences):
        """Pick a target based on preferences."""
        if not rides or random.random() < 0.3:  # 30% chance to explore freely
            return terrain.random_free_point()
            
        # Filter rides by visitor preference
        preferred_rides = []
        other_rides = []
        
        for ride in rides:
            ride_type = RidePreference(ride.ride_type)
            preference_score = ride_preferences.get(ride_type, 0.1)
            
            # Consider queue size
            queue_length = len(ride.queue)
            queue_penalty = min(queue_length * 0.1, 0.5)  # Penalize long queues
            
            final_score = preference_score - queue_penalty
            
            if final_score > 0.4:  # Threshold for attractive rides
                preferred_rides.append((ride, final_score))
            else:
                other_rides.append((ride, final_score))
        
        # Choose ride with weighted probability
        target_rides = preferred_rides if preferred_rides else other_rides
        
        if target_rides:
            # Sort by score and choose one of the top three
            target_rides.sort(key=lambda x: x[1], reverse=True)
            top_rides = target_rides[:min(3, len(target_rides))]
            chosen_ride = random.choice(top_rides)[0]
            
            x, y, w, h = chosen_ride.bbox
            return (x + w / 2.0, y + h + 1.5)
        else:
            return terrain.random_free_point()

    @staticmethod
    def choose_best_nearby_ride(nearby_rides, ride_preferences):
        """Select the best nearby ride."""
        if not nearby_rides:
            return None
            
        scored_rides = []
        for ride in nearby_rides:
            ride_type = RidePreference(ride.ride_type)
            preference = ride_preferences.get(ride_type, 0.1)
            queue_penalty = len(ride.queue) * 0.1
            score = preference - queue_penalty
            scored_rides.append((ride, score))
        
        # Pick the ride with the best score
        best_ride = max(scored_rides, key=lambda x: x[1])
        return best_ride[0] if best_ride[1] > 0.2 else None

    @staticmethod
    def calculate_exit_probability(rides_completed, patron_type):
        """Estimate the chance that a visitor leaves the park."""
        if patron_type == PatronType.IMPATIENT:
            if rides_completed >= 3:
                return 0.6  # 60% chance to leave
            elif rides_completed >= 5:
                return 0.9  # 90% chance to leave
        elif patron_type == PatronType.EXPLORER:
            if rides_completed >= 4:
                return 0.3  # 30% chance to leave
            elif rides_completed >= 6:
                return 0.7  # 70% chance to leave
        else:  # ADVENTURER, FAMILY
            if rides_completed >= 4:
                return 0.4  # 40% chance to leave
            elif rides_completed >= 6:
                return 0.8  # 80% chance to leave
                
        return 0.1  # Base probability
