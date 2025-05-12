from enum import Enum

class EntityType(Enum):
    ITEM = "item"
    SHELF = "shelf"
    KITTING_TABLE = "kitting_table"
    FLOOR = "floor"
    AGENT = "agent"


class EntityIdentifier:
    def __init__(self, entity_type: EntityType, entity_id: str):
        self.entity_type = entity_type
        self.entity_id = entity_id

    def __str__(self):
        return f"{self.entity_type.value}_{self.entity_id}"

    @classmethod
    def from_string(cls, identifier: str) -> 'EntityIdentifier':
        entity_type, entity_id = identifier.split('_', 1)
        return cls(EntityType(entity_type), entity_id)
