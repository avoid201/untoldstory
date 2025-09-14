"""
Move System for Untold Story
Handles move data, effects, and execution
"""

from typing import Dict, List, Optional, Any, Callable, Tuple, Union, TYPE_CHECKING
from enum import Enum
from dataclasses import dataclass
import logging
from engine.core.resources import resources
from engine.systems.talent_system import get_talent_database, TalentTier

if TYPE_CHECKING:
    # Lazy imports für zirkuläre Dependencies
    from engine.systems.monster_instance import MonsterInstance

# Logger für bessere Fehlerverfolgung
logger = logging.getLogger(__name__)

class MoveCategory(Enum):
    """Categories of moves."""
    PHYSICAL = "phys"
    MAGICAL = "mag"
    SUPPORT = "support"
    SPECIAL = "mag"  # Alias for compatibility
    STATUS = "support"  # Alias for compatibility
    
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
    
    # DQM-spezifische Felder
    drain_percent: float = 0.0  # Prozent des Schadens als Heilung
    recoil_percent: float = 0.0  # Prozent des Schadens als Rückstoß
    multi_hit_min: int = 1  # Mindestanzahl Treffer
    multi_hit_max: int = 1  # Maximalanzahl Treffer
    
    # Talent-System Integration
    talent_id: Optional[str] = None  # ID des Talents das diesen Move bereitstellt
    talent_tier: Optional[TalentTier] = None  # Talent-Tier das für diesen Move benötigt wird
    level_requirement: int = 1  # Level-Anforderung für den Move
    
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
        
        # PP system removed - DQM style uses unlimited moves
        
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
            required_fields = ["id", "name", "type", "category", "power", "accuracy", "priority", "targeting", "effects", "description"]
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
                priority=data["priority"],
                targeting=targeting,
                effects=effects,
                description=data["description"],
                contact=data.get("contact", False),
                sound_based=data.get("sound_based", False),
                punching=data.get("punching", False),
                biting=data.get("biting", False),
                pulse=data.get("pulse", False),
                multi_hit=data.get("multi_hit"),
                # DQM-spezifische Default-Werte für fehlende JSON-Felder
                drain_percent=data.get('drain_percent', 0),
                recoil_percent=data.get('recoil_percent', 0),
                multi_hit_min=data.get('multi_hit_min', 1),
                multi_hit_max=data.get('multi_hit_max', 1)
            )
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Move aus Dict: {e}")
            raise
    
    def can_use(self) -> bool:
        """Check if the move can be used."""
        try:
            # DQM-style: All moves are always available (no PP system)
            return not self.is_disabled()
        except Exception as e:
            logger.error(f"Fehler bei der Move-Verfügbarkeits-Prüfung: {e}")
            return False
    
    def is_disabled(self) -> bool:
        """Check if the move is disabled."""
        try:
            # Check if move is sealed/disabled by status effects
            # This could be extended with specific disable conditions
            return False
            
        except Exception as e:
            logger.error(f"Fehler bei der Move-Disabled-Prüfung: {e}")
            return False
    
    def use(self) -> bool:
        """Use the move (DQM-style: no PP consumption)."""
        try:
            # DQM-style: Moves have unlimited usage
            return True
        except Exception as e:
            logger.error(f"Fehler beim Verwenden des Moves: {e}")
            return False
    
    @property
    def category_string(self) -> str:
        """Get category as string with intelligent fallback logic."""
        try:
            if not hasattr(self, 'category') or not self.category:
                return "PHYSICAL"
            
            # Handle enum values
            if hasattr(self.category, 'value'):
                category_value = self.category.value.lower()
            else:
                category_value = str(self.category).lower()
            
            # Map to standardized categories
            if category_value in ['phys', 'physical', 'körperlich']:
                return "PHYSICAL"
            elif category_value in ['mag', 'magical', 'special', 'magisch']:
                return "MAGICAL"
            elif category_value in ['support', 'status', 'hilfe']:
                return "STATUS"
            else:
                # Fallback based on move properties
                if hasattr(self, 'power') and self.power > 0:
                    # Has power - determine if physical or magical
                    if hasattr(self, 'type'):
                        magic_types = ['feuer', 'wasser', 'pflanze', 'luft', 'energie', 'chaos', 'mystisch', 'gottheit', 'teufel']
                        if any(magic_type in self.type.lower() for magic_type in magic_types):
                            return "MAGICAL"
                    return "PHYSICAL"
                else:
                    return "STATUS"
                    
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der category_string: {e}")
            return "PHYSICAL"  # Safe fallback
    
    def get_category_metadata(self) -> Dict[str, Any]:
        """Get comprehensive category metadata for UI grouping"""
        try:
            category = self.category_string
            
            # Determine UI grouping based on category
            if category == "PHYSICAL":
                return {
                    "category": "PHYSICAL",
                    "display_name": "Körperlich",
                    "ui_group": "attack",
                    "color": "#FF6B6B",  # Red
                    "icon": "⚔️",
                    "description": "Körperliche Angriffe"
                }
            elif category == "MAGICAL":
                return {
                    "category": "MAGICAL", 
                    "display_name": "Magisch",
                    "ui_group": "attack",
                    "color": "#4ECDC4",  # Teal
                    "icon": "✨",
                    "description": "Magische Angriffe"
                }
            elif category == "STATUS":
                return {
                    "category": "STATUS",
                    "display_name": "Status",
                    "ui_group": "support",
                    "color": "#45B7D1",  # Blue
                    "icon": "🛡️",
                    "description": "Status-Effekte"
                }
            else:
                # Fallback
                return {
                    "category": "PHYSICAL",
                    "display_name": "Unbekannt",
                    "ui_group": "attack",
                    "color": "#95A5A6",  # Gray
                    "icon": "❓",
                    "description": "Unbekannte Kategorie"
                }
                
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Category-Metadata: {e}")
            return {
                "category": "PHYSICAL",
                "display_name": "Fehler",
                "ui_group": "attack", 
                "color": "#E74C3C",  # Red
                "icon": "⚠️",
                "description": "Fehler beim Laden"
            }
    

    
    def get_effectiveness(self, target_type: str) -> float:
        """Calculate type effectiveness against target using TypeChart."""
        try:
            # Use the proper TypeChart for effectiveness calculation
            from engine.systems.types import TypeChart
            
            type_chart = TypeChart()
            effectiveness = type_chart.get_effectiveness(self.type, target_type)
            
            logger.debug(f"Type effectiveness: {self.type} -> {target_type} = {effectiveness}")
            return effectiveness
            
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
            
            # PP validation removed - DQM style uses unlimited moves
            
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
                # PP fields removed - DQM style uses unlimited moves
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
    """Executes moves in battle with complete DQM-style damage application pipeline."""
    
    @staticmethod
    def execute(attacker: 'MonsterInstance', move: Move, target: 'MonsterInstance', battle_state: Any = None) -> Dict[str, Any]:
        """
        Execute a move and return complete results.
        
        Args:
            attacker: Monster performing the move
            move: Move to execute
            target: Target monster
            battle_state: Optional battle state for context
            
        Returns:
            Complete execution result with damage, effects, and messages
        """
        try:
            if not move or not move.is_valid():
                return {"success": False, "message": "Ungültiger Move"}
            
            if not move.can_use():
                return {"success": False, "message": "Move kann nicht verwendet werden"}
            
            # Check accuracy first
            if not MoveExecutor._check_accuracy(move, attacker, target):
                return {
                    "success": False, 
                    "message": f"{move.name} hat verfehlt!",
                    "damage": 0,
                    "critical": False,
                    "type_effectiveness": 1.0,
                    "status_applied": None,
                    "stat_changes": {},
                    "is_miss": True
                }
            
            # Initialize result structure
            result = {
                "damage": 0,
                "critical": False,
                "type_effectiveness": 1.0,
                "status_applied": None,
                "stat_changes": {},
                "message": "",
                "is_miss": False,
                "effects": []
            }
            
            # Execute damage calculation for physical/magical moves
            if move.category in [MoveCategory.PHYSICAL, MoveCategory.MAGICAL]:
                damage_result = MoveExecutor._execute_damage_calculation(attacker, move, target)
                result.update(damage_result)
                
                # Apply damage to target
                if damage_result["damage"] > 0:
                    damage_result_dict = target.take_damage(damage_result["damage"])
                    actual_damage = damage_result_dict["damage_dealt"]
                    result["damage"] = actual_damage
                    result["message"] = f"{move.name} verursacht {actual_damage} Schaden!"
                    
                    # Add critical hit message
                    if damage_result["critical"]:
                        result["message"] += " Kritischer Treffer!"
                    
                    # Add effectiveness message
                    if damage_result["type_effectiveness"] > 1.0:
                        result["message"] += " Sehr effektiv!"
                    elif damage_result["type_effectiveness"] < 1.0:
                        result["message"] += " Nicht sehr effektiv..."
                    
                    # Add faint message
                    if damage_result_dict["fainted"]:
                        result["message"] += f" {target.name} wurde besiegt!"
                        result["target_fainted"] = True
            
            # Execute additional effects
            for effect in move.effects:
                effect_result = MoveExecutor._execute_effect(effect, move, attacker, target, battle_state)
                if effect_result:
                    result["effects"].append(effect_result)
                    
                    # Handle status effects
                    if effect_result.get("type") == "status":
                        result["status_applied"] = effect_result.get("status")
                        result["message"] += f" {target.name} wurde {effect_result.get('status')}!"
                    
                    # Handle stat changes
                    if effect_result.get("type") == "stat_change":
                        stat = effect_result.get("stat")
                        stages = effect_result.get("stages", 0)
                        result["stat_changes"][stat] = stages
                        if stages > 0:
                            result["message"] += f" {target.name}'s {stat} stieg!"
                        else:
                            result["message"] += f" {target.name}'s {stat} sank!"
            
            # DQM-style: No PP consumption
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"Fehler bei der Move-Ausführung: {e}")
            return {
                "success": False, 
                "message": f"Move fehlgeschlagen: {str(e)}",
                "damage": 0,
                "critical": False,
                "type_effectiveness": 1.0,
                "status_applied": None,
                "stat_changes": {},
                "is_miss": False
            }
    
    @staticmethod
    def _execute_damage_calculation(attacker: 'MonsterInstance', move: Move, target: 'MonsterInstance') -> Dict[str, Any]:
        """
        Execute damage calculation using UnifiedDamageCalculator.
        
        Returns:
            Damage calculation result with all modifiers
        """
        try:
            # Import here to avoid circular dependency
            from engine.systems.unified_damage_calculator import unified_damage_calculator
            
            if not move or move.power <= 0:
                return {
                    "damage": 0,
                    "critical": False,
                    "type_effectiveness": 1.0,
                    "has_stab": False
                }
            
            # Use UnifiedDamageCalculator as Single Source of Truth
            damage_result = unified_damage_calculator.calculate_damage(
                attacker=attacker,
                defender=target,
                move=move
            )
            
            logger.debug(f"Damage calculated: {damage_result.damage} (effectiveness: {damage_result.effectiveness})")
            
            return {
                "damage": max(0, damage_result.damage),
                "critical": damage_result.is_critical,
                "type_effectiveness": damage_result.effectiveness,
                "has_stab": damage_result.has_stab,
                "effectiveness_text": damage_result.effectiveness_text
            }
            
        except Exception as e:
            logger.error(f"Error in damage calculation: {e}")
            # Simple fallback calculation
            try:
                level = getattr(attacker, 'level', 50)
                power = move.power
                attack_stat, defense_stat = MoveExecutor._get_battle_stats(attacker, target, move)
                
                # Basic damage formula
                base_damage = (((2 * level / 5 + 2) * power * attack_stat / defense_stat) / 50) + 2
                return {
                    "damage": max(1, int(base_damage)),
                    "critical": False,
                    "type_effectiveness": 1.0,
                    "has_stab": False
                }
            except Exception:
                logger.error("Even fallback damage calculation failed")
                return {
                    "damage": max(1, move.power // 2),
                    "critical": False,
                    "type_effectiveness": 1.0,
                    "has_stab": False
                }
    
    
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
        """Execute a single move effect with complete DQM-style handling."""
        try:
            if not effect or not effect.is_valid():
                return None
            
            # Check effect chance
            import random
            if random.random() * 100 > effect.chance:
                return None
            
            if effect.kind == EffectKind.DAMAGE:
                # Damage effects are handled in main execute method
                return None
            
            elif effect.kind == EffectKind.HEAL:
                healing = MoveExecutor._calculate_healing(move, attacker, target)
                if healing > 0:
                    actual_healing = target.heal(healing)
                    return {"type": "heal", "amount": actual_healing}
            
            elif effect.kind == EffectKind.STATUS and effect.status:
                # Apply status effect to target
                from engine.systems.monster_instance import StatusCondition
                try:
                    status = StatusCondition.from_string(effect.status)
                    target.apply_status(status, effect.duration or 0)
                    return {"type": "status", "status": effect.status, "duration": effect.duration}
                except Exception as e:
                    logger.error(f"Fehler beim Anwenden des Status-Effekts {effect.status}: {e}")
                    return None
            
            elif (effect.kind in (EffectKind.BUFF, EffectKind.DEBUFF) 
                  and effect.stat and effect.stages and hasattr(target, 'stat_stages')):
                # Apply stat change to target (unified BUFF/DEBUFF handling)
                stat_name = effect.stat.lower()
                current_stage = getattr(target.stat_stages, stat_name, 0)
                
                if effect.kind == EffectKind.BUFF:
                    new_stage = min(6, current_stage + effect.stages)
                    actual_stages = effect.stages
                else:  # DEBUFF
                    new_stage = max(-6, current_stage - abs(effect.stages))
                    actual_stages = -abs(effect.stages)
                
                setattr(target.stat_stages, stat_name, new_stage)
                return {"type": "stat_change", "stat": stat_name, "stages": actual_stages}
            
            elif effect.kind == EffectKind.CURE:
                # Cure status condition
                if hasattr(target, 'status') and target.status != StatusCondition.NONE:
                    old_status = target.status.value if hasattr(target.status, 'value') else target.status
                    target.status = StatusCondition.NONE
                    target.status_turns = 0
                    return {"type": "cure", "status": old_status}
            
            return None
            
        except Exception as e:
            logger.error(f"Fehler bei der Effect-Ausführung: {e}")
            return None
    
    @staticmethod
    def _get_battle_stats(attacker: Any, target: Any, move: Move) -> Tuple[int, int]:
        """Helper method to get attack and defense stats based on move category."""
        if move.category == MoveCategory.PHYSICAL:
            attack_stat = getattr(attacker, 'stats', {}).get('atk', 50)
            defense_stat = getattr(target, 'stats', {}).get('def', 50)
        else:
            attack_stat = getattr(attacker, 'stats', {}).get('mag', 50)
            defense_stat = getattr(target, 'stats', {}).get('res', 50)
        return attack_stat, defense_stat
    
    @staticmethod
    def _calculate_damage(move: Move, attacker: Any, target: Any) -> int:
        """Calculate damage for a move using UnifiedDamageCalculator (SINGLE SOURCE OF TRUTH)."""
        try:
            # Import here to avoid circular dependency
            from engine.systems.unified_damage_calculator import unified_damage_calculator
            
            if not move or move.power <= 0:
                return 0
            
            # Use UnifiedDamageCalculator as Single Source of Truth
            result = unified_damage_calculator.calculate_damage(
                attacker=attacker,
                defender=target,
                move=move
            )
            
            logger.debug(f"Damage calculated: {result.damage} (effectiveness: {result.effectiveness})")
            return max(0, result.damage)
            
        except Exception as e:
            logger.error(f"Error in UnifiedDamageCalculator: {e}")
            # Simple fallback calculation
            try:
                level = getattr(attacker, 'level', 50)
                power = move.power
                attack_stat, defense_stat = MoveExecutor._get_battle_stats(attacker, target, move)
                
                # Basic damage formula
                base_damage = (((2 * level / 5 + 2) * power * attack_stat / defense_stat) / 50) + 2
                return max(1, int(base_damage))
            except Exception:
                logger.error("Even fallback damage calculation failed")
                return max(1, move.power // 2)
    
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
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the move registry."""
        if self._initialized:
            return
        
        self._initialized = True
        self.moves: Dict[str, Move] = {}
        self._load_moves()
    
    def _load_moves(self) -> None:
        """Load moves from data files."""
        try:
            # Load moves from JSON data
            from engine.core.resources import resources
            
            moves_data = resources.load_json("moves.json")
            if moves_data and "moves" in moves_data:
                for move_data in moves_data["moves"]:
                    try:
                        move = self._create_move_from_dict(move_data)
                        self.register_move(move)
                        logger.debug(f"Loaded move: {move.name}")
                    except Exception as e:
                        logger.error(f"Error loading move {move_data.get('name', 'unknown')}: {e}")
                        
                logger.info(f"Successfully loaded {len(self.moves)} moves from JSON")
                
        except Exception as e:
            logger.error(f"Fehler beim Laden der Moves: {e}")
    
    def _create_move_from_dict(self, move_data: Dict[str, Any]) -> Move:
        """Create a Move instance from dictionary data."""
        try:
            # Parse category
            category_str = move_data.get("category", "physical")
            category = MoveCategory.PHYSICAL
            if category_str.lower() == "special":
                category = MoveCategory.SPECIAL
            elif category_str.lower() == "status":
                category = MoveCategory.STATUS
            
            # Parse targeting
            target_str = move_data.get("target", "single_enemy")
            targeting = MoveTarget.ENEMY
            if target_str == "self":
                targeting = MoveTarget.SELF
            elif target_str == "all_enemies":
                targeting = MoveTarget.ALL_ENEMIES
            elif target_str == "all_allies":
                targeting = MoveTarget.ALL_ALLIES
            elif target_str == "single_ally":
                targeting = MoveTarget.ALLY
            
            # Parse effects
            effects = []
            for effect_data in move_data.get("effects", []):
                try:
                    effect_kind = EffectKind.DAMAGE
                    if effect_data.get("kind") == "status":
                        effect_kind = EffectKind.STATUS
                    elif effect_data.get("kind") == "heal":
                        effect_kind = EffectKind.HEAL
                    elif effect_data.get("kind") == "stat_change":
                        effect_kind = EffectKind.STAT_CHANGE
                    
                    effect = MoveEffect(
                        kind=effect_kind,
                        power=effect_data.get("power", 0),
                        chance=effect_data.get("chance", 100),
                        status=effect_data.get("status"),
                        stat=effect_data.get("stat"),
                        stages=effect_data.get("stages", 0)
                    )
                    effects.append(effect)
                except Exception as e:
                    logger.error(f"Error parsing effect: {e}")
            
            # DQM-spezifische Default-Werte für fehlende JSON-Felder
            move = Move(
                id=move_data["id"],
                name=move_data["name"],
                type=move_data.get("type", "Bestie"),
                category=category,
                power=move_data.get("power", 0),
                accuracy=move_data.get("accuracy", 100),
                priority=move_data.get("priority", 0),
                targeting=targeting,
                effects=effects,
                description=move_data.get("description", ""),
                contact=move_data.get("contact", False),
                sound_based=move_data.get("sound_based", False),
                punching=move_data.get("punching", False),
                biting=move_data.get("biting", False),
                pulse=move_data.get("pulse", False),
                multi_hit=move_data.get("multi_hit"),
                # DQM-spezifische Felder mit Default-Werten
                drain_percent=move_data.get('drain_percent', 0),
                recoil_percent=move_data.get('recoil_percent', 0),
                multi_hit_min=move_data.get('multi_hit_min', 1),
                multi_hit_max=move_data.get('multi_hit_max', 1)
            )
            
            return move
            
        except Exception as e:
            logger.error(f"Error creating move from dict: {e}")
            raise
    
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

    
    def create_move_instance_by_name(self, move_name: str) -> Optional[Move]:
        """Create a move instance by name."""
        try:
            # Try to find the move by name
            for move in self.moves.values():
                if move.name.lower() == move_name.lower():
                    # Return a copy of the move
                    return Move(
                        id=move.id,
                        name=move.name,
                        description=move.description,
                        category=move.category,
                        targeting=move.targeting,
                        power=move.power,
                        accuracy=move.accuracy,
                        priority=move.priority,
                        effects=move.effects.copy() if move.effects else [],
                        type=move.type,
                        contact=move.contact,
                        sound_based=move.sound_based,
                        punching=move.punching,
                        biting=move.biting,
                        pulse=move.pulse,
                        multi_hit=move.multi_hit,
                        drain_percent=move.drain_percent,
                        recoil_percent=move.recoil_percent,
                        multi_hit_min=move.multi_hit_min,
                        multi_hit_max=move.multi_hit_max
                    )
            
            # If not found, create a placeholder move
            logger.warning(f"Move '{move_name}' nicht gefunden, erstelle Dummy-Move")
            return Move(
                id=f"dummy_{move_name.lower()}",
                name=move_name,
                description="Dummy-Move",
                category=MoveCategory.PHYSICAL,
                targeting=MoveTarget.ENEMY,
                power=40,
                accuracy=100,
                priority=0,
                effects=[MoveEffect(kind=EffectKind.DAMAGE, power=40)],
                type="Normal",
                contact=False,
                sound_based=False,
                punching=False,
                biting=False,
                pulse=False,
                multi_hit=None,
                drain_percent=0,
                recoil_percent=0,
                multi_hit_min=1,
                multi_hit_max=1
            )
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Move-Instanz für '{move_name}': {e}")
            return None
    
    def create_move_instance(self, move_id: str) -> Optional[Move]:
        """Create a move instance by ID."""
        try:
            move = self.get_move(move_id)
            if move:
                # Return a copy of the move
                return Move(
                    id=move.id,
                    name=move.name,
                    description=move.description,
                    category=move.category,
                    targeting=move.targeting,
                    power=move.power,
                    accuracy=move.accuracy,
                    priority=move.priority,
                    effects=move.effects.copy() if move.effects else [],
                    type=move.type,
                    contact=move.contact,
                    sound_based=move.sound_based,
                    punching=move.punching,
                    biting=move.biting,
                    pulse=move.pulse,
                    multi_hit=move.multi_hit,
                    drain_percent=move.drain_percent,
                    recoil_percent=move.recoil_percent,
                    multi_hit_min=move.multi_hit_min,
                    multi_hit_max=move.multi_hit_max,
                    talent_id=getattr(move, 'talent_id', None),
                    talent_tier=getattr(move, 'talent_tier', None),
                    level_requirement=getattr(move, 'level_requirement', 1)
                )
            return None
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Move-Instanz für ID '{move_id}': {e}")
            return None
    
    def create_move_from_talent(self, move_id: str, talent_id: str, talent_tier: TalentTier, level_requirement: int = 1) -> Optional[Move]:
        """
        Create a move instance from talent data.
        
        Args:
            move_id: ID of the move to create
            talent_id: ID of the talent providing this move
            talent_tier: Tier of the talent required
            level_requirement: Level requirement for the move
            
        Returns:
            Move instance with talent information
        """
        try:
            # First try to get existing move
            move = self.get_move(move_id)
            if move:
                # Create copy with talent information
                return Move(
                    id=move.id,
                    name=move.name,
                    description=move.description,
                    category=move.category,
                    targeting=move.targeting,
                    power=move.power,
                    accuracy=move.accuracy,
                    priority=move.priority,
                    effects=move.effects.copy() if move.effects else [],
                    type=move.type,
                    contact=move.contact,
                    sound_based=move.sound_based,
                    punching=move.punching,
                    biting=move.biting,
                    pulse=move.pulse,
                    multi_hit=move.multi_hit,
                    drain_percent=move.drain_percent,
                    recoil_percent=move.recoil_percent,
                    multi_hit_min=move.multi_hit_min,
                    multi_hit_max=move.multi_hit_max,
                    talent_id=talent_id,
                    talent_tier=talent_tier,
                    level_requirement=level_requirement
                )
            
            # If move doesn't exist, try to create from talent database
            talent_db = get_talent_database()
            return talent_db.create_move_from_talent_data(move_id)
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Move aus Talent-Daten: {e}")
            return None
    
    def get_moves_for_talent(self, talent_id: str, talent_tier: TalentTier, monster_level: int) -> List[Move]:
        """
        Get all moves available for a specific talent and tier.
        
        Args:
            talent_id: ID of the talent
            talent_tier: Current tier of the talent
            monster_level: Level of the monster
            
        Returns:
            List of available moves
        """
        try:
            talent_db = get_talent_database()
            talent = talent_db.get_talent(talent_id)
            
            if not talent:
                return []
            
            # Get move IDs for this talent tier and level
            move_ids = talent.get_moves_for_tier(talent_tier, monster_level)
            
            # Create move instances
            moves = []
            for move_id in move_ids:
                move = self.create_move_from_talent(move_id, talent_id, talent_tier, monster_level)
                if move:
                    moves.append(move)
            
            return moves
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Moves für Talent {talent_id}: {e}")
            return []
    
    # Diese Methode wurde entfernt - validate_move_availability() wird jetzt verwendet






# ====== GLOBAL INSTANCES ======

# Global move registry instance
move_registry = MoveRegistry()


def integrate_dqm_skills_with_moves() -> None:
    """
    Integrate DQM skills with the move system.
    This function converts DQM skills to moves and registers them.
    """
    try:
        logger.info("Integrating DQM skills with move system...")
        
        # Get the move registry
        registry = move_registry
        
        # DQM Skill families to integrate
        dqm_skill_families = [
            # Fire family
            {"id": "dqm_frizz", "name": "Frizz", "type": "feuer", "power": 40, "category": "mag"},
            {"id": "dqm_frizzle", "name": "Frizzle", "type": "feuer", "power": 80, "category": "mag"},
            {"id": "dqm_kafrizz", "name": "Kafrizz", "type": "feuer", "power": 120, "category": "mag"},
            
            # Water family
            {"id": "dqm_sizz", "name": "Sizz", "type": "wasser", "power": 40, "category": "mag"},
            {"id": "dqm_sizzle", "name": "Sizzle", "type": "wasser", "power": 80, "category": "mag"},
            {"id": "dqm_kasizz", "name": "Kasizz", "type": "wasser", "power": 120, "category": "mag"},
            
            # Wind family
            {"id": "dqm_woosh", "name": "Woosh", "type": "luft", "power": 40, "category": "mag"},
            {"id": "dqm_swoosh", "name": "Swoosh", "type": "luft", "power": 80, "category": "mag"},
            {"id": "dqm_kaswoosh", "name": "Kaswoosh", "type": "luft", "power": 120, "category": "mag"},
            
            # Earth family
            {"id": "dqm_crack", "name": "Crack", "type": "erde", "power": 40, "category": "mag"},
            {"id": "dqm_crackle", "name": "Crackle", "type": "erde", "power": 80, "category": "mag"},
            {"id": "dqm_kacrack", "name": "Kacrack", "type": "erde", "power": 120, "category": "mag"},
            
            # Light family
            {"id": "dqm_zap", "name": "Zap", "type": "energie", "power": 40, "category": "mag"},
            {"id": "dqm_zapple", "name": "Zapple", "type": "energie", "power": 80, "category": "mag"},
            {"id": "dqm_kazap", "name": "Kazap", "type": "energie", "power": 120, "category": "mag"},
            
            # Dark family
            {"id": "dqm_whack", "name": "Whack", "type": "chaos", "power": 40, "category": "mag"},
            {"id": "dqm_thwack", "name": "Thwack", "type": "chaos", "power": 80, "category": "mag"},
            {"id": "dqm_kathwack", "name": "Kathwack", "type": "chaos", "power": 120, "category": "mag"},
            
            # Physical attacks
            {"id": "dqm_slash", "name": "Slash", "type": "normal", "power": 50, "category": "phys"},
            {"id": "dqm_claw", "name": "Claw", "type": "normal", "power": 60, "category": "phys"},
            {"id": "dqm_bite", "name": "Bite", "type": "normal", "power": 70, "category": "phys"},
            {"id": "dqm_punch", "name": "Punch", "type": "normal", "power": 80, "category": "phys"},
            
            # Support moves
            {"id": "dqm_heal", "name": "Heal", "type": "mystisch", "power": 0, "category": "support"},
            {"id": "dqm_healmore", "name": "Healmore", "type": "mystisch", "power": 0, "category": "support"},
            {"id": "dqm_healus", "name": "Healus", "type": "mystisch", "power": 0, "category": "support"},
            {"id": "dqm_healall", "name": "Healall", "type": "mystisch", "power": 0, "category": "support"},
            
            # Status moves
            {"id": "dqm_sleep", "name": "Sleep", "type": "mystisch", "power": 0, "category": "support"},
            {"id": "dqm_poison", "name": "Poison", "type": "seuche", "power": 0, "category": "support"},
            {"id": "dqm_paralysis", "name": "Paralysis", "type": "energie", "power": 0, "category": "support"},
            {"id": "dqm_confusion", "name": "Confusion", "type": "chaos", "power": 0, "category": "support"},
            
            # Buff moves
            {"id": "dqm_oomph", "name": "Oomph", "type": "mystisch", "power": 0, "category": "support"},
            {"id": "dqm_oomphle", "name": "Oomphle", "type": "mystisch", "power": 0, "category": "support"},
            {"id": "dqm_kabuff", "name": "Kabuff", "type": "mystisch", "power": 0, "category": "support"},
            {"id": "dqm_kabuffe", "name": "Kabuffe", "type": "mystisch", "power": 0, "category": "support"},
        ]
        
        # Convert DQM skills to moves and register them
        for skill_data in dqm_skill_families:
            try:
                # Create move from DQM skill data
                move = _create_dqm_skill_move(skill_data)
                if move:
                    registry.register_move(move)
                    logger.debug(f"Registered DQM skill: {move.name}")
            except Exception as e:
                logger.error(f"Error creating DQM skill move {skill_data.get('name', 'unknown')}: {e}")
        
        logger.info(f"Successfully integrated {len(dqm_skill_families)} DQM skills with move system")
        
    except Exception as e:
        logger.error(f"Error integrating DQM skills with move system: {e}")
        raise


def _create_dqm_skill_move(skill_data: Dict[str, Any]) -> Optional[Move]:
    """
    Create a Move instance from DQM skill data.
    
    Args:
        skill_data: Dictionary containing DQM skill information
        
    Returns:
        Move instance or None if creation fails
    """
    try:
        # Parse category
        category_str = skill_data.get("category", "phys")
        if category_str == "mag":
            category = MoveCategory.MAGICAL
        elif category_str == "support":
            category = MoveCategory.SUPPORT
        else:
            category = MoveCategory.PHYSICAL
        
        # Create effects based on skill type
        effects = []
        if skill_data.get("power", 0) > 0:
            # Damage effect
            effects.append(MoveEffect(
                kind=EffectKind.DAMAGE,
                power=skill_data["power"],
                chance=100.0
            ))
        else:
            # Support effect
            if "heal" in skill_data["name"].lower():
                effects.append(MoveEffect(
                    kind=EffectKind.HEAL,
                    power=50,  # Base healing power
                    chance=100.0
                ))
            elif skill_data["name"].lower() in ["sleep", "poison", "paralysis", "confusion"]:
                effects.append(MoveEffect(
                    kind=EffectKind.STATUS,
                    status=skill_data["name"].lower(),
                    chance=80.0
                ))
            elif "oomph" in skill_data["name"].lower() or "buff" in skill_data["name"].lower():
                effects.append(MoveEffect(
                    kind=EffectKind.BUFF,
                    stat="atk",
                    stages=1,
                    chance=100.0
                ))
        
        # Create move
        move = Move(
            id=skill_data["id"],
            name=skill_data["name"],
            type=skill_data["type"],
            category=category,
            power=skill_data.get("power", 0),
            accuracy=100,  # DQM skills are generally accurate
            priority=0,
            targeting=MoveTarget.ENEMY,
            effects=effects,
            description=f"DQM skill: {skill_data['name']}",
            contact=False,
            sound_based=False,
            punching=False,
            biting=False,
            pulse=False,
            multi_hit=None,
            drain_percent=0.0,
            recoil_percent=0.0,
            multi_hit_min=1,
            multi_hit_max=1
        )
        
        return move
        
    except Exception as e:
        logger.error(f"Error creating DQM skill move: {e}")
        return None
