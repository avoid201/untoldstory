"""
State management methods - max 200 lines
Contains all state-related methods and monster information handling.
"""

import logging
from typing import Dict, Any, Optional, List
from engine.systems.battle.battle_enums import BattlePhase

logger = logging.getLogger(__name__)


class BattleControllerStateMixin:
    """
    State management methods extracted from main controller.
    Handles all state information and monster data.
    """
    
    def get_state_info(self, detail_level: str = 'full') -> Dict[str, Any]:
        """
        CONSOLIDATED STATE GETTER - Single source of truth for all state information.
        Replaces get_battle_state(), get_battle_status(), and get_current_phase_info().
        
        Args:
            detail_level: 'minimal', 'basic', 'full', 'complete'
                - minimal: Just phase and turn
                - basic: Phase, turn, active monsters
                - full: All battle data
                - complete: All data including logs and rewards
        
        Returns:
            Dict with battle state information
        """
        try:
            # Base information (always included)
            base_info = {
                "phase": self.state.phase.value,
                "turn": self.state.turn_count,
                "battle_ended": self.state.battle_ended,
                "battle_result": self.state.battle_result.value if self.state.battle_result else None
            }
            
            # Minimal level - just return base
            if detail_level == 'minimal':
                return base_info
            
            # Basic level - add active monsters
            if detail_level in ['basic', 'full', 'complete']:
                base_info.update({
                    "player_active": self._get_monster_info(self.state.player_active),
                    "enemy_active": self._get_monster_info(self.state.enemy_active),
                    "waiting_for_input": self.state.waiting_for_input,
                    "is_player_turn": self.state.phase == BattlePhase.INPUT,
                    "is_execution": self.state.phase == BattlePhase.EXECUTION,
                    "is_aftermath": self.state.phase == BattlePhase.AFTERMATH
                })
            
            # Full level - add battle configuration
            if detail_level in ['full', 'complete']:
                base_info.update({
                    "battle_type": self.state.battle_type.value,
                    "can_flee": self.state.can_flee,
                    "can_catch": self.state.can_catch
                })
            
            # Complete level - add logs and rewards
            if detail_level == 'complete':
                base_info.update({
                    "battle_log": self.state.battle_log[-10:],  # Last 10 messages
                    "exp_earned": self.state.exp_earned,
                    "money_earned": self.state.money_earned,
                    "items_earned": self.state.items_earned,
                    "player_team": [self._get_monster_info(monster) for monster in self.state.player_team],
                    "enemy_team": [self._get_monster_info(monster) for monster in self.state.enemy_team]
                })
            
            return base_info
            
        except Exception as e:
            logger.error(f"Error getting state info: {e}")
            return {"error": str(e)}
    
    def _get_monster_info(self, monster) -> Dict[str, Any]:
        """Helper method to get monster information."""
        if not monster:
            return None
        
        return {
            "name": monster.name,
            "hp": monster.current_hp,
            "max_hp": monster.max_hp,
            "status": getattr(monster, 'status_condition', None),
            "level": getattr(monster, 'level', 1),
            "is_fainted": getattr(monster, 'is_fainted', False)
        }
    
    # Diese Methode wurde entfernt - monster.get_available_moves() wird direkt verwendet
    
    def get_passive_abilities_for_monster(self, monster) -> List[Dict[str, Any]]:
        """
        Get passive abilities for a monster based on its talents.
        
        Args:
            monster: Monster to get passive abilities for
            
        Returns:
            List of passive ability dictionaries
        """
        try:
            if not monster or not hasattr(monster, 'talents'):
                return []
            
            passive_abilities = []
            
            # Get passive abilities from all learned talents
            for talent_instance in monster.talents:
                if not talent_instance.is_learned:
                    continue
                
                talent = self.talent_database.get_talent(talent_instance.talent_id)
                if not talent:
                    continue
                
                # Get passive abilities for current talent tier
                talent_passives = talent.get_passive_abilities_for_tier(talent_instance.current_tier)
                passive_abilities.extend(talent_passives)
            
            return passive_abilities
            
        except Exception as e:
            logger.error(f"Error getting passive abilities for monster {monster.name}: {e}")
            return []
    
    # Diese Methode wurde entfernt - validate_move_availability() wird jetzt verwendet
