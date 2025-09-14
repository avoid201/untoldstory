"""
Battle Validator - Facade for specialized validation modules
===========================================================
Facade maintaining backward compatibility while delegating to specialized modules.
All validation logic split into specialized modules to comply with 300-line limit.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple, TYPE_CHECKING
from engine.systems.monster_instance import MonsterInstance

# Import specialized validation modules
from .validation.battle_validation_core import BattleValidationCore
from .validation.battle_validation_moves import BattleValidationMoves
from .validation.battle_validation_talents import BattleValidationTalents

if TYPE_CHECKING:
    from engine.systems.battle.turn_logic import BattleAction
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.talent_system import TalentInstance

logger = logging.getLogger(__name__)


class BattleValidator:
    """
    BATTLE VALIDATOR FACADE - Delegates to specialized validation modules.
    Maintains backward compatibility while using modular architecture.
    """
    
    # Core validation methods - delegate to BattleValidationCore
    @staticmethod
    def validate_battle_state(player_active: Optional[MonsterInstance],
                             enemy_active: Optional[MonsterInstance],
                             player_team: List[MonsterInstance],
                             enemy_team: List[MonsterInstance]) -> bool:
        """Validate battle state - delegates to BattleValidationCore."""
        return BattleValidationCore.validate_battle_state(
            player_active, enemy_active, player_team, enemy_team
        )
    
    @staticmethod
    def validate_action(action: 'BattleAction', 
                       player_active: Optional[MonsterInstance],
                       enemy_active: Optional[MonsterInstance]) -> Tuple[bool, List[str]]:
        """Validate battle action - delegates to BattleValidationCore."""
        return BattleValidationCore.validate_action(action, player_active, enemy_active)
    
    @staticmethod
    def validate_action_with_recovery(action: 'BattleAction', state: 'BattleState') -> Tuple[bool, List[str], List[str]]:
        """Validate action with recovery suggestions - delegates to BattleValidationCore."""
        return BattleValidationCore.validate_action_with_recovery(action, state)
    
    @staticmethod
    def validate_team_composition(team: List[MonsterInstance]) -> Tuple[bool, List[str]]:
        """Validate team composition - delegates to BattleValidationCore."""
        return BattleValidationCore.validate_team_composition(team)
    
    @staticmethod
    def validate_battle_phase(phase: str, required_phase: str) -> bool:
        """Validate battle phase - delegates to BattleValidationCore."""
        return BattleValidationCore.validate_battle_phase(phase, required_phase)
    
    @staticmethod
    def validate_monster_instance(monster: MonsterInstance) -> Tuple[bool, List[str]]:
        """Validate monster instance - delegates to BattleValidationCore."""
        return BattleValidationCore.validate_monster_instance(monster)
    
    # Move validation methods - delegate to BattleValidationMoves
    @staticmethod
    def validate_move(move: Dict[str, Any], monster: MonsterInstance) -> Tuple[bool, List[str]]:
        """Validate move - delegates to BattleValidationMoves."""
        return BattleValidationMoves.validate_move(move, monster)
    
    @staticmethod
    def validate_move_execution(action: 'BattleAction', state: 'BattleState') -> Tuple[bool, str]:
        """Validate move execution - delegates to BattleValidationMoves."""
        return BattleValidationMoves.validate_move_execution(action, state)
    
    @staticmethod
    def get_available_moves_for_monster(monster: MonsterInstance) -> List[Dict[str, Any]]:
        """Get available moves for monster - delegates to BattleValidationMoves."""
        return BattleValidationMoves.get_available_moves_for_monster(monster)
    
    @staticmethod
    def validate_move_availability(move: Dict[str, Any], monster: MonsterInstance) -> bool:
        """Validate move availability - delegates to BattleValidationMoves."""
        return BattleValidationMoves.validate_move_availability(move, monster)
    
    @staticmethod
    def validate_move_targeting(move: Dict[str, Any], target: Optional[MonsterInstance]) -> Tuple[bool, str]:
        """Validate move targeting - delegates to BattleValidationMoves."""
        return BattleValidationMoves.validate_move_targeting(move, target)
    
    # Talent validation methods - delegate to BattleValidationTalents
    @staticmethod
    def validate_talent_instance(talent_instance: 'TalentInstance') -> Tuple[bool, List[str]]:
        """Validate talent instance - delegates to BattleValidationTalents."""
        return BattleValidationTalents.validate_talent_instance(talent_instance)
    
    @staticmethod
    def validate_talent_learning(monster: MonsterInstance, talent_id: str) -> Tuple[bool, List[str]]:
        """Validate talent learning - delegates to BattleValidationTalents."""
        return BattleValidationTalents.validate_talent_learning(monster, talent_id)
    
    @staticmethod
    def validate_talent_upgrade(talent_instance: 'TalentInstance', new_tier: int) -> Tuple[bool, List[str]]:
        """Validate talent upgrade - delegates to BattleValidationTalents."""
        return BattleValidationTalents.validate_talent_upgrade(talent_instance, new_tier)
    
    @staticmethod
    def validate_talent_experience_gain(talent_instance: 'TalentInstance', experience: int) -> Tuple[bool, List[str]]:
        """Validate talent experience gain - delegates to BattleValidationTalents."""
        return BattleValidationTalents.validate_talent_experience_gain(talent_instance, experience)
    
    @staticmethod
    def get_talent_validation_summary(monster: MonsterInstance) -> Dict[str, Any]:
        """Get talent validation summary - delegates to BattleValidationTalents."""
        return BattleValidationTalents.get_talent_validation_summary(monster)
    
    # Scout System Validation Methods
    
    @staticmethod
    def validate_scout_data(monster: MonsterInstance, battle_state: Optional['BattleState'] = None) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validate scout data for monster analysis.
        
        Args:
            monster: Monster to analyze
            battle_state: Current battle state (optional)
            
        Returns:
            Tuple of (is_valid, errors, scout_data)
        """
        errors = []
        scout_data = {}
        
        try:
            # Basic monster validation
            is_valid, basic_errors = BattleValidationCore.validate_monster_instance(monster)
            errors.extend(basic_errors)
            
            if not is_valid:
                return False, errors, {}
            
            # Extract scout data
            scout_data = BattleValidator._extract_scout_data(monster, battle_state)
            
            # Validate scout data completeness
            required_fields = ['name', 'level', 'rank', 'types', 'stats', 'current_hp', 'max_hp']
            for field in required_fields:
                if field not in scout_data:
                    errors.append(f"Missing required scout field: {field}")
            
            # Validate stats
            if 'stats' in scout_data:
                stat_errors = BattleValidator._validate_monster_stats(scout_data['stats'])
                errors.extend(stat_errors)
            
            # Validate type effectiveness data
            if 'types' in scout_data:
                type_errors = BattleValidator._validate_type_data(scout_data['types'])
                errors.extend(type_errors)
            
            # Validate taming data
            taming_errors = BattleValidator._validate_taming_data(monster, battle_state)
            errors.extend(taming_errors)
            
            return len(errors) == 0, errors, scout_data
            
        except Exception as e:
            errors.append(f"Scout data validation error: {str(e)}")
            return False, errors, {}
    
    @staticmethod
    def _extract_scout_data(monster: MonsterInstance, battle_state: Optional['BattleState'] = None) -> Dict[str, Any]:
        """Extract comprehensive scout data from monster."""
        scout_data = {
            'name': getattr(monster, 'name', '???'),
            'level': getattr(monster, 'level', 1),
            'rank': getattr(monster, 'rank', 'D'),
            'types': getattr(monster, 'types', []),
            'current_hp': getattr(monster, 'current_hp', 0),
            'max_hp': getattr(monster, 'max_hp', 1),
            'stats': {},
            'status': getattr(monster, 'status', None),
            'talents': [],
            'passive_abilities': [],
            'moves': [],
            'traits': [],
            'weakness': [],
            'resistance': [],
            'taming_difficulty': 'Mittel',
            'taming_chance': 0.0,
            'description': ''
        }
        
        # Extract stats
        if hasattr(monster, 'stats'):
            if isinstance(monster.stats, dict):
                scout_data['stats'] = monster.stats.copy()
            else:
                for stat in ['atk', 'def', 'mag', 'res', 'spd']:
                    if hasattr(monster.stats, stat):
                        scout_data['stats'][stat] = getattr(monster.stats, stat)
        
        # Extract talents and passive abilities
        if hasattr(monster, 'talents'):
            try:
                from engine.systems.talent_system import get_talent_database
                talent_db = get_talent_database()
                
                for talent_instance in monster.talents:
                    if talent_instance.is_learned:
                        talent = talent_db.get_talent(talent_instance.talent_id)
                        if talent:
                            scout_data['talents'].append({
                                'id': talent.id,
                                'name': talent.name,
                                'tier': talent_instance.current_tier.value,
                                'description': talent.description
                            })
                            
                            # Get passive abilities
                            abilities = talent.get_passive_abilities_for_tier(talent_instance.current_tier)
                            scout_data['passive_abilities'].extend(abilities)
            except Exception as e:
                logger.warning(f"Error extracting talent data: {e}")
        
        # Extract moves
        if hasattr(monster, 'moves'):
            for move in monster.moves[:6]:  # Max 6 moves
                if hasattr(move, 'name'):
                    move_data = {
                        'name': move.name,
                        'type': getattr(move, 'type', '???'),
                        'power': getattr(move, 'power', 0),
                        'category': getattr(move, 'category', '???')
                    }
                    scout_data['moves'].append(move_data)
        
        # Calculate type effectiveness
        if scout_data['types']:
            try:
                from engine.ui.battle_ui_utils import types
                weakness, resistance = types.calculate_weaknesses_and_resistances(scout_data['types'])
                scout_data['weakness'] = weakness
                scout_data['resistance'] = resistance
            except Exception as e:
                logger.warning(f"Error calculating type effectiveness: {e}")
        
        # Calculate taming data
        scout_data['taming_difficulty'] = BattleValidator._calculate_taming_difficulty(scout_data['rank'], scout_data['level'])
        scout_data['taming_chance'] = BattleValidator._calculate_taming_chance(monster, battle_state)
        
        return scout_data
    
    @staticmethod
    def _validate_monster_stats(stats: Dict[str, int]) -> List[str]:
        """Validate monster stats."""
        errors = []
        
        required_stats = ['atk', 'def', 'mag', 'res', 'spd']
        for stat in required_stats:
            if stat not in stats:
                errors.append(f"Missing stat: {stat}")
            elif not isinstance(stats[stat], int) or stats[stat] < 0:
                errors.append(f"Invalid stat value for {stat}: {stats[stat]}")
        
        return errors
    
    @staticmethod
    def _validate_type_data(types: List[str]) -> List[str]:
        """Validate type data."""
        errors = []
        
        valid_types = [
            'Feuer', 'Wasser', 'Erde', 'Luft', 'Pflanze', 'Bestie',
            'Energie', 'Chaos', 'Seuche', 'Mystisch', 'Gottheit', 'Teufel'
        ]
        
        for monster_type in types:
            if monster_type not in valid_types:
                errors.append(f"Invalid type: {monster_type}")
        
        return errors
    
    @staticmethod
    def _validate_taming_data(monster: MonsterInstance, battle_state: Optional['BattleState'] = None) -> List[str]:
        """Validate taming data."""
        errors = []
        
        try:
            # Check if monster can be tamed
            if hasattr(monster, 'can_be_tamed') and not monster.can_be_tamed:
                errors.append("Monster cannot be tamed")
            
            # Check battle state for taming restrictions
            if battle_state and hasattr(battle_state, 'can_catch') and not battle_state.can_catch:
                errors.append("Taming not allowed in current battle")
            
        except Exception as e:
            errors.append(f"Taming validation error: {str(e)}")
        
        return errors
    
    @staticmethod
    def _calculate_taming_difficulty(rank: str, level: int) -> str:
        """Calculate taming difficulty based on rank and level."""
        rank_scores = {
            'F': 1, 'E': 2, 'D': 3, 'C': 4,
            'B': 5, 'A': 6, 'S': 7, 'SS': 8, 'X': 9
        }
        
        score = rank_scores.get(rank, 3) + (level // 10)
        
        if score <= 2:
            return "Sehr Leicht"
        elif score <= 4:
            return "Leicht"
        elif score <= 6:
            return "Mittel"
        elif score <= 8:
            return "Schwer"
        else:
            return "Sehr Schwer"
    
    @staticmethod
    def _calculate_taming_chance(monster: MonsterInstance, battle_state: Optional['BattleState'] = None) -> float:
        """Calculate comprehensive taming chance with all modifiers."""
        try:
            # Base chance from rank
            rank_chances = {
                'F': 0.25, 'E': 0.20, 'D': 0.15, 'C': 0.10,
                'B': 0.08, 'A': 0.05, 'S': 0.03, 'SS': 0.02, 'X': 0.01
            }
            base_chance = rank_chances.get(getattr(monster, 'rank', 'D'), 0.10)
            
            # HP bonus (0-30%)
            current_hp = getattr(monster, 'current_hp', 1)
            max_hp = getattr(monster, 'max_hp', 1)
            hp_ratio = current_hp / max_hp if max_hp > 0 else 1.0
            hp_bonus = (1.0 - hp_ratio) * 0.30
            
            # Meat bonus (0-80%)
            meat_bonus = 0.0
            if battle_state:
                try:
                    from engine.systems.battle.meat_system import get_meat_system
                    meat_system = get_meat_system()
                    if meat_system.has_active_effect():
                        meat_bonus = meat_system.get_active_bonus()
                except Exception as e:
                    logger.debug(f"Could not get meat bonus: {e}")
            
            # Status bonus (0-15%)
            status_bonus = 0.0
            status = getattr(monster, 'status', None)
            if status:
                status_bonuses = {
                    'SLEEP': 0.15,
                    'PARALYSIS': 0.10,
                    'FREEZE': 0.10,
                    'CONFUSION': 0.05,
                    'POISON': 0.0,
                    'BURN': 0.0
                }
                status_bonus = status_bonuses.get(str(status).upper(), 0.0)
            
            # Calculate final chance
            final_chance = base_chance + hp_bonus + meat_bonus + status_bonus
            final_chance = min(0.95, max(0.01, final_chance))  # Clamp between 1% and 95%
            
            return final_chance
            
        except Exception as e:
            logger.error(f"Error calculating taming chance: {e}")
            return 0.10  # Default 10% chance