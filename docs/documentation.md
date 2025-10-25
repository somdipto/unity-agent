# AI-Driven Playtesting System

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Components](#components)
6. [Integration with Unity](#integration-with-unity)
7. [Test Scenarios](#test-scenarios)
8. [Reporting](#reporting)
9. [Troubleshooting](#troubleshooting)

## Overview

The AI-Driven Playtesting System is an automated solution that uses AI agents to simulate player behavior, detect bugs, identify balance issues, and generate engagement metrics for Unity games.

### Key Features
- AI agents that simulate natural player behavior
- Multiplayer swarm testing with 50+ concurrent agents
- Analytics and heatmap generation for difficulty and engagement
- Structured reporting with JSON and human-readable formats
- Unity integration plugin

## Architecture

The system is composed of several key modules:

```
ai-playtesting-system/
├── src/
│   ├── agents/           # AI agent simulation
│   ├── swarm/            # Multiplayer swarm testing
│   ├── analytics/        # Data collection and analysis
│   ├── reporting/        # Report generation
│   ├── unity_integration/ # Unity communication
│   ├── utils/            # Utility functions
│   └── tests/            # Test scenarios
├── examples/             # Usage examples
├── docs/                 # Documentation
├── unity_plugin/         # Unity plugin files
├── README.md
├── requirements.txt
└── .gitignore
```

## Installation

### Prerequisites
- Python 3.8 or higher
- Unity game engine (for integration)

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd ai-playtesting-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up API keys (for LLM features):
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Usage

### Basic Playtesting
```bash
python -m src --game-path /path/to/unity/game --agents 10
```

### Multiplayer Swarm Test
```bash
python -m src --game-path /path/to/unity/game --agents 50 --multiplayer
```

### Example Code
```python
from src.tests.test_scenarios import TestScenarioRunner

# Create a test runner
runner = TestScenarioRunner(output_dir="./reports")

# Run all test scenarios
all_results = runner.run_all_scenarios("./my-game.exe")
```

## Components

### Agent System
The agent system consists of:
- `BaseAgent`: The fundamental AI agent that simulates player behavior
- `AgentManager`: Manages multiple agents running in parallel
- Behavior trees and decision-making algorithms

### Swarm Testing
For multiplayer testing:
- `SwarmOrchestrator`: Coordinates multiple agents for stress testing
- `SwarmManager`: Handles agent interactions and coordination

### Analytics Engine
Collects and processes gameplay data:
- Event logging
- Heatmap generation
- Difficulty spike analysis
- Engagement metrics

### Reporting System
Generates comprehensive reports:
- JSON structured data
- Human-readable summaries
- LLM-based assessments

## Integration with Unity

The system integrates with Unity via a socket-based communication protocol:

1. Add the Unity plugin code to your Unity project (see `unity_plugin/` directory)
2. Configure the connection settings (default host: localhost, port: 8080)
3. Build your Unity game with the plugin included
4. Run the AI playtesting system against the built executable

The Unity plugin provides:
- Action execution commands
- Game state queries
- Real-time communication with AI agents
- Performance optimization settings

## Test Scenarios

The system includes four main test scenarios as specified in the requirements:

### Scenario 1: Softlock Detection
- Single-player platformer level with hidden softlock
- Agents identify stuck states and navigation issues

### Scenario 2: Multiplayer Stress Test
- 50+ agents joining, moving, and interacting simultaneously
- Stress tests networked multiplayer systems

### Scenario 3: Difficulty Spike Detection
- Levels with increasing difficulty
- Agents flag retry-heavy sections as frustration points

### Scenario 4: Open-World Exploration
- Agents find collectibles in open-world environments
- Reports include pacing, completion rate, and engagement metrics

## Reporting

### Output Formats
The system generates reports in multiple formats:

1. **JSON Reports**: Structured data for programmatic analysis
2. **Human-Readable Reports**: Plain text summaries of findings
3. **LLM Summaries**: Condensed data for language model processing

### Report Contents
Each report includes:
- Test session metadata
- Individual agent results
- Aggregated metrics
- Detected issues and anomalies
- Difficulty analysis
- Engagement assessment

### Heatmaps
Visual heatmaps show:
- Agent activity patterns
- Difficulty level distribution
- Engagement level distribution
- Combined metrics visualization

## Troubleshooting

### Common Issues

#### Connection Issues with Unity
- Ensure the Unity plugin is properly integrated
- Check that the correct host and port are configured
- Verify that Unity is built with the plugin included

#### Performance Issues
- Reduce the number of agents if performance degrades
- Lower Unity rendering quality during testing
- Close other applications to free up system resources

#### API Key Issues
- Ensure OPENAI_API_KEY environment variable is set
- Check that the API key has sufficient quota

### Support
For additional support, please contact the development team or submit an issue on the repository.

## Evaluation Approach

Our implementation addresses the key requirements and challenges outlined in the bounty:

### Subjectivity of Fun
- We quantify engagement through measurable metrics (retry rates, time spent, death counts)
- LLMs augment these metrics with qualitative assessment

### False Positives
- Differentiate between intentional design elements and actual bugs through behavioral analysis
- Context-aware detection algorithms

### Complex Mechanics
- Modular architecture allows for domain-specific agent behaviors
- Extensible decision-making system

The system provides a balance of automation and human insight, capturing both quantitative metrics and qualitative assessments for comprehensive playtesting.