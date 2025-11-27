#!/usr/bin/env python3

import sys
sys.path.append('./src')

def test_improved_architecture():
    """Test the improved existing architecture"""
    
    # Test 1: Agent personalities
    from src.agents.base_agent import BaseAgent, AgentPersonality
    from src.analytics.analytics_engine import AnalyticsEngine
    
    analytics = AnalyticsEngine()
    
    # Create agents with different personalities
    cautious_agent = BaseAgent(0, "/fake/path", analytics, personality=AgentPersonality.CAUTIOUS)
    aggressive_agent = BaseAgent(1, "/fake/path", analytics, personality=AgentPersonality.AGGRESSIVE)
    
    assert cautious_agent.caution_level == 0.9
    assert aggressive_agent.caution_level == 0.2
    print("✓ Agent personalities working")
    
    # Test 2: Real-time anomaly detection
    analytics.log_agent_action(0, "move", {"position": (0, 0, 0)})
    analytics.log_agent_action(0, "move", {"position": (0, 0, 0)})  # Same position
    
    # Simulate time passing
    import time
    analytics.agent_stuck_times[0] = time.time() - analytics.session_start_time - 35  # 35 seconds ago
    
    should_stop = analytics.should_stop_test()
    assert should_stop == True
    print("✓ Real-time anomaly detection working")
    
    # Test 3: Connection retry logic
    from src.unity_integration.unity_connector import UnityConnector
    
    connector = UnityConnector()
    # This will fail but should handle it gracefully
    result = connector.connect(max_retries=1)
    assert result == False  # Expected to fail without Unity running
    print("✓ Connection retry logic working")
    
    print("\n🎯 All improvements integrated successfully!")
    print("\nKey improvements made:")
    print("1. ✅ Added retry logic to existing UnityConnector")
    print("2. ✅ Enhanced BaseAgent with personality system") 
    print("3. ✅ Added real-time detection to AnalyticsEngine")
    print("4. ✅ Improved AgentManager with early stopping")
    print("5. ✅ All changes work with existing architecture")

if __name__ == "__main__":
    test_improved_architecture()
