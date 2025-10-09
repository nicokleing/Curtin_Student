# -*- coding: utf-8 -*-
"""
Tipos y Enums para el sistema de visitantes
============================================
Define los tipos de visitantes y sus preferencias
"""
from enum import Enum


class PatronType(Enum):
    """Tipos de visitantes con diferentes comportamientos"""
    AVENTURERO = "adventurer"    # prefers exciting rides, high patience
    FAMILIAR = "family"        # prefers safe rides, medium patience
    IMPACIENTE = "impatient"    # low patience, abandons queues quickly
    EXPLORADOR = "explorer"    # likes to try everything, variable patience


class RidePreference(Enum):
    """Preferencias por tipos de atracciones"""
    PIRATE = "pirate"   # Pirate ship - thrilling
    FERRIS = "ferris"   # Ferris wheel - calm / family