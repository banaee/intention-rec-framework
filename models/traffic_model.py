from my_mesa import Model
from my_mesa.space import MultiGrid
from my_mesa.time import RandomActivation
import random

from models.base_model import BaseModel 

# from agents.factory_agent import Item, Shelf, KittingTable, Robot, Human
# import config.factory_config as fc_config

class TrafficModel(BaseModel):
    def __init__(self, width, height):
        super().__init__(width, height) 

