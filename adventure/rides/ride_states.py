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
        override = getattr(self.ride, "loading_time", None)
        if override is not None:
            return max(0, int(override))
        if self.ride.ride_type == "pirate":
            return 4
        if self.ride.ride_type == "ferris":
            return 6
        return 3

    def get_unloading_time(self):
        """Get unloading time based on ride type."""
        override = getattr(self.ride, "unloading_time", None)
        if override is not None:
            return max(0, int(override))
        if self.ride.ride_type == "pirate":
            return 3
        if self.ride.ride_type == "ferris":
            return 5
        return 2

    def update(self, current_time):
        """Update the timer and manage state transitions."""
        self.ride.current_time = current_time
        self.ride.step_counter += 1
        if self.timer > 0:
            self.timer -= 1
            return False
        return True

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

    def reset(self):
        """Reset timer state for a fresh simulation run."""
        self.timer = 0
        self.loading_phase = 0
        self.unloading_phase = 0
