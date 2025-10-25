import unittest
from unittest.mock import Mock, patch
import sys
import os
import time

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.game_state import GameState
from agents.base_agent import BaseAgent
from analytics.analytics_engine import AnalyticsEngine
from unity_integration.unity_connector import UnityConnector


class TestGameState(unittest.TestCase):
    """Unit tests for GameState class"""
    
    def setUp(self):
        self.game_state = GameState()
    
    def test_initial_state(self):
        """Test that GameState initializes with correct default values"""
        self.assertEqual(self.game_state.position, (0, 0, 0))
        self.assertEqual(self.game_state.health, 100)
        self.assertFalse(self.game_state.in_combat)
        self.assertIsNone(self.game_state.current_objective)
        self.assertEqual(self.game_state.level_progress, 0.0)
        self.assertEqual(self.game_state.time_in_level, 0)
        self.assertFalse(self.game_state.is_dead)
        self.assertEqual(self.game_state.current_area, "unknown")
        self.assertFalse(self.game_state.puzzle_active)
        self.assertEqual(self.game_state.stuck_counter, 0)
        self.assertEqual(len(self.game_state.previous_positions), 0)
        self.assertEqual(self.game_state.max_stuck_positions, 10)
    
    def test_update_from_unity(self):
        """Test updating game state from Unity data"""
        unity_data = {
            'position': (5, 10, 15),
            'health': 75,
            'in_combat': True,
            'current_objective': 'Defeat the boss',
            'level_progress': 0.5,
            'time_in_level': 120,
            'is_dead': False,
            'current_area': 'Boss Room',
            'puzzle_active': True
        }
        
        self.game_state.update_from_unity(unity_data)
        
        self.assertEqual(self.game_state.position, (5, 10, 15))
        self.assertEqual(self.game_state.health, 75)
        self.assertTrue(self.game_state.in_combat)
        self.assertEqual(self.game_state.current_objective, 'Defeat the boss')
        self.assertEqual(self.game_state.level_progress, 0.5)
        self.assertEqual(self.game_state.time_in_level, 120)
        self.assertFalse(self.game_state.is_dead)
        self.assertEqual(self.game_state.current_area, 'Boss Room')
        self.assertTrue(self.game_state.puzzle_active)
        self.assertEqual(len(self.game_state.previous_positions), 1)
        self.assertEqual(self.game_state.previous_positions[0], (5, 10, 15))
    
    def test_is_stuck_detection(self):
        """Test the stuck detection logic"""
        # Add positions that are close together
        for i in range(10):
            self.game_state.previous_positions.append((0.1 * i, 0, 0))
        
        # Should not be stuck if we don't have enough positions
        self.game_state.previous_positions = self.game_state.previous_positions[:5]
        self.assertFalse(self.game_state.is_stuck())
        
        # Should be stuck if positions are close together
        for i in range(10):
            self.game_state.previous_positions.append((0.1 * i, 0, 0))
        self.assertTrue(self.game_state.is_stuck())
        
        # Should not be stuck if positions are far apart
        self.game_state.previous_positions = [(i, 0, 0) for i in range(10)]
        self.assertFalse(self.game_state.is_stuck())
    
    def test_behavior_context_detection(self):
        """Test that behavior context is correctly identified"""
        # Test dead context
        self.game_state.is_dead = True
        self.assertEqual(self.game_state.get_current_behavior_context(), "dead")
        
        # Test combat context
        self.game_state.is_dead = False
        self.game_state.in_combat = True
        self.assertEqual(self.game_state.get_current_behavior_context(), "combat")
        
        # Test puzzle context
        self.game_state.in_combat = False
        self.game_state.puzzle_active = True
        self.assertEqual(self.game_state.get_current_behavior_context(), "puzzle")
        
        # Test critical health context
        self.game_state.puzzle_active = False
        self.game_state.health = 10
        self.assertEqual(self.game_state.get_current_behavior_context(), "critical_health")
        
        # Test other contexts...
        self.game_state.health = 100
        self.game_state.current_objective = "test"
        self.assertEqual(self.game_state.get_current_behavior_context(), "goal_oriented")
    
    def test_to_dict(self):
        """Test that to_dict returns correct structure"""
        data = self.game_state.to_dict()
        self.assertIn('position', data)
        self.assertIn('health', data)
        self.assertIn('in_combat', data)
        self.assertIn('current_objective', data)
        self.assertIn('level_progress', data)
        self.assertIn('time_in_level', data)
        self.assertIn('is_dead', data)
        self.assertIn('current_area', data)
        self.assertIn('puzzle_active', data)


