# AI Playtesting System Demo

This demo showcases the capabilities of the AI-driven playtesting system.

## Setup

To run the demo, you'll need:

1. Python 3.8+
2. Install dependencies: `pip install -r requirements.txt`
3. A Unity game with the AI playtesting plugin installed (see documentation)

## Running the Demo

The demo includes several examples of the system in action:

### 1. Basic Playtesting
```bash
# Run with a simple game and 5 agents
python -m src --game-path ./example_game.exe --agents 5 --duration 300
```

### 2. Multiplayer Swarm Test
```bash
# Stress test with 50 agents
python -m src --game-path ./multiplayer_game.exe --agents 50 --multiplayer --duration 600
```

### 3. Running Test Scenarios
The system includes 4 specific test scenarios:

- **Scenario 1**: Softlock Detection - Detects when players get stuck
- **Scenario 2**: Multiplayer Stress - Tests with 50+ concurrent agents
- **Scenario 3**: Difficulty Spikes - Identifies frustrating challenge points
- **Scenario 4**: Exploration Analysis - Tracks player movement and engagement

To run all scenarios:
```python
from src.tests.test_scenarios import TestScenarioRunner

runner = TestScenarioRunner(output_dir="./demo_reports")
all_results = runner.run_all_scenarios("./your_game.exe")
```

## What You'll See

When you run the demo:

1. **AI Agents in Action**: Watch as AI agents navigate your game, making decisions and interacting with game elements
2. **Real-time Analytics**: Metrics updating as agents explore and play
3. **Issue Detection**: The system identifying potential problems like softlocks or difficulty spikes
4. **Heatmaps**: Visualizations of agent activity and engagement across game areas
5. **Comprehensive Reports**: Structured JSON and human-readable reports with findings

## Sample Output

After running the demo, you'll find reports in the `demo_reports/` directory:

- `structured_report.json` - Detailed metrics and data
- `human_readable_report.txt` - Plain text summary
- `llm_summary.json` - Input for language model assessment
- `heatmap.png` - Visual activity map of agent movements
- Individual scenario reports

## Next Steps

1. Try the demo with your own Unity game
2. Customize agent behaviors for your specific game mechanics
3. Integrate the system into your CI/CD pipeline
4. Use the API to programmatically trigger playtesting sessions

For more details, see the full documentation in the `docs/` directory.