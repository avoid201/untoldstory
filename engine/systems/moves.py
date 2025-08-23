"""
Move System for Untold Story
Handles move data, effects, and execution
"""

from typing import Dict, List, Optional, Any, Callable, Tuple, Union
from enum import Enum
from dataclasses import dataclass
import logging
from engine.core.resources import resources

# Logger für bessere Fehlerverfolgung
logger = logging.getLogger(__name__)

class MoveCategory(Enum):
    """Categories of moves."""
    PHYSICAL = "phys"
    MAGICAL = "mag"
    SUPPORT = "support"
    
    @classmethod
    def from_string(cls, value: str) -> 'MoveCategory':
        """Konvertiere String zu MoveCategory mit Fallback."""
        try:
            if isinstance(value, str):
                return cls(value.lower())
            return value
        except (ValueError, AttributeError):
            return cls.PHYSICAL


class MoveTarget(Enum):
    """Targeting options for moves."""
    ENEMY = "enemy"                # Single enemy
    ALLY = "ally"                  # Single ally
    SELF = "self"                  # Self only
    ALL_ENEMIES = "all_enemies"    # All enemies
    ALL_ALLIES = "all_allies"      # All allies
    ALL = "all"                    # Everyone
    RANDOM = "random"              # Random target
    
    @classmethod
    def from_string(cls, value: str) -> 'MoveTarget':
        """Konvertiere String zu MoveTarget mit Fallback."""
        try:
            if isinstance(value, str):
                return cls(value.lower())
            return value
        except (ValueError, AttributeError):
            return cls.ENEMY


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
    
    @classmethod
    def from_string(cls, value: str) -> 'EffectKind':
        """Konvertiere String zu EffectKind mit Fallback."""
        try:
            if isinstance(value, str):
                return cls(value.lower())
            return value
        except (ValueError, AttributeError):
            return cls.DAMAGE


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
    
    def __post_init__(self):
        """Validiere die MoveEffect nach der Initialisierung."""
        if not isinstance(self.kind, EffectKind):
            raise ValueError("kind muss ein EffectKind Enum sein")
        
        if not isinstance(self.chance, (int, float)) or self.chance < 0 or self.chance > 100:
            raise ValueError("chance muss zwischen 0 und 100 liegen")
        
        if self.power is not None and (not isinstance(self.power, int) or self.power < 0):
            raise ValueError("power muss eine nicht-negative Ganzzahl sein")
        
        if self.stages is not None and (not isinstance(self.stages, int) or self.stages < -6 or self.stages > 6):
            raise ValueError("stages muss zwischen -6 und 6 liegen")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MoveEffect':
        """Create from dictionary data."""
        try:
            if not isinstance(data, dict):
                raise ValueError("Daten müssen ein Dictionary sein")
            
            # Konvertiere kind
            kind_data = data.get("kind")
            if isinstance(kind_data, str):
                kind = EffectKind.from_string(kind_data)
            elif isinstance(kind_data, EffectKind):
                kind = kind_data
            else:
                kind = EffectKind.DAMAGE
            
            return cls(
                kind=kind,
                chance=data.get("chance", 100.0),
                power=data.get("power"),
                stat=data.get("stat"),
                stages=data.get("stages"),
                status=data.get("status"),
                amount=data.get("amount"),
                percent=data.get("percent", False),
                duration=data.get("duration")
            )
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der MoveEffect aus Dict: {e}")
            # Fallback: einfache MoveEffect
            return cls(kind=EffectKind.DAMAGE, power=40)
    
    def is_valid(self) -> bool:
        """Validiere die MoveEffect."""
        try:
            if not isinstance(self.kind, EffectKind):
                return False
            
            if not isinstance(self.chance, (int, float)) or self.chance < 0 or self.chance > 100:
                return False
            
            if self.power is not None and (not isinstance(self.power, int) or self.power < 0):
                return False
            
            if self.stages is not None and (not isinstance(self.stages, int) or self.stages < -6 or self.stages > 6):
                return False
            
            return True
        except Exception as e:
            logger.error(f"Fehler bei der MoveEffect-Validierung: {e}")
            return False


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
    
    def __post_init__(self):
        """Validiere die Move nach der Initialisierung."""
        if not self.id or not isinstance(self.id, str):
            raise ValueError("ID muss ein nicht-leerer String sein")
        
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Name muss ein nicht-leerer String sein")
        
        if not isinstance(self.category, MoveCategory):
            raise ValueError("category muss ein MoveCategory Enum sein")
        
        if not isinstance(self.power, int) or self.power < 0:
            raise ValueError("power muss eine nicht-negative Ganzzahl sein")
        
        if not isinstance(self.accuracy, int) or self.accuracy < 0 or self.accuracy > 100:
            raise ValueError("accuracy muss zwischen 0 und 100 liegen")
        
        if not isinstance(self.pp, int) or self.pp < 0:
            raise ValueError("pp muss eine nicht-negative Ganzzahl sein")
        
        if not isinstance(self.max_pp, int) or self.max_pp < 1:
            raise ValueError("max_pp muss mindestens 1 sein")
        
        if not isinstance(self.priority, int):
            raise ValueError("priority muss eine Ganzzahl sein")
        
        if not isinstance(self.targeting, MoveTarget):
            raise ValueError("targeting muss ein MoveTarget Enum sein")
        
        if not isinstance(self.effects, list):
            raise ValueError("effects muss eine Liste sein")
        
        if not isinstance(self.description, str):
            raise ValueError("description muss ein String sein")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Move':
        """Create from dictionary data."""
        try:
            if not isinstance(data, dict):
                raise ValueError("Daten müssen ein Dictionary sein")
            
            # Validiere erforderliche Felder
            required_fields = ["id", "name", "type", "category", "power", "accuracy", "pp", "max_pp", "priority", "targeting", "effects", "description"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Feld {field} ist erforderlich")
            
            # Konvertiere Enums
            category_data = data.get("category")
            if isinstance(category_data, str):
                category = MoveCategory.from_string(category_data)
            elif isinstance(category_data, MoveCategory):
                category = category_data
            else:
                category = MoveCategory.PHYSICAL
            
            targeting_data = data.get("targeting")
            if isinstance(targeting_data, str):
                targeting = MoveTarget.from_string(targeting_data)
            elif isinstance(targeting_data, MoveTarget):
                targeting = targeting_data
            else:
                targeting = MoveTarget.ENEMY
            
            # Konvertiere Effects
            effects_data = data.get("effects", [])
            if isinstance(effects_data, list):
                effects = [MoveEffect.from_dict(effect) for effect in effects_data if isinstance(effect, dict)]
            else:
                effects = []
            
            return cls(
                id=data["id"],
                name=data["name"],
                type=data["type"],
                category=category,
                power=data["power"],
                accuracy=data["accuracy"],
                pp=data["pp"],
                max_pp=data["max_pp"],
                priority=data["priority"],
                targeting=targeting,
                effects=effects,
                description=data["description"],
                contact=data.get("contact", False),
                sound_based=data.get("sound_based", False),
                punching=data.get("punching", False),
                biting=data.get("biting", False),
                pulse=data.get("pulse", False),
                multi_hit=data.get("multi_hit")
            )
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Move aus Dict: {e}")
            raise
    
    def can_use(self) -> bool:
        """Check if the move can be used."""
        try:
            return self.pp > 0 and not self.is_disabled()
        except Exception as e:
            logger.error(f"Fehler bei der Move-Verfügbarkeits-Prüfung: {e}")
            return False
    
    def is_disabled(self) -> bool:
        """Check if the move is disabled."""
        # Placeholder for future implementation
        return False
    
    def use(self) -> bool:
        """Use the move (reduce PP)."""
        try:
            if self.pp > 0:
                self.pp -= 1
                return True
            return False
        except Exception as e:
            logger.error(f"Fehler beim Verwenden des Moves: {e}")
            return False
    
    def restore_pp(self, amount: int = None) -> int:
        """Restore PP to the move."""
        try:
            if amount is None:
                amount = self.max_pp - self.pp
            
            old_pp = self.pp
            self.pp = min(self.max_pp, self.pp + amount)
            restored = self.pp - old_pp
            
            return restored
        except Exception as e:
            logger.error(f"Fehler beim Wiederherstellen der PP: {e}")
            return 0
    
    def get_effectiveness(self, target_type: str) -> float:
        """Calculate type effectiveness against target."""
        try:
            # Placeholder for type effectiveness calculation
            # This would implement the type chart
            return 1.0
        except Exception as e:
            logger.error(f"Fehler bei der Effektivitäts-Berechnung: {e}")
            return 1.0
    
    def is_valid(self) -> bool:
        """Validiere die Move."""
        try:
            # Prüfe grundlegende Eigenschaften
            if not self.id or not self.name:
                return False
            
            # Prüfe Stats
            if self.power < 0 or self.accuracy < 0 or self.accuracy > 100:
                return False
            
            if self.pp < 0 or self.max_pp < 1 or self.pp > self.max_pp:
                return False
            
            # Prüfe Effects
            if not isinstance(self.effects, list):
                return False
            
            for effect in self.effects:
                if not effect or not effect.is_valid():
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Fehler bei der Move-Validierung: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiere Move zu Dict für Serialisierung."""
        try:
            return {
                'id': self.id,
                'name': self.name,
                'type': self.type,
                'category': self.category.value,
                'power': self.power,
                'accuracy': self.accuracy,
                'pp': self.pp,
                'max_pp': self.max_pp,
                'priority': self.priority,
                'targeting': self.targeting.value,
                'effects': [effect.__dict__ for effect in self.effects],
                'description': self.description,
                'contact': self.contact,
                'sound_based': self.sound_based,
                'punching': self.punching,
                'biting': self.biting,
                'pulse': self.pulse,
                'multi_hit': self.multi_hit
            }
        except Exception as e:
            logger.error(f"Fehler bei der Move-zu-Dict-Konvertierung: {e}")
            return {'error': str(e)}


class MoveExecutor:
    """Executes moves in battle."""
    
    @staticmethod
    def execute_move(move: Move, attacker: Any, target: Any, battle_state: Any) -> Dict[str, Any]:
        """Execute a move in battle."""
        try:
            if not move or not move.is_valid():
                return {"success": False, "message": "Ungültiger Move"}
            
            if not move.can_use():
                return {"success": False, "message": "Move kann nicht verwendet werden"}
            
            # Check accuracy
            if not MoveExecutor._check_accuracy(move, attacker, target):
                return {"success": False, "message": f"{move.name} hat verfehlt!"}
            
            # Execute effects
            results = []
            for effect in move.effects:
                effect_result = MoveExecutor._execute_effect(effect, move, attacker, target, battle_state)
                if effect_result:
                    results.append(effect_result)
            
            # Use PP
            move.use()
            
            return {
                "success": True,
                "effects": results,
                "damage": MoveExecutor._calculate_damage(move, attacker, target),
                "healing": MoveExecutor._calculate_healing(move, attacker, target)
            }
            
        except Exception as e:
            logger.error(f"Fehler bei der Move-Ausführung: {e}")
            return {"success": False, "message": f"Move fehlgeschlagen: {str(e)}"}
    
    @staticmethod
    def _check_accuracy(move: Move, attacker: Any, target: Any) -> bool:
        """Check if move hits."""
        try:
            import random
            return random.random() * 100 < move.accuracy
        except Exception as e:
            logger.error(f"Fehler bei der Genauigkeits-Prüfung: {e}")
            return True  # Fallback
    
    @staticmethod
    def _execute_effect(effect: MoveEffect, move: Move, attacker: Any, target: Any, battle_state: Any) -> Optional[Dict[str, Any]]:
        """Execute a single move effect."""
        try:
            if not effect or not effect.is_valid():
                return None
            
            # Check effect chance
            import random
            if random.random() * 100 > effect.chance:
                return None
            
            if effect.kind == EffectKind.DAMAGE:
                damage = MoveExecutor._calculate_damage(move, attacker, target)
                if damage > 0:
                    target.take_damage(damage)
                    return {"type": "damage", "amount": damage}
            
            elif effect.kind == EffectKind.HEAL:
                healing = MoveExecutor._calculate_healing(move, attacker, target)
                if healing > 0:
                    target.heal(healing)
                    return {"type": "heal", "amount": healing}
            
            elif effect.kind == EffectKind.STATUS and effect.status:
                # Apply status effect
                return {"type": "status", "status": effect.status}
            
            return None
            
        except Exception as e:
            logger.error(f"Fehler bei der Effect-Ausführung: {e}")
            return None
    
    @staticmethod
    def _calculate_damage(move: Move, attacker: Any, target: Any) -> int:
        """Calculate damage for a move."""
        try:
            if not move or move.power <= 0:
                return 0
            
            # Placeholder damage calculation
            # This would implement the full damage formula
            base_damage = move.power
            
            # Apply attacker's attack stat
            if hasattr(attacker, 'stats') and isinstance(attacker.stats, dict):
                if move.category == MoveCategory.PHYSICAL:
                    attack_stat = attacker.stats.get('atk', 50)
                else:
                    attack_stat = attacker.stats.get('mag', 30)
            else:
                attack_stat = 50
            
            # Apply target's defense stat
            if hasattr(target, 'stats') and isinstance(target.stats, dict):
                if move.category == MoveCategory.PHYSICAL:
                    defense_stat = target.stats.get('def', 50)
                else:
                    defense_stat = target.stats.get('res', 30)
            else:
                defense_stat = 50
            
            # Simple damage formula
            damage = int((2 * attacker.level / 5 + 2) * move.power * attack_stat / defense_stat / 50 + 2)
            
            return max(1, damage)
            
        except Exception as e:
            logger.error(f"Fehler bei der Schadens-Berechnung: {e}")
            return move.power if move else 0
    
    @staticmethod
    def _calculate_healing(move: Move, attacker: Any, target: Any) -> int:
        """Calculate healing for a move."""
        try:
            if not move:
                return 0
            
            # Look for healing effects
            for effect in move.effects:
                if effect.kind == EffectKind.HEAL and effect.power:
                    return effect.power
            
            return 0
            
        except Exception as e:
            logger.error(f"Fehler bei der Heilungs-Berechnung: {e}")
            return 0


# Move Registry
class MoveRegistry:
    """Registry for all available moves."""
    
    def __init__(self):
        self.moves: Dict[str, Move] = {}
        self._load_moves()
    
    def _load_moves(self) -> None:
        """Load moves from data files."""
        try:
            # Placeholder for move loading
            # This would load from JSON files
            pass
        except Exception as e:
            logger.error(f"Fehler beim Laden der Moves: {e}")
    
    def get_move(self, move_id: str) -> Optional[Move]:
        """Get a move by ID."""
        try:
            return self.moves.get(move_id)
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Moves {move_id}: {e}")
            return None
    
    def register_move(self, move: Move) -> bool:
        """Register a new move."""
        try:
            if move and move.is_valid():
                self.moves[move.id] = move
                return True
            return False
        except Exception as e:
            logger.error(f"Fehler beim Registrieren des Moves: {e}")
            return False
    
    def get_all_moves(self) -> List[Move]:
        """Get all registered moves."""
        try:
            return list(self.moves.values())
        except Exception as e:
            logger.error(f"Fehler beim Abrufen aller Moves: {e}")
            return []


# Global move registry instance
move_registry = MoveRegistry()