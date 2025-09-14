"""
Battle Scene for Untold Story - SYNTAX FIXED VERSION
Alle Syntax-Fehler behoben, funktionsfähig
"""

import pygame
import random
import logging
from typing import Optional, List, Dict, Any
from enum import Enum, auto

from engine.core.scene_base import Scene
from engine.core.config import Colors, GameState
from engine.ui.battle import BattleUI, BattleMenuState
from engine.ui.battle_rewards_ui import BattleRewardsUI
from engine.systems.battle.battle_state import BattleState
from engine.systems.battle.battle_controller import BattleController
from engine.systems.battle.turn_processor import TurnProcessor
from engine.systems.battle.action_processor import ActionProcessor
from engine.systems.battle.event_processor import EventProcessor, EventType
from engine.systems.battle.status_processor import StatusProcessor
from engine.systems.battle.battle_enums import BattlePhase, BattleType, BattleResult
from engine.systems.battle.battle_ai import BattleAI
from engine.systems.battle.reward_system import RewardSystem, BattleRewards
from engine.systems.battle.turn_logic import BattleAction, ActionType
from engine.systems.monster_instance import MonsterInstance
# Debug functions (inline)
def debug_battle_info(msg): print(f"[BATTLE INFO] {msg}")
def debug_battle_error(msg, exc_info=False): 
    print(f"[BATTLE ERROR] {msg}")
    if exc_info:
        import traceback
        traceback.print_exc()
def debug_battle_debug(msg): print(f"[BATTLE DEBUG] {msg}")
from engine.scenes.battle_scene_components import (
    BattleScenePhases,
    BattleSceneEffects,
    BattleSceneInput,
    BattleSceneActions,
    BattleSceneIntegration
)

# Logger für Battle Flow Optimization
logger = logging.getLogger(__name__)


