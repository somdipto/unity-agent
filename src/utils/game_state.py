"""
Game State - Represents the current state of the game as perceived by an AI agent
"""
from typing import Dict, Any, Tuple


class GameState:
    """
    Represents the game state as observed by an AI agent
    """
    
    def __init__(self):
        self.position = (0, 0, 0)  # x, y, z coordinates
        self.health = 100
        self.in_combat = False
        self.current_objective = None
        self.level_progress = 0.0
        self.time_in_level = 0
        self.last_progress_time = 0
        self.is_dead = False
        self.current_area = "unknown"
        self.puzzle_active = False
        self.stuck_counter = 0
        self.previous_positions = []
        self.max_stuck_positions = 10  # Number of positions to track for stuck detection
        
    def update_from_game(self):
        """
        Update the game state from the actual game
        In a real implementation, this would interface with Unity
        """
        # This is a simulation - in reality, this would get data from Unity
        import time
        self.time_in_level = time.time()
        
        # Add current position to tracking list
        self.previous_positions.append(self.position)
        if len(self.previous_positions) > self.max_stuck_positions:
            self.previous_positions.pop(0)
    
    def update_from_unity(self, unity_state: dict):
        """
        Update the game state from Unity
        """
        import time
        # Update from Unity state data
        self.position = unity_state.get('position', self.position)
        self.health = unity_state.get('health', self.health)
        self.in_combat = unity_state.get('in_combat', self.in_combat)
        self.current_objective = unity_state.get('current_objective', self.current_objective)
        self.level_progress = unity_state.get('level_progress', self.level_progress)
        self.time_in_level = unity_state.get('time_in_level', time.time())
        self.is_dead = unity_state.get('is_dead', self.is_dead)
        self.current_area = unity_state.get('current_area', self.current_area)
        self.puzzle_active = unity_state.get('puzzle_active', self.puzzle_active)
        
        # Add current position to tracking list
        self.previous_positions.append(self.position)
        if len(self.previous_positions) > self.max_stuck_positions:
            self.previous_positions.pop(0)
        
    def get_position(self) -> Tuple[float, float, float]:
        """Get the current position of the agent"""
        return self.position
    
    def is_stuck(self) -> bool:
        """
        Check if the agent appears to be stuck in one location
        """
        if len(self.previous_positions) < self.max_stuck_positions:
            return False
        
        # Check if most recent positions are similar (indicating no movement)
        recent_positions = self.previous_positions[-5:]  # Check last 5 positions
        if not recent_positions:
            return False
            
        # Calculate distance between first and last of recent positions
        first_pos = recent_positions[0]
        last_pos = recent_positions[-1]
        
        # Calculate squared distance to avoid expensive sqrt operation
        dist_squared = (first_pos[0] - last_pos[0])**2 + (first_pos[1] - last_pos[1])**2 + (first_pos[2] - last_pos[2])**2
        
        # Compare squared distance to squared threshold to avoid sqrt
        return dist_squared < 1.0  # 1.0 squared is still 1.0
    
    def is_in_combat(self) -> bool:
        """Check if the agent is currently in combat"""
        return self.in_combat
    
    def is_puzzle_area(self) -> bool:
        """Check if the agent is in a puzzle area"""
        return self.puzzle_active
    
    def has_objective(self) -> bool:
        """Check if there's a current objective"""
        return self.current_objective is not None
    
    def is_infinite_loop(self) -> bool:
        """
        Check if the agent might be in an infinite loop
        This could be based on repetitive behavior patterns
        """
        # For now, a simple check based on repetitive position changes
        if len(self.previous_positions) < 20:
            return False
            
        # Check if the agent is oscillating between positions
        recent_positions = self.previous_positions[-10:]
        unique_positions = len(set(recent_positions))
        
        # If too few unique positions in recent history, might be a loop
        return unique_positions < 3
    
    def is_frustrated(self) -> bool:
        """
        Determine if the agent seems to be experiencing frustration
        based on repeated failures or retries
        """
        # This would need integration with retry/death tracking
        # For now, we'll use a heuristic based on health and progress
        if self.health < 30 and self.level_progress < 0.1:
            # Low health with little progress might indicate frustration
            return True
        return False
    
    def is_exploring(self) -> bool:
        """
        Determine if the agent is in an exploration phase
        based on movement patterns and objective status
        """
        # If no current objective and agent is moving to new areas
        if not self.has_objective():
            # Check if recent positions include new areas
            if len(self.previous_positions) > 5:
                unique_positions = len(set(self.previous_positions))
                total_positions = len(self.previous_positions)
                # If most positions are unique, agent might be exploring
                return (unique_positions / total_positions) > 0.8
        return False
    
    def is_progressing(self) -> bool:
        """
        Determine if the agent is making progress toward objectives
        """
        # Check if level progress has increased since last check
        # For now, we'll use a simple heuristic
        return self.level_progress > 0.0
    
    def get_movement_speed(self) -> float:
        """
        Calculate the agent's recent movement speed
        """
        if len(self.previous_positions) < 2:
            return 0.0
            
        # Calculate speed based on the last two positions
        pos1 = self.previous_positions[-2]
        pos2 = self.previous_positions[-1]
        
        distance = ((pos1[0] - pos2[0])**2 + 
                   (pos1[1] - pos2[1])**2 + 
                   (pos1[2] - pos2[2])**2)**0.5
        
        # Assuming each update happens at a fixed interval (0.5 seconds)
        time_interval = 0.5  # seconds
        speed = distance / time_interval
        return speed
    
    def is_slow_moving(self) -> bool:
        """
        Check if the agent is moving slowly which might indicate
        confusion or careful navigation
        """
        speed = self.get_movement_speed()
        return speed < 0.5  # threshold for slow movement
    
    def is_health_critical(self) -> bool:
        """
        Check if agent health is at critical levels
        """
        return self.health < 20  # critical health threshold
    
    def get_current_behavior_context(self) -> str:
        """
        Determine the current behavioral context of the agent
        """
        if self.is_dead:
            return "dead"
        elif self.in_combat:
            return "combat"
        elif self.puzzle_active:
            return "puzzle"
        elif self.is_health_critical():
            return "critical_health"
        elif self.is_stuck():
            return "stuck"
        elif self.is_infinite_loop():
            return "infinite_loop"
        elif self.is_frustrated():
            return "frustrated"
        elif self.is_exploring():
            return "exploring"
        elif self.has_objective():
            return "goal_oriented"
        else:
            return "idle"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the game state to a dictionary for logging"""
        return {
            'position': self.position,
            'health': self.health,
            'in_combat': self.in_combat,
            'current_objective': self.current_objective,
            'level_progress': self.level_progress,
            'time_in_level': self.time_in_level,
            'is_dead': self.is_dead,
            'current_area': self.current_area,
            'puzzle_active': self.puzzle_active
        }