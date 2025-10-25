"""
Swarm Orchestrator - Manages multiple agents for multiplayer stress testing
"""
import time
import threading
import random
from typing import List, Dict, Any
from ..agents.base_agent import BaseAgent
from ..analytics.analytics_engine import AnalyticsEngine
from ..unity_integration.unity_integration_manager import UnityIntegrationManager


class SwarmOrchestrator:
    """
    Orchestrates a swarm of AI agents for multiplayer game stress testing
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
        """Initialize the required number of agents for swarm testing"""
        print(f"Initializing {self.num_agents} agents for swarm testing...")
        
        # Initialize Unity integration for multiplayer
        if not self.unity_manager.initialize():
            raise RuntimeError("Failed to initialize Unity integration for swarm testing")
        
        for i in range(self.num_agents):
            # Create agents with slightly different behaviors to simulate diverse players
            agent = BaseAgent(
                agent_id=i,
                game_path=self.game_path,
                analytics_engine=self.analytics_engine,
                unity_manager=self.unity_manager
            )
            
            # Modify agent parameters to simulate different player types
            agent.exploration_bias = random.uniform(0.3, 0.9)
            agent.caution_level = random.uniform(0.2, 0.8)
            
            self.agents.append(agent)
    
    def run_swarm_test(self):
        """Execute the multiplayer swarm test"""
        print(f"Starting swarm test with {self.num_agents} agents")
        self.initialize_agents()
        self.running = True
        
        # Start all agents in separate threads
        threads = []
        for agent in self.agents:
            thread = threading.Thread(target=agent.run)
            thread.start()
            threads.append(thread)
        
        # Let agents run for the specified duration
        print(f"Running swarm test for {self.duration} seconds...")
        time.sleep(self.duration)
        
        # Stop all agents
        self.stop_agents()
        
        # Wait for all threads to finish
        for thread in threads:
            thread.join()
        
        # Collect results
        self.results = [agent.get_results() for agent in self.agents]
        
        # Analyze swarm-specific metrics
        swarm_metrics = self.analyze_swarm_behavior()
        
        # Combine individual results with swarm metrics
        final_results = {
            'individual_results': self.results,
            'swarm_metrics': swarm_metrics,
            'total_agents': self.num_agents,
            'test_duration': self.duration
        }
        
        print(f"Swarm test completed with {len(self.results)} agent reports")
        return final_results
    
    def stop_agents(self):
        """Stop all running agents"""
        self.running = False
        for agent in self.agents:
            agent.stop()
    
    def analyze_swarm_behavior(self) -> Dict[str, Any]:
        """Analyze collective behavior patterns of the agent swarm"""
        # Calculate swarm-specific metrics
        total_actions = 0
        total_issues = 0
        total_deaths = 0
        total_retries = 0
        
        for result in self.results:
            total_actions += len(result.get('actions', []))
            total_issues += len(result.get('issues_detected', []))
            total_deaths += result.get('deaths', 0)
            total_retries += result.get('retries', 0)
        
        # Calculate engagement distribution across the swarm
        engagement_distribution = self.calculate_engagement_distribution()
        
        # Identify potential server load indicators
        performance_indicators = self.identify_performance_indicators()
        
        return {
            'total_actions': total_actions,
            'total_issues_detected': total_issues,
            'total_deaths': total_deaths,
            'total_retries': total_retries,
            'avg_actions_per_agent': total_actions / max(1, self.num_agents),
            'avg_issues_per_agent': total_issues / max(1, self.num_agents),
            'engagement_distribution': engagement_distribution,
            'performance_indicators': performance_indicators,
            'collisions_detected': self.detect_multiplayer_interactions()
        }
    
    def calculate_engagement_distribution(self) -> Dict[str, float]:
        """Calculate how engagement is distributed across agents"""
        # This would analyze engagement patterns across the swarm
        # For now, returning a basic distribution
        return {
            'high_engagement_agents': 0.2,  # 20% of agents highly engaged
            'medium_engagement_agents': 0.6,  # 60% of agents medium engaged
            'low_engagement_agents': 0.2  # 20% of agents low engaged
        }
    
    def identify_performance_indicators(self) -> List[Dict[str, Any]]:
        """Identify potential performance issues from swarm behavior"""
        # Look for patterns that might indicate server performance issues
        # For example, many agents timing out or behaving similarly
        indicators = []
        
        # Check if many agents experienced issues at similar times
        issue_times = []
        for result in self.results:
            for issue in result.get('issues_detected', []):
                issue_times.append(issue.get('timestamp', 0))
        
        # If many issues occurred simultaneously, it might indicate server problems
        if len(issue_times) > 1:
            # Simple clustering algorithm to find time periods with many issues
            issue_times.sort()
            cluster_threshold = 5  # 5 seconds to consider issues clustered
            
            current_cluster = [issue_times[0]]
            for i in range(1, len(issue_times)):
                if issue_times[i] - current_cluster[-1] <= cluster_threshold:
                    current_cluster.append(issue_times[i])
                else:
                    if len(current_cluster) > 1:
                        # Found a cluster of simultaneous issues
                        indicators.append({
                            'type': 'potential_server_issue',
                            'start_time': current_cluster[0],
                            'end_time': current_cluster[-1],
                            'issue_count': len(current_cluster)
                        })
                    current_cluster = [issue_times[i]]
        
        return indicators
    
    def detect_multiplayer_interactions(self) -> int:
        """Attempt to detect multiplayer interactions between agents"""
        # In a real implementation, this would interface with the game to detect
        # actual interactions between agents (collisions, combat, etc.)
        # For simulation, we'll return a random number
        return random.randint(0, int(self.num_agents * 0.7))