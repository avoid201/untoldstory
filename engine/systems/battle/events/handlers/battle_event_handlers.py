"""
Battle Event Handlers - Battle-specific event handlers
======================================================
Battle-specific event handlers extracted from event_processor_handlers.py
to comply with 300-line limit.
"""

import logging
from typing import List, Dict, Any, Optional, TYPE_CHECKING
import time

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState

from engine.systems.battle.events.event_types import EventType, BattleEvent

logger = logging.getLogger(__name__)


class BattleEventHandlers:
    """
    Battle-specific event handlers.
    Handles battle-related events like damage, fainting, battle end, etc.
    """
    
    def __init__(self, battle_state: 'BattleState'):
        """Initialize battle event handlers."""
        self.state = battle_state
        logger.info("BattleEventHandlers initialized")
    
    def _handle_damage_dealt(self, event: BattleEvent) -> None:
        """Handle damage dealt event."""
        try:
            data = event.data
            target = data.get('target')
            damage = data.get('damage', 0)
            is_critical = data.get('is_critical', False)
            is_super_effective = data.get('is_super_effective', False)
            
            if target and hasattr(target, 'current_hp'):
                # Update HP
                target.current_hp = max(0, target.current_hp - damage)
                
                # Log damage
                crit_text = " (KRITISCH!)" if is_critical else ""
                effective_text = " (SEHR EFFEKTIV!)" if is_super_effective else ""
                logger.info(f"Damage dealt: {damage}{crit_text}{effective_text} to {target.name}")
                
                # Check if target fainted
                if target.current_hp <= 0:
                    self._handle_monster_fainted(BattleEvent(
                        EventType.MONSTER_FAINTED,
                        {'monster': target, 'fainted': True}
                    ))
            
        except Exception as e:
            logger.error(f"Error handling damage dealt event: {e}")
    
    def _handle_monster_fainted(self, event: BattleEvent) -> None:
        """Handle monster fainted event."""
        try:
            data = event.data
            monster = data.get('monster')
            fainted = data.get('fainted', False)
            
            if monster and fainted:
                # Set monster as fainted
                if hasattr(monster, 'current_hp'):
                    monster.current_hp = 0
                
                # Log fainting
                logger.info(f"Monster {monster.name} fainted!")
                
                # Check battle end conditions
                self._check_battle_end_after_faint(monster)
            
        except Exception as e:
            logger.error(f"Error handling monster fainted event: {e}")
    
    def _handle_battle_end(self, event: BattleEvent) -> None:
        """Handle battle end event."""
        try:
            data = event.data
            result = data.get('result', 'UNKNOWN')
            turn_count = data.get('turn_count', 0)
            
            # Set battle as ended
            if hasattr(self.state, 'battle_ended'):
                self.state.battle_ended = True
            
            if hasattr(self.state, 'battle_result'):
                # Ensure result is a BattleResult Enum, not a string
                if isinstance(result, str):
                    from engine.systems.battle.battle_enums import BattleResult
                    try:
                        self.state.battle_result = BattleResult(result.lower())
                    except ValueError:
                        logger.warning(f"Unknown battle result: {result}, defaulting to VICTORY")
                        self.state.battle_result = BattleResult.VICTORY
                else:
                    self.state.battle_result = result
            
            # Log battle end
            logger.info(f"Battle ended: {result} after {turn_count} turns")
            
        except Exception as e:
            logger.error(f"Error handling battle end event: {e}")
    
    def _handle_turn_start(self, event: BattleEvent) -> None:
        """Handle turn start event."""
        try:
            data = event.data
            turn_count = data.get('turn_count', 0)
            
            # Update turn count
            if hasattr(self.state, 'turn_count'):
                self.state.turn_count = turn_count
            
            # Log turn start
            logger.info(f"Turn {turn_count} started")
            
        except Exception as e:
            logger.error(f"Error handling turn start event: {e}")
    
    def _handle_turn_end(self, event: BattleEvent) -> None:
        """Handle turn end event."""
        try:
            data = event.data
            turn_count = data.get('turn_count', 0)
            
            # Log turn end
            logger.info(f"Turn {turn_count} ended")
            
        except Exception as e:
            logger.error(f"Error handling turn end event: {e}")
    
    def _handle_phase_change(self, event: BattleEvent) -> None:
        """Handle phase change event."""
        try:
            data = event.data
            old_phase = data.get('old_phase', 'UNKNOWN')
            new_phase = data.get('new_phase', 'UNKNOWN')
            
            # Update battle phase
            if hasattr(self.state, 'phase'):
                self.state.phase = new_phase
            
            # Log phase change
            logger.info(f"Phase changed: {old_phase} → {new_phase}")
            
        except Exception as e:
            logger.error(f"Error handling phase change event: {e}")
    
    def _handle_action_announce(self, event: BattleEvent) -> None:
        """Handle action announce event."""
        try:
            data = event.data
            actor = data.get('actor')
            action = data.get('action')
            move = data.get('move')
            
            if actor and action and move:
                # Log action announcement
                logger.info(f"{actor.name} announces {action} with {move.name}")
            
        except Exception as e:
            logger.error(f"Error handling action announce event: {e}")
    
    def _handle_action_execute(self, event: BattleEvent) -> None:
        """Handle action execute event."""
        try:
            data = event.data
            actor = data.get('actor')
            action = data.get('action')
            
            if actor and action:
                # Log action execution
                logger.info(f"{actor.name} executes {action}")
            
        except Exception as e:
            logger.error(f"Error handling action execute event: {e}")
    
    def _handle_action_complete(self, event: BattleEvent) -> None:
        """Handle action complete event."""
        try:
            data = event.data
            actor = data.get('actor')
            action = data.get('action')
            success = data.get('success', False)
            
            if actor and action:
                # Log action completion
                status = "successfully" if success else "failed"
                logger.info(f"{actor.name} completed {action} {status}")
            
        except Exception as e:
            logger.error(f"Error handling action complete event: {e}")
    
    def _check_battle_end_after_faint(self, fainted_monster) -> None:
        """Check if battle should end after monster faints."""
        try:
            if not hasattr(self.state, 'player_team') or not hasattr(self.state, 'enemy_team'):
                return
            
            # Check if all player monsters are fainted
            player_fainted = all(
                hasattr(m, 'current_hp') and m.current_hp <= 0
                for m in self.state.player_team
            )
            
            # Check if all enemy monsters are fainted
            enemy_fainted = all(
                hasattr(m, 'current_hp') and m.current_hp <= 0
                for m in self.state.enemy_team
            )
            
            if player_fainted:
                # Player defeated
                from engine.systems.battle.battle_enums import BattleResult
                self._handle_battle_end(BattleEvent(
                    EventType.BATTLE_END,
                    {'result': BattleResult.DEFEAT, 'turn_count': getattr(self.state, 'turn_count', 0)}
                ))
            elif enemy_fainted:
                # Player victorious
                from engine.systems.battle.battle_enums import BattleResult
                self._handle_battle_end(BattleEvent(
                    EventType.BATTLE_END,
                    {'result': BattleResult.VICTORY, 'turn_count': getattr(self.state, 'turn_count', 0)}
                ))
            
        except Exception as e:
            logger.error(f"Error checking battle end after faint: {e}")
    
    def register_handlers(self, event_processor) -> None:
        """Register battle event handlers."""
        try:
            # Register battle-specific handlers
            event_processor.register_handler(EventType.DAMAGE_DEALT, self._handle_damage_dealt)
            event_processor.register_handler(EventType.MONSTER_FAINTED, self._handle_monster_fainted)
            event_processor.register_handler(EventType.BATTLE_END, self._handle_battle_end)
            event_processor.register_handler(EventType.TURN_START, self._handle_turn_start)
            event_processor.register_handler(EventType.TURN_END, self._handle_turn_end)
            event_processor.register_handler(EventType.PHASE_CHANGE, self._handle_phase_change)
            event_processor.register_handler(EventType.ACTION_ANNOUNCE, self._handle_action_announce)
            event_processor.register_handler(EventType.ACTION_EXECUTE, self._handle_action_execute)
            event_processor.register_handler(EventType.ACTION_COMPLETE, self._handle_action_complete)
            
            logger.info("Battle event handlers registered")
            
        except Exception as e:
            logger.error(f"Error registering battle event handlers: {e}")
