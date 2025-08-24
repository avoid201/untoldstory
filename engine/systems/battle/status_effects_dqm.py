"""
DQM-Specific Status Effects System
Implements all Dragon Quest Monsters status conditions
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Dict, Any, List
import random
import logging

logger = logging.getLogger(__name__)

class DQMStatus(Enum):
    """All DQM status conditions."""
    # Basic Status
    NORMAL = "normal"
    POISON = "poison"          # Lose HP each turn
    PARALYSIS = "paralysis"    # May skip turn
    SLEEP = "sleep"            # Cannot act
    CONFUSION = "confusion"    # May attack allies
    BURN = "burn"             # Damage + reduced ATK
    FREEZE = "freeze"         # Cannot act, extra damage
    
    # DQM-Specific
    DAZZLE = "dazzle"         # Cannot use magic
    CURSE = "curse"           # All stats reduced
    BERSERK = "berserk"       # Auto-attack with bonus
    BOUNCE = "bounce"         # Reflects magic
    SILENCE = "silence"       # Cannot use skills
    BLIND = "blind"           # Reduced accuracy
    CHARM = "charm"           # May not attack
    FEAR = "fear"             # May flee
    ZOMBIE = "zombie"         # Reverse healing

@dataclass
class StatusEffect:
    """A single status effect with duration."""
    status: DQMStatus
    duration: int  # Turns remaining (-1 = permanent)
    potency: float = 1.0  # Effect strength
    source: Optional[str] = None  # What caused it
    
    def tick(self) -> bool:
        """Reduce duration. Returns True if expired."""
        if self.duration > 0:
            self.duration -= 1
            return self.duration == 0
        return False

class DQMStatusManager:
    """Manages all status effects for a monster."""
    
    def __init__(self, monster: Any):
        self.monster = monster
        self.active_statuses: Dict[DQMStatus, StatusEffect] = {}
        self.status_resistances: Dict[DQMStatus, float] = {}
        
    def apply_status(self, status: DQMStatus, duration: int = 3, 
                    potency: float = 1.0, source: str = None) -> bool:
        """
        Apply a status effect.
        
        Returns:
            True if status was applied, False if resisted
        """
        # Check immunity
        if self.is_immune(status):
            logger.info(f"{self.monster.name} ist immun gegen {status.value}!")
            return False
        
        # Check resistance
        if self.check_resistance(status):
            logger.info(f"{self.monster.name} widersteht {status.value}!")
            return False
        
        # Remove conflicting statuses
        self._remove_conflicts(status)
        
        # Apply the status
        self.active_statuses[status] = StatusEffect(
            status=status,
            duration=duration,
            potency=potency,
            source=source
        )
        
        logger.info(f"{self.monster.name} hat jetzt {status.value}!")
        
        # Apply immediate effects
        self._apply_immediate_effects(status)
        
        return True
    
    def remove_status(self, status: DQMStatus) -> bool:
        """Remove a status effect."""
        if status in self.active_statuses:
            del self.active_statuses[status]
            self._remove_status_effects(status)
            return True
        return False
    
    def cure_all_status(self):
        """Remove all negative status effects."""
        negative_statuses = [
            DQMStatus.POISON, DQMStatus.PARALYSIS, DQMStatus.SLEEP,
            DQMStatus.CONFUSION, DQMStatus.BURN, DQMStatus.FREEZE,
            DQMStatus.DAZZLE, DQMStatus.CURSE, DQMStatus.SILENCE,
            DQMStatus.BLIND, DQMStatus.CHARM, DQMStatus.FEAR
        ]
        
        for status in negative_statuses:
            self.remove_status(status)
    
    def process_turn_start(self) -> Dict[str, Any]:
        """Process status effects at turn start."""
        effects = {}
        
        # Check if can act
        if DQMStatus.SLEEP in self.active_statuses:
            if random.random() < 0.25:  # 25% wake chance
                self.remove_status(DQMStatus.SLEEP)
                effects['message'] = f"{self.monster.name} wacht auf!"
            else:
                effects['skip_turn'] = True
                effects['message'] = f"{self.monster.name} schläft!"
                
        elif DQMStatus.PARALYSIS in self.active_statuses:
            if random.random() < 0.25:  # 25% paralysis
                effects['skip_turn'] = True
                effects['message'] = f"{self.monster.name} ist paralysiert!"
                
        elif DQMStatus.FREEZE in self.active_statuses:
            if random.random() < 0.20:  # 20% thaw chance
                self.remove_status(DQMStatus.FREEZE)
                effects['message'] = f"{self.monster.name} ist aufgetaut!"
            else:
                effects['skip_turn'] = True
                effects['message'] = f"{self.monster.name} ist eingefroren!"
        
        # Confusion
        if DQMStatus.CONFUSION in self.active_statuses:
            if random.random() < 0.33:  # 33% confusion
                effects['confused'] = True
                effects['message'] = f"{self.monster.name} ist verwirrt!"
        
        # Berserk auto-attack
        if DQMStatus.BERSERK in self.active_statuses:
            effects['force_attack'] = True
            effects['damage_bonus'] = 1.5
            effects['message'] = f"{self.monster.name} greift wild an!"
        
        return effects
    
    def process_turn_end(self) -> Dict[str, Any]:
        """Process status effects at turn end."""
        effects = {}
        damage = 0
        
        # Poison damage
        if DQMStatus.POISON in self.active_statuses:
            poison_damage = max(1, int(self.monster.max_hp * 0.0625))  # 1/16 HP
            damage += poison_damage
            
        # Burn damage
        if DQMStatus.BURN in self.active_statuses:
            burn_damage = max(1, int(self.monster.max_hp * 0.0625))
            damage += burn_damage
        
        # Apply damage
        if damage > 0:
            self.monster.current_hp = max(0, self.monster.current_hp - damage)
            effects['damage'] = damage
            effects['message'] = f"{self.monster.name} nimmt {damage} Status-Schaden!"
        
        # Tick durations
        expired = []
        for status, effect in self.active_statuses.items():
            if effect.tick():
                expired.append(status)
        
        # Remove expired
        for status in expired:
            self.remove_status(status)
            effects['expired'] = effects.get('expired', [])
            effects['expired'].append(status.value)
        
        return effects
    
    def can_use_magic(self) -> bool:
        """Check if monster can use magic."""
        return DQMStatus.DAZZLE not in self.active_statuses
    
    def can_use_skills(self) -> bool:
        """Check if monster can use skills."""
        return DQMStatus.SILENCE not in self.active_statuses
    
    def get_stat_modifiers(self) -> Dict[str, float]:
        """Get stat modifications from status."""
        modifiers = {
            'atk': 1.0, 'def': 1.0, 'mag': 1.0, 
            'res': 1.0, 'spd': 1.0, 'accuracy': 1.0
        }
        
        # Burn reduces ATK
        if DQMStatus.BURN in self.active_statuses:
            modifiers['atk'] *= 0.75
        
        # Curse reduces all stats
        if DQMStatus.CURSE in self.active_statuses:
            for stat in modifiers:
                modifiers[stat] *= 0.75
        
        # Blind reduces accuracy
        if DQMStatus.BLIND in self.active_statuses:
            modifiers['accuracy'] *= 0.6
        
        # Berserk increases ATK
        if DQMStatus.BERSERK in self.active_statuses:
            modifiers['atk'] *= 1.5
        
        return modifiers
    
    def should_reflect_magic(self) -> bool:
        """Check if magic should be reflected."""
        return DQMStatus.BOUNCE in self.active_statuses
    
    def is_immune(self, status: DQMStatus) -> bool:
        """Check if immune to status."""
        # Check monster traits
        if hasattr(self.monster, 'traits'):
            if 'Status Guard' in self.monster.traits and random.random() < 0.5:
                return True
        
        # Type-based immunities
        if hasattr(self.monster, 'types'):
            types = self.monster.types
            if 'fire' in types and status == DQMStatus.BURN:
                return True
            if 'ice' in types and status == DQMStatus.FREEZE:
                return True
        
        return False
    
    def check_resistance(self, status: DQMStatus) -> bool:
        """Roll for status resistance."""
        base_resistance = self.status_resistances.get(status, 0.0)
        
        # Level-based resistance
        if hasattr(self.monster, 'level'):
            level_bonus = self.monster.level * 0.01  # 1% per level
            base_resistance += level_bonus
        
        return random.random() < base_resistance
    
    def _remove_conflicts(self, new_status: DQMStatus):
        """Remove conflicting statuses."""
        conflicts = {
            DQMStatus.SLEEP: [DQMStatus.BERSERK, DQMStatus.CONFUSION],
            DQMStatus.BERSERK: [DQMStatus.SLEEP, DQMStatus.FEAR, DQMStatus.CHARM],
            DQMStatus.FREEZE: [DQMStatus.BURN],
            DQMStatus.BURN: [DQMStatus.FREEZE]
        }
        
        if new_status in conflicts:
            for conflict in conflicts[new_status]:
                self.remove_status(conflict)
    
    def _apply_immediate_effects(self, status: DQMStatus):
        """Apply effects that happen immediately."""
        if status == DQMStatus.CURSE:
            # Reset all stat stages to 0
            if hasattr(self.monster, 'stat_stages'):
                for stat in self.monster.stat_stages:
                    self.monster.stat_stages[stat] = 0
    
    def _remove_status_effects(self, status: DQMStatus):
        """Clean up when status is removed."""
        # Restore any modified stats
        pass
    
    def get_status_icons(self) -> List[str]:
        """Get list of status icons to display."""
        icons = []
        icon_map = {
            DQMStatus.POISON: "🟢",
            DQMStatus.BURN: "🔥",
            DQMStatus.FREEZE: "❄️",
            DQMStatus.SLEEP: "💤",
            DQMStatus.PARALYSIS: "⚡",
            DQMStatus.CONFUSION: "💫",
            DQMStatus.DAZZLE: "✨",
            DQMStatus.CURSE: "💀",
            DQMStatus.BERSERK: "😤",
            DQMStatus.BOUNCE: "🛡️"
        }
        
        for status in self.active_statuses:
            if status in icon_map:
                icons.append(icon_map[status])
        
        return icons

# Export main components
__all__ = ['DQMStatus', 'StatusEffect', 'DQMStatusManager', 'StatusEffectSystem', 'StatusType']


# Alias for compatibility
StatusEffectSystem = DQMStatusManager
StatusType = DQMStatus
