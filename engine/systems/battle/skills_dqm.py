"""
🔮 Dragon Quest Monsters Skill System
Implementiert das authentische DQM Skill-Familie-System mit MP-Kosten
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum, auto
from dataclasses import dataclass, field
import json
import logging

logger = logging.getLogger(__name__)

class SkillElement(Enum):
    """Elementar-Typen für Skills"""
    NORMAL = "normal"
    FIRE = "fire"          # Frizz-Familie
    ICE = "ice"            # Crack-Familie  
    THUNDER = "thunder"    # Zap-Familie
    WIND = "wind"          # Woosh-Familie
    EXPLOSION = "explosion" # Bang-Familie
    DARK = "dark"          # Zam-Familie
    LIGHT = "light"        # Heal/Buff
    EARTH = "earth"        # Rock/Ground
    WATER = "water"        # Water attacks
    NONE = "none"          # Status/Buff/Debuff

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
    Zentrale Datenbank für alle DQM Skills
    Basiert auf authentischen Dragon Quest Monsters Daten
    """
    
    def __init__(self):
        self.skill_families: Dict[str, SkillFamily] = {}
        self.element_resistances: Dict[SkillElement, List[SkillElement]] = {}
        self._initialize_skill_families()
        self._initialize_element_chart()
        logger.info("DQM Skill Database initialized")
    
    def _initialize_skill_families(self):
        """Initialisiere alle DQM Skill-Familien"""
        
        # ====== FEUER-FAMILIE (Frizz) ======
        frizz_family = SkillFamily(
            family_name="Frizz",
            element=SkillElement.FIRE,
            skill_type=SkillType.ATTACK,
            target=SkillTarget.SINGLE_ENEMY,
            tiers=[
                SkillTier("Frizz", 1, 10, 2, 1.0, 
                         "Kleine Feuerkugel auf einen Gegner"),
                SkillTier("Frizzle", 2, 20, 4, 1.0,
                         "Mittlere Feuerkugel auf einen Gegner"),
                SkillTier("Kafrizz", 3, 40, 8, 0.95,
                         "Große Feuerkugel auf einen Gegner"),
                SkillTier("Kazfrizzle", 4, 80, 16, 0.9,
                         "Massive Feuerkugel auf einen Gegner")
            ]
        )
        self.skill_families["Frizz"] = frizz_family
        
        # Sizz-Familie (Gruppen-Feuer)
        sizz_family = SkillFamily(
            family_name="Sizz",
            element=SkillElement.FIRE,
            skill_type=SkillType.ATTACK,
            target=SkillTarget.ALL_ENEMIES,
            tiers=[
                SkillTier("Sizz", 1, 8, 4, 1.0,
                         "Feuerwelle auf alle Gegner"),
                SkillTier("Sizzle", 2, 16, 7, 1.0,
                         "Größere Feuerwelle auf alle Gegner"),
                SkillTier("Kasizz", 3, 32, 12, 0.95,
                         "Mächtige Feuerwelle auf alle Gegner"),
                SkillTier("Kasizzle", 4, 64, 20, 0.9,
                         "Inferno auf alle Gegner")
            ]
        )
        self.skill_families["Sizz"] = sizz_family
        
        # ====== EIS-FAMILIE (Crack) ======
        crack_family = SkillFamily(
            family_name="Crack",
            element=SkillElement.ICE,
            skill_type=SkillType.ATTACK,
            target=SkillTarget.SINGLE_ENEMY,
            tiers=[
                SkillTier("Crack", 1, 12, 3, 1.0,
                         "Eissplitter auf einen Gegner"),
                SkillTier("Crackle", 2, 25, 5, 1.0,
                         "Eisspeer auf einen Gegner"),
                SkillTier("Kacrack", 3, 50, 10, 0.95,
                         "Eisberg auf einen Gegner"),
                SkillTier("Kacrackle", 4, 100, 20, 0.9,
                         "Absolute Zero auf einen Gegner")
            ]
        )
        self.skill_families["Crack"] = crack_family
        
        # ====== BLITZ-FAMILIE (Zap) ======
        zap_family = SkillFamily(
            family_name="Zap",
            element=SkillElement.THUNDER,
            skill_type=SkillType.ATTACK,
            target=SkillTarget.SINGLE_ENEMY,
            tiers=[
                SkillTier("Zap", 1, 15, 4, 1.0,
                         "Blitzschlag auf einen Gegner"),
                SkillTier("Zapple", 2, 30, 7, 1.0,
                         "Starker Blitz auf einen Gegner"),
                SkillTier("Kazap", 3, 60, 15, 0.95,
                         "Gewaltiger Blitz auf einen Gegner"),
                SkillTier("Kazapple", 4, 120, 30, 0.9,
                         "Göttlicher Blitz auf einen Gegner")
            ]
        )
        self.skill_families["Zap"] = zap_family
        
        # Thwack-Familie (Alle Blitze)
        thwack_family = SkillFamily(
            family_name="Thwack",
            element=SkillElement.THUNDER,
            skill_type=SkillType.ATTACK,
            target=SkillTarget.ALL_ENEMIES,
            tiers=[
                SkillTier("Zammle", 1, 10, 6, 1.0,
                         "Blitze auf alle Gegner"),
                SkillTier("Thwack", 2, 20, 10, 0.9,
                         "Starke Blitze auf alle Gegner"),
                SkillTier("Kathwack", 3, 40, 18, 0.85,
                         "Gewitterfront auf alle Gegner")
            ]
        )
        self.skill_families["Thwack"] = thwack_family
        
        # ====== WIND-FAMILIE (Woosh) ======
        woosh_family = SkillFamily(
            family_name="Woosh",
            element=SkillElement.WIND,
            skill_type=SkillType.ATTACK,
            target=SkillTarget.ALL_ENEMIES,
            tiers=[
                SkillTier("Woosh", 1, 8, 2, 1.0,
                         "Windböe auf alle Gegner"),
                SkillTier("Swoosh", 2, 18, 4, 1.0,
                         "Windsichel auf alle Gegner"),
                SkillTier("Kaswoosh", 3, 35, 8, 0.95,
                         "Tornado auf alle Gegner"),
                SkillTier("Kaswooshle", 4, 70, 16, 0.9,
                         "Hurrikan auf alle Gegner")
            ]
        )
        self.skill_families["Woosh"] = woosh_family
        
        # ====== EXPLOSION-FAMILIE (Bang) ======
        bang_family = SkillFamily(
            family_name="Bang",
            element=SkillElement.EXPLOSION,
            skill_type=SkillType.ATTACK,
            target=SkillTarget.ALL_ENEMIES,
            tiers=[
                SkillTier("Bang", 1, 15, 4, 1.0,
                         "Kleine Explosion auf alle Gegner"),
                SkillTier("Boom", 2, 30, 8, 1.0,
                         "Explosion auf alle Gegner"),
                SkillTier("Kaboom", 3, 60, 15, 0.95,
                         "Große Explosion auf alle Gegner"),
                SkillTier("Kaboomle", 4, 120, 30, 0.9,
                         "Mega-Explosion auf alle Gegner")
            ]
        )
        self.skill_families["Bang"] = bang_family
        
        # ====== DUNKELHEIT-FAMILIE (Zam) ======
        zam_family = SkillFamily(
            family_name="Zam",
            element=SkillElement.DARK,
            skill_type=SkillType.ATTACK,
            target=SkillTarget.SINGLE_ENEMY,
            tiers=[
                SkillTier("Zam", 1, 18, 5, 1.0,
                         "Dunkle Energie auf einen Gegner"),
                SkillTier("Zammle", 2, 35, 9, 1.0,
                         "Dunkler Strahl auf einen Gegner"),
                SkillTier("Kazam", 3, 70, 18, 0.95,
                         "Dunkle Macht auf einen Gegner"),
                SkillTier("Kazammle", 4, 140, 35, 0.9,
                         "Ultimative Dunkelheit auf einen Gegner")
            ]
        )
        self.skill_families["Zam"] = zam_family
        
        # ====== HEIL-FAMILIE ======
        heal_family = SkillFamily(
            family_name="Heal",
            element=SkillElement.LIGHT,
            skill_type=SkillType.HEAL,
            target=SkillTarget.SINGLE_ALLY,
            tiers=[
                SkillTier("Heal", 1, 30, 3, 1.0,
                         "Heilt 30 HP eines Verbündeten"),
                SkillTier("Midheal", 2, 75, 6, 1.0,
                         "Heilt 75 HP eines Verbündeten"),
                SkillTier("Fullheal", 3, 999, 12, 1.0,
                         "Heilt alle HP eines Verbündeten"),
                SkillTier("Omniheal", 4, 999, 20, 1.0,
                         "Heilt alle HP aller Verbündeten",
                         {"target_override": SkillTarget.ALL_ALLIES})
            ]
        )
        self.skill_families["Heal"] = heal_family
        
        # Multiheal-Familie (Gruppen-Heilung)
        multiheal_family = SkillFamily(
            family_name="Multiheal",
            element=SkillElement.LIGHT,
            skill_type=SkillType.HEAL,
            target=SkillTarget.ALL_ALLIES,
            tiers=[
                SkillTier("Multiheal", 1, 25, 10, 1.0,
                         "Heilt 25 HP aller Verbündeten"),
                SkillTier("Moreheal", 2, 50, 18, 1.0,
                         "Heilt 50 HP aller Verbündeten"),
                SkillTier("Omniheal", 3, 100, 32, 1.0,
                         "Heilt 100 HP aller Verbündeten")
            ]
        )
        self.skill_families["Multiheal"] = multiheal_family
        
        # ====== BUFF-FAMILIEN ======
        buff_family = SkillFamily(
            family_name="Buff",
            element=SkillElement.NONE,
            skill_type=SkillType.BUFF,
            target=SkillTarget.SINGLE_ALLY,
            tiers=[
                SkillTier("Buff", 1, 0, 3, 1.0,
                         "Erhöht ATK eines Verbündeten",
                         {"stat": "atk", "stages": 1}),
                SkillTier("Kabuff", 1, 0, 3, 1.0,
                         "Erhöht DEF eines Verbündeten",
                         {"stat": "def", "stages": 1}),
                SkillTier("Oomph", 2, 0, 6, 1.0,
                         "Verdoppelt ATK eines Verbündeten",
                         {"stat": "atk", "stages": 2}),
                SkillTier("Insulatle", 2, 0, 4, 1.0,
                         "Erhöht Feuer/Eis-Resistenz",
                         {"resist": ["fire", "ice"], "amount": 0.5})
            ]
        )
        self.skill_families["Buff"] = buff_family
        
        # Acceleratle-Familie (Speed-Buffs)
        speed_family = SkillFamily(
            family_name="Acceleratle",
            element=SkillElement.NONE,
            skill_type=SkillType.BUFF,
            target=SkillTarget.ALL_ALLIES,
            tiers=[
                SkillTier("Acceleratle", 1, 0, 2, 1.0,
                         "Erhöht Speed aller Verbündeten",
                         {"stat": "spd", "stages": 1}),
                SkillTier("Accelerate", 2, 0, 4, 1.0,
                         "Erhöht Speed stark",
                         {"stat": "spd", "stages": 2})
            ]
        )
        self.skill_families["Acceleratle"] = speed_family
        
        # ====== DEBUFF-FAMILIEN ======
        sap_family = SkillFamily(
            family_name="Sap",
            element=SkillElement.NONE,
            skill_type=SkillType.DEBUFF,
            target=SkillTarget.SINGLE_ENEMY,
            tiers=[
                SkillTier("Sap", 1, 0, 3, 0.9,
                         "Senkt DEF eines Gegners",
                         {"stat": "def", "stages": -1}),
                SkillTier("Kasap", 2, 0, 6, 0.85,
                         "Senkt DEF aller Gegner",
                         {"stat": "def", "stages": -1, 
                          "target_override": SkillTarget.ALL_ENEMIES}),
                SkillTier("Blunt", 1, 0, 3, 0.9,
                         "Senkt ATK eines Gegners",
                         {"stat": "atk", "stages": -1})
            ]
        )
        self.skill_families["Sap"] = sap_family
        
        # Decelerate-Familie
        slow_family = SkillFamily(
            family_name="Decelerate",
            element=SkillElement.NONE,
            skill_type=SkillType.DEBUFF,
            target=SkillTarget.ALL_ENEMIES,
            tiers=[
                SkillTier("Decelerate", 1, 0, 3, 0.85,
                         "Senkt Speed aller Gegner",
                         {"stat": "spd", "stages": -1}),
                SkillTier("Deceleratle", 2, 0, 6, 0.8,
                         "Senkt Speed stark",
                         {"stat": "spd", "stages": -2})
            ]
        )
        self.skill_families["Decelerate"] = slow_family
        
        # ====== STATUS-FAMILIEN ======
        sleep_family = SkillFamily(
            family_name="Sleep",
            element=SkillElement.NONE,
            skill_type=SkillType.STATUS,
            target=SkillTarget.ALL_ENEMIES,
            tiers=[
                SkillTier("Snooze", 1, 0, 2, 0.7,
                         "Versetzt Gegner in Schlaf",
                         {"status": "sleep", "duration": 2}),
                SkillTier("Kasnooze", 2, 0, 5, 0.6,
                         "Tiefschlaf für alle Gegner",
                         {"status": "sleep", "duration": 3})
            ]
        )
        self.skill_families["Sleep"] = sleep_family
        
        # ====== ATEM-ATTACKEN ======
        fire_breath_family = SkillFamily(
            family_name="FireBreath",
            element=SkillElement.FIRE,
            skill_type=SkillType.BREATH,
            target=SkillTarget.ALL_ENEMIES,
            tiers=[
                SkillTier("Fire Breath", 1, 20, 0, 1.0,
                         "Feueratem auf alle Gegner"),
                SkillTier("Flame Breath", 2, 40, 0, 1.0,
                         "Starker Feueratem"),
                SkillTier("Inferno", 3, 70, 0, 1.0,
                         "Höllisches Inferno"),
                SkillTier("Scorch", 4, 120, 0, 1.0,
                         "Alles verbrennender Atem")
            ]
        )
        self.skill_families["FireBreath"] = fire_breath_family
        
        # Ice Breath
        ice_breath_family = SkillFamily(
            family_name="IceBreath",
            element=SkillElement.ICE,
            skill_type=SkillType.BREATH,
            target=SkillTarget.ALL_ENEMIES,
            tiers=[
                SkillTier("Cool Breath", 1, 18, 0, 1.0,
                         "Eisiger Atem auf alle Gegner"),
                SkillTier("Ice Breath", 2, 35, 0, 1.0,
                         "Frostiger Atem"),
                SkillTier("Blizzard Breath", 3, 65, 0, 1.0,
                         "Blizzard-Atem"),
                SkillTier("C-c-cold Breath", 4, 110, 0, 1.0,
                         "Absolut null Atem")
            ]
        )
        self.skill_families["IceBreath"] = ice_breath_family
        
        # ====== TANZ-SKILLS ======
        dance_family = SkillFamily(
            family_name="Dance",
            element=SkillElement.NONE,
            skill_type=SkillType.DANCE,
            target=SkillTarget.RANDOM_ENEMIES,
            tiers=[
                SkillTier("Sultry Dance", 1, 0, 0, 0.75,
                         "Verführerischer Tanz - verwirrt Gegner",
                         {"status": "confusion", "hits": 1}),
                SkillTier("Hustle Dance", 2, 0, 0, 1.0,
                         "Heilt alle Verbündeten beim Tanzen",
                         {"heal": 70, "target_override": SkillTarget.ALL_ALLIES}),
                SkillTier("Death Dance", 3, 0, 0, 0.3,
                         "Todestanz - instant KO möglich",
                         {"instant_death": True, "hits": 3})
            ]
        )
        self.skill_families["Dance"] = dance_family
        
        # ====== SLASH-ATTACKEN ======
        slash_family = SkillFamily(
            family_name="Slash",
            element=SkillElement.NORMAL,
            skill_type=SkillType.SLASH,
            target=SkillTarget.SINGLE_ENEMY,
            tiers=[
                SkillTier("Dragon Slash", 1, 50, 0, 1.0,
                         "Extra Schaden gegen Drachen",
                         {"bonus_vs": "dragon", "multiplier": 2.0}),
                SkillTier("Metal Slash", 1, 1, 2, 1.0,
                         "Durchdringt Metal-Verteidigung",
                         {"ignore_def": True, "fixed_damage": 1}),
                SkillTier("Falcon Slash", 2, 30, 0, 0.9,
                         "Zwei schnelle Schläge",
                         {"hits": 2, "damage_per_hit": 0.75}),
                SkillTier("Gigaslash", 3, 100, 15, 0.95,
                         "Mächtiger Schwerthieb mit Blitz",
                         {"element_add": "thunder"})
            ]
        )
        self.skill_families["Slash"] = slash_family
        
        logger.info(f"Initialized {len(self.skill_families)} skill families")
    
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
    
    def get_skill(self, family_name: str, tier: int = 1) -> Optional[SkillTier]:
        """Hole einen spezifischen Skill"""
        family = self.skill_families.get(family_name)
        if family:
            return family.get_tier(tier)
        return None
    
    def get_skill_by_name(self, skill_name: str) -> Optional[Tuple[SkillFamily, SkillTier]]:
        """Suche Skill by Name in allen Familien"""
        for family in self.skill_families.values():
            skill = family.get_by_name(skill_name)
            if skill:
                return (family, skill)
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
        for name, family in self.skill_families.items():
            if family.skill_type == skill_type:
                results.append((name, family))
        return results
    
    def get_skills_by_element(self, element: SkillElement) -> List[Tuple[str, SkillFamily]]:
        """Hole alle Skills eines Elements"""
        results = []
        for name, family in self.skill_families.items():
            if family.element == element:
                results.append((name, family))
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
        """Prüfe ob Monster Skill lernen kann"""
        # Basis Level-Requirements
        level_requirements = {
            1: 1,   # Tier 1: Ab Level 1
            2: 10,  # Tier 2: Ab Level 10
            3: 25,  # Tier 3: Ab Level 25
            4: 50   # Tier 4: Ab Level 50
        }
        
        required_level = level_requirements.get(skill_tier, 99)
        
        # Manche Monster-Familien lernen Skills früher
        if monster_family:
            if monster_family.lower() in ["dragon", "demon", "????"]:
                required_level -= 5  # Bonus für spezielle Familien
        
        return monster_level >= required_level
    
    def get_skill_inheritance(self, parent1_skills: List[str], 
                            parent2_skills: List[str],
                            offspring_family: str) -> List[str]:
        """
        Berechne Skill-Vererbung für Synthesis
        Basiert auf DQM-Regeln
        """
        inherited = []
        
        # Regel 1: Gemeinsame Skills werden vererbt
        common_skills = set(parent1_skills) & set(parent2_skills)
        inherited.extend(list(common_skills)[:2])  # Max 2 gemeinsame
        
        # Regel 2: Upgrade wenn beide Eltern gleiche Familie haben
        for skill_name in parent1_skills:
            result = self.get_skill_by_name(skill_name)
            if not result:
                continue
                
            family, skill = result
            # Prüfe ob anderer Elternteil höheren Tier hat
            for p2_skill in parent2_skills:
                p2_result = self.get_skill_by_name(p2_skill)
                if p2_result and p2_result[0].family_name == family.family_name:
                    p2_tier = p2_result[1].tier
                    if p2_tier > skill.tier:
                        # Vererbe höheren Tier
                        higher_skill = family.get_tier(p2_tier)
                        if higher_skill and higher_skill.name not in inherited:
                            inherited.append(higher_skill.name)
                            break
        
        # Regel 3: Zufällige Skills von Eltern
        all_parent_skills = list(set(parent1_skills + parent2_skills) - set(inherited))
        import random
        random.shuffle(all_parent_skills)
        
        # Füge bis zu 4 Skills hinzu
        for skill in all_parent_skills:
            if len(inherited) >= 4:
                break
            if skill not in inherited:
                inherited.append(skill)
        
        return inherited[:4]  # Maximum 4 Skills
    
    def export_to_json(self, filepath: str):
        """Exportiere Skill-Datenbank als JSON"""
        data = {}
        for family_name, family in self.skill_families.items():
            data[family_name] = {
                "element": family.element.value,
                "type": family.skill_type.value,
                "target": family.target.value,
                "tiers": [
                    {
                        "name": tier.name,
                        "tier": tier.tier,
                        "power": tier.power,
                        "mp_cost": tier.mp_cost,
                        "accuracy": tier.accuracy,
                        "description": tier.description,
                        "effects": tier.effects
                    }
                    for tier in family.tiers
                ]
            }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported skill database to {filepath}")


