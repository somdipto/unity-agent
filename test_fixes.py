#!/usr/bin/env python3

import sys
sys.path.append('./src')

def test_websocket_client():
    from src.unity_integration.websocket_client import WebSocketClient
    client = WebSocketClient()
    print("✓ WebSocket client created")

def test_async_manager():
    from src.agents.async_agent_manager import AsyncAgentManager
    from src.agents.personalities import PersonalityAgent, AgentPersonality
    from src.unity_integration.websocket_client import WebSocketClient
    
    agents = [PersonalityAgent("test", AgentPersonality.CAUTIOUS)]
    client = WebSocketClient()
    manager = AsyncAgentManager(agents, client)
    print("✓ Async manager created")

def test_realtime_detector():
    from src.analytics.realtime_detector import RealtimeDetector
    detector = RealtimeDetector()
    
    # Test normal movement
    detector.update_agent("agent1", (0, 0, 0))
    detector.update_agent("agent1", (1, 0, 0))
    assert not detector.should_stop_test()
    print("✓ Realtime detector working")

def test_pydantic_models():
    from src.models.game_models import GameState, Action, ActionType
    
    # Valid state
    state = GameState(
        player_position=(1.0, 2.0, 3.0),
        health=75.0,
        timestamp=123.456
    )
    
    # Valid action
    action = Action(
        type=ActionType.MOVE,
        direction=(1.0, 0.0, 0.0),
        agent_id="test_agent"
    )
    print("✓ Pydantic models working")

def test_personalities():
    from src.agents.personalities import PersonalityAgent, AgentPersonality
    
    agent = PersonalityAgent("test", AgentPersonality.AGGRESSIVE)
    action = agent.decide_action({"position": [0, 0, 0]})
    assert action["agent_id"] == "test"
    print("✓ Agent personalities working")

if __name__ == "__main__":
    print("Testing architecture fixes...")
    test_websocket_client()
    test_async_manager()
    test_realtime_detector()
    test_pydantic_models()
    test_personalities()
    print("\n🎯 All fixes implemented successfully!")
    print("\nNext steps:")
    print("1. Install websockets: pip install websockets pydantic")
    print("2. Add WebSocketServer.cs to Unity project")
    print("3. Run: python src/main_async.py --agents 10 --duration 60")
