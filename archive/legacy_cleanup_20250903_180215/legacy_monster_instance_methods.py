"""
LEGACY BACKUP: Deprecated methods from monster_instance.py
This file contains the deprecated methods that were removed.
"""

import logging

logger = logging.getLogger(__name__)

class LegacyMonsterInstanceMethods:
    """
    DEPRECATED: Legacy methods from MonsterInstance class.
    These methods were removed and replaced with new implementations.
    """
    
    def learn_move(self, move_name: str) -> bool:
        """DEPRECATED: Moves werden jetzt über Talents gelernt.
        
        Args:
            move_name: Name des Moves (wird ignoriert)
            
        Returns:
            False (Moves werden über Talents gelernt)
        """
        logger.warning(f"learn_move() ist deprecated. Verwende learn_talent() stattdessen.")
        return False
    
    def apply_status_legacy(self, status: str, duration: int = 0) -> bool:
        """Apply a status condition using legacy system only.
        
        Args:
            status: Status condition to apply
            duration: Duration in turns (0 = permanent until cured)
            
        Returns:
            True if status was applied successfully, False otherwise
        """
        # Legacy status system implementation
        pass
    
    def process_status_effects_legacy(self) -> bool:
        """
        Process status effects at end of turn using legacy system only.
        
        Returns:
            True if monster can act, False if prevented by status
        """
        # Legacy status processing implementation
        pass
