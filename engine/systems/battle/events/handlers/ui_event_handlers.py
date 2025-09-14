"""
UI Event Handlers - UI-specific event handlers
==============================================
UI-specific event handlers extracted from event_processor_handlers.py
to comply with 300-line limit.
"""

import logging
from typing import List, Dict, Any, Optional, TYPE_CHECKING
import time

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState

from engine.systems.battle.events.event_types import EventType, BattleEvent
from engine.ui.battle.battle_ui_state import BattleMenuState

logger = logging.getLogger(__name__)


class UIEventHandlers:
    """
    UI-specific event handlers.
    Handles UI-related events like messages, HP bar updates, menu changes, etc.
    """
    
    def __init__(self, battle_state: 'BattleState', battle_ui=None):
        """Initialize UI event handlers."""
        self.state = battle_state
        self.battle_ui = battle_ui
        self.message_queue = []
        self.current_message = None
        self.message_start_time = 0
        logger.info("UIEventHandlers initialized")
    
    def _handle_message_show(self, event: BattleEvent) -> None:
        """Handle message show event."""
        try:
            data = event.data
            message = data.get('message', '')
            duration = data.get('duration', 2.0)
            blocking = data.get('blocking', True)
            
            if message:
                # Add message to queue
                self.message_queue.append({
                    'message': message,
                    'duration': duration,
                    'blocking': blocking,
                    'start_time': time.time()
                })
                
                # Log message
                logger.info(f"Message queued: {message}")
            
        except Exception as e:
            logger.error(f"Error handling message show event: {e}")
    
    def _handle_hp_bar_update(self, event: BattleEvent) -> None:
        """Handle HP bar update event - SOFORTIGE UI-UPDATES."""
        try:
            data = event.data
            target = data.get('target')
            new_hp = data.get('new_hp', 0)
            max_hp = data.get('max_hp', 1)
            animated = data.get('animated', True)
            
            if target and hasattr(target, 'current_hp'):
                # Update monster HP
                target.current_hp = new_hp
                if hasattr(target, 'max_hp'):
                    target.max_hp = max_hp
                
                # Trigger UI update
                if hasattr(self.battle_ui, 'update_hp_bar'):
                    self.battle_ui.update_hp_bar(target, animated=animated)
                
                # Log HP update
                hp_percent = (new_hp / max_hp) * 100 if max_hp > 0 else 0
                logger.info(f"🎯 HP updated: {target.name} {new_hp}/{max_hp} ({hp_percent:.1f}%)")
            
        except Exception as e:
            logger.error(f"Error handling HP bar update event: {e}")
    
    def _handle_menu_open(self, event: BattleEvent) -> None:
        """Handle menu open event."""
        try:
            data = event.data
            menu_type = data.get('menu_type', 'UNKNOWN')
            
            # Update UI state
            if hasattr(self.state, 'waiting_for_input'):
                self.state.waiting_for_input = True
            
            # Log menu open
            logger.info(f"Menu opened: {menu_type}")
            
        except Exception as e:
            logger.error(f"Error handling menu open event: {e}")
    
    def _handle_menu_close(self, event: BattleEvent) -> None:
        """Handle menu close event."""
        try:
            data = event.data
            menu_type = data.get('menu_type', 'UNKNOWN')
            
            # Update UI state
            if hasattr(self.state, 'waiting_for_input'):
                self.state.waiting_for_input = False
            
            # Log menu close
            logger.info(f"Menu closed: {menu_type}")
            
        except Exception as e:
            logger.error(f"Error handling menu close event: {e}")
    
    def _handle_dialog_show(self, event: BattleEvent) -> None:
        """Handle dialog show event."""
        try:
            data = event.data
            dialog_type = data.get('dialog_type', 'UNKNOWN')
            text = data.get('text', '')
            
            # Log dialog
            logger.info(f"Dialog shown: {dialog_type} - {text}")
            
        except Exception as e:
            logger.error(f"Error handling dialog show event: {e}")
    
    def _handle_dialog_choice(self, event: BattleEvent) -> None:
        """Handle dialog choice event."""
        try:
            data = event.data
            choice = data.get('choice', 'UNKNOWN')
            options = data.get('options', [])
            
            # Log choice
            logger.info(f"Dialog choice: {choice} from {len(options)} options")
            
        except Exception as e:
            logger.error(f"Error handling dialog choice event: {e}")
    
    def _handle_animation_play(self, event: BattleEvent) -> None:
        """Handle animation play event."""
        try:
            data = event.data
            animation_type = data.get('animation_type', 'UNKNOWN')
            target = data.get('target')
            duration = data.get('duration', 1.0)
            
            # Log animation
            target_name = target.name if target and hasattr(target, 'name') else 'Unknown'
            logger.info(f"Animation playing: {animation_type} on {target_name} ({duration}s)")
            
        except Exception as e:
            logger.error(f"Error handling animation play event: {e}")
    
    def _handle_critical_hit(self, event: BattleEvent) -> None:
        """Handle critical hit event."""
        try:
            data = event.data
            attacker = data.get('attacker')
            target = data.get('target')
            damage = data.get('damage', 0)
            
            if attacker and target:
                # Log critical hit
                logger.info(f"CRITICAL HIT! {attacker.name} deals {damage} damage to {target.name}")
            
        except Exception as e:
            logger.error(f"Error handling critical hit event: {e}")
    
    def _handle_super_effective(self, event: BattleEvent) -> None:
        """Handle super effective event."""
        try:
            data = event.data
            move_type = data.get('move_type', 'UNKNOWN')
            target_types = data.get('target_types', [])
            multiplier = data.get('multiplier', 1.0)
            
            # Log super effective
            logger.info(f"SUPER EFFECTIVE! {move_type} vs {target_types} (x{multiplier})")
            
        except Exception as e:
            logger.error(f"Error handling super effective event: {e}")
    
    def _handle_not_effective(self, event: BattleEvent) -> None:
        """Handle not effective event."""
        try:
            data = event.data
            move_type = data.get('move_type', 'UNKNOWN')
            target_types = data.get('target_types', [])
            multiplier = data.get('multiplier', 1.0)
            
            # Log not effective
            logger.info(f"NOT EFFECTIVE! {move_type} vs {target_types} (x{multiplier})")
            
        except Exception as e:
            logger.error(f"Error handling not effective event: {e}")
    
    def _handle_no_effect(self, event: BattleEvent) -> None:
        """Handle no effect event."""
        try:
            data = event.data
            move_type = data.get('move_type', 'UNKNOWN')
            target_types = data.get('target_types', [])
            
            # Log no effect
            logger.info(f"NO EFFECT! {move_type} vs {target_types}")
            
        except Exception as e:
            logger.error(f"Error handling no effect event: {e}")
    
    def _handle_miss(self, event: BattleEvent) -> None:
        """Handle miss event."""
        try:
            data = event.data
            attacker = data.get('attacker')
            target = data.get('target')
            
            if attacker and target:
                # Log miss
                logger.info(f"MISS! {attacker.name} missed {target.name}")
            
        except Exception as e:
            logger.error(f"Error handling miss event: {e}")
    
    def _handle_dodge(self, event: BattleEvent) -> None:
        """Handle dodge event."""
        try:
            data = event.data
            attacker = data.get('attacker')
            target = data.get('target')
            
            if attacker and target:
                # Log dodge
                logger.info(f"DODGE! {target.name} dodged {attacker.name}'s attack")
            
        except Exception as e:
            logger.error(f"Error handling dodge event: {e}")
    
    def _handle_block(self, event: BattleEvent) -> None:
        """Handle block event."""
        try:
            data = event.data
            attacker = data.get('attacker')
            target = data.get('target')
            damage_blocked = data.get('damage_blocked', 0)
            
            if attacker and target:
                # Log block
                logger.info(f"BLOCK! {target.name} blocked {attacker.name}'s attack ({damage_blocked} damage blocked)")
            
        except Exception as e:
            logger.error(f"Error handling block event: {e}")
    
    def _handle_reflect(self, event: BattleEvent) -> None:
        """Handle reflect event."""
        try:
            data = event.data
            attacker = data.get('attacker')
            target = data.get('target')
            damage_reflected = data.get('damage_reflected', 0)
            
            if attacker and target:
                # Log reflect
                logger.info(f"REFLECT! {target.name} reflected {damage_reflected} damage to {attacker.name}")
            
        except Exception as e:
            logger.error(f"Error handling reflect event: {e}")
    
    def _handle_absorb(self, event: BattleEvent) -> None:
        """Handle absorb event."""
        try:
            data = event.data
            attacker = data.get('attacker')
            target = data.get('target')
            damage_absorbed = data.get('damage_absorbed', 0)
            
            if attacker and target:
                logger.info(f"ABSORB! {target.name} absorbed {damage_absorbed} damage from {attacker.name}")
        except Exception as e:
            logger.error(f"Error handling absorb event: {e}")
    
    def register_handlers(self, event_processor) -> None:
        """Register UI event handlers."""
        try:
            # Register UI-specific handlers
            event_processor.register_handler(EventType.MESSAGE_SHOW, self._handle_message_show)
            event_processor.register_handler(EventType.HP_BAR_UPDATE, self._handle_hp_bar_update)
            event_processor.register_handler(EventType.MENU_OPEN, self._handle_menu_open)
            event_processor.register_handler(EventType.MENU_CLOSE, self._handle_menu_close)
            event_processor.register_handler(EventType.DIALOG_SHOW, self._handle_dialog_show)
            event_processor.register_handler(EventType.DIALOG_CHOICE, self._handle_dialog_choice)
            event_processor.register_handler(EventType.ANIMATION_PLAY, self._handle_animation_play)
            event_processor.register_handler(EventType.CRITICAL_HIT, self._handle_critical_hit)
            event_processor.register_handler(EventType.SUPER_EFFECTIVE, self._handle_super_effective)
            event_processor.register_handler(EventType.NOT_EFFECTIVE, self._handle_not_effective)
            event_processor.register_handler(EventType.NO_EFFECT, self._handle_no_effect)
            event_processor.register_handler(EventType.MISS, self._handle_miss)
            event_processor.register_handler(EventType.DODGE, self._handle_dodge)
            event_processor.register_handler(EventType.BLOCK, self._handle_block)
            event_processor.register_handler(EventType.REFLECT, self._handle_reflect)
            event_processor.register_handler(EventType.ABSORB, self._handle_absorb)
            
            logger.info("UI event handlers registered")
            
        except Exception as e:
            logger.error(f"Error registering UI event handlers: {e}")
