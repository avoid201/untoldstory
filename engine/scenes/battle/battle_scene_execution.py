"""
Battle Scene Execution - Turn execution and action processing
Max 250 lines - contains only execution logic
"""

import logging
from typing import Optional, Dict, Any

from engine.systems.battle.turn_logic import BattleAction, ActionType
from engine.systems.battle.battle_enums import BattlePhase, BattleResult
from engine.systems.battle.battle_ai import BattleAI
from engine.systems.moves import Move
from engine.ui.battle import BattleMenuState
from engine.scenes.battle.battle_scene_debug import debug_battle_info, debug_battle_error, debug_battle_debug

logger = logging.getLogger(__name__)


class BattleSceneExecution:
    """Battle scene execution - handles turn execution and action processing."""
    
    def __init__(self, battle_scene_core):
        """Initialize execution handler with reference to core."""
        self.core = battle_scene_core
        self.battle_ai = BattleAI()
        logger.info("BattleSceneExecution initialized")
    
    def execute_turn(self, player_action: BattleAction) -> Dict[str, Any]:
        """Execute a complete battle turn with player and enemy actions."""
        try:
            debug_battle_info("⚔️ EXECUTING TURN: Starting turn execution")
            
            # Generate enemy action
            enemy_action = self._generate_enemy_action()
            if not enemy_action:
                debug_battle_error("Failed to generate enemy action")
                return {"success": False, "error": "No enemy action"}
            
            # Execute player action first
            player_result = self._execute_player_action(player_action)
            if not player_result.get('success'):
                debug_battle_error(f"Player action failed: {player_result.get('error')}")
                return player_result
            
            # Execute enemy action
            enemy_result = self._execute_enemy_action(enemy_action)
            if not enemy_result.get('success'):
                debug_battle_error(f"Enemy action failed: {enemy_result.get('error')}")
                return enemy_result
            
            # Create turn result
            turn_result = {
                'success': True,
                'turn': getattr(self.core.battle_state, 'turn_count', 1),
                'phase': 'input',
                'battle_ended': False,
                'battle_result': None,
                'result': {
                    'success': True,
                    'actions_executed': 2,
                    'actions_failed': 0,
                    'turn_events': [],
                    'damage_dealt': (player_result.get('damage_dealt', 0) + enemy_result.get('damage_dealt', 0)),
                    'monsters_fainted': (player_result.get('monsters_fainted', 0) + enemy_result.get('monsters_fainted', 0)),
                    'battle_ended': False,
                    'battle_result': None
                }
            }
            
            debug_battle_info(f"✅ TURN EXECUTED: {turn_result}")
            return turn_result
            
        except Exception as e:
            debug_battle_error(f"Error executing turn: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _execute_player_action(self, action: BattleAction) -> Dict[str, Any]:
        """Execute player action."""
        try:
            debug_battle_info(f"📝 PLAYER ACTION: {action.actor.name} setzt {action.move.name} ein!")
            
            # Execute action through battle controller
            if self.core.battle_controller and self.core.battle_controller.action_processor:
                result = self.core.battle_controller.action_processor.execute_action(action)
                debug_battle_info(f"✅ PLAYER ACTION EXECUTED: {result}")
                
                # CRITICAL: Update HP bars immediately after action
                self._update_hp_bars_after_action(action, result)
                
                return result
            else:
                debug_battle_error("No battle controller or action processor available")
                return {"success": False, "error": "No action processor"}
                
        except Exception as e:
            debug_battle_error(f"Error executing player action: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _execute_enemy_action(self, action: BattleAction) -> Dict[str, Any]:
        """Execute enemy action."""
        try:
            debug_battle_info(f"📝 ENEMY ACTION: {action.actor.name} setzt {action.move.name} ein!")
            
            # Execute action through battle controller
            if self.core.battle_controller and self.core.battle_controller.action_processor:
                result = self.core.battle_controller.action_processor.execute_action(action)
                debug_battle_info(f"✅ ENEMY ACTION EXECUTED: {result}")
                
                # CRITICAL: Update HP bars immediately after action
                self._update_hp_bars_after_action(action, result)
                
                return result
            else:
                debug_battle_error("No battle controller or action processor available")
                return {"success": False, "error": "No action processor"}
                
        except Exception as e:
            debug_battle_error(f"Error executing enemy action: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _generate_enemy_action(self) -> Optional[BattleAction]:
        """Generate enemy action using AI."""
        try:
            if not self.core.battle_state or not self.core.battle_state.enemy_active:
                return None
            
            # Get enemy moves
            enemy_moves = self.core.battle_state.enemy_active.moves
            if not enemy_moves:
                debug_battle_error("Enemy has no moves available")
                return None
            
            # Use AI to select move
            ai_action = self.battle_ai.get_action(
                self.core.battle_state.enemy_active,
                self.core.battle_state.player_active,
                enemy_moves
            )
            
            if not ai_action or ai_action.get('action_type') != 'ATTACK':
                debug_battle_error("AI failed to generate attack action")
                return None
            
            # Convert AI action to BattleAction
            move_data = ai_action.get('move', {})
            if not move_data:
                debug_battle_error("AI action has no move data")
                return None
            
            # Find matching move in enemy's moves
            selected_move = None
            for move in enemy_moves:
                if move.name == move_data.get('name'):
                    selected_move = move
                    break
            
            if not selected_move:
                debug_battle_error(f"Enemy move not found: {move_data.get('name')}")
                return None
            
            # Create BattleAction
            action = BattleAction(
                action_type=ActionType.ATTACK,
                actor=self.core.battle_state.enemy_active,
                move=selected_move,
                target=self.core.battle_state.player_active
            )
            
            debug_battle_info(f"Enemy action generated: {action.actor.name} -> {action.move.name}")
            return action
            
        except Exception as e:
            debug_battle_error(f"Error generating enemy action: {e}", exc_info=True)
            return None
    
    def check_battle_end(self) -> bool:
        """Check if battle has ended."""
        try:
            if not self.core.battle_state:
                return False
            
            # Check if battle is already ended
            if self.core.battle_state.battle_ended:
                return True
            
            # Check player team
            if all(m.current_hp <= 0 for m in self.core.battle_state.player_team):
                self.core.battle_state.battle_result = BattleResult.DEFEAT
                self.core.battle_state.battle_ended = True
                debug_battle_info("Player defeated - all monsters fainted")
                return True
            
            # Check enemy team
            if all(m.current_hp <= 0 for m in self.core.battle_state.enemy_team):
                self.core.battle_state.battle_result = BattleResult.VICTORY
                self.core.battle_state.battle_ended = True
                debug_battle_info("Enemy defeated - victory!")
                return True
            
            return False
            
        except Exception as e:
            debug_battle_error(f"Error checking battle end: {e}", exc_info=True)
            return False
    
    def handle_battle_end(self) -> bool:
        """Handle battle end - show appropriate screen."""
        try:
            if not self.core.battle_state or not self.core.battle_state.battle_ended:
                return False
            
            # Check if we already handled battle end
            if hasattr(self.core.battle_state, 'battle_end_handled') and self.core.battle_state.battle_end_handled:
                return True
            
            battle_result = self.core.battle_state.battle_result
            
            if battle_result == BattleResult.VICTORY:
                debug_battle_info("🏆 VICTORY! Showing victory screen")
                self._show_victory_screen()
                self.core.battle_state.battle_end_handled = True
                return True
            elif battle_result == BattleResult.DEFEAT:
                debug_battle_info("💀 DEFEAT! Showing defeat screen")
                self._show_defeat_screen()
                self.core.battle_state.battle_end_handled = True
                return True
            else:
                debug_battle_info(f"Unknown battle result: {battle_result}")
                return False
                
        except Exception as e:
            debug_battle_error(f"Error handling battle end: {e}", exc_info=True)
            return False
    
    def _show_victory_screen(self):
        """Show victory screen."""
        try:
            if self.core.battle_ui:
                self.core.battle_ui.show_victory_message()
                self.core.battle_ui.current_ui_state = BattleMenuState.BATTLE_RESULT
                # Set flag to wait for user input to continue
                self.core.battle_ui.state.waiting_for_input = True
            debug_battle_info("Victory screen shown")
        except Exception as e:
            debug_battle_error(f"Error showing victory screen: {e}")
    
    def _show_defeat_screen(self):
        """Show defeat screen."""
        try:
            if self.core.battle_ui:
                self.core.battle_ui.show_defeat_message()
                self.core.battle_ui.current_ui_state = BattleMenuState.BATTLE_RESULT
            debug_battle_info("Defeat screen shown")
        except Exception as e:
            debug_battle_error(f"Error showing defeat screen: {e}")
    
    def reset_ui_for_next_turn(self):
        """Reset UI for next turn."""
        try:
            if not self.core.battle_ui:
                return
            
            debug_battle_info("🔄 RESETTING UI for next turn")
            
            # Reset UI state
            self.core.battle_ui.current_menu_state = BattleMenuState.MAIN
            self.core.battle_ui.selected_option = 0
            self.core.battle_ui.waiting_for_input = True
            self.core.battle_ui._pending_action = None
            self.core.battle_ui.current_message = None
            self.core.battle_ui.message_timer = 0
            
            # CRITICAL: Reset UI state completely
            if hasattr(self.core.battle_ui, 'state'):
                self.core.battle_ui.state.waiting_for_input = True
                self.core.battle_ui.state.current_menu_state = BattleMenuState.MAIN
                self.core.battle_ui.state.selected_option = 0
            
            # Update UI state with current battle state
            if self.core.battle_state:
                self.core.battle_ui.state.player_active = self.core.battle_state.player_active
                self.core.battle_ui.state.enemy_active = self.core.battle_state.enemy_active
                
                # Update HP bars
                if hasattr(self.core.battle_ui, 'update_hp_bar'):
                    self.core.battle_ui.update_hp_bar(self.core.battle_state.player_active)
                    self.core.battle_ui.update_hp_bar(self.core.battle_state.enemy_active)
            
            # Force UI to be ready for input
            self.core.set_waiting_for_input(True)
            self.core.current_ui_state = BattleMenuState.MAIN
            
            debug_battle_info("✅ UI RESET COMPLETE - ready for next turn")
            
        except Exception as e:
            debug_battle_error(f"Error resetting UI: {e}", exc_info=True)
    
    def _update_hp_bars_after_action(self, action: BattleAction, result: Dict[str, Any]):
        """Update HP bars immediately after action execution."""
        try:
            if not self.core.battle_ui or not self.core.battle_state:
                return
            
            # Update HP bars for both monsters
            if self.core.battle_state.player_active:
                if hasattr(self.core.battle_ui, 'update_hp_bar'):
                    self.core.battle_ui.update_hp_bar(self.core.battle_state.player_active)
                    debug_battle_info(f"Updated player HP bar: {self.core.battle_state.player_active.current_hp}/{self.core.battle_state.player_active.max_hp}")
            
            if self.core.battle_state.enemy_active:
                if hasattr(self.core.battle_ui, 'update_hp_bar'):
                    self.core.battle_ui.update_hp_bar(self.core.battle_state.enemy_active)
                    debug_battle_info(f"Updated enemy HP bar: {self.core.battle_state.enemy_active.current_hp}/{self.core.battle_state.enemy_active.max_hp}")
            
        except Exception as e:
            debug_battle_error(f"Error updating HP bars: {e}", exc_info=True)
