# Unity Agent Plugin

This Unity plugin enables communication between Unity games and the AI Playtesting System.

## Components

- `PythonConnector.cs` - Main communication hub with the Python system
- `PlayerHealth.cs` - Health management for the player character
- `CombatManager.cs` - Tracks combat state and enemies
- `ObjectiveTracker.cs` - Manages game objectives and progress
- `PlayerInput.cs` - Handles player input (can be disabled for AI agents)
- `PlayerController.cs` - Player movement and animation control

## Setup Instructions

1. Attach the `PythonConnector.cs` script to a GameObject in your scene (e.g., a "GameManager" object)
2. Configure the IP address and port to match your Python system settings (default: localhost:8080)
3. Add required tags to your game objects:
   - "Enemy" for enemy characters
   - "PuzzleArea" for puzzle trigger volumes
   - "Ground" for ground surfaces
4. Add required components to your player character:
   - `PlayerHealth.cs`
   - `PlayerController.cs` or `PlayerInput.cs`
   - `Rigidbody` and `Collider` for physics interactions
   - `Animator` if using character animations

## Communication Protocol

The plugin communicates with the Python system via TCP socket connection using JSON messages.

### Message Format
```json
{
  "id": "request_id",
  "type": "message_type",
  "data": { ... },
  "timestamp": "ISO8601_timestamp"
}
```

### Supported Message Types

1. **From Unity to Python:**
   - `game_state_update` - Periodically sends current game state

2. **From Python to Unity:**
   - `action` - Execute a specific action (move_forward, jump, attack, etc.)
   - `get_state` - Send current game state
   - `set_setting` - Modify a game setting
   - `get_level_data` - Send level-specific information

## Configuration

### PythonConnector Settings
- `ipAddress` - IP address of the Python system (default: 127.0.0.1)
- `port` - Port number of the Python system (default: 8080)
- Enable/disable what game state information to send periodically

## Dependencies

The plugin requires the LitJson library for JSON serialization. You can import it via Unity's Package Manager or add the source files to your project.

## Testing

1. Start the AI Playtesting System Python server
2. Run your Unity game
3. Check the Unity console for connection messages
4. Verify that game state data is being sent and received properly

## Notes

- The connector sends game state updates every 0.5 seconds by default
- All communication is asynchronous to avoid blocking Unity's main thread
- The system includes basic error handling for network disconnections