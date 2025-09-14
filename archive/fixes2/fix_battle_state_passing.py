#!/usr/bin/env python3
"""
Fix 2: Battle-State an UI weitergeben
Stellt sicher, dass BattleScene den battle_state korrekt an die UI übergibt
"""

import os
import re

def fix_battle_scene():
    """Fügt battle_state passing in BattleScene hinzu"""
    
    battle_scene_path = "/Users/leon/Desktop/untold_story/engine/scenes/battle_scene.py"
    
    # Backup erstellen
    with open(battle_scene_path, 'r') as f:
        original_content = f.read()
    
    with open(battle_scene_path + '.backup', 'w') as f:
        f.write(original_content)
    
    lines = original_content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Nach BattleState-Initialisierung suchen
        if 'self.battle_state = BattleState(' in line:
            # Finde die schließende Klammer
            bracket_count = 1
            j = i + 1
            while j < len(lines) and bracket_count > 0:
                if '(' in lines[j]:
                    bracket_count += lines[j].count('(')
                if ')' in lines[j]:
                    bracket_count -= lines[j].count(')')
                if bracket_count == 0:
                    # Füge die UI-Verbindung nach der BattleState-Erstellung hinzu
                    indent = len(lines[j+1]) - len(lines[j+1].lstrip()) if j+1 < len(lines) else 12
                    new_lines.append(' ' * indent + '# Verbinde Battle-State mit UI')
                    new_lines.append(' ' * indent + 'self.battle_ui.battle_state = self.battle_state')
                    new_lines.append(' ' * indent + 'print("Battle-State mit UI verbunden")')
                    break
                j += 1
        
        # Nach battle_ui.init_battle suchen
        if 'self.battle_ui.init_battle(' in line:
            # Füge battle_state passing nach init_battle hinzu
            indent = len(line) - len(line.lstrip())
            # Prüfe ob nicht schon vorhanden
            if i+1 < len(lines) and 'battle_ui.battle_state' not in lines[i+1]:
                new_lines.append(' ' * indent + '# Stelle sicher, dass UI den battle_state hat')
                new_lines.append(' ' * indent + 'self.battle_ui.battle_state = self.battle_state')
    
    # Schreibe die aktualisierte Datei
    with open(battle_scene_path, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ BattleScene battle_state passing hinzugefügt")

def fix_handle_event():
    """Verbessert handle_event in BattleScene für korrektes State-Passing"""
    
    battle_scene_path = "/Users/leon/Desktop/untold_story/engine/scenes/battle_scene.py"
    
    with open(battle_scene_path, 'r') as f:
        content = f.read()
    
    # Füge battle_state zu allen handle_input Calls hinzu
    pattern = r'(self\.battle_ui\.handle_input\([^)]+)\)'
    replacement = r'\1, self.battle_state)'
    
    content = re.sub(pattern, replacement, content)
    
    # Korrigiere doppelte battle_state Parameter
    content = content.replace(', self.battle_state, self.battle_state)', ', self.battle_state)')
    
    with open(battle_scene_path, 'w') as f:
        f.write(content)
    
    print("✅ handle_event battle_state passing verbessert")

if __name__ == "__main__":
    fix_battle_scene()
    fix_handle_event()
    print("\n✅ Fix 2 abgeschlossen: Battle-State wird korrekt an UI übergeben")
