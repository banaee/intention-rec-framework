# intentions/task_library.py
from typing import Dict, List, Set
from collections import defaultdict
from intentions.factory_intentions import TaskIntention, TaskType, TaskOrigin, ActionType
from intentions.state_representation import State, Predicate

class TaskLibrary:
    """
    Central repository of all possible tasks in the simulation.
    Organizes tasks by origin (assigned, foreseeable, unknown) and provides
    access methods for task assignment and intention recognition.
    """
    
    def __init__(self, model):
        self.model = model
        # Main structure: {origin: {task_id: task_intention}}
        self.tasks = {
            TaskOrigin.ASSIGNED: {},
            TaskOrigin.FORESEEABLE: {},
            TaskOrigin.UNKNOWN: {}
        }
        
        # Additional indices for quick access
        self.tasks_by_type = defaultdict(list)  # {task_type: [task_intentions]}
        self.tasks_by_item = defaultdict(list)  # {item_id: [task_intentions]}
        self.task_action_sequences = {}   # store {task_id: [(action_type, parameters), ...]}

        
        # Initialize with all possible tasks
        self._initialize_all_tasks()

        # Initialize action sequences of tasks
        # self._initialize_action_sequences()


    # -------------------------------------------------------------
    # methods
    # -------------------------------------------------------------
    def initialize_action_sequences(self, planner=None):
        """Initialize the expected action sequence for each task using the planner"""
        if not hasattr(self.model, 'state_manager'):
            print("State manager not available yet")
            return False
            
        world_state = self.model.state_manager.get_state()
        
        # Use provided planner or find one from robots
        self.planner = planner
        if not self.planner and hasattr(self.model, 'robots'):
            # Use first robot's planner if available
            for robot in self.model.robots.values():
                if hasattr(robot, 'planner'):
                    self.planner = robot.planner
                    break
        
        if not self.planner:
            print("No planner available for task action sequences")
            return False
        
        # For each task in the system, use planner to determine action sequence
        for origin in self.tasks:
            for task_id, task in self.tasks[origin].items():
                # Use the planner to decompose the task into actions
                action_sequence = self.planner.plan_for_task(task, world_state)
                
                # Store the action sequence with its parameters
                self.task_action_sequences[task_id] = [
                    (action.action_type, action.parameters)
                    for action in action_sequence
                ]
                
        print(f"Initialized action sequences for {len(self.task_action_sequences)} tasks")
        return True
                
    
                
    def _initialize_all_tasks(self):
        """Initialize all possible tasks in the simulation"""
        # Generate all assigned tasks (e.g., deliveries)
        self._generate_assigned_tasks()
        
        # Generate all foreseeable tasks (e.g., coffee breaks)
        self._generate_foreseeable_tasks()
        
        # Generate all unknown tasks (potential future tasks)
        self._generate_unknown_tasks()
    
    
    
    
    def _generate_assigned_tasks(self):
        """Generate all assigned tasks based on items in the model"""
        # For each item, create a delivery task
        for item_id, item in self.model.items.items():
            # Create unique task ID
            task_id = f"deliver_{item_id}"
            
            # Create desired state for delivery task
            desired_state = State([Predicate("on", [item_id, "kitting_table"])])
            
            # Create task intention
            task = TaskIntention(
                task_type=TaskType.DELIVER_ITEM,
                origin=TaskOrigin.ASSIGNED,
                desired_state=desired_state,
                parameters={
                    "task_id": task_id,
                    "item_id": item_id
                }
            )
            
            # Add to main registry and indices
            self.tasks[TaskOrigin.ASSIGNED][task_id] = task
            self.tasks_by_type[TaskType.DELIVER_ITEM].append(task)
            self.tasks_by_item[item_id].append(task)
    
    def _generate_foreseeable_tasks(self):
        """Generate all foreseeable tasks like coffee breaks, bathroom visits, etc."""
         # Check if humans exist before trying to iterate them
        if not hasattr(self.model, 'humans') or not self.model.humans:
            return  # Skip if humans aren't initialized yet
        
         # Example: Coffee break task for each human
        for human_id, human in self.model.humans.items():
            task_id = f"coffee_break_{human_id}"
            
            # Only if TAKE_COFFEE is defined in your TaskType
            if hasattr(TaskType, 'TAKE_COFFEE'):
                # Create desired state
                desired_state = State([Predicate("has_coffee", [human_id])])
                
                # Create task intention
                task = TaskIntention(
                    task_type=TaskType.TAKE_COFFEE,
                    origin=TaskOrigin.FORESEEABLE,
                    desired_state=desired_state,
                    parameters={
                        "task_id": task_id,
                        "agent_id": human_id
                    }
                )
                
                # Add to registry
                self.tasks[TaskOrigin.FORESEEABLE][task_id] = task
                self.tasks_by_type[TaskType.TAKE_COFFEE].append(task)
    
    def _generate_unknown_tasks(self):
        """Generate placeholder for potential unknown tasks"""
        # You might not need to pre-generate these, as they're unpredictable
        # Could be added dynamically during simulation
        pass
    
    def get_all_tasks(self):
        """Get all tasks in the system, flattened"""
        all_tasks = []
        for origin_tasks in self.tasks.values():
            all_tasks.extend(origin_tasks.values())
        return all_tasks
    
    def get_tasks_by_origin(self, origin):
        """Get all tasks of a specific origin"""
        return list(self.tasks[origin].values())
    
    def get_tasks_by_type(self, task_type):
        """Get all tasks of a specific type"""
        return self.tasks_by_type[task_type]
    
    def get_tasks_for_item(self, item_id):
        """Get all tasks related to a specific item"""
        return self.tasks_by_item[item_id]
    
    def get_task_by_id(self, task_id):
        """Get a specific task by its ID"""
        for origin_tasks in self.tasks.values():
            if task_id in origin_tasks:
                return origin_tasks[task_id]
        return None
    
    def get_action_sequence(self, task_id):
        """Get the expected action sequence for a specific task"""
        return self.task_action_sequences.get(task_id, [])

    def get_all_possible_actions(self):
        """Get all possible actions from all tasks, without duplicates"""
        all_actions = set()
        for sequence in self.task_action_sequences.values():
            for action in sequence:
                # Convert action parameters dict to tuple for hashability
                params_tuple = tuple((k, v) for k, v in action[1].items())
                all_actions.add((action[0], params_tuple))
        return all_actions