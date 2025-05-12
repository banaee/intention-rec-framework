from enum import Enum, auto
from typing import List, Union, Dict, Any
from intentions.state_representation import State, Predicate, Fluent


class IntentionType(Enum):
    # GOAL = auto()
    TASK = auto()
    ACTION = auto()


class TaskOrigin(Enum):
    ASSIGNED = auto()      # explicitly given tasks (e.g., deliver items)
    FORESEEABLE = auto()   # human behavior tasks we can predict (e.g., take coffee, bathroom)
    UNKNOWN = auto()       # tasks we know exist but don't know when they'll happen (e.g., search for missing item)


class TaskType(Enum):
    # Usually ASSIGNED origin
    DELIVER_ITEM = "deliver_item"     # parameters: agent_id, item_id, target_holder
    
    # Usually FORESEEABLE origin
    TAKE_COFFEE = "take_coffee"       # parameters: agent_id, coffee_machine_id
    GO_BATHROOM = "go_bathroom"       # parameters: agent_id, bathroom_location
    OPEN_WINDOW = "open_window"       # parameters: agent_id, window_id
    
    # Usually UNKNOWN origin
    SEARCH_ITEM = "search_item"       # parameters: agent_id, item_id
    HANDLE_ERROR = "handle_error"     # parameters: agent_id, error_type


class ActionType(Enum):
    MOVE_TO = "move_to"         # parameters: agent_id, target_entity  
    PICK_UP = "pick_up"         # parameters: agent_id, item_id
    PLACE = "place"             # parameters: agent_id, item_id, target_holder



class Intention:
    def __init__(self, desired_state: State):
        self.desired_state = desired_state
        self.intention_type = None  # Will be set by child classes


    # def __repr__(self):
    #     return f"{self.intention_type.name}Intention(name='{self.name}', desired_state={self.desired_state})"


    def is_achieved(self, world_state: State) -> bool:
        """Check if intention is achieved by comparing desired state against world state"""
        for desired_pred in self.desired_state.predicates:
            found = False
            for world_pred in world_state.predicates:
                if (desired_pred.name == world_pred.name and 
                    desired_pred.args == world_pred.args):
                    found = True
                    break
            if not found:
                ####################################print(f"Failed to find / Not yet matching predicate for: {desired_pred}")
                return False
        return True
    

    def update_current_state(self, state: State):
        self.current_state = state



class TaskIntention(Intention):
    def __init__(self, task_type: TaskType, 
                 origin: TaskOrigin, 
                 desired_state: State, 
                 parameters: Dict[str, Any] = None):
        super().__init__(desired_state=desired_state)
        self.intention_type = IntentionType.TASK
        self.task_type = task_type
        self.origin = origin
        self.parameters = parameters or {}

    def __repr__(self):
        param_str = f"({self.parameters.get('item_id', '')})" if 'item_id' in self.parameters else ""
        return f"{self.task_type.name}{param_str}"
    

    def is_achieved(self, world_state: State) -> bool:
        """Check if task is achieved by comparing desired state against world state"""
        return super().is_achieved(world_state)
    


class ActionIntention(Intention):
    def __init__(self, action_type: ActionType, desired_state: State, 
                 parameters: Dict[str, Any]):
        super().__init__(desired_state=desired_state)
        self.intention_type = IntentionType.ACTION
        self.action_type = action_type
        self.parameters = parameters


    def __repr__(self):
        return f"ActionIntention(type={self.action_type.name}, parameters={self.parameters})"
    

    def is_achieved(self, world_state: State) -> bool:
        """Check if action is achieved by comparing desired state against world state"""
        return super().is_achieved(world_state)
    
    


# # Example action desired states:
# move_action = ActionIntention(
#     name="move_to",
#     desired_state=State([
#         Predicate("at", ["human_1", f"item_{item_id}"])
#     ]),
#     parameters={"agent_id": agent_id, "target_entity": f"item_{item_id}"}
# )

# pickup_action = ActionIntention(
#     name="pick_up",
#     desired_state=State([
#         Predicate("holding", ["human_1", item_id])
#     ]),
#     parameters={"agent_id": "human_1", "item_id": item_id}
# )

# place_action = ActionIntention(
#     name="place",
#     desired_state=State([
#         Predicate("on", ["human_1", "kitting_table"])
#     ]),
#     parameters={"agent_id": "human_1", "item_id": item_id, "location": "kitting_table"}
# )