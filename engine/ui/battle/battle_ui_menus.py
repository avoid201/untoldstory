"""
Battle UI Menu Manager - Menu-spezifische Logic für modulare Battle UI
Zerlegt aus der monolithischen battle_ui.py

Verantwortlichkeiten:
- Menu State Management
- Menu Transitions
- Menu-specific Logic
- Enhanced Menu Components
"""

import logging
import time
from typing import List, Dict, Any

# Setup logger
logger = logging.getLogger(__name__)

# Import modular components
from .battle_ui_state import BattleMenuState


class BattleUIMenuManager:
    """
    Menu Manager für Battle UI.
    
    Verantwortlich für Menu State Management und Transitions.
    """
    
    def __init__(self, battle_ui):
        """Initialisiere Menu Manager mit Battle UI Referenz."""
        self.battle_ui = battle_ui
        
        # Menu state
        self.current_menu = None
        self.menu_stack = []
        
        # Transition state
        self.transition_start = 0
        self.transition_duration = 0
        self.transition_from = None
        self.transition_to = None
        
        logger.info("Battle UI Menu Manager initialized")
    
    def update(self, dt):
        """Update Menu Manager."""
        # Update current menu
        if self.current_menu:
            if hasattr(self.current_menu, 'update'):
                self.current_menu.update(dt)
    
    def show_main_menu(self):
        """Zeige Hauptmenü."""
        self.current_menu = None
        self.battle_ui.current_menu_state = BattleMenuState.MAIN
        self.battle_ui.selected_option = 0
    
    def show_move_menu(self):
        """Zeige Talent-basiertes Move-Menü."""
        self.current_menu = None
        self.battle_ui.current_menu_state = BattleMenuState.MOVE_SELECT
        self.battle_ui.selected_move = 0
        logger.debug("Talent-based move menu shown")
    
    def show_item_menu(self):
        """Zeige Item-Menü."""
        self.current_menu = None
        self.battle_ui.current_menu_state = BattleMenuState.ITEM_SELECT
        self.battle_ui.selected_item = 0
    
    def show_team_menu(self):
        """Zeige Team-Menü."""
        self.current_menu = None
        self.battle_ui.current_menu_state = BattleMenuState.SWITCH_SELECT
        self.battle_ui.selected_team_member = 0
    
    def show_meat_menu(self):
        """Zeige Meat-Menü."""
        self.current_menu = None
        self.battle_ui.current_menu_state = BattleMenuState.TAME_MEAT
        self.battle_ui.selected_item = 0
    
    def show_tame_confirm_menu(self):
        """Zeige Tame-Confirm-Menü."""
        self.current_menu = None
        self.battle_ui.current_menu_state = BattleMenuState.TAME_CONFIRM
        self.battle_ui.selected_option = 0
    
    def show_scout_display(self):
        """Zeige Scout Display."""
        self.current_menu = None
        self.battle_ui.current_menu_state = BattleMenuState.SCOUT
    
    def show_message_display(self):
        """Zeige Message Display."""
        self.current_menu = None
        self.battle_ui.current_menu_state = BattleMenuState.MESSAGE
    
    def go_back(self):
        """Gehe zurück zum vorherigen Menü."""
        if self.menu_stack:
            previous_menu = self.menu_stack.pop()
            self.current_menu = previous_menu
        else:
            self.show_main_menu()
    
    def push_menu(self, menu):
        """Füge Menü zum Stack hinzu."""
        if self.current_menu:
            self.menu_stack.append(self.current_menu)
        self.current_menu = menu
    
    def pop_menu(self):
        """Entferne aktuelles Menü vom Stack."""
        if self.menu_stack:
            self.current_menu = self.menu_stack.pop()
        else:
            self.current_menu = None
    
    def reset(self):
        """Reset Menu Manager."""
        self.current_menu = None
        self.menu_stack.clear()
    
    def get_current_menu(self):
        """Hole aktuelles Menü."""
        return self.current_menu
    
    def is_menu_active(self):
        """Prüfe ob Menü aktiv ist."""
        return self.current_menu is not None
    
    def get_items_for_category(self, category: str) -> Dict[str, int]:
        """
        Get items for a specific category.
        
        Args:
            category: Item category name
            
        Returns:
            Dictionary of item_name -> count
        """
        if not hasattr(self.battle_ui, 'demo_inventory'):
            logger.debug(f"No inventory available for category {category}")
            return {}
        
        # Define item categories
        category_items = {
            "HEILUNG": ["Kräuter", "Starkkräuter", "Antidot", "Vollheilung"],
            "KAMPF-ITEMS": ["Kraftpulver", "Eisenpulver", "X-Angriff", "X-Verteidigung"],
            "FLEISCH": ["Fleisch", "Edelfleisch", "Götterfleisch"],
            "FANG-ITEMS": ["Fangball", "Superfangball", "Hyperfangball"],
            "SONSTIGE": ["Fluchtseil", "Rauchball", "Heilfeder"]
        }
        
        # Get items for category
        items = {}
        item_list = category_items.get(category, [])
        
        for item_name in item_list:
            count = self.battle_ui.demo_inventory.get(item_name, 0)
            if count > 0:
                items[item_name] = count
                logger.debug(f"Found {item_name} x{count} in category {category}")
        
        return items
    
    def get_moves_by_category(self, moves: List, category: str) -> List:
        """
        Filter moves by category.
        
        Args:
            moves: List of Move objects
            category: Category to filter by (PHYSISCH, MAGISCH, STATUS)
            
        Returns:
            Filtered list of moves
        """
        if not moves:
            return []
        
        filtered_moves = []
        for move in moves:
            # Determine move category based on move properties
            move_category = self._get_move_category(move)
            
            if move_category == category:
                filtered_moves.append(move)
                logger.debug(f"Move {move.name} matches category {category}")
        
        return filtered_moves
    
    def _get_move_category(self, move) -> str:
        """
        Determine category of a move - OPTIMIZED mit direkter Talent-System Integration.
        
        Args:
            move: Move object
            
        Returns:
            Category string (PHYSISCH, MAGISCH, STATUS)
        """
        try:
            # PRIORITY 1: Use Talent-System directly for accurate categorization
            if hasattr(move, 'category_string'):
                # Use the optimized category_string from Move class
                category = move.category_string.upper()
                if category == "PHYSICAL":
                    return "PHYSISCH"
                elif category == "MAGICAL":
                    return "MAGISCH"
                elif category == "STATUS":
                    return "STATUS"
            
            # PRIORITY 2: Check move.category from Talent-System
            if hasattr(move, 'category'):
                if hasattr(move.category, 'value'):
                    # MoveCategory enum
                    category_value = move.category.value.upper()
                    if category_value in ['PHYS', 'PHYSICAL']:
                        return "PHYSISCH"
                    elif category_value in ['MAG', 'MAGICAL']:
                        return "MAGISCH"
                    elif category_value in ['SUPPORT', 'STATUS']:
                        return "STATUS"
                elif isinstance(move.category, str):
                    # String category
                    category_upper = move.category.upper()
                    if category_upper in ['PHYS', 'PHYSICAL']:
                        return "PHYSISCH"
                    elif category_upper in ['MAG', 'MAGICAL']:
                        return "MAGISCH"
                    elif category_upper in ['SUPPORT', 'STATUS']:
                        return "STATUS"
            
            # PRIORITY 3: Load from Talent-Database as fallback
            try:
                from engine.systems.talent_system import get_talent_database
                talent_db = get_talent_database()
                
                # Try to find move in talent database
                for talent in talent_db.talents.values():
                    for talent_move in talent.moves:
                        if talent_move.move_id == move.id:
                            # Use talent category for move categorization
                            if talent.category.value == 'PHYSICAL':
                                return "PHYSISCH"
                            elif talent.category.value == 'ELEMENTAL':
                                return "MAGISCH"
                            elif talent.category.value in ['HEALING', 'SUPPORT']:
                                return "STATUS"
                            break
            except Exception as e:
                logger.debug(f"Talent database lookup failed: {e}")
            
            # PRIORITY 4: Check move properties for DQM-style categorization
            if hasattr(move, 'power'):
                if move.power == 0:
                    return "STATUS"
                elif hasattr(move, 'is_physical'):
                    return "PHYSISCH" if move.is_physical else "MAGISCH"
                else:
                    # DQM Type-based categorization
                    move_type = getattr(move, 'type', 'normal').lower()
                    physical_types = ["feuer", "wasser", "erde", "luft", "pflanze", "bestie"]
                    magical_types = ["energie", "chaos", "seuche", "mystisch", "gottheit", "teufel"]
                    
                    if move_type in physical_types:
                        return "PHYSISCH"
                    elif move_type in magical_types:
                        return "MAGISCH"
            
            # PRIORITY 5: Fallback based on move name patterns
            move_name = getattr(move, 'name', '').lower()
            if any(keyword in move_name for keyword in ['heal', 'cure', 'buff', 'debuff', 'status']):
                return "STATUS"
            elif any(keyword in move_name for keyword in ['punch', 'kick', 'strike', 'slash', 'claw']):
                return "PHYSISCH"
            elif any(keyword in move_name for keyword in ['blast', 'beam', 'wave', 'magic', 'spell']):
                return "MAGISCH"
            
            # Default fallback
            return "STATUS"
            
        except Exception as e:
            logger.error(f"Error determining move category: {e}")
            return "STATUS"
    
    def validate_menu_state(self) -> bool:
        """
        Validate current menu state.
        
        Returns:
            True if menu state is valid
        """
        try:
            # Check if battle_ui exists
            if not self.battle_ui:
                logger.error("No battle_ui reference")
                return False
            
            # Check if we have a valid menu state
            if not hasattr(self.battle_ui, 'current_menu_state'):
                logger.error("No current_menu_state in battle_ui")
                return False
            
            # Validate state-specific requirements
            state = self.battle_ui.current_menu_state
            
            if state == BattleMenuState.MOVE_SELECT:
                if not self.battle_ui.battle_state or not self.battle_ui.battle_state.player_active:
                    logger.warning("Move select requires active player")
                    return False
            
            elif state == BattleMenuState.ITEM_SELECT:
                if not hasattr(self.battle_ui, 'demo_inventory'):
                    logger.warning("Item select requires inventory")
                    return False
            
            elif state == BattleMenuState.SWITCH_SELECT:
                if not self.battle_ui.battle_state or not self.battle_ui.battle_state.player_team:
                    logger.warning("Switch select requires player team")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Menu state validation error: {e}")
            return False
    
    def transition_to_menu(self, target_menu: BattleMenuState, transition_time: float = 0.2) -> None:
        """
        Smoothly transition to a new menu state.
        
        Args:
            target_menu: Target menu state
            transition_time: Transition duration in seconds
        """
        try:
            # Store transition info
            self.transition_start = time.time() if hasattr(time, 'time') else 0
            self.transition_duration = transition_time
            self.transition_from = self.battle_ui.current_menu_state
            self.transition_to = target_menu
            
            # Start transition
            logger.info(f"Menu transition: {self.transition_from} -> {target_menu}")
            
            # Set new state after storing transition info
            self.battle_ui.current_menu_state = target_menu
            
            # Reset selection indices
            if target_menu == BattleMenuState.MAIN:
                self.battle_ui.selected_option = 0
            elif target_menu == BattleMenuState.MOVE_SELECT:
                self.battle_ui.selected_move = 0
            elif target_menu == BattleMenuState.ITEM_SELECT:
                self.battle_ui.selected_item = 0
            elif target_menu == BattleMenuState.SWITCH_SELECT:
                self.battle_ui.selected_team_member = 0
                
        except Exception as e:
            logger.error(f"Menu transition error: {e}")
            # Fallback: direct state change
            self.battle_ui.current_menu_state = target_menu
    
    def get_menu_options(self, menu_state: BattleMenuState) -> List[str]:
        """
        Get available options for a menu state.
        
        Args:
            menu_state: Current menu state
            
        Returns:
            List of option strings
        """
        options_map = {
            BattleMenuState.MAIN: ["ATTACKE", "ITEM", "WECHSEL", "ZÄHMEN", "SPÄHEN", "FLUCHT"],
            BattleMenuState.MOVE_SELECT: [],  # Dynamic based on moves
            BattleMenuState.ITEM_SELECT: [],  # Dynamic based on items
            BattleMenuState.SWITCH_SELECT: [],  # Dynamic based on team
            BattleMenuState.TAME_MEAT: ["Fleisch", "Edelfleisch", "Götterfleisch", "Kein Fleisch"],
            BattleMenuState.TAME_CONFIRM: ["Zähmen versuchen", "Abbrechen"],
            BattleMenuState.SCOUT: ["Zurück"],
            BattleMenuState.MESSAGE: []
        }
        
        base_options = options_map.get(menu_state, [])
        
        # Add dynamic options for specific menus
        if menu_state == BattleMenuState.MOVE_SELECT:
            if self.battle_ui.battle_state and self.battle_ui.battle_state.player_active:
                monster = self.battle_ui.battle_state.player_active
                if hasattr(monster, 'moves'):
                    base_options = [move.name for move in monster.moves]
        
        elif menu_state == BattleMenuState.ITEM_SELECT:
            all_items = []
            for category in ["HEILUNG", "KAMPF-ITEMS", "FLEISCH"]:
                items = self.get_items_for_category(category)
                all_items.extend(items.keys())
            base_options = all_items
        
        elif menu_state == BattleMenuState.SWITCH_SELECT:
            if self.battle_ui.battle_state and self.battle_ui.battle_state.player_team:
                base_options = [m.name for m in self.battle_ui.battle_state.player_team]
        
        return base_options
    
    def get_talent_moves(self, monster) -> List[Dict[str, Any]]:
        """
        Hole Talent-basierte Moves für ein Monster.
        
        Args:
            monster: MonsterInstance mit Talenten
            
        Returns:
            List of talent move dictionaries
        """
        if not monster or not hasattr(monster, 'talents'):
            return []
        
        talent_moves = []
        
        try:
            from engine.systems.talent_system import get_talent_database
            talent_db = get_talent_database()
            
            for talent_instance in monster.talents:
                if talent_instance.is_learned:
                    talent = talent_db.get_talent(talent_instance.talent_id)
                    if talent:
                        # Hole Moves für aktuelles Talent-Tier
                        moves_for_tier = talent.get_moves_for_tier(
                            talent_instance.current_tier, 
                            monster.level
                        )
                        
                        for move_id in moves_for_tier:
                            move = talent_db._create_move_from_id(move_id)
                            if move:
                                talent_moves.append({
                                    'move': move,
                                    'talent_id': talent.id,
                                    'talent_name': talent.name,
                                    'tier': talent_instance.current_tier.value,
                                    'tier_stars': '★' * talent_instance.current_tier.value,
                                    'category': self._get_move_category(move),
                                    'is_talent_move': True
                                })
            
            # Sortiere nach Talent-Tier und Name
            talent_moves.sort(key=lambda x: (x['tier'], x['move'].name))
            
        except Exception as e:
            logger.error(f"Error getting talent moves: {e}")
        
        return talent_moves
    
    def get_talent_categories(self, talent_moves: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Gruppiere Talent-Moves nach Kategorien.
        
        Args:
            talent_moves: List of talent move dictionaries
            
        Returns:
            Dictionary of category -> moves
        """
        categories = {
            "PHYSISCH": [],
            "MAGISCH": [],
            "STATUS": []
        }
        
        for move_data in talent_moves:
            category = move_data['category']
            if category in categories:
                categories[category].append(move_data)
        
        return categories
    
    def get_talent_passive_abilities(self, monster) -> List[Dict[str, Any]]:
        """
        Hole passive Fähigkeiten aus Talenten.
        
        Args:
            monster: MonsterInstance mit Talenten
            
        Returns:
            List of passive ability dictionaries
        """
        if not monster or not hasattr(monster, 'talents'):
            return []
        
        passive_abilities = []
        
        try:
            from engine.systems.talent_system import get_talent_database
            talent_db = get_talent_database()
            
            for talent_instance in monster.talents:
                if talent_instance.is_learned:
                    talent = talent_db.get_talent(talent_instance.talent_id)
                    if talent:
                        # Hole passive Fähigkeiten für aktuelles Talent-Tier
                        abilities = talent.get_passive_abilities_for_tier(talent_instance.current_tier)
                        for ability in abilities:
                            passive_abilities.append({
                                'name': ability['name'],
                                'description': ability['description'],
                                'effect_type': ability['effect_type'],
                                'value': ability['value'],
                                'talent_name': talent.name,
                                'tier': talent_instance.current_tier.value,
                                'tier_stars': '★' * talent_instance.current_tier.value
                            })
            
        except Exception as e:
            logger.error(f"Error getting passive abilities: {e}")
        
        return passive_abilities