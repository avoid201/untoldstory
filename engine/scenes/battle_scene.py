"""
Battle Scene - Clean modular version
Max 200 lines - uses modular components
"""

import pygame
import logging
from typing import Optional, List, Dict, Any

from engine.core.scene_base import Scene
from engine.core.config import GameState
from engine.ui.battle import BattleMenuState
from engine.systems.battle.battle_enums import BattlePhase, BattleResult
from engine.systems.monster_instance import MonsterInstance
from engine.scenes.battle.battle_scene_core import BattleSceneCore
from engine.scenes.battle.battle_scene_input import BattleSceneInput
from engine.scenes.battle.battle_scene_execution import BattleSceneExecution
from engine.scenes.battle.battle_scene_debug import debug_battle_info, debug_battle_error

logger = logging.getLogger(__name__)


class BattleScene(Scene):
    """Clean modular battle scene - uses specialized components."""
    
    def __init__(self, game):
        """Initialize battle scene with modular components."""
        super().__init__(game)
        
        # Core battle scene
        self.core = BattleSceneCore(game)
        
        # Specialized components
        self.input_handler = BattleSceneInput(self.core)
        self.execution_handler = BattleSceneExecution(self.core)
        
        logger.info("BattleScene initialized with modular components")
        
    def on_enter(self, **kwargs):
        """Enter battle scene."""
        try:
            # Delegate to core
            self.core.on_enter(**kwargs)
            
            # Initialize components
            self.input_handler = BattleSceneInput(self.core)
            self.execution_handler = BattleSceneExecution(self.core)
            
            debug_battle_info("Battle scene entered successfully")
            
        except Exception as e:
            debug_battle_error(f"Failed to enter battle scene: {e}", exc_info=True)
            self.game.change_state(GameState.MAIN_MENU)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events."""
        try:
            # Delegate to input handler
            return self.input_handler.handle_event(event)
                    
        except Exception as e:
            debug_battle_error(f"Error handling event: {e}", exc_info=True)
        return False
    
    def update(self, dt: float) -> None:
        """Update battle scene."""
        try:
            # CRITICAL: Update Battle UI first (includes intro sequence)
            if self.core.get_battle_ui():
                self.core.get_battle_ui().update(dt)
            
            # Process pending action
            if self.core.get_pending_action():
                self._process_pending_action()
            
            # Process battle events
            self._process_battle_events()
            
            # Update battle phase
            self._update_battle_phase()
            
            # Check for battle end
            if self.execution_handler.check_battle_end():
                self.execution_handler.handle_battle_end()
            
        except Exception as e:
            debug_battle_error(f"Error updating battle scene: {e}", exc_info=True)
    
    def _process_pending_action(self):
        """Process pending player action."""
        try:
            action = self.core.get_pending_action()
            if not action:
                return
            
            debug_battle_info(f"Processing pending action: {action.action_type}")
            
            # Execute turn
            turn_result = self.execution_handler.execute_turn(action)
            
            if turn_result.get('success'):
                # Clear pending action
                self.core.clear_pending_action()
                
                # Check if battle ended
                if turn_result.get('battle_ended'):
                    debug_battle_info("Battle ended during turn execution")
                else:
                    # Reset UI for next turn
                    self.execution_handler.reset_ui_for_next_turn()
            else:
                debug_battle_error(f"Turn execution failed: {turn_result.get('error')}")
                
        except Exception as e:
            debug_battle_error(f"Error processing pending action: {e}", exc_info=True)
    
    def _process_battle_events(self):
        """Process battle events."""
        try:
            if self.core.event_processor:
                # Process events
                events_processed = self.core.event_processor.process_events()
                if events_processed > 0:
                    debug_battle_info(f"Processed {events_processed} battle events")
            
        except Exception as e:
            debug_battle_error(f"Error processing battle events: {e}", exc_info=True)
    
    def _update_battle_phase(self):
        """Update battle phase."""
        try:
            current_phase = self.core.get_current_phase()
            
            # Only log phase changes
            if not hasattr(self, '_last_logged_phase') or self._last_logged_phase != current_phase:
                debug_battle_info(f"🔄 PHASE UPDATE: Current phase = {current_phase}")
                self._last_logged_phase = current_phase
            
            # CRITICAL: Auto-transition from START to INPUT after intro sequence
            from engine.systems.battle.battle_enums import BattlePhase
            if current_phase == BattlePhase.START:
                # Check if intro sequence is complete
                if (self.core.battle_ui and 
                    hasattr(self.core.battle_ui, 'intro_state') and 
                    self.core.battle_ui.intro_state.get('intro_complete', False)):
                    
                    # Transition to INPUT phase
                    self.core.battle_state.phase = BattlePhase.INPUT
                    self.core.battle_state.waiting_for_input = True
                    debug_battle_info("🔄 AUTO-TRANSITION: START → INPUT (intro complete)")
            
        except Exception as e:
            debug_battle_error(f"Error updating battle phase: {e}", exc_info=True)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw battle scene."""
        try:
            # Clear screen
            surface.fill((0, 0, 0))
            
            # Draw battle UI
            if self.core.get_battle_ui():
                self.core.get_battle_ui().draw(surface)
    
        except Exception as e:
            debug_battle_error(f"Error drawing battle scene: {e}", exc_info=True)
    
    def on_exit(self):
        """Exit battle scene."""
        try:
            debug_battle_info("Exiting battle scene")
            
            # Clean up components
            if hasattr(self, 'input_handler'):
                del self.input_handler
            if hasattr(self, 'execution_handler'):
                del self.execution_handler
                
        except Exception as e:
            debug_battle_error(f"Error exiting battle scene: {e}", exc_info=True)
    
    # Delegate methods to core
    def get_battle_state(self):
        """Get battle state."""
        return self.core.get_battle_state()
    
    def get_battle_controller(self):
        """Get battle controller."""
        return self.core.get_battle_controller()
    
    def get_battle_ui(self):
        """Get battle UI."""
        return self.core.get_battle_ui()
    
    def is_battle_over(self) -> bool:
        """Check if battle is over."""
        return self.core.is_battle_over()
    
    def get_battle_result(self) -> Optional[BattleResult]:
        """Get battle result."""
        return self.core.get_battle_result()
