from enum import Enum
import random
from typing import Dict, Any

class AgentPersonality(Enum):
    CAUTIOUS = "slow, careful exploration"
    AGGRESSIVE = "fast, risky actions"
    RANDOM = "unpredictable behavior"
    SPEEDRUNNER = "optimal path finding"

class PersonalityAgent:
    def __init__(self, agent_id: str, personality: AgentPersonality):
        self.id = agent_id
        self.personality = personality
        
    def decide_action(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Make decision based on personality"""
        base_action = {"agent_id": self.id, "type": "move"}
        
        if self.personality == AgentPersonality.CAUTIOUS:
            # Move slowly, check surroundings
            base_action["direction"] = (0.3, 0, 0)  # Slow movement
            
        elif self.personality == AgentPersonality.AGGRESSIVE:
            # Fast, direct movement
            base_action["direction"] = (1.0, 0, 0)  # Fast movement
            if random.random() < 0.3:  # 30% chance to attack
                base_action["type"] = "attack"
                
        elif self.personality == AgentPersonality.RANDOM:
            # Completely unpredictable
            actions = ["move", "jump", "attack", "interact"]
            base_action["type"] = random.choice(actions)
            base_action["direction"] = (
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                random.uniform(-1, 1)
            )
            
        elif self.personality == AgentPersonality.SPEEDRUNNER:
            # Always move toward objective
            base_action["direction"] = (1.0, 0, 0)  # Assume forward is optimal
            
        return base_action
