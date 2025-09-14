"""
Battle End Detection - Consolidated battle end logic
=====================================================
Single source of truth for all battle end detection logic.
"""

import logging
from typing import Dict, Any, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.battle.battle_state import BattleState

from engine.systems.battle.battle_enums import BattleResult, BattlePhase

logger = logging.getLogger(__name__)


class BattleEndDetection:
    """
    Consolidated battle end detection system.
    Single source of truth for all battle end checking logic.
    """
    
    @staticmethod
    def check_battle_end_conditions(battle_state: 'BattleState') -> Dict[str, Any]:
        """
        Check if battle should end - CONSOLIDATED IMPLEMENTATION.
        
        Args:
            battle_state: Current battle state
            
        Returns:
            Dict with battle end information:
            {
                'battle_ended': bool,
                'result': BattleResult | None,
                'player_team_fainted': bool,
                'enemy_team_fainted': bool,
                'reason': str
            }
        """
        try:
            if not battle_state:
                return {
                    'battle_ended': False,
                    'result': None,
                    'player_team_fainted': False,
                    'enemy_team_fainted': False,
                    'reason': 'No battle state'
                }
            
            # Check if all player monsters are fainted
            player_fainted = BattleEndDetection._are_all_monsters_fainted(
                battle_state.player_team
            )
            
            # Check if all enemy monsters are fainted
            enemy_fainted = BattleEndDetection._are_all_monsters_fainted(
                battle_state.enemy_team
            )
            
            # Determine battle result
            if player_fainted and enemy_fainted:
                # Both teams fainted - this is a draw
                logger.info("🟡 BATTLE ENDED: Draw - both teams fainted!")
                return {
                    'battle_ended': True,
                    'result': BattleResult.DRAW,
                    'player_team_fainted': True,
                    'enemy_team_fainted': True,
                    'reason': 'Both teams fainted'
                }
            elif player_fainted:
                # Player defeated
                logger.info("🔴 BATTLE ENDED: Player defeated!")
                return {
                    'battle_ended': True,
                    'result': BattleResult.DEFEAT,
                    'player_team_fainted': True,
                    'enemy_team_fainted': False,
                    'reason': 'Player team fainted'
                }
            elif enemy_fainted:
                # Player victorious
                logger.info("🟢 BATTLE ENDED: Player victorious!")
                return {
                    'battle_ended': True,
                    'result': BattleResult.VICTORY,
                    'player_team_fainted': False,
                    'enemy_team_fainted': True,
                    'reason': 'Enemy team fainted'
                }
            
            # Battle continues
            return {
                'battle_ended': False,
                'result': None,
                'player_team_fainted': False,
                'enemy_team_fainted': False,
                'reason': 'Battle ongoing'
            }
            
        except Exception as e:
            logger.error(f"Error checking battle end conditions: {e}")
            return {
                'battle_ended': False,
                'result': None,
                'player_team_fainted': False,
                'enemy_team_fainted': False,
                'reason': f'Error: {e}'
            }
    
    @staticmethod
    def _are_all_monsters_fainted(team: List['MonsterInstance']) -> bool:
        """
        Check if all monsters in a team are fainted.
        
        Args:
            team: List of monsters to check
            
        Returns:
            True if all monsters are fainted, False otherwise
        """
        try:
            if not team:
                return True  # Empty team is considered "all fainted"
            
            for monster in team:
                if not monster:
                    continue  # Skip None entries
                
                # Check if monster has HP attribute and is not fainted
                if hasattr(monster, 'current_hp'):
                    if monster.current_hp > 0:
                        return False  # Found a conscious monster
                else:
                    # Fallback: check is_fainted attribute
                    if hasattr(monster, 'is_fainted'):
                        if not monster.is_fainted:
                            return False  # Found a conscious monster
                    else:
                        # No HP or fainted attribute - assume conscious
                        logger.warning(f"Monster {getattr(monster, 'name', 'Unknown')} has no HP or fainted attribute")
                        return False
            
            # All monsters are fainted
            return True
            
        except Exception as e:
            logger.error(f"Error checking if team is fainted: {e}")
            return False  # Assume team is alive on error
    
    @staticmethod
    def apply_battle_end_result(battle_state: 'BattleState', 
                              battle_end_info: Dict[str, Any]) -> bool:
        """
        Apply battle end result to battle state.
        
        Args:
            battle_state: Battle state to update
            battle_end_info: Battle end information from check_battle_end_conditions
            
        Returns:
            True if battle state was updated, False otherwise
        """
        try:
            if not battle_state or not battle_end_info:
                return False
            
            if battle_end_info.get('battle_ended', False):
                # Set battle as ended
                battle_state.battle_ended = True
                battle_state.battle_result = battle_end_info.get('result')
                
                # Log the result
                result = battle_end_info.get('result')
                reason = battle_end_info.get('reason', 'Unknown reason')
                logger.info(f"✅ Battle ended: {result.value if result else 'None'} - {reason}")
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error applying battle end result: {e}")
            return False
    
    @staticmethod
    def emit_battle_end_event(battle_state: 'BattleState', 
                            battle_end_info: Dict[str, Any]) -> bool:
        """
        Emit battle end event through event processor.
        
        Args:
            battle_state: Battle state with event processor
            battle_end_info: Battle end information
            
        Returns:
            True if event was emitted, False otherwise
        """
        try:
            if not hasattr(battle_state, 'event_processor') or not battle_state.event_processor:
                logger.warning("No event processor available for battle end event")
                return False
            
            if not battle_end_info.get('battle_ended', False):
                return False  # No event to emit
            
            from engine.systems.battle.events.event_types import EventType
            
            # Prepare event data
            event_data = {
                'result': battle_end_info.get('result'),
                'battle_ended': True,
                'player_team_fainted': battle_end_info.get('player_team_fainted', False),
                'enemy_team_fainted': battle_end_info.get('enemy_team_fainted', False),
                'turn_count': getattr(battle_state, 'turn_count', 0),
                'reason': battle_end_info.get('reason', 'Unknown')
            }
            
            # Emit battle end event
            success = battle_state.event_processor.emit_event(
                EventType.BATTLE_END,
                event_data
            )
            
            if success:
                logger.info(f"✅ Battle end event emitted successfully")
            else:
                logger.warning(f"⚠️ Failed to emit battle end event")
            
            return success
            
        except Exception as e:
            logger.error(f"Error emitting battle end event: {e}")
            return False
    
    @staticmethod
    def check_and_handle_battle_end(battle_state: 'BattleState') -> Dict[str, Any]:
        """
        Complete battle end checking and handling.
        Combines check, apply, and emit in one call.
        
        Args:
            battle_state: Battle state to check and update
            
        Returns:
            Battle end information with additional 'handled' flag
        """
        try:
            # Check battle end conditions
            battle_end_info = BattleEndDetection.check_battle_end_conditions(battle_state)
            
            if battle_end_info.get('battle_ended', False):
                # Apply result to battle state
                applied = BattleEndDetection.apply_battle_end_result(battle_state, battle_end_info)
                
                # Emit event
                emitted = BattleEndDetection.emit_battle_end_event(battle_state, battle_end_info)
                
                # Add handling info
                battle_end_info['handled'] = applied and emitted
                
                logger.info(f"🏁 Battle end handled: applied={applied}, emitted={emitted}")
            else:
                battle_end_info['handled'] = True  # Nothing to handle
            
            return battle_end_info
            
        except Exception as e:
            logger.error(f"Error checking and handling battle end: {e}")
            return {
                'battle_ended': False,
                'result': None,
                'player_team_fainted': False,
                'enemy_team_fainted': False,
                'reason': f'Error: {e}',
                'handled': False
            }
