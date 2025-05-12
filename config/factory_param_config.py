from typing import Dict, List, Tuple
from config.layout_user_config import FACTORY_LAYOUT as LAYOUT

from config.factory_objects_params_config import get_objects_config
from config.factory_operators_param_config import get_operators_config


# =============================================================================
# NOTE: all the sizes and positions of the agents in mesa simulation are defined 
# in terms of cells in the grid. 
# For example, if the pos of robot is (3, 2), it means the robot is in the cell (1, 1) in the grid.
#   but if the cell size is defined as 12 pixels, then
#   the actual position of the robot in the canvas is (3*12, 2*12) = (36, 24) pixels. 
# =============================================================================


def get_factory_model_params() -> Dict:
 
    objects = get_objects_config()
    operators = get_operators_config(objects)
 
    return {
        "width": LAYOUT["width"],
        "height": LAYOUT["height"],
        
        "doors_p": objects["doors"],
        "kitting_table_p": objects["kitting_table"],
        "shelves_p": objects["shelves"],
        "items_p": objects["items"],
        
        "robots_p": operators["robots"],
        "humans_p": operators["humans"],
        
        "mytext_p": "TEXT mytext in model_params",

    }




def print_params(model_params):
    for key in model_params:
        print(key, ":", model_params[key])
        print("--"*50)


def test():
    model_params = get_factory_model_params()
    print_params(model_params)
    x=1
    
if __name__ == "__main__":    
    test()
    
    