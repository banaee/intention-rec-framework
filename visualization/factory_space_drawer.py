import solara
# from matplotlib.figure import Figure
# from my_mesa.visualization import SolaraViz

# from agents.factory_agent import Operator, Robot, Human, Item, KittingTable, Shelf
from agents.factory_agents.factory_operators import Human, Robot, Operator
from agents.factory_agents.factory_objects import Item, Shelf, KittingTable

import pandas as pd
import plotly.express as px


def factory_space_drawer(model, agent_portrayal):
    # Collect data for plotting
    
    # initialize a plotly express figure with empty figure
    fig = px.scatter()
    
    # -----------------------------------------------------
    # add static elements (shelves, kitting table) to the figure
    fig = _factory_static_elements(model)
    
    # -----------------------------------------------------
    # update the figure settings
    fig = _factory_update_figure_settings(model, fig)

    # -----------------------------------------------------
    # add dynamic elements (items, operators, robots, humans) to the figure
    fig = _factory_dynamic_elements(model, fig)


    # Render and return the figure
    solara.FigurePlotly(fig)
    return fig


def _factory_update_figure_settings(model, fig):
    fig.update_layout(
        width=model.width,
        height=model.height,
    )
    # remove background color 
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    # remove axes
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True)
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black', mirror=True)
    # remove x,y labels
    fig.update_xaxes(title_text='')
    fig.update_yaxes(title_text='')
    # remove legend
    fig.update_layout(showlegend=False)
    # remove margins
    # fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    # add  x , y tick, but remove grid
    fig.update_xaxes(showticklabels=True, showgrid=False)
    fig.update_yaxes(showticklabels=True, showgrid=False)
    
    
    return fig
    
    
def _factory_static_elements(model):
    fig = px.scatter()
    
    
    
    # draw a vertical dashed line in the middle of the factory
    fig.add_shape(
        type="line",
        x0=model.width/2,
        y0=30,
        x1=model.width/2,
        y1=model.height,
        line=dict(color="gray", width=2, dash="dash"),
        opacity=0.4,
    )
    
    # draw a horizontal dashed line in the middle of the factory
    fig.add_shape(
        type="line",
        x0=0,
        y0=model.height/2,
        x1=model.width,
        y1=model.height/2,
        line=dict(color="gray", width=1, dash="dash"), 
        opacity=0.1,
    )

    
    # draw kitting table as shape
    kt = model.kitting_table
    fig.add_shape(
        type="rect",
        x0=kt.pos[0]-1,
        y0=kt.pos[1]-1,
        x1=kt.pos[0]+kt.size[0],
        y1=kt.pos[1]+kt.size[1],
        line=dict(color="gray", width=2), 
        fillcolor="gray", 
        opacity=0.5,
    )


    # draw doors as shapes
    for _, door in model.doors.items():
        
        fig.add_shape(
            type="rect",
            x0= door.pos[0]-1,
            y0= door.pos[1]-1,
            x1= door.pos[0]+ door.size[0],
            y1= door.pos[1]+ door.size[1],
            line=dict(color="white", width=1), 
            fillcolor="red" if door.function == "exit" else "green",
            opacity=0.5,
        )
        
        # add the door id as annotation
        fig.add_annotation(
            x=door.pos[0]+ door.size[0]/2,
            y=door.pos[1]+ door.size[1]/2,
            text=door.name,
            # text color
            # bgcolor="red" if door.function == "exit" else "green",
            font=dict(color="white", size=12),
            showarrow=False,
        )
        
        
    # draw shelves as shapes
    for agent in model.schedule.agents:
        if isinstance(agent, Shelf):
            shelf = agent
            fig.add_shape(
                    type="rect",
                    x0= shelf.pos[0]-1,
                    y0= shelf.pos[1]-1,
                    x1= shelf.pos[0]+ shelf.size[0], 
                    y1= shelf.pos[1]+ shelf.size[1],
                    line=dict(color="orange", width=5), 
                    fillcolor="orange",
                    opacity=0.4,
                )
            # annotate the shelf with its id on top center
                        
            
            fig.add_annotation(
                x=shelf.pos[0]+ shelf.size[0]/2,
                y=shelf.pos[1]+ shelf.size[1],
                text=shelf.unique_id,
                font=dict(color="black", size=12),
                showarrow=False,
            )
    
    # fig.add_vrect(x0=300, x1=500, 
    #           annotation_text="decline", annotation_position="top left",
    #           fillcolor="green", opacity=0.25, line_width=0)

    return fig
    
    
