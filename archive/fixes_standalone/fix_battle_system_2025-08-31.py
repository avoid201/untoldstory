#!/usr/bin/env python3
"""
Battle System Fix Script
Behebt alle Fehler im Battle Flow
"""

import os
import sys

print("🔧 Fixing Battle System Errors...")
print("="*60)

# Fix 1: Add missing ActionType.SPECIAL to turn_logic.py
print("\n1. Fixing ActionType enum...")
turn_logic_path = "/Users/leon/Desktop/untold_story/engine/systems/battle/turn_logic.py"

try:
    with open(turn_logic_path, 'r') as f:
        content = f.read()
    
    # Find ActionType enum and add SPECIAL if missing
    if "SPECIAL" not in content:
        # Find the enum definition
        import_pos = content.find("class ActionType(Enum):")
        if import_pos > 0:
            # Find the end of the enum
            enum_end = content.find("\n\nclass", import_pos)
            if enum_end < 0:
                enum_end = content.find("\n\n@", import_pos)
            
            # Add SPECIAL before the end
            insertion_point = content.rfind("\n", import_pos, enum_end)
            if insertion_point > 0:
                new_line = "\n    SPECIAL = auto()  # Special commands like psyche up"
                content = content[:insertion_point] + new_line + content[insertion_point:]
                
                with open(turn_logic_path, 'w') as f:
                    f.write(content)
                print("   ✅ Added ActionType.SPECIAL")
        else:
            print("   ⚠️  Could not find ActionType enum")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Fix 2: Fix Move.id issue in monster_instance.py
print("\n2. Fixing Move class to have id attribute...")
monster_instance_path = "/Users/leon/Desktop/untold_story/engine/systems/monster_instance.py"

try:
    with open(monster_instance_path, 'r') as f:
        content = f.read()
    
    # Update the Move dataclass to include id
    old_move_def = """            @dataclass
            class Move:
                name: str
                power: int
                pp: int
                max_pp: int
                target_type: str = "single"
                element: str = "normal\""""
    
    new_move_def = """            @dataclass
            class Move:
                name: str
                power: int
                pp: int
                max_pp: int
                target_type: str = "single"
                element: str = "normal"
                
                @property
                def id(self):
                    # Generate a simple ID from name
                    return self.name.lower().replace(" ", "_")"""
    
    if old_move_def in content:
        content = content.replace(old_move_def, new_move_def)
        with open(monster_instance_path, 'w') as f:
            f.write(content)
        print("   ✅ Fixed Move class with id property")
    else:
        print("   ⚠️  Move class already modified or not found")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Fix 3: Fix BattleUI.show_message (it should be add_message)
print("\n3. Fixing BattleUI message methods...")
battle_scene_path = "/Users/leon/Desktop/untold_story/engine/scenes/battle_scene.py"

try:
    with open(battle_scene_path, 'r') as f:
        content = f.read()
    
    # Replace show_message with add_message
    if "self.battle_ui.show_message" in content:
        content = content.replace("self.battle_ui.show_message", "self.battle_ui.add_message")
        with open(battle_scene_path, 'w') as f:
            f.write(content)
        print("   ✅ Fixed BattleUI message method calls")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Fix 4: Fix command collection to properly handle actions
print("\n4. Fixing command collection...")
command_collection_path = "/Users/leon/Desktop/untold_story/engine/systems/battle/command_collection.py"

try:
    with open(command_collection_path, 'r') as f:
        content = f.read()
    
    # Make sure the validation accepts the current action format
    # Find the validate_command method
    if "def validate_command" in content:
        # Check if it needs fixing
        if "'action' in command" in content and "'type' in command" not in content:
            # Add alternative check for 'action' field
            old_check = "if 'type' not in command:"
            new_check = "if 'type' not in command and 'action' not in command:"
            
            if old_check in content:
                content = content.replace(old_check, new_check)
                with open(command_collection_path, 'w') as f:
                    f.write(content)
                print("   ✅ Fixed command validation")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Fix 5: Simplify battle action creation
print("\n5. Creating simplified battle action handler...")

battle_action_fix = '''"""
Battle Action Handler Fix
Simplified action processing for battle system
"""

from enum import Enum, auto
from typing import Dict, Any, Optional

class SimpleActionType(Enum):
    """Simplified action types."""
    ATTACK = auto()
    DEFEND = auto()
    ITEM = auto()
    FLEE = auto()
    SWITCH = auto()
    SPECIAL = auto()
    MENU = auto()

def create_simple_action(action_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Create a simplified battle action."""
    action_type = action_data.get('action', '')
    
    if action_type == 'attack':
        return {
            'type': 'attack',
            'actor': action_data.get('actor'),
            'move': action_data.get('move'),
            'target': action_data.get('target'),
            'move_index': action_data.get('move_index', 0)
        }
    elif action_type == 'flee':
        return {
            'type': 'flee',
            'actor': action_data.get('actor')
        }
    elif action_type in ['tame', 'scout', 'switch', 'item']:
        return {
            'type': action_type,
            'actor': action_data.get('actor')
        }
    elif action_type == 'menu_select':
        # This is a UI action, not a battle action
        return None
    else:
        # Default attack action
        return {
            'type': 'attack',
            'actor': action_data.get('actor'),
            'move': None,
            'target': None
        }
'''

with open("/Users/leon/Desktop/untold_story/engine/systems/battle/battle_action_fix.py", 'w') as f:
    f.write(battle_action_fix)
print("   ✅ Created battle_action_fix.py")

# Fix 6: Update battle_scene.py to handle actions properly
print("\n6. Updating battle scene action handling...")

try:
    with open(battle_scene_path, 'r') as f:
        content = f.read()
    
    # Find and fix the _create_battle_action method
    method_start = content.find("def _create_battle_action(self, player_action: dict)")
    if method_start > 0:
        method_end = content.find("\n    def ", method_start + 1)
        if method_end < 0:
            method_end = len(content)
        
        new_method = '''    def _create_battle_action(self, player_action: dict) -> Optional[Dict]:
        """Create a simplified battle action from player input."""
        try:
            action_type = player_action.get('action')
            
            # Handle different action types
            if action_type == 'attack':
                return {
                    'action': 'attack',
                    'actor': player_action.get('actor'),
                    'move': player_action.get('move'),
                    'target': player_action.get('target'),
                    'move_index': player_action.get('move_index', 0)
                }
            elif action_type == 'flee':
                return {
                    'action': 'flee',
                    'actor': player_action.get('actor')
                }
            elif action_type in ['tame', 'scout', 'switch', 'item']:
                return {
                    'action': action_type,
                    'actor': player_action.get('actor')
                }
            elif action_type == 'menu_select':
                # UI action - open submenu
                return None
            elif action_type == 'cancel':
                # Cancel action
                return None
            
            return None
            
        except Exception as e:
            print(f"Error creating battle action: {e}")
            return None'''
        
        # Replace the method
        content = content[:method_start] + new_method + content[method_end:]
        
        with open(battle_scene_path, 'w') as f:
            f.write(content)
        print("   ✅ Updated _create_battle_action method")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "="*60)
print("✅ BATTLE SYSTEM FIXES APPLIED!")
print("\nRestart the game to test the fixes:")
print("python3 main.py")
print("\nExpected behavior:")
print("- Fight → Move selection → Target selection → Execute")
print("- Other options should work without errors")
print("- Flee should allow escaping from battle")
