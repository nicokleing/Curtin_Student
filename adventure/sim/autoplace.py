"""Deterministic ride auto-placement helpers."""
from __future__ import annotations

from copy import deepcopy
from typing import Iterable, List, Sequence, Tuple

_DEFAULT_FOOTPRINT = {
    "pirate": (20, 12),
    "ferris": (18, 18),
    "roller": (24, 16),
}


def _get_size(ride: dict) -> Tuple[int, int]:
    ride_type = (ride.get("type") or "").lower()
    if ride_type in _DEFAULT_FOOTPRINT:
        return _DEFAULT_FOOTPRINT[ride_type]
    return _DEFAULT_FOOTPRINT["pirate"]


def _expand_bbox(left: int, top: int, width: int, height: int, pad: int) -> Tuple[int, int, int, int]:
    return (
        left - pad,
        top - pad,
        left + width + pad,
        top + height + pad,
    )


def _rects_overlap(a: Sequence[int], b: Sequence[int]) -> bool:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return not (ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1)


def auto_place(
    rides: Iterable[dict],
    width: int,
    height: int,
    min_gap: int = 2,
) -> Tuple[List[dict], List[str]]:
    """Return (placed_rides, warnings) ensuring no overlaps."""
    placed: List[dict] = []
    warnings: List[str] = []
    occupied: List[Tuple[int, int, int, int]] = []

    layout = deepcopy(list(rides))
    for index, ride in enumerate(layout):
        ride_width, ride_height = _get_size(ride)
        found = False
        y = min_gap
        while y + ride_height <= height - min_gap and not found:
            x = min_gap
            while x + ride_width <= width - min_gap and not found:
                expanded = _expand_bbox(x, y, ride_width, ride_height, min_gap)
                if any(_rects_overlap(expanded, other) for other in occupied):
                    x += ride_width + min_gap
                    continue
                ride_with_bbox = ride.copy()
                ride_with_bbox["bbox"] = (x, y, ride_width, ride_height)
                placed.append(ride_with_bbox)
                occupied.append(expanded)
                found = True
                break
            if not found:
                y += ride_height + min_gap
        if not found:
            warnings.append(f"Ride {ride.get('type', f'#{index + 1}')} trimmed due to space")

    return placed, warnings
