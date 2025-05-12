import random
import numpy as np
from my_mesa import Agent
# from typing import List, Optional, Tuple

import logging
# from actions.factory_action_manager import ActionType, microactionType, microaction, Action, Task, ActionPlanner


# parent class for all static objects in the factory
class StaticObject(Agent):
    def __init__(self, unique_id: str, model, size, pos, side):
        super().__init__(unique_id, model)
        
        self.size = size
        self.pos = pos   #TODO: update to be the centroid of the objects, not the corner
        self.side = side  
        # logging.debug(f"Initialized StaticObject {unique_id}")
    
    def update_pos(self, given_pos):
        self.pos = given_pos
    
    
    
    
    
class Item(Agent):
    def __init__(self, unique_id: str, size, model, init_pos, pos, init_shelf_id, holder):
        super().__init__(unique_id, model)   # unique_id is "item_X" where X is the number of the item
        
        self.size = size
        self.init_pos = init_pos
        self.init_shelf_id = init_shelf_id      

        self.pos = pos                          # Physical position
        self.holder = holder                    # # Reference to what holds it: shelf/table/agent/None (if on floor)


    def update_holder(self, holder_agent):
        self.holder = holder_agent
    
    def update_pos(self, given_pos):
        self.pos = given_pos

    @property
    def item_id(self) -> str:
        """Returns the full item_X ID string"""
        return self.unique_id




class Shelf(Agent):
    def __init__(self, unique_id, model, size, pos, side):
        super().__init__(unique_id, model)
        self.side = side
        self.size = size 
        self.pos = pos
        self.current_items = []
    
    def add_item(self, item):
        self.current_items.append(item)
        item.holder = self

    def remove_item(self, item):
        self.current_items.remove(item)
        item.holder = None



class KittingTable(Agent):
    def __init__(self, unique_id, model, size, pos, side):
        super().__init__(unique_id, model)
        
        self.size = size
        self.pos = pos
        self.side = side
        self.current_items = []
        # logging.debug(f"Initialized KittingTable {unique_id}")
    
    def add_item(self, item):
        self.current_items.append(item)
        item.holder = self

    def remove_item(self, item):
        self.current_items.remove(item)
        item.holder = None

class Door(Agent):
    def __init__(self, unique_id, model, function, name, size, pos, side):
        super().__init__(unique_id, model)
        
        self.function = function 
        self.name = name 
        self.size = size
        self.pos = pos
        
        # logging.debug(f"Initialized Door {unique_id}")
        
    def open(self):
        pass

    def close(self):
        pass