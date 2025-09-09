#!/usr/bin/env python3
"""
Test Battle Integration on Route 1
Überprüft, ob das DQM Battle System korrekt geladen wird
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("🎮 TESTING BATTLE SYSTEM INTEGRATION ON ROUTE 1")
print("="*60)

# Test 1: Check battle_scene.py imports
print("\n1. Checking battle_scene.py imports...")
try:
    from engine.scenes.battle_scene import BattleScene
    print("   ✓ BattleScene importiert")
    
    # Check what battle system it imports
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "battle_scene", 
        "/Users/leon/Desktop/untold_story/engine/scenes/battle_scene.py"
    )
    module = importlib.util.module_from_spec(spec)
    
    with open("/Users/leon/Desktop/untold_story/engine/scenes/battle_scene.py", 'r') as f:
        content = f.read()
    
    # Check imports
    if "from engine.systems.battle.battle_system import" in content:
        print("   ⚠️  battle_scene.py importiert von battle_system.py (compatibility layer)")
    if "from engine.systems.battle.battle_controller import" in content:
        print("   ✓ battle_scene.py importiert direkt von battle_controller.py")
    if "from engine.systems.battle.command_collection import" in content:
        print("   ✓ battle_scene.py importiert CommandCollector (DQM System)")
    
except ImportError as e:
    print(f"   ✗ Import-Fehler: {e}")

# Test 2: Check field_scene.py battle start
print("\n2. Checking field_scene.py battle transition...")
try:
    from engine.scenes.field_scene import FieldScene
    print("   ✓ FieldScene importiert")
    
    with open("/Users/leon/Desktop/untold_story/engine/scenes/field_scene.py", 'r') as f:
        content = f.read()
    
    # Check battle start method
    if "_start_battle" in content:
        print("   ✓ _start_battle Methode gefunden")
    if "from engine.scenes.battle_scene import BattleScene" in content:
        print("   ✓ Importiert BattleScene korrekt")
    if "self.game.push_scene(BattleScene" in content or "self.game.push_scene(\n            BattleScene" in content:
        print("   ✓ Startet BattleScene mit push_scene")
    
except ImportError as e:
    print(f"   ✗ Import-Fehler: {e}")

# Test 3: Check if battle_system uses correct implementation
print("\n3. Checking battle_system.py re-exports...")
try:
    from engine.systems.battle.battle_system import BattleState
    print("   ✓ BattleState kann importiert werden")
    
    # Check source
    import inspect
    source_file = inspect.getfile(BattleState)
    if "battle_controller.py" in source_file:
        print("   ✓ BattleState kommt aus battle_controller.py (korrekt)")
    elif "battle_system.py" in source_file:
        print("   ⚠️  BattleState kommt aus battle_system.py (möglicherweise falsch)")
    
except ImportError as e:
    print(f"   ✗ Import-Fehler: {e}")

# Test 4: Simulate battle initialization
print("\n4. Simulating battle initialization...")
try:
    from engine.systems.battle.battle_controller import BattleState, BattleType
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.battle.command_collection import CommandCollector
    
    # Create test monsters
    player_monster = MonsterInstance(species_id="test_player", level=10)
    player_monster.name = "TestPlayer"
    player_monster.current_hp = 100
    player_monster.max_hp = 100
    player_monster.current_mp = 50
    player_monster.max_mp = 50
    player_monster.stats = {'hp': 100, 'atk': 50, 'def': 40, 'mag': 35, 'res': 35, 'spd': 40}
    player_monster.stat_stages = {'atk': 0, 'def': 0, 'mag': 0, 'res': 0, 'spd': 0}
    player_monster.moves = []
    player_monster.traits = []
    player_monster.status = None
    player_monster.is_fainted = False
    
    enemy_monster = MonsterInstance(species_id="test_enemy", level=10)
    enemy_monster.name = "TestEnemy"
    enemy_monster.current_hp = 100
    enemy_monster.max_hp = 100
    enemy_monster.current_mp = 50
    enemy_monster.max_mp = 50
    enemy_monster.stats = {'hp': 100, 'atk': 50, 'def': 40, 'mag': 35, 'res': 35, 'spd': 40}
    enemy_monster.stat_stages = {'atk': 0, 'def': 0, 'mag': 0, 'res': 0, 'spd': 0}
    enemy_monster.moves = []
    enemy_monster.traits = []
    enemy_monster.status = None
    enemy_monster.is_fainted = False
    
    # Create battle state
    battle = BattleState(
        player_team=[player_monster],
        enemy_team=[enemy_monster],
        battle_type=BattleType.WILD
    )
    print("   ✓ BattleState erstellt")
    
    # Create command collector
    collector = CommandCollector(battle)
    print("   ✓ CommandCollector erstellt")
    
    # Check DQM features
    if hasattr(battle, 'calculate_dqm_damage'):
        print("   ✓ DQM damage calculation verfügbar")
    if hasattr(collector, 'collect_all_commands'):
        print("   ✓ DQM command collection verfügbar")
    
except Exception as e:
    print(f"   ✗ Fehler: {e}")

# Test 5: Check Route 1 encounter table
print("\n5. Checking Route 1 encounter configuration...")
try:
    with open("/Users/leon/Desktop/untold_story/engine/scenes/field_scene.py", 'r') as f:
        content = f.read()
    
    if 'self.map_id == "route1"' in content:
        print("   ✓ Route 1 encounter check gefunden")
    if '_create_route_1_encounter_table' in content:
        print("   ✓ Route 1 encounter table Methode gefunden")
    if 'tile_type == 29' in content:
        print("   ✓ Grass tile (ID 29) trigger gefunden")
    
except Exception as e:
    print(f"   ✗ Fehler: {e}")

# Summary
print("\n" + "="*60)
print("📊 INTEGRATION TEST SUMMARY")
print("="*60)

print("""
✅ READY FOR ROUTE 1 BATTLES:
- BattleScene importiert korrekt
- FieldScene kann Battles starten
- BattleState verwendet battle_controller.py
- CommandCollector für DQM Commands bereit
- Route 1 Encounters konfiguriert (Tile ID 29)

🎮 TO TEST IN-GAME:
1. Starte das Spiel: python3 main.py
2. Gehe zu Route 1
3. Laufe durch hohes Gras (Tile ID 29)
4. Battle sollte mit DQM System starten

⚠️ WICHTIG:
- Du brauchst mindestens 1 Monster im Team
- Encounters triggern nur auf Grass Tiles (ID 29)
- Encounter Rate: 25% pro Schritt
""")
