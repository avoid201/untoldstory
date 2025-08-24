#!/usr/bin/env python3
"""
Quick Fix Script für MonsterInstance und Battle Errors
"""

import os
import sys

print("🔧 Fixing MonsterInstance and Battle Issues...")
print("="*50)

# Fix 1: Clear Python cache
print("\n1. Clearing Python cache...")
cache_dir = "/Users/leon/Desktop/untold_story/engine/systems/__pycache__"
if os.path.exists(cache_dir):
    for file in os.listdir(cache_dir):
        if file.startswith("monster_instance"):
            os.remove(os.path.join(cache_dir, file))
            print(f"   ✅ Removed cache: {file}")

# Fix 2: Fix the species.name issue in field_scene.py
print("\n2. Fixing species.name error in field_scene.py...")
field_scene_path = "/Users/leon/Desktop/untold_story/engine/scenes/field_scene.py"

with open(field_scene_path, 'r') as f:
    content = f.read()

# Fix the problematic line
old_line = 'print(f"[Flint] Starte Battle Transition zu {wild_monster.species.name}")'
new_line = '''monster_name = wild_monster.species.get('name', 'Unknown') if isinstance(wild_monster.species, dict) else getattr(wild_monster.species, 'name', wild_monster.name)
        print(f"[Flint] Starte Battle Transition zu {monster_name}")'''

if old_line in content:
    content = content.replace(old_line, new_line)
    with open(field_scene_path, 'w') as f:
        f.write(content)
    print("   ✅ Fixed species.name error")
else:
    # Try alternative fix
    old_line2 = 'print(f"[Flint] Starte Battle Transition zu {wild_monster.species.name}")'
    new_line2 = 'print(f"[Flint] Starte Battle Transition zu {wild_monster.name}")'
    
    if old_line2 in content:
        content = content.replace(old_line2, new_line2)
        with open(field_scene_path, 'w') as f:
            f.write(content)
        print("   ✅ Fixed species.name error (alternative)")

# Fix 3: Also add __all__ export to monster_instance.py
print("\n3. Adding proper exports to monster_instance.py...")
monster_path = "/Users/leon/Desktop/untold_story/engine/systems/monster_instance.py"

with open(monster_path, 'r') as f:
    content = f.read()

if "__all__" not in content:
    # Add at the end of the file
    export_line = "\n\n# Export all classes\n__all__ = ['MonsterSpecies', 'MonsterInstance', 'StatusCondition', 'create_test_monster']\n"
    content += export_line
    
    with open(monster_path, 'w') as f:
        f.write(content)
    print("   ✅ Added __all__ exports")

print("\n" + "="*50)
print("✅ FIXES APPLIED!")
print("\nNow restart the game:")
print("python3 main.py")
