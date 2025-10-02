
# -*- coding: utf-8 -*-
"""Queue helpers (junior modular)."""
def enqueue(patron, ride):
    ride.queue.append(patron)

def dequeue(ride):
    if not ride.queue:
        return None
    return ride.queue.pop(0)
