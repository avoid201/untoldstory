"""
Turn Processor Execution Events - Event handling for turn execution
================================================================
Event handling and emission logic for turn execution.
"""

import logging
from typing import Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.battle.turn_logic import BattleAction
    from engine.systems.battle.event_processor import EventProcessor

from engine.systems.battle.events.event_types import EventType

logger = logging.getLogger(__name__)


class TurnProcessorExecutionEvents:
    """
    Event handling for turn execution.
    Handles event emission and processing during turn execution.
    """
    
    def __init__(self, battle_state: 'BattleState' = None):
        """Initialize turn execution events handler."""
        self.battle_state = battle_state
        logger.info("TurnProcessorExecutionEvents initialized")
    
    def emit_turn_start_event(self, turn_number: int) -> None:
        """Emit turn start event."""
        try:
            if hasattr(self.battle_state, 'event_processor') and self.battle_state.event_processor:
                self.battle_state.event_processor.emit_event(
                    EventType.TURN_START,
                    {'turn_number': turn_number}
                )
                logger.debug(f"Turn start event emitted for turn {turn_number}")
        except Exception as e:
            logger.error(f"Error emitting turn start event: {e}")
    
    def emit_turn_end_event(self, turn_number: int, results: Dict[str, Any]) -> None:
        """Emit turn end event."""
        try:
            if hasattr(self.battle_state, 'event_processor') and self.battle_state.event_processor:
                self.battle_state.event_processor.emit_event(
                    EventType.TURN_END,
                    {
                        'turn_number': turn_number,
                        'results': results
                    }
                )
                logger.debug(f"Turn end event emitted for turn {turn_number}")
        except Exception as e:
            logger.error(f"Error emitting turn end event: {e}")
    
    def emit_action_start_event(self, action: 'BattleAction') -> None:
        """Emit action start event."""
        try:
            if hasattr(self.battle_state, 'event_processor') and self.battle_state.event_processor:
                self.battle_state.event_processor.emit_event(
                    EventType.ACTION_START,
                    {
                        'action_type': action.action_type.value,
                        'actor': action.actor.name if hasattr(action.actor, 'name') else 'Unknown',
                        'target': action.target.name if action.target and hasattr(action.target, 'name') else None
                    }
                )
                logger.debug(f"Action start event emitted for {action.action_type}")
        except Exception as e:
            logger.error(f"Error emitting action start event: {e}")
    
    def emit_action_end_event(self, action: 'BattleAction', result: Dict[str, Any]) -> None:
        """Emit action end event."""
        try:
            if hasattr(self.battle_state, 'event_processor') and self.battle_state.event_processor:
                self.battle_state.event_processor.emit_event(
                    EventType.ACTION_END,
                    {
                        'action_type': action.action_type.value,
                        'actor': action.actor.name if hasattr(action.actor, 'name') else 'Unknown',
                        'success': result.get('success', False),
                        'message': result.get('message', '')
                    }
                )
                logger.debug(f"Action end event emitted for {action.action_type}")
        except Exception as e:
            logger.error(f"Error emitting action end event: {e}")
    
    def emit_damage_event(self, attacker: 'MonsterInstance', defender: 'MonsterInstance', 
                         damage: int, move_name: str = None) -> None:
        """Emit damage dealt event."""
        try:
            if hasattr(self.battle_state, 'event_processor') and self.battle_state.event_processor:
                self.battle_state.event_processor.emit_event(
                    EventType.DAMAGE_DEALT,
                    {
                        'attacker': attacker.name if hasattr(attacker, 'name') else 'Unknown',
                        'defender': defender.name if hasattr(defender, 'name') else 'Unknown',
                        'damage': damage,
                        'move_name': move_name
                    }
                )
                logger.debug(f"Damage event emitted: {damage} damage")
        except Exception as e:
            logger.error(f"Error emitting damage event: {e}")
    
    def emit_monster_fainted_event(self, monster: 'MonsterInstance') -> None:
        """Emit monster fainted event."""
        try:
            if hasattr(self.battle_state, 'event_processor') and self.battle_state.event_processor:
                self.battle_state.event_processor.emit_event(
                    EventType.MONSTER_FAINTED,
                    {
                        'monster': monster.name if hasattr(monster, 'name') else 'Unknown',
                        'team': 'player' if getattr(monster, 'is_player', False) else 'enemy'
                    }
                )
                logger.debug(f"Monster fainted event emitted for {monster.name}")
        except Exception as e:
            logger.error(f"Error emitting monster fainted event: {e}")
    
    def emit_status_effect_event(self, monster: 'MonsterInstance', status_name: str, 
                                effect_type: str, value: Any = None) -> None:
        """Emit status effect event."""
        try:
            if hasattr(self.battle_state, 'event_processor') and self.battle_state.event_processor:
                self.battle_state.event_processor.emit_event(
                    EventType.STATUS_EFFECT,
                    {
                        'monster': monster.name if hasattr(monster, 'name') else 'Unknown',
                        'status': status_name,
                        'effect_type': effect_type,
                        'value': value
                    }
                )
                logger.debug(f"Status effect event emitted: {status_name} - {effect_type}")
        except Exception as e:
            logger.error(f"Error emitting status effect event: {e}")
    
    def emit_battle_end_event(self, result: str, details: Dict[str, Any] = None) -> None:
        """Emit battle end event."""
        try:
            if hasattr(self.battle_state, 'event_processor') and self.battle_state.event_processor:
                self.battle_state.event_processor.emit_event(
                    EventType.BATTLE_END,
                    {
                        'result': result,
                        'details': details or {}
                    }
                )
                logger.info(f"Battle end event emitted: {result}")
        except Exception as e:
            logger.error(f"Error emitting battle end event: {e}")
    
    def emit_sequential_action_events(self, action: 'BattleAction', result: Dict[str, Any]) -> None:
        """
        Emit events for sequential action execution.
        AGENT 2: Implementiert sequenzielle Event-Emission für Action-Ausführung.
        
        Args:
            action: BattleAction being executed
            result: Action execution result
        """
        try:
            # Emit ACTION_ANNOUNCE event
            self._emit_action_announce_event(action)
            
            # Emit ACTION_START event
            self.emit_action_start_event(action)
            
            # Emit ACTION_EXECUTE event
            self._emit_action_execute_event(action)
            
            # Emit damage events if applicable
            if result.get('success', False) and result.get('damage_dealt', 0) > 0:
                self._emit_damage_sequence_events(action, result)
            
            # Emit ACTION_END event
            self.emit_action_end_event(action, result)
            
        except Exception as e:
            logger.error(f"Error emitting sequential action events: {e}")
    
    def _emit_action_announce_event(self, action: 'BattleAction') -> None:
        """Emit action announce event."""
        try:
            if hasattr(self.battle_state, 'event_processor') and self.battle_state.event_processor:
                self.battle_state.event_processor.emit_event(
                    EventType.ACTION_ANNOUNCE,
                    {
                        'action_type': action.action_type.name,
                        'actor': action.actor.name if hasattr(action.actor, 'name') else 'Unknown',
                        'target': action.target.name if action.target and hasattr(action.target, 'name') else None,
                        'move': action.move.name if action.move and hasattr(action.move, 'name') else None
                    }
                )
                logger.debug(f"Action announce event emitted for {action.action_type}")
        except Exception as e:
            logger.error(f"Error emitting action announce event: {e}")
    
    def _emit_action_execute_event(self, action: 'BattleAction') -> None:
        """Emit action execute event."""
        try:
            if hasattr(self.battle_state, 'event_processor') and self.battle_state.event_processor:
                self.battle_state.event_processor.emit_event(
                    EventType.ACTION_EXECUTE,
                    {
                        'action_type': action.action_type.name,
                        'actor': action.actor.name if hasattr(action.actor, 'name') else 'Unknown',
                        'target': action.target.name if action.target and hasattr(action.target, 'name') else None
                    }
                )
                logger.debug(f"Action execute event emitted for {action.action_type}")
        except Exception as e:
            logger.error(f"Error emitting action execute event: {e}")
    
    def _emit_damage_sequence_events(self, action: 'BattleAction', result: Dict[str, Any]) -> None:
        """Emit damage sequence events for sequential processing."""
        try:
            if not action.target:
                return
            
            damage = result.get('damage_dealt', 0)
            if damage > 0:
                # Emit DAMAGE_DEALT event
                self.emit_damage_event(
                    action.actor, 
                    action.target, 
                    damage, 
                    action.move.name if action.move else None
                )
                
                # Emit HP_BAR_UPDATE event
                self._emit_hp_bar_update_event(action.target, damage)
                
                # Emit critical hit event if applicable
                if result.get('is_critical', False):
                    self._emit_critical_hit_event(action)
                
                # Emit type effectiveness events
                if result.get('is_super_effective', False):
                    self._emit_super_effective_event(action)
                elif result.get('is_not_very_effective', False):
                    self._emit_not_very_effective_event(action)
                elif result.get('is_not_effective', False):
                    self._emit_not_effective_event(action)
                
        except Exception as e:
            logger.error(f"Error emitting damage sequence events: {e}")
    
    def _emit_hp_bar_update_event(self, target: 'MonsterInstance', damage: int) -> None:
        """Emit HP bar update event."""
        try:
            if hasattr(self.battle_state, 'event_processor') and self.battle_state.event_processor:
                self.battle_state.event_processor.emit_event(
                    EventType.HP_BAR_UPDATE,
                    {
                        'target': target,
                        'current_hp': target.current_hp,
                        'max_hp': target.max_hp,
                        'damage': damage
                    }
                )
                logger.debug(f"HP bar update event emitted for {target.name}")
        except Exception as e:
            logger.error(f"Error emitting HP bar update event: {e}")
    
    def _emit_critical_hit_event(self, action: 'BattleAction') -> None:
        """Emit critical hit event."""
        try:
            if hasattr(self.battle_state, 'event_processor') and self.battle_state.event_processor:
                self.battle_state.event_processor.emit_event(
                    EventType.CRITICAL_HIT,
                    {
                        'attacker': action.actor.name if hasattr(action.actor, 'name') else 'Unknown',
                        'target': action.target.name if action.target and hasattr(action.target, 'name') else 'Unknown',
                        'move': action.move.name if action.move and hasattr(action.move, 'name') else None
                    }
                )
                logger.debug(f"Critical hit event emitted")
        except Exception as e:
            logger.error(f"Error emitting critical hit event: {e}")
    
    def _emit_super_effective_event(self, action: 'BattleAction') -> None:
        """Emit super effective event."""
        try:
            if hasattr(self.battle_state, 'event_processor') and self.battle_state.event_processor:
                self.battle_state.event_processor.emit_event(
                    EventType.SUPER_EFFECTIVE,
                    {
                        'attacker': action.actor.name if hasattr(action.actor, 'name') else 'Unknown',
                        'target': action.target.name if action.target and hasattr(action.target, 'name') else 'Unknown',
                        'move': action.move.name if action.move and hasattr(action.move, 'name') else None
                    }
                )
                logger.debug(f"Super effective event emitted")
        except Exception as e:
            logger.error(f"Error emitting super effective event: {e}")
    
    def _emit_not_very_effective_event(self, action: 'BattleAction') -> None:
        """Emit not very effective event."""
        try:
            if hasattr(self.battle_state, 'event_processor') and self.battle_state.event_processor:
                self.battle_state.event_processor.emit_event(
                    EventType.NOT_VERY_EFFECTIVE,
                    {
                        'attacker': action.actor.name if hasattr(action.actor, 'name') else 'Unknown',
                        'target': action.target.name if action.target and hasattr(action.target, 'name') else 'Unknown',
                        'move': action.move.name if action.move and hasattr(action.move, 'name') else None
                    }
                )
                logger.debug(f"Not very effective event emitted")
        except Exception as e:
            logger.error(f"Error emitting not very effective event: {e}")
    
    def _emit_not_effective_event(self, action: 'BattleAction') -> None:
        """Emit not effective event."""
        try:
            if hasattr(self.battle_state, 'event_processor') and self.battle_state.event_processor:
                self.battle_state.event_processor.emit_event(
                    EventType.NOT_EFFECTIVE,
                    {
                        'attacker': action.actor.name if hasattr(action.actor, 'name') else 'Unknown',
                        'target': action.target.name if action.target and hasattr(action.target, 'name') else 'Unknown',
                        'move': action.move.name if action.move and hasattr(action.move, 'name') else None
                    }
                )
                logger.debug(f"Not effective event emitted")
        except Exception as e:
            logger.error(f"Error emitting not effective event: {e}")
    
    def process_turn_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process events that occurred during turn execution.
        
        Args:
            events: List of events to process
            
        Returns:
            Dictionary with event processing results
        """
        try:
            results = {
                'events_processed': 0,
                'events_failed': 0,
                'damage_total': 0,
                'monsters_fainted': 0,
                'status_effects_applied': 0
            }
            
            for event in events:
                try:
                    event_type = event.get('type')
                    
                    if event_type == EventType.DAMAGE_DEALT:
                        results['damage_total'] += event.get('damage', 0)
                    elif event_type == EventType.MONSTER_FAINTED:
                        results['monsters_fainted'] += 1
                    elif event_type == EventType.STATUS_EFFECT:
                        results['status_effects_applied'] += 1
                    
                    results['events_processed'] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing event: {e}")
                    results['events_failed'] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing turn events: {e}")
            return {'events_processed': 0, 'events_failed': len(events)}
