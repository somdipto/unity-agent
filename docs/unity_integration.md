# Unity Plugin Integration

## Overview

The AI Playtesting System requires a Unity plugin to be added to your Unity project for proper integration. This plugin enables communication between the AI agents and your game.

## Plugin Files

The Unity plugin consists of the following key components:

### 1. Network Communication Manager
- Manages socket connections to the AI system
- Handles message serialization/deserialization
- Provides game state access to external agents

### 2. Agent Action Handler
- Processes actions sent by AI agents
- Translates agent commands to Unity inputs
- Validates and sanitizes external commands

### 3. Game State Provider
- Collects relevant game state for agents
- Provides position, health, objectives, etc.
- Tracks relevant gameplay events

## Integration Steps

1. Download the Unity plugin package from the `unity_plugin/` directory
2. Import into your Unity project using Asset -> Import Package
3. Add the `AIPlaytestingController` component to your main camera or a dedicated game object
4. Configure connection settings (host, port) via the component inspector
5. Build your Unity game with the plugin included

## Security Considerations

- The plugin should only be enabled during testing
- Validate and sanitize all incoming commands
- Implement rate limiting to prevent command flooding
- Use local-only connections (localhost) by default

## Customization

For games with specific mechanics, you may need to extend the plugin:

- Override action handlers for custom game mechanics
- Add game-specific state information
- Implement custom logic for difficulty detection
- Add support for custom game events

## Troubleshooting

- If agents can't connect: Check that the Unity game is built with the plugin and is running
- If actions aren't executing: Verify that the action handler is properly configured
- If state isn't updating: Ensure the game state provider has access to all necessary information

For implementation details, refer to the `src/unity_integration/unity_plugin_interface.py` file which demonstrates the expected interface.