class TestBaseAgent(unittest.TestCase):
    """Unit tests for BaseAgent class"""
    
    def setUp(self):
        self.analytics_engine = Mock()
        self.base_agent = BaseAgent(
            agent_id=1,
            game_path="/test/path",
            analytics_engine=self.analytics_engine
        )
    
    def test_initialization(self):
        """Test that BaseAgent initializes correctly"""
        self.assertEqual(self.base_agent.agent_id, 1)
        self.assertEqual(self.base_agent.game_path, "/test/path")
        self.assertEqual(self.base_agent.analytics_engine, self.analytics_engine)
        self.assertIsInstance(self.base_agent.game_state, GameState)
        self.assertFalse(self.base_agent.is_running)
        self.assertEqual(len(self.base_agent.results['actions']), 0)
        self.assertEqual(self.base_agent.results['deaths'], 0)
        self.assertEqual(self.base_agent.exploration_bias, 0.7)
        self.assertEqual(self.base_agent.caution_level, 0.5)
        self.assertEqual(self.base_agent.focus_duration, 5)
    
    def test_decide_action_simple(self):
        """Test that decide_action returns a valid action"""
        action = self.base_agent.decide_action()
        self.assertIsInstance(action, str)
        self.assertTrue(len(action) > 0)
    
    def test_pursue_objective(self):
        """Test the pursue_objective method with various objectives"""
        # Test combat objective
        self.base_agent.game_state.current_objective = "Defeat the enemy"
        self.base_agent.game_state.in_combat = True
        action = self.base_agent.pursue_objective()
        self.assertIn(action, ['attack', 'defend'])
        
        # Test exploration objective
        self.base_agent.game_state.current_objective = "Explore the area"
        action = self.base_agent.pursue_objective()
        self.assertIn(action, ['move_forward', 'look_around', 'interact'])
    
    def test_stop_method(self):
        """Test the stop method"""
        self.base_agent.is_running = True
        self.base_agent.stop()
        self.assertFalse(self.base_agent.is_running)


class TestAnalyticsEngine(unittest.TestCase):
    """Unit tests for AnalyticsEngine class"""
    
    def setUp(self):
        self.analytics_engine = AnalyticsEngine()
    
    def test_initialization(self):
        """Test AnalyticsEngine initialization"""
        self.assertEqual(len(self.analytics_engine.agents_data), 0)
        self.assertEqual(len(self.analytics_engine.global_events), 0)
        self.assertEqual(len(self.analytics_engine.issue_logs), 0)
    
    def test_log_agent_action(self):
        """Test logging agent actions"""
        self.analytics_engine.log_agent_action(1, 'move_forward', {'position': (1, 2, 3)})
        self.assertIn(1, self.analytics_engine.agents_data)
        self.assertEqual(len(self.analytics_engine.agents_data[1]), 1)
        self.assertEqual(self.analytics_engine.agents_data[1][0]['action'], 'move_forward')
    
    def test_log_agent_death(self):
        """Test logging agent deaths"""
        self.analytics_engine.log_agent_death(1)
        self.assertEqual(len(self.analytics_engine.global_events), 1)
        self.assertEqual(self.analytics_engine.global_events[0]['event'], 'death')
        self.assertEqual(self.analytics_engine.global_events[0]['agent_id'], 1)
    
    def test_log_retry(self):
        """Test logging retries"""
        self.analytics_engine.log_retry(1)
        self.assertEqual(len(self.analytics_engine.global_events), 1)
        self.assertEqual(self.analytics_engine.global_events[0]['event'], 'retry')
        self.assertEqual(self.analytics_engine.global_events[0]['agent_id'], 1)
    
    def test_get_agent_metrics(self):
        """Test retrieving agent metrics"""
        # Log some data first
        self.analytics_engine.log_agent_action(1, 'move_forward', {'position': (1, 2, 3)})
        self.analytics_engine.log_high_engagement(1, 'attack')
        self.analytics_engine.log_agent_death(1)
        self.analytics_engine.log_retry(1)
        
        metrics = self.analytics_engine.get_agent_metrics(1)
        
        self.assertEqual(metrics['deaths'], 1)
        self.assertEqual(metrics['retries'], 1)
        self.assertGreater(metrics['total_actions'], 0)
        self.assertGreater(metrics['high_engagement_actions'], 0)
    
    def test_generate_advanced_analytics(self):
        """Test generating advanced analytics"""
        # Log some data first
        self.analytics_engine.log_agent_action(1, 'move_forward', {'position': (1, 2, 3)})
        self.analytics_engine.log_agent_action(1, 'jump', {'position': (2, 2, 3)})
        self.analytics_engine.log_high_engagement(1, 'attack')
        
        advanced_analytics = self.analytics_engine.generate_advanced_analytics()
        
        self.assertIn('basic_analytics', advanced_analytics)
        self.assertIn('behavior_analysis', advanced_analytics)
        self.assertIn('action_analysis', advanced_analytics)
        self.assertIn('engagement_insights', advanced_analytics)
        self.assertIn('progression_insights', advanced_analytics)
        self.assertIn('recommendations', advanced_analytics)


