from collections import defaultdict
from typing import List, Optional, Dict, Tuple, Set
import random
import numpy as np
import logging


from execution.microactions import microaction
from mesa_fork import Agent
# from intentions.factory_action_manager_old import ActionType, microactionType, microaction, Action, Task, ActionPlanner

from intentions.intention_recognition import HumanIntentionRecognition



from planning.planner import Planner
from execution.executor import Executor

from intentions.factory_intentions import TaskIntention, ActionIntention
from intentions.state_representation import State, Predicate, Fluent 


class Operator(Agent):
    def __init__(self, unique_id: str, model, 
                 size: Tuple[int, int], 
                 init_pos: Tuple[int, int], 
                 side: str, zone: str):
        super().__init__(unique_id, model)
        
        # id is inherited from Agent class. It will be set to unique_id in super().__init__()
        # pos is inherited from Agent class. It will be set when placing the agent on the grid (see FactoryModel)
        
        # basic attributes
        self.unique_id = unique_id
        self.model = model
        self.size = size
        self.init_pos = init_pos
        self.side = side
        self.zone = zone

        self.carrying = None
        self.planned_path = []


        # Tasks and intentions
        self.assigned_taskIntentions: Set[TaskIntention] = set()

        # We don't need those two attributes anymore. They're replaced by the state management in the Executor
        # self.acheived_taskIntentions: Set[TaskIntention] = set()
        # self.current_plan: List[ActionIntention] = []
        
    
    

    def step(self):
        # Base step method called by both Human and Robot
        print(f"\n--- {self.unique_id} Step no. {self.model.schedule.steps} ---")
        
        # runs subclass-specific step logic (implemented by subclasses)
        self._agent_step()
        
        # Update tracking variables from executor
        self.current_task = self.executor.current_task
        self.current_action = self.executor.current_action
        self.current_microaction = self.executor.current_microactions[0] if self.executor.current_microactions else None
        
        # Print debug info
        if self.carrying:
            print(f"Carrying: {self.carrying.unique_id}")
        print(f"Position: {self.pos}")
        print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {self.unique_id}, Current task: {self.current_task} ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(f"Current action: {self.current_action.action_type.name if self.current_action else None}")
        print(f"Current microaction: {self.current_microaction.microaction_type.name if self.current_microaction else None}")
    
    
    
        
    # def execute_microaction(self, microaction: microaction) -> bool:
    #     # each agent will have its own implementation of this method
    #     # it should return True if the micro-action was successful, False otherwise
    #     pass
            
    
    
        
        



# ========================================================
# Human class
# ========================================================
class Human(Operator):
    def __init__(self, unique_id: str, model, size: Tuple[int, int], init_pos: Tuple[int, int], side: str, zone: str):
        super().__init__(unique_id=unique_id, model=model, size=size, init_pos=init_pos, side=side, zone=zone)
        


        # Human-specific planning/execution
        self.planner = Planner()  # Can be HumanPlanner in future
        self.executor = Executor(self)  # Can be HumanExecutor in future
        
        # Keep for human-specific reasoning
        self.finished = False
        self.current_task: TaskIntention = None
        
        # These move to executor but we can track for human reasoning
        self.current_action: ActionIntention = None
        self.current_microaction: microaction = None


        # *_sequence attributes as they're handled in Executor
        # self.current_action_sequence: List[ActionIntention] = []
        # self.current_microaction_sequence: List[microaction] = []
       


    def _agent_step(self):

        # human specific simulaion-execution step
        self.executor.act()



# ========================================================
# Robot class
# ========================================================
class Robot(Operator):
    def __init__(self, unique_id: str, model, size: Tuple[int, int], init_pos: Tuple[int, int], side: str, zone: str):
        super().__init__(unique_id=unique_id, model=model, size=size, init_pos=init_pos, side=side, zone=zone)


        # Robot-specific planning/execution
        self.planner = Planner()  # Can be RobotPlanner in future
        self.executor = Executor(self)  # Can be RobotExecutor in future        
        # Robot-specific tracking
        self.current_action: ActionIntention = None
        self.current_microaction: microaction = None

        # initialising the intention recognision system
        self.intention_recognition = HumanIntentionRecognition(self)



        # *_sequence attributes as they're handled in Executor
        # self.current_action_sequence: List[ActionIntention] = []
        # self.current_microaction_sequence: List[microaction] = []
        
        # TODO: later for reasoning might be needed 
        # self.observed_human_microactions: List[microaction] = []
        # self.inferred_human_action: Optional[Action] = None
        # self.inferred_human_task_action: Optional[Task] = None
        # self.perceived_environment: Dict[str, Dict[int, Tuple[int, int]]] = {}


    def _agent_step(self):

        # First, observe humans and update beliefs BEFORE doing your own actions
        self.intention_recognition.step()

        # Then agent-specific step will act to do its own actions
        self.executor.act()


        self._print_beliefs()



    # ---------------------------------------------------------
    # methods for reasoning about human intentions
    # ---------------------------------------------------------

    def _print_beliefs(self):        
        # Print robot's reasoning about human intentions
        print(f"\n--- Robot's reasoning about humans ---")
        for human_id in self.model.humans:
            print(f"Task probabilities for {human_id}:")
            task_probs = self.intention_recognition.get_all_task_probabilities(human_id)
            
            if task_probs:
                # Group tasks by type for readability
                by_type = defaultdict(list)
                for task_id, prob in task_probs.items():
                    task = self.model.task_library.get_task_by_id(task_id)
                    if task:
                        by_type[task.task_type].append((task_id, prob, task.parameters.get('item_id')))
                
                # Print tasks grouped by type and sorted by probability
                for task_type, tasks in by_type.items():
                    print(f"  {task_type.name}:")
                    # Sort each group by probability
                    for task_id, prob, item_id in sorted(tasks, key=lambda x: x[1], reverse=True):
                        if prob > 0.01:    
                            if item_id:
                                print(f"    {task_id} ({item_id}): {prob:.2f}")
                            else:
                                print(f"    {task_id}: {prob:.2f}")
            else:
                print("  No task probabilities available yet")
            print()

        
    def get_belief_data_for_viz(self):
        """Return belief data for visualization"""
        belief_data = {}
        for human_id in self.model.humans:
            belief_data[human_id] = {
                'step': self.model.schedule.steps,
                'probabilities': self.intention_recognition.get_all_task_probabilities(human_id),
                'current_action': self.intention_recognition.inferred_actions.get(human_id, (None, {}))
            }
        return belief_data