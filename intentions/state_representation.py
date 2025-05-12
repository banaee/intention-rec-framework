from enum import Enum, auto
from typing import List, Union, Optional

# class Predicate:
#     def __init__(self, name: str, args: List[str]):
#         self.name = name
#         self.args = args


#     def __repr__(self):
#         # Convert all arguments to strings before joining
#         arg_strings = [str(arg) for arg in self.args]
#         return f"{self.name}({', '.join(arg_strings)})"



class Predicate:
    def __init__(self, name: str, args: List[str]):
        self.name = name
        self.args = args

    def __eq__(self, other):
        """Implement equality comparison"""
        if not isinstance(other, Predicate):
            return False
        return (self.name == other.name and 
                len(self.args) == len(other.args) and
                all(a1 == a2 for a1, a2 in zip(self.args, other.args)))

    def __hash__(self):
        """Implement hash for set operations"""
        return hash((self.name, tuple(self.args)))

    def __repr__(self):
        # Convert all arguments to strings before joining
        arg_strings = [str(arg) for arg in self.args]
        return f"{self.name}({', '.join(arg_strings)})"
    


    
class Fluent:
    def __init__(self, name: str, args: List[str], value: float):
        self.name = name
        self.args = args
        self.value = value

    def __repr__(self):
        # Convert all arguments to strings before joining
        arg_strings = [str(arg) for arg in self.args]
        return f"{self.name}({', '.join(arg_strings)}) = {self.value}"

class State:
    def __init__(self, predicates: List[Predicate], fluents: Optional[List[Fluent]] = None): 
        self.predicates = predicates
        self.fluents = fluents or []

    def __repr__(self):
        pred = ', '.join([str(p) for p in self.predicates])
        flus = ', '.join([str(f) for f in self.fluents])
        return f"State(predicates=[{pred}], fluents=[{flus}])"
