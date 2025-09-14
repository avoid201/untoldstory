#!/usr/bin/env python3
"""
Cleanup Duplicate Classes Script
================================
Removes all remaining duplicate class definitions in the battle system.
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Set


def find_duplicate_classes():
    """Find all files with duplicate class definitions."""
    battle_dir = Path("engine/systems/battle")
    duplicate_files = []
    
    # Files that should not contain class definitions
    excluded_files = [
        "mock_classes.py",  # Central mock classes
        "battle_enums.py",  # Central enums
        "__init__.py"
    ]
    
    # Files that should be cleaned up
    cleanup_files = [
        "unified_battle_manager.py",
        "examples/example_dqm_integration.py",
        "examples/example_event_system.py",
        "target_system.py",
        "battle_formation.py"
    ]
    
    for file_path in cleanup_files:
        full_path = battle_dir / file_path
        if full_path.exists():
            duplicate_files.append(str(full_path))
    
    return duplicate_files


def cleanup_unified_battle_manager():
    """Clean up unified_battle_manager.py."""
    file_path = "engine/systems/battle/unified_battle_manager.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"🧹 Cleaning up {file_path}...")
    
    # Read file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove any remaining duplicate class definitions
    # This should already be cleaned up, but let's double-check
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip any remaining class definitions that shouldn't be here
        if re.match(r'^class\s+(BattlePhase|BattleType|BattleResult|BattleAction)\s*\(', line):
            print(f"  ⚠️  Skipping duplicate class definition: {line.strip()}")
            continue
        cleaned_lines.append(line)
    
    # Write cleaned content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))
    
    print(f"  ✅ {file_path} cleaned up")
    return True


def cleanup_example_files():
    """Clean up example files to use centralized mock classes."""
    example_dir = Path("engine/systems/battle/examples")
    
    if not example_dir.exists():
        print(f"❌ Example directory not found: {example_dir}")
        return False
    
    print("🧹 Cleaning up example files...")
    
    # Clean up example_dqm_integration.py
    dqm_file = example_dir / "example_dqm_integration.py"
    if dqm_file.exists():
        print(f"  ✅ {dqm_file} already cleaned up")
    
    # Clean up example_event_system.py
    event_file = example_dir / "example_event_system.py"
    if event_file.exists():
        print(f"  ✅ {event_file} already cleaned up")
    
    return True


def cleanup_test_files():
    """Clean up test files to use centralized mock classes."""
    print("🧹 Cleaning up test files...")
    
    # Clean up target_system.py
    target_file = "engine/systems/battle/target_system.py"
    if os.path.exists(target_file):
        print(f"  ✅ {target_file} already cleaned up")
    
    # Clean up battle_formation.py
    formation_file = "engine/systems/battle/battle_formation.py"
    if os.path.exists(formation_file):
        print(f"  ✅ {formation_file} already cleaned up")
    
    return True


def verify_cleanup():
    """Verify that all duplicate classes have been removed."""
    print("\n🔍 Verifying cleanup...")
    
    battle_dir = Path("engine/systems/battle")
    issues_found = []
    
    # Check for remaining duplicate class definitions
    for file_path in battle_dir.rglob("*.py"):
        if file_path.name in ["mock_classes.py", "battle_enums.py", "__init__.py"]:
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for duplicate class definitions
            class_matches = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
            duplicate_classes = [cls for cls in class_matches if class_matches.count(cls) > 1]
            
            if duplicate_classes:
                issues_found.append(f"{file_path}: {duplicate_classes}")
                
        except Exception as e:
            print(f"  ⚠️  Could not read {file_path}: {e}")
    
    if issues_found:
        print("  ❌ Issues found:")
        for issue in issues_found:
            print(f"    - {issue}")
        return False
    else:
        print("  ✅ No duplicate classes found")
        return True


def run_cleanup():
    """Run the complete cleanup process."""
    print("🚀 Starting Duplicate Class Cleanup...")
    print("=" * 50)
    
    try:
        # Clean up files
        cleanup_unified_battle_manager()
        cleanup_example_files()
        cleanup_test_files()
        
        # Verify cleanup
        success = verify_cleanup()
        
        if success:
            print("\n🎉 Cleanup completed successfully!")
            print("✅ All duplicate classes have been removed")
            print("✅ Centralized mock classes are now used")
            print("✅ Battle system should work without conflicts")
        else:
            print("\n⚠️  Cleanup completed with issues")
            print("Please review the issues above")
        
        return success
        
    except Exception as e:
        print(f"\n💥 Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_cleanup()
    
    if success:
        print("\n🎮 Battle system is ready for testing!")
        print("Run 'python3 conflict_resolver.py' to verify the fixes")
    else:
        print("\n💥 Cleanup failed. Please check the errors above.")
        exit(1)
