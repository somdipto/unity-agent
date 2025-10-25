"""
Agent Manager - Controls the overall agent simulation process
"""
import time
import threading
from typing import List, Dict, Any
from .base_agent import BaseAgent
from ..analytics.analytics_engine import AnalyticsEngine
from ..unity_integration.unity_integration_manager import UnityIntegrationManager


class AgentManager:
    """
    Manages multiple AI agents running playtesting simulations
    """
    
    def __init__(self, game_path: str, num_agents: int, duration: int, analytics_engine: AnalyticsEngine):
        self.game_path = game_path
        self.num_agents = num_agents
        self.duration = duration  # in seconds
        self.analytics_engine = analytics_engine
        self.unity_manager = UnityIntegrationManager(game_path, analytics_engine)
        self.agents: List[BaseAgent] = []
        self.results: List[Dict[str, Any]] = []
        self.running = False
        
    def initialize_agents(self):
        """Initialize the required number of AI agents"""
        try:
            # Initialize Unity integration
            if not self.unity_manager.initialize():
                raise RuntimeError("Failed to initialize Unity integration")
                
            for i in range(self.num_agents):
                agent = BaseAgent(
                    agent_id=i,
                    game_path=self.game_path,
                    analytics_engine=self.analytics_engine,
                    unity_manager=self.unity_manager
                )
                self.agents.append(agent)
        except Exception as e:
            print(f"Error initializing agents: {str(e)}")
            raise
    
    def run_playtesting(self):
        """Run the playtesting simulation with all agents"""
        print(f"Initializing {self.num_agents} agents...")
        try:
            self.initialize_agents()
            self.running = True
            
            # Start all agents in separate threads
            threads = []
            for agent in self.agents:
                thread = threading.Thread(target=agent.run)
                thread.daemon = True  # Dies when main program exits
                thread.start()
                threads.append(thread)
            
            # Let agents run for the specified duration
            time.sleep(self.duration)
            
            # Stop all agents
            self.stop_agents()
            
            # Wait for all threads to finish with timeout
            for thread in threads:
                thread.join(timeout=5)  # 5 second timeout for each thread
                
                if thread.is_alive():
                    print(f"Warning: Agent thread did not finish gracefully")
        
        except Exception as e:
            print(f"Error during playtesting execution: {str(e)}")
            self.stop_agents()
            # Still try to collect partial results
            self.results = []
            for agent in self.agents:
                try:
                    self.results.append(agent.get_results())
                except:
                    # If we can't get results, add an empty result
                    self.results.append({'agent_id': agent.agent_id, 'actions': [], 'errors': [str(e)]})
            
            return self.results
        finally:
            # Always collect results even if there were errors
            if not hasattr(self, 'results') or not self.results:
                self.results = []
                for agent in self.agents:
                    try:
                        self.results.append(agent.get_results())
                    except:
                        # If we can't get results, add an empty result
                        self.results.append({'agent_id': agent.agent_id, 'actions': []})
        
        # Collect results
        self.results = [agent.get_results() for agent in self.agents]
        return self.results
    
    def stop_agents(self):
        """Stop all running agents"""
        self.running = False
        for agent in self.agents:
            agent.stop()