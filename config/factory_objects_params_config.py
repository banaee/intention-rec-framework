import random
from typing import Dict, List, Tuple
from config.layout_user_config import FACTORY_LAYOUT as LAYOUT, get_zone_for_position



# =============================================================================
# DOORS CONFIG
# =============================================================================
DOORS = [
    {
        "id": "south_exit",
        "name": "EXIT",
        "usage": "exit",
        "size": LAYOUT["door_size"],
        "init_pos": (LAYOUT["width"] // 2 - LAYOUT["door_size"][0] // 2, 
                0),
        "side": "south",
        "zone": get_zone_for_position((LAYOUT["width"] // 2 - LAYOUT["door_size"][0] // 2, 0))
    },
    {
        "id": "north_entry_west",
        "name": "ENTRANCE B",
        "usage": "enter",
        "size": LAYOUT["door_size"],
        "init_pos": (0, 
                LAYOUT["height"] - LAYOUT["door_size"][1]),
        "side": "left",
        "zone": get_zone_for_position((0, LAYOUT["height"] - LAYOUT["door_size"][1]))
    },
    {
        "id": "north_entry_east",
        "name": "ENTRANCE A",
        "usage": "enter",
        "size": LAYOUT["door_size"],
        "init_pos": (LAYOUT["width"] -  LAYOUT["door_size"][0], 
                LAYOUT["height"] - LAYOUT["door_size"][1]),
        "side": "right",
        "zone": get_zone_for_position((LAYOUT["width"] -  LAYOUT["door_size"][0], LAYOUT["height"] - LAYOUT["door_size"][1]))
    },
]
    


# =============================================================================
# KITTING TABLE CONFIG
# =============================================================================
WALL_MARGIN = 2

def get_kitting_table_position(layout: Dict) -> Tuple[int, int]:
    """Get the position of the kitting table."""
    return (layout["width"] // 2 - layout["kitting_size"][0] // 2, layout["height"] - layout["kitting_size"][1] - WALL_MARGIN)


KITTING_TABLE = {
    "id": "kitting_table",
    "size": LAYOUT["kitting_size"],
    "init_pos": get_kitting_table_position(LAYOUT),
    "side": "north",
    "zone": get_zone_for_position(get_kitting_table_position(LAYOUT))
}


# =============================================================================
# SHELVES CONFIG functions
# =============================================================================

# TODO: assign shelves to the walls automatically 
# there are 3 walls in the room: east, west, and south. 
# assign shelves to these walls: for now: 2 shelves on each west and east walls, and 4 shelves on the south wall.

shelf_east_x = LAYOUT["width"] - LAYOUT["shelf_size"][0] - WALL_MARGIN
SHELF_PLACES_EAST = [(shelf_east_x, 200, "right"), (shelf_east_x, 500, "right")] 
SHELF_PLACES_WEST = [(WALL_MARGIN, 200, "left"), (WALL_MARGIN, 500, "left")]
SHELF_PLACES_SOUTH_EAST = [(1000, WALL_MARGIN, "right"), (1300, WALL_MARGIN, "right")] 
SHELF_PLACES_SOUTH_WEST = [(200, WALL_MARGIN, "left"), (500, WALL_MARGIN, "left")] 
SHELF_POSITIONS = SHELF_PLACES_EAST + SHELF_PLACES_WEST + SHELF_PLACES_SOUTH_EAST + SHELF_PLACES_SOUTH_WEST

SHELVES = []
for i in range(LAYOUT["num_shelves"]):
    shelf_pos = random.choice(SHELF_POSITIONS)
    SHELVES.append({
        "id": f"shelf_{i+1}",
        "size": LAYOUT["shelf_size"],
        "init_pos": (shelf_pos[0], shelf_pos[1]),
        "side": shelf_pos[2],
        "zone": get_zone_for_position((shelf_pos[0], shelf_pos[1]))
    })
    SHELF_POSITIONS.remove(shelf_pos)


# =============================================================================
# ITEMS CONFIG
# =============================================================================

def generate_items(shelves: List[Dict]) -> List[Dict]:
    """Generate items and assign them to shelves."""
    items = []
    counter = 1  # Counter for generating unique_id
    item_w, item_h = LAYOUT["item_size"]

    for shelf in shelves:
        shelf_x, shelf_y = shelf["init_pos"]
        for i in range(LAYOUT["items_per_shelf"]):
            # Calculate exact position relative to shelf
            item_x = shelf_x + i * item_w
            item_y = shelf_y + i * item_h
            
            items.append({
                "unique_id": f"item_{counter}",
                "size": LAYOUT["item_size"],
                "init_pos": (item_x, item_y),
                "init_shelf_id": shelf["id"],
                "holder": None,
                "side": shelf["side"],
                "zone": shelf["zone"]
            })
            counter += 1
    
    return items



ITEMS = generate_items(SHELVES)



# Export configurations
def get_objects_config():
    return {
        "shelves": SHELVES,
        "items": ITEMS,
        "kitting_table": KITTING_TABLE,
        # "walls": WALLS,
        "doors": DOORS,
    }