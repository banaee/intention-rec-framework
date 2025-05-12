
from actors.factory_operators import Human, Robot
from objects.factory_objects import Item, Shelf, KittingTable



import logging
# logging.basicConfig(level=logging.DEBUG)

def factory_agent_portrayal(agent):
    if isinstance(agent, Item):
        portrayal = {
            "Shape": "circle",
            "Color": "red",
            "Filled": "true",
            "Layer": 0,
            "r": 1.9,
            "text": str(agent.unique_id),
            "text_color": "white",
            "text_size": 15,
            "Layer": 3
        }
    elif isinstance(agent, Shelf):
        portrayal = {
            "Shape": "rect",
            "Color": "yellow",
            "Filled": "true",
            "Layer": 0,
            "w": 8,
            "h": 8,
            "text": str.join(" - ", [""+str(item.unique_id) for item in agent.current_items]),
            "text_color": "black",
            "text_position": "bottom",
            "text_size": 35,
            "Layer": 2
        }
    elif isinstance(agent, KittingTable):
        portrayal = {
            "Shape": "rect",
            "Color": "gray",
            "Filled": "true",
            "Layer": 0,
            "w": 20,
            "h": 5,
            "text": str.join(", ", [str(item.unique_id) for item in agent.current_items]),
            "text_color": "black",
            "text_position": "top",
            "text_size": 35,
            "Layer": 1
        }
    elif isinstance(agent, Robot):
        portrayal = {
            "Shape": "images/robot.png",
            "scale": 3.5,
            "w": 1.9, "h": 1.9,
            "Filled": "true",
            "Color": "blue",
            "Layer": 3
        }
        if agent.carrying:
            portrayal["Shape"] = "images/robot_carrying.png"
            portrayal["text"] = str(agent.carrying.unique_id)
            portrayal["text_color"] = "red"
            portrayal["text_size"] = 15
            portrayal["text_position"] = "bottom"
            
            
    elif isinstance(agent, Human):
        portrayal = {
            "Shape": "images/human.png",
            "scale": 3.5,
            "w": 1.9, "h": 1.9,
            "Filled": "true",
            "Color": "green",
            "Layer": 3
        }
        if agent.carrying:
            portrayal["Shape"] = "images/human_carrying.png"
            portrayal["text"] = str(agent.carrying.unique_id)
            portrayal["text_color"] = "red"
            portrayal["text_size"] = 15
            portrayal["text_position"] = "bottom"
    return portrayal