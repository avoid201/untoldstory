"""
Move System for Untold Story
Handles move data, effects, and execution
"""

from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum
from dataclasses import dataclass
from engine.core.resources import resources


class MoveCategory(Enum):
    """Categories of moves."""
    PHYSICAL = "phys"
    MAGICAL = "mag"
    SUPPORT = "support"


class MoveTarget(Enum):
    """Targeting options for moves."""
    ENEMY = "enemy"                # Single enemy
    ALLY = "ally"                  # Single ally
    SELF = "self"                  # Self only
    ALL_ENEMIES = "all_enemies"    # All enemies
    ALL_ALLIES = "all_allies"      # All allies
    ALL = "all"                    # Everyone
    RANDOM = "random"              # Random target


class EffectKind(Enum):
    """Types of move effects."""
    DAMAGE = "damage"
    HEAL = "heal"
    BUFF = "buff"
    DEBUFF = "debuff"
    STATUS = "status"
    CURE = "cure"
    FIELD = "field"
    SWITCH = "switch"
    PROTECT = "protect"
    RECOIL = "recoil"
    DRAIN = "drain"
    DOT = "dot"


@dataclass
class MoveEffect:
    """Single effect of a move."""
    kind: EffectKind
    chance: float = 100.0  # Chance of effect occurring (0-100)
    
    # Effect-specific parameters
    power: Optional[int] = None  # For damage/heal
    stat: Optional[str] = None  # For buff/debuff
    stages: Optional[int] = None  # For buff/debuff
    status: Optional[str] = None  # For status effects
    amount: Optional[int] = None  # Generic amount
    percent: bool = False  # Whether amount is percentage
    duration: Optional[int] = None  # Effect duration
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MoveEffect':
        """Create from dictionary data."""
        return cls(
            kind=EffectKind(data["kind"]),
            chance=data.get("chance", 100.0),
            power=data.get("power"),
            stat=data.get("stat"),
            stages=data.get("stages"),
            status=data.get("status"),
            amount=data.get("amount"),
            percent=data.get("percent", False),
            duration=data.get("duration")
        )


@dataclass
class Move:
    """Complete move data."""
    id: str
    name: str
    type: str
    category: MoveCategory
    power: int
    accuracy: int
    pp: int
    max_pp: int
    priority: int
    targeting: MoveTarget
    effects: List[MoveEffect]
    description: str
    
    # Optional advanced properties
    contact: bool = False
    sound_based: bool = False
    punching: bool = False
    biting: bool = False
    pulse: bool = False
    multi_hit: Optional[Tuple[int, int]] = None  # (min_hits, max_hits)
    
    def get_damage_power(self) -> int:
        """Get the base damage power of the move."""
        if self.category == MoveCategory.SUPPORT:
            return 0
        return self.power
    
    def has_effect(self, effect_kind: EffectKind) -> bool:
        """Check if move has a specific effect type."""
        return any(e.kind == effect_kind for e in self.effects)
    
    def get_effect(self, effect_kind: EffectKind) -> Optional[MoveEffect]:
        """Get the first effect of a specific type."""
        for effect in self.effects:
            if effect.kind == effect_kind:
                return effect
        return None
    
    def can_use(self) -> bool:
        """Check if the move can be used (has PP)."""
        return self.pp > 0
    
    def use(self) -> bool:
        """
        Use the move (decrease PP).
        
        Returns:
            True if move was used, False if out of PP
        """
        if self.pp > 0:
            self.pp -= 1
            return True
        return False
    
    def restore_pp(self, amount: int = -1) -> int:
        """
        Restore PP for the move.
        
        Args:
            amount: Amount to restore (-1 for full)
            
        Returns:
            Amount of PP actually restored
        """
        if amount < 0:
            restored = self.max_pp - self.pp
            self.pp = self.max_pp
        else:
            restored = min(amount, self.max_pp - self.pp)
            self.pp += restored
        return restored


