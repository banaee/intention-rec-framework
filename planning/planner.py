from typing import List, Optional
from intentions.factory_intentions import TaskIntention, TaskType, ActionIntention, ActionType
from intentions.state_representation import State, Predicate
from intentions.entity_representation import EntityType, EntityIdentifier


'''
Planning Layer

Single Planner class handles ALL planning (replaces IntentionPlanner and ExecutionPlanner)
Plans in two stages: task→actions, then action→micro-actions
'''

class Planner:
    """Unified planner that handles task-to-action and action-to-microaction planning"""
    
    def plan_for_task(self, task: TaskIntention, world_state: State) -> List[ActionIntention]:
        """Convert a task into sequence of actions"""
        # if task.name.startswith("deliver_item"):
        if task.task_type == TaskType.DELIVER_ITEM:
            item_id = task.parameters.get('item_id')  # this is full item_X string (e.g. "item_1")
            agent_id = task.parameters.get('agent_id')
            
            return [
                # ---------------------------------------------------------
                # Move to item
                # ---------------------------------------------------------
                ActionIntention(
                    action_type=ActionType.MOVE_TO,
                    desired_state=State([
                        Predicate("reach", [agent_id, item_id])   # agent should be able to reach item, for now if they are at the same location, TODO: implement reachability check using neighborhood radius 
                    ]),
                    parameters={
                        "agent_id": agent_id,
                        "target_entity": item_id # this is full item_X string (e.g. "item_1")
                    }
                ),
                # ---------------------------------------------------------
                # Pick up item
                # ---------------------------------------------------------
                ActionIntention(
                    action_type=ActionType.PICK_UP,
                    desired_state=State([
                        Predicate("holding", [agent_id, item_id])
                    ]),
                    parameters={
                        "agent_id": agent_id,
                        "item_id": item_id
                    }
                ),
                # ---------------------------------------------------------
                # Move to kitting table
                # ---------------------------------------------------------
                ActionIntention(
                    action_type=ActionType.MOVE_TO,
                    desired_state=State([
                        Predicate("reach", [agent_id, "kitting_table"])
                    ]),
                    parameters={
                        "agent_id": agent_id,
                        "target_entity": "kitting_table"
                    }
                ),
                # ---------------------------------------------------------
                # Place item on kitting table
                # ---------------------------------------------------------
                ActionIntention(
                    action_type=ActionType.PLACE,
                    desired_state=State([
                        Predicate("on", [item_id, "kitting_table"])
                    ]),
                    parameters={
                        "agent_id": agent_id,
                        "item_id": item_id,
                        "target_holder": "kitting_table"   # could be any holder (shelf/kitting_table, floor, etc.)
                    }
                )
            ]
        return []