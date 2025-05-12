# main.py

# import sys
# import os
# Add the mesa directory to the Python path
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'my_mesa')))


from my_mesa.visualization import SolaraViz
# from my_mesa.visualization import JupyterViz

from models.factory_model import FactoryModel
from factory_portrayal import factory_agent_portrayal
import param_config.factory_param_config as fc_config

# test
from drawings.factory_drawers_nov17 import factory_space_drawer
# from drawings.factory_drawers_cg1 import factory_space_drawer
# from drawings.factory_drawers_cg2 import factory_space_drawer

# import mesa.space 

simulation_type = "factory"  # Change to "traffic" to run the traffic simulation

if simulation_type == "factory":
    model = FactoryModel
    agent_portrayal = factory_agent_portrayal
    model_params = fc_config.get_factory_model_params()    
    space_drawer = factory_space_drawer
    name = "Factory Model"
    
# elif simulation_type == "traffic":
#     page = None
    
else:
    print("Unsupported simulation type. Please choose 'factory' or 'traffic'.")

# print("-"*50)
# for key, value in model_params.items():
#     if key == "robots_p" or key == "humans_p":
#         print(f"{key}: {value}")
#     # if key == "items_p":
#     #         for door in value:
#     #             print(f"{key}: {door}")
#     # print(f"{key}: {value}")
# print("-"*50)


page = SolaraViz(
    model_class=model,
    model_params=model_params,
    space_drawer=space_drawer,
    name=name,
    agent_portrayal=agent_portrayal,
    play_interval=0.001,
)

# This is required to render the visualization in the Jupyter notebook
# page

