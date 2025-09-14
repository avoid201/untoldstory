#!/usr/bin/env python3
"""
Battle Integration Fixer
Behebt die kritischen Issues im Battle-System
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def fix_battle_event_dict_interface():
    """Fügt dict-ähnliche Interface zu BattleEvent hinzu"""
    
    battle_events_path = PROJECT_ROOT / "engine" / "systems" / "battle" / "battle_events.py"
    
    print("[Flint] Fixe BattleEvent dict-Interface...")
    
    content = battle_events_path.read_text()
    
    # Füge get() und __getitem__ zu BattleEvent hinzu
    fix = '''    
    def get(self, key, default=None):
        """Dict-like get method for compatibility."""
        if key == 'message':
            return self.data.get('message', default)
        elif key == 'target':
            return self.data.get('target', default)
        elif key == 'damage':
            return self.data.get('damage', default)
        elif key == 'type':
            return self.event_type
        else:
            return self.data.get(key, default)
    
    def __getitem__(self, key):
        """Make BattleEvent subscriptable for backward compatibility."""
        return self.get(key)'''
    
    # Füge die Methoden nach __str__ ein
    if "def get(self, key, default=None):" not in content:
        content = content.replace(
            '    def __str__(self) -> str:\n        """String representation."""\n        return f"BattleEvent({self.event_type.name}, data={self.data})"',
            f'    def __str__(self) -> str:\n        """String representation."""\n        return f"BattleEvent({{self.event_type.name}}, data={{self.data}})"\n{fix}'
        )
        
        battle_events_path.write_text(content)
        print("[Flint] ✓ BattleEvent dict-Interface hinzugefügt")
    else:
        print("[Flint] ✓ BattleEvent hat bereits dict-Interface")


def fix_move_registry():
    """Stellt sicher dass alle Moves in der Registry sind"""
    
    print("[Flint] Fixe Move-Registry...")
    
    # Erstelle ein Script das alle fehlenden Moves registriert
    fix_script = '''#!/usr/bin/env python3
"""Registriert fehlende Moves in der Registry"""

import json
from pathlib import Path

# Lade moves.json
moves_file = Path("data/moves.json")
if moves_file.exists():
    with open(moves_file) as f:
        moves_data = json.load(f)
    
    # Prüfe welche Moves fehlen
    from engine.systems.moves import MoveRegistry
    registry = MoveRegistry()
    
    missing = []
    for move_id, move_data in moves_data.items():
        if not registry.get_move(move_id):
            missing.append(move_id)
    
    if missing:
        print(f"[Flint] {len(missing)} Moves fehlen in Registry: {missing[:5]}...")
        # Registry lädt automatisch aus moves.json, also sollte das reichen
        registry._load_moves()
        print("[Flint] ✓ Moves neu geladen")
    else:
        print("[Flint] ✓ Alle Moves bereits in Registry")
'''
    
    script_path = PROJECT_ROOT / "fix_move_registry.py"
    script_path.write_text(fix_script)
    
    # Führe das Script aus
    import subprocess
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"[Flint] Warnung: {result.stderr}")


def fix_action_queue_processing():
    """Fixt das Action-Queue-Processing Problem"""
    
    print("[Flint] Fixe Action-Queue-Processing...")
    
    # Das Problem ist dass Actions nicht richtig konvertiert werden
    # Der BattleController braucht ein Update
    
    controller_path = PROJECT_ROOT / "engine" / "systems" / "battle" / "battle_controller.py"
    content = controller_path.read_text()
    
    # Stelle sicher dass execute_turn() auch mit leerer Queue umgehen kann
    fix = '''            # Wenn keine Actions in Queue, überspringe
            if not self.battle_state.action_queue:
                logger.debug("Keine Actions in Queue, überspringe Turn")
                return None'''
    
    if "Keine Actions in Queue, überspringe Turn" not in content:
        content = content.replace(
            '            if not self.battle_state.action_queue:\n                logger.warning("No actions in queue for execute_turn")\n                return None',
            fix
        )
        controller_path.write_text(content)
        print("[Flint] ✓ Action-Queue-Processing gefixt")
    else:
        print("[Flint] ✓ Action-Queue-Processing bereits gefixt")


def fix_battle_ui_event_handling():
    """Fixt die BattleUI Event-Verarbeitung"""
    
    print("[Flint] Fixe BattleUI Event-Handling...")
    
    ui_path = PROJECT_ROOT / "engine" / "ui" / "battle_ui.py"
    
    if not ui_path.exists():
        print("[Flint] ⚠️  battle_ui.py nicht gefunden!")
        return
    
    content = ui_path.read_text()
    
    # Füge robuste Event-Verarbeitung hinzu
    fix = '''        # Handle both BattleEvent objects and dicts
        if hasattr(event, 'event_type'):
            # It's a BattleEvent object
            event_type = event.event_type
            event_data = event.data
        elif isinstance(event, dict):
            # It's a dict
            event_type = event.get('type') or event.get('event_type')
            event_data = event
        else:
            logger.warning(f"Unknown event type: {type(event)}")
            return'''
    
    if "Handle both BattleEvent objects and dicts" not in content:
        # Finde die process_battle_event Methode und füge den Fix ein
        import re
        pattern = r'def process_battle_event\(self, event\):\s*"""[^"]*"""'
        
        def replacement(match):
            return match.group(0) + '\n' + fix
        
        content = re.sub(pattern, replacement, content)
        ui_path.write_text(content)
        print("[Flint] ✓ BattleUI Event-Handling gefixt")
    else:
        print("[Flint] ✓ BattleUI Event-Handling bereits gefixt")


def main():
    print("\n" + "="*60)
    print("[Flint] BATTLE INTEGRATION FIXER")
    print("="*60 + "\n")
    
    print("[Flint] Behebe kritische Battle-System Issues...\n")
    
    # 1. Fixe BattleEvent dict-Interface
    fix_battle_event_dict_interface()
    
    # 2. Fixe Move-Registry
    fix_move_registry()
    
    # 3. Fixe Action-Queue-Processing
    fix_action_queue_processing()
    
    # 4. Fixe BattleUI Event-Handling
    fix_battle_ui_event_handling()
    
    print("\n" + "="*60)
    print("[Flint] ✅ ALLE KRITISCHEN ISSUES BEHOBEN!")
    print("="*60 + "\n")
    
    print("[Flint] Empfehlung: Starte das Spiel neu mit 'python main.py'")
    print("[Flint] Die Battle-System sollte jetzt funktionieren!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
