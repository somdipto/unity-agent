<div align="center">

<h1>Unity‑Agent</h1>

<p><b>AI‑Driven Playtesting for Unity</b> — simulate players, find bugs, balance difficulty, and auto‑generate actionable reports with LLM-powered insights.</p>

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-%E2%89%A53.8-3776AB?logo=python&logoColor=white" />
  <img alt="Unity" src="https://img.shields.io/badge/Unity-Integration-000?logo=unity&logoColor=white" />
  <img alt="Platforms" src="https://img.shields.io/badge/Platforms-Windows%20%7C%20macOS%20%7C%20Linux-6E56CF" />
  <img alt="Status" src="https://img.shields.io/badge/Status-Active-success" />
  <img alt="Updated" src="https://img.shields.io/badge/Updated-2025--11--28-blue" />
</p>

</div>

---

- **Blazing‑fast Swarm Testing:** Orchestrate 50+ concurrent agents 🐜
- **Real-time Analytics:** Automatic anomaly, soft‑lock, and difficulty spike detection 🧭
- **Visual Insights:** Heatmaps, engagement metrics, and player flow analysis 📊
- **AI Game Critic:** LLM-powered "Fun Factor" assessment and narrative reviews 🧠
- **Robust Architecture:** Thread-safe analytics and optimized networking 🛡️

## Quickstart

```bash
# clone
git clone https://github.com/somdipto/unity-agent.git
cd unity-agent

# install dependencies
pip install -r requirements.txt

# run single‑player test (5 agents for 5 minutes)
python -m src.__main__ --game-path /path/to/game.exe --agents 5 --duration 300

# run with AI Critic enabled (requires OpenAI API Key)
python -m src.__main__ --game-path /path/to/game.exe --agents 10 --duration 300 --api-key sk-your-key-here
```

## Features

- 🤖 **AI Agents:** Naturalistic behavior modeling with distinct personalities (Cautious, Aggressive, Speedrunner, etc.).
- 🐜 **Swarm Orchestrator:** Scalable, multi-threaded control for multiplayer stress testing.
- 🧠 **Analytics Engine:** Thread-safe collection of engagement, difficulty, and pathing metrics.
- 📝 **AI Game Critic:** Uses OpenAI to generate qualitative feedback:
    - **Fun Assessment:** Scores the game's engagement level (1-10).
    - **Actionable Suggestions:** Proposes specific design fixes.
    - **Narrative Reports:** Writes a "review" of the session from the agent's perspective.
- 🔌 **Unity Plugin:** Optimized C# connector using efficient JSON/TCP communication.

## Architecture

The system uses a synchronous, multi-threaded architecture to manage agents, while utilizing a thread-safe Analytics Engine for data aggregation.

```mermaid
flowchart TB
  subgraph Unity["Unity Game Process"]
    PC[PythonConnector.cs]
    WS[WebSocketServer.cs]
    PH[PlayerHealth.cs]
    CM[CombatManager.cs]
    OT[ObjectiveTracker.cs]
  end
  
  subgraph Python["Python AI System"]
    Main[__main__.py]
    
    subgraph Integration["unity_integration/"]
      UC[unity_connector.py]
      UIM[unity_integration_manager.py]
    end
    
    subgraph Agents["agents/"]
      AM[agent_manager.py]
      BA[base_agent.py]
      PERS[personalities.py]
    end
    
    subgraph Swarm["swarm/"]
      SO[swarm_orchestrator.py]
    end
    
    subgraph Analytics["analytics/"]
      AE[analytics_engine.py]
      RD[realtime_detector.py]
      HM[heatmap_generator.py]
    end
    
    subgraph Reporting["reporting/"]
      RG[report_generator.py]
      LA[llm_analyzer.py]
    end
    
    subgraph Utils["utils/"]
      GS[game_state.py]
      CF[config.py]
    end
  end
  
  Output[(reports/)]
  OpenAI[OpenAI API]
  
  PC <-->|JSON/TCP| UC
  WS <-->|WebSocket| UC
  UC --> UIM
  
  Main --> AM
  Main --> SO
  Main --> AE
  Main --> RG
  Main --> LA
  
  AM --> UIM
  AM --> BA
  SO --> UIM
  SO --> BA
  
  BA -->|Thread-Safe Locks| AE
  BA --> PERS
  BA --> GS
  
  UIM --> UC
  UIM --> AE
  
  AE --> RD
  AE --> HM
  AE --> GS
  
  RG --> AE
  RG --> LA
  LA -->|API Calls| OpenAI
  
  RG --> Output
  
  CF -.->|Config| UC
  CF -.->|Config| LA
```

## Command Line Options

```
--game-path PATH       Path to the Unity game executable (Required)
--agents NUM           Number of AI agents to simulate (default: 1)
--multiplayer          Enable multiplayer swarm mode
--duration SECONDS     Test duration in seconds (default: 300)
--output PATH          Output directory for reports (default: ./reports)
--api-key KEY          OpenAI API Key for qualitative analysis (Optional)
```

## Unity Integration

1.  **Install Scripts:** Drop the C# scripts from `unity_plugin/Assets/Scripts/` into your Unity project.
2.  **Setup Connector:** Attach `PythonConnector.cs` to a persistent scene object (e.g., GameManager).
3.  **Configure Game:** Ensure standard components (`PlayerHealth`, `CombatManager`, etc.) are accessible to the connector.

## Reports

Reports are generated in timestamped folders under `./reports/`:

*   `human_readable_report.txt`: A concise summary for developers.
*   `structured_report.json`: Raw metrics for external tools.
*   `llm_insights.json`: (Optional) Qualitative analysis including Fun Score and Suggestions.

## Development

Run component tests:

```bash
export PYTHONPATH=$PYTHONPATH:.
python -c "from src.tests.unit_tests import test_game_state, test_base_agent, test_analytics_engine; test_game_state(); test_base_agent(); test_analytics_engine(); print('All component tests passed!')"
```

## Contributing

1.  Fork the repository.
2.  Create a feature branch.
3.  Submit a Pull Request.