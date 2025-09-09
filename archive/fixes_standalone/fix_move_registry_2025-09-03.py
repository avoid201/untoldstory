#!/usr/bin/env python3
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
