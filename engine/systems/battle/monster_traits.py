"""
Monster Traits System for Untold Story
DQM-style monster traits with battle effects
"""

import logging
import random
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class TraitCategory(Enum):
    """Categories of monster traits."""
    COMBAT = "combat"           # Attack/Defense/Agility/Magic Boosts
    RESISTANCE = "resistance"   # Element-Resistenzen
    SPECIAL = "special"         # Psycho, Last Stand, Early Bird
    PASSIVE = "passive"         # EXP/Gold/Item-Boni
    COUNTER = "counter"         # Counter, Magic Counter, Thorns
    REGEN = "regen"            # HP/MP Regeneration
    CRITICAL = "critical"      # Critical Master, Lucky Devil
    METAL = "metal"            # Metal Body, Metal Slash Weakness


class TraitTrigger(Enum):
    """When traits activate."""
    ALWAYS = "always"                    # Immer aktiv
    ON_ATTACK = "on_attack"              # Beim Angreifen
    ON_DEFEND = "on_defend"              # Beim Verteidigen
    TURN_START = "turn_start"            # Zu Rundenbeginn
    TURN_END = "turn_end"                # Zu Rundenende
    HEALTH_LOW = "health_low"            # Bei <25% HP
    HEALTH_CRITICAL = "health_critical"  # Bei <10% HP
    RANDOM = "random"                    # Zufällige Aktivierung


@dataclass
class TraitEffect:
    """Single effect of a trait."""
    effect_type: str                     # Type of effect
    value: Any                          # Effect value
    chance: float = 1.0                 # Activation chance (0-1)
    condition: Optional[Callable] = None # Additional condition
    description: str = ""               # Effect description


