"""
Configuration utilities for the AI playtesting system
"""
import os
from typing import Optional


def get_api_key() -> Optional[str]:
    """
    Get API key from environment variable or config file
    """
    # Try environment variable first
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        return api_key
    
    # Try config file
    config_path = os.path.expanduser('~/.ai-playtest-config')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY='):
                    return line.split('=', 1)[1].strip()
    
    return None


def get_unity_connection_settings() -> dict:
    """
    Get Unity connection settings from config
    """
    # Default settings
    settings = {
        'host': 'localhost',
        'port': 8080,
        'timeout': 30
    }
    
    # Try to load from environment or config file
    host = os.environ.get('UNITY_HOST')
    if host:
        settings['host'] = host
    
    port = os.environ.get('UNITY_PORT')
    if port:
        settings['port'] = int(port)
    
    timeout = os.environ.get('UNITY_TIMEOUT')
    if timeout:
        settings['timeout'] = int(timeout)
    
    return settings