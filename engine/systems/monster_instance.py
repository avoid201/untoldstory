"""
Monster Instance System for Untold Story
Individual monster instances with stats, moves, and progression
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import random
from engine.systems.stats import BaseStats, StatCalculator, Experience, GrowthCurve, StatStages
from engine.systems.moves import Move, move_registry
from engine.core.resources import resources


class StatusCondition(Enum):
    """Status conditions that can affect monsters."""
    NONE = "none"
    BURN = "burn"          # Feuer damage over time, halves ATK
    POISON = "poison"      # Seuche damage over time
    PARALYSIS = "paralysis"  # May skip turn, reduces SPD
    SLEEP = "sleep"        # Cannot act for 1-3 turns
    FREEZE = "freeze"      # Cannot act until thawed
    CONFUSION = "confusion"  # May hurt itself
    FLINCH = "flinch"      # Skip next turn only


class MonsterRank(Enum):
    """Monster rarity/power ranks."""
    F = "F"   # Common fodder
    E = "E"   # Common
    D = "D"   # Uncommon  
    C = "C"   # Uncommon+
    B = "B"   # Rare
    A = "A"   # Rare+
    S = "S"   # Epic
    SS = "SS"  # Epic+
    X = "X"   # Legendary
    
    @property
    def capture_difficulty(self) -> float:
        """Get capture difficulty modifier for this rank."""
        modifiers = {
            "F": 1.5, "E": 1.2, "D": 1.0, "C": 0.9,
            "B": 0.8, "A": 0.7, "S": 0.5, "SS": 0.3, "X": 0.1
        }
        return modifiers.get(self.value, 1.0)
    
    @property
    def exp_modifier(self) -> float:
        """Get experience yield modifier for this rank."""
        modifiers = {
            "F": 0.8, "E": 1.0, "D": 1.1, "C": 1.2,
            "B": 1.4, "A": 1.6, "S": 2.0, "SS": 2.5, "X": 3.0
        }
        return modifiers.get(self.value, 1.0)


@dataclass
class MonsterSpecies:
    """Static data for a monster species."""
    id: int
    name: str
    era: str  # past, present, future
    rank: MonsterRank
    types: List[str]
    base_stats: BaseStats
    growth_curve: GrowthCurve
    base_exp_yield: int
    capture_rate: int  # 0-255, higher = easier
    traits: List[str]
    learnset: List[Tuple[int, str]]  # [(level, move_id), ...]
    evolution: Optional[Dict[str, Any]]  # level, item, trade, etc.
    description: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MonsterSpecies':
        """Create from dictionary data."""
        return cls(
            id=data["id"],
            name=data["name"],
            era=data["era"],
            rank=MonsterRank(data["rank"]),
            types=data["types"],
            base_stats=BaseStats.from_dict(data["base_stats"]),
            growth_curve=GrowthCurve(data["growth"]["curve"]),
            base_exp_yield=data["growth"]["yield"],
            capture_rate=data["capture_rate"],
            traits=data.get("traits", []),
            learnset=[(l["level"], l["move"]) for l in data.get("learnset", [])],
            evolution=data.get("evolution"),
            description=data.get("description", "")
        )


class MonsterInstance:
    """
    An individual monster with its own stats, moves, and state.
    """
    
    def __init__(self, species: MonsterSpecies, level: int = 5,
                 nickname: Optional[str] = None):
        """
        Create a monster instance.
        
        Args:
            species: The species data
            level: Starting level
            nickname: Optional nickname
        """
        self.species = species
        self.nickname = nickname
        self.level = level
        
        # Individual Values (IVs) - genetic potential (0-31)
        self.ivs = self._generate_ivs()
        
        # Effort Values (EVs) - training bonuses (0-255 per stat, 510 total)
        self.evs = {
            "hp": 0, "atk": 0, "def": 0,
            "mag": 0, "res": 0, "spd": 0
        }
        
        # Nature (affects stat growth)
        self.nature = self._generate_nature()
        
        # Calculate stats
        self.stats = self._calculate_stats()
        self.max_hp = self.stats["hp"]
        self.current_hp = self.max_hp
        
        # Battle stats (stages)
        self.stat_stages = StatStages()
        
        # Status
        self.status = StatusCondition.NONE
        self.status_turns = 0
        
        # Moves (max 4)
        self.moves: List[Move] = []
        self._learn_initial_moves()
        
        # Experience
        self.exp = Experience.get_exp_for_level(level, species.growth_curve)
        
        # Traits/Abilities
        self.traits = species.traits.copy()
        self.held_item: Optional[str] = None
        
        # Battle state
        self.is_fainted = False
        self.turns_in_battle = 0
        
        # Capture info
        self.original_trainer = None
        self.capture_location = None
        self.capture_level = level

    # ---------------------- Kompatibilitäts-Hilfsmethoden ----------------------

    @classmethod
    def create_from_species(cls, species: Any, level: int = 5, **kwargs) -> 'MonsterInstance':
        """Erstellt eine MonsterInstance aus Spezies-Daten.

        Akzeptiert sowohl bereits geparste ``MonsterSpecies`` als auch ein ``dict``
        (z. B. direkt aus ``resources.get_monster_species``). Dadurch bleiben ältere
        Aufrufe wie ``MonsterInstance.create_from_species(species=..., level=...)``
        funktionsfähig.
        """
        if species is None:
            raise ValueError("species darf nicht None sein")

        # Falls ein Dict übergeben wurde – in MonsterSpecies konvertieren
        if isinstance(species, dict):
            species = MonsterSpecies.from_dict(species)

        if not isinstance(species, MonsterSpecies):
            raise TypeError("species muss MonsterSpecies oder dict sein")

        return cls(species, level, nickname=kwargs.get("nickname"))
    
    @property
    def name(self) -> str:
        """Get display name (nickname or species name)."""
        return self.nickname or self.species.name
    
    @property
    def types(self) -> List[str]:
        """Get monster's types."""
        return self.species.types
    
    @property
    def rank(self) -> MonsterRank:
        """Get monster's rank."""
        return self.species.rank
    
    def _generate_ivs(self) -> Dict[str, int]:
        """Generate random Individual Values."""
        return {
            "hp": random.randint(0, 31),
            "atk": random.randint(0, 31),
            "def": random.randint(0, 31),
            "mag": random.randint(0, 31),
            "res": random.randint(0, 31),
            "spd": random.randint(0, 31)
        }
    
    def _generate_nature(self) -> str:
        """Generate a random nature."""
        natures = [
            "Hardy", "Lonely", "Brave", "Adamant", "Naughty",
            "Bold", "Docile", "Relaxed", "Impish", "Lax",
            "Timid", "Hasty", "Serious", "Jolly", "Naive",
            "Modest", "Mild", "Quiet", "Bashful", "Rash",
            "Calm", "Gentle", "Sassy", "Careful", "Quirky"
        ]
        return random.choice(natures)
    
    def _calculate_stats(self) -> Dict[str, int]:
        """Calculate actual stats based on level, IVs, EVs, and nature."""
        return StatCalculator.calculate_all_stats(
            self.species.base_stats,
            self.level,
            self.ivs,
            self.evs,
            self.nature
        )
    
    def _learn_initial_moves(self) -> None:
        """Learn moves available at current level."""
        self.moves = []
        
        # Get all moves learnable up to current level
        learnable = []
        for learn_level, move_id in self.species.learnset:
            if learn_level <= self.level:
                learnable.append((learn_level, move_id))
        
        # Sort by level (newest first) and take up to 4
        learnable.sort(key=lambda x: x[0], reverse=True)
        
        for _, move_id in learnable[:4]:
            move = move_registry.create_move_instance(move_id)
            if move and move not in self.moves:
                self.moves.append(move)
    
    def gain_exp(self, amount: int) -> Dict[str, Any]:
        """
        Gain experience points.
        
        Args:
            amount: Experience points to gain
            
        Returns:
            Dictionary with level up info
        """
        result = {
            "exp_gained": amount,
            "leveled_up": False,
            "new_level": self.level,
            "new_moves": [],
            "evolved": False
        }
        
        old_level = self.level
        self.exp += amount
        
        # Check for level up
        new_level = Experience.get_level_from_exp(
            self.exp, self.species.growth_curve
        )
        
        if new_level > old_level:
            result["leveled_up"] = True
            result["new_level"] = new_level
            
            # Level up each level individually to learn moves
            for level in range(old_level + 1, new_level + 1):
                self.level = level
                self._recalculate_stats()
                
                # Check for new moves
                new_moves = self._check_new_moves(level)
                result["new_moves"].extend(new_moves)
                
                # Check for evolution
                if self._check_evolution(level):
                    result["evolved"] = True
        
        return result
    
    def _recalculate_stats(self) -> None:
        """Recalculate stats after level up."""
        old_max_hp = self.max_hp
        self.stats = self._calculate_stats()
        self.max_hp = self.stats["hp"]
        
        # Increase current HP by the same amount max HP increased
        hp_increase = self.max_hp - old_max_hp
        self.current_hp = min(self.current_hp + hp_increase, self.max_hp)
    
    def _check_new_moves(self, level: int) -> List[str]:
        """Check if any new moves are learned at this level."""
        new_moves = []
        
        for learn_level, move_id in self.species.learnset:
            if learn_level == level:
                new_moves.append(move_id)
        
        return new_moves
    
    def learn_move(self, move_id: str, slot: Optional[int] = None) -> bool:
        """
        Learn a new move.
        
        Args:
            move_id: ID of move to learn
            slot: Optional slot to replace (0-3), None to append
            
        Returns:
            True if move was learned
        """
        move = move_registry.create_move_instance(move_id)
        if not move:
            return False
        
        # Check if already knows the move
        if any(m.id == move_id for m in self.moves):
            return False
        
        if slot is not None and 0 <= slot < len(self.moves):
            # Replace existing move
            self.moves[slot] = move
            return True
        elif len(self.moves) < 4:
            # Add to empty slot
            self.moves.append(move)
            return True
        
        return False
    
    def _check_evolution(self, level: int) -> bool:
        """Check if monster should evolve."""
        if not self.species.evolution:
            return False
        
        evo = self.species.evolution
        if evo.get("level") == level:
            # Would trigger evolution here
            return True
        
        return False
    
    def take_damage(self, damage: int) -> int:
        """
        Take damage.
        
        Args:
            damage: Amount of damage to take
            
        Returns:
            Actual damage taken
        """
        actual_damage = min(damage, self.current_hp)
        self.current_hp -= actual_damage
        
        if self.current_hp <= 0:
            self.current_hp = 0
            self.faint()
        
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """
        Heal HP.
        
        Args:
            amount: Amount to heal
            
        Returns:
            Actual amount healed
        """
        if self.is_fainted:
            return 0
        
        actual_heal = min(amount, self.max_hp - self.current_hp)
        self.current_hp += actual_heal
        return actual_heal
    
    def faint(self) -> None:
        """Handle fainting."""
        self.is_fainted = True
        self.status = StatusCondition.NONE
        self.stat_stages.reset()
    
    def revive(self, hp_percent: float = 0.5) -> None:
        """
        Revive from fainting.
        
        Args:
            hp_percent: Percentage of max HP to restore
        """
        if not self.is_fainted:
            return
        
        self.is_fainted = False
        self.current_hp = max(1, int(self.max_hp * hp_percent))
    
    def apply_status(self, status: StatusCondition) -> bool:
        """
        Apply a status condition.
        
        Args:
            status: Status to apply
            
        Returns:
            True if status was applied
        """
        # Can't apply status if already statused (except minor ones)
        major_statuses = [
            StatusCondition.BURN, StatusCondition.POISON,
            StatusCondition.PARALYSIS, StatusCondition.SLEEP,
            StatusCondition.FREEZE
        ]
        
        if self.status in major_statuses and status in major_statuses:
            return False
        
        self.status = status
        
        # Set duration for temporary statuses
        if status == StatusCondition.SLEEP:
            self.status_turns = random.randint(1, 3)
        elif status == StatusCondition.CONFUSION:
            self.status_turns = random.randint(2, 5)
        else:
            self.status_turns = 0
        
        return True
    
    def cure_status(self) -> bool:
        """
        Cure current status condition.
        
        Returns:
            True if status was cured
        """
        if self.status != StatusCondition.NONE:
            self.status = StatusCondition.NONE
            self.status_turns = 0
            return True
        return False
    
    def process_status(self) -> Dict[str, Any]:
        """
        Process status effects at turn end.
        
        Returns:
            Dictionary with status effect results
        """
        result = {
            "damage": 0,
            "skip_turn": False,
            "cured": False,
            "message": ""
        }
        
        if self.status == StatusCondition.BURN:
            # Burn damage: 1/16 of max HP
            damage = max(1, self.max_hp // 16)
            self.take_damage(damage)
            result["damage"] = damage
            result["message"] = f"{self.name} leidet unter Verbrennung!"
            
        elif self.status == StatusCondition.POISON:
            # Poison damage: 1/8 of max HP
            damage = max(1, self.max_hp // 8)
            self.take_damage(damage)
            result["damage"] = damage
            result["message"] = f"{self.name} leidet unter Vergiftung!"
            
        elif self.status == StatusCondition.SLEEP:
            self.status_turns -= 1
            if self.status_turns <= 0:
                self.cure_status()
                result["cured"] = True
                result["message"] = f"{self.name} wacht auf!"
            else:
                result["skip_turn"] = True
                result["message"] = f"{self.name} schläft fest!"
                
        elif self.status == StatusCondition.PARALYSIS:
            # 25% chance to be fully paralyzed
            if random.random() < 0.25:
                result["skip_turn"] = True
                result["message"] = f"{self.name} ist paralysiert!"
                
        elif self.status == StatusCondition.FREEZE:
            # 20% chance to thaw
            if random.random() < 0.2:
                self.cure_status()
                result["cured"] = True
                result["message"] = f"{self.name} taut auf!"
            else:
                result["skip_turn"] = True
                result["message"] = f"{self.name} ist eingefroren!"
                
        elif self.status == StatusCondition.CONFUSION:
            self.status_turns -= 1
            if self.status_turns <= 0:
                self.cure_status()
                result["cured"] = True
                result["message"] = f"{self.name} ist nicht mehr verwirrt!"
            else:
                # 33% chance to hurt itself
                if random.random() < 0.33:
                    damage = max(1, self.max_hp // 8)
                    self.take_damage(damage)
                    result["damage"] = damage
                    result["skip_turn"] = True
                    result["message"] = f"{self.name} verletzt sich selbst vor Verwirrung!"
        
        return result
    
    def get_catch_rate(self, hp_percent: float, status_bonus: float = 1.0) -> float:
        """
        Calculate catch rate for this monster.
        
        Args:
            hp_percent: Current HP as percentage (0.0-1.0)
            status_bonus: Multiplier from status conditions
            
        Returns:
            Catch rate (0.0-1.0)
        """
        base_rate = self.species.capture_rate / 255.0
        
        # Modify by rank
        base_rate *= self.rank.capture_difficulty
        
        # HP factor (lower HP = easier catch)
        hp_factor = 2.0 - hp_percent
        
        # Calculate final rate
        catch_rate = base_rate * hp_factor * status_bonus
        
        return min(1.0, catch_rate)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for saving."""
        return {
            "species_id": self.species.id,
            "nickname": self.nickname,
            "level": self.level,
            "exp": self.exp,
            "ivs": self.ivs,
            "evs": self.evs,
            "nature": self.nature,
            "current_hp": self.current_hp,
            "status": self.status.value,
            "moves": [{"id": m.id, "pp": m.pp} for m in self.moves],
            "traits": self.traits,
            "held_item": self.held_item,
            "original_trainer": self.original_trainer,
            "capture_location": self.capture_location,
            "capture_level": self.capture_level
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], species: MonsterSpecies) -> 'MonsterInstance':
        """Create from saved dictionary data."""
        instance = cls(species, data["level"], data.get("nickname"))
        instance.exp = data["exp"]
        instance.ivs = data["ivs"]
        instance.evs = data["evs"]
        instance.nature = data["nature"]
        instance.current_hp = data["current_hp"]
        instance.status = StatusCondition(data.get("status", "none"))
        instance.traits = data.get("traits", species.traits.copy())
        instance.held_item = data.get("held_item")
        instance.original_trainer = data.get("original_trainer")
        instance.capture_location = data.get("capture_location")
        instance.capture_level = data.get("capture_level", data["level"])
        
        # Restore moves with PP
        instance.moves = []
        for move_data in data.get("moves", []):
            move = move_registry.create_move_instance(move_data["id"])
            if move:
                move.pp = move_data.get("pp", move.max_pp)
                instance.moves.append(move)
        
        # Recalculate stats
        instance.stats = instance._calculate_stats()
        instance.max_hp = instance.stats["hp"]
        
        return instance