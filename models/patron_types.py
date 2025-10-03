# -*- coding: utf-8 -*-
"""
Tipos y Enums para el sistema de visitantes
============================================
Define los tipos de visitantes y sus preferencias
"""
from enum import Enum


class PatronType(Enum):
    """Tipos de visitantes con diferentes comportamientos"""
    AVENTURERO = "aventurero"    # Prefiere rides emocionantes, alta paciencia
    FAMILIAR = "familiar"        # Prefiere rides seguros, paciencia media
    IMPACIENTE = "impaciente"    # Baja paciencia, abandona colas rápido
    EXPLORADOR = "explorador"    # Le gusta probar de todo, paciencia variable


class RidePreference(Enum):
    """Preferencias por tipos de atracciones"""
    PIRATE = "pirate"   # Barco pirata - emocionante
    FERRIS = "ferris"   # Noria - tranquila y familiar