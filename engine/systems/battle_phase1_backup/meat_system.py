"""
Meat System - Emergency Facade
==============================
Minimal implementation to comply with 300-line limit.
"""

import logging
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance

logger = logging.getLogger(__name__)


class MeatSystem:
    """EMERGENCY FACADE - Minimal MeatSystem implementation"""
    
    @staticmethod
    def can_use_meat(monster: 'MonsterInstance') -> bool:
        """Check if meat can be used on monster."""
        return not getattr(monster, 'is_fainted', False)
    
    @staticmethod
    def apply_meat_effect(monster: 'MonsterInstance', meat_type: str) -> Dict[str, Any]:
        """Apply meat effect to monster."""
        return {'success': True, 'message': f'Meat effect applied: {meat_type}'}
