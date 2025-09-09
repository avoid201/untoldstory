# ARCHIVED: 2025-09-03 - Replaced by battle_controller.py
"""
Battle System Compatibility Layer
Re-exports all battle system components for backwards compatibility
"""

# Import all enums and constants
from engine.systems.battle.battle_enums import (
    BattleType,
    BattlePhase,
    BattleCommand,
    AIPersonality
)

# Import tension system
# TensionManager removed - system simplified

# Import validation
from engine.systems.battle.battle_validation import BattleValidator

# Import action execution
from engine.systems.battle.battle_actions import BattleActionExecutor

# Import main controller
from engine.systems.battle.battle_controller import BattleState

# Re-export everything for compatibility
__all__ = [
    # Enums
    'BattleType',
    'BattlePhase',
    'BattleCommand',
    'AIPersonality',
    
    # Tension
    # 'TensionState', # Removed - system simplified
    # 'TensionManager', # Removed - system simplified
    
    # Validation
    'BattleValidator',
    
    # Actions
    'BattleActionExecutor',
    
    # Main controller
    'BattleState'
]

# Maintain compatibility with old imports
def get_battle_state(*args, **kwargs):
    """
    Factory function for creating BattleState instances.
    Maintains compatibility with old code.
    """
    return BattleState(*args, **kwargs)


# Additional helper functions for backwards compatibility
def create_battle(player_team, enemy_team, **kwargs):
    """
    Helper function to create a battle.
    
    Args:
        player_team: Player's monster team
        enemy_team: Enemy monster team
        **kwargs: Additional battle parameters
        
    Returns:
        BattleState instance
    """
    return BattleState(player_team, enemy_team, **kwargs)


def validate_battle_state(battle_state):
    """
    Helper function to validate a battle state.
    
    Args:
        battle_state: BattleState instance to validate
        
    Returns:
        True if valid, False otherwise
    """
    if isinstance(battle_state, BattleState):
        return battle_state.validate_battle_state()
    return False
