from typing import Dict, List, Tuple, Set, Optional, Any
import numpy as np
from collections import defaultdict, deque

from intentions.factory_intentions import TaskIntention, ActionIntention, TaskType, ActionType
from intentions.state_representation import State, Predicate, Fluent 
from execution.microactions import microaction, microactionType

from intentions import movement_probability as mv

class HumanIntentionRecognition:
    """System for robots to recognize human intentions based on observed world state changes"""
    
    def __init__(self, robot):
        self.robot = robot
        self.model = robot.model
        
        # Tracking human state across steps
        self.perceived_human_states = {}  # Current state of each human
        self.previous_human_states = {}   # Previous state of each human
        
        # Store position history for movement analysis (up to 5 recent positions)
        self.position_history = {}  # Dict of human_id -> deque of positions with timestamps
        
        # Store inferred human microactions (with timestamps)
        self.inferred_microactions = {}  # Dict of human_id -> deque of microactions
        
        
        # self.inferred_actions = {}  # Dict of human_id -> current action with parameters
        self.action_probabilities = {}  # Dict of human_id -> dict of action -> probability
        
        # for sequence matching
        self.action_history = {}  # Dict of human_id -> deque of actions with parameters

        
        # Use the task library to initialize possible tasks
        self.all_possible_tasks = self.model.task_library.get_all_tasks()
        
        
        # Store inferred task probabilities
        self.task_probabilities = {}  # Dict of human_id -> dict of task -> probability
        
          
    def step(self):
        """Main update function called from Robot's step method"""
        # 1. Update tracked humans' states
        self._update_perceived_human_states()
        
        # 2. Infer microactions from state changes
        self._infer_microactions()
        
        # 3. Infer actions from microaction patterns
        self._infer_actions()
        
        # 4. Infer tasks from action sequences
        self._infer_tasks()
        
        # 5. Print current beliefs
        # self._log_beliefs()
    
    
    
    def _update_perceived_human_states(self):
        """Update robot's perception of human states (internal belief)"""
        for human_id, human in self.model.humans.items():
            # Move current state to previous state
            if human_id in self.perceived_human_states:
                self.previous_human_states[human_id] = self.perceived_human_states[human_id].copy()
            else:
                self.previous_human_states[human_id] = self._extract_human_state(human)
            
            # Update current state
            self.perceived_human_states[human_id] = self._extract_human_state(human)
            
            # Update position history
            if human_id not in self.position_history:
                self.position_history[human_id] = deque(maxlen=5)  # Track last 5 positions
            
            self.position_history[human_id].append((self.model.schedule.steps, human.pos))
            
            
            # Initialize other tracking structures if needed
            if human_id not in self.inferred_microactions:
                self.inferred_microactions[human_id] = deque(maxlen=10)
            if human_id not in self.action_history:
                self.action_history[human_id] = deque(maxlen=5)
            # NEW:  ensures that each human has an empty dictionary for storing action probabilities when they're first observed
            if human_id not in self.action_probabilities:
                self.action_probabilities[human_id] = {}
            if human_id not in self.task_probabilities:
                self.task_probabilities[human_id] = self._initialize_task_probabilities(human_id)
        
        
    
    def _infer_microactions(self):
        """Infer microactions based on state changes between steps"""
        for human_id in self.perceived_human_states:
            prev = self.previous_human_states.get(human_id)
            curr = self.perceived_human_states[human_id]
            
            # If this is the first observation, can't infer a microaction
            if not prev:
                continue
            
            # Detect movement
            if prev['pos'] != curr['pos']:
                micro = microaction(microactionType.MOVE_STEP, {
                    'target_pos': curr['pos']
                })
                self._record_microaction(human_id, micro)
            
            # Detect grab action
            elif prev['carrying'] is None and curr['carrying'] is not None:
                micro = microaction(microactionType.GRAB, {
                    'item_id': curr['carrying']
                })
                self._record_microaction(human_id, micro)
            
            # Detect release action
            elif prev['carrying'] is not None and curr['carrying'] is None:
                micro = microaction(microactionType.RELEASE, {
                    'target_holder': self._infer_release_target(human_id)
                })
                self._record_microaction(human_id, micro)
            
            # Otherwise assume waiting/scanning - only if you have this microaction type
            elif hasattr(microactionType, 'WAIT'):
                micro = microaction(microactionType.WAIT, {})
                self._record_microaction(human_id, micro)
    
        
        
    def _extract_human_state(self, human):
        """Extract relevant state information from a human agent"""
        state = {
            'pos': human.pos,
            'carrying': human.carrying.unique_id if human.carrying else None,
        }
        return state
    
    # ==============================================
    # microaction inference
    # ==============================================
    
        
    def _record_microaction(self, human_id, micro):
        """Record an inferred microaction with current timestamp"""
        timestamp = self.model.schedule.steps
        self.inferred_microactions[human_id].append((timestamp, micro))
        
        print(f"Robot {self.robot.unique_id} observed {human_id} performing {micro.microaction_type.name}")
    
    
    # ==============================================
    # action probability inference
    # ==============================================
    

    def _infer_actions(self):
        """Infer which high-level action the human is performing based on microaction patterns"""
        for human_id, microactions in self.inferred_microactions.items():
            if not microactions:
                continue
                
            # Get the most recent microaction
            _, latest_micro = microactions[-1]
            
            # Action inference based on microaction type
            action_probs = {}
            
            
            if latest_micro.microaction_type == microactionType.MOVE_STEP:
                # Try to determine where they're moving to
                target_probs = self._infer_movement_targets(human_id)

                        
                # Convert target probabilities to action probabilities
                for target, prob in target_probs.items():
                    action_key = (ActionType.MOVE_TO, target)
                    action_probs[action_key] = prob
                    
                    
                    
            elif latest_micro.microaction_type == microactionType.GRAB:
                # For grab, we're fairly certain about the item
                item_id = latest_micro.parameters.get('item_id', 'unknown')
                action_key = (ActionType.PICK_UP, item_id)
                action_probs[action_key] = 1.0
                
            elif latest_micro.microaction_type == microactionType.RELEASE:
                # For release, we're fairly certain about the target
                target_holder = latest_micro.parameters.get('target_holder', 'unknown')
                action_key = (ActionType.PLACE, target_holder)
                action_probs[action_key] = 1.0
            
            
            # Store the action probabilities for this human
            self.action_probabilities[human_id] = action_probs
            
            
            # Record most likely action in history if different from previous
            if action_probs:
                most_likely_action = max(action_probs.items(), key=lambda x: x[1])
                action_type, target = most_likely_action[0]
                action_params = {'target_entity': target} if action_type == ActionType.MOVE_TO else \
                            {'item_id': target} if action_type == ActionType.PICK_UP else \
                            {'target_holder': target}
                
                # Only add to history if different from the last recorded action
                if (not self.action_history[human_id] or 
                    self.action_history[human_id][-1][0] != (action_type, action_params)):
                    self.action_history[human_id].append(((action_type, action_params), most_likely_action[1]))
        
            
    
    
    def _infer_movement_targets(self, human_id) -> Dict[str, float]:
        """Infer where the human is moving to with probabilities for each potential target"""
        human_pos = self.perceived_human_states[human_id]['pos']
        movement_dir = mv.calculate_movement_direction(self.position_history, human_id)
        return mv.calculate_target_probabilities(self.model, human_id, human_pos, movement_dir)




    
    def _infer_release_target(self, human_id) -> str:
        """Infer where the human placed an item"""
        # Get human's current position
        human_pos = self.perceived_human_states[human_id]['pos']
        
        # Check proximity to kitting table
        kt_distance = mv.calculate_distance(human_pos, self.model.kitting_table.pos)
        if kt_distance < 100:  # Assuming 100 is "close enough"
            return "kitting_table"
        
        # Check proximity to shelves
        for shelf_id, shelf in self.model.shelves.items():
            shelf_distance = mv.calculate_distance(human_pos, shelf.pos)
            if shelf_distance < 100:
                return shelf_id
        
        return "unknown"
    
    

    # ==============================================
    # task probability inference
    # ==============================================
    
    # Update _infer_tasks to use action probabilities
    def _infer_tasks(self):
        """Infer which task the human is trying to complete based on action probabilities"""
        world_state = self.model.state_manager.get_state()
        
        for human_id in self.perceived_human_states:
            if human_id not in self.task_probabilities:
                continue
            
            # Get completed tasks from world state
            completed_tasks = self._get_completed_tasks(human_id)
            print(f"Completed tasks for {human_id}: {completed_tasks}")
            if not completed_tasks:
                print(f"No completed tasks for {human_id}")
            
            
            # Reset completed tasks
            for task_id in completed_tasks:
                del self.task_probabilities[human_id][task_id]
            
            # Redistribute probabilities uniformly if tasks remain
            remaining_tasks = list(self.task_probabilities[human_id].keys())
            if remaining_tasks:
                uniform_prob = 1.0 / len(remaining_tasks)
                for task in remaining_tasks:
                    self.task_probabilities[human_id][task] = uniform_prob
            
            # Continue updating probabilities based on actions
            if human_id in self.action_probabilities and self.action_probabilities[human_id]:
                self._update_task_probabilities_with_probs(
                    human_id, 
                    self.action_probabilities[human_id]
                )
           
           
    # def _infer_tasks(self):
    #     """Infer which task the human is trying to complete based on action probabilities"""
    #     for human_id in self.perceived_human_states:
    #         if human_id not in self.action_probabilities or not self.action_probabilities[human_id]:
    #             continue
            
    #         # Update task probabilities based on observed action probabilities
    #         self._update_task_probabilities_with_probs(human_id, self.action_probabilities[human_id])
         
         
    def _get_completed_tasks(self, human_id):
        """Identify tasks that have been completed based on world state"""
        completed_tasks = []
        world_state = self.model.state_manager.get_state()
        
        for task_id, prob in self.task_probabilities[human_id].items():
            task = self.model.task_library.get_task_by_id(task_id)
            if task and task.is_achieved(world_state):
                completed_tasks.append(task_id)
        
        return completed_tasks   
                
    # Add method to update tasks with probabilistic actions
    def _update_task_probabilities_with_probs(self, human_id, action_probabilities):
        """Update task probabilities based on observed action probabilities"""
        if human_id not in self.task_probabilities:
            self.task_probabilities[human_id] = self._initialize_task_probabilities(human_id)
        
        # Get current task probabilities
        task_probs = self.task_probabilities[human_id]
        
        # Calculate likelihoods for each task given all possible actions
        total_likelihood = 0
        task_likelihoods = {task_id: 0.0 for task_id in task_probs}
        
        # For each task, calculate likelihood based on all possible actions
        for task in self.model.task_library.get_all_tasks():
            task_id = task.parameters.get('task_id')
            if not task_id or task_id not in task_probs:
                continue
                
            prior = task_probs[task_id]
            likelihood = 0.0
            
            # Consider all possible actions with their probabilities
            for action_key, action_prob in action_probabilities.items():
                action_type, target = action_key
                # Calculate how likely this action is given this task
                action_likelihood = self._calculate_action_likelihood_for_task(
                    action_type, target, human_id, task)
                # Weight by action probability
                likelihood += action_prob * action_likelihood
            
            # Store and accumulate with prior
            task_likelihoods[task_id] = likelihood
            total_likelihood += likelihood * prior
        
        # Update probabilities using Bayes' rule
        if total_likelihood > 0:
            for task_id in task_probs:
                prior = task_probs[task_id]
                likelihood = task_likelihoods.get(task_id, 0.0)
                task_probs[task_id] = (likelihood * prior) / total_likelihood
                
                
    # Add helper method for action likelihoods
    def _calculate_action_likelihood_for_task(self, action_type, target, human_id, task):
        """Calculate how likely an action is given a specific task"""
        likelihood = 0.1  # Default background likelihood
        
        if task.task_type == TaskType.DELIVER_ITEM:
            target_item_id = task.parameters.get('item_id')
            
            if action_type == ActionType.MOVE_TO:
                if target == target_item_id:
                    likelihood = 2.0  # Moving to the specific item
                elif target == 'kitting_table' and self.perceived_human_states[human_id]['carrying'] == target_item_id:
                    likelihood = 2.5  # Moving to table with the right item
                elif target.startswith('item_'):
                    likelihood = 0.2  # Moving to any item
                elif target == 'kitting_table':
                    likelihood = 0.3  # Moving to table
                    
            elif action_type == ActionType.PICK_UP:
                if target == target_item_id:
                    likelihood = 3.0  # Picking up the right item
                elif target.startswith('item_'):
                    likelihood = 0.2  # Picking up any item
                    
            elif action_type == ActionType.PLACE:
                if target == 'kitting_table' and self.previous_human_states[human_id]['carrying'] == target_item_id:
                    likelihood = 4.0  # Placing the right item on table
                elif target == 'kitting_table':
                    likelihood = 0.3  # Placing any item on table
        
        # Add additional task types here
        return likelihood                            
    
    
    
    
    # Add this helper method
    def _get_most_likely_action(self, human_id):
        """Get the most likely action for a human based on current probabilities"""
        if human_id not in self.action_probabilities or not self.action_probabilities[human_id]:
            return None
        
        return max(self.action_probabilities[human_id].items(), key=lambda x: x[1])
        
    # In _initialize_task_probabilities:
    def _initialize_task_probabilities(self, human_id):
        """Initialize task probabilities with uniform distribution"""
        task_probs = {}
        task_count = len(self.all_possible_tasks)
        uniform_prob = 1.0 / task_count if task_count > 0 else 0
        
        for task in self.all_possible_tasks:
            task_id = task.parameters.get('task_id', str(id(task)))  # Fallback to object ID
            task_probs[task_id] = uniform_prob
        
        self.task_probabilities[human_id] = task_probs
        return task_probs
    
    
    # Update _log_beliefs to display action probabilities
    def _log_beliefs(self):
        """Log the current beliefs about human intentions"""
        for human_id in self.perceived_human_states:
            print(f"\n--- Robot's beliefs about {human_id} ---")
            
            # Print action probabilities and task probabilities
            if human_id in self.action_probabilities and self.action_probabilities[human_id]:
                print("Action probabilities:")
                # Sort by probability
                sorted_actions = sorted(
                    self.action_probabilities[human_id].items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )
                for (action_type, target), prob in sorted_actions[:3]:  # Show top 3
                    print(f"  {action_type.name}({target}): {prob:.2f}")
            
            # Print task probabilities by type
            if human_id in self.task_probabilities:
                # Group by task type for readability
                by_type = defaultdict(list)
                for task_id, prob in self.task_probabilities[human_id].items():
                    task = self.model.task_library.get_task_by_id(task_id)
                    if task:
                        by_type[task.task_type].append((task_id, prob, task.parameters.get('item_id')))
                
                print("Task probabilities by type:")
                for task_type, tasks in by_type.items():
                    print(f"  {task_type.name}:")
                    # Sort by probability
                    for task_id, prob, item_id in sorted(tasks, key=lambda x: x[1], reverse=True):
                        if item_id:
                            print(f"    {task_id} ({item_id}): {prob:.2f}")
                        else:
                            print(f"    {task_id}: {prob:.2f}")
            
            print("-----------------------------------")
    
    
    
    def get_most_likely_task(self, human_id) -> Tuple[Optional[TaskType], float]:
        """Get the most likely task for a human and its probability"""
        if human_id not in self.task_probabilities or not self.task_probabilities[human_id]:
            return None, 0.0
            
        task_probs = self.task_probabilities[human_id]
        most_likely = max(task_probs.items(), key=lambda x: x[1])
        return most_likely


    def get_all_task_probabilities(self, human_id):
        """Return all task probabilities for visualization"""
        
        # return probs bigger than 0.05 only
        if human_id not in self.task_probabilities:
            return {}
        task_probs = self.task_probabilities[human_id]
        task_probs = {task_id: prob for task_id, prob in task_probs.items() if prob > 0.02}
        # Sort by probability
        sorted_tasks = sorted(task_probs.items(), key=lambda x: x[1], reverse=True)
        # Convert to dictionary
        sorted_task_probs = {task_id: prob for task_id, prob in sorted_tasks}
        return sorted_task_probs
        
        # if human_id in self.task_probabilities:
        #     return self.task_probabilities[human_id]
        # return {}