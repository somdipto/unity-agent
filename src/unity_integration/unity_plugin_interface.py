"""
Unity Plugin Interface - Python module that would be mirrored in Unity C# code
"""
import json
import socket
import threading
import time
from typing import Dict, Any, Callable


class UnityPluginInterface:
    """
    Interface that mirrors the C# plugin code that would be added to Unity projects
    This is a conceptual representation of what the Unity plugin would do
    """
    
    def __init__(self, host: str = 'localhost', port: int = 8080):
        self.host = host
        self.port = port
        self.socket = None
        self.is_running = False
        self.clients = []  # Connected AI system clients
        self.game_state_callbacks = []
        self.action_handlers = {}
        
    def start_server(self):
        """Start the socket server to communicate with AI agents"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        
        self.is_running = True
        
        print(f"Unity Plugin Server started on {self.host}:{self.port}")
        
        # Start listening for connections
        server_thread = threading.Thread(target=self._accept_connections, daemon=True)
        server_thread.start()
        
    def stop_server(self):
        """Stop the socket server"""
        self.is_running = False
        if self.socket:
            self.socket.close()
        print("Unity Plugin Server stopped")
    
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
                
                response = self._process_message(message)
                
                if response:
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    
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
        msg_type = message.get('type', '')
        data = message.get('data', {})
        
        if msg_type == 'action':
            return self._handle_action(data)
        elif msg_type == 'get_state':
            return self._handle_get_state(data)
        elif msg_type == 'set_setting':
            return self._handle_set_setting(data)
        elif msg_type == 'get_level_data':
            return self._handle_get_level_data(data)
        else:
            return {
                'id': message.get('id', ''),
                'type': 'error',
                'data': {'error': f'Unknown message type: {msg_type}'}
            }
    
    def _handle_action(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an action request from an AI agent"""
        agent_id = data.get('agent_id', -1)
        action = data.get('action', '')
        params = data.get('params', {})
        
        # In a real implementation, this would call Unity's APIs to execute the action
        # For now, we'll simulate the action
        result = self._execute_unity_action(agent_id, action, params)
        
        return {
            'id': data.get('request_id', ''),
            'type': 'action_response',
            'data': {
                'agent_id': agent_id,
                'action': action,
                'result': result,
                'success': True
            }
        }
    
    def _handle_get_state(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a request for current game state"""
        agent_id = data.get('agent_id', -1)
        
        # In a real implementation, this would get the actual game state from Unity
        # For now, we'll return a simulated state
        state = self._get_current_game_state(agent_id)
        
        return {
            'id': data.get('request_id', ''),
            'type': 'state_response',
            'data': {
                'agent_id': agent_id,
                'state': state
            }
        }
    
    def _handle_set_setting(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a request to change a game setting"""
        setting_name = data.get('setting', '')
        value = data.get('value', None)
        
        # In a real implementation, this would change Unity settings
        # For now, we'll just acknowledge the request
        self._set_unity_setting(setting_name, value)
        
        return {
            'id': data.get('request_id', ''),
            'type': 'setting_response',
            'data': {
                'setting': setting_name,
                'value': value,
                'success': True
            }
        }
    
    def _handle_get_level_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a request for level-specific data"""
        level_name = data.get('level_name', '')
        
        # In a real implementation, this would get level data from Unity
        # For now, we'll return simulated level data
        level_data = self._get_level_info(level_name)
        
        return {
            'id': data.get('request_id', ''),
            'type': 'level_data_response',
            'data': {
                'level_name': level_name,
                'level_data': level_data
            }
        }
    
    def _execute_unity_action(self, agent_id: int, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action in the Unity game (placeholder)"""
        # This would interface with Unity's C# code in the real implementation
        # For simulation purposes, we'll just return a success result
        return {
            'action': action,
            'agent_id': agent_id,
            'executed': True,
            'details': f'Action {action} executed for agent {agent_id}'
        }
    
    def _get_current_game_state(self, agent_id: int) -> Dict[str, Any]:
        """Get the current game state from Unity (placeholder)"""
        # This would get actual game state from Unity in the real implementation
        # For simulation, return a basic state
        return {
            'position': (0, 0, 0),
            'health': 100,
            'in_combat': False,
            'current_objective': None,
            'level_progress': 0.0,
            'time_in_level': time.time(),
            'is_dead': False,
            'current_area': "unknown",
            'puzzle_active': False
        }
    
    def _set_unity_setting(self, setting_name: str, value: Any):
        """Change a setting in the Unity game (placeholder)"""
        # This would change actual Unity settings in the real implementation
        print(f"Setting {setting_name} to {value}")
    
    def _get_level_info(self, level_name: str) -> Dict[str, Any]:
        """Get information about a specific level (placeholder)"""
        # This would get actual level data from Unity in the real implementation
        return {
            'level_name': level_name,
            'bounds': {'min': (-10, -10, -10), 'max': (10, 10, 10)},
            'obstacles': [],
            'collectibles': [],
            'enemies': [],
            'checkpoints': []
        }
    
    def register_game_state_callback(self, callback: Callable):
        """Register a callback to be notified when game state changes"""
        self.game_state_callbacks.append(callback)
    
    def notify_game_state_change(self, agent_id: int, new_state: Dict[str, Any]):
        """Notify all registered callbacks of a game state change"""
        for callback in self.game_state_callbacks:
            try:
                callback(agent_id, new_state)
            except Exception as e:
                print(f"Error in game state callback: {str(e)}")