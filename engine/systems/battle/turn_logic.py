"""
Turn order and priority system for battles.
Handles initiative, speed calculations, and action resolution order.
"""

import logging
from typing import List, Tuple, Optional, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum, auto
import random

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.moves import Move

# Import Formation System
from engine.systems.battle.battle_formation import (
    BattleFormation, FormationManager, FormationType, MonsterSlot
)

# Logger für das Turn-Logic-System
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
        """Convert string to ActionType with fallback."""
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
    targets: Optional[List['MonsterInstance']] = None  # Multi-target support
    move: Optional['Move'] = None
    item_id: Optional[str] = None
    switch_to: Optional['MonsterInstance'] = None
    is_multi_target: bool = False  # Multi-target flag
    formation_slot: Optional[MonsterSlot] = None  # Formation slot reference
    
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
                return self.move.priority
            elif self.action_type == ActionType.SKILL and self.move:
                # Skills have similar priority to attacks
                return getattr(self.move, 'priority', 2)
            else:  # PASS or invalid
                return 0
        except Exception as e:
            logger.error(f"Fehler bei der Prioritätsberechnung: {str(e)}")
            return 0
    
    @property
    def speed(self) -> int:
        """Get the effective speed of the actor."""
        try:
            if not self.actor:
                logger.warning("Actor ist None bei Geschwindigkeitsberechnung!")
                return 0
            
            # Überprüfe, ob das Monster gültige Stats hat
            if not hasattr(self.actor, 'stats') or not isinstance(self.actor.stats, dict):
                logger.warning(f"Monster {getattr(self.actor, 'name', 'Unknown')} hat keine gültigen Stats!")
                return 0
            
            if 'spd' not in self.actor.stats:
                logger.warning(f"Geschwindigkeits-Stat fehlt bei Monster {getattr(self.actor, 'name', 'Unknown')}!")
                return 0
            
            base_speed = self.actor.stats['spd']
            if not isinstance(base_speed, (int, float)) or base_speed <= 0:
                logger.warning(f"Ungültige Geschwindigkeit bei Monster {getattr(self.actor, 'name', 'Unknown')}: {base_speed}")
                return 1
            
            # Apply paralysis speed reduction
            if hasattr(self.actor, 'status') and self.actor.status == 'paralysis':
                base_speed = int(base_speed * 0.5)
            
            # Apply stat stage multipliers
            if hasattr(self.actor, 'stat_stages') and self.actor.stat_stages:
                try:
                    stage = self.actor.stat_stages.get('spd', 0)
                    if stage >= 0:
                        multiplier = (2 + stage) / 2
                    else:
                        multiplier = 2 / (2 - stage)
                    
                    base_speed = int(base_speed * multiplier)
                except Exception as e:
                    logger.error(f"Fehler bei der Stat-Stage-Berechnung: {str(e)}")
                    # Verwende Basis-Geschwindigkeit bei Fehlern
                    pass
            
            return max(1, base_speed)  # Mindestens 1
            
        except Exception as e:
            logger.error(f"Fehler bei der Geschwindigkeitsberechnung: {str(e)}")
            return 1  # Fallback-Wert
    
    def get_speed(self) -> int:
        """
        Sichere Methode zum Abrufen der Geschwindigkeit.
        
        Returns:
            Die Geschwindigkeit des Actors (mindestens 1)
        """
        try:
            return self.speed
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Geschwindigkeit: {str(e)}")
            return 1

    @property
    def effective_priority(self) -> int:
        """
        Get the effective priority for turn order calculation.
        Combines base priority with speed for tie-breaking.
        
        Returns:
            Effective priority value
        """
        try:
            base_priority = self.priority
            # Use speed as tie-breaker (higher speed = higher effective priority)
            speed_factor = self.speed / 1000.0  # Normalize speed to small decimal
            return base_priority + speed_factor
        except Exception as e:
            logger.error(f"Fehler bei der effektiven Prioritätsberechnung: {str(e)}")
            return self.priority
    SPECIAL = auto()  # Special commands like psyche up


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


