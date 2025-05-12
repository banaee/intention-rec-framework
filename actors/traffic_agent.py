from my_mesa import Agent


class AV(Agent):
    def __init__(self, unique_id, model, pos, route):
        super().__init__(unique_id, model, pos)
        self.route = route

    def step(self):
        pass

class HV(Agent):
    def __init__(self, unique_id, model, pos, route):
        super().__init__(unique_id, model, pos)
        self.route = route

    def step(self):
        pass
    
class TrafficLight(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        self.state = "red"

    def step(self):
        pass
    
class Pedestrian(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)

    def step(self):
        pass
    
class Crosswalk(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)

    def step(self):
        pass
    
    