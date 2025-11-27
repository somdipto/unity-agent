import asyncio
import argparse
from agents.personalities import PersonalityAgent, AgentPersonality
from agents.async_agent_manager import AsyncAgentManager
from unity_integration.websocket_client import WebSocketClient
from analytics.realtime_detector import RealtimeDetector

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agents", type=int, default=5)
    parser.add_argument("--duration", type=int, default=300)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    
    # Create diverse agent personalities
    personalities = list(AgentPersonality)
    agents = []
    for i in range(args.agents):
        personality = personalities[i % len(personalities)]
        agents.append(PersonalityAgent(f"agent_{i}", personality))
    
    # Setup WebSocket client and manager
    client = WebSocketClient(args.host, args.port)
    manager = AsyncAgentManager(agents, client)
    detector = RealtimeDetector()
    
    print(f"Starting {args.agents} agents for {args.duration}s...")
    
    # Connect and run
    if await client.connect():
        await manager.run_swarm(args.duration)
        print("Test completed successfully!")
    else:
        print("Failed to connect to Unity game")

if __name__ == "__main__":
    asyncio.run(main())
