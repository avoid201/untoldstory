"""
Battle Validation Talents - Talent validation logic
===================================================
Talent validation functionality extracted from battle_validation.py
to comply with 300-line limit.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple, TYPE_CHECKING
from engine.systems.monster_instance import MonsterInstance

if TYPE_CHECKING:
    from engine.systems.talent_system import TalentInstance

logger = logging.getLogger(__name__)


class BattleValidationTalents:
    """
    Talent validation functionality.
    Handles talent-specific validation logic.
    """
    
    @staticmethod
    def validate_talent_instance(talent_instance: 'TalentInstance') -> Tuple[bool, List[str]]:
        """
        Validate talent instance.
        
        Args:
            talent_instance: Talent instance to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            errors = []
            
            # Check if talent instance exists
            if not talent_instance:
                errors.append("No talent instance provided")
                return False, errors
            
            # Check required attributes
            required_attrs = ['talent_id', 'current_tier', 'experience', 'is_learned']
            for attr in required_attrs:
                if not hasattr(talent_instance, attr):
                    errors.append(f"Missing required attribute: {attr}")
                    return False, errors
            
            # Check talent_id
            if not talent_instance.talent_id or not isinstance(talent_instance.talent_id, str):
                errors.append("Invalid talent_id")
                return False, errors
            
            # Check current_tier
            if not isinstance(talent_instance.current_tier, int) or talent_instance.current_tier < 1:
                errors.append("Invalid current_tier")
                return False, errors
            
            # Check experience
            if not isinstance(talent_instance.experience, int) or talent_instance.experience < 0:
                errors.append("Invalid experience value")
                return False, errors
            
            # Check is_learned
            if not isinstance(talent_instance.is_learned, bool):
                errors.append("is_learned must be boolean")
                return False, errors
            
            return True, errors
            
        except Exception as e:
            logger.error(f"Talent instance validation failed: {e}")
            return False, [f"Validation error: {e}"]
    
    @staticmethod
    def validate_talent_learning(monster: MonsterInstance, talent_id: str) -> Tuple[bool, List[str]]:
        """
        Validate if monster can learn talent.
        
        Args:
            monster: Monster to check
            talent_id: Talent ID to check
            
        Returns:
            Tuple of (can_learn, error_messages)
        """
        try:
            errors = []
            
            # Check if monster exists
            if not monster:
                errors.append("No monster provided")
                return False, errors
            
            # Check if monster has talents attribute
            if not hasattr(monster, 'talents'):
                errors.append("Monster has no talents attribute")
                return False, errors
            
            # Check if talent_id is valid
            if not talent_id or not isinstance(talent_id, str):
                errors.append("Invalid talent_id")
                return False, errors
            
            # Check if monster already has this talent
            for talent_instance in monster.talents:
                if hasattr(talent_instance, 'talent_id') and talent_instance.talent_id == talent_id:
                    errors.append("Monster already has this talent")
                    return False, errors
            
            # Check talent limit (max 4 talents per monster)
            if len(monster.talents) >= 4:
                errors.append("Monster has maximum number of talents (4)")
                return False, errors
            
            return True, errors
            
        except Exception as e:
            logger.error(f"Talent learning validation failed: {e}")
            return False, [f"Validation error: {e}"]
    
    @staticmethod
    def validate_talent_upgrade(talent_instance: 'TalentInstance', new_tier: int) -> Tuple[bool, List[str]]:
        """
        Validate talent tier upgrade.
        
        Args:
            talent_instance: Talent instance to upgrade
            new_tier: New tier to upgrade to
            
        Returns:
            Tuple of (can_upgrade, error_messages)
        """
        try:
            errors = []
            
            # Check if talent instance exists
            if not talent_instance:
                errors.append("No talent instance provided")
                return False, errors
            
            # Check if talent is learned
            if not talent_instance.is_learned:
                errors.append("Talent is not learned")
                return False, errors
            
            # Check if new tier is valid
            if not isinstance(new_tier, int) or new_tier < 1 or new_tier > 5:
                errors.append("Invalid tier (must be 1-5)")
                return False, errors
            
            # Check if new tier is higher than current
            if new_tier <= talent_instance.current_tier:
                errors.append("New tier must be higher than current tier")
                return False, errors
            
            # Check if tier jump is valid (max 1 tier at a time)
            if new_tier > talent_instance.current_tier + 1:
                errors.append("Cannot skip tiers")
                return False, errors
            
            return True, errors
            
        except Exception as e:
            logger.error(f"Talent upgrade validation failed: {e}")
            return False, [f"Validation error: {e}"]
    
    @staticmethod
    def validate_talent_experience_gain(talent_instance: 'TalentInstance', experience: int) -> Tuple[bool, List[str]]:
        """
        Validate talent experience gain.
        
        Args:
            talent_instance: Talent instance to gain experience
            experience: Experience amount to gain
            
        Returns:
            Tuple of (can_gain, error_messages)
        """
        try:
            errors = []
            
            # Check if talent instance exists
            if not talent_instance:
                errors.append("No talent instance provided")
                return False, errors
            
            # Check if talent is learned
            if not talent_instance.is_learned:
                errors.append("Talent is not learned")
                return False, errors
            
            # Check if experience is valid
            if not isinstance(experience, int) or experience < 0:
                errors.append("Invalid experience amount")
                return False, errors
            
            # Check if experience would cause overflow
            if talent_instance.experience + experience > 999999:
                errors.append("Experience would exceed maximum")
                return False, errors
            
            return True, errors
            
        except Exception as e:
            logger.error(f"Talent experience validation failed: {e}")
            return False, [f"Validation error: {e}"]
    
    @staticmethod
    def get_talent_validation_summary(monster: MonsterInstance) -> Dict[str, Any]:
        """
        Get talent validation summary for monster.
        
        Args:
            monster: Monster to validate
            
        Returns:
            Validation summary dictionary
        """
        try:
            summary = {
                'total_talents': 0,
                'learned_talents': 0,
                'max_tier': 0,
                'total_experience': 0,
                'validation_errors': []
            }
            
            if not monster or not hasattr(monster, 'talents'):
                summary['validation_errors'].append("Monster has no talents")
                return summary
            
            for talent_instance in monster.talents:
                summary['total_talents'] += 1
                
                if talent_instance.is_learned:
                    summary['learned_talents'] += 1
                    summary['max_tier'] = max(summary['max_tier'], talent_instance.current_tier)
                    summary['total_experience'] += talent_instance.experience
                
                # Validate individual talent
                is_valid, errors = BattleValidationTalents.validate_talent_instance(talent_instance)
                if not is_valid:
                    summary['validation_errors'].extend(errors)
            
            return summary
            
        except Exception as e:
            logger.error(f"Talent validation summary failed: {e}")
            return {
                'total_talents': 0,
                'learned_talents': 0,
                'max_tier': 0,
                'total_experience': 0,
                'validation_errors': [f"Validation error: {e}"]
            }