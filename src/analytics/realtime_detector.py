import time
from typing import Dict, Tuple
from dataclasses import dataclass

@dataclass
class AgentState:
    position: Tuple[float, float, float]
    last_update: float
    stuck_duration: float = 0

class RealtimeDetector:
    def __init__(self, stuck_threshold: float = 30.0):
        self.stuck_threshold = stuck_threshold
        self.agent_states: Dict[str, AgentState] = {}
        self.anomalies = []
        
    def update_agent(self, agent_id: str, position: Tuple[float, float, float]):
        """Update agent position and detect if stuck"""
        current_time = time.time()
        
        if agent_id not in self.agent_states:
            self.agent_states[agent_id] = AgentState(position, current_time)
            return False
            
        prev_state = self.agent_states[agent_id]
        
        # Check if position changed significantly
        distance = sum((a - b) ** 2 for a, b in zip(position, prev_state.position)) ** 0.5
        
        if distance < 0.1:  # Barely moved
            prev_state.stuck_duration += current_time - prev_state.last_update
        else:
            prev_state.stuck_duration = 0
            
        prev_state.position = position
        prev_state.last_update = current_time
        
        # Detect soft-lock
        if prev_state.stuck_duration > self.stuck_threshold:
            self.anomalies.append({
                'type': 'soft_lock',
                'agent_id': agent_id,
                'position': position,
                'duration': prev_state.stuck_duration,
                'timestamp': current_time
            })
            return True
            
        return False
    
    def should_stop_test(self) -> bool:
        """Check if test should be stopped due to anomalies"""
        stuck_agents = sum(1 for state in self.agent_states.values() 
                          if state.stuck_duration > self.stuck_threshold)
        return stuck_agents > len(self.agent_states) * 0.5  # >50% stuck
