"""
Battle Scene Core - Essential battle scene logic
Max 250 lines - contains only core initialization and coordination
"""

import pygame
import logging
from typing import Optional, List, Dict, Any

from engine.core.scene_base import Scene
from engine.core.config import Colors, GameState
from engine.ui.battle import BattleUI, BattleMenuState
from engine.systems.battle.battle_state import BattleState
from engine.systems.battle.battle_controller import BattleController
from engine.systems.battle.turn_processor import TurnProcessor
from engine.systems.battle.action_processor import ActionProcessor
from engine.systems.battle.event_processor import EventProcessor, EventType
from engine.systems.battle.status_processor import StatusProcessor
from engine.systems.battle.battle_enums import BattlePhase, BattleType, BattleResult
from engine.systems.battle.battle_ai import BattleAI
from engine.systems.battle.reward_system import RewardSystem, BattleRewards
from engine.systems.battle.turn_logic import BattleAction, ActionType
from engine.systems.monster_instance import MonsterInstance
from engine.scenes.battle.battle_scene_debug import debug_battle_info, debug_battle_error, debug_battle_debug

logger = logging.getLogger(__name__)


class BattleSceneCore:
    """Core battle scene - essential initialization and coordination only."""
    
    def __init__(self, game):
        """Initialize battle scene with essential components only."""
        self.game = game
        
        # Core battle components
        self.battle_state: Optional[BattleState] = None
        self.battle_controller: Optional[BattleController] = None
        self.battle_ui: Optional[BattleUI] = None
        
        # Battle systems
        self.turn_processor: Optional[TurnProcessor] = None
        self.action_processor: Optional[ActionProcessor] = None
        self.event_processor: Optional[EventProcessor] = None
        self.status_processor: Optional[StatusProcessor] = None
        self.battle_ai: Optional[BattleAI] = None
        self.reward_system: Optional[RewardSystem] = None
        
        # Battle data
        self.player_team: List[MonsterInstance] = []
        self.enemy_team: List[MonsterInstance] = []
        self.battle_type: BattleType = BattleType.WILD
        
        # UI state
        self.current_ui_state = BattleMenuState.MAIN
        self.waiting_for_input = True
        self._pending_action = None
        
        # Debug state
        self._last_logged_phase = None
        
        logger.info("BattleSceneCore initialized")
    
    def on_enter(self, **kwargs):
        """Initialize battle when entering scene."""
        try:
            # Extract battle data from kwargs
            self.player_team = kwargs.get('player_team', [])
            self.enemy_team = kwargs.get('enemy_team', [])
            self.battle_type = kwargs.get('battle_type', BattleType.WILD)
            
            # Create default enemy if none provided
            if not self.enemy_team:
                self._create_default_enemy()
            
            # Initialize battle systems
            self._initialize_battle_systems()
            
            # Initialize battle
            self.initialize_battle()
            
            # Start battle intro sequence
            if self.battle_ui:
                self.battle_ui.start_battle_intro(self.player_team, self.enemy_team)
            
            logger.info(f"Battle scene entered: {len(self.player_team)} vs {len(self.enemy_team)}")
            
        except Exception as e:
            debug_battle_error(f"Failed to enter battle scene: {e}", exc_info=True)
            self.game.change_scene(GameState.MAIN_MENU)
    
    def _create_default_enemy(self):
        """Create default enemy monster for testing."""
        try:
            from engine.systems.monster_species import MonsterSpecies
            from engine.systems.monster_instance import MonsterInstance
            from engine.systems.talent_system import get_talent_database
            
            # Create basic enemy monster
            enemy_species = MonsterSpecies(
                id=1,
                name="Testgeist",
                types=["Normal"],
                base_stats={"hp": 40, "atk": 30, "def": 30, "mag": 20, "res": 20, "spd": 25},
                rank="F"
            )
            
            enemy_monster = MonsterInstance(
                species=enemy_species,
                level=5,
                current_hp=40,
                max_hp=40
            )
            
            self.enemy_team = [enemy_monster]
            debug_battle_info(f"Default enemy created: {enemy_monster.name}")
            
        except Exception as e:
            debug_battle_error(f"Failed to create default enemy: {e}")
            self.enemy_team = []
    
    def _initialize_battle_systems(self):
        """Initialize all battle systems."""
        try:
            # Create battle state
            self.battle_state = BattleState(
                player_team=self.player_team,
                enemy_team=self.enemy_team,
                battle_type=self.battle_type
            )
            
            # Create battle controller
            self.battle_controller = BattleController(
                player_team=self.player_team,
                enemy_team=self.enemy_team,
                battle_type=self.battle_type
            )
            
            # Create specialized processors
            self.turn_processor = TurnProcessor(self.battle_state)
            self.action_processor = ActionProcessor(self.battle_state)
            self.event_processor = EventProcessor(self.battle_state)
            self.status_processor = StatusProcessor(self.battle_state)
            self.battle_ai = BattleAI()
            self.reward_system = RewardSystem()
            
            # Connect processors
            self.battle_controller.set_managers(
                self.turn_processor,
                self.action_processor,
                self.event_processor,
                self.status_processor
            )
            
            # Create battle UI
            self.battle_ui = BattleUI(self.game)
            self.battle_controller.sync_state_with_ui(self.battle_ui)
            
            # Connect event processor to UI
            if hasattr(self.battle_ui, 'event_processor'):
                self.battle_ui.event_processor = self.event_processor
            
            debug_battle_info("All battle systems initialized successfully")
            
        except Exception as e:
            debug_battle_error(f"Failed to initialize battle systems: {e}", exc_info=True)
            raise
    
    def initialize_battle(self, player_team=None, enemy_team=None):
        """Initialize battle with teams."""
        try:
            if player_team:
                self.player_team = player_team
            if enemy_team:
                self.enemy_team = enemy_team
            
            # Initialize battle through controller
            result = self.battle_controller.initialize(self.player_team, self.enemy_team)
            
            if result.get('success'):
                debug_battle_info(f"Battle initialized: {result.get('player_active')} vs {result.get('enemy_active')}")
                return True
            else:
                debug_battle_error(f"Battle initialization failed: {result.get('error')}")
                return False
                
        except Exception as e:
            debug_battle_error(f"Battle initialization error: {e}", exc_info=True)
            return False
    
    def is_battle_over(self) -> bool:
        """Check if battle is over."""
        return self.battle_state and self.battle_state.battle_ended
    
    def get_battle_result(self) -> Optional[BattleResult]:
        """Get battle result."""
        return self.battle_state.battle_result if self.battle_state else None
    
    def get_current_phase(self) -> BattlePhase:
        """Get current battle phase."""
        return self.battle_state.phase if self.battle_state else BattlePhase.INIT
    
    def get_ui_state(self) -> BattleMenuState:
        """Get current UI state."""
        return self.current_ui_state
    
    def is_waiting_for_input(self) -> bool:
        """Check if UI is waiting for input."""
        return self.waiting_for_input
    
    def set_waiting_for_input(self, waiting: bool):
        """Set UI waiting state."""
        self.waiting_for_input = waiting
        if self.battle_ui:
            self.battle_ui.waiting_for_input = waiting
    
    def get_pending_action(self):
        """Get pending action."""
        return self._pending_action
    
    def set_pending_action(self, action):
        """Set pending action."""
        self._pending_action = action
    
    def clear_pending_action(self):
        """Clear pending action."""
        self._pending_action = None
    
    def get_battle_ui(self) -> Optional[BattleUI]:
        """Get battle UI instance."""
        return self.battle_ui
    
    def get_battle_controller(self) -> Optional[BattleController]:
        """Get battle controller instance."""
        return self.battle_controller
    
    def get_battle_state(self) -> Optional[BattleState]:
        """Get battle state instance."""
        return self.battle_state
