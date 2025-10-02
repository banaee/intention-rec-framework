import random
import numpy as np
from mesa_fork import Agent
# from typing import List, Optional, Tuple

import logging
# from actions.factory_action_manager import ActionType, microactionType, microaction, Action, Task, ActionPlanner


# parent class for all passive objects in the factory
class PassiveAgent(Agent):
    def __init__(self, unique_id: str, model, 
                 size, side, zone):
        super().__init__(unique_id, model)

        # ID and pos are inherited from Mesa Agent class. 
        # ID will be set to unique_id in super().__init__()
        # "pos" will be set when placing the agent on the grid (see FactoryModel)
        
        self.size = size
        self.side = side
        self.zone = zone

    def update_pos(self, given_pos):
        self.pos = given_pos
    
     
    
    
class Item(PassiveAgent):
    def __init__(self, unique_id: str, model,
                 size,  init_pos,  
                 init_shelf_id,
                 holder,
                 side, zone):
        super().__init__(unique_id, model, size, side=side, zone=zone)

        # ITEM SPECIFIC ATTRIBUTES
        self.init_pos = init_pos              # ONLY items have init_pos (where they start in the factory)
        self.init_shelf_id = init_shelf_id
        self.holder = holder                    # # Reference to what holds it: shelf/table/agent/None (if on floor)

    def update_holder(self, holder_agent):
        self.holder = holder_agent
    
    def update_pos(self, given_pos):
        self.pos = given_pos

    @property
    def item_id(self) -> str:
        """Returns the full item_X ID string"""
        return self.unique_id




class Shelf(PassiveAgent):
    def __init__(self, unique_id, model, 
                 size,  side, zone):
        super().__init__(unique_id, model, size, side=side, zone=zone)

        # Shelf-specific attributes
        self.current_items = []
    
    
    def add_item(self, item):
        self.current_items.append(item)
        item.holder = self

    def remove_item(self, item):
        self.current_items.remove(item)
        item.holder = None


class KittingTable(PassiveAgent):
    def __init__(self, unique_id, model, size, side, zone):
        super().__init__(unique_id, model, size, side=side, zone=zone)

        # KittingTable-specific attributes
        self.current_items = [] # items currently on the table, initially empty

    
    def add_item(self, item):
        self.current_items.append(item)
        item.holder = self

    def remove_item(self, item):
        self.current_items.remove(item)
        item.holder = None


class Door(PassiveAgent):
    def __init__(self, unique_id, model, 
                 size, name, usage, side, zone):
        super().__init__(unique_id, model, size, side=side, zone=zone)

        # Door-specific attributes
        self.usage = usage
        self.name = name

        
    def open(self):
        pass

    def close(self):
        pass



class CoffeeMachine(PassiveAgent):
    def __init__(self, unique_id, model, 
                 size, side, zone):
        super().__init__(unique_id, model, size, side=side, zone=zone)

class ACSwitch(PassiveAgent):
    def __init__(self, unique_id, model, 
                 size, side, zone):
        super().__init__(unique_id, model, size, side=side, zone=zone)    


