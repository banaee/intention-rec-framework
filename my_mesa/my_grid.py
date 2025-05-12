class Grid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = {}  # Dictionary to store agents at each position

    def place_agent(self, agent, pos: tuple):
        if self.is_cell_empty(pos):
            self.grid[pos] = agent
            agent.pos = pos
            return True
        return False



    '''
    
    Instead of ignoring the deletion outright, it’s better to address the root of the issue and ensure that:

    Multiple agents cannot occupy the same position simultaneously.
    Each agent's movement is handled independently and safely, avoiding concurrent modifications of the grid.
    '''

    def move_agent(self, agent, new_pos: tuple):
        
        if True:   #TODO: Originally it was if self.is_cell_empty(new_pos):
            old_pos = agent.pos
            # check if old_pos is in grid before deleting
            if old_pos in self.grid:    #If two agents are on the same position and move simultaneously, both will attempt to delete the same old_pos from the grid.
                del self.grid[old_pos]
            
            self.grid[new_pos] = agent
            agent.pos = new_pos
            return True
        return False








    def remove_agent(self, agent):
        if agent.pos in self.grid:
            del self.grid[agent.pos]
            agent.pos = None
            return True
        return False

    def get_distance(self, pos1: tuple, pos2: tuple) -> int:
        x1, y1 = pos1
        x2, y2 = pos2
        return abs(x1 - x2) + abs(y1 - y2)
    
    def is_cell_empty(self, pos: tuple) -> bool:
        return pos not in self.grid

    def get_cell_list_contents(self, cell_list):
        return [self.grid[pos] for pos in cell_list if pos in self.grid]

    # def get_neighbors(self, pos, moore=False, include_center=False, radius=1):
    #     x, y = pos
    #     coordinates = set()
    #     for dx in range(-radius, radius + 1):
    #         for dy in range(-radius, radius + 1):
    #             if not moore and abs(dx) + abs(dy) > radius:
    #                 continue
    #             if not include_center and dx == 0 and dy == 0:
    #                 continue
    #             new_x, new_y = x + dx, y + dy
    #             if 0 <= new_x < self.width and 0 <= new_y < self.height:
    #                 coordinates.add((new_x, new_y))
    #     return self.get_cell_list_contents(coordinates)
