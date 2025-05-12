# main.py

import sys
import os
# Add the mesa directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'my_mesa')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'models')))

from my_mesa.visualization import SolaraViz
# from my_mesa.visualization import JupyterViz

from models.factory_model import FactoryModel
import config.factory_param_config as fc_config

# from factory_portrayal import factory_agent_portrayal
# from drawings.factory_drawers import factory_space_drawer
# import mesa.space 

# simulation_type = "factory"  # Change to "traffic" to run the traffic simulation

# if simulation_type == "factory":
#     model = FactoryModel
#     agent_portrayal = factory_agent_portrayal
#     model_params = fc_config.get_factory_model_params()    
#     space_drawer = factory_space_drawer
#     name = "Factory Model"
    
# # elif simulation_type == "traffic":
# #     page = None
    
# else:
#     print("Unsupported simulation type. Please choose 'factory' or 'traffic'.")


# Retrieve the model parameters
model_params = fc_config.get_factory_model_params()
print(model_params.keys())
# Ensure model_params is a dictionary with the required keys
fac_model = FactoryModel(**model_params)

for i in range(100):
   fac_model.step()

x = 1