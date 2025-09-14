"""
Core battle coordination logic - max 250 lines
Contains essential initialization and coordination methods.
"""

import logging
from typing import List, Optional, Dict, Any, Callable, TYPE_CHECKING

from engine.systems.monster_instance import MonsterInstance
from engine.systems.battle.battle_enums import BattleType, BattlePhase, BattleResult
from engine.systems.battle.battle_state import BattleState
from engine.systems.battle.turn_logic import TurnOrder
from engine.systems.talent_system import get_talent_database

if TYPE_CHECKING:
    from engine.systems.battle.turn_processor import TurnProcessor
    from engine.systems.battle.action_processor import ActionProcessor
    from engine.systems.battle.event_processor import EventProcessor
    from engine.systems.battle.status_processor import StatusProcessor

logger = logging.getLogger(__name__)


class BattleControllerCore:
    """
    Core battle coordination - only essential methods.
    Handles initialization, manager setup, and basic coordination.
    """
    
    def __init__(self, 
                 player_team: List[MonsterInstance],
                 enemy_team: List[MonsterInstance],
                 battle_type: BattleType = BattleType.WILD,
                 can_flee: bool = True,
                 can_catch: bool = True):
        """Initialize battle controller with battle state and turn order system."""
        
        # Create battle state
        self.state = BattleState(
            player_team=player_team,
            enemy_team=enemy_team,
            battle_type=battle_type,
            can_flee=can_flee,
            can_catch=can_catch
        )
        
        # Initialize turn order system
        self.turn_order = TurnOrder()
        
        # Initialize specialized managers (will be injected by other agents)
        self.turn_processor: Optional['TurnProcessor'] = None
        self.action_processor: Optional['ActionProcessor'] = None
        self.event_processor: Optional['EventProcessor'] = None
        self.status_processor: Optional['StatusProcessor'] = None
        self.ui_sync_callback: Optional[Callable] = None
        
        # Talent System Integration
        self.talent_database = get_talent_database()
        
        # FIXED: Auto-create managers if not injected
        self._auto_initialize_managers()
        
        logger.info(f"BattleController initialized for {battle_type.value} battle")
    
    def set_managers(self, 
                    turn_processor: 'TurnProcessor',
                    action_processor: 'ActionProcessor',
                    event_processor: 'EventProcessor',
                    status_processor: 'StatusProcessor'):
        """Inject specialized managers (called by battle scene setup)."""
        self.turn_processor = turn_processor
        self.action_processor = action_processor
        self.event_processor = event_processor
        self.status_processor = status_processor
        
        # Connect processors
        if self.turn_processor and self.action_processor:
            self.turn_processor.set_action_processor(self.action_processor)
        
        logger.info("Specialized managers injected into BattleController")
    
    def _auto_initialize_managers(self) -> None:
        """Auto-create AND properly connect managers."""
        try:
            # Import all managers
            from engine.systems.battle.event_processor import EventProcessor
            from engine.systems.battle.action_processor import ActionProcessor
            from engine.systems.battle.turn_processor import TurnProcessor
            from engine.systems.battle.status_processor import StatusProcessor
            
            # 1. Create EventProcessor FIRST (most important)
            if not self.event_processor:
                self.event_processor = EventProcessor(self.state)
                logger.info("✓ EventProcessor created")
            
            # 2. Create others
            if not self.action_processor:
                self.action_processor = ActionProcessor(self.state)
                logger.info("✓ ActionProcessor created")
            
            if not self.turn_processor:
                self.turn_processor = TurnProcessor(self.state)
                logger.info("✓ TurnProcessor created")
            
            if not self.status_processor:
                self.status_processor = StatusProcessor(self.state)
                logger.info("✓ StatusProcessor created")
            
            # 3. CRITICAL CONNECTIONS
            if self.turn_processor and self.action_processor:
                self.turn_processor.set_action_processor(self.action_processor)
                logger.info("✓ TurnProcessor ← ActionProcessor connected")
            
            # 4. CRITICAL: Connect EventProcessor to battle state
            if self.event_processor:
                self.state.event_processor = self.event_processor
                # Also connect to battle controller for easy access
                self.event_processor.battle_controller = self
                logger.info("✓ EventProcessor connected to BattleState and BattleController")
            
            # 5. Verify all set
            if not all([self.event_processor, self.action_processor, 
                       self.turn_processor, self.status_processor]):
                raise RuntimeError("Failed to initialize all managers!")
                
            logger.info("✓✓✓ All managers initialized and connected!")
            
        except Exception as e:
            logger.error(f"❌ CRITICAL: Manager initialization failed: {e}")
            raise
    
    def initialize(self, player_team: List[MonsterInstance], enemy_team: List[MonsterInstance]) -> Dict[str, Any]:
        """
        Initialize battle with teams.
        
        Args:
            player_team: List of player monsters
            enemy_team: List of enemy monsters
            
        Returns:
            Dict with initialization result
        """
        try:
            # Update state with teams
            self.state.player_team = player_team
            self.state.enemy_team = enemy_team
            
            # Set active monsters
            if player_team:
                self.state.player_active = player_team[0]
            if enemy_team:
                self.state.enemy_active = enemy_team[0]
            
            # Initialize turn order
            self.turn_order.clear()
            
            # Set initial phase
            self.state.phase = BattlePhase.START
            self.state.turn_count = 0
            self.state.battle_ended = False
            self.state.battle_result = None
            self.state.waiting_for_input = False
            
            logger.info(f"Battle initialized: {len(player_team)} vs {len(enemy_team)}")
            
            return {
                "success": True,
                "player_active": self.state.player_active.name if self.state.player_active else None,
                "enemy_active": self.state.enemy_active.name if self.state.enemy_active else None,
                "phase": self.state.phase.value
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Battle-Initialisierung: {e}")
            return {"success": False, "error": str(e)}
    
    def get_player_monster(self) -> Optional[MonsterInstance]:
        """Get current active player monster."""
        return self.state.player_active
    
    def get_enemy_monster(self) -> Optional[MonsterInstance]:
        """Get current active enemy monster."""
        return self.state.enemy_active
    
    def is_battle_over(self) -> bool:
        """Check if battle is over - pure data access."""
        return self.state.battle_ended
    
    def get_battle_result(self) -> Optional[BattleResult]:
        """Get battle result - pure data access."""
        return self.state.battle_result
    
    def get_available_actions(self) -> List[str]:
        """
        Get available actions for current phase - pure data access.
        Returns available actions based on current state.
        """
        if self.state.phase != BattlePhase.INPUT:
            return []
        
        actions = ["attack", "switch", "item"]
        
        if self.state.can_flee:
            actions.append("flee")
        
        return actions
    
    def sync_state_with_ui(self, ui_component) -> None:
        """Synchronize state with UI component."""
        if ui_component and self.state:
            ui_component.battle_state = self.state
            ui_component.battle_controller = self
            if self.event_processor:
                ui_component.event_processor = self.event_processor
            logger.info("✓ State and Controller synchronized with UI")
    
    # AGENT 3: Removed old phase transition methods - now using transition_phase() from BattleControllerPhasesMixin
