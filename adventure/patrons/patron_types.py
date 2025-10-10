# -*- coding: utf-8 -*-
"""Enums and tables that describe visitors and ride categories."""
from enum import Enum


class PatronType(Enum):
    ADVENTURER = "adventurer"
    FAMILY = "family"
    IMPATIENT = "impatient"
    EXPLORER = "explorer"


class RideCategory(Enum):
    THRILL = "thrill"
    FAMILY = "family"
    GENTLE = "gentle"


DEFAULT_CATEGORY_WEIGHTS = {
    PatronType.ADVENTURER: {
        RideCategory.THRILL: 0.9,
        RideCategory.FAMILY: 0.3,
        RideCategory.GENTLE: 0.4,
    },
    PatronType.FAMILY: {
        RideCategory.THRILL: 0.25,
        RideCategory.FAMILY: 0.85,
        RideCategory.GENTLE: 0.7,
    },
    PatronType.IMPATIENT: {
        RideCategory.THRILL: 0.75,
        RideCategory.FAMILY: 0.5,
        RideCategory.GENTLE: 0.35,
    },
    PatronType.EXPLORER: {
        RideCategory.THRILL: 0.6,
        RideCategory.FAMILY: 0.6,
        RideCategory.GENTLE: 0.6,
    },
}


RIDE_CATEGORY_MAP = {
    "pirate": RideCategory.THRILL,
    "coaster": RideCategory.THRILL,
    "ferris": RideCategory.FAMILY,
    "gentle": RideCategory.GENTLE,
    "family": RideCategory.FAMILY,
}