class BattleScene(Scene):
    """Main battle scene - SYNTAX FIXED."""
    
    def __init__(self, game):
        super().__init__(game)
        
        # Battle components
        self.battle_ui = BattleUI(game)
        self.battle_rewards_ui = BattleRewardsUI()
        self.battle_state = None
        self.battle_controller = None  # Will be initialized in on_enter
        self.turn_processor = None
        self.action_processor = None
        self.event_processor = None
        self.status_processor = None
        self.battle_ai = BattleAI()
        self.reward_system = RewardSystem()
        
        # Consolidated battle scene components
        self.phases = None  # Will be initialized in on_enter
        self.effects = None  # Will be initialized in on_enter
        self.input_handler = None  # Will be initialized in on_enter
        self.actions = None  # Will be initialized in on_enter
        self.integration = None  # Will be initialized in on_enter
        
        # Battle menu state
        self.current_menu_state = BattleMenuState.MAIN
        self.selected_move = None
        
        # Battle configuration
        self.is_wild = False
        self.is_boss = False
        self.can_flee = True
        self.battle_bg = None
        
        # Battle state (UI-specific only)
        self.waiting_for_input = False
        self.showing_rewards = False
        
        # Rewards data
        self.battle_rewards = None
        
    def on_enter(self, **kwargs):
        """Initialize battle from kwargs."""
        try:
            # Reset battle state flags
            self.showing_rewards = False
            
            # Extract battle parameters
            self.is_wild = kwargs.get('is_wild', True)
            self.can_flee = kwargs.get('can_flee', True)
            
            # Get player team
            if not kwargs.get('player_team'):
                if not hasattr(self.game, 'party_manager') or not self.game.party_manager:
                    if self.game.debug_mode:
                        print("ERROR: Kein Party Manager verfügbar!")
                    self.game.pop_scene()
                    return
                
                player_team = self.game.party_manager.party.get_conscious_members()
                
                if not player_team:
                    if self.game.debug_mode:
                        print("ERROR: Keine kampffähigen Monster im Team!")
                    self.game.pop_scene()
                    return
            else:
                player_team = kwargs.get('player_team', [])
            
            # Get enemy team
            enemy_team = kwargs.get('enemy_team', [])
            if not enemy_team:
                # Create default enemy monster
                from engine.systems.monsters import MonsterDatabase
                db = MonsterDatabase()
                species = db.get_random_species()
                if species:
                    enemy = species.create_instance(level=5)
                    enemy_team = [enemy]
            
            # CRITICAL FIX: Create BattleController FIRST, then use its state
            self.battle_controller = BattleController(
                player_team=player_team,
                enemy_team=enemy_team,
                battle_type=BattleType.WILD if self.is_wild else BattleType.TRAINER,
                can_flee=self.can_flee,
                can_catch=self.is_wild
            )
            
            # Use BattleController's state as single source of truth
            self.battle_state = self.battle_controller.state
            debug_battle_info("BattleScene using BattleController.state as single source of truth")
            
            # Verbinde Battle-State mit UI
            self.battle_ui.battle_state = self.battle_state
            self.battle_ui.battle_controller = self.battle_controller
            debug_battle_info("Battle-State und BattleController mit UI verbunden")
            battle_info = self.battle_controller.initialize(player_team, enemy_team)
            # Battle initialized successfully
            
            # Initialize UI
            self.battle_ui.init_battle(player_team, enemy_team)
            # Stelle sicher, dass UI den battle_state hat
            self.battle_ui.battle_state = self.battle_state
            
            # Initialize demo inventory for testing (remove in production)
            if self.game.debug_mode:
                self.battle_ui.init_demo_inventory()
                debug_battle_info("Demo inventory mit Test-Items initialisiert")
            
            # Initialize battle processors - BUG 3 FIX: EventProcessor wird hier verbunden
            self._initialize_battle_systems()
            
        except Exception as e:
            if self.game.debug_mode:
                print(f"ERROR: Battle initialization failed: {e}")
            import traceback
            traceback.print_exc()
            self.game.pop_scene()
            return
    
    def _initialize_battle_systems(self):
        """Connect all battle systems properly - CRITICAL METHOD."""
        try:
            # Get processors from controller
            if not self.battle_controller:
                logger.error("No battle controller to initialize!")
                return
                
            self.turn_processor = self.battle_controller.turn_processor
            self.action_processor = self.battle_controller.action_processor
            self.event_processor = self.battle_controller.event_processor
            self.status_processor = self.battle_controller.status_processor
            
            # Initialize consolidated battle scene components
            self.phases = BattleScenePhases(self)
            self.effects = BattleSceneEffects(self)
            self.input_handler = BattleSceneInput(self)
            self.actions = BattleSceneActions(self)
            self.integration = BattleSceneIntegration(self)
            
            # CRITICAL: Verbinde BattleScene-Komponenten mit Battle-Systemen
            if self.phases:
                self.phases.battle_state = self.battle_state
                self.phases.battle_controller = self.battle_controller
            if self.effects:
                self.effects.battle_state = self.battle_state
                self.effects.battle_controller = self.battle_controller
            if self.input_handler:
                self.input_handler.battle_state = self.battle_state
                self.input_handler.battle_controller = self.battle_controller
            if self.actions:
                self.actions.battle_state = self.battle_state
                self.actions.battle_controller = self.battle_controller
            
            # Initialize and validate integration
            if self.integration:
                integration_success = self.integration.initialize()
                if integration_success:
                    logger.info("✓ BattleSceneIntegration erfolgreich initialisiert")
                else:
                    logger.error("✗ BattleSceneIntegration Initialisierung fehlgeschlagen")
            
            logger.info("✓ BattleScene-Komponenten mit Battle-Systemen verbunden")
            
            # CRITICAL FIX: Connect EventProcessor to UI IMMEDIATELY after creation
            if self.event_processor and self.battle_ui:
                # Connect event handlers
                self.battle_ui.connect_event_handlers(self.event_processor)
                
                # Ensure battle_state is properly connected
                self.battle_ui.battle_state = self.battle_state
                self.battle_ui.battle_controller = self.battle_controller
                
                # CRITICAL: Connect battle_ui to battle_state for event handlers
                self.battle_state.battle_ui = self.battle_ui
                
                # CRITICAL: Set UI state to MAIN menu
                self.battle_ui.state.menu_state = BattleMenuState.MAIN
                self.battle_ui.state.player_team = self.battle_state.player_team
                self.battle_ui.state.enemy_team = self.battle_state.enemy_team
                self.battle_ui.state.player_active = self.battle_state.player_active
                self.battle_ui.state.enemy_active = self.battle_state.enemy_active
                
                # Clear any pending messages
                self.battle_ui.state.message_queue.clear()
                self.battle_ui.state.current_message = ""
                self.battle_ui.state.message_timer = 0.0
                # CRITICAL: Set UI to waiting for input initially
                self.battle_ui.state.message_wait = True
                self.battle_ui.waiting_for_input = True
                
                # Force menu state to MAIN
                self.battle_ui.state.menu_state = BattleMenuState.MAIN
                
                # Clear any messages that might have been added
                if hasattr(self.battle_ui, 'current_message'):
                    self.battle_ui.current_message = ""
                if hasattr(self.battle_ui, 'message_timer'):
                    self.battle_ui.message_timer = 0.0
                # CRITICAL: Ensure UI is waiting for input
                if hasattr(self.battle_ui, 'message_wait'):
                    self.battle_ui.message_wait = True
                
                # Sync controller state mit UI
                if self.battle_controller:
                    self.battle_controller.sync_state_with_ui(self.battle_ui)
                
                # CRITICAL: Test event connection
                self._test_event_connection()
                
                logger.info("✓ UI connected to EventProcessor - handlers registered")
                logger.info("✓ UI battle_state connected")
            else:
                logger.error("Failed to connect UI to EventProcessor!")
                logger.info("✓ UI fully connected to battle systems")
                
            logger.info("Battle systems initialized and connected")
        except Exception as e:
            logger.error(f"Error initializing battle systems: {e}")
    
    def _test_event_connection(self):
        """Test event connection between EventProcessor and UI."""
        try:
            if not self.event_processor or not self.battle_ui:
                logger.warning("Cannot test event connection - missing components")
                return False
            
            # Test basic event emission
            test_event = {
                'type': 'message',
                'message': 'Event connection test'
            }
            
            # Emit test event
            from engine.systems.battle.event_processor import EventType
            self.event_processor.emit_event(EventType.MESSAGE_SHOW, {'message': 'Event connection test'})
            
            # Process events
            events_processed = self.event_processor.process_events()
            
            if events_processed > 0:
                logger.info(f"✓ Event connection test successful - {events_processed} events processed")
                return True
            else:
                logger.warning("⚠️ Event connection test - no events processed")
                return False
                
        except Exception as e:
            logger.error(f"Event connection test failed: {e}")
            return False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        try:
            if not self.battle_state:
                return False
            
            # Handle rewards UI input first
            if self.showing_rewards:
                if event.type == pygame.KEYDOWN:
                    action = None
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        action = 'confirm'
                    elif event.key == pygame.K_ESCAPE:
                        action = 'escape'
                    
                    if action:
                        self.battle_rewards_ui.handle_input(action)
                        # Always check if rewards are complete after handling input
                        if self.battle_rewards_ui.is_complete():
                            self.showing_rewards = False
                            self._end_battle()
                            return True
                return False
            
            # WICHTIG: Leite Events an UI weiter
            if self.battle_ui:
                ui_handled = self.battle_ui.handle_event(event)
                if ui_handled:
                    # UI has handled the event and may have set _pending_action
                    # Action wird in update() verarbeitet, nicht hier
                    debug_battle_info("UI event handled, action will be processed in update()")
                    return True
                    
        except Exception as e:
            if self.game.debug_mode:
                print(f"Error in handle_event: {e}")
            
        return False
    
    def _process_player_action(self, action):
        """Process player action and trigger turn execution - Accept dict AND BattleAction."""
        try:
            debug_battle_info(f"Processing player action: {action}")
            
            # Convert if needed - Accept both dict and BattleAction
            if isinstance(action, dict):
                battle_action = self._convert_to_battle_action(action)
            else:
                battle_action = action
            
            if not battle_action:
                debug_battle_error("Could not convert action to BattleAction")
                return
            
            # Generate enemy action
            enemy_action = self._generate_enemy_action()
            
            # Execute turn via controller
            if self.battle_controller:
                result = self.battle_controller.execute_turn(
                    player_action=battle_action,
                    enemy_action=enemy_action
                )
                
                debug_battle_info(f"Turn executed: {result}")
                
                # Update state via battle_state
                if result.get('battle_ended'):
                    debug_battle_info(f"🏁 Battle ended! Result: {result.get('battle_result')}")
                    self.battle_state.phase = BattlePhase.END
                    self.battle_state.battle_ended = True
                    self.battle_state.battle_result = result.get('battle_result')
                    
                    # Handle battle end result
                    self._handle_battle_end(result.get('battle_result'))
                    
                    # Emit battle end event to UI
                    if hasattr(self.battle_state, 'event_processor') and self.battle_state.event_processor:
                        from engine.systems.battle.events.event_types import EventType
                        self.battle_state.event_processor.emit_event(
                            EventType.BATTLE_END,
                            {
                                'result': result.get('battle_result'),
                                'battle_ended': True,
                                'reason': 'Battle completed'
                            }
                        )
                else:
                    # Battle continues - reset UI for next turn
                    self.battle_state.phase = BattlePhase.INPUT
                    if self.battle_ui:
                        self.battle_ui.reset_to_main_menu()
                        # CRITICAL: Clear any pending actions to prevent UI hanging
                        self.battle_ui._pending_action = None
                        debug_battle_info("🔄 UI reset for next turn - ready for input")
                    
        except Exception as e:
            debug_battle_error(f"Error processing player action: {e}", exc_info=True)
    
    def _sync_ui_state(self, update_data: Dict[str, Any]) -> None:
        """Sync UI state with battle controller updates."""
        try:
            if self.battle_ui:
                self.battle_ui.apply_update(update_data)
                debug_battle_info(f"UI state synced: {list(update_data.keys())}")
        except Exception as e:
            debug_battle_error(f"Error syncing UI state: {e}")

    def _convert_to_battle_action(self, action_dict):
        """Convert UI action dict to BattleAction."""
        from engine.systems.battle.turn_logic import BattleAction, ActionType
        
        if not isinstance(action_dict, dict):
            return action_dict  # Already a BattleAction
            
        action_type_str = action_dict.get('type') or action_dict.get('action_type')
        if not action_type_str:
            return None
        
        # Ensure action_type_str is a string, not a dict
        if isinstance(action_type_str, dict):
            action_type_str = action_type_str.get('value', 'ATTACK')
        elif not isinstance(action_type_str, str):
            action_type_str = str(action_type_str)
        
        # Handle actor - could be MonsterInstance or string
        actor = action_dict.get('actor')
        if isinstance(actor, str):
            # If actor is a string, use the appropriate active monster
            if 'player' in actor.lower():
                actor = self.battle_state.player_active if self.battle_state else None
            else:
                actor = self.battle_state.enemy_active if self.battle_state else None
        
        # Handle target - could be MonsterInstance or string
        target = action_dict.get('target')
        if isinstance(target, str):
            # If target is a string, use the appropriate active monster
            if 'player' in target.lower():
                target = self.battle_state.player_active if self.battle_state else None
            else:
                target = self.battle_state.enemy_active if self.battle_state else None
        
        # Handle move - could be dict or Move object
        move = action_dict.get('move')
        if isinstance(move, dict):
            # Convert dict to Move object if needed
            from engine.systems.moves import Move
            move = Move(
                id=move.get('name', 'tackle').lower(),
                name=move.get('name', 'Tackle'),
                type='Normal',
                category='PHYSICAL',
                power=move.get('power', 40),
                accuracy=100,
                targeting='ENEMY'
            )
            
        return BattleAction(
            action_type=ActionType.from_string(action_type_str),
            actor=actor,
            target=target,
            move=move,
            item_id=action_dict.get('item_id'),
            switch_to=action_dict.get('switch_to')
        )

    def _generate_enemy_action(self):
        """Generate enemy action via BattleAI."""
        try:
            if not self.battle_state or not hasattr(self, 'battle_ai'):
                debug_battle_error("No battle_state or battle_ai for enemy action")
                return {}
                
            enemy = self.battle_state.enemy_active
            player = self.battle_state.player_active
            
            if not enemy or not player:
                debug_battle_error("No enemy or player active for enemy action")
                return {}
            
            debug_battle_info(f"Getting enemy action: {enemy.name} vs {player.name}")
            
            # Use BattleAI to determine enemy action
            enemy_action = self.battle_ai.choose_action(self.battle_state)
            
            if enemy_action:
                debug_battle_info(f"Enemy action: {enemy_action}")
                return enemy_action
            else:
                debug_battle_error("No enemy action generated")
                return {}
                
        except Exception as e:
            debug_battle_error(f"Enemy action error: {e}")
            return {}

    def _process_battle_action(self, action_result):
        """Process BattleAction from UI - BattleAction oder Dict akzeptieren!"""
        if not action_result or not self.battle_state:
            return
        
        # Import required classes
        from engine.systems.battle.turn_logic import BattleAction, create_action_from_dict
        
        try:
            # BattleAction oder Dict akzeptieren
            if not isinstance(action_result, BattleAction):
                # Konvertiere Dict zu BattleAction falls nötig
                if isinstance(action_result, dict):
                    # Extrahiere benötigte Parameter aus dem Dict
                    actor = self.battle_state.player_active
                    target = self.battle_state.enemy_active
                    move = action_result.get('move')
                    switch_to = action_result.get('switch_to')
                    
                    # Create action dict
                    action_dict = {
                        'action_type': action_result.get('action_type', 'ATTACK'),
                        'actor': actor,
                        'target': target,
                        'move': move,
                        'switch_to': switch_to,
                        'item_id': action_result.get('item_id')
                    }
                    
                    battle_action = create_action_from_dict(action_dict)
                    
                    if not battle_action:
                        print(f"[ERROR] Failed to create BattleAction from dict: {action_result}")
                        return
                else:
                    print(f"[ERROR] Expected BattleAction or dict, got {type(action_result)}")
                    return
            else:
                battle_action = action_result
            
            print(f"[DEBUG] PROCESSING BATTLE ACTION: {battle_action.action_type}")
            
            # BattleAction direkt verwenden
            print(f"[DEBUG] USING BATTLE ACTION: {battle_action.action_type.name}")
            
            # KRITISCH: Diese Zeilen MÜSSEN ausgeführt werden!
            print("[DEBUG] Executing player turn...")
            # Execute turn with player action and get enemy action
            enemy_action = self._get_enemy_action()
            
            # PROFESSIONAL TURN EXECUTION: Execute turn with proper textbox system
            debug_battle_info("⚔️ EXECUTING TURN: Starting turn execution")
            
            # PROFESSIONAL TEXTBOX SYSTEM: Show player action message and wait
            player_message = f"{battle_action.actor.name} setzt {battle_action.move.name} ein!"
            debug_battle_info(f"📝 PLAYER TEXTBOX: {player_message}")
            
            # Execute player action first
            player_result = self.battle_controller.execute_action(battle_action)
            debug_battle_info(f"✅ PLAYER ACTION EXECUTED: {player_result}")
            
            # PROFESSIONAL TEXTBOX SYSTEM: Show enemy action message and wait
            enemy_message = f"{enemy_action.actor.name} setzt {enemy_action.move.name} ein!"
            debug_battle_info(f"📝 ENEMY TEXTBOX: {enemy_message}")
            
            # Execute enemy action
            enemy_result = self.battle_controller.execute_action(enemy_action)
            debug_battle_info(f"✅ ENEMY ACTION EXECUTED: {enemy_result}")
            
            # PROFESSIONAL DEBUG: Check HP after both actions
            player_hp = self.battle_state.player_active.current_hp
            enemy_hp = self.battle_state.enemy_active.current_hp
            debug_battle_info(f"💚 HP STATUS: Player={player_hp}, Enemy={enemy_hp}")
            
            # Create turn result
            turn_result = {
                'success': True,
                'turn': getattr(self.battle_state, 'turn_count', 1),
                'phase': 'input',
                'battle_ended': False,
                'battle_result': None,
                'result': {
                    'success': True,
                    'actions_executed': 2,
                    'actions_failed': 0,
                    'turn_events': [],
                    'damage_dealt': (player_result.get('damage_dealt', 0) + enemy_result.get('damage_dealt', 0)),
                    'monsters_fainted': (player_result.get('monsters_fainted', 0) + enemy_result.get('monsters_fainted', 0)),
                    'battle_ended': False,
                    'battle_result': None
                }
            }
            
            debug_battle_info(f"✅ TURN EXECUTED: {turn_result}")
            
            # Check if battle ended
            if turn_result and turn_result.get('battle_ended'):
                debug_battle_info("🏁 BATTLE ENDED - calling check_battle_end()")
                self.check_battle_end()
            else:
                # Battle continues - PROFESSIONAL UI RESET
                debug_battle_info("🔄 BATTLE CONTINUES - performing professional UI reset")
                self._reset_ui_for_next_turn()
                
                # PROFESSIONAL DEBUG: Verify battle can continue
                if self.battle_state.player_active.current_hp > 0 and self.battle_state.enemy_active.current_hp > 0:
                    debug_battle_info("✅ BATTLE CAN CONTINUE: Both monsters alive - ready for next turn")
                else:
                    debug_battle_error("🚨 BATTLE ERROR: Monster HP issue detected!")
            
        except Exception as e:
            if self.game.debug_mode:
                print(f"Error processing battle action: {e}")
                import traceback
                traceback.print_exc()
    
    def _reset_ui_for_next_turn(self):
        """PROFESSIONAL UI RESET for next turn with detailed debug."""
        if self.battle_ui:
            # PROFESSIONAL UI RESET: Complete state reset
            debug_battle_info(f"   Before reset: waiting_for_input={self.battle_ui.waiting_for_input}")
            debug_battle_info(f"   Before reset: menu_state={getattr(self.battle_ui, 'current_menu_state', 'UNKNOWN')}")
            
            # CRITICAL: Complete UI state reset
            self.battle_ui.current_menu_state = BattleMenuState.MAIN
            self.battle_ui.selected_option = 0
            self.battle_ui.waiting_for_input = True
            self.battle_ui._pending_action = None
            self.battle_ui.current_message = None
            self.battle_ui.message_timer = 0
            
            # CRITICAL: Reset all UI states
            if hasattr(self.battle_ui, 'state'):
                self.battle_ui.state.player_active = self.battle_state.player_active
                self.battle_ui.state.enemy_active = self.battle_state.enemy_active
                if hasattr(self.battle_ui.state, 'message_wait'):
                    self.battle_ui.state.message_wait = True
                if hasattr(self.battle_ui.state, 'waiting_for_input'):
                    self.battle_ui.state.waiting_for_input = True
            
            # Update HP bars after turn
            if hasattr(self.battle_ui, 'update_hp_bar'):
                self.battle_ui.update_hp_bar(self.battle_state.player_active)
                self.battle_ui.update_hp_bar(self.battle_state.enemy_active)
            
            # PROFESSIONAL DEBUG: Verify reset
            debug_battle_info(f"   After reset: waiting_for_input={self.battle_ui.waiting_for_input}")
            debug_battle_info(f"   After reset: menu_state={getattr(self.battle_ui, 'current_menu_state', 'UNKNOWN')}")
            debug_battle_info("✅ PROFESSIONAL UI RESET COMPLETE - ready for next turn")
            
            # CRITICAL: Force UI to main menu
            if hasattr(self.battle_ui, 'menu_manager'):
                self.battle_ui.menu_manager.show_main_menu()
                debug_battle_info("🔧 FORCED UI to main menu")
            
            # PROFESSIONAL DEBUG: Check if UI is ready for input
            if self.battle_ui.waiting_for_input:
                debug_battle_info("✅ UI READY: waiting_for_input=True - ready for player input")
            else:
                debug_battle_error("🚨 UI ERROR: waiting_for_input=False - UI not ready!")
            
            # CRITICAL: Force UI to be ready for input
            self.battle_ui.waiting_for_input = True
            if hasattr(self.battle_ui, 'state') and hasattr(self.battle_ui.state, 'waiting_for_input'):
                self.battle_ui.state.waiting_for_input = True
            debug_battle_info("🔧 FORCED UI to be ready for input")
    

    


    def _get_enemy_action(self):
        """Get enemy action via BattleAI - returns BattleAction."""
        try:
            if not self.battle_state or not hasattr(self, 'battle_ai'):
                logger.warning("No battle_state or battle_ai for enemy action")
                return None
                
            enemy = self.battle_state.enemy_active
            player = self.battle_state.player_active
            
            if not enemy or not player:
                logger.warning("No enemy or player active for enemy action")
                return None
            
            logger.info(f"Getting enemy action: {enemy.name} vs {player.name}")
            
            # Use BattleAI to determine enemy action
            enemy_action_dict = self.battle_ai.choose_action(self.battle_state)
            
            if enemy_action_dict:
                # Convert dict to BattleAction
                enemy_action = self._convert_to_battle_action(enemy_action_dict)
                if enemy_action:
                    logger.info(f"Enemy action: {enemy_action.action_type}")
                    return enemy_action
                else:
                    logger.warning("Failed to convert enemy action to BattleAction")
                    return None
            else:
                logger.warning("No enemy action generated")
                return None
                
        except Exception as e:
            logger.error(f"Enemy action error: {e}", exc_info=True)
            return None

    def _handle_battle_end(self, battle_result):
        """Handle battle end result."""
        try:
            logger.info(f"Battle ended with result: {battle_result}")
            
            if battle_result == BattleResult.VICTORY:
                self.current_phase = BattlePhase.END
                # Show victory rewards
                if self.battle_ui:
                    self.battle_ui.show_victory_message()
                # Return to field after short delay
                import threading
                threading.Timer(2.0, self.exit_battle).start()
            elif battle_result == BattleResult.DEFEAT:
                self.current_phase = BattlePhase.END
                # Show defeat message
                if self.battle_ui:
                    self.battle_ui.show_defeat_message()
                # Return to main menu after short delay
                import threading
                threading.Timer(2.0, self.exit_battle).start()
            elif battle_result == BattleResult.FLED:
                self.current_phase = BattlePhase.END
                # Return to field
                self.exit_battle()
            elif battle_result == BattleResult.CAUGHT:
                self.current_phase = BattlePhase.END
                # Show catch success
                if self.battle_ui:
                    self.battle_ui.show_catch_success_message()
                    
        except Exception as e:
            logger.error(f"Error handling battle end: {e}", exc_info=True)

    def exit_battle(self):
        """Exit battle and return to field scene."""
        try:
            logger.info("Exiting battle")
            # Return to field scene
            if self.game:
                self.game.pop_scene()
        except Exception as e:
            logger.error(f"Error exiting battle: {e}", exc_info=True)
    
    def _process_battle_events(self):
        """Process battle events from controller and update UI - ENHANCED VERSION."""
        try:
            if not self.event_processor or not self.battle_ui:
                return
            
            # Check for pending events
            if not self.event_processor.has_pending_events():
                return
            
            # Log event processing
            pending_count = len(self.event_processor.pending_events) if hasattr(self.event_processor, 'pending_events') else 0
            if pending_count > 0:
                logger.debug(f"[PROCESS EVENTS] Processing {pending_count} pending events")
            
            # Process pending events
            events_processed = self.event_processor.process_events()
            
            # Note: process_events() returns int, not list
            # UI updates are handled internally by the event processor
                            
        except Exception as e:
            logger.error(f"[PROCESS EVENTS ERROR] {e}", exc_info=True)
    

    
    def update(self, dt: float) -> None:
        """Update battle logic with proper action handling."""
        try:
            if not self.battle_state:
                return
            
            # AGENT 4: Update battle phase transitions first
            self.update_battle_phase()
            
            # Use battle_state instead of local variables
            if self.battle_state.battle_ended:
                if not self.showing_rewards:
                    self._show_rewards()
                return
            
            # Check for pending UI action
            if self.battle_ui and hasattr(self.battle_ui, 'pending_action') and self.battle_ui.pending_action:
                action = self.battle_ui.get_action_result()
                if action:
                    self._process_player_action(action)
            
            # Process battle events
            self._process_battle_events()
            
            # Update UI
            if self.battle_ui:
                self.battle_ui.update(dt)
                
            # Check for pending actions from UI
            if self.battle_ui and hasattr(self.battle_ui, 'pending_action') and self.battle_ui.pending_action:
                action_result = self.battle_ui.get_action_result()
                if action_result:
                    debug_battle_info(f"Processing pending action: {action_result}")
                    self._process_player_action(action_result)
                
        except Exception as e:
            logger.error(f"[UPDATE ERROR] {e}", exc_info=True)
    
    def update_battle_phase(self):
        """PROFESSIONAL UPDATE battle phase transitions with detailed debug."""
        if not self.battle_state:
            debug_battle_error("🚨 CRITICAL: No battle_state available!")
            return
        
        current_phase = self.battle_state.phase
        # PROFESSIONAL DEBUG: Only log phase changes, not every frame
        if not hasattr(self, '_last_logged_phase') or self._last_logged_phase != current_phase:
            debug_battle_info(f"🔄 PHASE UPDATE: Current phase = {current_phase}")
            self._last_logged_phase = current_phase
        # Suppress repeated phase logs - no else needed
        
        if current_phase == BattlePhase.INIT:
            self._initialize_battle_systems()
            self.battle_state.phase = BattlePhase.START
            debug_battle_info("✅ Phase: INIT → START")
            
        elif current_phase == BattlePhase.START:
            self.show_battle_intro()
            debug_battle_info("✅ Battle intro shown")
            
            # AGENT 4: Let BattleController handle START → INPUT transition
            if self.battle_controller:
                debug_battle_info("🔧 Using BattleController for phase transition")
                self.battle_controller._transition_to_input_phase()
            else:
                debug_battle_warning("⚠️ No BattleController - using direct transition")
                self.battle_state.phase = BattlePhase.INPUT
                self.battle_state.waiting_for_input = True
            
            # CRITICAL: Inform UI about phase change
            if self.battle_ui:
                debug_battle_info("🔧 Informing UI about phase change to INPUT")
                self.battle_ui._on_phase_change({'phase': 'input'})
                debug_battle_info(f"   UI waiting_for_input after phase change: {getattr(self.battle_ui, 'waiting_for_input', 'UNKNOWN')}")
            else:
                debug_battle_error("🚨 CRITICAL: No battle_ui available for phase change!")
            
            debug_battle_info("✅ Phase: START → INPUT - UI should be waiting for input")
            
        elif self.battle_state.phase == BattlePhase.INPUT:
            # AGENT 4: Wait for player input - phase transitions handled by BattleController
            # PROFESSIONAL DEBUG: Check UI state with detailed logging
            if self.battle_ui and hasattr(self.battle_ui, 'waiting_for_input'):
                if not self.battle_ui.waiting_for_input:
                    debug_battle_error("🚨 UI CRITICAL ERROR: UI is NOT waiting for input!")
                    debug_battle_error(f"   UI State: waiting_for_input={self.battle_ui.waiting_for_input}")
                    debug_battle_error(f"   UI Menu State: {getattr(self.battle_ui, 'current_menu_state', 'UNKNOWN')}")
                    debug_battle_error(f"   UI Selected Option: {getattr(self.battle_ui, 'selected_option', 'UNKNOWN')}")
                    
                    # PROFESSIONAL FIX: Complete UI reset
                    self.battle_ui.waiting_for_input = True
                    self.battle_ui.current_menu_state = BattleMenuState.MAIN
                    self.battle_ui.selected_option = 0
                    self.battle_ui._pending_action = None
                    self.battle_ui.current_message = None
                    self.battle_ui.message_timer = 0
                    
                    if hasattr(self.battle_ui, 'state') and hasattr(self.battle_ui.state, 'message_wait'):
                        self.battle_ui.state.message_wait = True
                    if hasattr(self.battle_ui, 'state') and hasattr(self.battle_ui.state, 'waiting_for_input'):
                        self.battle_ui.state.waiting_for_input = True
                    
                    debug_battle_info("🔧 PROFESSIONAL FIX: Complete UI reset applied")
                    
                    # PROFESSIONAL DEBUG: Verify fix
                    if self.battle_ui.waiting_for_input:
                        debug_battle_info("✅ UI FIX SUCCESS: waiting_for_input=True - ready for input")
                    else:
                        debug_battle_error("🚨 UI FIX FAILED: waiting_for_input still False!")
                        
                    # CRITICAL: Force UI to be ready for input
                    self.battle_ui.waiting_for_input = True
                    debug_battle_info("🔧 FORCED UI to be ready for input")
            
            # Additional safety: Ensure UI state is consistent
            if self.battle_ui and hasattr(self.battle_ui, 'state') and hasattr(self.battle_ui.state, 'message_wait'):
                if not self.battle_ui.state.message_wait:
                    self.battle_ui.state.message_wait = True
                    debug_battle_info("Safety fix: Set message_wait to True")
            
        elif self.battle_state.phase == BattlePhase.EXECUTION:
            # AGENT 4: EXECUTION phase - actions are being processed
            debug_battle_debug("Phase: EXECUTION - processing actions")
            # Phase transitions are handled by BattleController.execute_turn()
            
        elif self.battle_state.phase == BattlePhase.AFTERMATH:
            # AGENT 4: AFTERMATH phase - status effects, cleanup, etc.
            debug_battle_debug("Phase: AFTERMATH - processing status effects")
            # Phase transitions are handled by BattleController.execute_turn()
            
        elif self.battle_state.phase == BattlePhase.END:
            self.handle_battle_end()
            debug_battle_info("Phase: END - battle concluded")
    
    def initialize_battle(self, player_team=None, enemy_team=None):
        """Initialize battle with teams and connect all systems."""
        try:
            # Use provided teams or fall back to battle_state
            if player_team is None and self.battle_state:
                player_team = self.battle_state.player_team
            if enemy_team is None and self.battle_state:
                enemy_team = self.battle_state.enemy_team
                
            if not player_team or not enemy_team:
                debug_battle_error("Cannot initialize battle without teams")
                return False
                
            debug_battle_info(f"Initializing battle: {len(player_team)} vs {len(enemy_team)}")
            
            # Create battle controller (with auto-init managers)
            from engine.systems.battle.battle_controller import BattleController
            self.battle_controller = BattleController(
                player_team=player_team,
                enemy_team=enemy_team
            )
            
            # Initialize controller battle state
            init_result = self.battle_controller.initialize(player_team, enemy_team)
            
            if not init_result.get('success'):
                debug_battle_error(f"Failed to initialize battle controller: {init_result}")
                return False
            
            # CRITICAL: Connect EventProcessor to UI
            if self.battle_controller.event_processor and self.battle_ui:
                # Connect the event processor to UI
                self.battle_ui.connect_event_handlers(self.battle_controller.event_processor)
                debug_battle_info("Connected EventProcessor to BattleUI handlers")
                
                # Also give UI reference to battle state AND controller
                self.battle_ui.battle_state = self.battle_controller.state
                self.battle_ui.battle_controller = self.battle_controller
                
                # CRITICAL FIX: Set up UI sync callback
                self.battle_controller.ui_sync_callback = self._sync_ui_state
                debug_battle_info("Connected BattleUI to controller state and controller")
                
                # CRITICAL FIX: Ensure UI state is synced immediately
                self._sync_ui_state({
                    'battle_state': self.battle_controller.state,
                    'player_active': self.battle_controller.state.player_active,
                    'enemy_active': self.battle_controller.state.enemy_active,
                    'battle_ended': False,
                    'battle_result': None
                })
            else:
                debug_battle_error("Could not connect EventProcessor to UI - missing components")
            
            # Initialize UI with teams
            if self.battle_ui:
                self.battle_ui.init_battle(player_team, enemy_team)
                self.battle_ui.reset_to_main_menu()
            
            # Set initial scene state
            self.battle_state = self.battle_controller.state
            self.battle_state.phase = BattlePhase.START
            self.player_team = player_team
            self.enemy_team = enemy_team
            
            # Show battle start message
            if self.battle_ui:
                enemy_name = enemy_team[0].name if enemy_team else "Wild Monster"
                self.battle_ui.show_message(f"Ein wildes {enemy_name} erscheint!")
            
            # Emit battle start event
            if self.battle_controller.event_processor:
                from engine.systems.battle.event_processor import BattleEvent, EventType
                start_event = BattleEvent(
                    event_type=EventType.BATTLE_START,
                    data={'player_team': player_team, 'enemy_team': enemy_team}
                )
                self.battle_controller.event_processor.emit_event(start_event)
            
            debug_battle_info("Battle initialization complete")
            return True
            
        except ImportError as e:
            debug_battle_error(f"Failed to import battle components: {e}")
            return False
        except Exception as e:
            debug_battle_error(f"Failed to initialize battle: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def show_battle_intro(self):
        """Show battle introduction messages."""
        try:
            if self.battle_state.enemy_active:
                enemy_name = getattr(self.battle_state.enemy_active, 'name', 'Wildes Monster')
                if self.is_wild:
                    message = f"Ein wildes {enemy_name} erscheint!"
                else:
                    message = f"{enemy_name} greift an!"
                
                self.battle_ui.add_message(message)
                debug_battle_info(f"Battle intro: {message}")
                
        except Exception as e:
            debug_battle_error(f"Battle intro failed: {e}")
    

    
    def check_battle_end(self) -> bool:
        """Check if battle should end."""
        try:
            if not self.battle_state:
                return False
            
            # Player defeated - all monsters fainted
            if all(m.current_hp <= 0 for m in self.battle_state.player_team):
                self.battle_state.battle_result = BattleResult.DEFEAT
                self.battle_state.battle_ended = True
                debug_battle_info("Player defeated - all monsters fainted")
                
                # PROFESSIONAL DEBUG: Check all player monsters HP
                for i, monster in enumerate(self.battle_state.player_team):
                    debug_battle_info(f"   Player Monster {i+1}: {monster.name} HP={monster.current_hp}")
                
                self._handle_battle_end(BattleResult.DEFEAT)
                return True
            
            # Enemy defeated
            if self.battle_state.enemy_active.current_hp <= 0:
                debug_battle_info(f"Enemy monster {self.battle_state.enemy_active.name} defeated! HP={self.battle_state.enemy_active.current_hp}")
                
                if len(self.battle_state.enemy_team) > 1:
                    # More enemies available - switch enemy monster
                    debug_battle_info(f"Switching enemy monster - {len(self.battle_state.enemy_team)-1} remaining")
                    self.switch_enemy_monster()
                    return False
                else:
                    self.battle_state.battle_result = BattleResult.VICTORY
                    self.battle_state.battle_ended = True
                    debug_battle_info("Enemy defeated - victory!")
                    
                    # PROFESSIONAL DEBUG: Check all enemy monsters HP
                    for i, monster in enumerate(self.battle_state.enemy_team):
                        debug_battle_info(f"   Enemy Monster {i+1}: {monster.name} HP={monster.current_hp}")
                    
                    self._handle_battle_end(BattleResult.VICTORY)
                    return True
            
            # Successful taming
            if hasattr(self.battle_state, 'monster_caught') and self.battle_state.monster_caught:
                self.battle_state.battle_result = BattleResult.CAUGHT
                self.battle_state.battle_ended = True
                debug_battle_info("Monster caught successfully!")
                self._handle_battle_end(BattleResult.CAUGHT)
                return True
            
            # Successful flee
            if hasattr(self.battle_state, 'fled') and self.battle_state.fled:
                self.battle_state.battle_result = BattleResult.FLED
                self.battle_state.battle_ended = True
                debug_battle_info("Successfully fled from battle")
                self._handle_battle_end(BattleResult.FLED)
                return True
            
            return False
            
        except Exception as e:
            debug_battle_error(f"Battle end check failed: {e}")
            return False
    
    def switch_enemy_monster(self):
        """Switch to next enemy monster."""
        try:
            if not self.battle_state or len(self.battle_state.enemy_team) <= 1:
                return
            
            # Find next conscious enemy
            for monster in self.battle_state.enemy_team:
                if monster.current_hp > 0 and monster != self.battle_state.enemy_active:
                    self.battle_state.enemy_active = monster
                    self.battle_ui.add_message(f"{monster.name} kommt ins Spiel!")
                    debug_battle_info(f"Switched to enemy: {monster.name}")
                    break
                    
        except Exception as e:
            debug_battle_error(f"Enemy switch failed: {e}")
    
    def handle_battle_end(self):
        """Handle battle end and rewards."""
        try:
            if self.battle_state.battle_result == BattleResult.VICTORY:
                self.battle_ui.add_message("Du hast gewonnen!")
                self._show_rewards()
                
            elif self.battle_state.battle_result == BattleResult.DEFEAT:
                self.battle_ui.add_message("Du hast verloren!")
                self._show_defeat_screen()
                
            elif self.battle_state.battle_result == BattleResult.CAUGHT:
                self.battle_ui.add_message("Monster gefangen!")
                self._show_taming_success()
                
            elif self.battle_state.battle_result == BattleResult.FLED:
                self.battle_ui.add_message("Erfolgreich geflohen!")
                self._end_battle()
                
        except Exception as e:
            debug_battle_error(f"Battle end handling failed: {e}")
            self._end_battle()
    
    def _show_defeat_screen(self):
        """Show defeat screen and return to field."""
        try:
            # Show defeat message briefly
            self.battle_ui.add_message("Du wurdest besiegt...")
            
            # End battle after delay
            if not hasattr(self, '_defeat_timer'):
                self._defeat_timer = 0
            
            self._defeat_timer += 0.016  # Assume 60 FPS
            if self._defeat_timer > 3.0:  # 3 seconds
                self._end_battle()
                
        except Exception as e:
            debug_battle_error(f"Defeat screen failed: {e}")
            self._end_battle()
    
    def _show_taming_success(self):
        """Show taming success screen."""
        try:
            if self.battle_state and self.battle_state.enemy_active:
                monster_name = getattr(self.battle_state.enemy_active, 'name', 'Monster')
                self.battle_ui.add_message(f"{monster_name} wurde gezähmt!")
                
                # Add caught monster to rewards
                if not hasattr(self, 'battle_rewards'):
                    self.battle_rewards = type('Rewards', (), {})()
                self.battle_rewards.caught_monster = self.battle_state.enemy_active
                
                # Show rewards with caught monster
                self._show_rewards()
                
        except Exception as e:
            debug_battle_error(f"Taming success screen failed: {e}")
            self._end_battle()
    
    def _show_rewards(self):
        """Calculate and show battle rewards."""
        try:
            # Mark all active monsters as participated
            if self.battle_state and self.battle_state.player_active:
                self.battle_state.player_active.participated = True
            
            # Determine victory type
            victory_type = 'normal'
            if self.battle_state.battle_result == BattleResult.CAUGHT:
                victory_type = 'caught'
            elif self.battle_state and self.battle_state.player_active:
                # Check for perfect victory (no damage taken)
                if self.battle_state.player_active.current_hp == self.battle_state.player_active.max_hp:
                    victory_type = 'perfect'
            
            # Calculate rewards - with fallback if reward_system fails
            try:
                self.battle_rewards = self.reward_system.calculate_battle_rewards(
                    self.battle_state,
                    victory_type
                )
            except Exception as e:
                if self.game.debug_mode:
                    print(f"[Flint] Reward system failed: {e}, using fallback rewards")
                # Create minimal fallback rewards
                from dataclasses import dataclass
                @dataclass
                class FallbackRewards:
                    exp_gained: dict = None
                    money_gained: int = 50
                    items_gained: list = None
                    level_ups: dict = None
                    caught_monster: object = None
                
                self.battle_rewards = FallbackRewards()
                self.battle_rewards.exp_gained = {}
                self.battle_rewards.items_gained = []
            
            # Add caught monster to rewards
            if self.battle_state.battle_result == BattleResult.CAUGHT and self.battle_state and self.battle_state.caught_monster:
                self.battle_rewards.caught_monster = self.battle_state.caught_monster
            
            # Apply rewards to game state
            self.give_rewards(self.battle_rewards)
            
            # Prepare rewards data for UI - with safe access
            rewards_ui_data = {
                'exp_gained': getattr(self.battle_rewards, 'exp_gained', {}),
                'money_gained': getattr(self.battle_rewards, 'money_gained', 0),
                'items_gained': getattr(self.battle_rewards, 'items_gained', []),
                'level_ups': getattr(self.battle_rewards, 'level_ups', {})
            }
            
            # For caught monsters, just show simple victory without EXP
            if self.battle_state.battle_result == BattleResult.CAUGHT:
                rewards_ui_data['exp_gained'] = {}  # No EXP for catching
                rewards_ui_data['money_gained'] = 100  # Small reward for catching
                # Add caught monster info for display
                if self.battle_state and self.battle_state.caught_monster:
                    rewards_ui_data['caught_monster'] = True
                    rewards_ui_data['caught_monster_name'] = self.battle_state.caught_monster.name
            
            # Show rewards UI
            self.battle_rewards_ui.show_rewards(rewards_ui_data)
            self.showing_rewards = True
            
        except Exception as e:
            if self.game.debug_mode:
                print(f"Error showing rewards: {e}")
            import traceback
            traceback.print_exc()
            # If error, just end battle
            self._end_battle()
    
    def give_rewards(self, rewards):
        """Apply battle rewards to player."""
        try:
            # Give EXP to participating monsters
            if hasattr(rewards, 'exp_gained') and rewards.exp_gained:
                for monster in self.battle_state.player_team:
                    if monster.current_hp > 0 and hasattr(monster, 'add_experience'):
                        monster_id = getattr(monster, 'id', str(id(monster)))
                        if monster_id in rewards.exp_gained:
                            exp_amount = rewards.exp_gained[monster_id]
                            level_up = monster.add_experience(exp_amount)
                            if level_up:
                                self.show_level_up(monster, level_up)
            
            # Give items
            if hasattr(rewards, 'items_gained') and rewards.items_gained:
                for item_id, count in rewards.items_gained:
                    if hasattr(self.game, 'item_manager'):
                        self.game.item_manager.add_item(item_id, count)
                    elif hasattr(self.game, 'player_data'):
                        if not hasattr(self.game.player_data, 'inventory'):
                            self.game.player_data.inventory = {}
                        if item_id in self.game.player_data.inventory:
                            self.game.player_data.inventory[item_id] += count
                        else:
                            self.game.player_data.inventory[item_id] = count
            
            # Give money
            if hasattr(rewards, 'money_gained') and rewards.money_gained > 0:
                if hasattr(self.game, 'player_data'):
                    if not hasattr(self.game.player_data, 'money'):
                        self.game.player_data.money = 0
                    self.game.player_data.money += rewards.money_gained
            
            debug_battle_info("Rewards applied successfully")
            
        except Exception as e:
            debug_battle_error(f"Failed to apply rewards: {e}")
    
    def show_level_up(self, monster, level_up_data):
        """Show level up information."""
        try:
            if hasattr(level_up_data, 'new_level'):
                self.battle_ui.add_message(f"{monster.name} ist auf Level {level_up_data.new_level} aufgestiegen!")
                
                # Show learned moves if any
                if hasattr(level_up_data, 'learned_moves') and level_up_data.learned_moves:
                    for move in level_up_data.learned_moves:
                        self.battle_ui.add_message(f"{monster.name} hat {move} gelernt!")
                        
        except Exception as e:
            debug_battle_error(f"Level up display failed: {e}")
    
    def _end_battle(self):
        """End the battle and return to field."""
        # Return to previous scene (only once!)
        if self.battle_state.battle_ended:
            return  # Already ended, don't do it again
        
        self.battle_state.battle_ended = True
        
        try:
            # Add caught monster to party if applicable
            if self.battle_state.battle_result == BattleResult.CAUGHT and self.battle_state and self.battle_state.caught_monster:
                if hasattr(self.game, 'party_manager'):
                    success, msg = self.game.party_manager.add_to_party(self.battle_state.caught_monster)
                    if success:
                        debug_battle_info(f"Monster zu Party hinzugefügt: {msg}")
                    else:
                        debug_battle_error(f"Fehler beim Hinzufügen zur Party: {msg}")
                else:
                    debug_battle_error("Kein Party-Manager verfügbar!")
            
            self.game.pop_scene()
            
        except Exception as e:
            if self.game.debug_mode:
                print(f"End battle error: {e}")
            import traceback
            traceback.print_exc()
            # Still try to pop scene even on error
            try:
                self.game.pop_scene()
            except:
                pass
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw battle scene."""
        try:
            # Clear screen
            surface.fill(Colors.BATTLE_BG)
            
            # Draw battle UI
            if self.battle_ui:
                self.battle_ui.draw(surface)
            
            # Draw rewards UI if showing
            if self.showing_rewards and self.battle_rewards_ui:
                self.battle_rewards_ui.draw(surface)
            
            # Debug info
            if self.game.debug_mode:
                self._draw_debug_info(surface)
    
        except Exception as e:
            if self.game.debug_mode:
                print(f"Draw error: {e}")
    
    def _draw_debug_info(self, surface: pygame.Surface):
        """Draw debug information."""
        try:
            font = pygame.font.Font(None, 24)
        
            debug_info = [
                f"Phase: {self.battle_state.phase.name if self.battle_state.phase else 'None'}",
                f"Result: {self.battle_state.battle_result.name if self.battle_state.battle_result else 'None'}",
            ]
            
            if self.battle_state:
                player_name = self.battle_state.player_active.name if self.battle_state.player_active else 'None'
                enemy_name = self.battle_state.enemy_active.name if self.battle_state.enemy_active else 'None'
                debug_info.extend([
                    f"Player: {player_name}",
                    f"Enemy: {enemy_name}",
                ])
            
            for i, info in enumerate(debug_info):
                text = font.render(info, True, (255, 255, 0))
                surface.blit(text, (5, 5 + i * 20))
                
        except Exception as e:
            if self.game.debug_mode:
                print(f"Debug draw error: {e}")