# Singleton-Instanz
_skill_db_instance = None

def get_skill_database() -> DQMSkillDatabase:
    """Hole Singleton-Instanz der Skill-Datenbank"""
    global _skill_db_instance
    if _skill_db_instance is None:
        _skill_db_instance = DQMSkillDatabase()
    return _skill_db_instance


# Test-Code
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialisiere Datenbank
    db = get_skill_database()
    
    print("\n=== DQM SKILL DATABASE TEST ===\n")
    
    # Teste Skill-Abruf
    print("1. Skill-Abruf Test:")
    frizz = db.get_skill("Frizz", 1)
    if frizz:
        print(f"  {frizz.name}: {frizz.description}")
        print(f"  Power: {frizz.power}, MP: {frizz.mp_cost}")
    
    # Teste Skill-Suche
    print("\n2. Skill-Suche Test:")
    result = db.get_skill_by_name("Kaboom")
    if result:
        family, skill = result
        print(f"  Gefunden: {skill.name} aus Familie {family.family_name}")
        print(f"  Element: {family.element.value}, Typ: {family.skill_type.value}")
    
    # Teste Element-Modifikator
    print("\n3. Element-Modifikator Test:")
    mod = db.get_element_modifier(SkillElement.FIRE, SkillElement.ICE)
    print(f"  Feuer vs Eis: {mod:.0%} Schaden")
    mod = db.get_element_modifier(SkillElement.ICE, SkillElement.FIRE)
    print(f"  Eis vs Feuer: {mod:.0%} Schaden")
    
    # Teste Skill-Vererbung
    print("\n4. Skill-Vererbung Test:")
    parent1 = ["Frizz", "Heal", "Buff"]
    parent2 = ["Frizzle", "Crack", "Buff"]
    inherited = db.get_skill_inheritance(parent1, parent2, "Dragon")
    print(f"  Eltern 1: {parent1}")
    print(f"  Eltern 2: {parent2}")
    print(f"  Vererbt: {inherited}")
    
    # Zeige alle Heal-Skills
    print("\n5. Alle Heal-Skills:")
    heal_skills = db.get_skills_by_type(SkillType.HEAL)
    for name, family in heal_skills:
        print(f"  Familie: {name}")
        for tier in family.tiers:
            print(f"    - {tier.name} (MP: {tier.mp_cost})")
    
    # Exportiere als JSON
    print("\n6. Exportiere Datenbank...")
    db.export_to_json("/tmp/dqm_skills.json")
    print("  ✅ Export erfolgreich!")
    
    print("\n=== TEST ABGESCHLOSSEN ===")
