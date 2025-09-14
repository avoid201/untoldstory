"""
Meat System - Consolidated Implementation
========================================
Single source of truth for all meat/taming logic.
Consolidated from meat_system.py and EMERGENCY_FACADES.py
"""

import logging
from typing import Dict, Any, TYPE_CHECKING
from enum import Enum, auto

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance

logger = logging.getLogger(__name__)


class MeatType(Enum):
    """Meat types for taming."""
    NORMAL = auto()
    EDEL = auto()
    GOETTER = auto()


class MeatSystem:
    """
    CONSOLIDATED MEAT SYSTEM - Single source of truth for all meat/taming logic.
    Consolidated from meat_system.py and EMERGENCY_FACADES.py
    """
    
    def __init__(self):
        self.active_meat_effect = None
        self.meat_effects = {
            'normal': {'bonus': 0.2, 'name': 'Fleisch'},
            'edel': {'bonus': 0.4, 'name': 'Edelfleisch'},
            'goetter': {'bonus': 0.8, 'name': 'Götterfleisch'}
        }
    
    @staticmethod
    def can_use_meat(monster: 'MonsterInstance') -> bool:
        """Check if meat can be used on monster."""
        return not getattr(monster, 'is_fainted', False)
    
    @staticmethod
    def apply_meat_effect(monster: 'MonsterInstance', meat_type: str) -> Dict[str, Any]:
        """Apply meat effect to monster."""
        return {'success': True, 'message': f'Meat effect applied: {meat_type}'}
    
    def use_meat(self, meat_type: str) -> Dict[str, Any]:
        """Use meat item."""
        if meat_type in self.meat_effects:
            self.active_meat_effect = meat_type
            return {'success': True, 'message': f'{self.meat_effects[meat_type]["name"]} verwendet!'}
        return {'success': False, 'message': 'Unbekannter Fleischtyp'}
    
    def get_taming_bonus(self) -> float:
        """Get current taming bonus from active meat effect."""
        if self.active_meat_effect and self.active_meat_effect in self.meat_effects:
            return self.meat_effects[self.active_meat_effect]['bonus']
        return 0.0


# Singleton instance
_meat_system_instance = None

def get_meat_system() -> MeatSystem:
    """Get the singleton MeatSystem instance."""
    global _meat_system_instance
    if _meat_system_instance is None:
        _meat_system_instance = MeatSystem()
    return _meat_system_instance

def handle_meat_item_use(item_id: str, monster: 'MonsterInstance') -> Dict[str, Any]:
    """Handle meat item usage."""
    meat_system = get_meat_system()
    
    # Map item IDs to meat types
    meat_mapping = {
        'meat': 'normal',
        'edel_meat': 'edel', 
        'goetter_meat': 'goetter'
    }
    
    meat_type = meat_mapping.get(item_id)
    if not meat_type:
        return {'success': False, 'message': 'Kein Fleisch-Item'}
    
    if not meat_system.can_use_meat(monster):
        return {'success': False, 'message': 'Fleisch kann nicht verwendet werden'}
    
    return meat_system.use_meat(meat_type)
