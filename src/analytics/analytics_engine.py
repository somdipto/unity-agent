"""
Analytics Engine - Core system for collecting, processing, and analyzing gameplay data
"""
import time
import json
import threading
from typing import Dict, Any, List
from collections import defaultdict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


class AnalyticsEngine:
    """
    Main analytics engine for collecting and processing gameplay data
    """
    
    def __init__(self):
        self.lock = threading.Lock()  # Ensure thread safety for multi-threaded agent logging
        self.agents_data = defaultdict(list)  # Data per agent
        self.global_events = []  # Events affecting all agents
        self.performance_metrics = {}
        self.engagement_data = defaultdict(list)
        self.heatmap_data = defaultdict(lambda: defaultdict(int))
        self.issue_logs = []
        self.session_start_time = time.time()
        
        # Real-time anomaly detection
        self.agent_positions = {}  # Track last known positions
        self.agent_stuck_times = {}  # Track how long agents have been stuck
        self.stuck_threshold = 30.0  # Seconds before considering an agent stuck
        self.anomalies = []
        
    def log_agent_action(self, agent_id: int, action: str, game_state: Dict[str, Any]):
        """Log an action taken by an agent with real-time anomaly detection"""
        timestamp = time.time() - self.session_start_time
        
        with self.lock:
            # Check for stuck agents in real-time
            if 'position' in game_state:
                self._check_agent_movement(agent_id, game_state['position'], timestamp)
            
            action_record = (timestamp, action, game_state, agent_id)
            self.agents_data[agent_id].append(action_record)
    
    def _check_agent_movement(self, agent_id: int, position: tuple, timestamp: float):
        """Check if agent is stuck and log anomalies"""
        # Note: This method should be called within a lock context
        if agent_id not in self.agent_positions:
            self.agent_positions[agent_id] = position
            self.agent_stuck_times[agent_id] = timestamp
            return
        
        # Calculate distance moved
        prev_pos = self.agent_positions[agent_id]
        distance = sum((a - b) ** 2 for a, b in zip(position, prev_pos)) ** 0.5
        
        if distance < 0.1:  # Agent barely moved
            stuck_duration = timestamp - self.agent_stuck_times[agent_id]
            if stuck_duration > self.stuck_threshold:
                # Log soft-lock anomaly
                anomaly = {
                    'type': 'soft_lock',
                    'agent_id': agent_id,
                    'position': position,
                    'duration': stuck_duration,
                    'timestamp': timestamp
                }
                self.anomalies.append(anomaly)
                self.issue_logs.append(f"Agent {agent_id} soft-locked at {position} for {stuck_duration:.1f}s")
        else:
            # Agent moved, reset stuck timer
            self.agent_positions[agent_id] = position
            self.agent_stuck_times[agent_id] = timestamp
    
    def should_stop_test(self) -> bool:
        """Check if test should be stopped due to too many stuck agents"""
        with self.lock:
            if not self.agent_positions:
                return False
                
            current_time = time.time() - self.session_start_time
            stuck_agents = 0
            
            for agent_id, stuck_time in self.agent_stuck_times.items():
                if current_time - stuck_time > self.stuck_threshold:
                    stuck_agents += 1
            
            # Stop if more than 50% of agents are stuck
            return stuck_agents > len(self.agent_positions) * 0.5
    
    def log_agent_death(self, agent_id: int):
        """Log when an agent dies in the game"""
        death_record = {
            'timestamp': time.time() - self.session_start_time,
            'event': 'death',
            'agent_id': agent_id
        }
        with self.lock:
            self.global_events.append(death_record)
        
    def log_retry(self, agent_id: int):
        """Log when an agent retries a section"""
        retry_record = {
            'timestamp': time.time() - self.session_start_time,
            'event': 'retry',
            'agent_id': agent_id
        }
        with self.lock:
            self.global_events.append(retry_record)
        
    def log_high_engagement(self, agent_id: int, action: str):
        """Log high engagement events"""
        engagement_record = {
            'timestamp': time.time() - self.session_start_time,
            'action': action,
            'agent_id': agent_id,
            'engagement_level': 'high'
        }
        with self.lock:
            self.engagement_data[agent_id].append(engagement_record)
        
    def log_progression(self, agent_id: int, action: str):
        """Log progression-related events"""
        progression_record = {
            'timestamp': time.time() - self.session_start_time,
            'action': action,
            'agent_id': agent_id,
            'event_type': 'progression'
        }
        with self.lock:
            self.agents_data[agent_id].append(progression_record)
    
    def log_anomaly(self, anomaly_type: str, details: Dict[str, Any]):
        """Log detected anomalies like softlocks or infinite loops"""
        anomaly_record = {
            'timestamp': time.time() - self.session_start_time,
            'type': anomaly_type,
            'details': details
        }
        with self.lock:
            self.issue_logs.append(anomaly_record)
    
    def log_position(self, agent_id: int, position: tuple, level: str = "default"):
        """Log agent position for heatmap generation"""
        x, y, z = position
        # For heatmap, we'll use x, z coordinates (top-down view)
        with self.lock:
            self.heatmap_data[level][(int(x), int(z))] += 1
    
    def get_agent_metrics(self, agent_id: int) -> Dict[str, Any]:
        """Get computed metrics for a specific agent"""
        with self.lock:
            # Create copies to avoid holding lock during calculations if possible, 
            # but here calculations are fast enough.
            agent_data = list(self.agents_data[agent_id])
            engagements = list(self.engagement_data[agent_id])
            global_events = list(self.global_events)
        
        # Calculate basic metrics
        total_actions = len(agent_data)
        high_engagement_count = len([e for e in engagements if e['engagement_level'] == 'high'])
        death_count = len([e for e in global_events if e['event'] == 'death' and e['agent_id'] == agent_id])
        retry_count = len([e for e in global_events if e['event'] == 'retry' and e['agent_id'] == agent_id])
        
        # Calculate engagement rate
        engagement_rate = high_engagement_count / max(1, total_actions)
        
        # Calculate time metrics - handle compact data format (timestamp is first element)
        if agent_data:
            # agent_data now contains tuples in format (timestamp, action, game_state, agent_id)
            start_time = agent_data[0][0]  # First element is timestamp
            end_time = agent_data[-1][0]  # Last element's first item is timestamp
            total_time = end_time - start_time
        else:
            total_time = 0
            
        return {
            'total_actions': total_actions,
            'high_engagement_actions': high_engagement_count,
            'engagement_rate': engagement_rate,
            'deaths': death_count,
            'retries': retry_count,
            'total_time': total_time,
            'actions_per_second': total_actions / max(1, total_time) if total_time > 0 else 0
        }
    
    def generate_heatmap(self, level: str = "default", output_path: str = None) -> np.ndarray:
        """Generate a heatmap of agent activity in a level"""
        with self.lock:
            if level not in self.heatmap_data:
                print(f"No heatmap data for level: {level}")
                return np.array([])
            
            # Get all coordinates with activity - copy dict to avoid mutation during iteration
            coords_data = dict(self.heatmap_data[level])
            
        coords = list(coords_data.keys())
        if not coords:
            print(f"No activity data for level: {level}")
            return np.array([])
        
        # Determine bounds
        x_coords = [c[0] for c in coords]
        z_coords = [c[1] for c in coords]
        
        min_x, max_x = min(x_coords), max(x_coords)
        min_z, max_z = min(z_coords), max(z_coords)
        
        # Create grid
        grid_width = max_x - min_x + 1
        grid_height = max_z - min_z + 1
        heatmap = np.zeros((grid_height, grid_width))
        
        # Fill grid with activity counts
        for (x, z), count in coords_data.items():
            grid_x = x - min_x
            grid_z = z - min_z
            heatmap[grid_z, grid_x] = count
        
        # Visualize heatmap if output path provided
        if output_path:
            self._visualize_heatmap(heatmap, min_x, max_x, min_z, max_z, output_path)
        
        return heatmap
    
    def _visualize_heatmap(self, heatmap: np.ndarray, min_x: int, max_x: int, min_z: int, max_z: int, output_path: str):
        """Visualize and save the heatmap"""
        plt.figure(figsize=(10, 8))
        
        # Create custom colormap for better visualization
        colors = ['white', 'yellow', 'orange', 'red', 'darkred']
        n_bins = 100
        cmap = LinearSegmentedColormap.from_list('custom', colors, N=n_bins)
        
        # Plot heatmap
        plt.imshow(heatmap, extent=[min_x, max_x, min_z, max_z], origin='lower', cmap=cmap, aspect='auto')
        plt.colorbar(label='Agent Activity')
        plt.title('Agent Activity Heatmap')
        plt.xlabel('X Coordinate')
        plt.ylabel('Z Coordinate')
        
        # Save the plot
        plt.savefig(output_path)
        plt.close()
    
    def analyze_difficulty_spikes(self) -> List[Dict[str, Any]]:
        """Analyze the data to find difficulty spikes based on retry patterns"""
        # Group events by time windows
        time_window_size = 30  # seconds
        windows = {}
        
        for event in self.global_events:
            if event['event'] == 'retry':
                window_id = int(event['timestamp'] // time_window_size)
                if window_id not in windows:
                    windows[window_id] = {'retries': 0, 'deaths': 0, 'start_time': window_id * time_window_size}
                windows[window_id]['retries'] += 1
            elif event['event'] == 'death':
                window_id = int(event['timestamp'] // time_window_size)
                if window_id not in windows:
                    windows[window_id] = {'retries': 0, 'deaths': 0, 'start_time': window_id * time_window_size}
                windows[window_id]['deaths'] += 1
        
        # Find windows with above-average retry/death rates
        all_rates = [w['retries'] + w['deaths'] for w in windows.values()]
        if not all_rates:
            return []
        
        avg_rate = sum(all_rates) / len(all_rates)
        threshold = avg_rate * 1.5  # Consider 1.5x average as a spike
        
        difficulty_spikes = []
        for window_id, window_data in windows.items():
            if (window_data['retries'] + window_data['deaths']) > threshold:
                difficulty_spikes.append({
                    'time_range': (window_data['start_time'], window_data['start_time'] + time_window_size),
                    'retry_count': window_data['retries'],
                    'death_count': window_data['deaths'],
                    'severity': (window_data['retries'] + window_data['deaths']) / max(1, avg_rate)
                })
        
        return difficulty_spikes
    
    def generate_comprehensive_analytics(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        # Calculate engagement metrics across all agents
        all_engagement_rates = []
        all_actions_per_second = []
        
        for agent_id in self.agents_data.keys():
            metrics = self.get_agent_metrics(agent_id)
            all_engagement_rates.append(metrics['engagement_rate'])
            all_actions_per_second.append(metrics['actions_per_second'])
        
        # Calculate overall metrics
        avg_engagement_rate = sum(all_engagement_rates) / max(1, len(all_engagement_rates))
        avg_actions_per_second = sum(all_actions_per_second) / max(1, len(all_actions_per_second))
        
        # Get difficulty spike analysis
        difficulty_spikes = self.analyze_difficulty_spikes()
        
        # Count different types of issues
        issue_counts = defaultdict(int)
        for issue in self.issue_logs:
            issue_counts[issue['type']] += 1
        
        return {
            'session_duration': time.time() - self.session_start_time,
            'total_agents': len(self.agents_data),
            'total_actions': sum(len(data) for data in self.agents_data.values()),
            'average_engagement_rate': avg_engagement_rate,
            'average_actions_per_second': avg_actions_per_second,
            'difficulty_spikes': difficulty_spikes,
            'issue_counts': dict(issue_counts),
            'total_issues': len(self.issue_logs),
            'total_deaths': len([e for e in self.global_events if e['event'] == 'death']),
            'total_retries': len([e for e in self.global_events if e['event'] == 'retry'])
        }
    
    def export_data(self, output_path: str):
        """Export all analytics data to JSON file"""
        # Convert compact data format back to readable format for export
        readable_agents_data = {}
        for agent_id, agent_data in self.agents_data.items():
            readable_agents_data[agent_id] = []
            for record in agent_data:  # record is (timestamp, action, game_state, agent_id)
                readable_agents_data[agent_id].append({
                    'timestamp': record[0],
                    'action': record[1],
                    'game_state': record[2],
                    'agent_id': record[3]
                })
        
        export_data = {
            'session_start_time': self.session_start_time,
            'agents_data': readable_agents_data,
            'global_events': self.global_events,
            'engagement_data': dict(self.engagement_data),
            'issue_logs': self.issue_logs,
            'performance_metrics': self.performance_metrics,
            'comprehensive_analytics': self.generate_comprehensive_analytics()
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
    
    def analyze_agent_behavior_patterns(self) -> Dict[str, Any]:
        """Analyze behavioral patterns across agents"""
        behavior_analysis = {
            'action_distribution': self._get_action_distribution(),
            'behavior_clusters': self._identify_behavior_clusters(),
            'engagement_patterns': self._analyze_engagement_patterns(),
            'progression_analysis': self._analyze_progression_patterns()
        }
        
        return behavior_analysis
    
    def _get_action_distribution(self) -> Dict[str, Any]:
        """Get distribution of actions across all agents"""
        action_counts = defaultdict(int)
        total_actions = 0
        
        for agent_id, agent_data in self.agents_data.items():
            for record in agent_data:
                if 'action' in record:
                    action = record['action']
                    action_counts[action] += 1
                    total_actions += 1
        
        action_distribution = {
            action: count / total_actions if total_actions > 0 else 0
            for action, count in action_counts.items()
        }
        
        return {
            'counts': dict(action_counts),
            'percentages': action_distribution,
            'total_actions': total_actions
        }
    
    def _identify_behavior_clusters(self) -> List[Dict[str, Any]]:
        """Identify clusters of similar agent behavior"""
        clusters = []
        
        # This would use more sophisticated clustering in a real implementation
        # For now, we'll categorize based on action patterns
        for agent_id in self.agents_data.keys():
            metrics = self.get_agent_metrics(agent_id)
            behavior_profile = {
                'agent_id': agent_id,
                'engagement_rate': metrics['engagement_rate'],
                'deaths': metrics['deaths'],
                'retries': metrics['retries'],
                'actions_per_second': metrics['actions_per_second']
            }
            
            # Categorize based on engagement and challenge response
            if behavior_profile['engagement_rate'] > 0.7:
                behavior_profile['type'] = 'highly_engaged'
            elif behavior_profile['deaths'] > 10 or behavior_profile['retries'] > 10:
                behavior_profile['type'] = 'frustrated'
            elif behavior_profile['engagement_rate'] < 0.3:
                behavior_profile['type'] = 'disengaged'
            else:
                behavior_profile['type'] = 'balanced'
            
            clusters.append(behavior_profile)
        
        return clusters
    
    def _analyze_engagement_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in agent engagement over time"""
        engagement_over_time = []
        
        # Group engagement data by time windows
        time_window_size = 60  # 1 minute windows
        windows = {}
        
        for agent_id, engagements in self.engagement_data.items():
            for record in engagements:
                window_id = int(record['timestamp'] // time_window_size)
                if window_id not in windows:
                    windows[window_id] = {'high_engagement': 0, 'start_time': window_id * time_window_size}
                windows[window_id]['high_engagement'] += 1
        
        # Convert to time series data
        for window_id, data in sorted(windows.items()):
            engagement_over_time.append({
                'time_range': (data['start_time'], data['start_time'] + time_window_size),
                'high_engagement_count': data['high_engagement']
            })
        
        return {
            'time_series': engagement_over_time,
            'trend': self._calculate_engagement_trend(engagement_over_time)
        }
    
    def _calculate_engagement_trend(self, time_series: List[Dict[str, Any]]) -> str:
        """Calculate the overall trend in engagement"""
        if len(time_series) < 2:
            return "insufficient_data"
        
        early_avg = sum(item['high_engagement_count'] for item in time_series[:max(1, len(time_series)//2)]) / max(1, len(time_series)//2)
        late_avg = sum(item['high_engagement_count'] for item in time_series[len(time_series)//2:]) / len(time_series[len(time_series)//2:])
        
        if late_avg > early_avg * 1.2:
            return "increasing"
        elif late_avg < early_avg * 0.8:
            return "decreasing"
        else:
            return "stable"
    
    def _analyze_progression_patterns(self) -> Dict[str, Any]:
        """Analyze how agents progress through the game"""
        progression_analysis = {
            'completion_rate': self._calculate_completion_rate(),
            'progression_speed': self._calculate_progression_speed(),
            'bottleneck_analysis': self._identify_progression_bottlenecks()
        }
        return progression_analysis
    
    def _calculate_completion_rate(self) -> float:
        """Calculate the rate at which agents are progressing"""
        # This would need to track actual progress objectives
        # For now, using placeholder implementation
        if not self.agents_data:
            return 0.0
        
        # In a real implementation, this would track level/objective completion
        # For now, using a placeholder based on action count
        completed_agents = sum(1 for agent_id in self.agents_data.keys() 
                              if len(self.agents_data[agent_id]) > 50)  # arbitrary threshold
        
        return completed_agents / len(self.agents_data)
    
    def _calculate_progression_speed(self) -> Dict[str, Any]:
        """Calculate the speed at which agents progress"""
        speeds = []
        for agent_id in self.agents_data.keys():
            metrics = self.get_agent_metrics(agent_id)
            if metrics['total_time'] > 0:
                # Placeholder: using action count as proxy for progress
                speed = metrics['total_actions'] / metrics['total_time']
                speeds.append(speed)
        
        if not speeds:
            return {'avg_speed': 0, 'min_speed': 0, 'max_speed': 0}
        
        return {
            'avg_speed': sum(speeds) / len(speeds),
            'min_speed': min(speeds),
            'max_speed': max(speeds),
            'std_deviation': np.std(speeds) if len(speeds) > 1 else 0
        }
    
    def _identify_progression_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify areas where agents struggle to progress"""
        bottlenecks = []
        
        # Analyze areas with high death/retry rates
        # Group events by location (would need position data in events)
        # For now, this is a simplified version
        
        # Identify time periods with high difficulty
        difficulty_spikes = self.analyze_difficulty_spikes()
        for spike in difficulty_spikes:
            bottlenecks.append({
                'type': 'difficulty_spike',
                'time_range': spike['time_range'],
                'severity': spike['severity'],
                'issue_details': f"High death/retry rate during {spike['time_range']}"
            })
        
        return bottlenecks
    
    def generate_advanced_analytics(self) -> Dict[str, Any]:
        """Generate advanced analytics beyond the basic set"""
        comprehensive = self.generate_comprehensive_analytics()
        behavior_analysis = self.analyze_agent_behavior_patterns()
        
        advanced_analytics = {
            'basic_analytics': comprehensive,
            'behavior_analysis': behavior_analysis,
            'action_analysis': self._get_action_distribution(),
            'engagement_insights': self._analyze_engagement_patterns(),
            'progression_insights': self._analyze_progression_patterns(),
            'recommendations': self._generate_recommendations(comprehensive, behavior_analysis)
        }
        
        return advanced_analytics
    
    def _generate_recommendations(self, basic_analytics: Dict[str, Any], behavior_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analytics data"""
        recommendations = []
        
        # Difficulty recommendations
        if basic_analytics['total_deaths'] > basic_analytics['total_agents'] * 5:
            recommendations.append("High death rate detected - consider reducing difficulty in certain areas")
        
        if basic_analytics['total_retries'] > basic_analytics['total_agents'] * 3:
            recommendations.append("High retry rate detected - identify frustrating sections")
        
        # Engagement recommendations
        if basic_analytics['average_engagement_rate'] < 0.3:
            recommendations.append("Low overall engagement - consider adding more engaging elements")
        
        # Progression recommendations
        difficulty_spikes = basic_analytics['difficulty_spikes']
        if len(difficulty_spikes) > basic_analytics['total_agents'] * 0.5:
            recommendations.append("Multiple difficulty spikes detected - smooth difficulty curve")
        
        # Behavioral pattern recommendations
        frustrated_agents = [agent for agent in behavior_analysis['behavior_clusters'] 
                            if agent['type'] == 'frustrated']
        if len(frustrated_agents) > len(behavior_analysis['behavior_clusters']) * 0.3:
            recommendations.append("High percentage of frustrated agents - investigate causes")
        
        return recommendations