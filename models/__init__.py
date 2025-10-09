# -*- coding: utf-8 -*-
"""
Model package.
==================
Exposes the main classes and data types.
"""
from .patron_types import (
	PatronType,
	RideCategory,
	DEFAULT_CATEGORY_WEIGHTS,
	RIDE_CATEGORY_MAP,
)
from .patron import Patron

__all__ = [
	'PatronType',
	'RideCategory',
	'DEFAULT_CATEGORY_WEIGHTS',
	'RIDE_CATEGORY_MAP',
	'Patron',
]
