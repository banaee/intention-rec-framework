from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any

class microactionType(Enum):
    MOVE_STEP = "move-step"     # parameters: target_pos
    GRAB = "grab"               # parameters: item_id
    RELEASE = "release"         # parameters: target_holder


@dataclass
class microaction:
    """Atomic executable microaction"""
    microaction_type: microactionType
    parameters: Dict[str, Any]

    def __repr__(self):
        return f"microaction({self.microaction_type.name}, {self.parameters})"
