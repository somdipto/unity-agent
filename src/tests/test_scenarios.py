"""
Test Scenarios - Implementation of the required test scenarios
"""
from typing import Dict, Any
import time
import os
from ..agents.agent_manager import AgentManager
from ..swarm.swarm_orchestrator import SwarmOrchestrator
from ..analytics.analytics_engine import AnalyticsEngine
from ..reporting.report_generator import ReportGenerator


class TestScenarioRunner:
    """
    Runs the specified test scenarios to validate the AI playtesting system
    """
    
    def __init__(self, output_dir: str = "./test_reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.analytics_engine = AnalyticsEngine()
        self.report_generator = ReportGenerator(output_dir)
    
    def run_scenario_1_softlock_detection(self, game_path: str):
        """
        Scenario 1: Single-player platformer level with hidden softlock.
        Agents must identify the stuck state.
        """
        print("Running Scenario 1: Softlock Detection Test")
        
        # Create a specialized agent manager for this test
        agent_manager = AgentManager(
            game_path=game_path,
            num_agents=1,  # Single player for this test
            duration=600,  # Run for 10 minutes
            analytics_engine=self.analytics_engine
        )
        
        # Run the playtesting session
        results = agent_manager.run_playtesting()
        
        # Generate report for this scenario
        report_path = os.path.join(self.output_dir, "scenario1_softlock_report.json")
        self.report_generator.generate_comprehensive_report(results)
        
        # Analyze results for softlock detection
        softlock_issues = []
        for agent_result in results:
            for issue in agent_result.get('issues_detected', []):
                if issue.get('type') == 'softlock':
                    softlock_issues.append(issue)
        
        print(f"Scenario 1 completed. Detected {len(softlock_issues)} softlock issues.")
        return results
    
    def run_scenario_2_multiplayer_stress(self, game_path: str):
        """
        Scenario 2: Multiplayer game stress test with 50+ agents
        joining, moving, and interacting simultaneously.
        """
        print("Running Scenario 2: Multiplayer Stress Test")
        
        # Create swarm orchestrator with 50+ agents
        swarm_orchestrator = SwarmOrchestrator(
            game_path=game_path,
            num_agents=50,  # 50 agents for stress testing
            duration=900,   # Run for 15 minutes
            analytics_engine=self.analytics_engine
        )
        
        # Run the swarm test
        results = swarm_orchestrator.run_swarm_test()
        
        # Generate report for this scenario
        report_path = os.path.join(self.output_dir, "scenario2_stress_report.json")
        self.report_generator.generate_comprehensive_report(results['individual_results'])
        
        # Analyze swarm-specific metrics
        swarm_metrics = results.get('swarm_metrics', {})
        performance_indicators = swarm_metrics.get('performance_indicators', [])
        
        print(f"Scenario 2 completed. Total issues: {swarm_metrics.get('total_issues_detected', 0)}")
        print(f"Performance indicators: {len(performance_indicators)}")
        return results
    
    def run_scenario_3_difficulty_spike(self, game_path: str):
        """
        Scenario 3: Level with increasing difficulty spikes.
        Agents should flag retry-heavy sections as frustration points.
        """
        print("Running Scenario 3: Difficulty Spike Detection")
        
        # Create an agent manager to test difficulty progression
        agent_manager = AgentManager(
            game_path=game_path,
            num_agents=10,  # Multiple agents to get diverse data
            duration=1200,  # Run for 20 minutes
            analytics_engine=self.analytics_engine
        )
        
        # Run the playtesting session
        results = agent_manager.run_playtesting()
        
        # Analyze for difficulty spikes
        difficulty_spikes = self.analytics_engine.analyze_difficulty_spikes()
        
        print(f"Scenario 3 completed. Detected {len(difficulty_spikes)} difficulty spikes.")
        
        # Generate report
        report_path = os.path.join(self.output_dir, "scenario3_difficulty_report.json")
        self.report_generator.generate_comprehensive_report(results)
        
        return results, difficulty_spikes
    
    def run_scenario_4_open_world_exploration(self, game_path: str):
        """
        Scenario 4: Open-world exploration where agents must find collectibles.
        Reports should note pacing, completion rate, and engagement levels.
        """
        print("Running Scenario 4: Open-World Exploration Test")
        
        # Create an agent manager for exploration testing
        agent_manager = AgentManager(
            game_path=game_path,
            num_agents=20,  # More agents for exploration
            duration=1800,  # Run for 30 minutes
            analytics_engine=self.analytics_engine
        )
        
        # Run the playtesting session
        results = agent_manager.run_playtesting()
        
        # Generate heatmaps for exploration patterns
        for level in ['level1', 'level2']:  # Assuming multiple levels
            try:
                heatmap = self.analytics_engine.generate_heatmap(
                    level=level,
                    output_path=os.path.join(self.output_dir, f"exploration_heatmap_{level}.png")
                )
            except:
                # If specific levels aren't found, try default
                heatmap = self.analytics_engine.generate_heatmap(
                    output_path=os.path.join(self.output_dir, "exploration_heatmap_default.png")
                )
        
        # Calculate exploration metrics
        total_agents = len(results)
        collectibles_found = 0
        total_time = 0
        
        for agent_result in results:
            total_time += agent_result.get('time_spent', 0)
            # In a real implementation, this would track collectible collection
            # For now, we'll use a placeholder
            collectibles_found += len(agent_result.get('actions', [])) // 10  # Placeholder
        
        avg_time_per_agent = total_time / total_agents if total_agents > 0 else 0
        completion_rate = min(1.0, collectibles_found / max(1, total_agents * 5))  # Assuming 5 collectibles per agent target
        
        print(f"Scenario 4 completed.")
        print(f"  Total agents: {total_agents}")
        print(f"  Avg time per agent: {avg_time_per_agent:.2f}s")
        print(f"  Completion rate: {completion_rate:.2%}")
        print(f"  Collectibles 'found': {collectibles_found}")
        
        # Generate report
        report_path = os.path.join(self.output_dir, "scenario4_exploration_report.json")
        self.report_generator.generate_comprehensive_report(results)
        
        return results
    
    def run_all_scenarios(self, game_path: str):
        """
        Run all test scenarios and generate comprehensive results
        """
        print("Starting all test scenarios...")
        
        # Run each scenario
        scenario1_results = self.run_scenario_1_softlock_detection(game_path)
        scenario2_results = self.run_scenario_2_multiplayer_stress(game_path)
        scenario3_results = self.run_scenario_3_difficulty_spike(game_path)
        scenario4_results = self.run_scenario_4_open_world_exploration(game_path)
        
        # Generate a summary report for all scenarios
        summary_report = {
            'scenario_summaries': {
                'scenario_1': {
                    'description': 'Softlock Detection Test',
                    'test_type': 'single_player',
                    'agents_used': 1,
                    'duration': 600,
                    'issues_found': self._count_issues(scenario1_results)
                },
                'scenario_2': {
                    'description': 'Multiplayer Stress Test',
                    'test_type': 'multiplayer',
                    'agents_used': 50,
                    'duration': 900,
                    'issues_found': scenario2_results['swarm_metrics']['total_issues_detected']
                },
                'scenario_3': {
                    'description': 'Difficulty Spike Detection',
                    'test_type': 'balance_analysis',
                    'agents_used': 10,
                    'duration': 1200,
                    'issues_found': len(scenario3_results[1])  # difficulty spikes
                },
                'scenario_4': {
                    'description': 'Open-World Exploration',
                    'test_type': 'engagement_analysis',
                    'agents_used': 20,
                    'duration': 1800,
                    'issues_found': self._count_issues(scenario4_results)
                }
            }
        }
        
        # Save summary report
        summary_path = os.path.join(self.output_dir, "all_scenarios_summary.json")
        import json
        with open(summary_path, 'w') as f:
            json.dump(summary_report, f, indent=2)
        
        print("All test scenarios completed successfully!")
        return {
            'scenario_1': scenario1_results,
            'scenario_2': scenario2_results,
            'scenario_3': scenario3_results,
            'scenario_4': scenario4_results,
            'summary': summary_report
        }
    
    def _count_issues(self, results):
        """Helper method to count issues in results"""
        if not results:
            return 0
            
        total_issues = 0
        if isinstance(results, list):
            for agent_result in results:
                total_issues += len(agent_result.get('issues_detected', []))
        else:
            # If results is a dict from swarm, check individual_results
            if 'individual_results' in results:
                for agent_result in results['individual_results']:
                    total_issues += len(agent_result.get('issues_detected', []))
            else:
                # If it's a single agent result
                total_issues = len(results.get('issues_detected', []))
        
        return total_issues