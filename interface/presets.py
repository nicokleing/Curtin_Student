"""AdventureWorld configuration presets for the simple CLI mode."""

PRESETS = {
    "small": {
        "width": 100,
        "height": 70,
        "visitors": 60,
        "rides": [
            {"type": "pirate", "capacity": 12, "duration": 30, "queue_limit": 24},
            {"type": "ferris", "capacity": 10, "duration": 35, "queue_limit": 20},
        ],
    },
    "medium": {
        "width": 140,
        "height": 90,
        "visitors": 120,
        "rides": [
            {"type": "pirate", "capacity": 12, "duration": 30, "queue_limit": 30},
            {"type": "ferris", "capacity": 12, "duration": 35, "queue_limit": 25},
            {"type": "pirate", "capacity": 14, "duration": 28, "queue_limit": 30},
        ],
    },
    "large": {
        "width": 180,
        "height": 120,
        "visitors": 200,
        "rides": [
            {"type": "pirate", "capacity": 14, "duration": 30, "queue_limit": 40},
            {"type": "ferris", "capacity": 12, "duration": 35, "queue_limit": 30},
            {"type": "pirate", "capacity": 16, "duration": 28, "queue_limit": 40},
            {"type": "ferris", "capacity": 12, "duration": 32, "queue_limit": 30},
        ],
    },
}
