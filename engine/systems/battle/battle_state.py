"""
Battle State - Pure Data Container
Contains only battle data without any business logic or methods.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import logging
from engine.systems.battle.battle_enums import BattlePhase, BattleType, BattleResult

logger = logging.getLogger(__name__)

# Forward declarations to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.battle.event_processor import EventProcessor


@dataclass
class BattleState:
    """Pure battle data container - no business logic, only data."""
    
    # Team data
    player_team: List['MonsterInstance']
    enemy_team: List['MonsterInstance']
    
    # Active monsters
    player_active: Optional['MonsterInstance'] = None
    enemy_active: Optional['MonsterInstance'] = None
    
    # Battle state
    phase: BattlePhase = BattlePhase.INIT
    turn_count: int = 0
    battle_type: BattleType = BattleType.WILD
    
    # Battle options
    can_flee: bool = True
    can_catch: bool = False
    
    # Battle log and results
    battle_log: List[str] = field(default_factory=list)
    exp_earned: int = 0
    money_earned: int = 0
    items_earned: List[str] = field(default_factory=list)
    
    # Additional battle state data
    weather: Optional[str] = None
    terrain: Optional[str] = None
    field_effects: List[str] = field(default_factory=list)
    
    # Turn order and action queue
    turn_order: List['MonsterInstance'] = field(default_factory=list)
    action_queue: List[Dict[str, Any]] = field(default_factory=list)
    
    # Battle flags
    battle_ended: bool = False
    battle_result: Optional[BattleResult] = None
    
    # Player input state
    waiting_for_input: bool = False
    input_type: Optional[str] = None  # 'move', 'switch', 'item', etc.
    
    # Animation and UI state
    current_animation: Optional[str] = None
    message_queue: List[str] = field(default_factory=list)
    
    # CRITICAL FIX: Add missing properties for taming and fleeing
    caught_monster: Optional['MonsterInstance'] = None
    fled: bool = False
    monster_caught: bool = False
    
    # CRITICAL FIX: Event processor connection
    event_processor: Optional['EventProcessor'] = None
    battle_ui: Optional[Any] = None
    
    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.player_active is None and self.player_team:
            self.player_active = self.player_team[0]
        if self.enemy_active is None and self.enemy_team:
            self.enemy_active = self.enemy_team[0]
        
        # CRITICAL: Initialize event processor if not set
        if self.event_processor is None:
            try:
                self.event_processor = EventProcessor(self)
                logger.info("✓ EventProcessor auto-created in BattleState")
            except Exception as e:
                logger.warning(f"Could not auto-create EventProcessor: {e}")
                # Create a minimal fallback
                self.event_processor = None
    
    def get_event_processor(self) -> Optional['EventProcessor']:
        """Get event processor with fallback creation."""
        if self.event_processor is None:
            try:
                # Lazy import to avoid circular imports
                import importlib
                event_module = importlib.import_module('engine.systems.battle.event_processor')
                EventProcessor = getattr(event_module, 'EventProcessor')
                self.event_processor = EventProcessor(self)
                logger.info("✓ EventProcessor created on demand")
            except Exception as e:
                logger.error(f"Failed to create EventProcessor: {e}")
                # Return None if creation fails
                return None
        return self.event_processor
    
    
    # DQM Meat Effects - persistent for entire battle
    active_meat_effect: Optional[str] = None  # 'fleisch', 'edelfleisch', etc.
    meat_bonus: float = 0.0  # 0.0 to 0.8 (0% to 80%)
    
    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.player_active is None and self.player_team:
            self.player_active = self.player_team[0]
        if self.enemy_active is None and self.enemy_team:
            self.enemy_active = self.enemy_team[0]
    
    @property
    def is_player_turn(self) -> bool:
        """Check if it's player's turn."""
        return self.phase == BattlePhase.INPUT
    
    @property
    def is_battle_over(self) -> bool:
        """Check if battle has ended."""
        return self.battle_ended
    
    @property
    def player_active_monster(self):
        """Active player monster with fallback."""
        if self.player_active:
            return self.player_active
        return self.player_team[0] if self.player_team else None
    
    @property
    def has_caught_monster(self) -> bool:
        """Check if monster was caught."""
        return self.caught_monster is not None or self.monster_caught
    
    @property
    def player_can_continue(self) -> bool:
        """Check if player has conscious monsters."""
        return any(m.current_hp > 0 for m in self.player_team)
    
    @property
    def enemy_defeated(self) -> bool:
        """Check if all enemies defeated."""
        return all(m.current_hp <= 0 for m in self.enemy_team)
    
    def reset(self):
        """Reset battle state for new battle."""
        self.phase = BattlePhase.INIT
        self.turn_count = 0
        self.battle_ended = False
        self.battle_result = None
        self.battle_log.clear()
        self.message_queue.clear()
        
        # Reset meat system if available
        if hasattr(self, 'meat_system') and self.meat_system:
            self.meat_system.reset_battle_effect()