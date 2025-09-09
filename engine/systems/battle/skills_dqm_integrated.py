"""
🔮 Dragon Quest Monsters Skill System - INTEGRIERT MIT TALENT-SYSTEM
Verwendet das neue Talent-System für DQM-authentische Skills
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum, auto
from dataclasses import dataclass, field
import json
import logging

# Import Talent-System
from engine.systems.talent_system import get_talent_database, TalentInstance, TalentTier

logger = logging.getLogger(__name__)

class SkillElement(Enum):
    """Elementar-Typen für Skills - MAPPED ZU TALENT-SYSTEM"""
    NORMAL = "normal"
    FIRE = "fire"          # → fire_i, fire_group, fire_breath
    ICE = "ice"            # → ice_i, ice_breath
    THUNDER = "thunder"    # → thunder_i, thunder_group
    WIND = "wind"          # → wind_i
    EXPLOSION = "explosion" # → explosion_i
    DARK = "dark"          # → dark_i
    LIGHT = "light"        # → heal_i, multiheal
    EARTH = "earth"        # → earth_i
    WATER = "water"        # → water_i
    NONE = "none"          # → buff_i, debuff_i, status_i

class SkillType(Enum):
    """Skill-Kategorien"""
    ATTACK = "attack"           # Schadens-Skills
    HEAL = "heal"              # Heilungs-Skills
    BUFF = "buff"              # Stat-Erhöhung
    DEBUFF = "debuff"          # Stat-Senkung
    STATUS = "status"          # Status-Effekte
    BREATH = "breath"          # Atem-Attacken
    DANCE = "dance"            # Tanz-Skills
    SLASH = "slash"            # Schnitt-Attacken
    SPECIAL = "special"        # Spezial-Skills

class SkillTarget(Enum):
    """Ziel-Typen für Skills"""
    SINGLE_ENEMY = "single_enemy"
    ALL_ENEMIES = "all_enemies"
    ROW_ENEMIES = "row_enemies"
    SINGLE_ALLY = "single_ally"
    ALL_ALLIES = "all_allies"
    SELF = "self"
    RANDOM_ENEMIES = "random_enemies"
    FIELD = "field"

@dataclass
class SkillTier:
    """Repräsentiert eine Stufe in einer Skill-Familie"""
    name: str
    tier: int
    power: int
    mp_cost: int
    accuracy: float = 1.0
    description: str = ""
    effects: Dict[str, Any] = field(default_factory=dict)

@dataclass 
class SkillFamily:
    """Eine Familie von verwandten Skills (z.B. Frizz-Familie)"""
    family_name: str
    element: SkillElement
    skill_type: SkillType
    target: SkillTarget
    tiers: List[SkillTier] = field(default_factory=list)
    
    def get_tier(self, tier_level: int) -> Optional[SkillTier]:
        """Hole Skill einer bestimmten Stufe"""
        for tier in self.tiers:
            if tier.tier == tier_level:
                return tier
        return None
    
    def get_by_name(self, name: str) -> Optional[SkillTier]:
        """Hole Skill by Name"""
        for tier in self.tiers:
            if tier.name.lower() == name.lower():
                return tier
        return None
    
    def can_upgrade(self, current_tier: int) -> bool:
        """Prüfe ob Upgrade möglich ist"""
        return any(t.tier == current_tier + 1 for t in self.tiers)

class DQMSkillDatabase:
    """
    Zentrale Datenbank für alle DQM Skills - INTEGRIERT MIT TALENT-SYSTEM
    Verwendet das Talent-System als Basis für DQM-Skills
    """
    
    def __init__(self):
        self.talent_db = get_talent_database()
        self.element_resistances: Dict[SkillElement, List[SkillElement]] = {}
        self._initialize_element_chart()
        logger.info("DQM Skill Database initialized (integrated with Talent System)")
    
    def get_skill_family_from_talent(self, talent_id: str) -> Optional[SkillFamily]:
        """Konvertiere Talent zu DQM Skill-Familie"""
        talent = self.talent_db.get_talent(talent_id)
        if not talent:
            return None
        
        # Mappe Talent-Kategorie zu Skill-Element
        element_mapping = {
            "elemental": self._get_element_from_talent_id(talent_id),
            "healing": SkillElement.LIGHT,
            "support": SkillElement.NONE,
            "breath": self._get_element_from_talent_id(talent_id),
            "physical": SkillElement.NORMAL,
            "special": SkillElement.NONE
        }
        
        element = element_mapping.get(talent.category.value, SkillElement.NORMAL)
        
        # Mappe Talent-Kategorie zu Skill-Typ
        type_mapping = {
            "elemental": SkillType.ATTACK,
            "healing": SkillType.HEAL,
            "support": SkillType.BUFF,
            "breath": SkillType.BREATH,
            "physical": SkillType.ATTACK,
            "special": SkillType.SPECIAL
        }
        
        skill_type = type_mapping.get(talent.category.value, SkillType.ATTACK)
        
        # Konvertiere Talent-Moves zu Skill-Tiers
        tiers = []
        for move in talent.moves:
            tier = SkillTier(
                name=move.move_id,
                tier=move.tier_requirement.value,
                power=self._get_power_for_move(move.move_id),
                mp_cost=self._get_mp_cost_for_move(move.move_id),
                accuracy=1.0,
                description=move.description
            )
            tiers.append(tier)
        
        return SkillFamily(
            family_name=talent.name,
            element=element,
            skill_type=skill_type,
            target=SkillTarget.SINGLE_ENEMY,  # Default
            tiers=tiers
        )
    
    def _get_element_from_talent_id(self, talent_id: str) -> SkillElement:
        """Bestimme Skill-Element basierend auf Talent-ID"""
        if "fire" in talent_id:
            return SkillElement.FIRE
        elif "ice" in talent_id:
            return SkillElement.ICE
        elif "thunder" in talent_id:
            return SkillElement.THUNDER
        elif "wind" in talent_id:
            return SkillElement.WIND
        elif "earth" in talent_id:
            return SkillElement.EARTH
        elif "water" in talent_id:
            return SkillElement.WATER
        elif "dark" in talent_id or "chaos" in talent_id:
            return SkillElement.DARK
        elif "explosion" in talent_id:
            return SkillElement.EXPLOSION
        else:
            return SkillElement.NORMAL
    
    def _get_power_for_move(self, move_id: str) -> int:
        """Bestimme Power für Move basierend auf ID - VERBUNDEN MIT MOVEREGISTRY"""
        # Versuche zuerst MoveRegistry zu verwenden
        try:
            from engine.systems.moves import MoveRegistry
            move_registry = MoveRegistry()
            move = move_registry.get_move(move_id)
            if move and hasattr(move, 'power'):
                return move.power
        except Exception as e:
            logger.debug(f"Could not get power from MoveRegistry for {move_id}: {e}")
        
        # Fallback zu vereinfachter Power-Bestimmung
        if "frizz" in move_id.lower():
            return {"frizz": 10, "frizzle": 20, "kafrizz": 40, "kazfrizzle": 80}.get(move_id.lower(), 10)
        elif "crack" in move_id.lower():
            return {"crack": 12, "crackle": 25, "kacrack": 50, "kacrackle": 100}.get(move_id.lower(), 12)
        elif "zap" in move_id.lower():
            return {"zap": 15, "zapple": 30, "kazap": 60, "kazapple": 120}.get(move_id.lower(), 15)
        elif "heal" in move_id.lower():
            return {"heal": 30, "midheal": 75, "fullheal": 999, "omniheal": 999}.get(move_id.lower(), 30)
        else:
            return 20  # Default power
    
    def _get_mp_cost_for_move(self, move_id: str) -> int:
        """Bestimme MP-Kosten für Move basierend auf ID - VERBUNDEN MIT MOVEREGISTRY"""
        # Versuche zuerst MoveRegistry zu verwenden
        try:
            from engine.systems.moves import MoveRegistry
            move_registry = MoveRegistry()
            move = move_registry.get_move(move_id)
            if move and hasattr(move, 'mp_cost'):
                return move.mp_cost
        except Exception as e:
            logger.debug(f"Could not get MP cost from MoveRegistry for {move_id}: {e}")
        
        # Fallback zu vereinfachter MP-Kosten-Bestimmung
        if "frizz" in move_id.lower():
            return {"frizz": 2, "frizzle": 4, "kafrizz": 8, "kazfrizzle": 16}.get(move_id.lower(), 2)
        elif "crack" in move_id.lower():
            return {"crack": 3, "crackle": 5, "kacrack": 10, "kacrackle": 20}.get(move_id.lower(), 3)
        elif "zap" in move_id.lower():
            return {"zap": 4, "zapple": 7, "kazap": 15, "kazapple": 30}.get(move_id.lower(), 4)
        elif "heal" in move_id.lower():
            return {"heal": 3, "midheal": 6, "fullheal": 12, "omniheal": 20}.get(move_id.lower(), 3)
        else:
            return 5  # Default MP cost
    
    def _initialize_element_chart(self):
        """Initialisiere Element-Resistenz-Chart"""
        # Was ist stark gegen was?
        self.element_resistances = {
            SkillElement.FIRE: [SkillElement.ICE, SkillElement.EARTH],
            SkillElement.ICE: [SkillElement.FIRE, SkillElement.WIND],
            SkillElement.THUNDER: [SkillElement.WATER, SkillElement.WIND],
            SkillElement.WIND: [SkillElement.EARTH, SkillElement.THUNDER],
            SkillElement.EARTH: [SkillElement.THUNDER, SkillElement.FIRE],
            SkillElement.WATER: [SkillElement.FIRE, SkillElement.EARTH],
            SkillElement.LIGHT: [SkillElement.DARK],
            SkillElement.DARK: [SkillElement.LIGHT],
            SkillElement.EXPLOSION: [],  # Neutral
            SkillElement.NORMAL: []  # Neutral
        }
    
    def get_skill(self, talent_id: str, tier: int = 1) -> Optional[SkillTier]:
        """Hole einen spezifischen Skill aus Talent"""
        skill_family = self.get_skill_family_from_talent(talent_id)
        if skill_family:
            return skill_family.get_tier(tier)
        return None
    
    def get_skill_by_name(self, skill_name: str) -> Optional[Tuple[SkillFamily, SkillTier]]:
        """Suche Skill by Name in allen Talent-Familien"""
        # Durchsuche alle Talents
        for talent_id in self.talent_db.talents.keys():
            skill_family = self.get_skill_family_from_talent(talent_id)
            if skill_family:
                skill = skill_family.get_by_name(skill_name)
                if skill:
                    return (skill_family, skill)
        return None
    
    def get_element_modifier(self, attack_element: SkillElement, 
                            defense_element: SkillElement) -> float:
        """Berechne Element-Modifikator"""
        # Stark gegen
        if defense_element in self.element_resistances.get(attack_element, []):
            return 1.5  # 150% Schaden
        # Schwach gegen
        elif attack_element in self.element_resistances.get(defense_element, []):
            return 0.5  # 50% Schaden
        # Neutral
        return 1.0
    
    def get_skills_by_type(self, skill_type: SkillType) -> List[Tuple[str, SkillFamily]]:
        """Hole alle Skills eines Typs"""
        results = []
        for talent_id in self.talent_db.talents.keys():
            skill_family = self.get_skill_family_from_talent(talent_id)
            if skill_family and skill_family.skill_type == skill_type:
                results.append((talent_id, skill_family))
        return results
    
    def get_skills_by_element(self, element: SkillElement) -> List[Tuple[str, SkillFamily]]:
        """Hole alle Skills eines Elements"""
        results = []
        for talent_id in self.talent_db.talents.keys():
            skill_family = self.get_skill_family_from_talent(talent_id)
            if skill_family and skill_family.element == element:
                results.append((talent_id, skill_family))
        return results
    
    def calculate_mp_cost(self, skill: SkillTier, 
                         caster_level: int,
                         mp_reduction: float = 0.0) -> int:
        """Berechne tatsächliche MP-Kosten"""
        base_cost = skill.mp_cost
        
        # MP-Reduktion durch Traits oder Equipment
        reduced_cost = base_cost * (1.0 - mp_reduction)
        
        # Minimum 1 MP (außer bei 0-Kosten-Skills)
        if base_cost > 0:
            return max(1, int(reduced_cost))
        return 0
    
    def can_learn_skill(self, monster_level: int, 
                       skill_tier: int,
                       monster_family: str = None) -> bool:
        """Prüfe ob Monster Skill lernen kann - DELEGIERT AN TALENT-SYSTEM"""
        # Das Talent-System übernimmt diese Logik
        return True  # Vereinfacht - Talent-System prüft bereits
    
    def get_skill_inheritance(self, parent1_skills: List[str], 
                            parent2_skills: List[str],
                            offspring_family: str) -> List[str]:
        """
        Berechne Skill-Vererbung für Synthesis - DELEGIERT AN TALENT-SYSTEM
        """
        # Das Talent-System übernimmt diese Logik
        return []  # Vereinfacht - Talent-System übernimmt Vererbung
    
    def get_skill_as_move(self, talent_id: str, tier: int = 1) -> Optional[Any]:
        """
        Hole Skill als Move-Objekt für Battle-System Integration.
        Skills erweitern Moves, ersetzen sie nicht.
        
        Args:
            talent_id: Talent-ID
            tier: Skill-Tier
            
        Returns:
            Move-Objekt oder None
        """
        try:
            from engine.systems.moves import MoveRegistry
            move_registry = MoveRegistry()
            
            # Hole Skill-Tier
            skill = self.get_skill(talent_id, tier)
            if not skill:
                return None
            
            # Hole entsprechendes Move aus Registry
            move = move_registry.get_move(skill.name)
            if move:
                # Erweitere Move mit DQM-spezifischen Eigenschaften
                if hasattr(move, 'dqm_skill_data'):
                    move.dqm_skill_data = {
                        'talent_id': talent_id,
                        'tier': tier,
                        'element': self.get_skill_family_from_talent(talent_id).element.value if self.get_skill_family_from_talent(talent_id) else 'normal',
                        'unlimited_pp': True  # DQM-Style: Unlimited PP
                    }
                return move
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting skill as move: {e}")
            return None
    
    def export_to_json(self, filepath: str):
        """Exportiere Skill-Datenbank als JSON - DELEGIERT AN TALENT-SYSTEM"""
        # Das Talent-System übernimmt diese Logik
        self.talent_db.export_to_json(filepath)


# Singleton-Instanz
_skill_db_instance = None

def get_skill_database() -> DQMSkillDatabase:
    """Hole Singleton-Instanz der Skill-Datenbank"""
    global _skill_db_instance
    if _skill_db_instance is None:
        _skill_db_instance = DQMSkillDatabase()
    return _skill_db_instance


# Test-Code
# Main block removed - use proper testing framework instead
