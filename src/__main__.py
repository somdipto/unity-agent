"""
Main entry point for the AI-Driven Playtesting System
"""
import argparse
import os
from src.agents.agent_manager import AgentManager
from src.swarm.swarm_orchestrator import SwarmOrchestrator
from src.analytics.analytics_engine import AnalyticsEngine
from src.reporting.report_generator import ReportGenerator
from src.reporting.llm_analyzer import LLMAnalyzer


def main():
    parser = argparse.ArgumentParser(description="AI-Driven Playtesting System")
    parser.add_argument("--game-path", required=True, help="Path to the Unity game executable")
    parser.add_argument("--agents", type=int, default=1, help="Number of AI agents to simulate")
    parser.add_argument("--multiplayer", action="store_true", help="Run multiplayer swarm test")
    parser.add_argument("--duration", type=int, default=300, help="Test duration in seconds")
    parser.add_argument("--output", default="./reports", help="Output directory for reports")
    parser.add_argument("--api-key", help="OpenAI API Key for qualitative analysis")
    
    args = parser.parse_args()
    
    print(f"Starting AI playtesting for game: {args.game_path}")
    print(f"Number of agents: {args.agents}")
    print(f"Duration: {args.duration} seconds")
    
    try:
        # Initialize components
        analytics_engine = AnalyticsEngine()
        
        # Initialize LLM Analyzer
        llm_analyzer = None
        api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
        
        if api_key:
            print("LLM Analysis: ENABLED (API Key detected)")
            llm_analyzer = LLMAnalyzer(api_key=api_key)
        else:
            # Try to init without explicit key (might pick up from internal config)
            try:
                analyzer_candidate = LLMAnalyzer()
                # Check if it actually found a key in config
                import openai
                if openai.api_key:
                    print("LLM Analysis: ENABLED (Config Key detected)")
                    llm_analyzer = analyzer_candidate
                else:
                    print("LLM Analysis: DISABLED (No API Key provided)")
            except Exception:
                 print("LLM Analysis: DISABLED (Initialization failed)")

        report_generator = ReportGenerator(output_dir=args.output, llm_analyzer=llm_analyzer)
        
        if args.multiplayer:
            # Run swarm test
            print("Running multiplayer swarm test...")
            swarm_orchestrator = SwarmOrchestrator(
                game_path=args.game_path,
                num_agents=args.agents,
                duration=args.duration,
                analytics_engine=analytics_engine
            )
            results = swarm_orchestrator.run_swarm_test()
        else:
            # Run single-player test
            print("Running single-player test...")
            agent_manager = AgentManager(
                game_path=args.game_path,
                num_agents=args.agents,
                duration=args.duration,
                analytics_engine=analytics_engine
            )
            results = agent_manager.run_playtesting()
        
        # Generate reports
        report_generator.generate_comprehensive_report(results)
        print(f"Playtesting completed successfully. Reports generated in {args.output}")
        
    except KeyboardInterrupt:
        print("\nPlaytesting interrupted by user.")
        exit(1)
    except FileNotFoundError:
        print(f"Error: Game file not found at {args.game_path}")
        exit(1)
    except Exception as e:
        print(f"An error occurred during playtesting: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()