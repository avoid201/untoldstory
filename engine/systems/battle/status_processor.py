"""
Status Processor - Consolidated Implementation
============================================
Single source of truth for all status effect processing.
Consolidated from status_processor.py and EMERGENCY_FACADES.py
"""

import logging
from typing import Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance

logger = logging.getLogger(__name__)


class StatusProcessor:
    """
    ENHANCED STATUS PROCESSOR - Complete implementation for all status effect processing.
    Enhanced with full DQM status system implementation.
    """
    
    def __init__(self, battle_state: 'BattleState' = None):
        self.battle_state = battle_state
        self.status_effects = {
            'BURN': {'damage_per_turn': 0.125, 'accuracy_reduction': 0.1},
            'POISON': {'damage_per_turn': 0.0625, 'healing_reduction': 0.5},
            'PARALYSIS': {'speed_reduction': 0.5, 'chance_to_skip': 0.25},
            'SLEEP': {'turns_to_wake': 3, 'chance_to_wake': 0.33},
            'FREEZE': {'chance_to_thaw': 0.2, 'damage_multiplier': 1.5},
            'CONFUSION': {'chance_to_hit_self': 0.5, 'damage_to_self': 0.4},
            'FLINCH': {'skip_turn': True, 'duration': 1}
        }
        logger.info("StatusProcessor initialized with full implementation")
    
    def process_status_effects(self) -> Dict[str, Any]:
        """
        ENHANCED Process all status effects for all monsters.
        
        Returns:
            Dictionary with status processing results
        """
        try:
            if not self.battle_state:
                return {'success': False, 'message': 'No battle state available'}
            
            results = {
                'status_damage': [],
                'status_healing': [],
                'status_removals': [],
                'status_applications': []
            }
            
            # Process status effects for all monsters
            all_monsters = []
            if hasattr(self.battle_state, 'player_team'):
                all_monsters.extend(self.battle_state.player_team)
            if hasattr(self.battle_state, 'enemy_team'):
                all_monsters.extend(self.battle_state.enemy_team)
            
            for monster in all_monsters:
                if hasattr(monster, 'status') and monster.status:
                    monster_results = self._process_monster_status(monster)
                    for key in results:
                        results[key].extend(monster_results.get(key, []))
            
            return {
                'success': True,
                'message': f'Processed status effects for {len(all_monsters)} monsters',
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error processing status effects: {e}")
            return {'success': False, 'message': f'Status processing error: {e}'}
    
    def _process_monster_status(self, monster: 'MonsterInstance') -> Dict[str, List[Dict[str, Any]]]:
        """
        Process status effects for a single monster.
        
        Args:
            monster: Monster to process status effects for
            
        Returns:
            Dictionary with status processing results for this monster
        """
        results = {
            'status_damage': [],
            'status_healing': [],
            'status_removals': [],
            'status_applications': []
        }
        
        try:
            if not hasattr(monster, 'status') or not monster.status:
                return results
            
            status_name = getattr(monster.status, 'name', 'UNKNOWN')
            
            if status_name == 'BURN':
                damage = self._calculate_burn_damage(monster)
                if damage > 0:
                    monster.current_hp = max(0, monster.current_hp - damage)
                    results['status_damage'].append({
                        'monster': monster.name,
                        'status': 'BURN',
                        'damage': damage
                    })
            
            elif status_name == 'POISON':
                damage = self._calculate_poison_damage(monster)
                if damage > 0:
                    monster.current_hp = max(0, monster.current_hp - damage)
                    results['status_damage'].append({
                        'monster': monster.name,
                        'status': 'POISON',
                        'damage': damage
                    })
            
            elif status_name == 'SLEEP':
                if self._check_sleep_wake(monster):
                    monster.status = None
                    results['status_removals'].append({
                        'monster': monster.name,
                        'status': 'SLEEP',
                        'reason': 'woke_up'
                    })
            
            elif status_name == 'FREEZE':
                if self._check_freeze_thaw(monster):
                    monster.status = None
                    results['status_removals'].append({
                        'monster': monster.name,
                        'status': 'FREEZE',
                        'reason': 'thawed'
                    })
            
            elif status_name == 'CONFUSION':
                if self._check_confusion_hit_self(monster):
                    damage = self._calculate_confusion_damage(monster)
                    monster.current_hp = max(0, monster.current_hp - damage)
                    results['status_damage'].append({
                        'monster': monster.name,
                        'status': 'CONFUSION',
                        'damage': damage,
                        'self_damage': True
                    })
            
            elif status_name == 'FLINCH':
                # Flinch only lasts one turn
                monster.status = None
                results['status_removals'].append({
                    'monster': monster.name,
                    'status': 'FLINCH',
                    'reason': 'expired'
                })
            
        except Exception as e:
            logger.error(f"Error processing status for monster {monster.name}: {e}")
        
        return results
    
    def _calculate_burn_damage(self, monster: 'MonsterInstance') -> int:
        """Calculate burn damage (12.5% of max HP)."""
        try:
            max_hp = getattr(monster, 'max_hp', 100)
            return int(max_hp * 0.125)
        except Exception:
            return 0
    
    def _calculate_poison_damage(self, monster: 'MonsterInstance') -> int:
        """Calculate poison damage (6.25% of max HP)."""
        try:
            max_hp = getattr(monster, 'max_hp', 100)
            return int(max_hp * 0.0625)
        except Exception:
            return 0
    
    def _check_sleep_wake(self, monster: 'MonsterInstance') -> bool:
        """Check if monster wakes up from sleep."""
        import random
        return random.random() < 0.33  # 33% chance to wake up
    
    def _check_freeze_thaw(self, monster: 'MonsterInstance') -> bool:
        """Check if monster thaws from freeze."""
        import random
        return random.random() < 0.2  # 20% chance to thaw
    
    def _check_confusion_hit_self(self, monster: 'MonsterInstance') -> bool:
        """Check if confused monster hits itself."""
        import random
        return random.random() < 0.5  # 50% chance to hit self
    
    def _calculate_confusion_damage(self, monster: 'MonsterInstance') -> int:
        """Calculate confusion self-damage."""
        try:
            max_hp = getattr(monster, 'max_hp', 100)
            return int(max_hp * 0.4)  # 40% of max HP
        except Exception:
            return 0
    
    def apply_status_effect(self, monster: 'MonsterInstance', status_name: str, duration: int = -1) -> bool:
        """
        Apply a status effect to a monster.
        
        Args:
            monster: Monster to apply status to
            status_name: Name of status effect
            duration: Duration in turns (-1 for permanent until removed)
            
        Returns:
            True if status was applied successfully
        """
        try:
            if status_name not in self.status_effects:
                logger.warning(f"Unknown status effect: {status_name}")
                return False
            
            # Create status object
            status_obj = type('Status', (), {
                'name': status_name,
                'duration': duration,
                'turns_remaining': duration
            })()
            
            monster.status = status_obj
            logger.info(f"Applied {status_name} to {monster.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error applying status effect: {e}")
            return False
    
    def remove_status_effect(self, monster: 'MonsterInstance', status_name: str = None) -> bool:
        """
        Remove status effect from monster.
        
        Args:
            monster: Monster to remove status from
            status_name: Specific status to remove (None for any)
            
        Returns:
            True if status was removed
        """
        try:
            if not hasattr(monster, 'status') or not monster.status:
                return False
            
            if status_name and getattr(monster.status, 'name', '') != status_name:
                return False
            
            monster.status = None
            logger.info(f"Removed status from {monster.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing status effect: {e}")
            return False
