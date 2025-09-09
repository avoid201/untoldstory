"""
Turn order and priority system for battles.
Handles initiative, speed calculations, and action resolution order.
Simplified version for 1v1 battles only.
"""

import logging
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum, auto
import random

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.moves import Move

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of actions that can be taken in battle."""
    FLEE = auto()      # Priority 6
    SWITCH = auto()    # Priority 5
    ITEM = auto()      # Priority 4
    USE_MEAT = auto()  # Priority 4 (same as item)
    ATTACK = auto()    # Priority varies by move
    TAME = auto()      # Priority 3
    SCOUT = auto()     # Priority 2 (lower priority, costs turn)
    PASS = auto()      # Priority 0
    AUTO = auto()      # Priority 0
    SKILL = auto()     # Priority varies by skill

    
    @classmethod
    def from_string(cls, action_str: str) -> 'ActionType':
        """Convert string to ActionType with comprehensive fallback."""
        try:
            if not action_str:
                return cls.PASS
            
            # Clean the input
            cleaned = str(action_str).strip().lower()
            
            # Direct enum matching (case insensitive)
            try:
                return cls[cleaned.upper()]
            except KeyError:
                pass
            
            # Comprehensive mapping with all variations
            mapping = {
                'attack': cls.ATTACK,
                'move': cls.ATTACK,  # Alias for attack
                'skill': cls.SKILL,
                'item': cls.ITEM,
                'use_item': cls.ITEM,  # Alias
                'switch': cls.SWITCH,
                'change': cls.SWITCH,  # Alias
                'flee': cls.FLEE,
                'run': cls.FLEE,  # Alias
                'tame': cls.TAME,
                'catch': cls.TAME,  # Alias
                'wait': cls.PASS,
                'pass': cls.PASS,  # Alias
                'use_meat': cls.USE_MEAT,
                'meat': cls.USE_MEAT,  # Alias
                'scout': cls.SCOUT,
                'scan': cls.SCOUT,  # Alias
                'auto': cls.AUTO
            }
            
            return mapping.get(cleaned, cls.PASS)
            
        except Exception as e:
            logger.error(f"Error converting string to ActionType: {e}")
            return cls.PASS


@dataclass
class BattleAction:
    """Represents a single action in battle."""
    actor: 'MonsterInstance'
    action_type: ActionType
    target: Optional['MonsterInstance'] = None
    move: Optional['Move'] = None
    item_id: Optional[str] = None
    item: Optional[object] = None  # For actual item objects
    switch_to: Optional['MonsterInstance'] = None
    meat_type: Optional[object] = None  # For meat system
    meat_system: Optional[object] = None  # Reference to meat system
    meat_bonus: int = 0  # Meat bonus percentage (0-100)
    
    # Talent System Integration
    talent_id: Optional[str] = None  # Talent that provides this move
    talent_instance: Optional[object] = None  # TalentInstance object
    talent_level: int = 1  # Level of the talent
    passive_abilities: List[Dict[str, Any]] = None  # Passive abilities from talent
    
    def __post_init__(self):
        """Validiere die Action nach der Initialisierung."""
        if not self.actor:
            raise ValueError("Actor muss angegeben werden")
        if not isinstance(self.action_type, ActionType):
            # Try to convert string to ActionType
            if isinstance(self.action_type, str):
                try:
                    self.action_type = ActionType[self.action_type.upper()]
                except KeyError:
                    raise ValueError(f"Invalid action_type: {self.action_type}")
            else:
                raise ValueError("action_type muss ein ActionType Enum sein")
        
        # Initialize passive_abilities if not provided
        if self.passive_abilities is None:
            self.passive_abilities = []
    
    @property
    def priority(self) -> int:
        """Get the priority of this action."""
        try:
            if self.action_type == ActionType.FLEE:
                return 6
            elif self.action_type == ActionType.SWITCH:
                return 5
            elif self.action_type == ActionType.ITEM:
                return 4
            elif self.action_type == ActionType.USE_MEAT:
                return 4  # Same priority as items
            elif self.action_type == ActionType.TAME:
                return 3
            elif self.action_type == ActionType.SCOUT:
                return 2  # Scout has lower priority
            elif self.action_type == ActionType.ATTACK and self.move:
                return getattr(self.move, 'priority', 0)
            else:  # PASS or invalid
                return 0
        except Exception as e:
            logger.error(f"Fehler bei Priority-Berechnung: {e}")
            return 0
    
    @property
    def speed(self) -> int:
        """Get the effective speed of the actor."""
        try:
            if not self.actor:
                return 0
                
            # Hole Basis-Speed - FIXED: Nutze actor.stats.spd statt actor.stats['spd']
            if hasattr(self.actor, 'stats') and hasattr(self.actor.stats, 'spd'):
                base_speed = self.actor.stats.spd
            elif hasattr(self.actor, 'stats') and isinstance(self.actor.stats, dict):
                base_speed = self.actor.stats.get('spd', 0)
            else:
                base_speed = 0
            
            if not isinstance(base_speed, (int, float)) or base_speed <= 0:
                base_speed = 1  # Fallback
            
            # Apply paralysis speed reduction
            if hasattr(self.actor, 'status'):
                status = self.actor.status
                if isinstance(status, str) and status.lower() == 'paralysis':
                    base_speed = int(base_speed * 0.5)
                elif hasattr(status, 'value') and status.value == 'paralysis':
                    base_speed = int(base_speed * 0.5)
            
            # Apply stat stage multipliers
            if hasattr(self.actor, 'stat_stages'):
                stat_stages = self.actor.stat_stages
                if hasattr(stat_stages, 'get'):
                    stage = stat_stages.get('spd', 0)
                elif hasattr(stat_stages, 'spd'):
                    stage = stat_stages.spd
                else:
                    stage = 0
                
                if isinstance(stage, (int, float)):
                    if stage >= 0:
                        multiplier = (2 + stage) / 2
                    else:
                        multiplier = 2 / (2 - stage)
                    base_speed = int(base_speed * multiplier)
            
            return max(1, int(base_speed))  # Mindestens 1
            
        except Exception as e:
            logger.error(f"Fehler bei Speed-Berechnung: {e}")
            return 1  # Fallback
    
    def is_valid(self) -> bool:
        """Validiere die Action."""
        try:
            if not self.actor:
                return False
            
            if self.action_type == ActionType.ATTACK:
                if not self.move:
                    return False
                if not self.target:
                    return False
            elif self.action_type == ActionType.SWITCH:
                if not self.switch_to:
                    return False
            elif self.action_type == ActionType.ITEM:
                if not self.item_id:
                    return False
            elif self.action_type == ActionType.TAME:
                if not self.target:
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Fehler bei Action-Validierung: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert BattleAction to dict for serialization."""
        try:
            return {
                'type': self.action_type.name,
                'actor_id': self.actor.id if hasattr(self.actor, 'id') else str(id(self.actor)),
                'target_id': self.target.id if self.target and hasattr(self.target, 'id') else None,
                'move_id': self.move.id if self.move and hasattr(self.move, 'id') else None,
                'move_name': self.move.name if self.move else None,
                'item_id': self.item_id,
                'switch_to_id': self.switch_to.id if self.switch_to and hasattr(self.switch_to, 'id') else None,
                'priority': self.priority,
                'speed': self.speed
            }
        except Exception as e:
            logger.error(f"Fehler bei Action-zu-Dict-Konvertierung: {e}")
            return {'error': str(e)}
    
    @classmethod
    def create_talent_action(cls, actor: 'MonsterInstance', talent_instance: object, 
                           move: 'Move', target: Optional['MonsterInstance'] = None) -> 'BattleAction':
        """
        Create a talent-based action.
        
        Args:
            actor: Monster performing the action
            talent_instance: TalentInstance providing the move
            move: Move being used
            target: Target monster (optional)
            
        Returns:
            BattleAction with talent information
        """
        try:
            # Get talent information
            talent_id = getattr(talent_instance, 'talent_id', None)
            talent_level = getattr(talent_instance, 'level', 1)
            
            # Get passive abilities from talent
            passive_abilities = []
            if hasattr(talent_instance, 'get_passive_abilities'):
                passive_abilities = talent_instance.get_passive_abilities()
            
            return cls(
                actor=actor,
                action_type=ActionType.ATTACK,
                target=target,
                move=move,
                talent_id=talent_id,
                talent_instance=talent_instance,
                talent_level=talent_level,
                passive_abilities=passive_abilities
            )
        except Exception as e:
            logger.error(f"Error creating talent action: {e}")
            # Fallback to regular action
            return cls(
                actor=actor,
                action_type=ActionType.ATTACK,
                target=target,
                move=move
            )


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

    def set_seed(self, seed: int) -> None:
        """Setze RNG-Seed für deterministische Tests."""
        self.rng = random.Random(seed)
    
    def clear(self) -> None:
        """Clear all actions for a new turn."""
        try:
            self.actions.clear()
            self.resolved_actions.clear()
        except Exception as e:
            logger.error(f"Fehler beim Löschen der Actions: {e}")
    
    def add_action(self, action: BattleAction) -> bool:
        """Add an action to the current turn."""
        try:
            if not action or not isinstance(action, BattleAction):
                logger.warning("Ungültige Action hinzugefügt")
                return False
            
            if not action.is_valid():
                logger.warning("Ungültige Action kann nicht hinzugefügt werden")
                return False
            
            self.actions.append(action)
            return True
        except Exception as e:
            logger.error(f"Fehler beim Hinzufügen der Action: {e}")
            return False
    
    def sort_actions(self, use_dqm_formula: bool = True) -> List[BattleAction]:
        """
        Sort actions by priority and speed.
        
        Args:
            use_dqm_formula: Whether to use DQM turn order formula
        
        Returns:
            Sorted list of actions
        """
        try:
            # Validiere alle Actions vor dem Sortieren
            valid_actions = [action for action in self.actions if action and action.is_valid()]
            
            if not valid_actions:
                logger.warning("Keine gültigen Actions zum Sortieren gefunden")
                return []
            
            if use_dqm_formula:
                # DQM-Formel: Priorität zuerst, dann Speed + Random(0-255)
                def dqm_sort_key(action: BattleAction):
                    priority = action.priority
                    # DQM-Formel: Speed + Random(0-255)
                    speed_with_random = action.speed + self.rng.randint(0, 255)
                    # Höhere Werte = früher dran
                    return (-priority, -speed_with_random)
                
                sorted_actions = sorted(valid_actions, key=dqm_sort_key)
                logger.debug(f"DQM-Sortierung: {len(sorted_actions)} Actions sortiert")
            else:
                # Einfache Sortierung nach Priority und Speed
                sorted_actions = sorted(
                    valid_actions,
                    key=lambda a: (-a.priority, -a.speed)  # Negative für absteigende Sortierung
                )
                logger.debug(f"Einfache Sortierung: {len(sorted_actions)} Actions sortiert")
            
            return sorted_actions
            
        except Exception as e:
            logger.error(f"Fehler beim Sortieren der Actions: {e}")
            return []
    
    def get_next_action(self) -> Optional[BattleAction]:
        """Get the next action to execute."""
        try:
            if not self.actions:
                return None
            
            # Sortiere Actions falls noch nicht geschehen
            sorted_actions = self.sort_actions()
            
            if sorted_actions:
                return sorted_actions[0]
            return None
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der nächsten Action: {e}")
            return None
    
    def execute_action(self, action: BattleAction) -> bool:
        """Mark an action as executed."""
        try:
            if action in self.actions:
                self.actions.remove(action)
                self.resolved_actions.append(action)
                return True
            return False
        except Exception as e:
            logger.error(f"Fehler beim Ausführen der Action: {e}")
            return False
    
    def get_turn_summary(self) -> Dict[str, Any]:
        """Hole eine Zusammenfassung des aktuellen Turns."""
        try:
            return {
                'total_actions': len(self.actions),
                'resolved_actions': len(self.resolved_actions),
                'next_action': self.get_next_action().to_dict() if self.get_next_action() else None,
                'all_actions': [action.to_dict() for action in self.actions]
            }
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Turn-Zusammenfassung: {e}")
            return {'error': str(e)}
    
    def validate_turn_state(self) -> bool:
        """Validiere den aktuellen Turn-Status."""
        try:
            # Prüfe, dass alle Actions gültig sind
            for action in self.actions:
                if not action or not action.is_valid():
                    return False
            
            # Prüfe, dass keine doppelten Actions existieren
            action_ids = []
            for action in self.actions:
                if hasattr(action, 'actor') and hasattr(action.actor, 'id'):
                    action_ids.append(action.actor.id)
            
            if len(action_ids) != len(set(action_ids)):
                return False
            
            return True
        except Exception as e:
            logger.error(f"Fehler bei Turn-Status-Validierung: {e}")
            return False


