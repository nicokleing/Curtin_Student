# -*- coding: utf-8 -*-
"""Queue behavior for visitors."""
from adventure.patrons.patron_types import PatronType


class QueueBehavior:
    """Encapsulate queue-related behavior."""

    @staticmethod
    def should_join_queue(ride, patron_type):
        """Decide whether a visitor should join a queue."""
        queue_length = len(ride.queue)

        # Different tolerance per type
        if patron_type == PatronType.IMPATIENT and queue_length > 3:
            return False
        if patron_type == PatronType.ADVENTURER and queue_length > 8:
            return False
        if patron_type == PatronType.FAMILY and queue_length > 6:
            return False
        if patron_type == PatronType.EXPLORER and queue_length > 5:
            return False

        return True

    @staticmethod
    def process_queue_patience(patron, current_time, rides):
        """Handle patience while the visitor is in the queue."""
        patron.patience -= 1

        current_ride = None
        for ride in rides:
            if patron in ride.queue:
                current_ride = ride
                break

        if current_ride is None:
            return "roaming"

        queue_position = current_ride.queue.index(patron) + 1
        queue_length = len(current_ride.queue)

        patience_factor = patron.patience / max(1, patron.max_patience)
        queue_factor = min(queue_position / 10.0, 0.5)

        abandon_threshold = 0.1 + queue_factor

        if patience_factor < abandon_threshold:
            QueueBehavior.abandon_queue(patron, current_ride, current_time, queue_length)
            return "roaming"

        return "queueing"

    @staticmethod
    def abandon_queue(patron, ride, current_time, queue_length):
        """Leave a ride queue."""
        if patron in ride.queue:
            ride.queue.remove(patron)

        patron.abandoned_queues += 1
        patron.state = "roaming"
        patron.target = None
        patron.last_abandon_event = {
            "time": current_time,
            "ride_id": ride.name,
            "queue_len": queue_length,
            "patience_at_leave": patron.patience,
        }

        type_msg = patron.patron_type.value
        print(f"{patron.name} ({type_msg}) left {ride.name} queue due to impatience!")

        patron.patience = min(patron.max_patience, patron.patience + 5)
