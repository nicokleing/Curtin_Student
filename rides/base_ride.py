# -*- coding: utf-8 -*-
"""Base class for all rides."""

import matplotlib.patches as patches
from .ride_states import RideState, RideTimer

# Simple queue implementation
def dequeue(ride):
    """Remove and return first patron from ride queue."""
    if ride.queue:
        return ride.queue.pop(0)
    return None

class Ride:
    """Base class used by every ride in the park."""
    
    def __init__(self, name, capacity, duration, bbox, ride_type="generic"):
        self.name = name
        self.capacity = capacity
        self.duration = duration
        self.bbox = bbox  # (x, y, w, h)
        self.ride_type = ride_type

        self.state = RideState.IDLE.value
        self.queue = []          # Holds Patron instances
        self.riders = []         # Riders currently on the attraction
        self.current_time = 0

        # Timing component
        self.timer_manager = RideTimer(self)
        
        # Counter for simple animations
        self.step_counter = 0

    def admit_riders(self):
        """Pull up to `capacity` people from the queue using dequeue."""
        free = self.capacity - len(self.riders)
        for _ in range(max(0, free)):
            p = dequeue(self)
            if p is None:
                break
            p.board_ride(self)
            self.riders.append(p)

    def finish_cycle(self):
        """Finish a cycle by letting all riders leave."""
        for p in list(self.riders):
            p.leave_ride()
        self.riders.clear()

    def step_change(self, t):
        """Handle time-step based state changes."""
        if not self.timer_manager.update(t):
            # Timer still running, run progressive animations
            if self.state == RideState.LOADING.value:
                self._progressive_loading()
            elif self.state == RideState.UNLOADING.value:
                self._progressive_unloading()
            return

        # Timer completed, drive state transitions
        if self.state == RideState.IDLE.value:
            if self.queue and len(self.riders) < self.capacity:
                self.state = RideState.LOADING.value
                self.timer_manager.start_loading()
                
        elif self.state == RideState.LOADING.value:
            self.admit_riders()  # Load remaining visitors
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
        """Gradually board visitors during LOADING."""
        self.timer_manager.loading_phase += 1
        if self.timer_manager.loading_phase % 2 == 0 and self.queue:
            free_space = self.capacity - len(self.riders)
            if free_space > 0 and self.queue:
                p = dequeue(self)
                if p:
                    p.board_ride(self)
                    self.riders.append(p)
                        
    def _progressive_unloading(self):
        """Gradually unload visitors during UNLOADING."""
        self.timer_manager.unloading_phase += 1
        if self.timer_manager.unloading_phase % 2 == 0 and self.riders:
            if len(self.riders) > 0:
                rider = self.riders.pop(0)
                rider.leave_ride()

    def center(self):
        """Return the center of the ride."""
        x, y, w, h = self.bbox
        return x + w / 2.0, y + h / 2.0

    def plot(self, ax, t):
        """Base plot: draw bounding box and queue unless overridden."""
        self._draw_bbox(ax)
        self._draw_queue(ax)
        self._draw_capacity_info(ax)

    def _draw_bbox(self):
        """Draw the ride area; subclasses must implement."""
        raise NotImplementedError("Subclasses must implement _draw_bbox")
        
    def _draw_queue(self, ax):
        """Draw the visual queue; subclasses must implement."""
        raise NotImplementedError("Subclasses must implement _draw_queue")
        
    def _draw_capacity_info(self, ax):
        """Draw capacity information; subclasses must implement.""" 
        raise NotImplementedError("Subclasses must implement _draw_capacity_info")
