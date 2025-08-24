"""
🧬 Dragon Quest Monsters Traits System
Implementiert spezielle Monster-Eigenschaften und Fähigkeiten
"""

from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum, auto
from dataclasses import dataclass, field
import logging
import random
import json

logger = logging.getLogger(__name__)

class TraitCategory(Enum):
    """Kategorien von Monster-Traits"""
    COMBAT = "combat"          # Kampf-bezogene Traits
    RESISTANCE = "resistance"  # Resistenzen gegen Elemente/Status
    SPECIAL = "special"        # Spezielle Fähigkeiten
    PASSIVE = "passive"        # Passive Boni
    COUNTER = "counter"        # Konter-Fähigkeiten
    REGEN = "regen"           # Regenerations-Traits
    CRITICAL = "critical"     # Kritische Treffer
    METAL = "metal"           # Metal-Slime Traits

class TraitTrigger(Enum):
    """Wann ein Trait aktiviert wird"""
    ALWAYS = "always"                  # Immer aktiv
    ON_ATTACK = "on_attack"           # Beim Angreifen
    ON_DEFEND = "on_defend"           # Beim Verteidigen
    ON_DAMAGE = "on_damage"           # Bei Schaden
    ON_HEAL = "on_heal"               # Bei Heilung
    TURN_START = "turn_start"         # Zu Rundenbeginn
    TURN_END = "turn_end"             # Zu Rundenende
    HEALTH_LOW = "health_low"         # Bei wenig HP (<25%)
    HEALTH_CRITICAL = "health_critical" # Bei kritischen HP (<10%)
    RANDOM = "random"                  # Zufällig

@dataclass
class TraitEffect:
    """Effekt eines Traits"""
    effect_type: str                      # Typ des Effekts
    value: Any                            # Wert/Stärke des Effekts
    chance: float = 1.0                   # Aktivierungswahrscheinlichkeit
    condition: Optional[Callable] = None  # Zusätzliche Bedingung
    description: str = ""                 # Beschreibung des Effekts

