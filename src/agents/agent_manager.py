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
        """Initialize the required number of AI agents with diverse personalities"""
        try:
            # Initialize Unity integration
            if not self.unity_manager.initialize():
                raise RuntimeError("Failed to initialize Unity integration")
            
            # Import here to avoid circular imports
            from .base_agent import AgentPersonality
            personalities = list(AgentPersonality)
            
            for i in range(self.num_agents):
                # Distribute personalities evenly across agents
                personality = personalities[i % len(personalities)]
                
                agent = BaseAgent(
                    agent_id=i,
                    game_path=self.game_path,
                    analytics_engine=self.analytics_engine,
                    unity_manager=self.unity_manager,
                    personality=personality
                )
                self.agents.append(agent)
                
            print(f"Initialized {self.num_agents} agents with diverse personalities")
        except Exception as e:
            print(f"Error initializing agents: {str(e)}")
            raise
    
    def run_playtesting(self):
        """Run the playtesting simulation with all agents and real-time monitoring"""
        print(f"Initializing {self.num_agents} agents...")
        try:
            self.initialize_agents()
            self.running = True
            
            # Start all agents in separate threads
            threads = []
            for agent in self.agents:
                thread = threading.Thread(target=agent.run)
                thread.daemon = True
                thread.start()
                threads.append(thread)
            
            # Monitor test with real-time anomaly detection
            start_time = time.time()
            check_interval = 5  # Check every 5 seconds
            
            while time.time() - start_time < self.duration:
                time.sleep(check_interval)
                
                # Check if test should be stopped early due to anomalies
                if self.analytics_engine.should_stop_test():
                    print("Stopping test early: Too many agents are stuck")
                    break
                    
                # Print progress
                elapsed = time.time() - start_time
                print(f"Test progress: {elapsed:.0f}/{self.duration}s, "
                      f"Anomalies detected: {len(self.analytics_engine.anomalies)}")
            
            # Stop all agents
            self.stop_agents()
            
            # Wait for all threads to finish with timeout
            for thread in threads:
                thread.join(timeout=5)
                if thread.is_alive():
                    print(f"Warning: Agent thread did not finish gracefully")
        
        except Exception as e:
            print(f"Error during playtesting execution: {str(e)}")
            self.stop_agents()
            self.results = []
            for agent in self.agents:
                try:
                    self.results.append(agent.get_results())
                except:
                    self.results.append({'agent_id': agent.agent_id, 'actions': [], 'errors': [str(e)]})
            return self.results
        finally:
            if not hasattr(self, 'results') or not self.results:
                self.results = []
                for agent in self.agents:
                    try:
                        self.results.append(agent.get_results())
                    except:
                        self.results.append({'agent_id': agent.agent_id, 'actions': []})
        
        # Collect results
        self.results = [agent.get_results() for agent in self.agents]
        return self.results
    
    def stop_agents(self):
        """Stop all running agents"""
        self.running = False
        for agent in self.agents:
            agent.stop()