class FormationTurnOrder(TurnOrder):
    """Turn order system for 3v3 formation battles."""
    
    def __init__(self, formation_manager: Optional[FormationManager] = None, seed=None):
        super().__init__(seed)
        self.formation_manager = formation_manager
    
    def get_all_active_actors(self) -> List[Tuple[str, MonsterSlot]]:
        """Get all monsters that can act this turn from formations."""
        if not self.formation_manager:
            return []
        
        active_actors = []
        for team_id, formation in self.formation_manager.formations.items():
            for slot in formation.get_active_monsters():
                if slot.can_act():
                    active_actors.append((team_id, slot))
        
        return active_actors
    
    def calculate_formation_turn_order(self) -> List[Tuple[str, MonsterSlot]]:
        """Calculate turn order for all active monsters in formations."""
        actors = self.get_all_active_actors()
        
        # DQM formula: Speed + Random(0-255)
        def get_speed_value(actor_tuple):
            team_id, slot = actor_tuple
            base_speed = slot.monster.stats.get('spd', 50)
            
            # Apply status effects
            if hasattr(slot.monster, 'status'):
                if slot.monster.status == 'paralysis':
                    base_speed = int(base_speed * 0.5)
            
            # Apply formation bonus
            if self.formation_manager:
                formation = self.formation_manager.formations.get(team_id)
                if formation:
                    bonuses = formation.get_formation_bonus()
                    base_speed = int(base_speed * bonuses.get('spd', 1.0))
            
            return base_speed + self.rng.randint(0, 255)
        
        # Sort by speed value
        actors.sort(key=get_speed_value, reverse=True)
        return actors
    
    def add_formation_action(self, team_id: str, slot: MonsterSlot, action: BattleAction):
        """Add an action from a formation slot."""
        action.formation_slot = slot
        self.add_action(action)
    
    def clear(self) -> None:
        """Clear all actions for a new turn."""
        try:
            self.actions.clear()
            self.resolved_actions.clear()
        except Exception as e:
            logger.error(f"Fehler beim Löschen der Aktionen: {str(e)}")
    
    def add_action(self, action: BattleAction) -> None:
        """Add an action to the current turn."""
        try:
            if not action:
                logger.warning("Versuch, None-Aktion hinzuzufügen!")
                return
            
            if not hasattr(action, 'actor') or not action.actor:
                logger.warning("Aktion ohne gültigen Actor!")
                return
            
            self.actions.append(action)
            
        except Exception as e:
            logger.error(f"Fehler beim Hinzufügen der Aktion: {str(e)}")
    
    def sort_actions(self, use_dqm_formula: bool = True) -> List[BattleAction]:
        """
        Sort actions by priority and speed.
        
        Args:
            use_dqm_formula: Whether to use DQM turn order formula
        
        Returns:
            Sorted list of actions in execution order
        """
        try:
            if use_dqm_formula:
                # Use DQM turn order formula: Agility + Random(0-255)
                def sort_key(action: BattleAction) -> Tuple[int, int, float]:
                    try:
                        # Priority groups still matter (flee > switch > item > attack)
                        priority_group = -action.priority * 1000  # Ensure priority overrides speed
                        
                        # DQM formula: Speed + Random(0-255)
                        speed_value = action.get_speed() + self.rng.randint(0, 255)
                        
                        return (
                            priority_group,  # Priority group first
                            -speed_value,    # Then speed + random (higher goes first)
                            self.rng.random()  # Final tiebreaker
                        )
                    except Exception as e:
                        logger.error(f"Fehler bei der DQM-Sortierung: {str(e)}")
                        return (0, 0, 0.0)
            else:
                # Original sorting method
                def sort_key(action: BattleAction) -> Tuple[int, int, float]:
                    try:
                        return (
                            -action.priority,  # Higher priority first
                            -action.get_speed(),     # Higher speed first
                            self.rng.random()  # Random tiebreaker
                        )
                    except Exception as e:
                        logger.error(f"Fehler bei der Sortierung: {str(e)}")
                        return (0, 0, 0.0)  # Fallback für ungültige Aktionen
            
            # Filtere ungültige Aktionen heraus
            valid_actions = [a for a in self.actions if a and hasattr(a, 'actor') and a.actor]
            
            if not valid_actions:
                logger.warning("Keine gültigen Aktionen zum Sortieren vorhanden!")
                return []
            
            valid_actions.sort(key=sort_key)
            return valid_actions.copy()
            
        except Exception as e:
            logger.error(f"Fehler beim Sortieren der Aktionen: {str(e)}")
            return []
    
    def get_next_action(self) -> Optional[BattleAction]:
        """
        Get the next action to resolve.
        
        Returns:
            Next action or None if no actions remain
        """
        try:
            if not self.actions:
                return None
            
            action = self.actions.pop(0)
            if action:
                self.resolved_actions.append(action)
            return action
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der nächsten Aktion: {str(e)}")
            return None
    
    def remove_actions_by_actor(self, actor: 'MonsterInstance') -> None:
        """
        Remove all pending actions by a specific actor.
        Used when a monster faints before acting.
        
        Args:
            actor: The monster whose actions should be removed
        """
        try:
            if not actor:
                logger.warning("Versuch, Aktionen für None-Actor zu entfernen!")
                return
            
            self.actions = [a for a in self.actions if a and a.actor != actor]
            
        except Exception as e:
            logger.error(f"Fehler beim Entfernen der Aktionen: {str(e)}")
    
    def has_actions(self) -> bool:
        """Check if there are pending actions."""
        try:
            return len(self.actions) > 0
        except Exception as e:
            logger.error(f"Fehler bei der Aktionen-Überprüfung: {str(e)}")
            return False
    
    def get_action_order_preview(self) -> List[str]:
        """
        Get a preview of action order for UI display.
        
        Returns:
            List of actor names in action order
        """
        try:
            sorted_actions = self.sort_actions()
            preview = []
            
            for action in sorted_actions:
                try:
                    if action and action.actor:
                        actor_name = getattr(action.actor, 'nickname', None) or getattr(action.actor, 'species', None)
                        if actor_name:
                            if hasattr(actor_name, 'name'):
                                actor_name = actor_name.name
                            preview.append(f"{actor_name} ({action.action_type.name})")
                        else:
                            preview.append(f"Unbekanntes Monster ({action.action_type.name})")
                    else:
                        preview.append("Ungültige Aktion")
                except Exception as e:
                    logger.error(f"Fehler bei der Aktionen-Vorschau: {str(e)}")
                    preview.append("Fehler bei der Aktion")
            
            return preview
            
        except Exception as e:
            logger.error(f"Fehler bei der Aktionen-Vorschau: {str(e)}")
            return ["Fehler bei der Vorschau"]


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
        try:
            if defender_speed <= 0:
                logger.warning("Verteidiger-Geschwindigkeit ist 0 oder negativ!")
                return 2.0
            
            ratio = attacker_speed / defender_speed
            # Clamp between 0.5 and 2.0
            return max(0.5, min(2.0, ratio))
            
        except Exception as e:
            logger.error(f"Fehler bei der Geschwindigkeitsverhältnis-Berechnung: {str(e)}")
            return 1.0  # Neutraler Multiplikator bei Fehlern
    
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
        try:
            if runner_speed <= 0:
                logger.warning("Läufer-Geschwindigkeit ist 0 oder negativ!")
                return 0.0
            
            if opponent_speed <= 0:
                logger.warning("Gegner-Geschwindigkeit ist 0 oder negativ!")
                return 1.0  # Immer erfolgreich gegen unbewegliche Gegner
            
            if runner_speed >= opponent_speed:
                return 1.0  # Always succeed if faster
            
            # Base formula similar to Pokémon
            base_chance = (runner_speed * 128 / opponent_speed + 30 * attempts) / 256
            return min(1.0, base_chance)
            
        except Exception as e:
            logger.error(f"Fehler bei der Fluchtwahrscheinlichkeits-Berechnung: {str(e)}")
            return 0.5  # Standard-Fluchtwahrscheinlichkeit bei Fehlern
    
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
        try:
            if defender_speed <= 0:
                logger.warning("Verteidiger-Geschwindigkeit ist 0 oder negativ!")
                return 0
            
            ratio = attacker_speed / defender_speed
            
            if ratio >= 2.0:
                return 2
            elif ratio >= 1.5:
                return 1
            else:
                return 0
                
        except Exception as e:
            logger.error(f"Fehler bei der Kritischer-Treffer-Bonus-Berechnung: {str(e)}")
            return 0


