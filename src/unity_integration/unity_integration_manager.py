"""
Unity Integration Manager - Main interface for connecting AI agents to Unity games
"""
import time
from typing import Dict, Any, Optional
from .unity_connector import UnityConnector
from ..agents.base_agent import BaseAgent
from ..analytics.analytics_engine import AnalyticsEngine


class UnityIntegrationManager:
    """
    Manages the integration between AI agents and Unity games
    """
    
    def __init__(self, game_path: str = None, analytics_engine: AnalyticsEngine = None):
        self.game_path = game_path
        self.analytics_engine = analytics_engine
        self.unity_connector = UnityConnector()
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Initialize the connection to the Unity game"""
        print("Initializing Unity integration...")
        
        try:
            # Connect to the Unity game
            if not self.unity_connector.connect():
                print("Failed to connect to Unity game")
                return False
            
            # Perform any necessary setup in Unity
            self._setup_unity_environment()
            
            self.is_initialized = True
            print("Unity integration initialized successfully")
            return True
        except Exception as e:
            print(f"Error during Unity integration initialization: {str(e)}")
            self.is_initialized = False
            return False
    
    def _setup_unity_environment(self):
        """Set up the Unity environment for playtesting"""
        # Configure Unity to run in playtesting mode
        # Disable UI elements that might interfere
        # Set appropriate rendering settings
        
        # Example settings that might be changed:
        self.unity_connector.set_game_setting('rendering_quality', 'low')  # Better performance
        self.unity_connector.set_game_setting('ui_visible', False)  # Hide UI for clean testing
        self.unity_connector.set_game_setting('player_input_disabled', True)  # Disable human input
    
    def get_game_state(self, agent_id: int) -> Dict[str, Any]:
        """Get the current game state for an agent from Unity"""
        if not self.is_initialized:
            raise RuntimeError("Unity integration not initialized")
        
        return self.unity_connector.get_game_state(agent_id)
    
    def send_action_to_unity(self, agent_id: int, action: str, params: Dict[str, Any] = None) -> bool:
        """Send an action to Unity for execution"""
        if not self.is_initialized:
            raise RuntimeError("Unity integration not initialized")
        
        request_id = self.unity_connector.send_action(agent_id, action, params)
        return len(request_id) > 0
    
    def run_playtesting_session(self, agents: list, duration: int):
        """Run a complete playtesting session with the agents"""
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("Cannot start playtesting session - failed to initialize Unity integration")
        
        print(f"Starting playtesting session with {len(agents)} agents for {duration} seconds")
        
        # Start all agents
        for agent in agents:
            # In a real implementation, we'd run each agent in its own thread
            # and monitor their progress
            pass
        
        # Let the agents run for the specified duration
        start_time = time.time()
        while time.time() - start_time < duration:
            time.sleep(0.1)  # Small pause to prevent busy waiting
            
            # Monitor agents and collect data
            self._monitor_agents(agents)
        
        # Stop all agents
        for agent in agents:
            agent.stop()
        
        print("Playtesting session completed")
    
    def _monitor_agents(self, agents: list):
        """Monitor agents and collect data during the playtesting session"""
        for agent in agents:
            # Update agent's view of the game state
            game_state = self.get_game_state(agent.agent_id)
            
            # Log agent position for heatmap generation
            if self.analytics_engine and 'position' in game_state:
                self.analytics_engine.log_position(
                    agent.agent_id, 
                    game_state['position'], 
                    level=game_state.get('current_area', 'default')
                )
    
    def get_level_data(self, level_name: str) -> Dict[str, Any]:
        """Get level-specific data for analysis"""
        if not self.is_initialized:
            raise RuntimeError("Unity integration not initialized")
        
        return self.unity_connector.get_level_data(level_name)
    
    def cleanup(self):
        """Clean up Unity integration resources"""
        self.unity_connector.disconnect()
        self.is_initialized = False
        print("Unity integration cleaned up")