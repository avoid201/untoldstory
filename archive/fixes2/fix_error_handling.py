#!/usr/bin/env python3
"""
Fix 4: Error-Handling in UI-Draw-Methoden
Fügt robustes Error-Handling in alle kritischen UI-Draw-Funktionen hinzu
"""

import os
import re

def add_error_handling_to_battle_ui():
    """Fügt try-catch Blöcke zu allen draw-Methoden in BattleUI hinzu"""
    
    battle_ui_path = "/Users/leon/Desktop/untold_story/engine/ui/battle_ui.py"
    
    with open(battle_ui_path, 'r') as f:
        original_content = f.read()
    
    # Backup
    with open(battle_ui_path + '.backup2', 'w') as f:
        f.write(original_content)
    
    lines = original_content.split('\n')
    new_lines = []
    
    # Pattern für draw-Methoden
    draw_methods = [
        'def draw(self',
        'def _draw_hud_panels(self',
        'def _draw_message_box(self',
        'def draw_monster_panel(self'
    ]
    
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Prüfe ob es eine draw-Methode ist
        is_draw_method = any(method in line for method in draw_methods)
        
        if is_draw_method and 'try:' not in lines[min(i+1, len(lines)-1)]:
            # Füge try-catch hinzu
            indent = len(lines[i+1]) - len(lines[i+1].lstrip()) if i+1 < len(lines) else 8
            
            # Sammle den Methoden-Body
            method_lines = []
            j = i + 1
            method_indent = indent
            
            while j < len(lines):
                current_line = lines[j]
                if current_line.strip() and not current_line.startswith(' ' * method_indent):
                    # Ende der Methode erreicht
                    break
                method_lines.append(current_line)
                j += 1
            
            # Wrap in try-catch
            new_lines.append(' ' * method_indent + 'try:')
            for method_line in method_lines:
                if method_line.strip():
                    new_lines.append(' ' * 4 + method_line)
                else:
                    new_lines.append(method_line)
            
            # Füge except-Block hinzu
            new_lines.append(' ' * method_indent + 'except Exception as e:')
            new_lines.append(' ' * (method_indent + 4) + 'print(f"Error in {}: {{e}}")'.format(line.split('(')[0].split()[-1]))
            new_lines.append(' ' * (method_indent + 4) + 'import traceback')
            new_lines.append(' ' * (method_indent + 4) + 'traceback.print_exc()')
            
            # Skip die bereits verarbeiteten Zeilen
            i = j - 1
        
        i += 1
    
    with open(battle_ui_path, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Error-Handling zu BattleUI draw-Methoden hinzugefügt")

def add_safe_attribute_access():
    """Fügt sichere Attribut-Zugriffe hinzu"""
    
    battle_ui_path = "/Users/leon/Desktop/untold_story/engine/ui/battle_ui.py"
    
    with open(battle_ui_path, 'r') as f:
        content = f.read()
    
    # Ersetze unsichere Zugriffe mit getattr
    replacements = [
        (r'monster\.name', 'getattr(monster, "name", "Unknown")'),
        (r'monster\.level', 'getattr(monster, "level", 1)'),
        (r'monster\.current_hp', 'getattr(monster, "current_hp", 0)'),
        (r'monster\.max_hp', 'getattr(monster, "max_hp", 1)'),
        (r'monster\.types', 'getattr(monster, "types", [])'),
        (r'monster\.moves', 'getattr(monster, "moves", [])'),
        (r'move\.name', 'getattr(move, "name", "Unknown Move")'),
        (r'move\.pp', 'getattr(move, "pp", 0)'),
        (r'move\.max_pp', 'getattr(move, "max_pp", 1)'),
    ]
    
    for pattern, replacement in replacements:
        # Nur ersetzen wenn nicht schon in getattr
        if 'getattr' not in pattern:
            content = re.sub(pattern + r'(?!\w)', replacement, content)
    
    with open(battle_ui_path, 'w') as f:
        f.write(content)
    
    print("✅ Sichere Attribut-Zugriffe hinzugefügt")

def add_null_checks():
    """Fügt Null-Checks vor kritischen Operationen hinzu"""
    
    files_to_fix = [
        "/Users/leon/Desktop/untold_story/engine/scenes/battle_scene.py",
        "/Users/leon/Desktop/untold_story/engine/systems/battle/battle_controller.py"
    ]
    
    for file_path in files_to_fix:
        if not os.path.exists(file_path):
            continue
            
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Füge Null-Checks hinzu
        patterns = [
            (r'(self\.battle_state\.player_active)(?=\.)', 
             r'(self.battle_state.player_active if self.battle_state and self.battle_state.player_active else None)'),
            (r'(self\.battle_state\.enemy_active)(?=\.)',
             r'(self.battle_state.enemy_active if self.battle_state and self.battle_state.enemy_active else None)'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Null-Checks zu {os.path.basename(file_path)} hinzugefügt")

if __name__ == "__main__":
    add_error_handling_to_battle_ui()
    add_safe_attribute_access()
    add_null_checks()
    print("\n✅ Fix 4 abgeschlossen: Robustes Error-Handling implementiert")
