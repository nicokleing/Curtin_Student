# -*- coding: utf-8 -*-
"""Defines the Patron class used in the park simulation."""
import random

from models.patron_types import PatronType, DEFAULT_CATEGORY_WEIGHTS
from behaviors.movement_behavior import MovementBehavior
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
        self.last_abandon_event = None
        
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
            self.ride_preferences = DEFAULT_CATEGORY_WEIGHTS[self.patron_type].copy()
        elif self.patron_type == PatronType.FAMILY:
            self.speed = 0.6
            self.max_patience = 18
            self.ride_preferences = DEFAULT_CATEGORY_WEIGHTS[self.patron_type].copy()
        elif self.patron_type == PatronType.IMPATIENT:
            self.speed = 1.0
            self.max_patience = 10
            self.ride_preferences = DEFAULT_CATEGORY_WEIGHTS[self.patron_type].copy()
        elif self.patron_type == PatronType.EXPLORER:
            self.speed = 0.7
            self.max_patience = random.randint(12, 22)
            self.ride_preferences = DEFAULT_CATEGORY_WEIGHTS[self.patron_type].copy()
        
        self.patience = self.max_patience

    def _decision_behavior(self):
        from behaviors.decision_behavior import DecisionBehavior
        return DecisionBehavior

    def _at_target(self):
        """Check if the patron has reached the target."""
        return MovementBehavior.at_target(self.position, self.target)

    def _step_towards(self):
        """Move toward the target."""
        new_position, path_found = MovementBehavior.step_towards(
            self.position, self.target, self.speed, self.terrain
        )
        self.position = new_position
        if not path_found:
            self.target = None

    def _choose_target(self, rides):
        """Pick a target ride using the decision behavior."""
        decision = self._decision_behavior()
        self.target = decision.choose_target(
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
        self.target = None
        
        # Regain some patience after finishing a ride
        self.patience = min(self.max_patience, self.patience + 8)

    def _calculate_exit_probability(self):
        """Calculate the chance of leaving the park."""
        decision = self._decision_behavior()
        return decision.calculate_exit_probability(
            self.rides_completed, self.patron_type
        )

    def abandon_queue(self, ride, current_time=0):
        """Leave a ride queue manually if needed."""
        QueueBehavior.abandon_queue(self, ride, current_time, len(ride.queue))

    def step_change(self, t, rides):
        """Main per-step update for the visitor."""
        self.timer -= 1
        
        if self.state == "spawning":
            if self.timer <= 0:
                self.position = random.choice(self.spawns)
                self.state = "roaming"
                self.target = None
            return
        
        if self.state == "roaming":
            if self.target is None or self._at_target():
                self._choose_target(rides)
            self._step_towards()
            
            if self.state == "roaming":
                decision = self._decision_behavior()
                nearby_rides = MovementBehavior.find_nearby_rides(self.position, rides)
                if nearby_rides:
                    best_ride = decision.choose_best_nearby_ride(
                        self.position, nearby_rides, self.terrain, self.ride_preferences
                    )
                    if best_ride and QueueBehavior.should_join_queue(best_ride, self.patron_type):
                        added = best_ride.enqueue(self)
                        if added:
                            self.state = "queueing"
                            self.queue_start_time = t
                            self.target = None
                        else:
                            # queue full
                            pass
            
            if self.state == "roaming" and self.exits:
                exit_prob = self._calculate_exit_probability()
                if random.random() < exit_prob:
                    self.state = "leaving"
                    self.target = random.choice(self.exits)
            return
        
        if self.state == "queueing":
            self.state = QueueBehavior.process_queue_patience(self, t, rides)
            if self.state == "roaming":
                self.target = None
            return
        
        if self.state == "riding":
            return  # Ride decides when the patron leaves
        
        if self.state == "leaving":
            if self._at_target():
                self.state = "left"
            else:
                self._step_towards()

    def reset(self):
        """Restore original visitor state for a new run."""
        self.state = "spawning"
        self.position = (0.0, 0.0)
        self.target = None
        self.timer = random.randint(3, 8)
        self.current_ride = None
        self.last_abandon_event = None
        self.queue_start_time = 0
        self.total_queue_time = 0
        self.rides_completed = 0
        self.abandoned_queues = 0
        self.patience = self.max_patience

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
