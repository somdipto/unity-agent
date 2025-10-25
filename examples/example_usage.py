"""
Example script demonstrating how to run the AI playtesting system
"""
import os
import sys
from src.tests.test_scenarios import TestScenarioRunner


def main():
    # Example game path - in practice, this would be the path to a Unity executable
    game_path = "./example_unity_game.exe"  # This is just an example
    
    # Create test scenario runner
    runner = TestScenarioRunner(output_dir="./example_reports")
    
    print("AI Playtesting System - Example Usage")
    print("=" * 40)
    
    # Option 1: Run all scenarios
    print("\nOption 1: Running all test scenarios...")
    all_results = runner.run_all_scenarios(game_path)
    
    # Option 2: Run specific scenarios
    print("\nOption 2: Running specific scenarios...")
    
    # Uncomment these lines to run individual scenarios:
    # runner.run_scenario_1_softlock_detection(game_path)
    # runner.run_scenario_2_multiplayer_stress(game_path)
    # runner.run_scenario_3_difficulty_spike(game_path)
    # runner.run_scenario_4_open_world_exploration(game_path)
    
    print("\nReports have been generated in the 'example_reports' directory.")
    print("Each scenario produces its own detailed report and analysis.")


if __name__ == "__main__":
    main()