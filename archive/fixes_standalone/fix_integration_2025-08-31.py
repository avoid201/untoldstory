#!/usr/bin/env python3
"""
Fix Integration Issues
Behebt die verbleibenden Integrationsprobleme
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🔧 Fixing Integration Issues...")
print("="*50)

# Fix 1: Update status_effects_dqm.py to have StatusEffectSystem alias
print("\n1. Fixing StatusEffectSystem import...")
status_file_path = "/Users/leon/Desktop/untold_story/engine/systems/battle/status_effects_dqm.py"

with open(status_file_path, 'r') as f:
    content = f.read()

# Add alias at the end
if "StatusEffectSystem = DQMStatusManager" not in content:
    content += "\n\n# Alias for compatibility\nStatusEffectSystem = DQMStatusManager\nStatusType = DQMStatus\n"
    
    # Update __all__
    content = content.replace(
        "__all__ = ['DQMStatus', 'StatusEffect', 'DQMStatusManager']",
        "__all__ = ['DQMStatus', 'StatusEffect', 'DQMStatusManager', 'StatusEffectSystem', 'StatusType']"
    )
    
    with open(status_file_path, 'w') as f:
        f.write(content)
    print("   ✅ Added StatusEffectSystem alias")

# Fix 2: Fix DQMDamageResult subscriptable issue
print("\n2. Fixing DQMDamageResult subscriptable issue...")
dqm_formulas_path = "/Users/leon/Desktop/untold_story/engine/systems/battle/dqm_formulas.py"

with open(dqm_formulas_path, 'r') as f:
    content = f.read()

# Check if DQMDamageResult has __getitem__
if "def __getitem__" not in content:
    # Find the DQMDamageResult class
    class_start = content.find("@dataclass\nclass DQMDamageResult:")
    if class_start > 0:
        # Find the end of the class (next class or end of file)
        next_class = content.find("\nclass ", class_start + 1)
        if next_class < 0:
            next_class = content.find("\n\n# ", class_start + 1)
        if next_class < 0:
            next_class = len(content)
        
        # Add __getitem__ method
        getitem_method = '''
    
    def __getitem__(self, key):
        """Make DQMDamageResult subscriptable for backward compatibility."""
        return getattr(self, key, None)
    
    def get(self, key, default=None):
        """Dict-like get method."""
        return getattr(self, key, default)
'''
        
        # Insert before the next class
        content = content[:next_class] + getitem_method + content[next_class:]
        
        with open(dqm_formulas_path, 'w') as f:
            f.write(content)
        print("   ✅ Made DQMDamageResult subscriptable")

# Fix 3: Update verify_integration.py to use correct imports
print("\n3. Updating verify_integration.py...")
verify_path = "/Users/leon/Desktop/untold_story/verify_integration.py"

with open(verify_path, 'r') as f:
    content = f.read()

# Fix the SimpleMonster class to inherit from MonsterInstance or bypass check
old_simple_monster = """    # Create simple test monsters
    class SimpleMonster:
        def __init__(self, name):
            self.name = name
            self.id = name.lower()
            self.level = 10
            self.current_hp = 100
            self.max_hp = 100
            self.current_mp = 50
            self.max_mp = 50
            self.stats = {'atk': 50, 'def': 40, 'mag': 35, 'res': 35, 'spd': 40}
            self.moves = []
            self.traits = []
            self.status = None
            self.is_fainted = False"""

new_simple_monster = """    # Create test monsters using actual MonsterInstance
    from engine.systems.monster_instance import MonsterInstance
    
    # Create proper MonsterInstance objects
    player_monster = MonsterInstance(species_id="test_player", level=10)
    player_monster.name = "TestPlayer"
    player_monster.current_hp = 100
    player_monster.max_hp = 100
    player_monster.current_mp = 50
    player_monster.max_mp = 50
    player_monster.stats = {'atk': 50, 'def': 40, 'mag': 35, 'res': 35, 'spd': 40}
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
    enemy_monster.stats = {'atk': 50, 'def': 40, 'mag': 35, 'res': 35, 'spd': 40}
    enemy_monster.moves = []
    enemy_monster.traits = []
    enemy_monster.status = None
    enemy_monster.is_fainted = False"""

if "class SimpleMonster:" in content:
    # Find and replace the entire SimpleMonster section
    content = content.replace(old_simple_monster, new_simple_monster)
    
    # Also remove the instantiation lines
    content = content.replace(
        "    player_monster = SimpleMonster(\"TestPlayer\")\n    enemy_monster = SimpleMonster(\"TestEnemy\")",
        ""
    )
    
    with open(verify_path, 'w') as f:
        f.write(content)
    print("   ✅ Updated verify_integration.py to use MonsterInstance")

# Fix 4: Create a compatibility wrapper for StatusEffectSystem
print("\n4. Creating status effect compatibility wrapper...")
wrapper_content = '''"""
Status Effect System Compatibility Wrapper
Provides unified interface for status effects
"""

from engine.systems.battle.status_effects_dqm import DQMStatusManager, DQMStatus, StatusEffect

class StatusEffectSystem:
    """Compatibility wrapper for DQMStatusManager."""
    
    def __init__(self):
        self.managers = {}
        
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
print("   ✅ Created status system compatibility wrapper")

print("\n" + "="*50)
print("✅ ALL FIXES APPLIED!")
print("\nTeste jetzt nochmal mit:")
print("python3 verify_integration.py")
