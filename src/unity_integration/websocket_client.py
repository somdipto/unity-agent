import asyncio
import websockets
import json
import logging
from typing import Optional, Callable

class WebSocketClient:
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.uri = f"ws://{host}:{port}"
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.retry_count = 0
        self.max_retries = 5
        
    async def connect(self):
        """Connect with exponential backoff retry"""
        while self.retry_count < self.max_retries:
            try:
                self.websocket = await websockets.connect(self.uri)
                self.retry_count = 0
                return True
            except Exception as e:
                self.retry_count += 1
                wait_time = 2 ** self.retry_count
                logging.warning(f"Connection failed, retrying in {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
        return False
    
    async def send_action(self, action: dict):
        """Send action with auto-reconnect"""
        if not self.websocket:
            await self.connect()
        
        try:
            await self.websocket.send(json.dumps(action))
        except websockets.exceptions.ConnectionClosed:
            await self.connect()
            await self.websocket.send(json.dumps(action))
    
    async def receive_state(self) -> dict:
        """Receive game state with auto-reconnect"""
        if not self.websocket:
            await self.connect()
        
        try:
            data = await self.websocket.recv()
            return json.loads(data)
        except websockets.exceptions.ConnectionClosed:
            await self.connect()
            data = await self.websocket.recv()
            return json.loads(data)
