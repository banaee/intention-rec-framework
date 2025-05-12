# task_assignment.py

import random
from intentions.factory_intentions import TaskIntention, TaskType, State, Predicate, TaskOrigin

def assign_tasks_to_operators(model):
    """Assign tasks to operators from the task library"""
    assign_tasks_to_operator_group(model, model.humans.values(), "right")
    assign_tasks_to_operator_group(model, model.robots.values(), "left")

def assign_tasks_to_operator_group(model, operators, side):
    """Assign tasks to a group of operators based on side"""
    # Get all tasks from the task library for this side
    side_tasks = []
    for task_id, task in model.task_library.tasks[TaskOrigin.ASSIGNED].items():
        item_id = task.parameters.get('item_id')
        if item_id and model.items[item_id].init_shelf_id and model.shelves[model.items[item_id].init_shelf_id].side == side:
            side_tasks.append(task)
    
    # Assign tasks to operators
    for operator in operators:
        # Select random subset of tasks (up to 3)
        if side_tasks:
            assigned_tasks = random.sample(side_tasks, min(3, len(side_tasks)))
            for task in assigned_tasks:
                # Create a copy of the task with the specific operator assigned
                operator_task = create_item_delivery_task(operator, model.items[task.parameters['item_id']])
                operator.assigned_taskIntentions.add(operator_task)
                print(f"Assigned {task.parameters['item_id']} to {operator.unique_id}")

def create_item_delivery_task(operator, item):
    """Create a delivery task for a specific operator and item"""
    task_id = f"deliver_{item.unique_id}_{operator.unique_id}"
    task_state = State([Predicate("on", [item.unique_id, "kitting_table"])])
    return TaskIntention(
        task_type=TaskType.DELIVER_ITEM,
        origin=TaskOrigin.ASSIGNED,
        desired_state=task_state,
        parameters={
            "task_id": task_id,
            "agent_id": operator.unique_id,
            "item_id": item.unique_id
        }
    )

def get_items_by_side(model, side):
    """Get items located on a specific side of the factory"""
    return [item for item in model.items.values() 
            if model.shelves[item.init_shelf_id].side == side]

def print_assigned_taskIntentions(model):
    """Print all tasks assigned to operators"""
    print("\n=== Assigned Task Intentions ===")
    for operator_type, operators in [("Humans", model.humans.values()), ("Robots", model.robots.values())]:
        print(f"\n{operator_type}:")
        for operator in operators:
            print(f"  {operator.unique_id}:")
            if operator.assigned_taskIntentions:
                for task in operator.assigned_taskIntentions:
                    print(f"    - {task}")
                    print(f"      Desired State: {task.desired_state}")
                    print(f"      Parameters: {task.parameters}")
            else:
                print("    No assigned tasks")
    print("\n===============================")