@dataclass
class MonsterTrait:
    """A monster trait with effects."""
    name: str
    category: TraitCategory
    trigger: TraitTrigger
    effects: List[TraitEffect] = field(default_factory=list)
    description: str = ""
    icon: str = ""
    tier: int = 1                       # Rarity/strength (1-5)
    stackable: bool = False             # Can have multiple instances
    inheritable: bool = True            # Can be inherited
    
    def can_activate(self, context: Dict[str, Any]) -> bool:
        """Check if trait can activate."""
        if self.trigger == TraitTrigger.ALWAYS:
            return True
        elif self.trigger == TraitTrigger.HEALTH_LOW:
            hp_percent = context.get('hp_percent', 1.0)
            return hp_percent <= 0.25
        elif self.trigger == TraitTrigger.HEALTH_CRITICAL:
            hp_percent = context.get('hp_percent', 1.0)
            return hp_percent <= 0.10
        elif self.trigger == TraitTrigger.RANDOM:
            return True
        
        # Check if current context matches trigger
        current_phase = context.get('phase', '')
        return current_phase == self.trigger.value
    
    def apply_effects(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply trait effects."""
        applied = []
        
        for effect in self.effects:
            # Check activation chance
            if random.random() > effect.chance:
                continue
            
            # Check additional condition
            if effect.condition and not effect.condition(context):
                continue
            
            # Apply effect
            result = self._apply_single_effect(effect, context)
            if result:
                applied.append(result)
        
        return applied
    
    def _apply_single_effect(self, effect: TraitEffect, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Apply a single trait effect."""
        try:
            if effect.effect_type == "stat_boost":
                return {
                    "type": "stat_boost",
                    "stat": effect.value.get("stat"),
                    "amount": effect.value.get("amount", 0),
                    "description": effect.description
                }
            elif effect.effect_type == "damage_reduction":
                return {
                    "type": "damage_reduction",
                    "reduction": effect.value,
                    "description": effect.description
                }
            elif effect.effect_type == "counter_attack":
                return {
                    "type": "counter_attack",
                    "chance": effect.value,
                    "description": effect.description
                }
            elif effect.effect_type == "regeneration":
                return {
                    "type": "regeneration",
                    "amount": effect.value,
                    "description": effect.description
                }
            elif effect.effect_type == "critical_boost":
                return {
                    "type": "critical_boost",
                    "multiplier": effect.value,
                    "description": effect.description
                }
            elif effect.effect_type == "metal_body":
                return {
                    "type": "metal_body",
                    "active": True,
                    "description": effect.description
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error applying trait effect {effect.effect_type}: {e}")
            return None


class TraitDatabase:
    """Database of all available monster traits."""
    
    def __init__(self):
        """Initialize trait database."""
        self.traits: Dict[str, MonsterTrait] = {}
        self._load_traits()
    
    def _load_traits(self):
        """Load traits from data."""
        # Combat Traits
        self._add_trait(MonsterTrait(
            name="Attack Boost",
            category=TraitCategory.COMBAT,
            trigger=TraitTrigger.ALWAYS,
            effects=[TraitEffect(
                effect_type="stat_boost",
                value={"stat": "atk", "amount": 0.1},
                description="+10% Angriff"
            )],
            description="Erhöht den Angriff um 10%",
            tier=1
        ))
        
        self._add_trait(MonsterTrait(
            name="Defense Boost",
            category=TraitCategory.COMBAT,
            trigger=TraitTrigger.ALWAYS,
            effects=[TraitEffect(
                effect_type="stat_boost",
                value={"stat": "def", "amount": 0.1},
                description="+10% Verteidigung"
            )],
            description="Erhöht die Verteidigung um 10%",
            tier=1
        ))
        
        self._add_trait(MonsterTrait(
            name="Agility Boost",
            category=TraitCategory.COMBAT,
            trigger=TraitTrigger.ALWAYS,
            effects=[TraitEffect(
                effect_type="stat_boost",
                value={"stat": "spd", "amount": 0.2},
                description="+20% Geschwindigkeit"
            )],
            description="Erhöht die Geschwindigkeit um 20%",
            tier=2
        ))
        
        # Resistance Traits
        self._add_trait(MonsterTrait(
            name="Fire Breath Guard",
            category=TraitCategory.RESISTANCE,
            trigger=TraitTrigger.ALWAYS,
            effects=[TraitEffect(
                effect_type="damage_reduction",
                value=0.5,
                description="50% Feuer-Resistenz"
            )],
            description="Reduziert Feuerschaden um 50%",
            tier=2
        ))
        
        self._add_trait(MonsterTrait(
            name="Ice Breath Guard",
            category=TraitCategory.RESISTANCE,
            trigger=TraitTrigger.ALWAYS,
            effects=[TraitEffect(
                effect_type="damage_reduction",
                value=0.5,
                description="50% Eis-Resistenz"
            )],
            description="Reduziert Eisschaden um 50%",
            tier=2
        ))
        
        # Special Traits
        self._add_trait(MonsterTrait(
            name="Last Stand",
            category=TraitCategory.SPECIAL,
            trigger=TraitTrigger.HEALTH_CRITICAL,
            effects=[TraitEffect(
                effect_type="stat_boost",
                value={"stat": "atk", "amount": 0.5},
                description="+50% Angriff bei <10% HP"
            ), TraitEffect(
                effect_type="stat_boost",
                value={"stat": "def", "amount": 0.5},
                description="+50% Verteidigung bei <10% HP"
            )],
            description="Erhöht Angriff und Verteidigung um 50% bei <10% HP",
            tier=3
        ))
        
        self._add_trait(MonsterTrait(
            name="Early Bird",
            category=TraitCategory.SPECIAL,
            trigger=TraitTrigger.ALWAYS,
            effects=[TraitEffect(
                effect_type="status_resistance",
                value={"status": "sleep", "reduction": 0.5},
                description="50% Resistenz gegen Schlaf"
            )],
            description="Wacht schneller aus Schlaf auf",
            tier=2
        ))
        
        # Counter Traits
        self._add_trait(MonsterTrait(
            name="Counter",
            category=TraitCategory.COUNTER,
            trigger=TraitTrigger.ON_DEFEND,
            effects=[TraitEffect(
                effect_type="counter_attack",
                value=0.25,
                description="25% Chance auf Gegenangriff"
            )],
            description="25% Chance auf Gegenangriff nach physischem Schaden",
            tier=2
        ))
        
        self._add_trait(MonsterTrait(
            name="Thorns",
            category=TraitCategory.COUNTER,
            trigger=TraitTrigger.ON_DEFEND,
            effects=[TraitEffect(
                effect_type="damage_reflection",
                value=0.1,
                description="10% Rückschaden"
            )],
            description="Verursacht 10% Rückschaden an Angreifer",
            tier=1
        ))
        
        # Regen Traits
        self._add_trait(MonsterTrait(
            name="HP Regeneration",
            category=TraitCategory.REGEN,
            trigger=TraitTrigger.TURN_START,
            effects=[TraitEffect(
                effect_type="regeneration",
                value=0.05,
                description="5% HP-Regeneration pro Runde"
            )],
            description="Regeneriert 5% HP pro Runde",
            tier=2
        ))
        
        # Critical Traits
        self._add_trait(MonsterTrait(
            name="Critical Master",
            category=TraitCategory.CRITICAL,
            trigger=TraitTrigger.ALWAYS,
            effects=[TraitEffect(
                effect_type="critical_boost",
                value=2.0,
                description="Verdoppelt Crit-Rate"
            )],
            description="Verdoppelt die kritische Trefferchance",
            tier=3
        ))
        
        # Metal Traits
        self._add_trait(MonsterTrait(
            name="Metal Body",
            category=TraitCategory.METAL,
            trigger=TraitTrigger.ALWAYS,
            effects=[TraitEffect(
                effect_type="metal_body",
                value=True,
                description="Reduziert fast allen Schaden auf 0-1"
            )],
            description="Reduziert fast allen Schaden auf 0 oder 1",
            tier=5,
            inheritable=False  # Cannot be inherited
        ))
        
        logger.info(f"Loaded {len(self.traits)} monster traits")
    
    def _add_trait(self, trait: MonsterTrait):
        """Add a trait to the database."""
        self.traits[trait.name] = trait
    
    def get_trait(self, name: str) -> Optional[MonsterTrait]:
        """Get a trait by name."""
        return self.traits.get(name)
    
    def get_traits_by_category(self, category: TraitCategory) -> List[MonsterTrait]:
        """Get all traits in a category."""
        return [trait for trait in self.traits.values() if trait.category == category]
    
    def get_traits_by_tier(self, tier: int) -> List[MonsterTrait]:
        """Get all traits of a specific tier."""
        return [trait for trait in self.traits.values() if trait.tier == tier]
    
    def get_inheritable_traits(self) -> List[MonsterTrait]:
        """Get all inheritable traits."""
        return [trait for trait in self.traits.values() if trait.inheritable]


class TraitSystem:
    """Manages trait effects in battle."""
    
    def __init__(self):
        """Initialize trait system."""
        self.database = TraitDatabase()
    
    def apply_traits(self, monster, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply all active traits for a monster."""
        if not hasattr(monster, 'traits') or not monster.traits:
            return []
        
        applied_effects = []
        
        for trait_name in monster.traits:
            trait = self.database.get_trait(trait_name)
            if trait and trait.can_activate(context):
                effects = trait.apply_effects(context)
                applied_effects.extend(effects)
        
        return applied_effects
    
    def get_trait_bonus(self, monster, stat_name: str) -> float:
        """Get stat bonus from traits."""
        if not hasattr(monster, 'traits') or not monster.traits:
            return 0.0
        
        total_bonus = 0.0
        
        for trait_name in monster.traits:
            trait = self.database.get_trait(trait_name)
            if trait:
                for effect in trait.effects:
                    if (effect.effect_type == "stat_boost" and 
                        effect.value.get("stat") == stat_name):
                        total_bonus += effect.value.get("amount", 0.0)
        
        return total_bonus
    
    def has_metal_body(self, monster) -> bool:
        """Check if monster has Metal Body trait."""
        if not hasattr(monster, 'traits') or not monster.traits:
            return False
        
        return "Metal Body" in monster.traits
    
    def get_critical_multiplier(self, monster) -> float:
        """Get critical hit multiplier from traits."""
        if not hasattr(monster, 'traits') or not monster.traits:
            return 1.0
        
        multiplier = 1.0
        
        for trait_name in monster.traits:
            trait = self.database.get_trait(trait_name)
            if trait:
                for effect in trait.effects:
                    if effect.effect_type == "critical_boost":
                        multiplier *= effect.value
        
        return multiplier


# Global trait system instance
_trait_system_instance = None

def get_trait_system() -> TraitSystem:
    """Get the global trait system instance."""
    global _trait_system_instance
    if _trait_system_instance is None:
        _trait_system_instance = TraitSystem()
    return _trait_system_instance
