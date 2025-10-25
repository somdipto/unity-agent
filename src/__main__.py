"""
Main entry point for the AI-Driven Playtesting System
"""
import argparse
from src.agents.agent_manager import AgentManager
from src.swarm.swarm_orchestrator import SwarmOrchestrator
from src.analytics.analytics_engine import AnalyticsEngine
from src.reporting.report_generator import ReportGenerator


def main():
    parser = argparse.ArgumentParser(description="AI-Driven Playtesting System")
    parser.add_argument("--game-path", required=True, help="Path to the Unity game executable")
    parser.add_argument("--agents", type=int, default=1, help="Number of AI agents to simulate")
    parser.add_argument("--multiplayer", action="store_true", help="Run multiplayer swarm test")
    parser.add_argument("--duration", type=int, default=300, help="Test duration in seconds")
    parser.add_argument("--output", default="./reports", help="Output directory for reports")
    
    args = parser.parse_args()
    
    print(f"Starting AI playtesting for game: {args.game_path}")
    print(f"Number of agents: {args.agents}")
    print(f"Duration: {args.duration} seconds")
    
    try:
        # Initialize components
        analytics_engine = AnalyticsEngine()
        report_generator = ReportGenerator(output_dir=args.output)
        
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