def _factory_dynamic_elements(model, fig):
    
    # add robot and human agents as scatter plot
    for agent in model.schedule.agents:
        if isinstance(agent, Robot):
            # fig.add_shape(
            #     type="circle",
            #     x0=agent.pos[0]-1,
            #     y0=agent.pos[1]-1,
            #     x1=agent.pos[0]+ agent.size[0],
            #     y1=agent.pos[1]+ agent.size[1],
            #     line=dict(color="blue", width=1), 
            # )
            # Using Emoji of a robot face:
            fig.add_annotation(
                x=agent.pos[0]+ agent.size[0]/2,
                y=agent.pos[1]+ agent.size[1]/2,
                text="🤖",
                font=dict(color="blue", size= agent.size[0]*1.1),
                showarrow=False,
            )
            
        elif isinstance(agent, Human):
            # fig.add_shape(
            #     type="circle",
            #     x0=agent.pos[0]-1,
            #     y0=agent.pos[1]-1,
            #     x1=agent.pos[0]+ agent.size[0],
            #     y1=agent.pos[1]+ agent.size[1],
            #     line=dict(color="green", width=1), 
            # )
            # Using Emoji of a worke face: 
            fig.add_annotation(
                x=agent.pos[0]+ agent.size[0]/2,
                y=agent.pos[1]+ agent.size[1]/2,
                text="👷🏼‍♀️",
                font=dict(color="green", size= agent.size[0]*2),
                showarrow=False,
            )
    
    # add item agents as scatter plot
    for agent in model.schedule.agents:
        if isinstance(agent, Item):
            
            holder_ag = agent.holder
            
            
            fig.add_shape(
                type="circle",
                x0=agent.pos[0]-1,
                y0=agent.pos[1]-1,
                x1=agent.pos[0]+ agent.size[0],
                y1=agent.pos[1]+ agent.size[1],
                line=dict(
                    color="red" if isinstance(holder_ag, Operator) else "black", 
                    width=1), 
            )
            # annotate the item with its id
            fig.add_annotation(
                x=agent.pos[0]+ agent.size[0]/2,
                y=agent.pos[1]+ agent.size[1]/2,
                text=agent.unique_id,
                font=dict(color="red" if isinstance(holder_ag, Operator) else "black", 
                          size=12),
                showarrow=False,
            )

    # Add planned paths for operators
    for agent in model.schedule.agents:
        if isinstance(agent, Operator) and hasattr(agent, 'planned_path') and agent.planned_path:
            # Extract x and y coordinates from path
            x_coords = [pos[0] for pos in agent.planned_path]
            y_coords = [pos[1] for pos in agent.planned_path]
            
            # Choose color based on agent type
            path_color = 'blue' if isinstance(agent, Robot) else 'green'
            
            # Create a scatter plot with markers for the path points
            path_fig = px.scatter(x=x_coords, y=y_coords)
            
            # Update the marker properties
            path_fig.update_traces(
                mode='markers',
                marker=dict(
                    color=path_color,
                    size=5,
                    symbol='circle',
                    opacity=0.4
                ),
                showlegend=False
            )
            
            # Add the path traces to the main figure
            for trace in path_fig.data:
                fig.add_trace(trace)
                
                

    return fig
    
    

