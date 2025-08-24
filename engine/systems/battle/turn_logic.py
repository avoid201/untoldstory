"""
Turn order and priority system for battles.
Handles initiative, speed calculations, and action resolution order.
"""

from typing import List, Tuple, Optional, TYPE_CHECKING, Union
from dataclasses import dataclass
from enum import Enum, auto
import random
import logging

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.moves import Move

# Logger für bessere Fehlerverfolgung
logger = logging.getLogger(__name__)

class ActionType(Enum):
    """Types of actions that can be taken in battle."""
    FLEE = auto()      # Priority 6
    SWITCH = auto()    # Priority 5
    ITEM = auto()      # Priority 4
    ATTACK = auto()    # Priority varies by move
    TAME = auto()      # Priority 3
    PASS = auto()      # Priority 0
    AUTO = auto()      # Priority 0
    
    @classmethod
    def from_string(cls, value: str) -> 'ActionType':
        """Konvertiere String zu ActionType mit Fallback."""
        try:
            return cls[value.upper()]
        except KeyError:
            # Fallback für verschiedene Schreibweisen
            action_type_map = {
                'attack': cls.ATTACK,
                'switch': cls.SWITCH,
                'item': cls.ITEM,
                'flee': cls.FLEE,
                'tame': cls.TAME,
                'pass': cls.PASS,
                'auto': cls.AUTO
            }
            return action_type_map.get(value.lower(), cls.PASS)


@dataclass
class BattleAction:
    """Represents a single action in battle."""
    actor: 'MonsterInstance'
    action_type: ActionType
    target: Optional['MonsterInstance'] = None
    move: Optional['Move'] = None
    item_id: Optional[str] = None
    switch_to: Optional['MonsterInstance'] = None
    
    def __post_init__(self):
        """Validiere die Action nach der Initialisierung."""
        if not self.actor:
            raise ValueError("Actor muss angegeben werden")
        if not isinstance(self.action_type, ActionType):
            raise ValueError("action_type muss ein ActionType Enum sein")
    
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
            elif self.action_type == ActionType.TAME:
                return 3
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
                
            # Hole Basis-Speed
            if hasattr(self.actor, 'stats') and isinstance(self.actor.stats, dict):
                base_speed = self.actor.stats.get('spd', 0)
            elif hasattr(self.actor, 'stats') and hasattr(self.actor.stats, 'spd'):
                base_speed = self.actor.stats.spd
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
    
    def to_dict(self) -> dict:
        """Konvertiere Action zu Dict für Serialisierung."""
        try:
            return {
                'actor_id': getattr(self.actor, 'id', None),
                'actor_name': getattr(self.actor, 'name', 'Unknown'),
                'action_type': self.action_type.name,
                'target_id': getattr(self.target, 'id', None) if self.target else None,
                'move_id': getattr(self.move, 'id', None) if self.move else None,
                'item_id': self.item_id,
                'switch_to_id': getattr(self.switch_to, 'id', None) if self.switch_to else None,
                'priority': self.priority,
                'speed': self.speed
            }
        except Exception as e:
            logger.error(f"Fehler bei Action-zu-Dict-Konvertierung: {e}")
            return {'error': str(e)}


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
    
    def sort_actions(self) -> List[BattleAction]:
        """
        Sort actions by priority and speed.
        
        Returns:
            Sorted list of actions
        """
        try:
            # Validiere alle Actions vor dem Sortieren
            valid_actions = [action for action in self.actions if action and action.is_valid()]
            
            # Sortiere nach Priority (höher = zuerst) und dann nach Speed (höher = zuerst)
            sorted_actions = sorted(
                valid_actions,
                key=lambda a: (a.priority, a.speed),
                reverse=True
            )
            
            return sorted_actions
            
        except Exception as e:
            logger.error(f"Fehler beim Sortieren der Actions: {e}")
            # Fallback: einfache Sortierung nach Priority
            try:
                return sorted(
                    [a for a in self.actions if a],
                    key=lambda a: getattr(a, 'priority', 0),
                    reverse=True
                )
            except Exception as e2:
                logger.error(f"Fallback-Sortierung fehlgeschlagen: {e2}")
                return self.actions.copy()  # Rückgabe der ursprünglichen Liste
    
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
    
    def get_turn_summary(self) -> dict:
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


def create_action_from_dict(action_data: dict, 
                           actor: 'MonsterInstance',
                           target: Optional['MonsterInstance'] = None,
                           move: Optional['Move'] = None,
                           switch_to: Optional['MonsterInstance'] = None) -> Optional[BattleAction]:
    """
    Erstelle eine BattleAction aus einem Dictionary.
    
    Args:
        action_data: Dictionary mit Action-Daten
        actor: Das ausführende Monster
        target: Ziel-Monster (optional)
        move: Zu verwendender Move (optional)
        switch_to: Wechsel-Monster (optional)
    
    Returns:
        BattleAction oder None bei Fehlern
    """
    try:
        if not action_data or 'action_type' not in action_data:
            return None
        
        # Konvertiere action_type
        action_type_str = action_data['action_type']
        if isinstance(action_type_str, str):
            action_type = ActionType.from_string(action_type_str)
        else:
            action_type = action_type_str
        
        return BattleAction(
            actor=actor,
            action_type=action_type,
            target=target,
            move=move,
            item_id=action_data.get('item_id'),
            switch_to=switch_to
        )
        
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Action aus Dict: {e}")
        return None


def validate_action_sequence(actions: List[BattleAction]) -> Tuple[bool, List[str]]:
    """
    Validiere eine Sequenz von Actions.
    
    Args:
        actions: Liste von BattleActions
    
    Returns:
        Tuple aus (is_valid, error_messages)
    """
    errors = []
    
    try:
        for i, action in enumerate(actions):
            if not action:
                errors.append(f"Action {i}: Action ist None")
                continue
            
            if not action.is_valid():
                errors.append(f"Action {i}: Ungültige Action")
                continue
            
            # Prüfe auf doppelte Actor-Actions
            for j, other_action in enumerate(actions[i+1:], i+1):
                if (action.actor and other_action.actor and 
                    action.actor == other_action.actor):
                    errors.append(f"Action {i} und {j}: Doppelter Actor")
        
        return len(errors) == 0, errors
        
    except Exception as e:
        errors.append(f"Fehler bei der Action-Sequenz-Validierung: {e}")
        return False, errors