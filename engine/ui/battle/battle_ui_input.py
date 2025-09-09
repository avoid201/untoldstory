"""
Battle UI Input Handler - Input handling für modulare Battle UI
Zerlegt aus der monolithischen battle_ui.py

Verantwortlichkeiten:
- Input handling für alle Menüs
- Action processing
- Input validation
- Event delegation
"""

import logging
from typing import Dict

# Setup logger
logger = logging.getLogger(__name__)

# Import modular components
from .battle_ui_state import BattleMenuState


class BattleUIInputHandler:
    """
    Input Handler für Battle UI.
    
    Verantwortlich für alle Input-Verarbeitung und Action-Erstellung.
    """
    
    def __init__(self, battle_ui):
        """Initialisiere Input Handler mit Battle UI Referenz."""
        self.battle_ui = battle_ui
        
        logger.info("Battle UI Input Handler initialized")
    
    def update(self, dt):
        """Update Input Handler."""
        # Input handler doesn't need continuous updates
        pass
    
    def handle_input(self, action, battle_state=None):
        """Enhanced input handler with proper action creation and phase validation."""
        if not action:
            return None
        
        # Update state
        if battle_state:
            self.battle_ui.battle_state = battle_state
        
        # CRITICAL: Check if UI is waiting for input
        if not self.battle_ui.waiting_for_input:
            logger.debug("Input ignored - UI not waiting for input")
            return None
        
        # CRITICAL: Check battle phase
        if self.battle_ui.battle_state and hasattr(self.battle_ui.battle_state, 'phase'):
            current_phase = self.battle_ui.battle_state.phase
            if current_phase and current_phase.name not in ['INPUT', 'START']:
                logger.debug(f"Input ignored - wrong phase: {current_phase.name}")
                return None
        
        # Route to handler
        result = None
        if self.battle_ui.current_menu_state == BattleMenuState.MAIN:
            result = self.handle_main_menu_input(action)
        elif self.battle_ui.current_menu_state == BattleMenuState.MOVE_SELECT:
            result = self.handle_move_menu_input(action)
        elif self.battle_ui.current_menu_state == BattleMenuState.ITEM_SELECT:
            result = self.handle_item_menu_input(action)
        elif self.battle_ui.current_menu_state == BattleMenuState.SWITCH_SELECT:
            result = self.handle_switch_menu_input(action)
        elif self.battle_ui.current_menu_state == BattleMenuState.TAME_MEAT:
            result = self.handle_meat_menu_input(action)
        elif self.battle_ui.current_menu_state == BattleMenuState.TAME_CONFIRM:
            result = self.handle_tame_confirm_input(action)
        elif self.battle_ui.current_menu_state == BattleMenuState.SCOUT:
            result = self.handle_scout_input(action)
        elif self.battle_ui.current_menu_state == BattleMenuState.MESSAGE:
            result = self.handle_message_input(action)
        
        # If we have a result, queue it
        if result and isinstance(result, dict):
            # Ensure proper action format
            if 'type' not in result and 'action' in result:
                result['type'] = result['action']
            
            # Set actor/target from battle state if not present
            if 'actor' not in result or result['actor'] == 'player':
                result['actor'] = self.battle_ui.battle_state.player_active
            if 'target' not in result or result['target'] == 'enemy':
                result['target'] = self.battle_ui.battle_state.enemy_active
            
            # Queue the action atomisch
            self.battle_ui.queue_action(result)
            
            logger.info(f"Input produced action: {result.get('type', 'unknown')}")
        
        return result
    
    def handle_main_menu_input(self, action):
        """Handle Hauptmenü Input."""
        if action == "up":
            self.battle_ui.selected_option = (self.battle_ui.selected_option - 1) % 6
            return True  # Input handled
        elif action == "down":
            self.battle_ui.selected_option = (self.battle_ui.selected_option + 1) % 6
            return True  # Input handled
        elif action == "confirm":
            return self.process_main_menu_selection()
        elif action == "cancel":
            # No cancel in main menu
            pass
        
        return None
    
    def process_main_menu_selection(self):
        """Process main menu selection."""
        options = ["ATTACKE", "ITEM", "WECHSEL", "ZÄHMEN", "SPÄHEN", "FLUCHT"]
        selected_option = options[self.battle_ui.selected_option]
        
        if selected_option == "ATTACKE":
            self.battle_ui.current_menu_state = BattleMenuState.MOVE_SELECT
            self.battle_ui.selected_move = 0
            return True  # Input handled
        
        elif selected_option == "ITEM":
            self.battle_ui.current_menu_state = BattleMenuState.ITEM_SELECT
            self.battle_ui.selected_item = 0
            return True  # Input handled
        
        elif selected_option == "WECHSEL":
            self.battle_ui.current_menu_state = BattleMenuState.SWITCH_SELECT
            self.battle_ui.selected_team_member = 0
            return True  # Input handled
        
        elif selected_option == "ZÄHMEN":
            # Check if this is a wild battle
            if self.battle_ui.battle_state and self.battle_ui.battle_state.enemy_team:
                enemy = self.battle_ui.battle_state.enemy_active
                if enemy and getattr(enemy, 'is_wild', True):
                    self.battle_ui.current_menu_state = BattleMenuState.TAME_MEAT
                    self.battle_ui.selected_item = 0
                    return True  # Input handled
                else:
                    self.battle_ui.add_message("Dieses Monster kann nicht gezähmt werden!")
                    return True  # Input handled
            else:
                self.battle_ui.add_message("Kein Monster zum Zähmen verfügbar!")
                return True  # Input handled
        
        elif selected_option == "SPÄHEN":
            if self.battle_ui.battle_state and self.battle_ui.battle_state.enemy_active:
                # CRITICAL: Return complete scout action
                return {
                    "type": "scout",
                    "actor": self.battle_ui.battle_state.player_active,
                    "target": self.battle_ui.battle_state.enemy_active
                }
            else:
                self.battle_ui.add_message("Kein Monster zum Spähen verfügbar!")
                return True  # Input handled
        
        elif selected_option == "FLUCHT":
            # CRITICAL: Return complete flee action with objects
            return {
                "type": "flee",
                "actor": self.battle_ui.battle_state.player_active if self.battle_ui.battle_state else None,
                "target": None
            }
        
        return None
    
    def handle_move_menu_input(self, action):
        """Handle Move-Menü Input."""
        if action == "up":
            self.battle_ui.selected_move = max(0, self.battle_ui.selected_move - 1)
            return True  # Input handled
        elif action == "down":
            # Get total number of moves
            total_moves = self.get_total_moves_count()
            self.battle_ui.selected_move = min(total_moves - 1, self.battle_ui.selected_move + 1)
            return True  # Input handled
        elif action == "confirm":
            return self.process_move_selection()
        elif action == "cancel":
            self.battle_ui.current_menu_state = BattleMenuState.MAIN
            self.battle_ui.selected_option = 0
            return True  # Input handled
        
        return None
    
    def get_total_moves_count(self):
        """Hole Gesamtanzahl verfügbarer Moves."""
        if not self.battle_ui.battle_state or not self.battle_ui.battle_state.player_active:
            return 0
        
        monster = self.battle_ui.battle_state.player_active
        return len(monster.moves)
    
    def process_move_selection(self):
        """Process move selection with complete action dict."""
        if not self.battle_ui.battle_state or not self.battle_ui.battle_state.player_active:
            logger.warning("No battle state or active player for move selection")
            return True  # Input handled
        
        monster = self.battle_ui.battle_state.player_active
        moves = monster.moves if hasattr(monster, 'moves') else []
        
        if not moves or self.battle_ui.selected_move >= len(moves):
            logger.warning(f"Invalid move selection: {self.battle_ui.selected_move}")
            return True  # Input handled
        
        selected_move = moves[self.battle_ui.selected_move]
        
        # Check MP cost
        if hasattr(selected_move, 'mp_cost') and hasattr(monster, 'current_mp'):
            if monster.current_mp < selected_move.mp_cost:
                self.battle_ui.add_message(f"Nicht genug MP für {selected_move.name}!")
                return True  # Input handled
        
        # CRITICAL: Return complete action with OBJECTS not strings
        action = {
            "type": "attack",
            "actor": monster,  # Pass MonsterInstance object
            "move": selected_move,  # Pass Move object
            "target": self.battle_ui.battle_state.enemy_active  # Pass MonsterInstance object
        }
        
        logger.info(f"Move action created: {selected_move.name} by {monster.name}")
        return action
    
    def handle_item_menu_input(self, action):
        """Handle Item-Menü Input."""
        if action == "up":
            self.battle_ui.selected_item = max(0, self.battle_ui.selected_item - 1)
            return True  # Input handled
        elif action == "down":
            # Get total number of items
            total_items = self.get_total_items_count()
            self.battle_ui.selected_item = min(total_items - 1, self.battle_ui.selected_item + 1)
            return True  # Input handled
        elif action == "confirm":
            return self.process_item_selection()
        elif action == "cancel":
            self.battle_ui.current_menu_state = BattleMenuState.MAIN
            self.battle_ui.selected_option = 1  # ITEM option
            return True  # Input handled
        
        return None
    
    def get_total_items_count(self):
        """Hole Gesamtanzahl verfügbarer Items."""
        if not hasattr(self.battle_ui, 'demo_inventory'):
            return 0
        
        total = 0
        for category in ["HEILUNG", "KAMPF-ITEMS", "FLEISCH"]:
            items = self.battle_ui.menu_manager.get_items_for_category(category)
            total += len(items)
        
        return total
    
    def process_item_selection(self):
        """Process item selection with complete action dict."""
        if not hasattr(self.battle_ui, 'demo_inventory'):
            logger.warning("No inventory available")
            return None
        
        # Find selected item
        current_index = 0
        selected_item = None
        selected_category = None
        
        for category in ["HEILUNG", "KAMPF-ITEMS", "FLEISCH"]:
            items = self.battle_ui.menu_manager.get_items_for_category(category)
            for item_name, count in items.items():
                if current_index == self.battle_ui.selected_item:
                    selected_item = item_name
                    selected_category = category
                    break
                current_index += 1
            if selected_item:
                break
        
        if not selected_item:
            logger.warning("No item selected")
            return None
        
        # Check if item is available
        if self.battle_ui.demo_inventory.get(selected_item, 0) <= 0:
            self.battle_ui.add_message(f"{selected_item} nicht verfügbar!")
            return None
        
        # Determine target based on item category
        if selected_category == "HEILUNG":
            target = self.battle_ui.battle_state.player_active
        elif selected_category == "KAMPF-ITEMS":
            target = self.battle_ui.battle_state.enemy_active
        else:
            target = self.battle_ui.battle_state.player_active
        
        # CRITICAL: Return complete action with proper objects
        action = {
            "type": "item",
            "actor": self.battle_ui.battle_state.player_active,  # MonsterInstance
            "item_id": selected_item,  # Item ID string
            "item": selected_item,  # Item name for compatibility
            "target": target,  # MonsterInstance
            "category": selected_category  # For processing
        }
        
        logger.info(f"Item action created: {selected_item} targeting {target.name if target else 'None'}")
        return action
    
    def handle_switch_menu_input(self, action):
        """Handle Switch-Menü Input."""
        if action == "up":
            if self.battle_ui.battle_state and self.battle_ui.battle_state.player_team:
                max_team = len(self.battle_ui.battle_state.player_team) - 1
                if max_team > 0:  # Only navigate if there are multiple team members
                    self.battle_ui.selected_team_member = max(0, self.battle_ui.selected_team_member - 1)
                    return True  # Input handled
        elif action == "down":
            if self.battle_ui.battle_state and self.battle_ui.battle_state.player_team:
                max_team = len(self.battle_ui.battle_state.player_team) - 1
                if max_team > 0:  # Only navigate if there are multiple team members
                    self.battle_ui.selected_team_member = min(max_team, self.battle_ui.selected_team_member + 1)
                    return True  # Input handled
        elif action == "confirm":
            return self.process_switch_selection()
        elif action == "cancel":
            self.battle_ui.current_menu_state = BattleMenuState.MAIN
            self.battle_ui.selected_option = 2  # WECHSEL option
            return True  # Input handled
        
        return None
    
    def process_switch_selection(self):
        """Process switch selection with complete action dict."""
        if not self.battle_ui.battle_state or not self.battle_ui.battle_state.player_team:
            logger.warning("No battle state or player team")
            return None
        
        if self.battle_ui.selected_team_member >= len(self.battle_ui.battle_state.player_team):
            logger.warning(f"Invalid team member selection: {self.battle_ui.selected_team_member}")
            return None
        
        selected_monster = self.battle_ui.battle_state.player_team[self.battle_ui.selected_team_member]
        current_active = self.battle_ui.battle_state.player_active
        
        # Check if monster is already active
        if selected_monster == current_active:
            self.battle_ui.add_message("Dieses Monster ist bereits aktiv!")
            return None
        
        # Check if monster is fainted
        if selected_monster.current_hp <= 0:
            self.battle_ui.add_message("Dieses Monster ist ohnmächtig!")
            return None
        
        # CRITICAL: Return complete action with objects
        action = {
            "type": "switch",
            "actor": current_active,  # Current MonsterInstance
            "switch_to": selected_monster,  # Target MonsterInstance
            "monster_index": self.battle_ui.selected_team_member  # For compatibility
        }
        
        logger.info(f"Switch action created: {current_active.name} -> {selected_monster.name}")
        return action
    
    def handle_meat_menu_input(self, action):
        """Handle Meat-Menü Input."""
        if action == "up":
            self.battle_ui.selected_item = max(0, self.battle_ui.selected_item - 1)
            return True  # Input handled
        elif action == "down":
            self.battle_ui.selected_item = min(3, self.battle_ui.selected_item + 1)  # 4 meat options
            return True  # Input handled
        elif action == "confirm":
            return self.process_meat_selection()
        elif action == "cancel":
            self.battle_ui.current_menu_state = BattleMenuState.MAIN
            self.battle_ui.selected_option = 3  # ZÄHMEN option
            return True  # Input handled
        
        return None
    
    def process_meat_selection(self):
        """Verarbeite Meat-Auswahl."""
        meat_options = [
            ("Fleisch", 20),
            ("Edelfleisch", 40),
            ("Götterfleisch", 80),
            ("Kein Fleisch", 0)
        ]
        
        if self.battle_ui.selected_item >= len(meat_options):
            return None
        
        meat_name, bonus = meat_options[self.battle_ui.selected_item]
        
        # Check if meat is available (except "Kein Fleisch")
        if meat_name != "Kein Fleisch":
            if self.battle_ui.demo_inventory.get(meat_name, 0) <= 0:
                self.battle_ui.add_message(f"{meat_name} nicht verfügbar!")
                return None
        
        # Create meat action
        return {
            "type": "use_meat",
            "actor": "player",
            "meat": meat_name,
            "bonus": bonus
        }
    
    def handle_tame_confirm_input(self, action):
        """Handle Tame-Confirm Input."""
        if action == "up":
            self.battle_ui.selected_option = 0
            return True  # Input handled
        elif action == "down":
            self.battle_ui.selected_option = 1
            return True  # Input handled
        elif action == "confirm":
            if self.battle_ui.selected_option == 0:  # "Zähmen versuchen"
                return self.process_tame_attempt()
            else:  # "Abbrechen"
                self.battle_ui.current_menu_state = BattleMenuState.MAIN
                self.battle_ui.selected_option = 3  # ZÄHMEN option
                return True  # Input handled
        elif action == "cancel":
            self.battle_ui.current_menu_state = BattleMenuState.MAIN
            self.battle_ui.selected_option = 3  # ZÄHMEN option
            return True  # Input handled
        
        return None
    
    def process_tame_attempt(self):
        """Process tame attempt with complete action dict."""
        if not self.battle_ui.battle_state or not self.battle_ui.battle_state.enemy_active:
            logger.warning("No enemy to tame")
            return None
        
        # Get meat bonus from previous selection
        meat_bonus = getattr(self.battle_ui, 'selected_meat_bonus', 0)
        
        # CRITICAL: Return complete tame action with objects
        action = {
            "type": "tame",
            "actor": self.battle_ui.battle_state.player_active,  # MonsterInstance
            "target": self.battle_ui.battle_state.enemy_active,  # MonsterInstance
            "meat_bonus": meat_bonus,
            "meat_type": getattr(self.battle_ui, 'selected_meat_type', None)
        }
        
        logger.info(f"Tame action created: targeting {action['target'].name}")
        return action
    
    def handle_scout_input(self, action):
        """Handle Scout Input."""
        if action == "confirm" or action == "cancel":
            self.battle_ui.current_menu_state = BattleMenuState.MAIN
            self.battle_ui.selected_option = 4  # SPÄHEN option
            return True  # Input handled
        
        return None
    
    def handle_message_input(self, action):
        """Handle Message Input."""
        if action == "confirm" or action == "cancel":
            # Check if there are more messages
            if self.battle_ui.message_queue:
                self.battle_ui._next_message()
            else:
                self.battle_ui.current_menu_state = BattleMenuState.MAIN
                self.battle_ui.waiting_for_input = True
            return True  # Input handled
        
        return None
    
    def validate_event_flow(self) -> Dict[str, bool]:
        """Validate that all critical events have handlers - ENHANCED."""
        critical_events = [
            "DAMAGE_DEALT",
            "HP_BAR_UPDATE", 
            "MESSAGE_SHOW",
            "TURN_START",
            "TURN_END",
            "PHASE_CHANGE",
            "HP_UPDATE",
            "MESSAGE",
            "DAMAGE",
            "STATUS_CHANGE",
            "HEALING",
            "MONSTER_FAINT",
            "MONSTER_SWITCH"
        ]
        
        validation = {}
        for event_name in critical_events:
            # Check if battle_ui has event processor
            has_processor = hasattr(self.battle_ui, 'event_processor')
            has_handlers = False
            
            if has_processor and self.battle_ui.event_processor:
                # Check if event processor has register_ui_handlers method
                if hasattr(self.battle_ui.event_processor, 'register_ui_handlers'):
                    has_handlers = True
                    logger.debug(f"✓ Event processor has UI handlers for {event_name}")
                else:
                    logger.warning(f"⚠️ Event processor missing register_ui_handlers method")
            else:
                logger.warning(f"⚠️ No event processor available for {event_name}")
            
            validation[event_name] = has_handlers
            if not has_handlers:
                logger.warning(f"⚠️ No handlers for critical event: {event_name}")
        
        # Additional validation: Check if UI has all required event handlers
        required_handlers = [
            '_handle_hp_update_event',
            '_handle_message_event', 
            '_handle_damage_event',
            '_handle_status_event',
            '_handle_healing_event',
            '_handle_faint_event',
            '_handle_switch_event'
        ]
        
        for handler_name in required_handlers:
            if hasattr(self.battle_ui, handler_name):
                validation[f"UI_{handler_name}"] = True
                logger.debug(f"✓ UI has {handler_name}")
            else:
                validation[f"UI_{handler_name}"] = False
                logger.warning(f"⚠️ UI missing {handler_name}")
        
        return validation

    def reset(self):
        """Reset Input Handler."""
        # Input handler doesn't have persistent state to reset
        pass