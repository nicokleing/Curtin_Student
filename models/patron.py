# -*- coding: utf-8 -*-
"""
Patron class (refactored).
==========================
Park visitor with modular behaviors.
"""
import math
import random

from models.patron_types import PatronType, RidePreference
from behaviors.movement_behavior import MovementBehavior
from behaviors.decision_behavior import DecisionBehavior
from behaviors.queue_behavior import QueueBehavior


class Patron:
    """Park visitor with specialized behaviors."""
    
    def __init__(self, name, spawns, exits, terrain, patron_type=None):
        self.name = name
        self.id = name  # Use name as id for export logging
        self.spawns = spawns
        self.exits = exits
        self.terrain = terrain

        # Visitor type and preferences
        self.patron_type = patron_type or random.choice(list(PatronType))
        self._setup_patron_characteristics()

        self.state = "spawning"
        self.position = (0.0, 0.0)
        self.target = None
        self.timer = random.randint(3, 8)  # Slightly random spawn delay
        self.current_ride = None
        
        # Queue patience tracking
        self.queue_start_time = 0
        self.total_queue_time = 0
        self.rides_completed = 0
        self.abandoned_queues = 0
        
    def _setup_patron_characteristics(self):
        """Configure characteristics based on visitor type."""
        if self.patron_type == PatronType.ADVENTURER:
            self.speed = 0.8
            self.max_patience = 25
            self.ride_preferences = {
                RidePreference.PIRATE: 0.9,
                RidePreference.FERRIS: 0.3
            }
        elif self.patron_type == PatronType.FAMILY:
            self.speed = 0.6
            self.max_patience = 18
            self.ride_preferences = {
                RidePreference.PIRATE: 0.2,
                RidePreference.FERRIS: 0.8
            }
        elif self.patron_type == PatronType.IMPATIENT:
            self.speed = 1.0
            self.max_patience = 10
            self.ride_preferences = {
                RidePreference.PIRATE: 0.7,
                RidePreference.FERRIS: 0.6
            }
        elif self.patron_type == PatronType.EXPLORER:
            self.speed = 0.7
            self.max_patience = random.randint(12, 22)
            self.ride_preferences = {
                RidePreference.PIRATE: 0.6,
                RidePreference.FERRIS: 0.6
            }
        
        self.patience = self.max_patience

    def _at_target(self):
        """Check if the patron has reached the target."""
        return MovementBehavior.at_target(self.position, self.target)

    def _step_towards(self):
        """Move toward the target."""
        self.position = MovementBehavior.step_towards(
            self.position, self.target, self.speed, self.terrain
        )

    def _choose_target(self, rides):
        """Pick a target ride using the decision behavior."""
        self.target = DecisionBehavior.choose_target(
            self.position, rides, self.terrain, self.ride_preferences
        )

    def board_ride(self, ride):
        """Board a ride."""
        self.current_ride = ride
        self.state = "riding"
        self.queue_start_time = 0
        print(f"{self.name} boarded {ride.name}")

    def leave_ride(self):
        """Leave the current ride."""
        if self.current_ride:
            print(f"{self.name} exited {self.current_ride.name}")
            self.current_ride = None
        
        self.state = "roaming"
        self.rides_completed += 1
        
        # Regain some patience after finishing a ride
        self.patience = min(self.max_patience, self.patience + 8)

    def _calculate_exit_probability(self):
        """Calculate the chance of leaving the park."""
        return DecisionBehavior.calculate_exit_probability(
            self.rides_completed, self.patron_type
        )

    def abandon_queue(self, ride):
        """Leave a ride queue."""
        QueueBehavior.abandon_queue(self, ride)

    def step_change(self, t, rides):
        """Main per-step update for the visitor."""
        self.timer -= 1
        
        if self.state == "spawning":
            if self.timer <= 0:
                self.position = random.choice(self.spawns)
                self.state = "roaming"
        
        elif self.state == "roaming":
            if self._at_target():
                self._choose_target(rides)
            else:
                self._step_towards()
                
            # Look for nearby rides to join
            nearby_rides = MovementBehavior.find_nearby_rides(self.position, rides)
            if nearby_rides:
                best_ride = DecisionBehavior.choose_best_nearby_ride(
                    nearby_rides, self.ride_preferences
                )
                if best_ride and QueueBehavior.should_join_queue(best_ride, self.patron_type):
                    best_ride.queue.append(self)
                    self.state = "queueing"
                    self.queue_start_time = t
                    
        elif self.state == "queueing":
            self.state = QueueBehavior.process_queue_patience(self, t, rides)
                    
        elif self.state == "riding":
            pass  # The ride decides when the patron leaves
            
        elif self.state == "roaming":
            # Decide whether to exit the park
            exit_prob = self._calculate_exit_probability()
            if random.random() < exit_prob:
                self.state = "leaving"
                self.target = random.choice(self.exits)
                
        elif self.state == "leaving":
            if self._at_target():
                self.state = "left"
            else:
                self._step_towards()

    def plot(self, ax):
        """Render the visitor on the map."""
        # Marker by visitor type
        type_colors = {
            PatronType.ADVENTURER: "^",
            PatronType.FAMILY: "s",
            PatronType.IMPATIENT: "D",
            PatronType.EXPLORER: "o",
        }
        
        marker = type_colors.get(self.patron_type, "o")
        ax.scatter(self.position[0], self.position[1], 
                  c='blue', marker=marker, s=25, alpha=0.8)

    def get_status_info(self):
        """Provide a status summary for debugging."""
        return {
            "name": self.name,
            "type": self.patron_type.value,
            "state": self.state,
            "position": self.position,
            "patience": self.patience,
            "rides_completed": self.rides_completed,
            "abandoned_queues": self.abandoned_queues,
        }
