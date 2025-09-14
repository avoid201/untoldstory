#!/usr/bin/env python3
"""
Final Fix Script - Behebt die letzten Integrationsprobleme
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🔧 Final Integration Fixes...")
print("="*50)

# Fix 1: Update status wrapper to not require monster in __init__
print("\n1. Fixing StatusEffectSystem initialization...")

wrapper_content = '''"""
Status Effect System Compatibility Wrapper
Provides unified interface for status effects
"""

from engine.systems.battle.status_effects_dqm import DQMStatusManager, DQMStatus, StatusEffect

class StatusEffectSystem:
    """Compatibility wrapper for DQMStatusManager."""
    
    def __init__(self):
        """Initialize without requiring a monster."""
        self.managers = {}
        
    def initialize_monster(self, monster):
        """Initialize status manager for a monster."""
        if monster not in self.managers:
            self.managers[monster] = DQMStatusManager(monster)
        return self.managers[monster]
        
    def apply_status(self, monster, status):
        """Apply status to a monster."""
        if monster not in self.managers:
            self.managers[monster] = DQMStatusManager(monster)
        
        # Convert string to DQMStatus if needed
        if isinstance(status, str):
            status = DQMStatus[status.upper()] if status.upper() in DQMStatus.__members__ else DQMStatus.NORMAL
        
        # Apply with default duration
        return self.managers[monster].apply_status(status, duration=3)
    
    def process_turn_end(self, monster):
        """Process end of turn for a monster."""
        if monster not in self.managers:
            self.managers[monster] = DQMStatusManager(monster)
        
        effects = self.managers[monster].process_turn_end()
        
        # Update monster's HP if damaged
        if 'damage' in effects:
            monster.current_hp = max(0, monster.current_hp - effects['damage'])
        
        return effects
    
    def can_monster_act(self, monster):
        """Check if monster can act this turn."""
        if monster not in self.managers:
            return True
        
        effects = self.managers[monster].process_turn_start()
        return not effects.get('skip_turn', False)

# Export
StatusType = DQMStatus
'''

wrapper_path = "/Users/leon/Desktop/untold_story/engine/systems/battle/status_system_wrapper.py"
with open(wrapper_path, 'w') as f:
    f.write(wrapper_content)
print("   ✅ Fixed StatusEffectSystem initialization")

# Fix 2: Update verify_integration.py to add hp stat
print("\n2. Fixing MonsterInstance stats in verify_integration.py...")

verify_path = "/Users/leon/Desktop/untold_story/verify_integration.py"
with open(verify_path, 'r') as f:
    content = f.read()

# Find the monster creation section and fix it
old_stats = "player_monster.stats = {'atk': 50, 'def': 40, 'mag': 35, 'res': 35, 'spd': 40}"
new_stats = "player_monster.stats = {'hp': 100, 'atk': 50, 'def': 40, 'mag': 35, 'res': 35, 'spd': 40}"

content = content.replace(old_stats, new_stats)

# Same for enemy
old_enemy_stats = "enemy_monster.stats = {'atk': 50, 'def': 40, 'mag': 35, 'res': 35, 'spd': 40}"
new_enemy_stats = "enemy_monster.stats = {'hp': 100, 'atk': 50, 'def': 40, 'mag': 35, 'res': 35, 'spd': 40}"

content = content.replace(old_enemy_stats, new_enemy_stats)

with open(verify_path, 'w') as f:
    f.write(content)
print("   ✅ Added hp stat to test monsters")

# Fix 3: Check what BattleValidator expects
print("\n3. Checking BattleValidator requirements...")

validator_path = "/Users/leon/Desktop/untold_story/engine/systems/battle/battle_validation.py"
if os.path.exists(validator_path):
    with open(validator_path, 'r') as f:
        validator_content = f.read()
    
    # Check if validator specifically checks for hp stat
    if "'hp'" in validator_content or '"hp"' in validator_content:
        print("   ⚠️  BattleValidator requires 'hp' stat - already fixed above")
    else:
        print("   ✓ BattleValidator doesn't specifically require 'hp' stat")

# Fix 4: Also fix StatusEffectSystem import in verify_integration.py
print("\n4. Updating StatusEffectSystem import...")

# Update the import to use the wrapper
old_import = "from engine.systems.battle.status_effects_dqm import StatusEffectSystem"
new_import = "from engine.systems.battle.status_system_wrapper import StatusEffectSystem"

with open(verify_path, 'r') as f:
    content = f.read()

if old_import in content:
    content = content.replace(old_import, new_import)
    with open(verify_path, 'w') as f:
        f.write(content)
    print("   ✅ Updated StatusEffectSystem import to use wrapper")

print("\n" + "="*50)
print("✅ FINAL FIXES APPLIED!")
print("\nNow test again with:")
print("python3 verify_integration.py")