class TrickRoom:
    """Special field effect that reverses speed order."""
    
    def __init__(self, duration: int = 5):
        """
        Initialize Trick Room effect.
        
        Args:
            duration: Number of turns the effect lasts
        """
        self.duration = max(1, duration)  # Mindestens 1 Runde
        self.turns_remaining = self.duration
        self.active = False
    
    def activate(self) -> None:
        """Activate Trick Room."""
        try:
            self.active = True
            self.turns_remaining = self.duration
        except Exception as e:
            logger.error(f"Fehler beim Aktivieren von Trick Room: {str(e)}")
    
    def deactivate(self) -> None:
        """Deactivate Trick Room."""
        try:
            self.active = False
            self.turns_remaining = 0
        except Exception as e:
            logger.error(f"Fehler beim Deaktivieren von Trick Room: {str(e)}")
    
    def tick(self) -> bool:
        """
        Reduce duration by one turn.
        
        Returns:
            True if effect expired this turn
        """
        try:
            if not self.active:
                return False
            
            self.turns_remaining -= 1
            if self.turns_remaining <= 0:
                self.deactivate()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Fehler beim Tick von Trick Room: {str(e)}")
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
        try:
            if self.active:
                return max_speed - speed
            return speed
            
        except Exception as e:
            logger.error(f"Fehler bei der Geschwindigkeitsmodifikation: {str(e)}")
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


