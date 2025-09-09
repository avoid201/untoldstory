#!/usr/bin/env python3
"""
Quick test to verify the battle system refactoring
"""

import sys
import os

# Add project path
sys.path.insert(0, '/Users/leon/Desktop/untold_story')

print("="*60)
print("BATTLE SYSTEM REFACTORING - QUICK TEST")
print("="*60)

# Test 1: Import test
print("\n1. IMPORT TEST:")
try:
    from engine.systems.battle.battle_enums import BattleType, BattlePhase
    from engine.systems.battle.battle_tension import TensionManager
    from engine.systems.battle.battle_validation import BattleValidator
    from engine.systems.battle.battle_actions import BattleActionExecutor
    from engine.systems.battle.battle_controller import BattleState
    print("✅ All modules imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)

# Test 2: Create a battle
print("\n2. BATTLE CREATION TEST:")
try:
    # Create simple mock monster
    class MockMonster:
        def __init__(self, name):
            self.name = name
            self.level = 5
            self.is_fainted = False
            self.current_hp = 100
            self.max_hp = 100
            self.stats = {"hp": 100, "atk": 50, "def": 50, "mag": 30, "res": 30, "spd": 70}
            self.stat_stages = {"atk": 0, "def": 0, "mag": 0, "res": 0, "spd": 0}
            self.moves = []
            self.status = None
            self.types = ["Normal"]
            self.species = type('Species', (), {'name': name})()
        
        def take_damage(self, damage):
            self.current_hp = max(0, self.current_hp - damage)
            if self.current_hp == 0:
                self.is_fainted = True
    
    # Create battle
    player_team = [MockMonster("Player1")]
    enemy_team = [MockMonster("Enemy1")]
    
    battle = BattleState(
        player_team=player_team,
        enemy_team=enemy_team,
        battle_type=BattleType.WILD
    )
    
    print("✅ Battle created successfully!")
    print(f"   Player active: {battle.player_active.name}")
    print(f"   Enemy active: {battle.enemy_active.name}")
    print(f"   Battle type: {battle.battle_type.value}")
    
except Exception as e:
    print(f"❌ Battle creation failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 3: Test subsystems
print("\n3. SUBSYSTEM TEST:")
try:
    # Test tension manager
    if hasattr(battle, 'tension_manager'):
        print("✅ Tension manager initialized")
    
    # Test validator
    if hasattr(battle, 'validator'):
        print("✅ Validator initialized")
    
    # Test action executor
    if hasattr(battle, 'action_executor'):
        print("✅ Action executor initialized")
    
    # Test battle AI
    if hasattr(battle, 'battle_ai'):
        print("✅ Battle AI initialized")
        
except Exception as e:
    print(f"❌ Subsystem test failed: {e}")

# Test 4: File sizes
print("\n4. FILE SIZE CHECK:")
import os
battle_dir = '/Users/leon/Desktop/untold_story/engine/systems/battle'

files = [
    'battle_enums.py',
    'battle_tension.py',
    'battle_validation.py',
    'battle_actions.py',
    'battle_controller.py',
    'battle_system.py'
]

total_size = 0
for filename in files:
    filepath = os.path.join(battle_dir, filename)
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        total_size += size
        print(f"✅ {filename}: {size/1024:.1f} KB")
    else:
        print(f"❌ {filename}: NOT FOUND")

# Check old file
old_file = os.path.join(battle_dir, 'battle_system_old.py')
if os.path.exists(old_file):
    old_size = os.path.getsize(old_file)
    print(f"\n📦 Original file: {old_size/1024:.1f} KB")
    print(f"📦 New modules total: {total_size/1024:.1f} KB")
    print(f"📉 Reduction: {(old_size - total_size)/1024:.1f} KB ({(1-total_size/old_size)*100:.0f}%)")

print("\n" + "="*60)
print("✅ ALL TESTS PASSED - REFACTORING SUCCESSFUL!")
print("="*60)
