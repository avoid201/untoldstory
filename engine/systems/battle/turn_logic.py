"""
Turn order and priority system for battles.
Handles initiative, speed calculations, and action resolution order.
"""

from typing import List, Tuple, Optional, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum, auto
import random

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.moves import Move


class ActionType(Enum):
    """Types of actions that can be taken in battle."""
    FLEE = auto()      # Priority 6
    SWITCH = auto()    # Priority 5
    ITEM = auto()      # Priority 4
    MOVE = auto()      # Priority varies by move
    TAME = auto()      # Priority 3
    PASS = auto()      # Priority 0


@dataclass
class BattleAction:
    """Represents a single action in battle."""
    actor: 'MonsterInstance'
    action_type: ActionType
    target: Optional['MonsterInstance'] = None
    move: Optional['Move'] = None
    item_id: Optional[str] = None
    switch_to: Optional['MonsterInstance'] = None
    
    @property
    def priority(self) -> int:
        """Get the priority of this action."""
        if self.action_type == ActionType.FLEE:
            return 6
        elif self.action_type == ActionType.SWITCH:
            return 5
        elif self.action_type == ActionType.ITEM:
            return 4
        elif self.action_type == ActionType.TAME:
            return 3
        elif self.action_type == ActionType.MOVE and self.move:
            return self.move.priority
        else:  # PASS or invalid
            return 0
    
    @property
    def speed(self) -> int:
        """Get the effective speed of the actor."""
        if not self.actor:
            return 0
            
        base_speed = self.actor.stats['spd']
        
        # Apply paralysis speed reduction
        if self.actor.status == 'paralysis':
            base_speed = int(base_speed * 0.5)
        
        # Apply stat stage multipliers
        stage = self.actor.stat_stages.get('spd', 0)
        if stage >= 0:
            multiplier = (2 + stage) / 2
        else:
            multiplier = 2 / (2 - stage)
        
        return int(base_speed * multiplier)