@dataclass
class MonsterTrait:
    """Ein einzelner Monster-Trait"""
    name: str
    category: TraitCategory
    trigger: TraitTrigger
    effects: List[TraitEffect] = field(default_factory=list)
    description: str = ""
    icon: str = ""  # Icon für UI
    tier: int = 1   # Seltenheit/Stärke (1-5)
    stackable: bool = False  # Kann mehrfach vorhanden sein
    inheritable: bool = True  # Kann vererbt werden
    
    def can_activate(self, context: Dict[str, Any]) -> bool:
        """Prüft ob Trait aktiviert werden kann"""
        # Prüfe Trigger-Bedingung
        if self.trigger == TraitTrigger.ALWAYS:
            return True
        elif self.trigger == TraitTrigger.HEALTH_LOW:
            hp_percent = context.get('hp_percent', 1.0)
            return hp_percent <= 0.25
        elif self.trigger == TraitTrigger.HEALTH_CRITICAL:
            hp_percent = context.get('hp_percent', 1.0)
            return hp_percent <= 0.10
        elif self.trigger == TraitTrigger.RANDOM:
            # Wird bei Effekt-Check geprüft
            return True
        
        # Prüfe ob aktueller Kontext zum Trigger passt
        current_phase = context.get('phase', '')
        return current_phase == self.trigger.value
    
    def apply_effects(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Wendet Trait-Effekte an"""
        applied = []
        
        for effect in self.effects:
            # Prüfe Aktivierungschance
            if random.random() > effect.chance:
                continue
            
            # Prüfe zusätzliche Bedingung
            if effect.condition and not effect.condition(context):
                continue
            
            # Wende Effekt an
            result = self._apply_single_effect(effect, context)
            if result:
                applied.append(result)
        
        return applied
    
    def _apply_single_effect(self, effect: TraitEffect, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Wendet einen einzelnen Effekt an"""
        result = {
            'trait': self.name,
            'effect_type': effect.effect_type,
            'value': effect.value
        }
        
        # Verschiedene Effekt-Typen
        if effect.effect_type == 'damage_reduction':
            # Reduziere eingehenden Schaden
            damage = context.get('damage', 0)
            reduced = int(damage * (1 - effect.value))
            result['damage_reduced'] = damage - reduced
            context['damage'] = reduced
            
        elif effect.effect_type == 'damage_multiplier':
            # Erhöhe ausgehenden Schaden
            damage = context.get('damage', 0)
            context['damage'] = int(damage * effect.value)
            result['damage_multiplied'] = context['damage'] - damage
            
        elif effect.effect_type == 'stat_boost':
            # Erhöhe Stat
            stat_name = effect.value.get('stat')
            boost = effect.value.get('amount', 0)
            if stat_name in context.get('stats', {}):
                context['stats'][stat_name] += boost
                result['stat_boosted'] = {stat_name: boost}
        
        elif effect.effect_type == 'counter_attack':
            # Löse Gegenangriff aus
            result['counter'] = True
            result['counter_chance'] = effect.value
            
        elif effect.effect_type == 'hp_regen':
            # HP-Regeneration
            max_hp = context.get('max_hp', 100)
            regen = int(max_hp * effect.value)
            result['hp_regen'] = regen
            
        elif effect.effect_type == 'mp_regen':
            # MP-Regeneration
            max_mp = context.get('max_mp', 50)
            regen = int(max_mp * effect.value)
            result['mp_regen'] = regen
        
        return result

class TraitDatabase:
    """Zentrale Datenbank für alle Monster-Traits"""
    
    def __init__(self):
        self.traits: Dict[str, MonsterTrait] = {}
        self._initialize_traits()
        logger.info(f"Trait Database initialized with {len(self.traits)} traits")
    
    def _initialize_traits(self):
        """Initialisiere alle DQM Traits"""
        
        # ====== METAL TRAITS ======
        self.traits["Metal Body"] = MonsterTrait(
            name="Metal Body",
            category=TraitCategory.METAL,
            trigger=TraitTrigger.ON_DEFEND,
            effects=[
                TraitEffect(
                    effect_type="metal_defense",
                    value=0.99,  # 99% Damage reduction
                    description="Reduziert fast allen Schaden auf 0-1"
                ),
                TraitEffect(
                    effect_type="fixed_damage",
                    value=1,
                    chance=0.5,  # 50% chance for 1 damage, else 0
                    description="Schaden wird auf 0 oder 1 reduziert"
                )
            ],
            description="Metallischer Körper der fast unverwundbar ist",
            tier=5,
            inheritable=False  # Sehr selten, nicht vererbbar
        )
        
        self.traits["Metal Slash Weakness"] = MonsterTrait(
            name="Metal Slash Weakness",
            category=TraitCategory.METAL,
            trigger=TraitTrigger.ON_DEFEND,
            effects=[
                TraitEffect(
                    effect_type="weakness_to_skill",
                    value={"skill": "Metal Slash", "multiplier": 999},
                    description="Nimmt vollen Schaden von Metal Slash"
                )
            ],
            description="Verwundbar gegen Metal Slash",
            tier=1,
            inheritable=False
        )
        
        # ====== CRITICAL TRAITS ======
        self.traits["Critical Master"] = MonsterTrait(
            name="Critical Master",
            category=TraitCategory.CRITICAL,
            trigger=TraitTrigger.ON_ATTACK,
            effects=[
                TraitEffect(
                    effect_type="crit_rate_multiplier",
                    value=2.0,  # Verdoppelt Crit-Rate
                    description="Verdoppelt kritische Trefferchance"
                )
            ],
            description="Meister der kritischen Treffer",
            tier=3
        )
        
        self.traits["Lucky Devil"] = MonsterTrait(
            name="Lucky Devil",
            category=TraitCategory.CRITICAL,
            trigger=TraitTrigger.ON_ATTACK,
            effects=[
                TraitEffect(
                    effect_type="crit_rate_bonus",
                    value=0.1,  # +10% Crit chance
                    description="+10% kritische Trefferchance"
                ),
                TraitEffect(
                    effect_type="accuracy_bonus",
                    value=1.1,  # +10% Accuracy
                    description="+10% Treffergenauigkeit"
                )
            ],
            description="Glück des Teufels",
            tier=2
        )
        
        # ====== COMBAT TRAITS ======
        self.traits["Attack Boost"] = MonsterTrait(
            name="Attack Boost",
            category=TraitCategory.COMBAT,
            trigger=TraitTrigger.ALWAYS,
            effects=[
                TraitEffect(
                    effect_type="stat_boost",
                    value={"stat": "atk", "amount": 10},
                    description="+10% Angriff"
                )
            ],
            description="Permanent erhöhter Angriff",
            tier=1,
            stackable=True
        )
        
        self.traits["Defense Boost"] = MonsterTrait(
            name="Defense Boost",
            category=TraitCategory.COMBAT,
            trigger=TraitTrigger.ALWAYS,
            effects=[
                TraitEffect(
                    effect_type="stat_boost",
                    value={"stat": "def", "amount": 10},
                    description="+10% Verteidigung"
                )
            ],
            description="Permanent erhöhte Verteidigung",
            tier=1,
            stackable=True
        )
        
        self.traits["Agility Boost"] = MonsterTrait(
            name="Agility Boost",
            category=TraitCategory.COMBAT,
            trigger=TraitTrigger.ALWAYS,
            effects=[
                TraitEffect(
                    effect_type="stat_boost",
                    value={"stat": "agility", "amount": 20},
                    description="+20% Geschwindigkeit"
                )
            ],
            description="Permanent erhöhte Geschwindigkeit",
            tier=2
        )
        
        self.traits["Magic Boost"] = MonsterTrait(
            name="Magic Boost",
            category=TraitCategory.COMBAT,
            trigger=TraitTrigger.ALWAYS,
            effects=[
                TraitEffect(
                    effect_type="stat_boost",
                    value={"stat": "mag", "amount": 15},
                    description="+15% Magie"
                )
            ],
            description="Permanent erhöhte Magiekraft",
            tier=2
        )
        
        # ====== RESISTANCE TRAITS ======
        self.traits["Fire Breath Guard"] = MonsterTrait(
            name="Fire Breath Guard",
            category=TraitCategory.RESISTANCE,
            trigger=TraitTrigger.ON_DEFEND,
            effects=[
                TraitEffect(
                    effect_type="element_resist",
                    value={"element": "fire", "reduction": 0.5},
                    description="50% Feuer-Resistenz"
                )
            ],
            description="Schutz vor Feuer-Attacken",
            tier=2
        )
        
        self.traits["Ice Breath Guard"] = MonsterTrait(
            name="Ice Breath Guard",
            category=TraitCategory.RESISTANCE,
            trigger=TraitTrigger.ON_DEFEND,
            effects=[
                TraitEffect(
                    effect_type="element_resist",
                    value={"element": "ice", "reduction": 0.5},
                    description="50% Eis-Resistenz"
                )
            ],
            description="Schutz vor Eis-Attacken",
            tier=2
        )
        
        self.traits["Bang Ward"] = MonsterTrait(
            name="Bang Ward",
            category=TraitCategory.RESISTANCE,
            trigger=TraitTrigger.ON_DEFEND,
            effects=[
                TraitEffect(
                    effect_type="element_resist",
                    value={"element": "explosion", "reduction": 0.5},
                    description="50% Explosions-Resistenz"
                )
            ],
            description="Schutz vor Explosionen",
            tier=2
        )
        
        self.traits["Status Guard"] = MonsterTrait(
            name="Status Guard",
            category=TraitCategory.RESISTANCE,
            trigger=TraitTrigger.ON_DEFEND,
            effects=[
                TraitEffect(
                    effect_type="status_resist",
                    value=0.5,  # 50% chance to resist
                    description="50% Status-Resistenz"
                )
            ],
            description="Widerstand gegen Status-Effekte",
            tier=3
        )
        
        # ====== COUNTER TRAITS ======
        self.traits["Counter"] = MonsterTrait(
            name="Counter",
            category=TraitCategory.COUNTER,
            trigger=TraitTrigger.ON_DEFEND,
            effects=[
                TraitEffect(
                    effect_type="counter_attack",
                    value=0.25,  # 25% Counter chance
                    description="25% Chance auf Konter bei physischen Angriffen"
                )
            ],
            description="Kontert physische Angriffe",
            tier=3
        )
        
        self.traits["Magic Counter"] = MonsterTrait(
            name="Magic Counter",
            category=TraitCategory.COUNTER,
            trigger=TraitTrigger.ON_DEFEND,
            effects=[
                TraitEffect(
                    effect_type="magic_reflect",
                    value=0.25,  # 25% Reflect chance
                    description="25% Chance Magie zu reflektieren"
                )
            ],
            description="Reflektiert magische Angriffe",
            tier=4
        )
        
        self.traits["Thorns"] = MonsterTrait(
            name="Thorns",
            category=TraitCategory.COUNTER,
            trigger=TraitTrigger.ON_DEFEND,
            effects=[
                TraitEffect(
                    effect_type="damage_return",
                    value=0.1,  # Return 10% damage
                    description="Verursacht 10% Rückschaden"
                )
            ],
            description="Stacheln die Angreifer verletzen",
            tier=2
        )
        
        # ====== REGEN TRAITS ======
        self.traits["HP Regeneration"] = MonsterTrait(
            name="HP Regeneration",
            category=TraitCategory.REGEN,
            trigger=TraitTrigger.TURN_END,
            effects=[
                TraitEffect(
                    effect_type="hp_regen",
                    value=0.05,  # 5% max HP per turn
                    description="Regeneriert 5% HP pro Runde"
                )
            ],
            description="Automatische HP-Regeneration",
            tier=3
        )
        
        self.traits["MP Regeneration"] = MonsterTrait(
            name="MP Regeneration",
            category=TraitCategory.REGEN,
            trigger=TraitTrigger.TURN_END,
            effects=[
                TraitEffect(
                    effect_type="mp_regen",
                    value=0.1,  # 10% max MP per turn
                    description="Regeneriert 10% MP pro Runde"
                )
            ],
            description="Automatische MP-Regeneration",
            tier=3
        )
        
        self.traits["Fast Healer"] = MonsterTrait(
            name="Fast Healer",
            category=TraitCategory.REGEN,
            trigger=TraitTrigger.ON_HEAL,
            effects=[
                TraitEffect(
                    effect_type="heal_boost",
                    value=1.5,  # 50% more healing received
                    description="Erhält 50% mehr Heilung"
                )
            ],
            description="Erhöhte Heilungseffektivität",
            tier=2
        )
        
        # ====== SPECIAL TRAITS ======
        self.traits["Psycho"] = MonsterTrait(
            name="Psycho",
            category=TraitCategory.SPECIAL,
            trigger=TraitTrigger.ON_ATTACK,
            effects=[
                TraitEffect(
                    effect_type="random_action",
                    value=0.25,  # 25% chance
                    chance=0.25,
                    description="25% Chance auf zufällige Aktion"
                )
            ],
            description="Unberechenbar und chaotisch",
            tier=2
        )
        
        self.traits["Early Bird"] = MonsterTrait(
            name="Early Bird",
            category=TraitCategory.SPECIAL,
            trigger=TraitTrigger.ALWAYS,
            effects=[
                TraitEffect(
                    effect_type="wake_faster",
                    value=2.0,  # Wake 2x faster
                    description="Wacht doppelt so schnell aus Schlaf auf"
                ),
                TraitEffect(
                    effect_type="status_duration",
                    value={"status": "sleep", "multiplier": 0.5},
                    description="Schlaf-Dauer halbiert"
                )
            ],
            description="Frühaufsteher",
            tier=2
        )
        
        self.traits["Intimidating"] = MonsterTrait(
            name="Intimidating",
            category=TraitCategory.SPECIAL,
            trigger=TraitTrigger.TURN_START,
            effects=[
                TraitEffect(
                    effect_type="intimidate",
                    value={"stat": "atk", "reduction": 0.1},
                    chance=0.3,
                    description="30% Chance Gegner einzuschüchtern"
                )
            ],
            description="Einschüchternde Präsenz",
            tier=3
        )
        
        self.traits["Last Stand"] = MonsterTrait(
            name="Last Stand",
            category=TraitCategory.SPECIAL,
            trigger=TraitTrigger.HEALTH_CRITICAL,
            effects=[
                TraitEffect(
                    effect_type="stat_boost",
                    value={"stat": "atk", "amount": 50},
                    description="+50% Angriff bei kritischen HP"
                ),
                TraitEffect(
                    effect_type="stat_boost",
                    value={"stat": "def", "amount": 50},
                    description="+50% Verteidigung bei kritischen HP"
                )
            ],
            description="Kämpft härter wenn dem Tod nahe",
            tier=4
        )
        
        self.traits["Escape Artist"] = MonsterTrait(
            name="Escape Artist",
            category=TraitCategory.SPECIAL,
            trigger=TraitTrigger.ALWAYS,
            effects=[
                TraitEffect(
                    effect_type="flee_bonus",
                    value=1.5,  # 50% better flee chance
                    description="+50% Fluchtchance"
                )
            ],
            description="Meister der Flucht",
            tier=1
        )
        
        # ====== PASSIVE TRAITS ======
        self.traits["Hard Worker"] = MonsterTrait(
            name="Hard Worker",
            category=TraitCategory.PASSIVE,
            trigger=TraitTrigger.ALWAYS,
            effects=[
                TraitEffect(
                    effect_type="exp_bonus",
                    value=1.2,  # 20% more EXP
                    description="+20% EXP-Gewinn"
                )
            ],
            description="Lernt schneller durch harte Arbeit",
            tier=2
        )
        
        self.traits["Treasure Hunter"] = MonsterTrait(
            name="Treasure Hunter",
            category=TraitCategory.PASSIVE,
            trigger=TraitTrigger.ALWAYS,
            effects=[
                TraitEffect(
                    effect_type="item_find",
                    value=1.5,  # 50% better item find
                    description="+50% Item-Fundchance"
                )
            ],
            description="Findet mehr Items",
            tier=2
        )
        
        self.traits["Gold Finder"] = MonsterTrait(
            name="Gold Finder",
            category=TraitCategory.PASSIVE,
            trigger=TraitTrigger.ALWAYS,
            effects=[
                TraitEffect(
                    effect_type="gold_bonus",
                    value=1.3,  # 30% more gold
                    description="+30% Gold-Gewinn"
                )
            ],
            description="Findet mehr Gold",
            tier=2
        )
    
    def get_trait(self, name: str) -> Optional[MonsterTrait]:
        """Hole einen Trait by Name"""
        return self.traits.get(name)
    
    def get_traits_by_category(self, category: TraitCategory) -> List[MonsterTrait]:
        """Hole alle Traits einer Kategorie"""
        return [t for t in self.traits.values() if t.category == category]
    
    def get_traits_by_tier(self, tier: int) -> List[MonsterTrait]:
        """Hole alle Traits eines Tiers"""
        return [t for t in self.traits.values() if t.tier == tier]
    
    def get_inheritable_traits(self) -> List[MonsterTrait]:
        """Hole alle vererbbaren Traits"""
        return [t for t in self.traits.values() if t.inheritable]
    
    def calculate_trait_inheritance(self, 
                                   parent1_traits: List[str],
                                   parent2_traits: List[str],
                                   offspring_family: str = None) -> List[str]:
        """
        Berechne Trait-Vererbung für Synthesis
        
        Args:
            parent1_traits: Traits des ersten Elternteils
            parent2_traits: Traits des zweiten Elternteils
            offspring_family: Monster-Familie des Nachwuchses
            
        Returns:
            Liste der vererbten Traits
        """
        inherited = []
        
        # Regel 1: Gemeinsame Traits werden immer vererbt
        common_traits = set(parent1_traits) & set(parent2_traits)
        for trait_name in common_traits:
            trait = self.get_trait(trait_name)
            if trait and trait.inheritable:
                inherited.append(trait_name)
        
        # Regel 2: Hohe Chance für starke Traits
        all_parent_traits = list(set(parent1_traits + parent2_traits) - common_traits)
        for trait_name in all_parent_traits:
            trait = self.get_trait(trait_name)
            if not trait or not trait.inheritable:
                continue
            
            # Höhere Tiers haben höhere Vererbungschance
            inherit_chance = 0.2 * trait.tier  # 20% per tier
            if random.random() < inherit_chance:
                inherited.append(trait_name)
        
        # Regel 3: Familie-spezifische Traits
        if offspring_family:
            family_traits = self._get_family_traits(offspring_family)
            for trait_name in family_traits:
                if trait_name not in inherited and random.random() < 0.3:
                    inherited.append(trait_name)
        
        # Maximum 3 Traits (kann erhöht werden mit speziellen Synthesis)
        return inherited[:3]
    
    def _get_family_traits(self, family: str) -> List[str]:
        """Hole typische Traits für eine Monster-Familie"""
        family_trait_map = {
            "dragon": ["Fire Breath Guard", "Attack Boost", "Counter"],
            "slime": ["HP Regeneration", "Defense Boost", "Early Bird"],
            "beast": ["Agility Boost", "Counter", "Intimidating"],
            "bird": ["Agility Boost", "Early Bird", "Escape Artist"],
            "plant": ["HP Regeneration", "Status Guard", "Thorns"],
            "insect": ["Agility Boost", "Psycho", "Escape Artist"],
            "demon": ["Magic Boost", "Magic Counter", "Last Stand"],
            "zombie": ["HP Regeneration", "Status Guard", "Counter"],
            "material": ["Defense Boost", "Hard Worker", "Gold Finder"],
            "????": ["Metal Body", "Critical Master", "Last Stand"]
        }
        
        return family_trait_map.get(family.lower(), [])
    
    def apply_trait_to_stats(self, trait: MonsterTrait, stats: Dict[str, int]) -> Dict[str, int]:
        """
        Wendet permanente Stat-Modifikationen eines Traits an
        
        Args:
            trait: Der anzuwendende Trait
            stats: Aktuelle Stats des Monsters
            
        Returns:
            Modifizierte Stats
        """
        if trait.trigger != TraitTrigger.ALWAYS:
            return stats  # Nur ALWAYS-Traits modifizieren permanente Stats
        
        modified_stats = stats.copy()
        
        for effect in trait.effects:
            if effect.effect_type == 'stat_boost':
                stat_name = effect.value.get('stat')
                amount = effect.value.get('amount', 0)
                
                if stat_name in modified_stats:
                    # Prozentuale Erhöhung
                    if isinstance(amount, float) or amount < 0:
                        modified_stats[stat_name] = int(modified_stats[stat_name] * (1 + amount))
                    else:
                        # Absolute Erhöhung
                        modified_stats[stat_name] += amount
        
        return modified_stats
    
    def export_to_json(self, filepath: str):
        """Exportiere Trait-Datenbank als JSON"""
        data = {}
        for name, trait in self.traits.items():
            data[name] = {
                "category": trait.category.value,
                "trigger": trait.trigger.value,
                "description": trait.description,
                "tier": trait.tier,
                "stackable": trait.stackable,
                "inheritable": trait.inheritable,
                "effects": [
                    {
                        "type": effect.effect_type,
                        "value": effect.value,
                        "chance": effect.chance,
                        "description": effect.description
                    }
                    for effect in trait.effects
                ]
            }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported {len(data)} traits to {filepath}")


class TraitManager:
    """Verwaltet Traits für ein Monster im Kampf"""
    
    def __init__(self, monster: Any):
        self.monster = monster
        self.traits: List[MonsterTrait] = []
        self.trait_db = get_trait_database()
        self.active_effects: Dict[str, Any] = {}
        
    def add_trait(self, trait_name: str) -> bool:
        """Füge einen Trait hinzu"""
        trait = self.trait_db.get_trait(trait_name)
        if not trait:
            logger.warning(f"Trait {trait_name} not found")
            return False
        
        # Prüfe ob stackable oder bereits vorhanden
        if not trait.stackable and trait in self.traits:
            logger.info(f"Trait {trait_name} already present and not stackable")
            return False
        
        self.traits.append(trait)
        logger.info(f"Added trait {trait_name} to {self.monster.name}")
        return True
    
    def remove_trait(self, trait_name: str) -> bool:
        """Entferne einen Trait"""
        for i, trait in enumerate(self.traits):
            if trait.name == trait_name:
                self.traits.pop(i)
                logger.info(f"Removed trait {trait_name} from {self.monster.name}")
                return True
        return False
    
    def has_trait(self, trait_name: str) -> bool:
        """Prüfe ob Monster einen Trait hat"""
        return any(t.name == trait_name for t in self.traits)
    
    def get_traits_by_trigger(self, trigger: TraitTrigger) -> List[MonsterTrait]:
        """Hole alle Traits mit bestimmtem Trigger"""
        return [t for t in self.traits if t.trigger == trigger]
    
    def process_traits(self, trigger: TraitTrigger, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Verarbeite alle relevanten Traits
        
        Args:
            trigger: Aktueller Trigger
            context: Kontext-Informationen
            
        Returns:
            Liste der angewendeten Effekte
        """
        applied_effects = []
        
        # Füge Monster-Informationen zum Kontext hinzu
        context['monster'] = self.monster
        context['hp_percent'] = self.monster.current_hp / max(1, self.monster.max_hp)
        
        # Hole relevante Traits
        relevant_traits = self.get_traits_by_trigger(trigger)
        
        # Zusätzlich ALWAYS-Traits wenn nicht bereits verarbeitet
        if trigger != TraitTrigger.ALWAYS:
            relevant_traits.extend(self.get_traits_by_trigger(TraitTrigger.ALWAYS))
        
        # Verarbeite jeden Trait
        for trait in relevant_traits:
            if trait.can_activate(context):
                effects = trait.apply_effects(context)
                applied_effects.extend(effects)
        
        return applied_effects
    
    def get_stat_modifiers(self) -> Dict[str, float]:
        """Hole alle Stat-Modifikatoren von Traits"""
        modifiers = {
            'atk': 1.0,
            'def': 1.0,
            'mag': 1.0,
            'res': 1.0,
            'agility': 1.0,
            'accuracy': 1.0
        }
        
        for trait in self.traits:
            if trait.trigger != TraitTrigger.ALWAYS:
                continue
            
            for effect in trait.effects:
                if effect.effect_type == 'stat_boost':
                    stat = effect.value.get('stat')
                    amount = effect.value.get('amount', 0)
                    if stat in modifiers:
                        # Konvertiere zu Multiplikator
                        modifiers[stat] *= (1 + amount / 100)
        
        return modifiers
    
    def get_element_resistances(self) -> Dict[str, float]:
        """Hole alle Element-Resistenzen"""
        resistances = {}
        
        for trait in self.traits:
            for effect in trait.effects:
                if effect.effect_type == 'element_resist':
                    element = effect.value.get('element')
                    reduction = effect.value.get('reduction', 0)
                    
                    if element not in resistances:
                        resistances[element] = 1.0
                    
                    # Multiplikative Stacking
                    resistances[element] *= (1 - reduction)
        
        return resistances


# Singleton-Instanz
_trait_db_instance = None

def get_trait_database() -> TraitDatabase:
    """Hole Singleton-Instanz der Trait-Datenbank"""
    global _trait_db_instance
    if _trait_db_instance is None:
        _trait_db_instance = TraitDatabase()
    return _trait_db_instance


# Test-Code
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test Trait-Datenbank
    db = get_trait_database()
    
    print("\n=== DQM TRAIT DATABASE TEST ===\n")
    
    # Zeige alle Kategorien
    print("Trait-Kategorien:")
    for category in TraitCategory:
        traits = db.get_traits_by_category(category)
        print(f"  {category.value}: {len(traits)} Traits")
    
    # Teste Metal Body
    print("\n1. Metal Body Test:")
    metal_body = db.get_trait("Metal Body")
    if metal_body:
        print(f"  Name: {metal_body.name}")
        print(f"  Beschreibung: {metal_body.description}")
        print(f"  Tier: {metal_body.tier}")
        print(f"  Vererbbar: {metal_body.inheritable}")
    
    # Teste Trait-Vererbung
    print("\n2. Trait-Vererbung Test:")
    parent1 = ["Attack Boost", "Fire Breath Guard", "Counter"]
    parent2 = ["Attack Boost", "HP Regeneration", "Critical Master"]
    inherited = db.calculate_trait_inheritance(parent1, parent2, "dragon")
    print(f"  Eltern 1: {parent1}")
    print(f"  Eltern 2: {parent2}")
    print(f"  Vererbt: {inherited}")
    
    # Teste Stat-Modifikation
    print("\n3. Stat-Modifikation Test:")
    stats = {"atk": 100, "def": 80, "mag": 60, "agility": 70}
    atk_boost = db.get_trait("Attack Boost")
    if atk_boost:
        modified = db.apply_trait_to_stats(atk_boost, stats)
        print(f"  Original Stats: {stats}")
        print(f"  Mit Attack Boost: {modified}")
    
    # Zeige Traits nach Tier
    print("\n4. Traits nach Tier:")
    for tier in range(1, 6):
        tier_traits = db.get_traits_by_tier(tier)
        if tier_traits:
            names = [t.name for t in tier_traits[:3]]  # Erste 3
            print(f"  Tier {tier}: {', '.join(names)}...")
    
    print("\n=== TEST ABGESCHLOSSEN ===")