def create_action_from_dict(action_dict: Dict[str, Any], 
                           actor: 'MonsterInstance' = None,
                           target: Optional['MonsterInstance'] = None,
                           move: Optional['Move'] = None,
                           switch_to: Optional['MonsterInstance'] = None,
                           **kwargs) -> Optional[BattleAction]:
    """
    SINGLE SOURCE OF TRUTH for Action Conversion.
    Creates BattleAction from dict with comprehensive validation and key normalization.
    
    SUPPORTED ACTION KEYS (normalized to 'type'):
    - 'type' (preferred)
    
    Args:
        action_dict: Dictionary containing action data
        actor: Optional actor override
        target: Optional target override
        move: Optional move override
        switch_to: Optional switch target override
        **kwargs: Additional parameters
        
    Returns:
        BattleAction object or None if creation failed
    """
    try:
        # Validate input
        if not action_dict or not isinstance(action_dict, dict):
            logger.warning("Invalid action_dict provided - must be non-empty dict")
            return None
        
        # NORMALIZE ACTION TYPE - Extract and standardize action type
        # Support ALL variations: 'type', 'action', 'action_type'
        action_type_str = (action_dict.get('type') or 
                          action_dict.get('action') or 
                          action_dict.get('action_type') or 
                          'wait')
        
        # Convert to ActionType enum
        action_type = ActionType.from_string(action_type_str)
        if not action_type:
            logger.warning(f"Invalid action type: {action_type_str}")
            return None
        
        # Use provided parameters or extract from dict
        final_actor = actor or action_dict.get('actor')
        final_target = target or action_dict.get('target')
        final_move = move or action_dict.get('move')
        final_item = action_dict.get('item_id') or action_dict.get('item')
        final_switch = switch_to or action_dict.get('switch_to')
        
        # Validate required actor
        if not final_actor:
            logger.warning("Actor is required for BattleAction creation")
            return None
        
        # Get move if attack action and not provided
        if action_type == ActionType.ATTACK and not final_move:
            move_name = (action_dict.get('move_name') or 
                        action_dict.get('move_id'))
            if move_name:
                try:
                    from engine.systems.moves import move_registry
                    if isinstance(move_name, str):
                        final_move = move_registry.create_move_instance_by_name(move_name)
                    else:
                        final_move = move_name  # Already a Move object
                except Exception as e:
                    logger.warning(f"Failed to load move {move_name}: {e}")
                    final_move = None
        
        # Get meat type if use_meat action
        meat_type = None
        if action_type == ActionType.USE_MEAT:
            meat_type_str = action_dict.get('meat_type')
            if meat_type_str:
                try:
                    from engine.systems.battle.meat_system import MeatType
                    meat_type = MeatType.from_string(meat_type_str) if hasattr(MeatType, 'from_string') else MeatType.NONE
                except Exception as e:
                    logger.warning(f"Failed to load meat type {meat_type_str}: {e}")
                    meat_type = None
        
        # Create BattleAction with comprehensive data
        battle_action = BattleAction(
            actor=final_actor,
            action_type=action_type,
            target=final_target,
            move=final_move,
            item_id=final_item,
            item=action_dict.get('item'),
            switch_to=final_switch,
            meat_type=meat_type,
            meat_system=action_dict.get('meat_system'),
            meat_bonus=action_dict.get('meat_bonus', 0)
        )
        
        # Validate the created action
        if not battle_action.is_valid():
            logger.warning(f"Created BattleAction is invalid: {battle_action}")
            return None
        
        logger.debug(f"Successfully created BattleAction: {action_type.name}")
        return battle_action
        
    except Exception as e:
        logger.error(f"Failed to create BattleAction from dict: {e}")
        return None


def validate_action_sequence(actions: List[BattleAction]) -> tuple[bool, List[str]]:
    """
    Validiere eine Sequenz von Actions using consolidated BattleValidator.
    DELEGATED: Use BattleValidator directly for consistency.
    
    Args:
        actions: Liste von BattleActions
    
    Returns:
        Tuple aus (is_valid, error_messages)
    """
    from engine.systems.battle.battle_validation import BattleValidator
    return BattleValidator.validate_action_sequence(actions)
