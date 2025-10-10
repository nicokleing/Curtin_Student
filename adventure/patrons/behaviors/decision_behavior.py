# -*- coding: utf-8 -*-
"""Decision behavior for visitors."""
from __future__ import annotations

import random

from adventure.patrons.patron_types import (
    PatronType,
    RideCategory,
    RIDE_CATEGORY_MAP,
)


class DecisionBehavior:
    """Encapsulate visitor decision-making logic."""

    EXPLORE_PROBABILITY = 0.25
    MIN_COMMIT_SCORE = 0.25
    UTILITY_WEIGHTS = {
        "preference": 0.55,
        "rating": 0.25,
        "queue": -0.4,
        "distance": -0.3,
    }

    @classmethod
    def choose_target(cls, position, rides, terrain, ride_preferences):
        """Pick a target based on preferences."""
        if not rides:
            return terrain.random_free_point()

        if random.random() < cls.EXPLORE_PROBABILITY:
            return terrain.random_free_point()

        scored_rides = []
        for ride in rides:
            score = cls.compute_ride_score(position, ride, terrain, ride_preferences)
            scored_rides.append((ride, score))

        if not scored_rides:
            return terrain.random_free_point()

        scored_rides.sort(key=lambda item: item[1], reverse=True)
        top_score = scored_rides[0][1]
        if top_score < cls.MIN_COMMIT_SCORE:
            return terrain.random_free_point()

        top_candidates = [ride for ride, score in scored_rides if score >= top_score - 0.1]
        chosen = random.choice(top_candidates)
        return cls._queue_entry_point(chosen)

    @classmethod
    def choose_best_nearby_ride(cls, position, nearby_rides, terrain, ride_preferences):
        """Select the best nearby ride."""
        if not nearby_rides:
            return None

        best_ride = None
        best_score = None
        for ride in nearby_rides:
            score = cls.compute_ride_score(position, ride, terrain, ride_preferences)
            if best_score is None or score > best_score:
                best_ride = ride
                best_score = score

        if best_score is None or best_score < cls.MIN_COMMIT_SCORE:
            return None
        return best_ride

    @classmethod
    def compute_ride_score(cls, position, ride, terrain, ride_preferences):
        """Score a ride combining preference, rating, queue, and distance."""
        category = cls._resolve_category(ride)
        preference = ride_preferences.get(category, 0.2)
        rating = getattr(ride, "rating", 0.5)
        queue_ratio = len(ride.queue) / max(1, ride.capacity)

        rx, ry = ride.center()
        px, py = position
        distance = abs(px - rx) + abs(py - ry)
        normaliser = max(1.0, terrain.width + terrain.height)
        distance_score = distance / normaliser

        w = cls.UTILITY_WEIGHTS
        return (
            w["preference"] * preference
            + w["rating"] * rating
            + w["queue"] * queue_ratio
            + w["distance"] * distance_score
        )

    @staticmethod
    def calculate_exit_probability(rides_completed, patron_type):
        """Estimate the chance that a visitor leaves the park."""
        if patron_type == PatronType.IMPATIENT:
            if rides_completed >= 7:
                return 0.7
            if rides_completed >= 5:
                return 0.35
            base = 0.05
        elif patron_type == PatronType.EXPLORER:
            if rides_completed >= 6:
                return 0.55
            if rides_completed >= 4:
                return 0.25
            base = 0.02
        else:  # ADVENTURER, FAMILY
            if rides_completed >= 7:
                return 0.65
            if rides_completed >= 5:
                return 0.3
            base = 0.03

        return base

    @staticmethod
    def _queue_entry_point(ride):
        x, y, w, h = ride.bbox
        return (x + w / 2.0, y + h + 1.0)

    @staticmethod
    def _resolve_category(ride):
        category = getattr(ride, "category", None)
        if category:
            return category
        category = RIDE_CATEGORY_MAP.get(ride.ride_type)
        if category:
            return category
        return RideCategory.GENTLE
