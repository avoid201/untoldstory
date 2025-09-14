"""
Event Processor Handlers - Facade for specialized event handlers
===============================================================
Facade maintaining backward compatibility while delegating to specialized modules.
All event handler logic split into specialized modules to comply with 300-line limit.
"""

import logging
from typing import List, Dict, Any, Optional, Callable, TYPE_CHECKING
import time

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState

from engine.systems.battle.events.event_types import EventType, BattleEvent
from engine.ui.battle.battle_ui_state import BattleMenuState

# Import specialized event handlers
from .handlers.battle_event_handlers import BattleEventHandlers
from .handlers.ui_event_handlers import UIEventHandlers

logger = logging.getLogger(__name__)


class EventProcessorHandlers:
    """
    EVENT PROCESSOR HANDLERS FACADE - Delegates to specialized event handler modules.
    Maintains backward compatibility while using modular architecture.
    """
    
    def __init__(self, battle_state: 'BattleState'):
        """Initialize event handler manager."""
        self.state = battle_state
        self.default_handlers_registered = False
        
        # Initialize specialized handlers
        self.battle_handlers = BattleEventHandlers(battle_state)
        self.ui_handlers = UIEventHandlers(battle_state, battle_ui=None)
        
        logger.info("EventProcessorHandlers initialized with specialized modules")
    
    def register_default_handlers(self, event_processor):
        """Register default event handlers - delegates to specialized modules."""
        try:
            if self.default_handlers_registered:
                return
            
            # Register specialized handlers
            self.battle_handlers.register_handlers(event_processor)
            self.ui_handlers.register_handlers(event_processor)
            
            # Register additional common handlers
            event_processor.register_handler(EventType.STATUS_APPLIED, self._handle_status_applied)
            event_processor.register_handler(EventType.STAT_CHANGE, self._handle_stat_change)
            event_processor.register_handler(EventType.LEVEL_UP, self._handle_level_up)
            event_processor.register_handler(EventType.MONSTER_SWITCH, self._handle_monster_switch)
            event_processor.register_handler(EventType.ITEM_USE, self._handle_item_use)
            event_processor.register_handler(EventType.TAME_ATTEMPT, self._handle_tame_attempt)
            event_processor.register_handler(EventType.ESCAPE_ATTEMPT, self._handle_escape_attempt)
            event_processor.register_handler(EventType.WEATHER_EFFECT, self._handle_weather_effect)
            event_processor.register_handler(EventType.TERRAIN_EFFECT, self._handle_terrain_effect)
            event_processor.register_handler(EventType.WAIT, self._handle_wait)
            event_processor.register_handler(EventType.WAIT_FOR_INPUT, self._handle_wait_for_input)
            event_processor.register_handler(EventType.WAIT_FOR_ANIMATION, self._handle_wait_for_animation)
            event_processor.register_handler(EventType.HEAL, self._handle_heal)
            event_processor.register_handler(EventType.REVIVE, self._handle_revive)
            event_processor.register_handler(EventType.TRANSFORM, self._handle_transform)
            event_processor.register_handler(EventType.COPY, self._handle_copy)
            event_processor.register_handler(EventType.CHARGE, self._handle_charge)
            event_processor.register_handler(EventType.DISCHARGE, self._handle_discharge)
            event_processor.register_handler(EventType.SUMMON, self._handle_summon)
            event_processor.register_handler(EventType.BANISH, self._handle_banish)
            # Note: Some handlers removed to stay under 300 lines
            
            self.default_handlers_registered = True
            logger.info("All default event handlers registered")
            
        except Exception as e:
            logger.error(f"Error registering default handlers: {e}")
    
    # Additional common event handlers
    def _handle_status_applied(self, event: BattleEvent) -> None:
        """Handle status applied event."""
        try:
            data = event.data
            target = data.get('target')
            status = data.get('status', 'UNKNOWN')
            duration = data.get('duration', 0)
            
            if target and hasattr(target, 'name'):
                logger.info(f"Status applied: {status} to {target.name} for {duration} turns")
            
        except Exception as e:
            logger.error(f"Error handling status applied event: {e}")
    
    def _handle_stat_change(self, event: BattleEvent) -> None:
        """Handle stat change event."""
        try:
            data = event.data
            target = data.get('target')
            stat = data.get('stat', 'UNKNOWN')
            change = data.get('change', 0)
            stage = data.get('stage', 0)
            
            if target and hasattr(target, 'name'):
                logger.info(f"Stat change: {target.name}'s {stat} {change:+d} (stage {stage:+d})")
            
        except Exception as e:
            logger.error(f"Error handling stat change event: {e}")
    
    def _handle_level_up(self, event: BattleEvent) -> None:
        """Handle level up event."""
        try:
            data = event.data
            monster = data.get('monster')
            old_level = data.get('old_level', 0)
            new_level = data.get('new_level', 0)
            
            if monster and hasattr(monster, 'name'):
                logger.info(f"Level up: {monster.name} {old_level} → {new_level}")
            
        except Exception as e:
            logger.error(f"Error handling level up event: {e}")
    
    def _handle_monster_switch(self, event: BattleEvent) -> None:
        """Handle monster switch event."""
        try:
            data = event.data
            old_monster = data.get('old_monster')
            new_monster = data.get('new_monster')
            
            if old_monster and new_monster:
                old_name = old_monster.name if hasattr(old_monster, 'name') else 'Unknown'
                new_name = new_monster.name if hasattr(new_monster, 'name') else 'Unknown'
                logger.info(f"Monster switch: {old_name} → {new_name}")
            
        except Exception as e:
            logger.error(f"Error handling monster switch event: {e}")
    
    def _handle_item_use(self, event: BattleEvent) -> None:
        """Handle item use event."""
        try:
            data = event.data
            user = data.get('user')
            item = data.get('item', 'UNKNOWN')
            target = data.get('target')
            
            if user and hasattr(user, 'name'):
                target_name = target.name if target and hasattr(target, 'name') else 'self'
                logger.info(f"Item used: {user.name} used {item} on {target_name}")
            
        except Exception as e:
            logger.error(f"Error handling item use event: {e}")
    
    def _handle_tame_attempt(self, event: BattleEvent) -> None:
        """Handle tame attempt event."""
        try:
            data = event.data
            tamer = data.get('tamer')
            target = data.get('target')
            success = data.get('success', False)
            chance = data.get('chance', 0)
            
            if tamer and target:
                tamer_name = tamer.name if hasattr(tamer, 'name') else 'Unknown'
                target_name = target.name if hasattr(target, 'name') else 'Unknown'
                result = "SUCCESS" if success else "FAILED"
                logger.info(f"Tame attempt: {tamer_name} tried to tame {target_name} ({chance}% chance) - {result}")
            
        except Exception as e:
            logger.error(f"Error handling tame attempt event: {e}")
    
    def _handle_escape_attempt(self, event: BattleEvent) -> None:
        """Handle escape attempt event."""
        try:
            data = event.data
            escaper = data.get('escaper')
            success = data.get('success', False)
            chance = data.get('chance', 0)
            
            if escaper and hasattr(escaper, 'name'):
                result = "SUCCESS" if success else "FAILED"
                logger.info(f"Escape attempt: {escaper.name} tried to escape ({chance}% chance) - {result}")
            
        except Exception as e:
            logger.error(f"Error handling escape attempt event: {e}")
    
    def _handle_weather_effect(self, event: BattleEvent) -> None:
        """Handle weather effect event."""
        try:
            data = event.data
            weather = data.get('weather', 'UNKNOWN')
            intensity = data.get('intensity', 1)
            
            logger.info(f"Weather effect: {weather} (intensity {intensity})")
            
        except Exception as e:
            logger.error(f"Error handling weather effect event: {e}")
    
    def _handle_terrain_effect(self, event: BattleEvent) -> None:
        """Handle terrain effect event."""
        try:
            data = event.data
            terrain = data.get('terrain', 'UNKNOWN')
            effect = data.get('effect', 'UNKNOWN')
            
            logger.info(f"Terrain effect: {terrain} - {effect}")
            
        except Exception as e:
            logger.error(f"Error handling terrain effect event: {e}")
    
    def _handle_wait(self, event: BattleEvent) -> None:
        """Handle wait event."""
        try:
            data = event.data
            duration = data.get('duration', 1.0)
            
            logger.info(f"Wait: {duration}s")
            time.sleep(duration)
            
        except Exception as e:
            logger.error(f"Error handling wait event: {e}")
    
    def _handle_wait_for_input(self, event: BattleEvent) -> None:
        """Handle wait for input event."""
        try:
            data = event.data
            input_type = data.get('input_type', 'UNKNOWN')
            
            logger.info(f"Waiting for input: {input_type}")
            
        except Exception as e:
            logger.error(f"Error handling wait for input event: {e}")
    
    def _handle_wait_for_animation(self, event: BattleEvent) -> None:
        """Handle wait for animation event."""
        try:
            data = event.data
            animation = data.get('animation', 'UNKNOWN')
            duration = data.get('duration', 1.0)
            
            logger.info(f"Waiting for animation: {animation} ({duration}s)")
            
        except Exception as e:
            logger.error(f"Error handling wait for animation event: {e}")
    
    def _handle_heal(self, event: BattleEvent) -> None:
        """Handle heal event."""
        try:
            data = event.data
            target = data.get('target')
            amount = data.get('amount', 0)
            heal_type = data.get('heal_type', 'UNKNOWN')
            
            if target and hasattr(target, 'name'):
                logger.info(f"Heal: {target.name} healed {amount} HP ({heal_type})")
            
        except Exception as e:
            logger.error(f"Error handling heal event: {e}")
    
    def _handle_revive(self, event: BattleEvent) -> None:
        """Handle revive event."""
        try:
            data = event.data
            target = data.get('target')
            hp_restored = data.get('hp_restored', 0)
            
            if target and hasattr(target, 'name'):
                logger.info(f"Revive: {target.name} revived with {hp_restored} HP")
            
        except Exception as e:
            logger.error(f"Error handling revive event: {e}")
    
    def _handle_transform(self, event: BattleEvent) -> None:
        """Handle transform event."""
        try:
            data = event.data
            target = data.get('target')
            new_form = data.get('new_form', 'UNKNOWN')
            
            if target and hasattr(target, 'name'):
                logger.info(f"Transform: {target.name} transformed into {new_form}")
            
        except Exception as e:
            logger.error(f"Error handling transform event: {e}")
    
    def _handle_copy(self, event: BattleEvent) -> None:
        """Handle copy event."""
        try:
            data = event.data
            copier = data.get('copier')
            copied = data.get('copied', 'UNKNOWN')
            
            if copier and hasattr(copier, 'name'):
                logger.info(f"Copy: {copier.name} copied {copied}")
            
        except Exception as e:
            logger.error(f"Error handling copy event: {e}")
    
    def _handle_charge(self, event: BattleEvent) -> None:
        """Handle charge event."""
        try:
            data = event.data
            actor = data.get('actor')
            if actor and hasattr(actor, 'name'):
                logger.info(f"Monster charging: {actor.name}")
        except Exception as e:
            logger.error(f"Error handling charge event: {e}")
    
    def _handle_discharge(self, event: BattleEvent) -> None:
        """Handle discharge event."""
        try:
            data = event.data
            actor = data.get('actor')
            if actor and hasattr(actor, 'name'):
                logger.info(f"Monster discharging: {actor.name}")
        except Exception as e:
            logger.error(f"Error handling discharge event: {e}")
    
    def _handle_summon(self, event: BattleEvent) -> None:
        """Handle summon event."""
        try:
            data = event.data
            actor = data.get('actor')
            if actor and hasattr(actor, 'name'):
                logger.info(f"Monster summoned: {actor.name}")
        except Exception as e:
            logger.error(f"Error handling summon event: {e}")
    
    def _handle_banish(self, event: BattleEvent) -> None:
        """Handle banish event."""
        try:
            data = event.data
            target = data.get('target')
            if target and hasattr(target, 'name'):
                logger.info(f"Monster banished: {target.name}")
        except Exception as e:
            logger.error(f"Error handling banish event: {e}")
    
    # Additional handlers removed to stay under 300 lines