class TurnOrder:
    """Manages turn order and action resolution in battle."""
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize turn order system.
        
        Args:
            seed: Random seed for deterministic behavior (for replays/tests)
        """
        self.rng = random.Random(seed)
        self.actions: List[BattleAction] = []
        self.resolved_actions: List[BattleAction] = []
    
    def clear(self) -> None:
        """Clear all actions for a new turn."""
        self.actions.clear()
        self.resolved_actions.clear()
    
    def add_action(self, action: BattleAction) -> None:
        """Add an action to the current turn."""
        self.actions.append(action)
    
    def sort_actions(self) -> List[BattleAction]:
        """
        Sort actions by priority and speed.
        
        Returns:
            Sorted list of actions in execution order
        """
        # Sort by priority (descending), then speed (descending)
        # Use random tiebreaker for same priority and speed
        def sort_key(action: BattleAction) -> Tuple[int, int, float]:
            return (
                -action.priority,  # Higher priority first
                -action.speed,     # Higher speed first
                self.rng.random()  # Random tiebreaker
            )
        
        self.actions.sort(key=sort_key)
        return self.actions.copy()
    
    def get_next_action(self) -> Optional[BattleAction]:
        """
        Get the next action to resolve.
        
        Returns:
            Next action or None if no actions remain
        """
        if not self.actions:
            return None
        
        action = self.actions.pop(0)
        self.resolved_actions.append(action)
        return action
    
    def remove_actions_by_actor(self, actor: 'MonsterInstance') -> None:
        """
        Remove all pending actions by a specific actor.
        Used when a monster faints before acting.
        
        Args:
            actor: The monster whose actions should be removed
        """
        self.actions = [a for a in self.actions if a.actor != actor]
    
    def has_actions(self) -> bool:
        """Check if there are pending actions."""
        return len(self.actions) > 0
    
    def get_action_order_preview(self) -> List[str]:
        """
        Get a preview of action order for UI display.
        
        Returns:
            List of actor names in action order
        """
        sorted_actions = self.sort_actions()
        return [f"{a.actor.nickname or a.actor.species.name} ({a.action_type.name})" 
                for a in sorted_actions]


class SpeedTier:
    """Helper class for speed tier calculations."""
    
    @staticmethod
    def calculate_speed_ratio(attacker_speed: int, defender_speed: int) -> float:
        """
        Calculate speed ratio for effects like accuracy/evasion.
        
        Args:
            attacker_speed: Speed of the attacking monster
            defender_speed: Speed of the defending monster
            
        Returns:
            Speed ratio multiplier
        """
        if defender_speed <= 0:
            return 2.0
        
        ratio = attacker_speed / defender_speed
        # Clamp between 0.5 and 2.0
        return max(0.5, min(2.0, ratio))
    
    @staticmethod
    def calculate_flee_chance(runner_speed: int, opponent_speed: int, attempts: int = 1) -> float:
        """
        Calculate chance to successfully flee from battle.
        
        Args:
            runner_speed: Speed of the fleeing monster
            opponent_speed: Speed of the opponent
            attempts: Number of flee attempts this battle
            
        Returns:
            Probability of successful flee (0.0 to 1.0)
        """
        if runner_speed >= opponent_speed:
            return 1.0  # Always succeed if faster
        
        # Base formula similar to Pokémon
        base_chance = (runner_speed * 128 / opponent_speed + 30 * attempts) / 256
        return min(1.0, base_chance)
    
    @staticmethod
    def calculate_critical_speed_bonus(attacker_speed: int, defender_speed: int) -> int:
        """
        Calculate critical hit stage bonus from speed advantage.
        
        Args:
            attacker_speed: Speed of the attacking monster
            defender_speed: Speed of the defending monster
            
        Returns:
            Additional critical hit stages (0-2)
        """
        ratio = attacker_speed / max(1, defender_speed)
        
        if ratio >= 2.0:
            return 2
        elif ratio >= 1.5:
            return 1
        else:
            return 0


class TrickRoom:
    """Special field effect that reverses speed order."""
    
    def __init__(self, duration: int = 5):
        """
        Initialize Trick Room effect.
        
        Args:
            duration: Number of turns the effect lasts
        """
        self.duration = duration
        self.turns_remaining = duration
        self.active = False
    
    def activate(self) -> None:
        """Activate Trick Room."""
        self.active = True
        self.turns_remaining = self.duration
    
    def deactivate(self) -> None:
        """Deactivate Trick Room."""
        self.active = False
        self.turns_remaining = 0
    
    def tick(self) -> bool:
        """
        Reduce duration by one turn.
        
        Returns:
            True if effect expired this turn
        """
        if not self.active:
            return False
        
        self.turns_remaining -= 1
        if self.turns_remaining <= 0:
            self.deactivate()
            return True
        return False
    
    def modify_speed(self, speed: int, max_speed: int = 999) -> int:
        """
        Modify speed value under Trick Room.
        
        Args:
            speed: Original speed value
            max_speed: Maximum possible speed for inversion
            
        Returns:
            Modified speed (inverted if Trick Room active)
        """
        if self.active:
            return max_speed - speed
        return speed


# Priority brackets for common move effects
PRIORITY_BRACKETS = {
    'protect': 4,      # Protective moves
    'quick': 3,        # Quick Attack style moves  
    'priority': 2,     # Generic priority moves
    'standard': 1,     # Normal moves
    'status': 0,       # Status moves
    'counter': -1,     # Counter/Mirror moves
    'room': -2,        # Room effects
    'slow': -3,        # Deliberately slow moves
}


def determine_move_order(actions: List[BattleAction], 
                        trick_room: Optional[TrickRoom] = None,
                        seed: Optional[int] = None) -> List[BattleAction]:
    """
    Convenience function to determine move order.
    
    Args:
        actions: List of actions to sort
        trick_room: Optional Trick Room effect
        seed: Random seed for tiebreakers
        
    Returns:
        Sorted list of actions
    """
    turn_order = TurnOrder(seed)
    
    # Modify speeds if Trick Room is active
    if trick_room and trick_room.active:
        for action in actions:
            original_speed = action.speed
            # Create a modified action with inverted speed
            # This is a simplified approach - in practice, you'd modify the speed calculation
            pass
    
    for action in actions:
        turn_order.add_action(action)
    
    return turn_order.sort_actions()