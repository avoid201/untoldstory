"""
Battle Controller - Facade for split modules
Maintains backward compatibility while delegating to specialized modules.
"""

# ==== AGENT 1 COMPLETED ====
# CHANGES: Split 916 lines into 4 modules (<300 each)
# ==== END AGENT WORK ====

from engine.systems.battle.core.battle_controller_core import BattleControllerCore
from engine.systems.battle.core.battle_controller_state import BattleControllerStateMixin
from engine.systems.battle.core.battle_controller_actions import BattleControllerActionsMixin
from engine.systems.battle.core.battle_controller_phases import BattleControllerPhasesMixin


class BattleController(
    BattleControllerCore,
    BattleControllerStateMixin,
    BattleControllerActionsMixin,
    BattleControllerPhasesMixin
):
    """
    Facade controller maintaining backward compatibility.
    All original methods available through inheritance.
    
    This class combines all specialized modules through multiple inheritance:
    - BattleControllerCore: Essential initialization and coordination
    - BattleControllerStateMixin: State management and monster info
    - BattleControllerActionsMixin: Action execution and validation
    - BattleControllerPhasesMixin: Phase transitions and rewards
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the facade controller."""
        super().__init__(*args, **kwargs)
    
    # All methods are inherited from the mixin classes
    # No additional methods needed - facade pattern