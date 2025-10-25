#!/usr/bin/env python3
"""
Simple test runner that tests the key functionality without complex imports
"""
import sys
import os

# Add the src directory to Python path
src_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_dir)

def test_game_state():
    """Test GameState functionality"""
    from src.utils.game_state import GameState
    
    # Create a game state instance
    gs = GameState()
    
    # Test initial values
    assert gs.position == (0, 0, 0), f"Expected (0, 0, 0), got {gs.position}"
    assert gs.health == 100, f"Expected 100, got {gs.health}"
    assert gs.in_combat == False, f"Expected False, got {gs.in_combat}"
    
    # Test updating from Unity data
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
    
    gs.update_from_unity(unity_data)
    
    assert gs.position == (5, 10, 15), f"Expected (5, 10, 15), got {gs.position}"
    assert gs.health == 75, f"Expected 75, got {gs.health}"
    assert gs.in_combat == True, f"Expected True, got {gs.in_combat}"
    assert gs.current_objective == 'Defeat the boss', f"Expected 'Defeat the boss', got {gs.current_objective}"
    
    print("✓ GameState tests passed")

def test_base_agent():
    """Test BaseAgent functionality"""
    from src.agents.base_agent import BaseAgent
    from src.analytics.analytics_engine import AnalyticsEngine
    
    analytics = AnalyticsEngine()
    agent = BaseAgent(agent_id=1, game_path="/test/path", analytics_engine=analytics)
    
    # Test initial state
    assert agent.agent_id == 1, f"Expected 1, got {agent.agent_id}"
    assert agent.game_path == "/test/path", f"Expected '/test/path', got {agent.game_path}"
    assert agent.exploration_bias == 0.7, f"Expected 0.7, got {agent.exploration_bias}"
    
    # Test action decision
    action = agent.decide_action()
    assert isinstance(action, str), f"Expected string action, got {type(action)}"
    assert len(action) > 0, f"Expected non-empty action, got '{action}'"
    
    print("✓ BaseAgent tests passed")

def test_analytics_engine():
    """Test AnalyticsEngine functionality"""
    from src.analytics.analytics_engine import AnalyticsEngine
    
    ae = AnalyticsEngine()
    
    # Test logging an action
    ae.log_agent_action(1, 'move_forward', {'position': (1, 2, 3)})
    
    agent_data = ae.agents_data[1]
    assert len(agent_data) == 1, f"Expected 1 action, got {len(agent_data)}"
    assert agent_data[0]['action'] == 'move_forward', f"Expected 'move_forward', got {agent_data[0]['action']}"
    
    # Test logging death
    ae.log_agent_death(1)
    death_events = [e for e in ae.global_events if e['event'] == 'death']
    assert len(death_events) == 1, f"Expected 1 death event, got {len(death_events)}"
    
    # Test metrics
    metrics = ae.get_agent_metrics(1)
    assert 'total_actions' in metrics, "Expected 'total_actions' in metrics"
    assert 'deaths' in metrics, "Expected 'deaths' in metrics"
    
    print("✓ AnalyticsEngine tests passed")

def test_advanced_analytics():
    """Test advanced analytics functionality"""
    from src.analytics.analytics_engine import AnalyticsEngine
    
    ae = AnalyticsEngine()
    
    # Add some test data
    for i in range(5):
        ae.log_agent_action(i, 'move_forward', {'position': (i, i, i)})
        ae.log_high_engagement(i, 'attack')
        if i % 2 == 0:
            ae.log_agent_death(i)
        if i % 3 == 0:
            ae.log_retry(i)
    
    # Test advanced analytics
    advanced = ae.generate_advanced_analytics()
    
    assert 'basic_analytics' in advanced, "Expected 'basic_analytics' in result"
    assert 'behavior_analysis' in advanced, "Expected 'behavior_analysis' in result"
    assert 'recommendations' in advanced, "Expected 'recommendations' in result"
    
    print("✓ Advanced Analytics tests passed")

def test_game_state_enhancements():
    """Test the new GameState enhancements"""
    from src.utils.game_state import GameState
    
    gs = GameState()
    
    # Test behavior context detection
    gs.is_dead = True
    assert gs.get_current_behavior_context() == "dead", f"Expected 'dead', got {gs.get_current_behavior_context()}"
    
    gs.is_dead = False
    gs.in_combat = True
    assert gs.get_current_behavior_context() == "combat", f"Expected 'combat', got {gs.get_current_behavior_context()}"
    
    gs.in_combat = False
    gs.puzzle_active = True
    assert gs.get_current_behavior_context() == "puzzle", f"Expected 'puzzle', got {gs.get_current_behavior_context()}"
    
    gs.puzzle_active = False
    gs.health = 10
    assert gs.get_current_behavior_context() == "critical_health", f"Expected 'critical_health', got {gs.get_current_behavior_context()}"
    
    print("✓ GameState enhancements tests passed")

if __name__ == "__main__":
    print("Running functionality tests...")
    
    test_game_state()
    test_base_agent()
    test_analytics_engine()
    test_advanced_analytics()
    test_game_state_enhancements()
    
    print("\n✓ All functionality tests passed!")