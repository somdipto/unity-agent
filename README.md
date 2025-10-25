# Unity-Agent: AI-Driven Playtesting System

Unity-Agent is an advanced AI system that uses intelligent agents to simulate player behavior, automatically detect bugs, identify balance issues, and generate engagement metrics for Unity games.

## Quickstart

```bash
git clone https://github.com/somdipto/unity-agent.git
cd unity-agent
pip install -r requirements.txt
python -m src --game-path /path/to/game.exe --agents 5 --duration 300
```


## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Unity Integration](#unity-integration)
- [Test Scenarios](#test-scenarios)
- [Analytics & Reporting](#analytics--reporting)
- [Examples](#examples)
- [Development](#development)

## Features

- **AI Agents**: Intelligent agents that simulate natural player behavior patterns
- **Multiplayer Swarm Testing**: Test with 50+ concurrent agents for stress testing
- **Anomaly Detection**: Automatically detect softlocks, infinite loops, and other issues
- **Engagement Analytics**: Track player engagement and frustration metrics
- **Difficulty Analysis**: Identify difficulty spikes and balance issues
- **Heatmap Generation**: Visualize player behavior patterns in game environments
- **Comprehensive Reporting**: JSON, human-readable, and LLM-friendly report formats

## Architecture

```
unity-agent/
├── src/                    # Main source code
│   ├── agents/            # AI agent implementation
│   ├── analytics/         # Data collection and analysis
│   ├── reporting/         # Report generation
│   ├── swarm/             # Multiplayer orchestration
│   ├── unity_integration/ # Unity communication
│   ├── utils/             # Utility functions
│   └── tests/             # Test implementations
├── unity_plugin/          # Unity plugin files
├── examples/              # Usage examples
├── docs/                  # Documentation
├── reports/               # Generated reports
└── mock_unity_server.py   # Mock server for testing
```

## Requirements

### System Requirements
- Python 3.8 or higher
- Unity game engine (for integration)

### Python Dependencies
Install all dependencies with:
```bash
pip install -r requirements.txt
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/somdipto/unity-agent.git
cd unity-agent
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (if using LLM features):
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Usage

### Basic Playtesting
Run playtesting with 10 agents for 5 minutes:
```bash
python -m src --game-path /path/to/your/game.exe --agents 10 --duration 300
```

### Multiplayer Swarm Testing
Test with 50 agents in multiplayer mode:
```bash
python -m src --game-path /path/to/your/game.exe --agents 50 --multiplayer --duration 900
```

### Command Line Options
```
--game-path PATH          Path to the Unity game executable
--agents NUM             Number of AI agents to simulate (default: 1)
--multiplayer            Run multiplayer swarm test
--duration SECONDS       Test duration in seconds (default: 300)
--output PATH            Output directory for reports (default: ./reports)
```

## Unity Integration

### Setting up the Unity Plugin

1. Copy the files from `unity_plugin/Assets/Scripts/` to your Unity project's Assets/Scripts/ directory
2. Attach the `PythonConnector.cs` script to a GameObject in your scene (e.g., "GameManager")
3. Configure connection settings (IP: localhost, Port: 8080 by default)
4. Add required tags to your game objects:
   - "Enemy" for enemy characters
   - "PuzzleArea" for puzzle trigger volumes  
   - "Ground" for ground surfaces
5. Build your Unity game with the plugin included

### Communication Protocol

The plugin communicates with the AI system via TCP socket connection using JSON messages. The system expects the following game components:

- A `PlayerHealth` component to track health status
- A `CombatManager` component to track combat state
- An `ObjectiveTracker` to track game objectives
- A `PlayerController` to handle movement

## Test Scenarios

### Scenario 1: Softlock Detection
Tests a single-player level to identify areas where agents get stuck or cannot progress.

### Scenario 2: Multiplayer Stress Test  
Stress tests multiplayer systems with 50+ agents joining, moving, and interacting simultaneously.

### Scenario 3: Difficulty Spike Detection
Analyzes levels with increasing difficulty to identify sections causing excessive retries or deaths.

### Scenario 4: Open-World Exploration
Tests open-world mechanics to analyze player exploration patterns and collectible discovery.

## Analytics & Reporting

The system generates three types of reports in timestamped directories within the `reports/` folder:

1. **Structured Report** (`structured_report.json`): Complete JSON data for programmatic analysis
2. **Human-Readable Report** (`human_readable_report.txt`): Plain text summary suitable for human review
3. **LLM Summary** (`llm_summary.json`): Concise data formatted for language model processing

### Analytics Features
- Heatmap generation showing agent activity in game environments
- Difficulty spike analysis identifying frustrating sections
- Engagement metrics tracking player interest
- Behavioral pattern analysis identifying common paths and actions
- Performance indicators for multiplayer systems

## Examples

### Example Usage in Code
```python
from src.agents.agent_manager import AgentManager
from src.analytics.analytics_engine import AnalyticsEngine

# Initialize the system
analytics = AnalyticsEngine()
agent_manager = AgentManager(
    game_path="/path/to/game.exe",
    num_agents=10,
    duration=300,  # 5 minutes
    analytics_engine=analytics
)

# Run playtesting
results = agent_manager.run_playtesting()

# Generate reports
from src.reporting.report_generator import ReportGenerator
report_gen = ReportGenerator(output_dir="./reports")
report_gen.generate_comprehensive_report(results)
```

### Running Test Scenarios
```python
from src.tests.test_scenarios import TestScenarioRunner

runner = TestScenarioRunner(output_dir="./test_reports")

# Run all scenarios
all_results = runner.run_all_scenarios("/path/to/game.exe")

# Or run specific scenarios
scenario1_results = runner.run_scenario_1_softlock_detection("/path/to/game.exe")
```

## Development

### Project Structure

- `src/agents/`: Core AI agent implementation including decision-making algorithms
- `src/analytics/`: Data collection, processing, and analysis systems
- `src/reporting/`: Report generation and formatting
- `src/swarm/`: Multiplayer testing orchestration
- `src/unity_integration/`: Communication layer with Unity games
- `src/utils/`: Helper functions and utilities

### Running Tests

The system includes unit tests and integration tests:

```bash
python -c "import sys; sys.path.append('./src'); from tests.unit_tests import test_game_state, test_base_agent, test_analytics_engine; test_game_state(); test_base_agent(); test_analytics_engine(); print('All component tests passed!')"
```

### Adding New Features

1. Add new agent behaviors by extending the `BaseAgent.decide_action()` method
2. Create new analytics by extending the `AnalyticsEngine` class
3. Add new test scenarios by extending the `TestScenarioRunner` class
4. Create new Unity plugin components that follow the existing communication protocol

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation as needed
6. Submit a pull request

## License

[Add your license information here]

## Support

For support, please check the GitHub Issues page or contact the development team.
