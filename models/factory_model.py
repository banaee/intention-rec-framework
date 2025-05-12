import time
import cProfile
import logging

import my_mesa 
# from my_mesa.space import MultiGrid
from my_mesa.time import RandomActivation
from my_mesa.datacollection import DataCollector
from my_mesa.my_grid import Grid
from my_mesa import Model


import random
from typing import List, Union, Optional

import config.factory_param_config as fc_config
# from models.base_model import BaseModel 
from actors.factory_operators import Robot, Human
from objects.factory_objects import Item, Shelf, KittingTable, Door
from intentions.state_representation import State, Predicate, Fluent
from intentions.factory_intentions import  TaskIntention, TaskOrigin, ActionIntention
# from intentions.intention_planner import IntentionPlanner
# from intentions.execution_planner import ExecutionPlanner
from intentions.state_representation import State, Predicate
from intentions.task_assignment import assign_tasks_to_operators 

from intentions.task_library import TaskLibrary

from state.world_state_manager import WorldStateManager
# logging.basicConfig(level=logging.DEBUG)



class FactoryModel(Model):   
    # not  BaseModel for now
    def __init__(self, 
                 width,
                 height, 
                 doors_p,
                 kitting_table_p,
                 shelves_p,
                 items_p,
                 robots_p,
                 humans_p,
                 mytext_p,
                 ):
        super().__init__()
        
        
        self.width = width
        self.height = height

        self.current_id = 0
        self.mytext = mytext_p

        self.grid = Grid(width, height)  # Use our custom Grid
        # TODO: check which scheduler to use 
        # self.schedule = my_mesa.time.RandomActivation(self)
        self.schedule = my_mesa.time.SimultaneousActivation(self)
        self.schedule = my_mesa.time.BaseScheduler(self)      


        # Initialize environment components
        self.init_doors(doors_p)
        self.init_kitting_table(kitting_table_p)
        self.init_shelves(shelves_p)
        self.init_items(items_p)


        # Initialize task library
        self.task_library = TaskLibrary(self)

        
        # Initialize agents
        # TODO: ensure human is initialized before robot
        self.init_humans(humans_p)
        self.init_robots(robots_p)

        
        # --------------------------------------------------------------
        # Initialize state manager after all other components, state manager is a property of the model
        # --------------------------------------------------------------
        self.state_manager = WorldStateManager(self)
        self.state_manager.update()
        self.state_manager.print_state()


        # Now initialize action sequences
        self.task_library.initialize_action_sequences()
                

        # --------------------------------------------------------------
        # Assign tasks to operators after all initializations
        # --------------------------------------------------------------
        assign_tasks_to_operators(self)
        # print_assigned_taskIntentions(self)


        # --------------------------------------------------------------
        # set up collector for visualization
        # --------------------------------------------------------------
        # logging.debug("Setting up datacollector")
        self.datacollector = DataCollector(
            model_reporters={"Step": lambda m: m.schedule.steps},
            agent_reporters={"Position": lambda a: a.pos}
        )



 
    # =========================================================================
    # step is defined in BaseModel if using BaseModel


    def step(self):
        """Single step of simulation"""
        print("="*50+f"starting step {self.schedule.steps}")


        # Update state before step
        self.state_manager.update()
        
        # Execute step - operators will handle their own planning/execution
        self.schedule.step()
        
        # Update state after step
        self.state_manager.update()
        
        # Collect data
        self.datacollector.collect(self)
        # logging.debug(f"finished step {self.schedule.steps}"+"-"*50)


    # Overriding the run_model method from BaseModel
    # def run_model(self):
    #     """Run the model until the end condition is reached."""
    #     while self.running:
    #         start_time = time.time()
    #         for _ in range(5):  # Executes 5 steps in one loop iteration
    #             self.step()
    #         end_time = time.time()  
    #         print(f"Time taken for 5 steps: {end_time - start_time}")
    #         if self.schedule.steps > 100:
    #             self.running = False



    # =============================================================================
    # Initialization methods
    # =============================================================================
        
    def init_doors(self, doors_p):    
        # initialize shelves
        # logging.debug("Initializing shelves")
        self.doors = {}
        for door_data in doors_p:
            door = Door(unique_id=door_data["id"], 
                          model=self, 
                          name=door_data["name"],
                          function=door_data["function"],
                          size=door_data["size"],
                          pos=door_data["pos"], 
                          side=door_data["side"])
            self.doors[door_data["id"]] = door
            self.grid.place_agent(door, door.pos)
            self.schedule.add(door)

        
    def init_kitting_table(self, kitting_table_p):
        # initialize kittin table
        # logging.debug("Initializing kitting table")
        self.kitting_table = KittingTable(unique_id="kitting_table", 
                                          model=self,
                                          size=kitting_table_p["size"],
                                          pos=kitting_table_p["pos"],
                                            side=kitting_table_p["side"])
        
        self.grid.place_agent(self.kitting_table, self.kitting_table.pos)
        self.schedule.add(self.kitting_table)

        
    def init_shelves(self, shelves_p):
        # initialize shelves
        # logging.debug("Initializing shelves")
        self.shelves = {}
        for shelf_data in shelves_p:
            shelf = Shelf(unique_id=shelf_data["id"], 
                          model=self, 
                          size=shelf_data["size"],
                          pos=shelf_data["pos"], 
                          side=shelf_data["side"])
            self.shelves[shelf_data["id"]] = shelf
            self.grid.place_agent(shelf, shelf.pos)
            self.schedule.add(shelf)
    
    
    def init_items(self, items_p):        
        # initialize items
        # logging.debug("Initializing items")
        self.items = {}
        for item_data in items_p:
            item = Item(unique_id=item_data["unique_id"], 
                        model=self,
                        size=item_data["size"],
                        init_pos=item_data["init_pos"],
                        pos=item_data["pos"],
                        init_shelf_id=item_data["init_shelf_id"],
                        holder = self.shelves[item_data["init_shelf_id"]],
                        )
            self.items[item_data["unique_id"]] = item
            self.grid.place_agent(item, item.pos)

            self.schedule.add(item)
             
            # UPDATE shelves: add items to shelves
            self.shelves[item_data["init_shelf_id"]].add_item(item)

    def init_humans(self, humans_p):
        # Initialize humans
        self.humans = {}
        # logging.debug("Initializing humans")
        for human_data in humans_p:
            human = Human(unique_id=human_data["id"], 
                          model=self, 
                          size=human_data["size"],
                          init_pos=human_data["init_pos"],
                          pos=human_data["pos"],
                          side=human_data["side"],
                          )
            
            # self.assign_tasks_to_operator(human, 
            # self.print_assigned_tasks_to_operator()
            
            self.humans[human_data["id"]] = human
            self.grid.place_agent(human, human.pos)            
            self.schedule.add(human)


        logging.debug("FactoryModel initialization complete")
    
            
    def init_robots(self, robots_p):            
        # Initialize robots
        # logging.debug("Initializing robots")
        self.robots = {}
        
        for robot_data in robots_p:
            robot = Robot(unique_id=robot_data["id"], 
                          model=self, 
                          size=robot_data["size"],
                          init_pos=robot_data["init_pos"],
                          pos=robot_data["pos"],
                          side=robot_data["side"], 
            )
            # self.assign_tasks_to_operator(robot, robot_data['task_intentions'])
            
            self.robots[robot_data["id"]] = robot
            self.grid.place_agent(robot, robot.pos)
            self.schedule.add(robot)


    # =============================================================================
    # Auxiliary methods
    # =============================================================================

    # --------------------------------------------------------------
    # Auxiliary methods on World state management
    # --------------------------------------------------------------


    def get_world_state(self) -> State:
        """Get current world state"""
        return self.state_manager.get_state()
    

    # --------------------------------------------------------------
    # Auxiliary methods on Agent management
    # --------------------------------------------------------------

    # def get_environment_state(self):
    #     return {
    #         'items': {item.unique_id: item.pos for item in self.items.values()},
    #         'kitting_table': self.kitting_table.pos,
    #         'shelves': {shelf.unique_id: shelf.pos for shelf in self.shelves.values()},
    #         'robots': {robot.unique_id: robot.pos for robot in self.robots.values()},
    #         'humans': {human.unique_id: human.pos for human in self.humans.values()}
    #     }

    # def update_agent_position(self, agent, new_pos):
    #     self.grid.move_agent(agent, new_pos)

    # def get_items_on_kitting_table(self):
    #     return self.kitting_table.current_items

    # def is_action_complete(self):
    #     required_items = set([item for robot in self.robots.values() for item in robot.action_planner.task_actions] +
    #                          [item for human in self.humans.values() for item in human.action_planner.task_actions])
    #     items_on_table = set([item.unique_id for item in self.get_items_on_kitting_table()])
    #     return required_items.issubset(items_on_table)
    
    
    
