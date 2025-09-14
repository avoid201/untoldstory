"""
Battle UI Events - Event-Handling für modulare Battle UI
Zerlegt aus der monolithischen battle_ui.py

ENHANCED: Visual Effects Integration
- Event-Handler für HP-Bar-Animationen
- Event-Handler für Damage-Numbers
- Event-Handler für Visual-Effects
- Event-Handler für Attack-Animationen

Verantwortlichkeiten:
- Event-Handler Registration
- Event Processing
- UI Event Integration
- Event Validation
- Visual Effects Integration
"""

import logging
from typing import Dict, Any, Optional

# Setup logger
logger = logging.getLogger(__name__)

# Import modular components
from .battle_ui_state import BattleMenuState


class BattleUIEventManager:
    """
    Event Manager für Battle UI.
    
    Verantwortlich für Event-Handler Registration und Processing.
    """
    
    def __init__(self, battle_ui):
        """Initialisiere Event Manager mit Battle UI Referenz."""
        self.battle_ui = battle_ui
        self.event_handlers = {}
        
        logger.info("Battle UI Event Manager initialized")
    
    def register_event_handler(self, event_type: str, handler_func) -> None:
        """Registriere Event Handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler_func)
        logger.debug(f"Event handler registered for {event_type}")
    
    def process_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Process Event."""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event_data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")
        else:
            logger.warning(f"No handlers for event type: {event_type}")
    
    def register_ui_event_handlers(self, event_processor) -> None:
        """Registriere alle UI Event Handler - BEREINIGT für 45 Events."""
        from engine.systems.battle.events.event_types import EventType
        
        # Core Battle Events (11)
        event_processor.register_handler(EventType.BATTLE_START, self.battle_ui._on_battle_start)
        event_processor.register_handler(EventType.PHASE_CHANGE, self.battle_ui._on_phase_change)
        event_processor.register_handler(EventType.TURN_START, self.battle_ui._on_turn_start)
        event_processor.register_handler(EventType.TURN_END, self.battle_ui._on_turn_end)
        event_processor.register_handler(EventType.BATTLE_END, self.battle_ui._on_battle_end)
        event_processor.register_handler(EventType.ACTION_ANNOUNCE, self.battle_ui._on_action_announce)
        event_processor.register_handler(EventType.ACTION_START, self.battle_ui._on_action_start)
        event_processor.register_handler(EventType.ACTION_EXECUTE, self.battle_ui._on_action_execute)
        event_processor.register_handler(EventType.ACTION_END, self.battle_ui._on_action_end)
        event_processor.register_handler(EventType.ACTION_COMPLETE, self.battle_ui._on_action_complete)
        event_processor.register_handler(EventType.DAMAGE_DEALT, self.battle_ui._on_damage_dealt)
        
        # Combat Events (3)
        event_processor.register_handler(EventType.STATUS_APPLIED, self.battle_ui._on_status_applied)
        event_processor.register_handler(EventType.STAT_CHANGE, self.battle_ui._on_stat_change)
        
        # Monster Events (2)
        event_processor.register_handler(EventType.MONSTER_FAINTED, self.battle_ui._on_monster_fainted)
        event_processor.register_handler(EventType.MONSTER_SWITCH, self.battle_ui._on_monster_switch)
        
        # UI Events (4)
        event_processor.register_handler(EventType.MESSAGE_SHOW, self.battle_ui._on_message_show)
        event_processor.register_handler(EventType.MENU_OPEN, self.battle_ui._on_menu_open)
        event_processor.register_handler(EventType.MENU_CLOSE, self.battle_ui._on_menu_close)
        event_processor.register_handler(EventType.HP_BAR_UPDATE, self.battle_ui._on_hp_update)
        
        # Combat Mechanics (6)
        event_processor.register_handler(EventType.CRITICAL_HIT, self.battle_ui._on_critical_hit)
        event_processor.register_handler(EventType.MISS, self.battle_ui._on_miss)
        event_processor.register_handler(EventType.DODGE, self.battle_ui._on_dodge)
        event_processor.register_handler(EventType.BLOCK, self.battle_ui._on_block)
        event_processor.register_handler(EventType.REFLECT, self.battle_ui._on_reflect)
        event_processor.register_handler(EventType.ABSORB, self.battle_ui._on_absorb)
        
        # Special Moves (4)
        event_processor.register_handler(EventType.CHARGE, self.battle_ui._on_charge)
        event_processor.register_handler(EventType.DISCHARGE, self.battle_ui._on_discharge)
        event_processor.register_handler(EventType.SUMMON, self.battle_ui._on_summon)
        event_processor.register_handler(EventType.BANISH, self.battle_ui._on_banish)
        
        # Battle Actions (3)
        event_processor.register_handler(EventType.ESCAPE_ATTEMPT, self.battle_ui._on_escape_attempt)
        event_processor.register_handler(EventType.ITEM_USE, self.battle_ui._on_item_use)
        event_processor.register_handler(EventType.TAME_ATTEMPT, self.battle_ui._on_tame_attempt)
        
        # Dialog Events (2)
        event_processor.register_handler(EventType.DIALOG_SHOW, self.battle_ui._on_dialog_show)
        event_processor.register_handler(EventType.DIALOG_CHOICE, self.battle_ui._on_dialog_choice)
        
        # Weather/Terrain Events (2)
        event_processor.register_handler(EventType.WEATHER_EFFECT, self.battle_ui._on_weather_effect)
        event_processor.register_handler(EventType.TERRAIN_EFFECT, self.battle_ui._on_terrain_effect)
        
        # Wait Events (3)
        event_processor.register_handler(EventType.WAIT, self.battle_ui._on_wait)
        event_processor.register_handler(EventType.WAIT_FOR_INPUT, self.battle_ui._on_wait_for_input)
        event_processor.register_handler(EventType.WAIT_FOR_ANIMATION, self.battle_ui._on_wait_for_animation)
        
        # Level/Type Events (6)
        event_processor.register_handler(EventType.LEVEL_UP, self.battle_ui._on_level_up)
        event_processor.register_handler(EventType.SUPER_EFFECTIVE, self.battle_ui._on_super_effective)
        event_processor.register_handler(EventType.NOT_EFFECTIVE, self.battle_ui._on_not_effective)
        event_processor.register_handler(EventType.NOT_VERY_EFFECTIVE, self.battle_ui._on_not_very_effective)
        event_processor.register_handler(EventType.NO_EFFECT, self.battle_ui._on_no_effect)
        event_processor.register_handler(EventType.IMMUNE, self.battle_ui._on_immune)
        
        # ENHANCED: Visual Effects Events (8)
        event_processor.register_handler(EventType.ANIMATION_PLAY, self.battle_ui._on_animation_play)
        event_processor.register_handler(EventType.HEAL, self.battle_ui._on_heal)
        event_processor.register_handler(EventType.REVIVE, self.battle_ui._on_revive)
        event_processor.register_handler(EventType.TRANSFORM, self.battle_ui._on_transform)
        event_processor.register_handler(EventType.COPY, self.battle_ui._on_copy)
        event_processor.register_handler(EventType.STEAL, self.battle_ui._on_steal)
        event_processor.register_handler(EventType.SWAP, self.battle_ui._on_swap)
        event_processor.register_handler(EventType.TRAP, self.battle_ui._on_trap)
        
        logger.info("✅ All 53 UI Event Handlers registered (Enhanced with Visual Effects)")
    
    def register_all_ui_handlers(self, event_processor) -> None:
        """Alias for register_ui_event_handlers for compatibility."""
        self.register_ui_event_handlers(event_processor)
    
    def validate_event_handlers(self) -> Dict[str, bool]:
        """Validate that all critical event handlers are registered."""
        critical_events = [
            "HP_BAR_UPDATE",
            "DAMAGE_DEALT", 
            "HEALING_DONE",
            "MESSAGE_SHOW",
            "TURN_START",
            "TURN_END",
            "PHASE_CHANGE",
            "BATTLE_START",
            "BATTLE_END",
            "MONSTER_FAINTED",
            "MONSTER_SWITCH",
            "MONSTER_APPEAR",
            "STATUS_APPLIED",
            "STATUS_REMOVED",
            "STATUS_DAMAGE",
            "CRITICAL_HIT",
            "MISS",
            "TAME_ATTEMPT",
            # ENHANCED: Visual Effects Events
            "ANIMATION_PLAY",
            "HEAL",
            "REVIVE",
            "TRANSFORM",
            "COPY",
            "STEAL",
            "SWAP",
            "TRAP"
        ]
        
        validation = {}
        for event_type in critical_events:
            has_handlers = event_type in self.event_handlers and len(self.event_handlers[event_type]) > 0
            validation[event_type] = has_handlers
            
            if not has_handlers:
                logger.warning(f"⚠️ No handlers for critical event: {event_type}")
            else:
                logger.debug(f"✓ Event handlers available for {event_type}")
        
        return validation
    
    def get_event_handler_count(self) -> int:
        """Get total number of registered event handlers."""
        total = 0
        for handlers in self.event_handlers.values():
            total += len(handlers)
        return total
    
    def clear_event_handlers(self) -> None:
        """Clear all event handlers."""
        self.event_handlers.clear()
        logger.info("All event handlers cleared")
    
    def get_event_handler_info(self) -> Dict[str, Any]:
        """Get information about registered event handlers."""
        info = {
            "total_events": len(self.event_handlers),
            "total_handlers": self.get_event_handler_count(),
            "events": {}
        }
        
        for event_type, handlers in self.event_handlers.items():
            info["events"][event_type] = {
                "handler_count": len(handlers),
                "handlers": [handler.__name__ for handler in handlers]
            }
        
        return info
