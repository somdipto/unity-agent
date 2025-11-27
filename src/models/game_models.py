from pydantic import BaseModel, validator
from typing import Tuple, Optional
from enum import Enum

class ActionType(str, Enum):
    MOVE = "move"
    JUMP = "jump"
    ATTACK = "attack"
    INTERACT = "interact"

class GameState(BaseModel):
    player_position: Tuple[float, float, float]
    health: float
    timestamp: float
    level_name: Optional[str] = None
    
    @validator('health')
    def health_bounds(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Health must be between 0 and 100')
        return v

class Action(BaseModel):
    type: ActionType
    direction: Optional[Tuple[float, float, float]] = None
    target_position: Optional[Tuple[float, float, float]] = None
    agent_id: str
    
    @validator('direction')
    def normalize_direction(cls, v):
        if v is None:
            return v
        # Normalize direction vector
        magnitude = sum(x**2 for x in v) ** 0.5
        return tuple(x / magnitude if magnitude > 0 else 0 for x in v)