class TestUnityConnector(unittest.TestCase):
    """Unit tests for UnityConnector class"""
    
    @patch('socket.socket')
    def test_initialization(self, mock_socket):
        """Test UnityConnector initialization"""
        connector = UnityConnector()
        # Should use default settings from config
        self.assertIsNotNone(connector.host)
        self.assertIsNotNone(connector.port)
        self.assertIsNotNone(connector.timeout)
        self.assertFalse(connector.is_connected)
    
    @patch('socket.socket')
    def test_connect_method(self, mock_socket):
        """Test the connect method"""
        connector = UnityConnector()
        
        # Mock socket connection
        mock_socket_instance = Mock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.connect.return_value = None
        mock_socket_instance.recv.return_value = b'{"id": "test", "type": "test"}'
        
        # Test connection
        result = connector.connect()
        self.assertTrue(result)
        self.assertTrue(connector.is_connected)
        mock_socket_instance.connect.assert_called_once()


class TestIntegration(unittest.TestCase):
    """Integration tests that test multiple components working together"""
    
    def test_agent_with_analytics(self):
        """Test that agents properly log to analytics engine"""
        analytics_engine = AnalyticsEngine()
        agent = BaseAgent(agent_id=1, game_path="/test", analytics_engine=analytics_engine)
        
        # Simulate agent performing actions
        agent.handle_action_effects('attack')
        agent.handle_action_effects('died')  # This should increment death count
        agent.handle_action_effects('retry')  # This should increment retry count
        
        # Check that analytics were logged
        metrics = analytics_engine.get_agent_metrics(1)
        self.assertEqual(metrics['deaths'], 1)
        self.assertEqual(metrics['retries'], 1)
    
    def test_game_state_integration(self):
        """Test game state updates with agent behavior"""
        analytics_engine = AnalyticsEngine()
        agent = BaseAgent(agent_id=1, game_path="/test", analytics_engine=analytics_engine)
        
        # Update game state to trigger different behaviors
        unity_data = {
            'position': (5, 10, 15),
            'health': 100,
            'in_combat': True,
            'current_objective': 'Defeat the boss',
            'level_progress': 0.5,
            'time_in_level': 120,
            'is_dead': False,
            'current_area': 'Boss Room',
            'puzzle_active': False
        }
        agent.game_state.update_from_unity(unity_data)
        
        # Should be in combat context now
        self.assertEqual(agent.game_state.get_current_behavior_context(), "combat")
        
        # Decide action based on new state
        action = agent.decide_action()
        # In combat context, should be more likely to attack or defend
        self.assertIsInstance(action, str)


if __name__ == '__main__':
    unittest.main()