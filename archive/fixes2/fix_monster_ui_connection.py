#!/usr/bin/env python3
"""
Fix 1: Monster-UI-Verbindung reparieren
Verbindet die Battle-UI korrekt mit den Monster-Daten
"""

import os
import sys

def fix_battle_ui():
    """Repariert die _get_monster_by_id Methode in BattleUI"""
    
    battle_ui_path = "/Users/leon/Desktop/untold_story/engine/ui/battle_ui.py"
    
    # Backup erstellen
    with open(battle_ui_path, 'r') as f:
        original_content = f.read()
    
    with open(battle_ui_path + '.backup', 'w') as f:
        f.write(original_content)
    
    # Finde und ersetze die _get_monster_by_id Methode
    new_method = '''    def _get_monster_by_id(self, actor_id: str):
        """Get monster instance by actor ID."""
        try:
            # Check if we have access to battle_state
            battle_state = None
            
            # Try to get battle_state from different sources
            if hasattr(self, 'battle_state'):
                battle_state = self.battle_state
            elif hasattr(self, 'game') and hasattr(self.game, 'current_scene'):
                scene = self.game.current_scene
                if hasattr(scene, 'battle_state'):
                    battle_state = scene.battle_state
            
            if not battle_state:
                print(f"WARNING: No battle_state available for actor_id {actor_id}")
                return None
            
            # Parse actor_id and return appropriate monster
            if actor_id.startswith('player_'):
                try:
                    index = int(actor_id.split('_')[1])
                    if index < len(battle_state.player_team):
                        return battle_state.player_team[index]
                except (ValueError, IndexError) as e:
                    print(f"ERROR: Invalid player index in {actor_id}: {e}")
                    
            elif actor_id.startswith('enemy_'):
                try:
                    index = int(actor_id.split('_')[1])
                    if index < len(battle_state.enemy_team):
                        return battle_state.enemy_team[index]
                except (ValueError, IndexError) as e:
                    print(f"ERROR: Invalid enemy index in {actor_id}: {e}")
            
            return None
            
        except Exception as e:
            print(f"ERROR in _get_monster_by_id: {e}")
            return None'''
    
    # Ersetze die alte Methode
    lines = original_content.split('\n')
    new_lines = []
    in_method = False
    skip_lines = 0
    
    for i, line in enumerate(lines):
        if skip_lines > 0:
            skip_lines -= 1
            continue
            
        if 'def _get_monster_by_id(self, actor_id: str):' in line:
            in_method = True
            # Füge die neue Methode ein
            new_lines.append(new_method)
            # Finde das Ende der alten Methode
            indent_level = len(line) - len(line.lstrip())
            for j in range(i+1, len(lines)):
                if lines[j].strip() and not lines[j].startswith(' ' * (indent_level + 1)):
                    skip_lines = j - i - 1
                    break
        elif not in_method:
            new_lines.append(line)
        
        if in_method and skip_lines == 0:
            in_method = False
    
    # Schreibe die aktualisierte Datei
    with open(battle_ui_path, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ BattleUI._get_monster_by_id() repariert")
    
    # Füge battle_state Property hinzu falls nicht vorhanden
    if 'self.battle_state = None' not in original_content:
        # Füge es im __init__ hinzu
        lines = new_lines
        new_lines = []
        for i, line in enumerate(lines):
            new_lines.append(line)
            if 'def __init__(self, game):' in line:
                # Finde die richtige Einrückung
                for j in range(i+1, min(i+10, len(lines))):
                    if 'self.' in lines[j]:
                        indent = len(lines[j]) - len(lines[j].lstrip())
                        new_lines.append(' ' * indent + 'self.battle_state = None  # Will be set by BattleScene')
                        break
        
        with open(battle_ui_path, 'w') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ battle_state Property zu BattleUI hinzugefügt")

if __name__ == "__main__":
    fix_battle_ui()
    print("\n✅ Fix 1 abgeschlossen: Monster-UI-Verbindung repariert")
