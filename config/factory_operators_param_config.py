import random
from typing import Dict, List, Tuple
from config.layout_user_config import FACTORY_LAYOUT as LAYOUT


# =============================================================================
# define the operators
# =============================================================================
ROBOTS = [
    {
        "id": "robot_1",
        "size": LAYOUT["robot_size"],
        "init_pos": None,
        "pos": None,
        "side": "left"
    }
]

HUMANS = [
    {
        "id": "human_1",
        "size": LAYOUT["human_size"],
        "init_pos": None,
        "pos": None,
        "side": "right"
    }
]


# =============================================================================
# Export configurations
# ============================================================================= 
def get_operators_config(objects: Dict) -> Dict:
    
    items = objects["items"]
    shelves = objects["shelves"]
    kitting_table = objects["kitting_table"]
    doors = objects["doors"]
    
    
    
    global ROBOTS, HUMANS
    
    # Assign initial positions
    for robot in ROBOTS:
        robot["init_pos"] = __get_operator_init_position(robot, doors)
        robot["pos"] = robot["init_pos"]

    for human in HUMANS:
        human["init_pos"] = __get_operator_init_position(human, doors)
        human["pos"] = human["init_pos"]
    
    return {
        "robots": ROBOTS,
        "humans": HUMANS
    }



# =============================================================================
# AUXILIARY FUNCTIONS
# =============================================================================

def __get_operator_init_position(data: Dict, doors: List[Dict]) -> tuple:
    entry_door = [door for door in doors if door["side"] == data["side"] and door["usage"] == "enter"][0]
    # calculate pos_x
    if data["side"] == "left":
        pos_x = entry_door["pos"][0] + entry_door["size"][0] 
    else:
        pos_x = entry_door["pos"][0] - data["size"][0]
    # calculate pos_y
    pos_y = entry_door["pos"][1] - data["size"][1]
    return (pos_x, pos_y)


def get_robot_ids(robots):
    return [robot["id"] for robot in robots]

def get_human_ids(humans):
    return [human["id"] for human in humans]


