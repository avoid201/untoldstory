"""
Simplified MonsterInstance for 3v3 Battle Testing
This is a temporary implementation for testing the 3v3 system
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class MonsterSpecies:
    """Monster species data"""
    id: int
    name: str
    base_stats: Dict[str, int]
    types: List[str]
    rank: str = "F"
    abilities: List[str] = None
    evolution_level: Optional[int] = None
    evolution_to: Optional[int] = None
    
    def __post_init__(self):
        if self.abilities is None:
            self.abilities = []

class StatusCondition(Enum):
    """Status conditions for monsters"""
    NORMAL = "normal"
    POISON = "poison"
    BURN = "burn"
    PARALYSIS = "paralysis"
    SLEEP = "sleep"
    FREEZE = "freeze"
    CONFUSION = "confusion"

class MonsterInstance:
    """Simplified monster instance for battle testing"""
    
    def __init__(self, species_id: str = "test", level: int = 5, **kwargs):
        # Basic info
        self.species_id = species_id
        self.id = kwargs.get('id', species_id)  # For compatibility
        self.level = level
        self.name = kwargs.get('name', f"Monster_{species_id}")
        self.species_name = kwargs.get('species_name', self.name)
        self.species = kwargs.get('species', None)
        self.nickname = kwargs.get('nickname', None)
        self.rank = kwargs.get('rank', 'F')
        self.experience = kwargs.get('experience', 0)
        
        # HP/MP
        # Use stats['hp'] if available, otherwise calculate
        hp_stat = self.stats.get('hp', 100) if hasattr(self, 'stats') else 100
        self.max_hp = kwargs.get('max_hp', hp_stat + level * 10)
        self.current_hp = kwargs.get('current_hp', self.max_hp)
        
        # Ensure HP is never 0 on creation
        if self.current_hp <= 0:
            self.current_hp = self.max_hp
        self.max_mp = kwargs.get('max_mp', 50 + level * 5)
        self.current_mp = kwargs.get('current_mp', self.max_mp)
        
        # Stats
        base_stat = 40 + level * 2
        self.stats = kwargs.get('stats', {
            'atk': base_stat,
            'def': base_stat - 5,
            'mag': base_stat - 10,
            'res': base_stat - 10,
            'agility': base_stat,
            'speed': base_stat  # Alias for agility
        })
        
        # Status
        self.status = StatusCondition.NORMAL
        self.is_fainted = False
        self.stat_stages = {'atk': 0, 'def': 0, 'mag': 0, 'res': 0, 'spd': 0}
        
        # Moves (simplified)
        self.moves = kwargs.get('moves', [])
        if not self.moves:
            # Create some default moves
            from dataclasses import dataclass
            
            # Default moves
            from dataclasses import dataclass
            
            @dataclass
            class Move:
                name: str
                power: int
                pp: int
                max_pp: int
                target_type: str = "single"
                element: str = "normal"
                
                @property
                def id(self):
                    """Generate ID from name."""
                    return self.name.lower().replace(" ", "_")
                
                @property 
                def category(self):
                    """Determine category."""
                    return "phys" if self.element in ["normal", "fighting"] else "mag"

            self.moves = [
                Move("Tackle", 40, 35, 35),
                Move("Fireball", 50, 20, 20, "single", "fire"),
                Move("Ice Storm", 45, 15, 15, "all", "ice"),
                Move("Heal", 0, 10, 10, "self", "heal")
            ]
    
    def take_damage(self, damage: int) -> int:
        """Take damage and update status"""
        actual_damage = min(damage, self.current_hp)
        self.current_hp -= actual_damage
        
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_fainted = True
            self.status = StatusCondition.NORMAL  # Clear status on faint
        
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """Heal HP"""
        if self.is_fainted:
            return 0
        
        actual_heal = min(amount, self.max_hp - self.current_hp)
        self.current_hp += actual_heal
        return actual_heal
    
    def use_mp(self, amount: int) -> bool:
        """Use MP for a skill"""
        if self.current_mp >= amount:
            self.current_mp -= amount
            return True
        return False
    
    def restore_mp(self, amount: int) -> int:
        """Restore MP"""
        actual_restore = min(amount, self.max_mp - self.current_mp)
        self.current_mp += actual_restore
        return actual_restore
    
    def get_stat(self, stat_name: str) -> int:
        """Get effective stat value with stages"""
        base_value = self.stats.get(stat_name, 50)
        
        # Apply stat stages if they exist
        if hasattr(self, 'stat_stages') and stat_name in self.stat_stages:
            stage = self.stat_stages[stat_name]
            # Each stage is 10% boost/reduction
            multiplier = 1.0 + (stage * 0.1)
            return int(base_value * multiplier)
        
        return base_value
    
    def reset_stat_stages(self):
        """Reset all stat stages to 0"""
        self.stat_stages = {'atk': 0, 'def': 0, 'mag': 0, 'res': 0, 'spd': 0}
    
    def apply_status(self, status: StatusCondition) -> bool:
        """Apply a status condition"""
        if self.is_fainted:
            return False
        
        if self.status == StatusCondition.NORMAL:
            self.status = status
            return True
        
        return False  # Already has a status
    
    def cure_status(self):
        """Remove status condition"""
        self.status = StatusCondition.NORMAL
    
    def can_act(self) -> bool:
        """Check if monster can take action"""
        if self.is_fainted:
            return False
        
        if self.status in [StatusCondition.SLEEP, StatusCondition.FREEZE]:
            return False
        
        if self.status == StatusCondition.PARALYSIS:
            # 25% chance to not act
            import random
            return random.random() > 0.25
        
        return True
    
    def __repr__(self):
        return f"MonsterInstance({self.name}, Lv{self.level}, HP:{self.current_hp}/{self.max_hp})"
    
    def __str__(self):
        return self.name
    
    @classmethod
    def create_from_species(cls, species: 'MonsterSpecies', level: int = 1) -> 'MonsterInstance':
        """Create a monster instance from species data"""
        # Handle both dict and object
        if isinstance(species, dict):
            species_id = species.get('id', 'unknown')
            name = species.get('name', 'Unknown')
            base_stats = species.get('base_stats', {})
            rank = species.get('rank', 'F')
        else:
            species_id = getattr(species, 'id', 'unknown')
            name = getattr(species, 'name', 'Unknown')
            base_stats = getattr(species, 'base_stats', {})
            rank = getattr(species, 'rank', 'F')
        
        # Calculate stats based on level
        stats = {}
        for stat_name, base_value in base_stats.items():
            # Simple level scaling
            stats[stat_name] = base_value + (level - 1) * 2
        
        # Ensure all required stats exist
        required_stats = ['hp', 'atk', 'def', 'mag', 'res', 'spd']
        for stat in required_stats:
            if stat not in stats:
                stats[stat] = 40 + level * 2
        
        # Calculate HP and MP
        max_hp = stats.get('hp', 100) + level * 10
        max_mp = 50 + level * 5
        
        return cls(
            species_id=str(species_id),
            level=level,
            name=name,
            species_name=name,
            species=species,
            max_hp=max_hp,
            current_hp=max_hp,
            max_mp=max_mp,
            current_mp=max_mp,
            stats=stats,
            rank=rank
        )
    
    def gain_exp(self, amount: int):
        """Gain experience points"""
        self.experience += amount
        # Simple level up check
        exp_needed = self.level * 100
        while self.experience >= exp_needed:
            self.experience -= exp_needed
            self.level += 1
            # Increase stats on level up
            for stat in self.stats:
                self.stats[stat] += 2
            self.max_hp += 10
            self.current_hp = self.max_hp
            self.max_mp += 5
            self.current_mp = self.max_mp
            exp_needed = self.level * 100


# For backwards compatibility
def create_test_monster(name: str = "TestMonster", **kwargs) -> MonsterInstance:
    """Factory function to create test monsters"""
    return MonsterInstance(species_id="test", name=name, **kwargs)


# Export all classes
__all__ = ['MonsterSpecies', 'MonsterInstance', 'StatusCondition', 'create_test_monster']
