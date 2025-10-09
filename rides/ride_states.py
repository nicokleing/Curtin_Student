# -*- coding: utf-8 -*-
"""Ride states and timing helpers."""

from enum import Enum

class RideState(Enum):
    """Possible states for a ride."""
    IDLE = "idle"
    LOADING = "loading" 
    RUNNING = "running"
    UNLOADING = "unloading"

class RideTimer:
    """Handles timing and state transitions for rides."""
    
    def __init__(self, ride):
        self.ride = ride
        self.timer = 0
        self.loading_phase = 0
        self.unloading_phase = 0
        
    def get_loading_time(self):
        """Get loading time based on ride type."""
        if self.ride.ride_type == "pirate":
            return 4  # Pirate ship needs extra time to secure riders
        elif self.ride.ride_type == "ferris":
            return 6  # Ferris wheel loads slower due to multiple cabins
        return 3  # Default loading time
        
    def get_unloading_time(self):
        """Get unloading time based on ride type."""
        if self.ride.ride_type == "pirate":
            return 3  # Pirate ship unloads quickly
        elif self.ride.ride_type == "ferris":
            return 5  # Ferris wheel stops at each cabin
        return 2  # Default unloading time

    def update(self, current_time):
        """Update the timer and manage state transitions."""
        self.ride.current_time = current_time
        
        # Keep an animation counter in sync
        self.ride.step_counter += 1
        
        if self.timer > 0:
            self.timer -= 1
            return False  # No state change yet
        return True  # Timer completed, allow transition

    def start_loading(self):
        """Start the loading phase."""
        self.timer = self.get_loading_time()
        self.loading_phase = 0
        
    def start_running(self):
        """Start the running phase."""
        self.timer = self.ride.duration
        
    def start_unloading(self):
        """Start the unloading phase."""
        self.timer = self.get_unloading_time()
        self.unloading_phase = 0
