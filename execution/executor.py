from typing import List, Optional
from intentions.factory_intentions import ActionIntention, ActionType
from execution.microactions import microaction, microactionType
from intentions.state_representation import State
from planning import path_planner


'''
Execution Layer

Single Executor class handles ALL execution (replaces microactionExecutor and ActionExecutionManager)
Manages microaction sequences, handles failures, triggers replanning
Executes microactions, monitors results
'''


class Executor:
    def __init__(self, agent):
        self.agent = agent

        self.current_action = None
        self.current_task = None

        self.current_microactions = []
        self.current_action_sequence = []
        

    def act(self):
        """act is called by the agent's step method each tick"""
        '''
        print(f"\n--- Executor Step [{self.agent.unique_id}] ---")
        '''
        
        # ------------------------------------------------
        # 1. Action Management
        # ------------------------------------------------
        # Get new action if needed
        if not self.current_action:
            print(f"Assigned task: {self.agent.assigned_taskIntentions}")
            self.current_action = self._get_next_action()
            if self.current_action:
                print(f"→ Starting new action: {self.current_action.action_type.name}")
                # print(f"  Parameters: {self.current_action.parameters}")
            else:
                print("→ No actions available")
                return

        # ------------------------------------------------
        # 2. World State Check
        # ------------------------------------------------
        world_state = self.agent.model.state_manager.get_state()

        # Check if current action is complete with debug info
        if self.current_action:
            print("\nChecking action achievement:")
            print(f"Action: {self.current_action.action_type.name}: {self.current_action.parameters}")
            # print(f"Desired state: {self.current_action.desired_state}")
            # print(f"Current world predicates: {world_state.predicates}")
            achieved = self.current_action.is_achieved(world_state)
            print(f"Action achieved: {achieved}")
            
            if achieved:
                print(f"✓ Action completed: {self.current_action.action_type.name}")
                self.current_action = None
                self.current_microactions = []
                return

        # # Check if current action is complete with debug info 
        # if self.current_action and self.current_action.is_achieved(world_state):
        #     print(f"✓ Action completed: {self.current_action.action_type.name}")
        #     self.current_action = None
        #     self.current_microactions = []
        #     return


        # ------------------------------------------------
        # 3. microaction Planning
        # ------------------------------------------------
        # Plan new microactions if needed
        if not self.current_microactions:
            self.current_microactions = self._plan_microactions_for_action(self.current_action, world_state)
            if self.current_microactions:
                print(f"→ Planned new micro-action: {self.current_microactions[0].microaction_type.name}")
            else:
                print("✗ Could not plan micro-actions for action")
                self.current_action = None  # Clear action to force replanning
                return

        # ------------------------------------------------
        # 4. micro-action Execution
        # ------------------------------------------------
        # Execute next micro-action
        microaction = self.current_microactions[0]
        '''
        print(f"→ Executing: {microaction.microaction_type.name}")
        '''
        
        if self._execute_microaction(microaction):
            '''
            print(f"✓ micro-action completed: {microaction.microaction_type.name}")
            '''
            self.current_microactions.pop(0)
        
        else:
            print("✗ micro-action failed. Discarding remaining micro-actions.")
            self.current_microactions = []

            '''
            Potential Improvements
                Error Handling for micro-actions:
                    If an micro-action fails, the entire plan is discarded. 
                    This is acceptable for simple simulations, but for complex ones, consider implementing error recovery 
                    to reattempt failed micro-actions or replan dynamically without discarding everything.
                    ...
                    print("✗ micro-action failed. Attempting recovery.")
                    if self._recover_microaction(microaction):
                        print(f"✓ micro-action recovered: {microaction.microaction_type.name}")
                    else:
                        print("✗ Recovery failed. Discarding plan.")
                        self.current_microactions = []
            '''

        # Print current state
        print(f"Position: {self.agent.pos}")
        if self.agent.carrying:
            print(f"Carrying: {self.agent.carrying.unique_id}")



        
        
       
    def _execute_microaction(self, microaction: microaction) -> bool:
        """Execute a single micro-action"""
        
        # ------------------------------------------------
        # MOVE_STEP micro-action
        # ------------------------------------------------
        if microaction.microaction_type == microactionType.MOVE_STEP:
            target_pos = microaction.parameters.get('target_pos')
            # if target_pos and self.agent.model.grid.is_cell_empty(target_pos):
            if target_pos:
                # Move agent itself
                self.agent.model.grid.move_agent(self.agent, target_pos)
                
                # if carrying item, ensure position sync and move
                if self.agent.carrying:
                    item = self.agent.carrying
                    item.pos = self.agent.pos       # Ensure position is synced
                    self.agent.model.grid.move_agent(item, target_pos)      # Move item in grid
                
                return True
 
        # ------------------------------------------------
        # GRAB micro-action
        # ------------------------------------------------  
        elif microaction.microaction_type == microactionType.GRAB:
            item_id = microaction.parameters.get('item_id')
            item = self.agent.model.items.get(item_id)
            
            if not item or self.agent.carrying:
                print(f"Cannot grab: item={item}, carrying={self.agent.carrying}")
                return False
                
            # Handle item pickup/grab
            prev_holder = item.holder
            if prev_holder and hasattr(prev_holder, 'remove_item'):
                prev_holder.remove_item(item)    # this will clear item.holder 
                
            # just move the item to the agent's position
            item.pos = self.agent.pos   # Ensure position is synced before move
            self.agent.model.grid.move_agent(item, self.agent.pos)    # Move_agent handles the item's holder and pos update

            
            # Update relationship state
            self.agent.carrying = item
            item.holder = self.agent
            
            print(f"Successfully grabbed {item_id}")
            return True

        # ------------------------------------------------
        # RELEASE micro-action
        # ------------------------------------------------
        elif microaction.microaction_type == microactionType.RELEASE:
            if not self.agent.carrying:
                print("Cannot release: not carrying anything")
                return False
                
            item = self.agent.carrying
            target_holder = microaction.parameters.get('target_holder')   #consistant naming of target_holder (e.g. kitting_table, shelf_1, shelf_2)
            
            
            # Get target holder object
            holder_obj = None
            if target_holder == "kitting_table":
                holder_obj = self.agent.model.kitting_table
            elif target_holder.startswith("shelf_"):
                holder_obj = self.agent.model.shelves.get(target_holder)
                
            if not holder_obj or not hasattr(holder_obj, 'add_item'):
                print(f"Invalid target holder: {target_holder}")
                return False
            

            # Move item to holder's position (handles grid updates)
            self.agent.model.grid.move_agent(item, holder_obj.pos)    # Move_agent handles the item's holder and pos update in physical layer
            
            
            # Update relationship state in physical layer
            self.agent.carrying = None
            holder_obj.add_item(item)   # this will update item.holder to holder_obj
            print(f"Successfully released {item.unique_id} on {target_holder}")
            return True
                

        else:
            print(f"Unknown micro-action type: {microaction.microaction_type}")


        return False



    def _get_next_action(self) -> Optional[ActionIntention]:
        """Get next unachieved action from tasks"""
        print("Getting next action")
        world_state = self.agent.model.state_manager.get_state()

        # If we have remaining actions for current task, use next one
        if self.current_action_sequence:
            return self.current_action_sequence.pop(0)
            

        if self.current_task and self.current_task.is_achieved(world_state):
            # Update agent's current_task to None
            self.agent.current_task = None
            self.current_task = None
    
    
        # Get new task and its actions if needed
        if not self.current_task:
            for task in self.agent.assigned_taskIntentions:
                if not task.is_achieved(world_state):
                    # Set both executor's and agent's current task
                    self.current_task = task
                    self.agent.current_task = task
                    
                    actions = self.agent.planner.plan_for_task(task, world_state)
                    if actions:
                        # Store remaining actions in the sequence
                        self.current_action_sequence = actions[1:]
                        return actions[0]
        
        return None





    # def _get_next_action(self) -> Optional[ActionIntention]:
    #     """Get next unachieved action from tasks"""
        
    #     print("Getting next action")
    #     print(self.agent.assigned_taskIntentions)
    #     world_state = self.agent.model.state_manager.get_state()
    #     # # print("world_state in _get_next_action is: ", world_state)

    #     # If we have remaining actions in sequence, use next one
    #     if self.current_action_sequence:
    #         return self.current_action_sequence.pop(0)
            
    #     # Otherwise plan new sequence for unachieved task
    #     for task in self.agent.assigned_taskIntentions:
    #         if not task.is_achieved(world_state):
    #             actions = self.agent.planner.plan_for_task(task, world_state)
    #             if actions:
    #                 self.current_action_sequence = actions[1:]  # Store rest of sequence
    #                 return actions[0]
    #     return None



    def _plan_microactions_for_action(self, action: ActionIntention, world_state: State) -> List[microaction]:
        """Convert action to sequence of micro-actions with debug prints"""
        print(f"\nPlanning micro-actions for action: {action.action_type.name}")
        # print(f"Action parameters: {action.parameters}")
        # print(f"Current world state predicates:")
        # for pred in world_state.predicates:
        #     print(f"  {pred}")


        '''
        TODO: Handling Actions with Preconditions
            If actions require specific preconditions (e.g., "carrying an item" or "reaching a position"), ensure the Planner checks these and plans accordingly.
                Example in _plan_microactions_for_action:
                def _plan_microactions_for_action(self, action, world_state):
                    if not action.preconditions_met(world_state):
                        print(f"✗ Preconditions not met for action: {action.action_type.name}")
                        return []
                    return self.planner.plan(action, world_state)
        '''



        # ------------------------------------------------
        # Action: move_to 
        # ------------------------------------------------
        if action.action_type == ActionType.MOVE_TO:
            # Get current and target positions
            start_pos = self.agent.pos
            target_entity_id = action.parameters['target_entity']
            target_pos = None
            
            print(f"Planning move from {start_pos} to entity {target_entity_id}")
            
            # Find target position in world state
            for predicate in world_state.predicates:
                if predicate.name == "at" and predicate.args[0] == target_entity_id:
                    try:
                        x, y = map(int, predicate.args[1].split(","))
                        target_pos = (x, y)
                        print(f"Found target position: {target_pos}")
                    except Exception as e:
                        print(f"Error parsing position: {e}")
                    break
                    
            if not target_pos:
                print(f"Could not find position for entity {target_entity_id}")
                return []
            
            
            # call an advanced path panning to generate a path
            # path_with_velocity = path_planner.get_robot_path_with_velocity(start_pos, target_pos, world_state, self.agent)
            
            
            
            # Generate path as sequence of positions
            path = self._calculate_path(start_pos, target_pos)
            print(f"Calculated path: {path}")
            
            # Store the path in the agent for visualization
            if not hasattr(self.agent, 'planned_path'):
                self.agent.planned_path = []
            self.agent.planned_path = path

            # Convert path to micro-actions
            microactions = [microaction(microactionType.MOVE_STEP, {"target_pos": pos}) for pos in path[1:]]
            print(f"Generated {len(microactions)} move micro-actions")
            return microactions




        # ------------------------------------------------
        # Action: pick_up
        # ------------------------------------------------
        elif action.action_type == ActionType.PICK_UP:
            print(f"Planning pickup for item {action.parameters['item_id']}")
            # clear the planned path if any
            if hasattr(self.agent, 'planned_path'):
                self.agent.planned_path = []
            # Check if item is already held
            # Check if item is already held by another agent
            # Check if item is in the world state
                # TODO
            
            
            return [microaction(microactionType.GRAB, {"item_id": action.parameters['item_id']})]

        # ------------------------------------------------
        # Action: place
        # ------------------------------------------------
        elif action.action_type == ActionType.PLACE:
            print(f"Planning place micro-action for item {action.parameters['item_id']} on {action.parameters['target_holder']}")
            # clear the planned path if any
            if hasattr(self.agent, 'planned_path'):
                self.agent.planned_path = []
            # Check if item is already held
            # Check if item is already held by another agent
            # Check if item is in the world state
                # TODO
            return [microaction(microactionType.RELEASE, {"target_holder": action.parameters['target_holder']})]

        
        print(f"Unknown action type: {action.action_type.name}")
        return []







    def _plan_move_microactions(self, action: ActionIntention, world_state: State) -> List[microaction]:
        """Plan sequence of move micro-actions to reach target"""
        # Get current and target positions
        start_pos = self.agent.pos
        target_entity_id = action.parameters['target_entity']
        target_pos = None
        
        # Find target position in world state
        for predicate in world_state.predicates:
            if predicate.name == "at" and predicate.args[0] == target_entity_id:
                x, y = map(int, predicate.args[1].split(","))
                target_pos = (x, y)
                break
                
        if not target_pos:
            return []
            
        # Generate path as sequence of positions
        path = self._calculate_path(start_pos, target_pos)
        
        # Convert path to micro-actions
        return [microaction(microactionType.MOVE_STEP, {"target_pos": pos}) for pos in path[1:]]


    def _plan_pickup_microactions(self, action: ActionIntention, world_state: State) -> List[microaction]:
        """Plan sequence of micro-actions to pick up item"""
        return [microaction(microactionType.GRAB, {"item_id": action.parameters['item_id']})]

    
    def _plan_place_microactions(self, action: ActionIntention, world_state: State) -> List[microaction]:
        """Plan sequence of micro-actions to place item"""
        return [microaction(microactionType.RELEASE, {"target_holder": action.parameters['target_holder']})]
    

    # ------------------------------------------------
    # Helper methods
    # ------------------------------------------------
    def _calculate_path(self, start: tuple, end: tuple) -> List[tuple]:
        """Simple direct path planning - could be enhanced with pathfinding"""
        path = []
        x, y = start
        target_x, target_y = end
        pixels_per_step = 50
        
        dx = target_x - x
        dy = target_y - y
        # distance = max(abs(dx), abs(dy))  # Chebyshev distance (max of dx, dy or L-infinity norm)
        distance = int(((dx ** 2 + dy ** 2) ** 0.5)) # Euclidean distance (L2 norm)

        if distance <= pixels_per_step:
            # If distance is less than or equal to pixels_per_step, create one step
            path.append(start)
            path.append(end)
            return path

        # Otherwise, calculate the number of steps
        steps = max(1, int(distance / pixels_per_step) + 1)

        for i in range(steps + 1):
            next_x = x + (dx * i) // steps
            next_y = y + (dy * i) // steps
            path.append((next_x, next_y))
            
        if path[-1] != end:
            path.append(end)
            
        return path
    