class MoveRegistry:
    """
    Central registry for all moves in the game.
    Singleton that loads and caches move data.
    """
    
    _instance: Optional['MoveRegistry'] = None
    
    def __new__(cls) -> 'MoveRegistry':
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize the move registry."""
        if self._initialized:
            return
        
        self._initialized = True
        self.moves: Dict[str, Move] = {}
        self.moves_by_type: Dict[str, List[str]] = {}
        self.moves_by_category: Dict[MoveCategory, List[str]] = {}
        
        # Load move data
        self._load_move_data()
    
    def _load_move_data(self) -> None:
        """Load move data from JSON."""
        try:
            move_data = resources.load_json("moves.json")
            
            for move_dict in move_data.get("moves", []):
                move = self._create_move_from_dict(move_dict)
                self.register_move(move)
                
        except Exception as e:
            print(f"Error loading move data: {e}")
            # Create a default tackle move
            self._create_default_moves()
    
    def _create_move_from_dict(self, data: Dict[str, Any]) -> Move:
        """Create a Move object from dictionary data."""
        # Parse effects
        effects = []
        for effect_data in data.get("effects", []):
            effects.append(MoveEffect.from_dict(effect_data))
        
        # Create move
        move = Move(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            category=MoveCategory(data["category"]),
            power=data.get("power", 0),
            accuracy=data.get("accuracy", 100),
            pp=data.get("pp", 10),
            max_pp=data.get("pp", 10),
            priority=data.get("priority", 0),
            targeting=MoveTarget(data.get("targeting", "enemy")),
            effects=effects,
            description=data.get("description", "")
        )
        
        # Set optional properties
        move.contact = data.get("contact", False)
        move.sound_based = data.get("sound_based", False)
        move.punching = data.get("punching", False)
        move.biting = data.get("biting", False)
        move.pulse = data.get("pulse", False)
        
        if "multi_hit" in data:
            move.multi_hit = tuple(data["multi_hit"])
        
        return move
    
    def _create_default_moves(self) -> None:
        """Create default moves if loading fails."""
        tackle = Move(
            id="tackle",
            name="Rempler",
            type="Bestie",
            category=MoveCategory.PHYSICAL,
            power=40,
            accuracy=100,
            pp=35,
            max_pp=35,
            priority=0,
            targeting=MoveTarget.ENEMY,
            effects=[],
            description="Ein einfacher Körperangriff.",
            contact=True
        )
        self.register_move(tackle)
    
    def register_move(self, move: Move) -> None:
        """
        Register a move in the registry.
        
        Args:
            move: Move to register
        """
        self.moves[move.id] = move
        
        # Index by type
        if move.type not in self.moves_by_type:
            self.moves_by_type[move.type] = []
        self.moves_by_type[move.type].append(move.id)
        
        # Index by category
        if move.category not in self.moves_by_category:
            self.moves_by_category[move.category] = []
        self.moves_by_category[move.category].append(move.id)
    
    def get_move(self, move_id: str) -> Optional[Move]:
        """
        Get a move by ID.
        
        Args:
            move_id: Move identifier
            
        Returns:
            Move object or None if not found
        """
        return self.moves.get(move_id)
    
    def create_move_instance(self, move_id: str) -> Optional[Move]:
        """
        Create a new instance of a move (with full PP).
        
        Args:
            move_id: Move identifier
            
        Returns:
            New Move instance or None if not found
        """
        template = self.get_move(move_id)
        if not template:
            return None
        
        # Create a copy with full PP
        import copy
        move = copy.deepcopy(template)
        move.pp = move.max_pp
        return move
    
    def get_moves_by_type(self, move_type: str) -> List[Move]:
        """Get all moves of a specific type."""
        move_ids = self.moves_by_type.get(move_type, [])
        return [self.moves[mid] for mid in move_ids if mid in self.moves]
    
    def get_moves_by_category(self, category: MoveCategory) -> List[Move]:
        """Get all moves of a specific category."""
        move_ids = self.moves_by_category.get(category, [])
        return [self.moves[mid] for mid in move_ids if mid in self.moves]
    
    def get_learnable_moves(self, monster_type: str, level: int) -> List[str]:
        """
        Get moves that could be learned by a monster type at a level.
        
        Args:
            monster_type: Monster's type
            level: Monster's level
            
        Returns:
            List of move IDs
        """
        # This would normally check a learnset database
        # For now, return moves matching the monster's type
        return self.moves_by_type.get(monster_type, [])[:4]


class MoveExecutor:
    """Handles the execution of moves in battle."""
    
    @staticmethod
    def execute_move(move: Move, user: 'MonsterInstance', 
                     target: 'MonsterInstance',
                     battle_context: Optional[Any] = None) -> Dict[str, Any]:
        """
        Execute a move and return the results.
        
        Args:
            move: Move to execute
            user: Monster using the move
            target: Target of the move
            battle_context: Optional battle state for context
            
        Returns:
            Dictionary with execution results
        """
        results = {
            "success": False,
            "damage": 0,
            "healing": 0,
            "effects": [],
            "messages": []
        }
        
        # Check accuracy
        import random
        if random.randint(1, 100) > move.accuracy:
            results["messages"].append(f"{user.name} verfehlt!")
            return results
        
        results["success"] = True
        
        # Process each effect
        for effect in move.effects:
            if random.random() * 100 > effect.chance:
                continue  # Effect didn't trigger
            
            effect_result = MoveExecutor._apply_effect(
                effect, move, user, target, battle_context
            )
            results["effects"].append(effect_result)
            
            # Aggregate results
            if "damage" in effect_result:
                results["damage"] += effect_result["damage"]
            if "healing" in effect_result:
                results["healing"] += effect_result["healing"]
            if "message" in effect_result:
                results["messages"].append(effect_result["message"])
        
        # Apply base damage if it's a damaging move
        if move.category != MoveCategory.SUPPORT and move.power > 0:
            damage = MoveExecutor._calculate_damage(
                move, user, target, battle_context
            )
            results["damage"] = damage
            
            if damage > 0:
                results["messages"].append(
                    f"{target.name} nimmt {damage} Schaden!"
                )
        
        return results
    
    @staticmethod
    def _apply_effect(effect: MoveEffect, move: Move,
                     user: 'MonsterInstance', target: 'MonsterInstance',
                     battle_context: Optional[Any]) -> Dict[str, Any]:
        """Apply a single move effect."""
        result = {"type": effect.kind.value}
        
        if effect.kind == EffectKind.HEAL:
            amount = effect.amount or 50
            if effect.percent:
                healing = int(target.max_hp * (amount / 100))
            else:
                healing = amount
            
            result["healing"] = healing
            result["message"] = f"{target.name} heilt {healing} HP!"
            
        elif effect.kind == EffectKind.BUFF:
            result["stat"] = effect.stat
            result["stages"] = effect.stages
            result["message"] = f"{target.name}'s {effect.stat} steigt!"
            
        elif effect.kind == EffectKind.DEBUFF:
            result["stat"] = effect.stat
            result["stages"] = -abs(effect.stages or 1)
            result["message"] = f"{target.name}'s {effect.stat} sinkt!"
            
        elif effect.kind == EffectKind.STATUS:
            result["status"] = effect.status
            result["message"] = f"{target.name} wird {effect.status}!"
        
        return result
    
    @staticmethod
    def _calculate_damage(move: Move, user: 'MonsterInstance',
                         target: 'MonsterInstance',
                         battle_context: Optional[Any]) -> int:
        """Calculate damage for a move."""
        # This is simplified - full implementation would use DamageCalculator
        if move.category == MoveCategory.PHYSICAL:
            attack = user.stats["atk"]
            defense = target.stats["def"]
        else:
            attack = user.stats["mag"]
            defense = target.stats["res"]
        
        # Basic damage formula
        import random
        base_damage = ((2 * user.level / 5 + 2) * move.power * attack / defense) / 50 + 2
        
        # Random factor
        base_damage *= random.uniform(0.85, 1.0)
        
        return max(1, int(base_damage))


# Global singleton instance
move_registry = MoveRegistry()