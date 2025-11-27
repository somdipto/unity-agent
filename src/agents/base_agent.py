"""
Base Agent - The fundamental AI agent that interacts with the game
"""
import time
import random
from enum import Enum
from typing import Dict, Any, List
from ..utils.game_state import GameState
from ..analytics.analytics_engine import AnalyticsEngine


class AgentPersonality(Enum):
    CAUTIOUS = "cautious"
    AGGRESSIVE = "aggressive" 
    RANDOM = "random"
    SPEEDRUNNER = "speedrunner"


class BaseAgent:
    """
    Base AI agent that simulates player behavior in games
    """
    
    def __init__(self, agent_id: int, game_path: str, analytics_engine: AnalyticsEngine, 
                 unity_manager=None, personality: AgentPersonality = None):
        self.agent_id = agent_id
        self.game_path = game_path
        self.analytics_engine = analytics_engine
        self.unity_manager = unity_manager
        self.game_state = GameState()
        self.is_running = False
        
        # Assign personality if not provided
        if personality is None:
            personalities = list(AgentPersonality)
            self.personality = personalities[agent_id % len(personalities)]
        else:
            self.personality = personality
            
        # Adjust behavior parameters based on personality
        self._set_personality_traits()
        
        self.results: Dict[str, Any] = {
            'agent_id': agent_id,
            'personality': self.personality.value,
            'actions': [],
            'time_spent': 0,
            'retries': 0,
            'deaths': 0,
            'level_progress': 0,
            'issues_detected': [],
            'engagement_metrics': {}
        }
        
    def _set_personality_traits(self):
        """Set behavior parameters based on agent personality"""
        if self.personality == AgentPersonality.CAUTIOUS:
            self.exploration_bias = 0.3
            self.caution_level = 0.9
            self.focus_duration = 10
        elif self.personality == AgentPersonality.AGGRESSIVE:
            self.exploration_bias = 0.8
            self.caution_level = 0.2
            self.focus_duration = 3
        elif self.personality == AgentPersonality.RANDOM:
            self.exploration_bias = random.uniform(0.1, 0.9)
            self.caution_level = random.uniform(0.1, 0.9)
            self.focus_duration = random.randint(1, 8)
        elif self.personality == AgentPersonality.SPEEDRUNNER:
            self.exploration_bias = 0.1
            self.caution_level = 0.3
            self.focus_duration = 2
        
    def run(self):
        """Main execution loop for the agent"""
        self.is_running = True
        start_time = time.time()
        # Cache start_time to avoid repeated function calls
        session_start_time = start_time
        
        print(f"Agent {self.agent_id} starting playtesting...")
        
        try:
            while self.is_running:
                try:
                    # Update game state from Unity
                    self.update_game_state()
                    
                    # Decide next action based on game state
                    action = self.decide_action()
                    
                    # Execute action in the game
                    self.execute_action(action)
                    
                    # Cache current time to avoid multiple calls
                    current_time = time.time()
                    
                    # Log the action - using more efficient data structure
                    self.results['actions'].append((
                        current_time - session_start_time,  # timestamp
                        action,
                        self.game_state.to_dict()
                    ))
                    
                    # Check for anomalies and issues
                    self.detect_anomalies()
                    
                except Exception as e:
                    print(f"Error in agent {self.agent_id} during execution: {str(e)}")
                    # Add error to results for reporting
                    current_time = time.time()
                    error_record = (
                        current_time - session_start_time,  # timestamp
                        str(e),
                        self.game_state.to_dict()
                    )
                    self.results['actions'].append(error_record)
                
                # Small delay to simulate realistic input timing
                time.sleep(0.1)
        except KeyboardInterrupt:
            print(f"Agent {self.agent_id} interrupted by user")
        except Exception as e:
            print(f"Critical error in agent {self.agent_id}: {str(e)}")
        finally:
            self.results['time_spent'] = time.time() - session_start_time
            print(f"Agent {self.agent_id} finished playtesting")
    
    def update_game_state(self):
        """Update the agent's understanding of the current game state"""
        try:
            if self.unity_manager:
                # Get the actual game state from Unity
                unity_state = self.unity_manager.get_game_state(self.agent_id)
                self.game_state.update_from_unity(unity_state)
            else:
                # Fallback to simulation if Unity is not available
                self.game_state.update_from_game()
        except Exception as e:
            print(f"Error updating game state for agent {self.agent_id}: {str(e)}")
            # Still update time to prevent issues
            import time
            self.game_state.time_in_level = time.time()
            # Add to tracking list to prevent stuck detection issues
            self.game_state.previous_positions.append(self.game_state.position)
            if len(self.game_state.previous_positions) > self.game_state.max_stuck_positions:
                self.game_state.previous_positions.pop(0)
    
    def decide_action(self) -> str:
        """Decide what action to take based on current game state"""
        # Get the current behavioral context
        context = self.game_state.get_current_behavior_context()
        
        # Determine possible actions based on context
        possible_actions = self._get_actions_for_context(context)
        
        # Adjust based on agent parameters and game state
        action = self._select_action_with_strategy(possible_actions, context)
        
        return action
    
    def _get_actions_for_context(self, context: str) -> list:
        """Get appropriate actions for the current behavioral context"""
        base_actions = [
            'move_forward', 'move_backward', 'jump', 'crouch', 
            'interact', 'look_around'
        ]
        
        if context == "combat":
            combat_actions = ['attack', 'defend', 'dodge', 'move_forward', 'move_backward']
            return base_actions + combat_actions
        elif context == "puzzle":
            puzzle_actions = ['interact', 'examine', 'think', 'look_around']
            return base_actions + puzzle_actions
        elif context == "critical_health":
            survival_actions = ['defend', 'move_backward', 'crouch', 'interact']  # Maybe interact with health items
            return base_actions + survival_actions
        elif context == "stuck":
            navigation_actions = ['jump', 'move_backward', 'crouch', 'look_around']
            return base_actions + navigation_actions
        elif context == "frustrated":
            patience_actions = ['think', 'look_around', 'interact', 'crouch']  # Take a break, look for alternatives
            return base_actions + patience_actions
        elif context == "exploring":
            exploration_actions = ['move_forward', 'look_around', 'interact', 'jump']
            return base_actions + exploration_actions
        elif context == "goal_oriented":
            goal_actions = ['move_forward', 'interact', 'attack']  # Push toward objective
            return base_actions + goal_actions
        else:
            # Default actions for idle or other states
            return base_actions
    
    def _select_action_with_strategy(self, possible_actions: list, context: str) -> str:
        """Select an action using different strategies based on context and parameters"""
        # Adjust strategy based on the agent's caution level and other factors
        if context == "critical_health" or context == "frustrated":
            # In critical situations, be more cautious
            if random.random() < self.caution_level:
                cautious_actions = [action for action in possible_actions if 'aggressive' not in action]
                cautious_actions = [a for a in cautious_actions if a not in ['attack', 'move_forward', 'jump']]
                if cautious_actions:
                    return random.choice(cautious_actions)
        
        elif context == "combat":
            # In combat, balance aggression with defense based on health
            if self.game_state.health < 50:  # If health is low
                defensive_actions = [a for a in possible_actions if a in ['defend', 'dodge', 'move_backward']]
                if defensive_actions and random.random() < 0.7:  # 70% chance of defensive action
                    return random.choice(defensive_actions)
            else:
                aggressive_actions = [a for a in possible_actions if a in ['attack', 'move_forward']]
                if aggressive_actions and random.random() < 0.6:  # 60% chance of aggressive action
                    return random.choice(aggressive_actions)
        
        # Add more sophisticated selection based on exploration bias
        if random.random() < self.exploration_bias:
            # Exploration-focused selection
            exploration_favorable = [a for a in possible_actions if a in ['move_forward', 'look_around', 'interact']]
            if exploration_favorable:
                # Higher chance of exploration actions when in exploration mode
                if random.random() < 0.7:
                    return random.choice(exploration_favorable)
        
        # Default: random selection from possible actions
        return random.choice(possible_actions)
    
    def pursue_objective(self) -> str:
        """Determine action based on current game objective"""
        objective = self.game_state.current_objective
        
        if not objective:
            # If somehow called without an objective, explore
            return 'move_forward'
        
        # Map objectives to actions - this would be expanded based on specific games
        objective_lower = objective.lower()
        
        if any(keyword in objective_lower for keyword in ['defeat', 'kill', 'eliminate', 'attack']):
            if self.game_state.in_combat:
                return 'attack' if random.random() < 0.7 else 'defend'
            else:
                return 'move_forward'  # Move toward enemies
        elif any(keyword in objective_lower for keyword in ['explore', 'find', 'locate', 'discover']):
            # For exploration objectives, more random movement
            exploration_actions = ['move_forward', 'look_around', 'interact']
            return random.choice(exploration_actions)
        elif any(keyword in objective_lower for keyword in ['collect', 'gather', 'pickup', 'obtain']):
            # For collection objectives, focus on interaction
            if 'interact' in self._get_actions_for_context('goal_oriented'):
                return 'interact'
            else:
                return 'move_forward'
        elif any(keyword in objective_lower for keyword in ['reach', 'go_to', 'travel', 'get_to']):
            # For destination objectives, focus on movement
            return 'move_forward'
        elif any(keyword in objective_lower for keyword in ['solve', 'complete', 'finish', 'puzzle']):
            # For puzzle objectives
            if self.game_state.puzzle_active:
                puzzle_actions = ['interact', 'examine', 'think']
                return random.choice(puzzle_actions)
            else:
                return 'move_forward'  # Move toward puzzle if not in one
        else:
            # Default for unrecognized objectives
            return 'move_forward'
    
    def execute_action(self, action: str):
        """Execute the decided action in the game"""
        try:
            if self.unity_manager:
                # Send the action to Unity for execution
                success = self.unity_manager.send_action_to_unity(self.agent_id, action)
                if not success:
                    print(f"Failed to execute action {action} for agent {self.agent_id}")
            else:
                # Fallback to simulation if Unity is not available
                print(f"Unity not connected, simulating action: {action}")
            
            # Log engagement metrics based on action
            if action in ['attack', 'jump', 'dodge']:
                self.analytics_engine.log_high_engagement(self.agent_id, action)
            elif action in ['move_forward', 'explore']:
                self.analytics_engine.log_progression(self.agent_id, action)
            
            # Update internal state based on action
            self.handle_action_effects(action)
        except Exception as e:
            print(f"Error executing action {action} for agent {self.agent_id}: {str(e)}")
            # Still log the action to maintain consistency
            try:
                self.analytics_engine.log_agent_action(self.agent_id, action, self.game_state.to_dict())
            except:
                pass  # If logging fails, continue anyway
    
    def handle_action_effects(self, action: str):
        """Handle the consequences of an action"""
        if action == 'died':
            self.results['deaths'] += 1
            self.analytics_engine.log_agent_death(self.agent_id)
        elif action == 'retry':
            self.results['retries'] += 1
            self.analytics_engine.log_retry(self.agent_id)
    
    def detect_anomalies(self):
        """Detect potential issues in the game"""
        # Check for softlocks (agent not making progress)
        if self.game_state.is_stuck():
            issue = {
                'type': 'softlock',
                'timestamp': time.time(),
                'location': self.game_state.get_position(),
                'details': 'Agent appears to be stuck in location'
            }
            self.results['issues_detected'].append(issue)
            self.analytics_engine.log_anomaly('softlock', issue)
        
        # Check for other anomalies
        if self.game_state.is_infinite_loop():
            issue = {
                'type': 'infinite_loop',
                'timestamp': time.time(),
                'details': 'Agent detected infinite loop behavior'
            }
            self.results['issues_detected'].append(issue)
            self.analytics_engine.log_anomaly('infinite_loop', issue)
    
    def stop(self):
        """Stop the agent's execution"""
        self.is_running = False
    
    def get_results(self) -> Dict[str, Any]:
        """Get the results from this agent's playtesting session"""
        # Convert compact action tuples back to dictionary format for compatibility
        readable_actions = []
        for action_data in self.results['actions']:
            if isinstance(action_data, tuple) and len(action_data) == 3:
                # Check if second element is an error or action
                if isinstance(action_data[1], str) and 'error' in str(action_data[1]).lower():
                    # Error format: (timestamp, error, game_state)
                    readable_actions.append({
                        'timestamp': action_data[0],
                        'error': action_data[1],
                        'game_state': action_data[2]
                    })
                else:
                    # Regular action format: (timestamp, action, game_state)
                    readable_actions.append({
                        'timestamp': action_data[0],
                        'action': action_data[1],
                        'game_state': action_data[2]
                    })
            else:
                # Already in dictionary format or unknown format
                readable_actions.append(action_data)
        
        # Update results with readable format
        self.results['actions'] = readable_actions
        self.results['engagement_metrics'] = self.analytics_engine.get_agent_metrics(self.agent_id)
        return self.results