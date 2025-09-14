#!/usr/bin/env python3
"""
Battle System Test Script
Tests the battle system components and identifies potential bugs
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_monster_creation():
    """Test monster creation from database."""
    print("=== Testing Monster Creation ===")
    
    try:
        from engine.systems.monsters import MonsterDatabase
        from engine.systems.monster_instance import MonsterInstance
        
        db = MonsterDatabase()
        print(f"✅ MonsterDatabase loaded: {len(db.species)} species")
        
        # Test creating a monster
        monster = db.create_monster(species_id=1, level=5, nickname="Test-Monster")
        if monster:
            print(f"✅ Monster created: {monster.species.name} (Level {monster.level})")
            print(f"   Types: {monster.types}")
            print(f"   HP: {monster.current_hp}/{monster.max_hp}")
            print(f"   Stats: ATK={monster.attack}, DEF={monster.defense}")
            return monster
        else:
            print("❌ Failed to create monster")
            return None
            
    except Exception as e:
        print(f"❌ Error creating monster: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_battle_state_creation():
    """Test BattleState creation."""
    print("\n=== Testing BattleState Creation ===")
    
    try:
        from engine.systems.battle.battle import BattleState, BattleType
        from engine.systems.monsters import MonsterDatabase
        
        # Create test monsters
        db = MonsterDatabase()
        player_monster = db.create_monster(species_id=1, level=5)
        enemy_monster = db.create_monster(species_id=2, level=5)
        
        if not player_monster or not enemy_monster:
            print("❌ Failed to create test monsters")
            return None
        
        # Create battle state
        battle_state = BattleState(
            player_team=[player_monster],
            enemy_team=[enemy_monster],
            battle_type=BattleType.WILD,
            can_flee=True,
            can_catch=True
        )
        
        print(f"✅ BattleState created successfully")
        print(f"   Player active: {battle_state.player_active.species.name}")
        print(f"   Enemy active: {battle_state.enemy_active.species.name}")
        print(f"   Battle type: {battle_state.battle_type}")
        print(f"   Phase: {battle_state.phase}")
        
        return battle_state
        
    except Exception as e:
        print(f"❌ Error creating BattleState: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_battle_start():
    """Test battle start process."""
    print("\n=== Testing Battle Start ===")
    
    try:
        battle_state = test_battle_state_creation()
        if not battle_state:
            return None
        
        # Start battle
        battle_info = battle_state.start_battle()
        print(f"✅ Battle started successfully")
        print(f"   Battle info: {battle_info}")
        print(f"   Phase: {battle_state.phase}")
        print(f"   Battle log: {battle_state.battle_log}")
        
        return battle_state
        
    except Exception as e:
        print(f"❌ Error starting battle: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_encounter_system():
    """Test encounter system."""
    print("\n=== Testing Encounter System ===")
    
    try:
        from engine.systems.monsters import MonsterDatabase
        
        # Test Route 1 encounter table creation
        db = MonsterDatabase()
        print(f"✅ MonsterDatabase available: {len(db.species)} species")
        
        # Test getting random species
        random_species = db.get_random_species()
        if random_species:
            print(f"✅ Random species: {random_species.name} (ID: {random_species.id})")
        else:
            print("❌ Failed to get random species")
        
        # Test creating wild monster
        wild_monster = db.create_wild_monster(area="route1", player_level=5)
        if wild_monster:
            print(f"✅ Wild monster created: {wild_monster.species.name} (Level {wild_monster.level})")
        else:
            print("❌ Failed to create wild monster")
        
    except Exception as e:
        print(f"❌ Error testing encounter system: {e}")
        import traceback
        traceback.print_exc()

def test_battle_ui():
    """Test battle UI components."""
    print("\n=== Testing Battle UI ===")
    
    try:
        from engine.ui.battle_ui import BattleUI
        
        # Create mock game object
        class MockGame:
            def __init__(self):
                self.logical_size = (320, 180)
        
        mock_game = MockGame()
        battle_ui = BattleUI(mock_game)
        print(f"✅ BattleUI created successfully")
        
        # Test UI initialization
        from engine.systems.monsters import MonsterDatabase
        db = MonsterDatabase()
        player_monster = db.create_monster(species_id=1, level=5)
        enemy_monster = db.create_monster(species_id=2, level=5)
        
        if player_monster and enemy_monster:
            battle_ui.init_battle([player_monster], [enemy_monster])
            print(f"✅ BattleUI initialized with monsters")
        else:
            print("❌ Failed to create test monsters for UI")
        
    except Exception as e:
        print(f"❌ Error testing battle UI: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all battle system tests."""
    print("🐛 BATTLE SYSTEM ANALYSIS")
    print("=" * 50)
    
    # Test individual components
    test_monster_creation()
    test_battle_state_creation()
    test_battle_start()
    test_encounter_system()
    test_battle_ui()
    
    print("\n" + "=" * 50)
    print("🎯 BATTLE SYSTEM ANALYSIS COMPLETE")
    print("\nNext steps:")
    print("1. Test actual battle flow in game")
    print("2. Check for missing move data")
    print("3. Verify battle UI rendering")
    print("4. Test encounter triggering on Route 1")

if __name__ == "__main__":
    main()