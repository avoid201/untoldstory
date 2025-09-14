"""
Battle Controller Aftermath - Battle aftermath processing
========================================================
Handles aftermath phase processing, battle end conditions, and monster switching.
"""

import logging
from typing import Dict, Any, Optional
from engine.systems.battle.battle_enums import BattlePhase, BattleResult

logger = logging.getLogger(__name__)


class BattleControllerAftermathMixin:
    """Aftermath processing methods for battle controller."""
    
    def _process_aftermath(self) -> None:
        """
        Process aftermath phase - status effects, battle end check, etc.
        AGENT 3: Implements proper aftermath processing.
        """
        try:
            logger.info("Processing aftermath phase")
            
            # Check for battle end conditions
            if self._check_battle_end_conditions():
                # Battle state is already updated by BattleEndDetection
                self.transition_phase(BattlePhase.END)
                logger.info("✅ Battle ended during aftermath - transitioning to END phase")
                return
            
            # Process status effects
            if self.status_processor:
                self.status_processor.process_status_effects()
            
            # Check for fainted monsters
            self._check_fainted_monsters()
            
            logger.info("Aftermath processing complete")
            
        except Exception as e:
            logger.error(f"Error in aftermath processing: {e}")
    
    def _check_battle_end_conditions(self) -> bool:
        """
        Check if battle should end - CONSOLIDATED IMPLEMENTATION.
        AGENT 3: Implements proper battle end checking.
        """
        try:
            # Use consolidated battle end detection
            from ..battle_end_detection import BattleEndDetection
            battle_end_info = BattleEndDetection.check_and_handle_battle_end(self.state)
            
            # Return True if battle ended, False otherwise
            return battle_end_info.get('battle_ended', False)
            
        except Exception as e:
            logger.error(f"Error checking battle end conditions: {e}")
            return False
    
    # _emit_battle_end_event method removed - now handled by BattleEndDetection
    
    def _check_fainted_monsters(self) -> None:
        """
        Check for fainted monsters and switch if needed.
        AGENT 3: Implements proper monster switching.
        """
        try:
            # Check player monster
            if self.state.player_active and self.state.player_active.current_hp <= 0:
                logger.info(f"Player monster {self.state.player_active.name} fainted")
                # TODO: Implement monster switching logic
                
            # Check enemy monster
            if self.state.enemy_active and self.state.enemy_active.current_hp <= 0:
                logger.info(f"Enemy monster {self.state.enemy_active.name} fainted")
                # TODO: Implement enemy monster switching logic
                
        except Exception as e:
            logger.error(f"Error checking fainted monsters: {e}")
