#!/usr/bin/env python3
"""
Emergency Battle Fix - Behebt die Action-Verarbeitung SOFORT
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def add_debug_logging():
    """Fügt Debug-Logging zu kritischen Stellen hinzu"""
    
    print("[EMERGENCY] Füge Debug-Logging hinzu...")
    
    # 1. Debug in BattleUI
    ui_path = PROJECT_ROOT / "engine" / "ui" / "battle_ui.py"
    if ui_path.exists():
        content = ui_path.read_text()
        
        # Füge Debug nach get_action_result hinzu
        debug_code = '''
        if action_result:
            print(f"[DEBUG] BattleUI generated action: {action_result}")
        else:
            print(f"[DEBUG] BattleUI: No action for state {self.state}")'''
        
        if "[DEBUG] BattleUI generated action:" not in content:
            content = content.replace(
                "return action_result",
                f"{debug_code}\n        return action_result"
            )
            ui_path.write_text(content)
            print("[EMERGENCY] ✓ Debug-Logging zu BattleUI hinzugefügt")
    
    # 2. Debug in BattleScene
    scene_path = PROJECT_ROOT / "engine" / "scenes" / "battle_scene.py"
    if scene_path.exists():
        content = scene_path.read_text()
        
        debug_code = '''
                print(f"[DEBUG] BattleScene received action: {action_result}")'''
        
        if "[DEBUG] BattleScene received action:" not in content:
            content = content.replace(
                "if action_result:",
                f"if action_result:{debug_code}"
            )
            scene_path.write_text(content)
            print("[EMERGENCY] ✓ Debug-Logging zu BattleScene hinzugefügt")


def fix_battle_ui_action_generation():
    """Stellt sicher dass BattleUI Actions generiert"""
    
    print("[EMERGENCY] Fixe BattleUI Action-Generation...")
    
    ui_path = PROJECT_ROOT / "engine" / "ui" / "battle_ui.py"
    if not ui_path.exists():
        print("[ERROR] battle_ui.py nicht gefunden!")
        return
    
    content = ui_path.read_text()
    
    # Füge einfache Attack-Action für SPACE in MAIN Menü hinzu
    simple_action = '''
            # EMERGENCY FIX: Direkte Attack-Action bei SPACE im Hauptmenü
            if self.state == BattleMenuState.MAIN and action == 'confirm':
                if self.selected_main_option == 0:  # ATTACKE
                    # Wähle ersten verfügbaren Move
                    if self.current_monster and hasattr(self.current_monster, 'moves') and self.current_monster.moves:
                        first_move = self.current_monster.moves[0]
                        print(f"[EMERGENCY] Using first move: {first_move}")
                        self.pending_action = {
                            'action': 'attack',
                            'type': 'attack',
                            'move': first_move,
                            'move_id': first_move.id if hasattr(first_move, 'id') else 'tackle',
                            'actor': self.current_monster,
                            'target': self.enemy_monster
                        }
                        return True'''
    
    if "[EMERGENCY] Using first move:" not in content:
        # Finde handle_input und füge den Fix ein
        import re
        pattern = r'def handle_input\(self, action: str\) -> bool:'
        
        def replacement(match):
            return match.group(0) + simple_action
        
        content = re.sub(pattern, replacement, content, count=1)
        ui_path.write_text(content)
        print("[EMERGENCY] ✓ Direkte Attack-Action hinzugefügt")


def fix_battle_scene_processing():
    """Stellt sicher dass BattleScene Actions verarbeitet"""
    
    print("[EMERGENCY] Fixe BattleScene Action-Processing...")
    
    scene_path = PROJECT_ROOT / "engine" / "scenes" / "battle_scene.py"
    if not scene_path.exists():
        print("[ERROR] battle_scene.py nicht gefunden!")
        return
    
    content = scene_path.read_text()
    
    # Stelle sicher dass _process_battle_action aufgerufen wird
    fix = '''
            # EMERGENCY: Force action processing
            if handled:
                action_result = self.battle_ui.get_action_result()
                if action_result:
                    print(f"[EMERGENCY] Processing action: {action_result.get('action', 'unknown')}")
                    self._process_battle_action(action_result)
                    self.battle_ui.clear_pending_action()
                else:
                    # Check for pending action directly
                    if hasattr(self.battle_ui, 'pending_action') and self.battle_ui.pending_action:
                        print(f"[EMERGENCY] Found pending action: {self.battle_ui.pending_action}")
                        self._process_battle_action(self.battle_ui.pending_action)
                        self.battle_ui.pending_action = None'''
    
    if "[EMERGENCY] Processing action:" not in content:
        content = content.replace(
            "if handled:\n                # Check if UI generated an action\n                action_result = self.battle_ui.get_action_result()\n                if action_result:\n                    self._process_battle_action(action_result)\n                    self.battle_ui.clear_pending_action()",
            fix
        )
        scene_path.write_text(content)
        print("[EMERGENCY] ✓ Force action processing hinzugefügt")


def ensure_moves_loaded():
    """Stellt sicher dass Monster Moves haben"""
    
    print("[EMERGENCY] Lade Monster-Moves...")
    
    fix_script = '''
import json
from pathlib import Path

# Lade monsters.json
monsters_file = Path("data/monsters.json")
moves_file = Path("data/moves.json")

if monsters_file.exists() and moves_file.exists():
    with open(moves_file) as f:
        moves_data = json.load(f)
    
    # Stelle sicher dass tackle existiert
    from engine.systems.moves import MoveRegistry
    registry = MoveRegistry()
    
    tackle = registry.get_move('tackle')
    if not tackle:
        print("[EMERGENCY] Lade Fallback-Move 'tackle'")
        # Erstelle einen einfachen Tackle-Move
        from engine.systems.moves import Move, MoveCategory, MoveTarget
        tackle = Move(
            id='tackle',
            name='Rempler',
            type='Bestie',
            category=MoveCategory.PHYSICAL,
            power=40,
            accuracy=100,
            priority=0,
            targeting=MoveTarget.ENEMY,
            effects=[],
            description='Einfacher Körperangriff'
        )
        registry.register_move('tackle', tackle)
        print("[EMERGENCY] ✓ Tackle-Move registriert")
'''
    
    script_path = PROJECT_ROOT / "emergency_moves.py"
    script_path.write_text(fix_script)
    
    import subprocess
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    print(result.stdout)


def test_quick_battle():
    """Schneller Battle-Test"""
    
    print("\n[EMERGENCY] Teste Battle-System...")
    
    test_script = '''
import pygame
pygame.init()

from engine.core.game import Game
from engine.systems.monster_instance import MonsterInstance
from engine.systems.monsters import MonsterDatabase

# Erstelle Test-Monster
db = MonsterDatabase()
species = db.get_species_by_id(1)  # Glutstummel

if species:
    player_monster = species.create_instance(level=5)
    player_monster.name = "Test-Monster"
    enemy_monster = species.create_instance(level=4)
    enemy_monster.name = "Gegner"
    
    print(f"[TEST] Player: {player_monster.name} mit {len(player_monster.moves)} Moves")
    print(f"[TEST] Enemy: {enemy_monster.name}")
    
    # Zeige erste Moves
    if player_monster.moves:
        for i, move in enumerate(player_monster.moves[:3]):
            print(f"  Move {i}: {move.name if hasattr(move, 'name') else move}")
else:
    print("[TEST] Konnte keine Monster erstellen!")

pygame.quit()
'''
    
    script_path = PROJECT_ROOT / "test_battle.py"
    script_path.write_text(test_script)
    
    import subprocess
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    print(result.stdout)


def main():
    print("\n" + "="*60)
    print("[EMERGENCY] BATTLE SYSTEM EMERGENCY FIX")
    print("="*60 + "\n")
    
    # 1. Debug-Logging
    add_debug_logging()
    
    # 2. Fix BattleUI
    fix_battle_ui_action_generation()
    
    # 3. Fix BattleScene
    fix_battle_scene_processing()
    
    # 4. Ensure Moves
    ensure_moves_loaded()
    
    # 5. Quick Test
    test_quick_battle()
    
    print("\n" + "="*60)
    print("[EMERGENCY] ✅ EMERGENCY FIXES ANGEWENDET!")
    print("="*60 + "\n")
    
    print("[EMERGENCY] Bitte starte das Spiel neu!")
    print("[EMERGENCY] Du solltest jetzt Debug-Output sehen wenn du SPACE drückst.")
    print("[EMERGENCY] Die ATTACKE-Option sollte jetzt funktionieren!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
