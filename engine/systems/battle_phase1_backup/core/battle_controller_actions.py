"""
Action handling methods - max 200 lines
Contains all action-related methods and battle execution logic.
"""

import logging
from typing import Dict, Any, Optional, List
from engine.systems.battle.battle_enums import BattlePhase, BattleResult
from engine.systems.battle.turn_logic import BattleAction

logger = logging.getLogger(__name__)


class BattleControllerActionsMixin:
    """
    Action handling methods extracted from main controller.
    Handles all action execution and validation.
    """
    
    def execute_turn(self, player_action, enemy_action) -> Dict[str, Any]:
        """
        Execute a complete turn with player and enemy actions.
        AGENT 4: Implements proper phase transitions: INPUT → EXECUTION → AFTERMATH → INPUT
        
        Args:
            player_action: Player action (BattleAction or dict)
            enemy_action: Enemy action (BattleAction or dict)
            
        Returns:
            Dict with turn execution result
        """
        try:
            # AGENT 4: Transition to EXECUTION phase when turn starts
            if self.state.phase == BattlePhase.INPUT:
                self._transition_to_execution_phase()
            
            # Convert to BattleAction if needed
            if isinstance(player_action, dict):
                player_battle_action = self._create_battle_action(player_action, is_player=True)
            else:
                player_battle_action = player_action
                
            if isinstance(enemy_action, dict):
                enemy_battle_action = self._create_battle_action(enemy_action, is_player=False)
            else:
                enemy_battle_action = enemy_action
            
            # Validate actions
            if not player_battle_action:
                logger.warning("Ungültige Player-Action: Failed to create BattleAction")
                return {"success": False, "error": "Invalid player action"}
            
            if not enemy_battle_action:
                logger.warning("Ungültige Enemy-Action: Failed to create BattleAction")
                return {"success": False, "error": "Invalid enemy action"}
            
            # Use TurnProcessor for proper turn execution
            if self.turn_processor:
                actions = [player_battle_action, enemy_battle_action]
                # CRITICAL FIX: Ensure actions are properly queued
                self.turn_processor.turn_order.clear()
                for action in actions:
                    self.turn_processor.turn_order.add_action(action)
                battle_result = self.turn_processor.execute_turn(actions)
                
                # AGENT 4: Transition to AFTERMATH phase after execution
                self._transition_to_aftermath_phase()
                
                # Update state with result
                if battle_result != BattleResult.ONGOING:
                    self.state.battle_ended = True
                    self.state.battle_result = battle_result
                else:
                    # AGENT 4: If battle continues, transition back to INPUT phase
                    self._transition_aftermath_to_input()
                
                # CRITICAL FIX: Sync state with UI after turn execution
                if hasattr(self, 'ui_sync_callback') and self.ui_sync_callback:
                    self.ui_sync_callback({
                        'battle_state': self.state,
                        'player_active': self.state.player_active,
                        'enemy_active': self.state.enemy_active,
                        'battle_ended': self.state.battle_ended,
                        'battle_result': battle_result.value if battle_result else None
                    })
                
                return {
                    "success": True,
                    "turn": self.state.turn_count,
                    "phase": self.state.phase.value,
                    "battle_ended": self.state.battle_ended,
                    "battle_result": self.state.battle_result.value if self.state.battle_result else None,
                    "result": {"battle_result": battle_result.value if battle_result else None}
                }
            else:
                # Fallback to old method
                self.turn_order.add_action(player_battle_action)
                self.turn_order.add_action(enemy_battle_action)
                result = self._execute_actions()
                self.state.turn_count += 1
                
                # AGENT 4: Apply phase transitions in fallback mode too
                self._transition_to_aftermath_phase()
                if not self.state.battle_ended:
                    self._transition_aftermath_to_input()
                
                return {
                    "success": True,
                    "turn": self.state.turn_count,
                    "phase": self.state.phase.value,
                    "battle_ended": self.state.battle_ended,
                    "battle_result": self.state.battle_result.value if self.state.battle_result else None,
                    "result": result
                }
            
        except Exception as e:
            logger.error(f"Fehler bei Turn-Ausführung: {e}")
            return {"success": False, "error": str(e)}
    
    def start_battle(self) -> Dict[str, Any]:
        """
        Start the battle - pure coordination.
        Delegates to turn_processor for initialization.
        """
        if not self.turn_processor:
            raise RuntimeError("TurnProcessor not set - call set_managers() first")
        
        logger.info("Starting battle")
        
        # Delegate to turn processor
        result = self.turn_processor.initialize_battle(self.state)
        
        return {
            "player_active": self.state.player_active.name if self.state.player_active else None,
            "enemy_active": self.state.enemy_active.name if self.state.enemy_active else None,
            "battle_type": self.state.battle_type.value,
            "turn": self.state.turn_count,
            "phase": self.state.phase.value,
            "result": result
        }
    
    def process_player_input(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process player input - pure coordination.
        Delegates to action_processor for execution.
        """
        if not self.action_processor:
            raise RuntimeError("ActionProcessor not set - call set_managers() first")
        
        logger.info(f"Processing player input: {action.get('type', 'unknown')}")
        
        # Delegate to action processor
        result = self.action_processor.process_player_action(self.state, action)
        
        return {
            "result": result,
            "phase": self.state.phase.value,
            "turn": self.state.turn_count,
            "battle_ended": self.state.battle_ended,
            "battle_result": self.state.battle_result.value if self.state.battle_result else None
        }
    
    def process_enemy_turn(self) -> Dict[str, Any]:
        """
        Process enemy turn - pure coordination.
        Delegates to turn_processor for enemy AI decisions.
        """
        if not self.turn_processor:
            raise RuntimeError("TurnProcessor not set - call set_managers() first")
        
        logger.info("Processing enemy turn")
        
        # Delegate to turn processor
        result = self.turn_processor.process_enemy_turn(self.state)
        
        return {
            "result": result,
            "phase": self.state.phase.value,
            "turn": self.state.turn_count,
            "battle_ended": self.state.battle_ended,
            "battle_result": self.state.battle_result.value if self.state.battle_result else None
        }
    
    def validate_action(self, action_data: Dict[str, Any], is_player: bool = True, detailed: bool = False):
        """
        CONSOLIDATED ACTION VALIDATION - Single source of truth.
        Replaces _validate_action() and validate_action_with_errors().
        
        Args:
            action_data: Action data to validate
            is_player: Whether this is a player action
            detailed: If True, returns detailed error information
            
        Returns:
            If detailed=False: bool (is_valid)
            If detailed=True: dict with 'valid', 'errors', 'warnings' keys
        """
        from engine.systems.battle.battle_validation import BattleValidator
        return BattleValidator.validate_action_complete(action_data, self.state, is_player, detailed)
    
    def _create_battle_action(self, action_data: Dict[str, Any], is_player: bool) -> Optional[BattleAction]:
        """
        Create BattleAction from action data.
        DELEGATED: Use turn_logic.create_action_from_dict for consistency.
        
        Args:
            action_data: Action data
            is_player: Whether this is a player action
            
        Returns:
            BattleAction or None if creation fails
        """
        try:
            from engine.systems.battle.turn_logic import create_action_from_dict
            
            actor = self.state.player_active if is_player else self.state.enemy_active
            if not actor:
                logger.error(f"No active monster for {'player' if is_player else 'enemy'}")
                return None
            
            # Use centralized action creation
            return create_action_from_dict(
                action_dict=action_data,
                actor=actor,
                target=action_data.get('target'),
                move=action_data.get('move')
            )
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der BattleAction: {e}")
            return None
    
    def _execute_actions(self) -> Dict[str, Any]:
        """
        Execute all actions in turn order.
        DELEGATED: Use ActionProcessor for all action execution.
        
        Returns:
            Dict with execution result
        """
        try:
            if not self.action_processor:
                logger.error("No ActionProcessor available for execution")
                return {'error': 'No ActionProcessor available'}
            
            # Sort actions by priority and speed
            sorted_actions = self.turn_order.sort_actions()
            
            results = []
            for action in sorted_actions:
                # Delegate to ActionProcessor
                result = self.action_processor.execute_action(action)
                results.append(result)
                
                # Mark action as executed
                self.turn_order.execute_action(action)
            
            return {
                "actions_executed": len(results),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Action-Ausführung: {e}")
            return {"error": str(e)}
