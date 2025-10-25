"""
Unity Connector - Handles communication between the AI system and Unity games
"""
import json
import socket
import threading
import time
from typing import Dict, Any, Optional, Callable
from ..utils.config import get_unity_connection_settings


class UnityConnector:
    """
    Manages communication with Unity games via socket connection
    """
    
    def __init__(self):
        settings = get_unity_connection_settings()
        self.host = settings['host']
        self.port = settings['port']
        self.timeout = settings['timeout']
        self.socket: Optional[socket.socket] = None
        self.is_connected = False
        self.message_handlers: Dict[str, Callable] = {}
        self.response_callbacks: Dict[str, Callable] = {}
        self.request_id_counter = 0
        
    def connect(self) -> bool:
        """Establish connection to Unity game"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Set socket options for better reliability
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.settimeout(self.timeout)
            
            self.socket.connect((self.host, self.port))
            self.is_connected = True
            
            # Start message listening thread
            self.listener_thread = threading.Thread(target=self._listen_for_messages, daemon=True)
            self.listener_thread.start()
            
            print(f"Connected to Unity game at {self.host}:{self.port}")
            return True
        except ConnectionRefusedError:
            print(f"Failed to connect to Unity: Connection refused at {self.host}:{self.port}")
            self.is_connected = False
            return False
        except socket.timeout:
            print(f"Failed to connect to Unity: Connection timeout ({self.timeout}s)")
            self.is_connected = False
            return False
        except Exception as e:
            print(f"Unexpected error connecting to Unity: {str(e)}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Close connection to Unity game"""
        self.is_connected = False
        if self.socket:
            self.socket.close()
        print("Disconnected from Unity game")
    
    def send_message(self, message_type: str, data: Dict[str, Any]) -> str:
        """Send a message to the Unity game and return a request ID"""
        if not self.is_connected:
            raise ConnectionError("Not connected to Unity game")
        
        self.request_id_counter += 1
        request_id = f"req_{self.request_id_counter}"
        
        message = {
            'id': request_id,
            'type': message_type,
            'data': data,
            'timestamp': time.time()
        }
        
        try:
            # Use a more efficient serialization approach
            serialized_message = json.dumps(message, separators=(',', ':'))  # Compact JSON
            self.socket.send(serialized_message.encode('utf-8'))
            return request_id
        except BlockingIOError:
            print(f"Failed to send message: socket would block")
            return ""
        except Exception as e:
            print(f"Failed to send message: {str(e)}")
            return ""
    
    def send_action(self, agent_id: int, action: str, params: Dict[str, Any] = None) -> str:
        """Send an action for an agent to perform in the Unity game"""
        data = {
            'agent_id': agent_id,
            'action': action,
            'params': params or {}
        }
        return self.send_message('action', data)
    
    def get_game_state(self, agent_id: int) -> Dict[str, Any]:
        """Request current game state for an agent"""
        # Prepare request
        request_id = f"req_{int(time.time() * 1000000)}"  # unique request ID based on microseconds
        message = {
            'id': request_id,
            'type': 'get_state',
            'data': {'agent_id': agent_id},
            'timestamp': time.time()
        }
        
        # Store callback to handle the response when it arrives
        response_queue = []
        def callback(response):
            response_queue.append(response)
        
        self.response_callbacks[request_id] = callback
        
        # Send the message
        try:
            serialized_message = json.dumps(message)
            self.socket.send(serialized_message.encode('utf-8'))
        except Exception as e:
            print(f"Failed to send get_state message: {str(e)}")
            # Return default state if communication fails
            return self._get_default_game_state()
        
        # Wait for response with timeout
        timeout = time.time() + self.timeout
        while time.time() < timeout:
            if response_queue:
                response = response_queue[0]
                if 'data' in response:
                    return response['data']
                else:
                    # If response doesn't have expected data structure, return default
                    return self._get_default_game_state()
            time.sleep(0.01)  # Small delay to prevent busy waiting
        
        # If no response received within timeout, return default state
        print(f"Warning: No response received for get_state request {request_id}")
        return self._get_default_game_state()

    def _get_default_game_state(self) -> Dict[str, Any]:
        """Return a default game state when actual state can't be retrieved"""
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
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """Register a handler for specific message types"""
        self.message_handlers[message_type] = handler
    
    def _listen_for_messages(self):
        """Listen for messages from the Unity game"""
        while self.is_connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    print("Unity connection closed by remote end")
                    break
                
                message_str = data.decode('utf-8')
                
                # Handle potential partial messages by accumulating until we get complete JSON
                if not message_str.strip():
                    continue
                
                try:
                    message = json.loads(message_str)
                except json.JSONDecodeError as je:
                    print(f"Received invalid JSON from Unity: {str(je)}. Message: {message_str[:100]}...")
                    continue
                
                # Handle response to a request
                if 'id' in message and message['id'] in self.response_callbacks:
                    callback = self.response_callbacks[message['id']]
                    try:
                        callback(message)
                    except Exception as cb_error:
                        print(f"Error in callback for message {message.get('id', 'unknown')}: {str(cb_error)}")
                    finally:
                        # Always remove the callback to prevent memory leaks
                        if message['id'] in self.response_callbacks:
                            del self.response_callbacks[message['id']]
                # Handle incoming message
                elif 'type' in message and message['type'] in self.message_handlers:
                    handler = self.message_handlers[message['type']]
                    try:
                        handler(message)
                    except Exception as h_error:
                        print(f"Error in message handler for type {message['type']}: {str(h_error)}")
                
            except socket.timeout:
                # This is normal, just continue
                continue
            except ConnectionResetError:
                print("Unity connection reset by remote end")
                break
            except OSError as oe:
                print(f"Socket error in Unity connection: {str(oe)}")
                break
            except Exception as e:
                if self.is_connected:  # Only log error if connection should still be active
                    print(f"Unexpected error receiving message from Unity: {str(e)}")
                break
        
        # Clean up if the connection is no longer active
        if self.is_connected:
            print("Unity connection closed, cleaning up...")
            self.is_connected = False
            if hasattr(self, 'socket') and self.socket:
                try:
                    self.socket.close()
                except:
                    pass  # Socket might already be closed
    
    def set_game_setting(self, setting_name: str, value: Any):
        """Change a game setting in Unity"""
        data = {
            'setting': setting_name,
            'value': value
        }
        self.send_message('set_setting', data)
    
    def get_level_data(self, level_name: str) -> Dict[str, Any]:
        """Get level-specific data from Unity"""
        # Prepare request
        request_id = f"req_{int(time.time() * 1000000)}"  # unique request ID based on microseconds
        message = {
            'id': request_id,
            'type': 'get_level_data',
            'data': {'level_name': level_name},
            'timestamp': time.time()
        }
        
        # Store callback to handle the response when it arrives
        response_queue = []
        def callback(response):
            response_queue.append(response)
        
        self.response_callbacks[request_id] = callback
        
        # Send the message
        try:
            serialized_message = json.dumps(message)
            self.socket.send(serialized_message.encode('utf-8'))
        except Exception as e:
            print(f"Failed to send get_level_data message: {str(e)}")
            # Return default level data if communication fails
            return self._get_default_level_data(level_name)
        
        # Wait for response with timeout
        timeout = time.time() + self.timeout
        while time.time() < timeout:
            if response_queue:
                response = response_queue[0]
                if 'data' in response:
                    return response['data']
                else:
                    # If response doesn't have expected data structure, return default
                    return self._get_default_level_data(level_name)
            time.sleep(0.01)  # Small delay to prevent busy waiting
        
        # If no response received within timeout, return default level data
        print(f"Warning: No response received for get_level_data request {request_id}")
        return self._get_default_level_data(level_name)

    def _get_default_level_data(self, level_name: str) -> Dict[str, Any]:
        """Return default level data when actual data can't be retrieved"""
        return {
            'level_name': level_name,
            'bounds': {'min': (-10, -10, -10), 'max': (10, 10, 10)},
            'obstacles': [],
            'collectibles': [],
            'enemies': [],
            'checkpoints': []
        }