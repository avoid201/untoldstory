"""
Battle Validation Module
Contains all validation logic for battle states and actions
"""

import logging
from typing import List, Optional
from engine.systems.monster_instance import MonsterInstance

logger = logging.getLogger(__name__)


class BattleValidator:
    """Validates battle states and actions."""
    
    @staticmethod
    def validate_battle_state(player_active: Optional[MonsterInstance],
                             enemy_active: Optional[MonsterInstance],
                             player_team: List[MonsterInstance],
                             enemy_team: List[MonsterInstance]) -> bool:
        """
        Validates the current battle state.
        
        Args:
            player_active: Active player monster
            enemy_active: Active enemy monster
            player_team: Player's team
            enemy_team: Enemy's team
            
        Returns:
            True if the battle state is valid, False otherwise
        """
        try:
            # Check if active monsters exist
            if not player_active or not enemy_active:
                logger.error("Active monsters are missing!")
                return False
            
            # Validate monster stats
            if not BattleValidator._validate_monster_stats(player_active):
                logger.error(f"Invalid stats for player monster: {player_active.name}")
                return False
            
            if not BattleValidator._validate_monster_stats(enemy_active):
                logger.error(f"Invalid stats for enemy monster: {enemy_active.name}")
                return False
            
            # Check if teams are valid
            if not BattleValidator.has_able_monsters(player_team):
                logger.error("No able monsters in player team!")
                return False
            
            if not BattleValidator.has_able_monsters(enemy_team):
                logger.error("No able monsters in enemy team!")
                return False
            
            # Check if battle can continue
            if not BattleValidator.is_battle_valid(player_active, enemy_active, player_team, enemy_team):
                logger.error("Battle cannot continue!")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating battle state: {str(e)}")
            return False
    
    @staticmethod
    def _validate_monster_stats(monster: MonsterInstance) -> bool:
        """
        Validates a monster's stats.
        
        Args:
            monster: The monster to validate
            
        Returns:
            True if all stats are valid, False otherwise
        """
        if not monster:
            return False
        
        try:
            # Check if stats exists and is a dict
            if not hasattr(monster, 'stats') or not isinstance(monster.stats, dict):
                logger.error(f"Monster {monster.name} has no valid stats!")
                return False
            
            # Check required stats
            required_stats = ["hp", "atk", "def", "mag", "res", "spd"]
            for stat in required_stats:
                if stat not in monster.stats:
                    logger.error(f"Stat '{stat}' missing for monster {monster.name}!")
                    return False
                
                if not isinstance(monster.stats[stat], (int, float)) or monster.stats[stat] < 0:
                    logger.error(f"Invalid value for stat '{stat}' in monster {monster.name}: {monster.stats[stat]}")
                    return False
            
            # Check stat_stages
            if not hasattr(monster, 'stat_stages') or monster.stat_stages is None:
                logger.error(f"Monster {monster.name} has no stat_stages!")
                return False
            
            # Check moves
            if not hasattr(monster, 'moves') or not isinstance(monster.moves, list):
                logger.error(f"Monster {monster.name} has no valid moves!")
                return False
            
            # Check basic attributes
            if not hasattr(monster, 'name') or not hasattr(monster, 'level'):
                logger.error(f"Monster missing basic attributes!")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating monster: {str(e)}")
            return False
    
    @staticmethod
    def has_able_monsters(team: List[MonsterInstance]) -> bool:
        """
        Check if team has any conscious monsters.
        
        Args:
            team: Team to check
            
        Returns:
            True if team has able monsters, False otherwise
        """
        try:
            return any(monster and not monster.is_fainted for monster in team)
        except Exception as e:
            logger.error(f"Error checking able monsters: {str(e)}")
            return False
    
    @staticmethod
    def is_battle_valid(player_active: Optional[MonsterInstance],
                       enemy_active: Optional[MonsterInstance],
                       player_team: List[MonsterInstance],
                       enemy_team: List[MonsterInstance]) -> bool:
        """
        Check if battle can continue.
        
        Args:
            player_active: Active player monster
            enemy_active: Active enemy monster
            player_team: Player's team
            enemy_team: Enemy's team
            
        Returns:
            True if battle can continue, False otherwise
        """
        try:
            return (BattleValidator.has_able_monsters(player_team) and 
                   BattleValidator.has_able_monsters(enemy_team) and
                   player_active and not player_active.is_fainted and
                   enemy_active and not enemy_active.is_fainted)
        except Exception as e:
            logger.error(f"Error validating battle: {str(e)}")
            return False
    
    @staticmethod
    def validate_action(action: dict) -> bool:
        """
        Validate a battle action.
        
        Args:
            action: Action dictionary to validate
            
        Returns:
            True if action is valid, False otherwise
        """
        try:
            # Check if action is a dict
            if not action or not isinstance(action, dict):
                logger.error("Invalid action: Not a dict!")
                return False
            
            # Check required fields
            if 'action' not in action:
                logger.error("Action missing required field: action")
                return False
            
            action_type = action.get('action')
            
            # Special handling for UI actions
            if action_type == 'menu_select':
                return 'option' in action
            
            # Check battle action requirements
            if 'actor' not in action:
                logger.error("Battle action needs actor!")
                return False
            
            actor = action.get('actor')
            if not actor or not isinstance(actor, MonsterInstance):
                logger.error("Invalid actor in action!")
                return False
            
            # Check if actor is not fainted
            if actor.is_fainted:
                logger.error(f"Actor {actor.name} is fainted and cannot perform action!")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating action: {str(e)}")
            return False
