
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
