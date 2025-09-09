"""
🎯 Talent Manager - Zentrale Verwaltung des DQM Talent-Systems
Verwaltet Talent-Learning, -Upgrades und passive Fähigkeiten
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json
import logging
from pathlib import Path

from engine.systems.talent_system import TalentInstance, TalentTier, get_talent_database
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance

logger = logging.getLogger(__name__)

@dataclass
class TalentLearningRule:
    """Regel für Talent-Learning"""
    talent_id: str
    required_level: int
    prerequisites: List[str]
    type_requirements: List[str]
    special_conditions: Dict[str, Any] = None

class TalentManager:
    """Zentrale Verwaltung des Talent-Systems"""
    
    def __init__(self):
        self.talent_db = get_talent_database()
        self.learning_rules = self._load_learning_rules()
        self.passive_abilities = self._load_passive_abilities()
    
    def _load_learning_rules(self) -> Dict[str, TalentLearningRule]:
        """Lade Talent-Learning-Regeln aus JSON"""
        learning_rules = {}
        
        try:
            learning_file = Path("data/talent_learning.json")
            if not learning_file.exists():
                logger.warning("Talent-Learning-Datei nicht gefunden")
                return learning_rules
            
            with open(learning_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            type_rules = data.get("type_based_learning", {})
            
            for monster_type, type_data in type_rules.items():
                learnable = type_data.get("learnable", [])
                level_requirements = type_data.get("level_requirements", {})
                
                for talent_id in learnable:
                    required_level = level_requirements.get(talent_id, 1)
                    
                    learning_rules[talent_id] = TalentLearningRule(
                        talent_id=talent_id,
                        required_level=required_level,
                        prerequisites=[],
                        type_requirements=[monster_type]
                    )
            
            logger.info(f"Geladen: {len(learning_rules)} Talent-Learning-Regeln")
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der Learning-Regeln: {e}")
        
        return learning_rules
    
    def _load_passive_abilities(self) -> Dict[str, Dict[str, Any]]:
        """Lade passive Fähigkeiten aus JSON"""
        passive_abilities = {}
        
        try:
            abilities_file = Path("data/passive_abilities.json")
            if not abilities_file.exists():
                logger.warning("Passive-Fähigkeiten-Datei nicht gefunden")
                return passive_abilities
            
            with open(abilities_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for ability in data.get("passive_abilities", []):
                passive_abilities[ability["id"]] = ability
            
            logger.info(f"Geladen: {len(passive_abilities)} passive Fähigkeiten")
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der passiven Fähigkeiten: {e}")
        
        return passive_abilities
    
    def get_available_moves(self, monster: 'MonsterInstance') -> List[str]:
        """Hole alle verfügbaren Moves eines Monsters aus seinen Talenten"""
        moves = []
        
        try:
            for talent_instance in monster.talents:
                if not talent_instance.is_learned:
                    continue
                
                talent = self.talent_db.get_talent(talent_instance.talent_id)
                if not talent:
                    continue
                
                talent_moves = talent.get_moves_for_tier(
                    talent_instance.current_tier, 
                    monster.level
                )
                moves.extend(talent_moves)
            
            return list(set(moves))  # Entferne Duplikate
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der Moves: {e}")
            return []
    
    def get_passive_abilities(self, monster: 'MonsterInstance') -> List[Dict[str, Any]]:
        """Hole alle passiven Fähigkeiten eines Monsters"""
        passive_abilities = []
        
        try:
            for talent_instance in monster.talents:
                if not talent_instance.is_learned:
                    continue
                
                talent = self.talent_db.get_talent(talent_instance.talent_id)
                if not talent:
                    continue
                
                talent_passives = talent.get_passive_abilities_for_tier(talent_instance.current_tier)
                passive_abilities.extend(talent_passives)
            
            return passive_abilities
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der passiven Fähigkeiten: {e}")
            return []
    
    def can_learn_talent(self, monster: 'MonsterInstance', talent_id: str) -> bool:
        """Prüfe ob Monster ein Talent lernen kann"""
        try:
            # Prüfe ob Talent existiert
            talent = self.talent_db.get_talent(talent_id)
            if not talent:
                return False
            
            # Prüfe ob bereits gelernt
            for existing_talent in monster.talents:
                if existing_talent.talent_id == talent_id:
                    return False
            
            # Prüfe Learning-Regel
            if talent_id in self.learning_rules:
                rule = self.learning_rules[talent_id]
                
                # Level-Anforderung
                if monster.level < rule.required_level:
                    return False
                
                # Type-Anforderung
                if rule.type_requirements:
                    if not any(t in rule.type_requirements for t in monster.types):
                        return False
                
                # Prerequisites
                for prereq in rule.prerequisites:
                    if not self.has_talent(monster, prereq):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Prüfen des Talent-Lernens: {e}")
            return False
    
    def learn_talent(self, monster: 'MonsterInstance', talent_id: str) -> bool:
        """Lerne ein neues Talent"""
        try:
            if not self.can_learn_talent(monster, talent_id):
                return False
            
            talent_instance = TalentInstance(talent_id, is_learned=True)
            monster.talents.append(talent_instance)
            
            # Aktualisiere Moves
            monster.moves = monster._initialize_moves()
            
            logger.info(f"{monster.name} hat Talent {talent_id} gelernt!")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Lernen des Talents {talent_id}: {e}")
            return False
    
    def upgrade_talent(self, monster: 'MonsterInstance', talent_id: str) -> bool:
        """Upgrade ein bestehendes Talent"""
        try:
            for talent_instance in monster.talents:
                if (talent_instance.talent_id == talent_id and 
                    talent_instance.is_learned):
                    
                    talent = self.talent_db.get_talent(talent_id)
                    if not talent:
                        return False
                    
                    if talent.can_upgrade_to_tier(talent_instance.current_tier, monster.level):
                        talent_instance.current_tier = TalentTier(talent_instance.current_tier.value + 1)
                        
                        # Aktualisiere Moves
                        monster.moves = monster._initialize_moves()
                        
                        logger.info(f"{monster.name} hat Talent {talent_id} auf Stufe {talent_instance.current_tier.value} upgegradet!")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Fehler beim Upgraden des Talents {talent_id}: {e}")
            return False
    
    def has_talent(self, monster: 'MonsterInstance', talent_id: str) -> bool:
        """Prüfe ob Monster ein Talent hat"""
        for talent_instance in monster.talents:
            if talent_instance.talent_id == talent_id and talent_instance.is_learned:
                return True
        return False
    
    def get_talent_tier(self, monster: 'MonsterInstance', talent_id: str) -> Optional[int]:
        """Hole das aktuelle Tier eines Talents"""
        for talent_instance in monster.talents:
            if talent_instance.talent_id == talent_id and talent_instance.is_learned:
                return talent_instance.current_tier.value
        return None
    
    def get_learnable_talents(self, monster: 'MonsterInstance') -> List[str]:
        """Hole alle lernbaren Talents für ein Monster"""
        learnable = []
        
        try:
            for talent_id, rule in self.learning_rules.items():
                if self.can_learn_talent(monster, talent_id):
                    learnable.append(talent_id)
            
            return learnable
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der lernbaren Talents: {e}")
            return []
    
    def get_talent_info(self, monster: 'MonsterInstance', talent_id: str) -> Optional[Dict[str, Any]]:
        """Hole detaillierte Informationen über ein Talent"""
        try:
            talent = self.talent_db.get_talent(talent_id)
            if not talent:
                return None
            
            # Prüfe ob gelernt
            learned = self.has_talent(monster, talent_id)
            current_tier = self.get_talent_tier(monster, talent_id)
            
            # Prüfe ob Upgrade möglich ist (ohne es durchzuführen)
            can_upgrade = False
            if learned and current_tier:
                can_upgrade = talent.can_upgrade_to_tier(TalentTier(current_tier), monster.level)
            
            return {
                "id": talent.id,
                "name": talent.name,
                "description": talent.description,
                "category": talent.category.value,
                "learned": learned,
                "current_tier": current_tier,
                "max_tier": talent.max_tier.value,
                "can_learn": self.can_learn_talent(monster, talent_id),
                "can_upgrade": can_upgrade,
                "moves": talent.get_moves_for_tier(TalentTier(current_tier) if current_tier else TalentTier.BASIC, monster.level),
                "passive_abilities": talent.get_passive_abilities_for_tier(TalentTier(current_tier) if current_tier else TalentTier.BASIC)
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der Talent-Info: {e}")
            return None
    
    def apply_passive_effects(self, monster: 'MonsterInstance', effect_type: str, value: float) -> float:
        """Wende passive Effekte an"""
        try:
            passive_abilities = self.get_passive_abilities(monster)
            
            for ability in passive_abilities:
                if ability.get("effect_type") == effect_type:
                    ability_value = ability.get("value", 0)
                    
                    if effect_type == "damage_reduction":
                        # Reduziere Schaden
                        value *= (1 - ability_value)
                    elif effect_type == "stat_boost":
                        # Erhöhe Wert
                        value *= (1 + ability_value)
                    else:
                        # Standard: Multipliziere mit (1 + Wert)
                        value *= (1 + ability_value)
            
            return value
            
        except Exception as e:
            logger.error(f"Fehler beim Anwenden passiver Effekte: {e}")
            return value

# Singleton-Instanz
_talent_manager = None

def get_talent_manager() -> TalentManager:
    """Hole die Singleton-Instanz des Talent-Managers"""
    global _talent_manager
    if _talent_manager is None:
        _talent_manager = TalentManager()
    return _talent_manager
