



GRID_WIDTH = 1600
GRID_HEIGHT = 800


# Factory Layout Configuration
FACTORY_LAYOUT = {
    "width": GRID_WIDTH,
    "height": GRID_HEIGHT,
    "door_size": (150, 30),  # Size of the door (width, height)
    "kitting_size": (300, 90),  # Size of the kitting table (width, height)
    "num_shelves": 8,  # Total number of shelves
    "items_per_shelf": 4,  # Number of items per shelf
    "shelf_size": (100,100),   # Size of each shelf (width and height)
    "item_size": (25,25),     # Size of each item (width and height)
    "robot_size": (30,50),    # Size of each robot (width and height)
    "human_size": (20,50),   # Size of each human (width and height)
    }




# =============================================================================
# WALLS CONFIG
# =============================================================================
# WALLS = [
#     {
#         "id": "north_wall",
#         "start": (0, 0),
#         "end": (FACTORY_LAYOUT["width"], 0)
#     },
#     {
#         "id": "east_wall",
#         "start": (FACTORY_LAYOUT["width"], 0),
#         "end": (FACTORY_LAYOUT["width"], FACTORY_LAYOUT["height"])
#     },
#     {
#         "id": "south_wall",
#         "start": (0, FACTORY_LAYOUT["height"]),
#         "end": (FACTORY_LAYOUT["width"], FACTORY_LAYOUT["height"])
#     },
#     {
#         "id": "west_wall",
#         "start": (0, 0),
#         "end": (0, FACTORY_LAYOUT["height"])
#     }
# ]

# Simple 2-zone layout in south corners
ZONE_SIZE = min(GRID_WIDTH, GRID_HEIGHT) // 2
    
ZONES = [
    {
        "id": "zone_SE",
        "name": "Zone Southeast",
        "x_min": GRID_WIDTH - ZONE_SIZE,
        "x_max": GRID_WIDTH,
        "y_min": 0,
        "y_max": ZONE_SIZE
    },
    {
        "id": "zone_SW",
        "name": "Zone Southwest",
        "x_min": 0,
        "x_max": ZONE_SIZE,
        "y_min": 0,
        "y_max": ZONE_SIZE
    },
    {
        "id": "zone_NW",
        "name": "Zone Northwest",
        "x_min": 0,
        "x_max": ZONE_SIZE,
        "y_min": GRID_HEIGHT - ZONE_SIZE,
        "y_max": GRID_HEIGHT
    },
    {
        "id": "zone_NE",
        "name": "Zone Northeast",
        "x_min": GRID_WIDTH - ZONE_SIZE,
        "x_max": GRID_WIDTH,
        "y_min": GRID_HEIGHT - ZONE_SIZE,
        "y_max": GRID_HEIGHT
    }
]

def get_zone_for_position(pos):
    x, y = pos
    for zone in ZONES:
        if (zone["x_min"] <= x <= zone["x_max"] and
            zone["y_min"] <= y <= zone["y_max"]):
            return zone
    
    return None  # Position not in any defined zone


# 