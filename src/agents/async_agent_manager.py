import asyncio
from typing import List
from .base_agent import BaseAgent
from ..unity_integration.websocket_client import WebSocketClient

class AsyncAgentManager:
    def __init__(self, agents: List[BaseAgent], game_client: WebSocketClient):
        self.agents = agents
        self.game_client = game_client
        self.running = False
        
    async def run_agent(self, agent: BaseAgent):
        """Run single agent asynchronously"""
        while self.running:
            try:
                state = await self.game_client.receive_state()
                action = agent.decide_action(state)
                await self.game_client.send_action(action)
                await asyncio.sleep(0.1)  # Prevent overwhelming
            except Exception as e:
                print(f"Agent {agent.id} error: {e}")
                await asyncio.sleep(1)
    
    async def run_swarm(self, duration: int):
        """Run all agents concurrently"""
        self.running = True
        
        # Start all agents
        tasks = [self.run_agent(agent) for agent in self.agents]
        
        # Run for specified duration
        try:
            await asyncio.wait_for(asyncio.gather(*tasks), timeout=duration)
        except asyncio.TimeoutError:
            pass
        finally:
            self.running = False
