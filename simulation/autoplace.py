"""Deterministic ride auto-placement helpers."""

from copy import deepcopy

_DEFAULT_FOOTPRINT = {
    "pirate": (20, 12),
    "ferris": (18, 18),
    "roller": (24, 16),
}


def _get_size(ride):
    rtype = (ride.get("type") or "").lower()
    if rtype in _DEFAULT_FOOTPRINT:
        return _DEFAULT_FOOTPRINT[rtype]
    return _DEFAULT_FOOTPRINT["pirate"]


def _expand_bbox(left, top, width, height, pad):
    return (
        left - pad,
        top - pad,
        left + width + pad,
        top + height + pad,
    )


def _rects_overlap(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return not (ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1)


def auto_place(rides, width, height, min_gap=2):
    """Return (placed_rides, warnings) ensuring no overlaps.

    rides: iterable of ride dicts without bbox or with bbox to be replaced.
    width/height: terrain dimensions.
    min_gap: minimum empty tiles around each ride.
    """
    placed = []
    warnings = []
    occupied = []

    layout = deepcopy(list(rides))
    for idx, ride in enumerate(layout):
        rw, rh = _get_size(ride)
        found = False
        y = min_gap
        while y + rh <= height - min_gap and not found:
            x = min_gap
            while x + rw <= width - min_gap and not found:
                expanded = _expand_bbox(x, y, rw, rh, min_gap)
                if any(_rects_overlap(expanded, other) for other in occupied):
                    x += rw + min_gap
                    continue
                ride_with_bbox = ride.copy()
                ride_with_bbox["bbox"] = (x, y, rw, rh)
                placed.append(ride_with_bbox)
                occupied.append(expanded)
                found = True
                break
            if not found:
                y += rh + min_gap
        if not found:
            warnings.append(f"Ride {ride.get('type', f'#{idx+1}')} trimmed due to space")

    return placed, warnings
