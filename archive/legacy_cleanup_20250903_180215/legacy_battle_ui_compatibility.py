"""
LEGACY BACKUP: Deprecated compatibility methods from battle_ui.py
This file contains the deprecated compatibility methods that were removed.
"""

import pygame
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class LegacyBattleUICompatibility:
    """
    DEPRECATED: Legacy compatibility methods from PixelBattleUI.
    These methods were removed as they are no longer needed.
    """
    
    def init_battle(self, player_monsters: List, enemy_monsters: List):
        """Initialize UI for a new battle (compatibility method)."""
        logger.warning("init_battle() is deprecated - use new battle system instead")
        # Legacy implementation would initialize sprites and teams
        pass
    
    def set_menu_state(self, state):
        """Change the current menu state (compatibility method)."""
        logger.warning("set_menu_state() is deprecated - use new battle system instead")
        # Legacy implementation would change menu state
        pass
    
    def trigger_flash_effect(self, duration: float = 0.5):
        """Trigger flash effect (compatibility method)."""
        logger.warning("trigger_flash_effect() is deprecated - use new battle system instead")
        # Legacy implementation would trigger flash
        pass
    
    def show_taming_result(self, success: bool, monster_name: str = ""):
        """Show taming result animation (compatibility)."""
        logger.warning("show_taming_result() is deprecated - use new battle system instead")
        # Legacy implementation would show taming result
        pass
    
    def init_demo_inventory(self):
        """Initialize inventory with demo items for testing."""
        logger.warning("init_demo_inventory() is deprecated - use new battle system instead")
        # Legacy implementation would initialize demo inventory
        pass

# Legacy sprite system
class LegacySpriteSystem:
    """DEPRECATED: Legacy sprite system for compatibility."""
    
    def __init__(self):
        self.sprites: Dict[str, Any] = {}
        self.hp_animations: Dict[str, Dict] = {}
        logger.warning("LegacySpriteSystem is deprecated - use new battle system instead")

# Legacy UI components that were removed
class BattleActionFactory:
    """DEPRECATED: This class was removed and replaced with UnifiedAction."""
    pass

def get_standardized_action():
    """DEPRECATED: This function was removed and replaced with get_action_result()."""
    pass
