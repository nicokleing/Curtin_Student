# -*- coding: utf-8 -*-
"""
Visitor enums for the patron system.
=====================================
Defines visitor types and their ride preferences.
"""
from enum import Enum


class PatronType(Enum):
    """Visitor types with different behaviors."""
    ADVENTURER = "adventurer"    # prefers exciting rides, high patience
    FAMILY = "family"           # prefers safe rides, medium patience
    IMPATIENT = "impatient"     # low patience, abandons queues quickly
    EXPLORER = "explorer"       # likes to try everything, variable patience


class RidePreference(Enum):
    """Ride preferences by patron type."""
    PIRATE = "pirate"   # Pirate ship - thrilling
    FERRIS = "ferris"   # Ferris wheel - calm / family