def resolve_multi_target_action(action: BattleAction, formation_manager: FormationManager) -> List[BattleAction]:
    """Split multi-target action into individual targets."""
    if not action.is_multi_target or not action.targets:
        return [action]
    
    # Create individual action for each target
    individual_actions = []
    for target in action.targets:
        individual_action = BattleAction(
            actor=action.actor,
            action_type=action.action_type,
            target=target,
            move=action.move,
            item_id=action.item_id,
            formation_slot=action.formation_slot
        )
        individual_actions.append(individual_action)
    
    return individual_actions


def determine_move_order(actions: List[BattleAction], 
                        trick_room: Optional[TrickRoom] = None,
                        seed: Optional[int] = None,
                        use_dqm_formula: bool = True) -> List[BattleAction]:
    """
    Convenience function to determine move order.
    
    Args:
        actions: List of actions to sort
        trick_room: Optional Trick Room effect
        seed: Random seed for tiebreakers
        use_dqm_formula: Whether to use DQM turn order formula
        
    Returns:
        Sorted list of actions
    """
    try:
        turn_order = TurnOrder(seed)
        
        # Filtere ungültige Aktionen heraus
        valid_actions = [a for a in actions if a and hasattr(a, 'actor') and a.actor]
        
        if not valid_actions:
            logger.warning("Keine gültigen Aktionen für die Zugreihenfolge-Bestimmung!")
            return []
        
        # Modify speeds if Trick Room is active
        if trick_room and trick_room.active:
            for action in valid_actions:
                try:
                    # Trick Room würde hier die Geschwindigkeitsberechnung beeinflussen
                    # Vereinfachte Implementierung für jetzt
                    pass
                except Exception as e:
                    logger.error(f"Fehler bei der Trick Room-Geschwindigkeitsmodifikation: {str(e)}")
        
        for action in valid_actions:
            turn_order.add_action(action)
        
        return turn_order.sort_actions(use_dqm_formula)
        
    except Exception as e:
        logger.error(f"Fehler bei der Zugreihenfolge-Bestimmung: {str(e)}")
        return []


class TurnManager:
    """Manages turn flow and state in battle scenes."""
    
    def __init__(self, game):
        """
        Initialize turn manager.
        
        Args:
            game: Game instance for accessing systems
        """
        self.game = game
        self.current_phase = "input"
        self.turn_order = TurnOrder()
        self.actions_this_turn: List[BattleAction] = []
        self.turn_count = 0
        
    def start_new_turn(self) -> None:
        """Begin a new turn."""
        try:
            self.turn_count += 1
            self.current_phase = "input"
            self.turn_order.clear()
            self.actions_this_turn.clear()
        except Exception as e:
            logger.error(f"Fehler beim Starten einer neuen Runde: {str(e)}")
        
    def add_action(self, action: BattleAction) -> None:
        """Add an action for the current turn."""
        try:
            if not action:
                logger.warning("Versuch, None-Aktion hinzuzufügen!")
                return
            
            self.actions_this_turn.append(action)
            self.turn_order.add_action(action)
            
        except Exception as e:
            logger.error(f"Fehler beim Hinzufügen der Aktion: {str(e)}")
        
    def resolve_turn(self) -> List[BattleAction]:
        """Resolve the current turn and return action order."""
        try:
            sorted_actions = self.turn_order.sort_actions()
            self.current_phase = "execution"
            return sorted_actions
        except Exception as e:
            logger.error(f"Fehler bei der Zugauflösung: {str(e)}")
            return []
        
    def get_current_phase(self) -> str:
        """Get the current battle phase."""
        try:
            return self.current_phase
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der aktuellen Phase: {str(e)}")
            return "error"
        
    def set_phase(self, phase: str) -> None:
        """Set the current battle phase."""
        try:
            if phase not in ["input", "execution", "aftermath", "end"]:
                logger.warning(f"Ungültige Phase gesetzt: {phase}")
                return
            
            self.current_phase = phase
        except Exception as e:
            logger.error(f"Fehler beim Setzen der Phase: {str(e)}")
        
    def is_turn_complete(self) -> bool:
        """Check if all actions for this turn have been added."""
        try:
            # This is a simplified check - in practice you'd check against expected action count
            return len(self.actions_this_turn) > 0
        except Exception as e:
            logger.error(f"Fehler bei der Runden-Vollständigkeits-Überprüfung: {str(e)}")
            return False
