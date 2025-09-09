"""
Status Processor für das Battle System.
Verwaltet nur Status-Effekte - getrennt von der Battle-Logik.
"""

import logging
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum

from engine.systems.conditions import StatusCondition

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance

logger = logging.getLogger(__name__)

# Export StatusCondition for other modules
__all__ = ['StatusProcessor', 'StatusResult', 'StatusCondition']


@dataclass
class StatusResult:
    """Result of status effect processing."""
    success: bool
    message: str
    damage_dealt: int = 0
    prevented_by: Optional[str] = None


class StatusProcessor:
    """Verwaltet nur Status-Effekte"""
    
    def __init__(self, battle_state: 'BattleState'):
        """
        Initialize status processor.
        
        Args:
            battle_state: The battle state to process status effects for
        """
        self.state = battle_state
        
        # Status condition immunities by type (from original StatusEffects)
        self.TYPE_IMMUNITIES = {
            'burn': ['feuer'],
            'freeze': ['feuer', 'luft'],
            'poison': ['seuche', 'teufel'],
            'paralysis': ['energie']
        }
        
        # Status definitions - using StatusCondition enum values
        self.STATUS_DEFINITIONS = {
            'burn': {
                'damage_per_turn': 8,  # 1/8 of max HP
                'stat_modifiers': {'atk': 0.5},  # Burn reduces attack
                'description': "Verursacht Schaden und reduziert Angriff"
            },
            'poison': {
                'damage_per_turn': 16,  # 1/16 of max HP
                'description': "Verursacht Schaden jede Runde"
            },
            'badly_poisoned': {
                'damage_per_turn': 16,  # Increases each turn
                'description': "Verursacht zunehmenden Schaden"
            },
            'freeze': {
                'prevents_action': True,
                'description': "Verhindert Aktionen"
            },
            'paralysis': {
                'stat_modifiers': {'spd': 0.5},  # Reduces speed
                'description': "Reduziert Initiative und kann Aktionen verhindern"
            },
            'sleep': {
                'duration': 3,  # 1-3 turns
                'prevents_action': True,
                'description': "Verhindert Aktionen für einige Runden"
            },
            'confusion': {
                'duration': 3,  # 1-3 turns
                'description': "Kann sich selbst schaden"
            }
        }
        
        # Status messages
        self.STATUS_MESSAGES = {
            'burn': "wurde verbrannt!",
            'freeze': "wurde eingefroren!",
            'paralysis': "wurde paralysiert!",
            'poison': "wurde vergiftet!",
            'badly_poisoned': "wurde schwer vergiftet!",
            'sleep': "ist eingeschlafen!",
            'confusion': "wurde verwirrt!"
        }
    
    def can_apply_status(self, monster: 'MonsterInstance', status: str) -> Tuple[bool, str]:
        """
        Check if a status can be applied.
        
        Args:
            monster: Target monster
            status: Status to apply
            
        Returns:
            Tuple of (can_apply, reason_if_not)
        """
        # Already has a status
        if monster.status:
            return False, f"{monster.nickname or monster.species.name} hat bereits eine Statusveränderung!"
        
        # Check type immunity
        if status in self.TYPE_IMMUNITIES:
            immune_types = self.TYPE_IMMUNITIES[status]
            for monster_type in monster.species.types:
                if monster_type in immune_types:
                    return False, f"{monster.nickname or monster.species.name} ist immun gegen {status}!"
        
        return True, ""
    
    def apply_status(self, monster: 'MonsterInstance', status: str, duration: int = -1) -> StatusResult:
        """
        Apply a status condition.
        
        Args:
            monster: Target monster
            status: Status to apply
            duration: Duration in turns (-1 for permanent)
            
        Returns:
            StatusResult
        """
        can_apply, reason = self.can_apply_status(monster, status)
        if not can_apply:
            return StatusResult(success=False, message=reason)
        
        # Set status
        monster.status = status
        monster.status_turns = duration
        
        # Initialize status-specific counters
        if status == 'badly_poisoned':
            monster.poison_counter = 1
        
        # Get message
        monster_name = monster.nickname or monster.species.name
        message = f"{monster_name} {self.STATUS_MESSAGES.get(status, 'erhielt einen Status!')}"
        
        logger.info(f"Applied status {status} to {monster_name}")
        return StatusResult(success=True, message=message)
    
    def process_status_effects(self, monster: 'MonsterInstance') -> StatusResult:
        """
        Process end-of-turn status effects.
        
        Args:
            monster: Monster with status
            
        Returns:
            StatusResult with damage dealt
        """
        if not monster.status:
            return StatusResult(success=False, message="")
        
        status = monster.status
        damage = 0
        message = ""
        
        # Process status damage
        if status == 'burn':
            damage = max(1, monster.max_hp // 8)
            message = f"{monster.nickname or monster.species.name} leidet unter der Verbrennung!"
            
        elif status == 'poison':
            damage = max(1, monster.max_hp // 16)
            message = f"{monster.nickname or monster.species.name} leidet unter der Vergiftung!"
            
        elif status == 'badly_poisoned':
            # Increases each turn
            if not hasattr(monster, 'poison_counter'):
                monster.poison_counter = 1
            damage = max(1, (monster.max_hp * monster.poison_counter) // 16)
            monster.poison_counter += 1
            monster_name = monster.nickname or monster.species.name
            message = f"{monster_name} leidet schwer unter der Vergiftung!"
        
        # Apply damage
        if damage > 0:
            monster.current_hp = max(0, monster.current_hp - damage)
            monster_name = monster.nickname or monster.species.name
            logger.info(f"Status damage: {damage} to {monster_name}")
        
        # Process status duration
        if monster.status_turns > 0:
            monster.status_turns -= 1
            if monster.status_turns <= 0:
                # Status expires
                old_status = monster.status
                monster.status = None
                monster.status_turns = 0
                monster_name = monster.nickname or monster.species.name
                message += f" {monster_name} wurde von {old_status} geheilt!"
                logger.info(f"Status {old_status} expired for {monster_name}")
        
        return StatusResult(
            success=damage > 0 or message != "",
            message=message,
            damage_dealt=damage
        )
    
    def remove_status(self, monster: 'MonsterInstance', status: str) -> StatusResult:
        """
        Remove a status condition.
        
        Args:
            monster: Target monster
            status: Status to remove
            
        Returns:
            StatusResult
        """
        if monster.status != status:
            return StatusResult(
                success=False, 
                message=f"{monster.nickname or monster.species.name} hat nicht den Status {status}!"
            )
        
        monster.status = None
        monster.status_turns = 0
        
        # Clear status-specific counters
        if hasattr(monster, 'poison_counter'):
            monster.poison_counter = 0
        
        monster_name = monster.nickname or monster.species.name
        message = f"{monster_name} wurde von {status} geheilt!"
        logger.info(f"Removed status {status} from {monster_name}")
        
        return StatusResult(success=True, message=message)
    
    def get_status_modifiers(self, monster: 'MonsterInstance') -> Dict[str, float]:
        """
        Get stat modifiers from current status.
        
        Args:
            monster: Monster to check
            
        Returns:
            Dictionary of stat modifiers
        """
        if not monster.status or monster.status not in self.STATUS_DEFINITIONS:
            return {}
        
        status_def = self.STATUS_DEFINITIONS[monster.status]
        return status_def.stat_modifiers.copy()
    
    def can_act(self, monster: 'MonsterInstance') -> Tuple[bool, str]:
        """
        Check if monster can act (not prevented by status).
        
        Args:
            monster: Monster to check
            
        Returns:
            Tuple of (can_act, reason_if_not)
        """
        try:
            # Check if monster is fainted first
            if getattr(monster, 'is_fainted', False) or monster.current_hp <= 0:
                return False, f"{monster.nickname or monster.species.name} ist ohnmächtig!"
            
            if not monster.status:
                return True, ""
            
            status_def = self.STATUS_DEFINITIONS.get(monster.status)
            if not status_def:
                return True, ""
            
            if status_def.get('prevents_action', False):
                # Check if status prevents action this turn
                if monster.status == 'sleep':
                    return False, f"{monster.nickname or monster.species.name} schläft!"
                elif monster.status == 'freeze':
                    # 20% chance to thaw
                    import random
                    if random.random() < 0.2:
                        # Thaw out
                        self.remove_status(monster, 'freeze')
                        return True, f"{monster.nickname or monster.species.name} ist aufgetaut!"
                    else:
                        return False, f"{monster.nickname or monster.species.name} ist eingefroren!"
                elif monster.status == 'paralysis':
                    # 25% chance to be paralyzed
                    import random
                    if random.random() < 0.25:
                        return False, f"{monster.nickname or monster.species.name} ist paralysiert!"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"Error checking if monster can act: {e}")
            # Fallback: assume monster can act if there's an error
            return True, ""
    
    def get_status_info(self, status: str) -> Optional[dict]:
        """
        Get information about a status condition.
        
        Args:
            status: Status name
            
        Returns:
            Status definition or None
        """
        return self.STATUS_DEFINITIONS.get(status)
    
    def get_all_statuses(self) -> List[str]:
        """
        Get list of all available status conditions.
        
        Returns:
            List of status names
        """
        return list(self.STATUS_DEFINITIONS.keys())
    
    def is_status_immune(self, monster: 'MonsterInstance', status: str) -> bool:
        """
        Check if monster is immune to a status.
        
        Args:
            monster: Monster to check
            status: Status to check immunity for
            
        Returns:
            True if immune
        """
        if status not in self.TYPE_IMMUNITIES:
            return False
        
        immune_types = self.TYPE_IMMUNITIES[status]
        for monster_type in monster.species.types:
            if monster_type in immune_types:
                return True
        
        return False
    
    def process_all_status_effects(self, monsters: List['MonsterInstance']) -> List[StatusResult]:
        """
        Process status effects for multiple monsters.
        
        Args:
            monsters: List of monsters to process
            
        Returns:
            List of status results
        """
        results = []
        for monster in monsters:
            if monster and monster.current_hp > 0:
                result = self.process_status_effects(monster)
                if result.success:
                    results.append(result)
        
        return results
    
    def get_status_damage(self, monster: 'MonsterInstance') -> int:
        """
        Calculate status damage for a monster.
        
        Args:
            monster: Monster to calculate for
            
        Returns:
            Damage amount
        """
        if not monster.status:
            return 0
        
        status = monster.status
        
        if status == 'burn':
            return max(1, monster.max_hp // 8)
        elif status == 'poison':
            return max(1, monster.max_hp // 16)
        elif status == 'badly_poisoned':
            counter = getattr(monster, 'poison_counter', 1)
            return max(1, (monster.max_hp * counter) // 16)
        
        return 0
