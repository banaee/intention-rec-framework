# world_state_manager.py
from typing import List, Dict, Any, Tuple
from intentions.state_representation import State, Predicate, Fluent
from actors.factory_operators import Operator
from objects.factory_objects import Item, Shelf, KittingTable
import logging


class WorldStateManager:
    def __init__(self, model):
        self.model = model
        self.state = None
        self.REACH_DISTANCE = 60 # Radius of neighborhood for near predicate  (path calculator uses pixels_per_step = 50, so, in last step, agent will be in the neighborhood of the target)

        # Initialize world state with initial model state
        self.static_predicates = self._get_static_predicates()


    def _get_static_predicates(self) -> List[Predicate]:
        """Get static predicates that are true in the initial state"""
        static_predicates = []
        
        # Kitting Table
        kt_pos_str = f"{self.model.kitting_table.pos[0]},{self.model.kitting_table.pos[1]}"
        static_predicates.append(Predicate("at", ["kitting_table", kt_pos_str]))
        
        # Shelves
        for shelf_id, shelf in self.model.shelves.items():
            shelf_pos_str = f"{shelf.pos[0]},{shelf.pos[1]}"
            static_predicates.append(Predicate("at", [shelf_id, shelf_pos_str]))
        
        # Doors
        for door_id, door in self.model.doors.items():
            door_pos_str = f"{door.pos[0]},{door.pos[1]}"
            static_predicates.append(Predicate("at", [door_id, door_pos_str]))
            
        return static_predicates



    def _check_reach(self, pos1: tuple, pos2: tuple) -> bool:
        """Check if two positions are exactly the same"""  
        return pos1 == pos2
        # TODO: later a more sophisticated check can be implemented using reach distance
        # """Check if two positions are within reach distance"""
        # dx = abs(pos1[0] - pos2[0])
        # dy = abs(pos1[1] - pos2[1])
        # return (dx * dx + dy * dy) ** 0.5 <= self.REACH_DISTANCE




    def update(self):
        """Update the complete world state based on current model state"""

        new_predicates = self.static_predicates.copy()  # Start with static predicates  TODO: it is based on the fact that static predicates are not changed during the simulation
        new_fluents = []

        
        # =========================================================
        # Update predicates for agents
        # =========================================================
        all_agents = list(self.model.humans.values()) + list(self.model.robots.values())       
        
        for agent in all_agents:
            # --------------------------------------------------------- 
            # Update "at(agent, pos)"  
            # ---------------------------------------------------------
            agent_pos_str = f"{agent.pos[0]},{agent.pos[1]}"
            pos_pred = Predicate("at", [agent.unique_id, agent_pos_str])
            '''            
            print(f"update agent position pred to world state: {pos_pred}") 
            '''            
            new_predicates.append(pos_pred)

            # ---------------------------------------------------------
            # Check reach predicates with items and static objects
            # ---------------------------------------------------------
            for item in self.model.items.values():
                if self._check_reach(agent.pos, item.pos):
                    new_predicates.append(Predicate("reach", [agent.unique_id, item.unique_id]))
   
            # Check reach with kitting table
            if self._check_reach(agent.pos, self.model.kitting_table.pos):
                new_predicates.append(Predicate("reach", [agent.unique_id, "kitting_table"]))

            # ---------------------------------------------------------
            # Handle carrying case - using item.holder relationship
            # ---------------------------------------------------------            
            if agent.carrying:
                # Add holding predicate
                new_predicates.append(
                    Predicate("holding", [agent.unique_id, agent.carrying.unique_id])
                )
                # Add carried item's position (same as agent)
                new_predicates.append(
                    Predicate("at", [agent.carrying.unique_id, agent_pos_str])
                )
        
            
        # =========================================================
        # ITEMS: Update predicates for items based on their holders
        # =========================================================
        for item in self.model.items.values():
            # Always add item's current position
            new_predicates.append(
                Predicate("at", [item.unique_id, f"{item.pos[0]},{item.pos[1]}"])
            )
            
            # Add relationship with holder if any
            if item.holder:
                if isinstance(item.holder, Shelf):
                    new_predicates.append(
                        Predicate("on", [item.unique_id, item.holder.unique_id])
                    )
                elif isinstance(item.holder, KittingTable):
                    new_predicates.append(
                        Predicate("on", [item.unique_id, "kitting_table"])
                    )
                # Note: if holder is an agent, we already handled it above



        # =========================================================
        # Create new state
        # =========================================================
        self.state = State(new_predicates, new_fluents)


        # =========================================================
        # Debugging
        # =========================================================
        # print("World state updated with predicates:")
        # # for pred in new_predicates:
        # #     print(f"  {pred}")
        # print("... (commented) \n")




    def get_state(self) -> State:
        """Get current world state, updating if necessary"""
        if self.state is None:
            self.update()
        return self.state
    
    def print_state(self):
        # print("\nCurrent World State:")
        # for predicate in self.state.predicates:
        #     print(f"  - {predicate}")
        # if self.state.fluents:
        #     print("\nFluents:")
        #     for fluent in self.state.fluents:
        #         print(f"  - {fluent}")
        print("\n")