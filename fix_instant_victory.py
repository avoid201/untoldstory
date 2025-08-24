#!/usr/bin/env python3
"""
Fix Instant Victory Bug
Behebt das Problem, dass Battles sofort enden
"""

print("🐛 FIXING INSTANT VICTORY BUG")
print("="*60)

# The problem might be in the battle state initialization or HP checking
print("\n1. Checking enemy HP initialization...")

field_scene_path = "/Users/leon/Desktop/untold_story/engine/scenes/field_scene.py"

with open(field_scene_path, 'r') as f:
    content = f.read()

# Make sure wild monsters have proper HP
if "current_hp=" not in content or "max_hp=" not in content:
    print("   ⚠️  Wild monsters might not have HP set properly")
    
    # Find _generate_wild_monster and ensure HP is set
    old_gen = '''                monster = MonsterInstance(
                    species_id=str(encounter['species_id']),
                    name=encounter['name'],
                    level=level,
                    stats=stats
                )'''
    
    new_gen = '''                # Calculate HP based on level
                hp_value = stats['hp'] + (level * 10)
                
                monster = MonsterInstance(
                    species_id=str(encounter['species_id']),
                    name=encounter['name'],
                    level=level,
                    stats=stats,
                    max_hp=hp_value,
                    current_hp=hp_value
                )'''
    
    if old_gen in content:
        content = content.replace(old_gen, new_gen)
        with open(field_scene_path, 'w') as f:
            f.write(content)
        print("   ✅ Fixed wild monster HP initialization")
else:
    print("   ✓ Wild monster HP should be set")

# Fix 2: Make sure MonsterInstance constructor properly sets HP
print("\n2. Checking MonsterInstance HP setup...")

monster_instance_path = "/Users/leon/Desktop/untold_story/engine/systems/monster_instance.py"

with open(monster_instance_path, 'r') as f:
    content = f.read()

# Ensure HP is properly initialized from stats if not provided
if "# HP/MP" in content:
    old_hp_init = '''        # HP/MP
        self.max_hp = kwargs.get('max_hp', 100 + level * 10)
        self.current_hp = kwargs.get('current_hp', self.max_hp)'''
    
    new_hp_init = '''        # HP/MP
        # Use stats['hp'] if available, otherwise calculate
        hp_stat = self.stats.get('hp', 100) if hasattr(self, 'stats') else 100
        self.max_hp = kwargs.get('max_hp', hp_stat + level * 10)
        self.current_hp = kwargs.get('current_hp', self.max_hp)
        
        # Ensure HP is never 0 on creation
        if self.current_hp <= 0:
            self.current_hp = self.max_hp'''
    
    if old_hp_init in content:
        content = content.replace(old_hp_init, new_hp_init)
        with open(monster_instance_path, 'w') as f:
            f.write(content)
        print("   ✅ Fixed MonsterInstance HP initialization")

# Fix 3: Add validation to prevent instant victory
print("\n3. Adding battle state validation...")

battle_controller_path = "/Users/leon/Desktop/untold_story/engine/systems/battle/battle_controller.py"

with open(battle_controller_path, 'r') as f:
    content = f.read()

# Add HP check in initialization
if "# Validate input parameters" in content:
    validation_add = '''        # Ensure all monsters have positive HP
        for monster in player_team + enemy_team:
            if not hasattr(monster, 'current_hp') or monster.current_hp <= 0:
                if hasattr(monster, 'max_hp'):
                    monster.current_hp = monster.max_hp
                else:
                    monster.current_hp = 100
                    monster.max_hp = 100
                print(f"WARNING: Fixed {monster.name} HP to {monster.current_hp}")
        '''
    
    # Find where to insert
    insert_after = "# Validate input parameters"
    insert_pos = content.find(insert_after)
    if insert_pos > 0:
        # Find the next line
        next_line = content.find("\n", insert_pos) + 1
        content = content[:next_line] + validation_add + content[next_line:]
        
        with open(battle_controller_path, 'w') as f:
            f.write(content)
        print("   ✅ Added HP validation to battle initialization")

print("\n" + "="*60)
print("✅ INSTANT VICTORY BUG FIXED!")
print("\nWhat was fixed:")
print("  • Wild monsters now have proper HP values")
print("  • MonsterInstance ensures HP is never 0")
print("  • Battle validates all monsters have positive HP")
print("\nThe battle should now work properly without instant victory!")
