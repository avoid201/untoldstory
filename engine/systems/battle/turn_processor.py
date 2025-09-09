"""
Turn Processor - Handles Turn Management
Manages turn order, execution, and turn-based logic
"""

import logging
from typing import List, Optional, Dict, Any, TYPE_CHECKING

from engine.systems.battle.battle_enums import BattlePhase, BattleResult
from engine.systems.battle.turn_logic import BattleAction, TurnOrder
from engine.systems.battle.event_processor import EventType

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.battle.action_processor import ActionProcessor

logger = logging.getLogger(__name__)


class TurnProcessor:
    """
    Manages only turns and their execution.
    Handles turn order, execution, and turn-based logic.
    """
    
    def __init__(self, battle_state: 'BattleState'):
        """Initialize turn processor with battle state."""
        self.state = battle_state
        self.turn_count = 0
        self.current_phase = BattlePhase.INIT
        self.turn_order = TurnOrder()
        self.action_processor = None  # Will be injected by BattleController
    
    def set_action_processor(self, action_processor: 'ActionProcessor') -> None:
        """Set the action processor for turn execution."""
        self.action_processor = action_processor
        logger.info("ActionProcessor connected to TurnProcessor")
    
    def start_turn(self) -> None:
        """
        Start a new turn.
        Increments turn count and sets phase to INPUT.
        """
        try:
            self.turn_count += 1
            self.current_phase = BattlePhase.INPUT
            self.state.turn_count = self.turn_count
            self.state.phase = self.current_phase
            
            logger.info(f"Starting turn {self.turn_count}")
            
        except Exception as e:
            logger.error(f"Error starting turn: {e}")
            raise
    
    def execute_turn(self, actions: List[BattleAction]) -> BattleResult:
        """Execute turn with full event support."""
        try:
            # EMIT TURN_START - KONSOLIDIERT (nur hier, nicht im battle_controller)
            if hasattr(self.state, 'event_processor') and self.state.event_processor:
                self.state.event_processor.emit_event(
                    EventType.TURN_START,
                    {
                        'turn': self.turn_count, 
                        'action_count': len(actions),
                        'player_action': actions[0].action_type.value if len(actions) > 0 else None,
                        'enemy_action': actions[1].action_type.value if len(actions) > 1 else None
                    }
                )
            
            # Sort and execute actions
            self.turn_order.clear()
            for action in actions:
                self.turn_order.add_action(action)
            
            sorted_actions = self.turn_order.sort_actions(use_dqm_formula=True)
            
            for action in sorted_actions:
                # CRITICAL FIX: Check if target is still alive before executing
                if action.target and action.target.current_hp <= 0:
                    logger.info(f"Skipping action - target {action.target.name} already fainted")
                    continue
                
                # Execute with event emission
                if self.action_processor:
                    result = self.action_processor.execute_action(action)
                    
                    # EMIT ACTION_COMPLETE
                    if hasattr(self.state, 'event_processor') and self.state.event_processor:
                        self.state.event_processor.emit_event(
                            EventType.ACTION_COMPLETE,
                            {'action': action.action_type.name, 'result': result}
                        )
                
                # CRITICAL FIX: Check if defender fainted after attack
                if (result.get('type') == 'attack' and 
                    action.target and 
                    action.target.current_hp <= 0):
                    logger.info(f"Target {action.target.name} fainted after attack")
                    self._handle_monster_faint(action.target)
                    break  # Skip remaining actions
                
                # Battle-End-Prüfung erfolgt nur am Ende des Turns
            
            # Process turn end effects
            self.process_turn_end()
            
            # Battle-End-Prüfung am Ende des Turns
            battle_result = self.check_battle_end()
            
            # EMIT TURN_END - KONSOLIDIERT (nur hier, nicht im battle_controller)
            if hasattr(self.state, 'event_processor') and self.state.event_processor:
                self.state.event_processor.emit_event(
                    EventType.TURN_END,
                    {
                        'turn': self.turn_count,
                        'battle_result': battle_result.value if battle_result else None
                    }
                )
            
            return battle_result
        except Exception as e:
            logger.error(f"Turn execution failed: {e}")
            return BattleResult.ONGOING
    
    def process_turn_end(self) -> None:
        """
        Process end-of-turn effects.
        Handles status effects, stat changes, etc.
        """
        try:
            logger.debug("Processing turn end effects")
            
            # Process status effects for all active monsters
            for monster in [self.state.player_active, self.state.enemy_active]:
                if monster and hasattr(monster, 'status_manager'):
                    messages = monster.status_manager.process_turn_start()
                    for message in messages:
                        self.state.battle_log.append(message)
                        
                        # EMIT STATUS EVENT if EventProcessor is available
                        if hasattr(self.state, 'event_processor') and self.state.event_processor:
                            # Create BattleEvent properly
                            from engine.systems.battle.event_processor import BattleEvent
                            status_event = BattleEvent(
                                event_type=EventType.STATUS_DAMAGE,
                                data={
                                    "monster": monster.name,
                                    "message": message,
                                    "status": getattr(monster, 'status_condition', None)
                                }
                            )
                            self.state.event_processor.emit_event(status_event)
            
            # Process field effects, weather, etc.
            # This would be implemented based on specific game mechanics
            
            logger.debug("Turn end effects processed")
            
        except Exception as e:
            logger.error(f"Error processing turn end: {e}")
    
    def check_battle_end(self) -> BattleResult:
        """
        Check if the battle has ended.
        
        Returns:
            BattleResult.ONGOING if battle continues, specific result if ended
        """
        try:
            # Check if player team is defeated
            player_has_conscious = any(monster.current_hp > 0 for monster in self.state.player_team)
            
            if not player_has_conscious:
                logger.info("Player team defeated")
                self.state.battle_result = BattleResult.DEFEAT
                self.state.battle_ended = True
                return BattleResult.DEFEAT
            
            # Check if enemy team is defeated
            enemy_has_conscious = any(monster.current_hp > 0 for monster in self.state.enemy_team)
            
            if not enemy_has_conscious:
                logger.info("Enemy team defeated")
                self.state.battle_result = BattleResult.VICTORY
                self.state.battle_ended = True
                return BattleResult.VICTORY
            
            # Check for caught monster (if applicable)
            if hasattr(self.state, 'caught_monster') and self.state.caught_monster:
                logger.info("Monster caught")
                self.state.battle_result = BattleResult.CAUGHT
                self.state.battle_ended = True
                return BattleResult.CAUGHT
            
            # Check for fled battle (if applicable)
            if hasattr(self.state, 'fled') and self.state.fled:
                logger.info("Battle fled")
                self.state.battle_result = BattleResult.FLED
                self.state.battle_ended = True
                return BattleResult.FLED
            
            # Battle continues
            return BattleResult.ONGOING
            
        except Exception as e:
            logger.error(f"Error checking battle end: {e}")
            # Return ONGOING on error
            return BattleResult.ONGOING
    
    def increment_turn(self) -> None:
        """
        Increment turn counter.
        Called after turn execution is complete.
        """
        try:
            # Turn count is already incremented in start_turn()
            # This method is for any additional turn increment logic
            logger.debug(f"Turn {self.turn_count} completed")
            
        except Exception as e:
            logger.error(f"Error incrementing turn: {e}")
    
    def get_turn_info(self) -> Dict[str, Any]:
        """Get current turn information."""
        return {
            'turn_count': self.turn_count,
            'phase': self.current_phase.value,
            'battle_ended': self.state.battle_ended,
            'battle_result': self.state.battle_result.value if self.state.battle_result else None
        }
    
    def _transition_to_input_phase(self, battle_state: 'BattleState') -> None:
        """
        Transition from START phase to INPUT phase.
        """
        try:
            if battle_state.phase == BattlePhase.START:
                battle_state.phase = BattlePhase.INPUT
                battle_state.waiting_for_input = True
                self.current_phase = BattlePhase.INPUT
                
                # EMIT PHASE_CHANGE Event
                if hasattr(battle_state, 'event_processor') and battle_state.event_processor:
                    battle_state.event_processor.emit_event(
                        EventType.PHASE_CHANGE,
                        {
                            'old_phase': BattlePhase.START.value,
                            'new_phase': BattlePhase.INPUT.value,
                            'turn': self.turn_count
                        }
                    )
                
                logger.info("✓ TurnProcessor: Battle phase transitioned START → INPUT")
            else:
                logger.warning(f"Unexpected phase transition from {battle_state.phase.value} to INPUT")
                
        except Exception as e:
            logger.error(f"Error transitioning to INPUT phase: {e}")
            # Fallback: Force INPUT phase
            battle_state.phase = BattlePhase.INPUT
            battle_state.waiting_for_input = True
            self.current_phase = BattlePhase.INPUT
    
    def reset_turn_state(self) -> None:
        """Reset turn state for new battle."""
        try:
            self.turn_count = 0
            self.current_phase = BattlePhase.INIT
            self.turn_order.clear()
            logger.debug("Turn state reset")
            
        except Exception as e:
            logger.error(f"Error resetting turn state: {e}")
    
    def initialize_battle(self, battle_state: 'BattleState') -> Dict[str, Any]:
        """
        Initialize battle state for new battle.
        
        Args:
            battle_state: The battle state to initialize
            
        Returns:
            Dict with success status and message
        """
        try:
            # Reset turn count to 0
            self.turn_count = 0
            
            # Set phase to START
            self.current_phase = BattlePhase.START
            battle_state.phase = self.current_phase
            
            # Clear turn order
            self.turn_order.clear()
            
            # Automatischer Übergang START → INPUT
            self._transition_to_input_phase(battle_state)
            
            # Log initialization
            logger.info("Battle initialized - TurnProcessor ready")
            
            return {
                'success': True, 
                'message': 'Battle initialized'
            }
            
        except Exception as e:
            logger.error(f"Error initializing battle: {e}")
            return {
                'success': False,
                'message': f'Failed to initialize battle: {e}'
            }
    
    def _handle_monster_faint(self, monster: 'MonsterInstance') -> None:
        """
        Handle monster faint event.
        
        Args:
            monster: The monster that fainted
        """
        try:
            logger.info(f"Monster {monster.name} fainted")
            
            # Set monster as fainted
            monster.current_hp = 0
            
            # EMIT MONSTER_FAINTED Event
            if hasattr(self.state, 'event_processor') and self.state.event_processor:
                self.state.event_processor.emit_event(
                    EventType.MONSTER_FAINTED,
                    {
                        'monster': monster,
                        'monster_name': monster.name,
                        'message': f"{monster.name} ist ohnmächtig geworden!"
                    }
                )
            
            # Add to battle log
            if hasattr(self.state, 'battle_log'):
                self.state.battle_log.append(f"{monster.name} ist ohnmächtig geworden!")
            
        except Exception as e:
            logger.error(f"Error handling monster faint: {e}")
    
    def process_enemy_turn(self, battle_state: 'BattleState') -> Dict[str, Any]:
        """
        Process enemy turn by getting AI action.
        
        Args:
            battle_state: Current battle state
            
        Returns:
            Dict containing enemy action data
        """
        try:
            # Import BattleAI here to avoid circular imports
            from engine.systems.battle.battle_ai import BattleAI
            
            # Get active monsters
            enemy_active = battle_state.enemy_active
            player_active = battle_state.player_active
            
            if not enemy_active:
                logger.warning("No enemy active monster for AI turn")
                return {
                    'success': False,
                    'message': 'No enemy active monster'
                }
            
            # Create AI instance and choose action
            ai = BattleAI()
            action = ai.choose_action(
                enemy_monster=enemy_active,
                player_monster=player_active,
                battle_state=battle_state
            )
            
            # Convert result to dict if it's a BattleAction
            if hasattr(action, 'to_dict'):
                action_dict = action.to_dict()
            else:
                # Fallback for non-BattleAction results
                action_dict = {
                    'action_type': 'attack',
                    'actor': enemy_active.name,
                    'target': player_active.name if player_active else 'unknown'
                }
            
            logger.debug(f"Enemy AI chose action: {action_dict}")
            
            return {
                'success': True,
                'action': action_dict,
                'message': 'Enemy action generated'
            }
            
        except Exception as e:
            logger.error(f"Error processing enemy turn: {e}")
            return {
                'success': False,
                'message': f'Failed to process enemy turn: {e}'
            }