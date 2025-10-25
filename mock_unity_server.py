#!/usr/bin/env python3
"""
Mock Unity Server - Simulates the Unity plugin for testing purposes
"""
import json
import socket
import threading
import time
from typing import Dict, Any, Callable


class MockUnityServer:
    """
    A mock Unity server to simulate the Unity plugin for testing the AI playtesting system
    """
    
    def __init__(self, host: str = 'localhost', port: int = 8080):
        self.host = host
        self.port = port
        self.socket = None
        self.is_running = False
        self.clients = []  # Connected AI system clients
        
    def start_server(self):
        """Start the mock Unity socket server"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        
        self.is_running = True
        
        print(f"Mock Unity Server started on {self.host}:{self.port}")
        
        # Start listening for connections
        server_thread = threading.Thread(target=self._accept_connections, daemon=True)
        server_thread.start()
        
        # Keep the server running
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down Mock Unity Server...")
            self.stop_server()
    
    def stop_server(self):
        """Stop the socket server"""
        self.is_running = False
        if self.socket:
            self.socket.close()
        print("Mock Unity Server stopped")
    
    def _accept_connections(self):
        """Accept incoming connections from AI system"""
        while self.is_running:
            try:
                client_socket, address = self.socket.accept()
                print(f"New connection from {address}")
                
                # Start a thread to handle this client
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
                
                self.clients.append(client_socket)
                
            except Exception as e:
                if self.is_running:
                    print(f"Error accepting connections: {str(e)}")
    
    def _handle_client(self, client_socket: socket.socket, address: tuple):
        """Handle communication with a single AI system client"""
        while self.is_running:
            try:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                message_str = data.decode('utf-8')
                message = json.loads(message_str)
                
                print(f"Received message: {message}")
                response = self._process_message(message)
                
                if response:
                    response_str = json.dumps(response)
                    client_socket.send(response_str.encode('utf-8'))
                    print(f"Sent response: {response}")
                    
            except json.JSONDecodeError:
                print(f"Received invalid JSON from client {address}")
            except Exception as e:
                print(f"Error handling client {address}: {str(e)}")
                break
        
        # Remove client when connection is closed
        if client_socket in self.clients:
            self.clients.remove(client_socket)
        client_socket.close()
    
    def _process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process a message from the AI system"""
        msg_id = message.get('id', '')
        msg_type = message.get('type', '')
        data = message.get('data', {})
        
        if msg_type == 'action':
            return self._handle_action(msg_id, data)
        elif msg_type == 'get_state':
            return self._handle_get_state(msg_id, data)
        elif msg_type == 'set_setting':
            return self._handle_set_setting(msg_id, data)
        elif msg_type == 'get_level_data':
            return self._handle_get_level_data(msg_id, data)
        else:
            return {
                'id': msg_id,
                'type': 'error',
                'data': {'error': f'Unknown message type: {msg_type}'}
            }
    
    def _handle_action(self, msg_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an action request from an AI agent"""
        agent_id = data.get('agent_id', -1)
        action = data.get('action', '')
        params = data.get('params', {})
        
        print(f"Executing action '{action}' for agent {agent_id}")
        
        # Simulate different actions
        if action == 'move_forward':
            # Simulate movement by changing position
            pass
        elif action == 'attack':
            # Simulate attack
            pass
        elif action == 'jump':
            # Simulate jump
            pass
        
        return {
            'id': msg_id,
            'type': 'action_response',
            'data': {
                'agent_id': agent_id,
                'action': action,
                'result': 'executed',
                'success': True
            }
        }
    
    def _handle_get_state(self, msg_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a request for current game state"""
        agent_id = data.get('agent_id', -1)
        
        # Return a simulated game state
        state = {
            'position': (0.0, 0.0, 0.0),
            'health': 100,
            'in_combat': False,
            'current_objective': 'explore',
            'level_progress': 0.2,
            'time_in_level': time.time(),
            'is_dead': False,
            'current_area': "starting_area",
            'puzzle_active': False,
            'enemies_nearby': 0,
            'collectibles_found': 0
        }
        
        # Simulate some movement to make the demo more interesting
        # Each agent gets a slightly different position
        state['position'] = (
            float(agent_id) * 1.5,
            0.0,
            float(agent_id) * 1.5
        )
        
        return {
            'id': msg_id,
            'type': 'state_response',
            'data': {
                'agent_id': agent_id,
                'state': state
            }
        }
    
    def _handle_set_setting(self, msg_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a request to change a game setting"""
        setting_name = data.get('setting', '')
        value = data.get('value', None)
        
        print(f"Setting {setting_name} to {value}")
        
        return {
            'id': msg_id,
            'type': 'setting_response',
            'data': {
                'setting': setting_name,
                'value': value,
                'success': True
            }
        }
    
    def _handle_get_level_data(self, msg_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a request for level-specific data"""
        level_name = data.get('level_name', 'default_level')
        
        level_data = {
            'level_name': level_name,
            'bounds': {'min': (-100, -10, -100), 'max': (100, 10, 100)},
            'obstacles': [
                {'type': 'wall', 'position': (10, 0, 10), 'size': (2, 4, 2)},
                {'type': 'wall', 'position': (-10, 0, 10), 'size': (2, 4, 2)},
            ],
            'collectibles': [
                {'type': 'health', 'position': (5, 1, 5)},
                {'type': 'coin', 'position': (-5, 1, -5)},
            ],
            'enemies': [
                {'type': 'guard', 'position': (0, 0, 0), 'patrol_path': [(0,0,0), (5,0,5), (0,0,10)]},
            ],
            'checkpoints': [
                {'name': 'start', 'position': (0, 0, 0)},
                {'name': 'mid', 'position': (10, 0, 10)},
            ]
        }
        
        return {
            'id': msg_id,
            'type': 'level_data_response',
            'data': {
                'level_name': level_name,
                'level_data': level_data
            }
        }


if __name__ == "__main__":
    # Start the mock Unity server
    server = MockUnityServer()
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\nReceived interrupt signal")
        server.stop_server()