"""
ARCHIVED: BattleResult Definition from battle_scene.py
Date: 2024-12-28
Reason: Duplicate definition, consolidated in battle_enums.py

Original code:

class BattleResult(Enum):
    '''Possible battle outcomes.'''
    ONGOING = auto()
    VICTORY = auto()
    DEFEAT = auto()
    FLED = auto()
    CAUGHT = auto()

This has been replaced with the unified definition in:
engine/systems/battle/battle_enums.py
"""