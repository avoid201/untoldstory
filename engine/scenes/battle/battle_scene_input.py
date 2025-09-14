"""
Battle Scene Input - Input handling and action processing
Max 250 lines - contains only input handling logic
"""

import pygame
import logging
from typing import Optional, Dict, Any

from engine.ui.battle import BattleMenuState
from engine.systems.battle.turn_logic import BattleAction, ActionType
from engine.systems.battle.battle_enums import BattlePhase
from engine.systems.moves import Move
from engine.scenes.battle.battle_scene_debug import debug_battle_info, debug_battle_error, debug_battle_debug

logger = logging.getLogger(__name__)


class BattleSceneInput:
    """Battle scene input handling - processes player input and converts to actions."""
    
    def __init__(self, battle_scene_core):
        """Initialize input handler with reference to core."""
        self.core = battle_scene_core
        logger.info("BattleSceneInput initialized")
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events and convert to battle actions."""
        try:
            if not self.core.is_waiting_for_input():
                debug_battle_debug("UI is not waiting for input - ignoring event")
                return False
            
            if event.type == pygame.KEYDOWN:
                return self._handle_keydown(event)
            elif event.type == pygame.KEYUP:
                return self._handle_keyup(event)
            
            return False
            
        except Exception as e:
            debug_battle_error(f"Error handling event: {e}", exc_info=True)
            return False
    
    def _handle_keydown(self, event: pygame.event.Event) -> bool:
        """Handle keydown events."""
        try:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                return self._handle_confirm()
            elif event.key == pygame.K_ESCAPE:
                return self._handle_cancel()
            elif event.key == pygame.K_UP:
                return self._handle_up()
            elif event.key == pygame.K_DOWN:
                return self._handle_down()
            elif event.key == pygame.K_LEFT:
                return self._handle_left()
            elif event.key == pygame.K_RIGHT:
                return self._handle_right()
            
            return False
            
        except Exception as e:
            debug_battle_error(f"Error handling keydown: {e}")
            return False
    
    def _handle_keyup(self, event: pygame.event.Event) -> bool:
        """Handle keyup events."""
        # Currently no keyup handling needed
        return False
    
    def _handle_confirm(self) -> bool:
        """Handle confirm action (SPACE/ENTER)."""
        try:
            if not self.core.is_waiting_for_input():
                debug_battle_debug("UI is not waiting for input - ignoring confirm")
                return False
            
            # Get current UI state
            ui_state = self.core.get_ui_state()
            
            if ui_state == BattleMenuState.MAIN:
                return self._handle_main_menu_confirm()
            elif ui_state == BattleMenuState.MOVE_SELECT:
                return self._handle_move_select_confirm()
            elif ui_state == BattleMenuState.ITEM_SELECT:
                return self._handle_item_select_confirm()
            elif ui_state == BattleMenuState.TAMING_UI:
                return self._handle_taming_confirm()
            elif ui_state == BattleMenuState.SCOUT_DISPLAY:
                return self._handle_scout_confirm()
            elif ui_state == BattleMenuState.BATTLE_RESULT:
                return self._handle_battle_result_confirm()
            else:
                debug_battle_debug(f"Unknown UI state for confirm: {ui_state}")
                return False
                
        except Exception as e:
            debug_battle_error(f"Error handling confirm: {e}", exc_info=True)
            return False
    
    def _handle_cancel(self) -> bool:
        """Handle cancel action (ESCAPE)."""
        try:
            ui_state = self.core.get_ui_state()
            
            if ui_state == BattleMenuState.MAIN:
                # Can't cancel from main menu
                return False
            elif ui_state in [BattleMenuState.MOVE_SELECT, BattleMenuState.ITEM_SELECT, 
                            BattleMenuState.TAMING_UI, BattleMenuState.SCOUT_DISPLAY]:
                # Return to main menu
                self.core.current_ui_state = BattleMenuState.MAIN
                if self.core.battle_ui:
                    self.core.battle_ui.current_menu_state = BattleMenuState.MAIN
                debug_battle_info("Returned to main menu")
                return True
            else:
                debug_battle_debug(f"Unknown UI state for cancel: {ui_state}")
                return False
                
        except Exception as e:
            debug_battle_error(f"Error handling cancel: {e}")
            return False
    
    def _handle_up(self) -> bool:
        """Handle up arrow key."""
        try:
            if self.core.battle_ui:
                self.core.battle_ui.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
                return True
            return False
        except Exception as e:
            debug_battle_error(f"Error handling up: {e}")
            return False
    
    def _handle_down(self) -> bool:
        """Handle down arrow key."""
        try:
            if self.core.battle_ui:
                self.core.battle_ui.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
                return True
            return False
        except Exception as e:
            debug_battle_error(f"Error handling down: {e}")
            return False
    
    def _handle_left(self) -> bool:
        """Handle left arrow key."""
        try:
            if self.core.battle_ui:
                self.core.battle_ui.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))
                return True
            return False
        except Exception as e:
            debug_battle_error(f"Error handling left: {e}")
            return False
    
    def _handle_right(self) -> bool:
        """Handle right arrow key."""
        try:
            if self.core.battle_ui:
                self.core.battle_ui.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
                return True
            return False
        except Exception as e:
            debug_battle_error(f"Error handling right: {e}")
            return False
    
    def _handle_main_menu_confirm(self) -> bool:
        """Handle confirm from main menu."""
        try:
            if not self.core.battle_ui:
                return False
            
            # Get selected option
            selected_option = getattr(self.core.battle_ui, 'selected_option', 0)
            
            if selected_option == 0:  # ATTACKE
                self.core.current_ui_state = BattleMenuState.MOVE_SELECT
                self.core.battle_ui.current_menu_state = BattleMenuState.MOVE_SELECT
                debug_battle_info("Switched to move selection")
                return True
            elif selected_option == 1:  # ITEM
                self.core.current_ui_state = BattleMenuState.ITEM_SELECT
                self.core.battle_ui.current_menu_state = BattleMenuState.ITEM_SELECT
                debug_battle_info("Switched to item selection")
                return True
            elif selected_option == 2:  # WECHSEL
                debug_battle_info("Switch monster selected")
                return True
            elif selected_option == 3:  # ZÄHMEN
                self.core.current_ui_state = BattleMenuState.TAMING_UI
                self.core.battle_ui.current_menu_state = BattleMenuState.TAMING_UI
                debug_battle_info("Switched to taming UI")
                return True
            elif selected_option == 4:  # SPÄHEN
                self.core.current_ui_state = BattleMenuState.SCOUT_DISPLAY
                self.core.battle_ui.current_menu_state = BattleMenuState.SCOUT_DISPLAY
                debug_battle_info("Switched to scout display")
                return True
            elif selected_option == 5:  # FLUCHT
                debug_battle_info("Flee selected")
                return True
            else:
                debug_battle_debug(f"Unknown main menu option: {selected_option}")
                return False
                
        except Exception as e:
            debug_battle_error(f"Error handling main menu confirm: {e}", exc_info=True)
            return False
    
    def _handle_move_select_confirm(self) -> bool:
        """Handle confirm from move selection."""
        try:
            if not self.core.battle_ui:
                return False
            
            # Get selected move
            selected_option = getattr(self.core.battle_ui, 'selected_option', 0)
            moves = self.core.battle_state.player_active.moves if self.core.battle_state.player_active else []
            
            if 0 <= selected_option < len(moves):
                selected_move = moves[selected_option]
                debug_battle_info(f"Move selected: {selected_move.name}")
                
                # Create battle action
                action = self._create_attack_action(selected_move)
                if action:
                    self.core.set_pending_action(action)
                    return True
            else:
                debug_battle_debug(f"Invalid move selection: {selected_option}")
                return False
                
        except Exception as e:
            debug_battle_error(f"Error handling move select confirm: {e}", exc_info=True)
            return False
    
    def _handle_item_select_confirm(self) -> bool:
        """Handle confirm from item selection."""
        try:
            debug_battle_info("Item selection not implemented yet")
            return False
        except Exception as e:
            debug_battle_error(f"Error handling item select confirm: {e}")
            return False
    
    def _handle_taming_confirm(self) -> bool:
        """Handle confirm from taming UI."""
        try:
            debug_battle_info("Taming not implemented yet")
            return False
        except Exception as e:
            debug_battle_error(f"Error handling taming confirm: {e}")
            return False
    
    def _handle_scout_confirm(self) -> bool:
        """Handle confirm from scout display."""
        try:
            # Return to main menu
            self.core.current_ui_state = BattleMenuState.MAIN
            if self.core.battle_ui:
                self.core.battle_ui.current_menu_state = BattleMenuState.MAIN
            debug_battle_info("Returned to main menu from scout")
            return True
        except Exception as e:
            debug_battle_error(f"Error handling scout confirm: {e}")
            return False
    
    def _create_attack_action(self, move: Move) -> Optional[BattleAction]:
        """Create attack action from selected move."""
        try:
            if not self.core.battle_state or not self.core.battle_state.player_active:
                return None
            
            return BattleAction(
                action_type=ActionType.ATTACK,
                actor=self.core.battle_state.player_active,
                move=move,
                target=self.core.battle_state.enemy_active
            )
        except Exception as e:
            debug_battle_error(f"Error creating attack action: {e}")
            return None
    
    def _handle_battle_result_confirm(self) -> bool:
        """Handle confirm on battle result screen - exit battle."""
        try:
            debug_battle_info("🎯 Battle result confirmed - exiting battle")
            
            # Exit battle scene
            if hasattr(self.core, 'game') and self.core.game:
                # Return to previous scene (usually field scene)
                self.core.game.change_scene('field')
                return True
            else:
                debug_battle_error("No game reference to exit battle")
                return False
                
        except Exception as e:
            debug_battle_error(f"Error handling battle result confirm: {e}", exc_info=True)
            return False
