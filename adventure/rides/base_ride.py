# -*- coding: utf-8 -*-
"""Base class for all rides."""
from __future__ import annotations

from adventure.rides.ride_states import RideState, RideTimer


def dequeue(ride):
    """Remove and return first patron from ride queue."""
    if ride.queue:
        return ride.queue.pop(0)
    return None


class Ride:
    """Base class used by every ride in the park."""

    def __init__(
        self,
        name,
        capacity,
        duration,
        bbox,
        ride_type="generic",
        *,
        loading_time=None,
        unloading_time=None,
    ):
        self.name = name
        self.capacity = capacity
        self.duration = duration
        self.bbox = bbox
        self.ride_type = ride_type
        self.category = None
        self.rating = 0.6
        self.loading_time = loading_time
        self.unloading_time = unloading_time

        self.state = RideState.IDLE.value
        self.queue = []
        self.riders = []
        self.current_time = 0

        self.timer_manager = RideTimer(self)

        self.step_counter = 0

    def admit_riders(self):
        """Pull up to capacity patrons from the queue."""
        free = self.capacity - len(self.riders)
        for _ in range(max(0, free)):
            patron = dequeue(self)
            if patron is None:
                break
            patron.board_ride(self)
            self.riders.append(patron)

    def finish_cycle(self):
        """Finish a cycle by letting all riders leave."""
        for patron in list(self.riders):
            patron.leave_ride()
        self.riders.clear()

    def step_change(self, step_index):
        """Handle time-step based state changes."""
        if not self.timer_manager.update(step_index):
            if self.state == RideState.LOADING.value:
                self._progressive_loading()
            elif self.state == RideState.UNLOADING.value:
                self._progressive_unloading()
            return

        if self.state == RideState.IDLE.value:
            if self.queue and len(self.riders) < self.capacity:
                self.state = RideState.LOADING.value
                self.timer_manager.start_loading()
        elif self.state == RideState.LOADING.value:
            self.admit_riders()
            if self.riders:
                self.state = RideState.RUNNING.value
                self.timer_manager.start_running()
                print(
                    f"Ride {self.name} starting with {len(self.riders)}/{self.capacity} passengers"
                )
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
            if free_space > 0:
                patron = dequeue(self)
                if patron:
                    patron.board_ride(self)
                    self.riders.append(patron)

    def _progressive_unloading(self):
        """Gradually unload visitors during UNLOADING."""
        self.timer_manager.unloading_phase += 1
        if self.timer_manager.unloading_phase % 2 == 0 and self.riders:
            rider = self.riders.pop(0)
            rider.leave_ride()

    def reset(self):
        """Reset ride state between simulation runs."""
        self.state = RideState.IDLE.value
        self.queue.clear()
        self.riders.clear()
        self.current_time = 0
        self.step_counter = 0
        if hasattr(self, "timer_manager"):
            self.timer_manager.reset()

    def center(self):
        """Return the center of the ride."""
        x, y, w, h = self.bbox
        return x + w / 2.0, y + h / 2.0

    def plot(self, ax, step_index):
        """Base plot: draw bounding box and queue unless overridden."""
        self._draw_bbox(ax)
        self._draw_queue(ax)
        self._draw_capacity_info(ax)

    def _draw_bbox(self, ax):
        raise NotImplementedError("Subclasses must implement _draw_bbox")

    def _draw_queue(self, ax):
        raise NotImplementedError("Subclasses must implement _draw_queue")

    def _draw_capacity_info(self, ax):
        raise NotImplementedError("Subclasses must implement _draw_capacity_info")
