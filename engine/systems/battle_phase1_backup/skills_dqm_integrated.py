"""
Skills DQM Integrated - Talent System Integration
================================================
Vollständige Integration des Talent-Systems für Move-Verfügbarkeit
"""

import logging
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from engine.systems.talent_system import get_talent_database, TalentTier
from engine.systems.talent_manager import get_talent_manager

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.moves import Move

logger = logging.getLogger(__name__)


class SkillsDQMIntegrated:
    """DQM Talent System Integration für Skills und Moves"""
    
    def __init__(self, battle_state: 'BattleState' = None):
        self.battle_state = battle_state
        self.talent_db = get_talent_database()
        self.talent_manager = get_talent_manager()
        logger.info("SkillsDQMIntegrated initialized")
    
    def validate_move_availability(self, monster: 'MonsterInstance', move_id: str) -> bool:
        """
        Validiere ob Monster einen Move durch Talents hat.
        
        Args:
            monster: Monster das den Move verwenden will
            move_id: ID des Moves
            
        Returns:
            True wenn Move verfügbar ist
        """
        try:
            available_moves = monster.get_available_moves()
            return any(move.id == move_id for move in available_moves)
        except Exception as e:
            logger.error(f"Fehler bei Move-Validierung: {e}")
            return False
    
    def get_available_moves_for_monster(self, monster: 'MonsterInstance') -> List[Dict[str, Any]]:
        """
        Hole alle verfügbaren Moves für ein Monster aus Talents.
        
        Args:
            monster: Monster für das Moves abgerufen werden sollen
            
        Returns:
            Liste der verfügbaren Moves als Dict
        """
        try:
            available_moves = monster.get_available_moves()
            move_list = []
            
            for move in available_moves:
                move_info = {
                    'id': move.id,
                    'name': move.name,
                    'type': move.type,
                    'category': move.category.value if hasattr(move.category, 'value') else str(move.category),
                    'power': move.power,
                    'accuracy': move.accuracy,
                    'description': move.description,
                    'targeting': move.targeting.value if hasattr(move.targeting, 'value') else str(move.targeting)
                }
                move_list.append(move_info)
            
            return move_list
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der verfügbaren Moves: {e}")
            return []
    
    def award_talent_experience(self, monster: 'MonsterInstance', battle_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Vergib Talent-EXP nach Kampf.
        
        Args:
            monster: Monster das EXP erhalten soll
            battle_result: Ergebnis des Battles mit Details
            
        Returns:
            Liste der Talent-Upgrades die stattfanden
        """
        try:
            return monster.gain_talent_experience_from_battle(battle_result)
        except Exception as e:
            logger.error(f"Fehler beim Talent-EXP Gewinn: {e}")
            return []
    
    def calculate_talent_exp(self, battle_result: Dict[str, Any]) -> int:
        """
        Berechne Talent-EXP basierend auf Battle-Ergebnis.
        
        Args:
            battle_result: Battle-Ergebnis mit Details
            
        Returns:
            Talent-EXP Menge
        """
        try:
            base_exp = battle_result.get('base_talent_exp', 10)
            participation_bonus = battle_result.get('participation_bonus', 1.0)
            victory_bonus = battle_result.get('victory_bonus', 1.0)
            
            return int(base_exp * participation_bonus * victory_bonus)
            
        except Exception as e:
            logger.error(f"Fehler bei Talent-EXP Berechnung: {e}")
            return 10
    
    def synthesize_monster_talents(self, parent1: 'MonsterInstance', parent2: 'MonsterInstance') -> List[str]:
        """
        DQM-authentische Talent-Vererbung für Synthesis.
        
        Args:
            parent1: Erstes Elternteil
            parent2: Zweites Elternteil
            
        Returns:
            Liste der vererbten Talent-IDs
        """
        try:
            inherited_talents = []
            
            # Hole alle gelernten Talents beider Eltern
            parent1_talents = [t.talent_id for t in parent1.get_learned_talents()]
            parent2_talents = [t.talent_id for t in parent2.get_learned_talents()]
            
            # Vererbe alle Talents die mindestens ein Elternteil hat
            all_talents = set(parent1_talents + parent2_talents)
            
            for talent_id in all_talents:
                # Prüfe ob Talent vererbbar ist
                talent = self.talent_db.get_talent(talent_id)
                if talent and talent.is_inheritable:
                    inherited_talents.append(talent_id)
            
            # Füge zufällige Talents basierend auf Synthesis-Bonus hinzu
            synthesis_bonus = self._calculate_synthesis_bonus(parent1, parent2)
            if synthesis_bonus > 1.0:
                bonus_talents = self._get_bonus_talents_for_synthesis(parent1, parent2)
                inherited_talents.extend(bonus_talents)
            
            return inherited_talents
            
        except Exception as e:
            logger.error(f"Fehler bei Talent-Vererbung: {e}")
            return []
    
    def _calculate_synthesis_bonus(self, parent1: 'MonsterInstance', parent2: 'MonsterInstance') -> float:
        """Berechne Synthesis-Bonus basierend auf Talent-Kompatibilität."""
        try:
            bonus = 1.0
            
            # Prüfe Talent-Kompatibilität
            parent1_talents = parent1.get_learned_talents()
            parent2_talents = parent2.get_learned_talents()
            
            for talent1 in parent1_talents:
                for talent2 in parent2_talents:
                    if talent1.talent_id == talent2.talent_id:
                        # Gleiche Talents = höherer Bonus
                        talent = self.talent_db.get_talent(talent1.talent_id)
                        if talent:
                            bonus += talent.synthesis_bonus - 1.0
            
            return min(bonus, 2.0)  # Max 2.0x Bonus
            
        except Exception as e:
            logger.error(f"Fehler bei Synthesis-Bonus Berechnung: {e}")
            return 1.0
    
    def _get_bonus_talents_for_synthesis(self, parent1: 'MonsterInstance', parent2: 'MonsterInstance') -> List[str]:
        """Hole Bonus-Talents für Synthesis."""
        try:
            bonus_talents = []
            
            # Prüfe ob spezielle Synthesis-Talents verfügbar sind
            synthesis_talents = [
                "synthesis_master",
                "breath_master",
                "elemental_master"
            ]
            
            for talent_id in synthesis_talents:
                talent = self.talent_db.get_talent(talent_id)
                if talent and talent.is_inheritable:
                    # 20% Chance auf Bonus-Talent
                    import random
                    if random.random() < 0.2:
                        bonus_talents.append(talent_id)
            
            return bonus_talents
            
        except Exception as e:
            logger.error(f"Fehler bei Bonus-Talent Berechnung: {e}")
            return []
    
    def process(self) -> Dict[str, Any]:
        """Process operation."""
        return {'success': True, 'message': 'Talent system integration active'}


# Legacy compatibility
skillsdqmintegrated = SkillsDQMIntegrated
