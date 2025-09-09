#!/usr/bin/env python3
"""Test-Skript für das Save-System"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.systems.save import SaveSystem, SaveMetadata

def test_save_system():
    """Test the save system functionality"""
    print("=" * 50)
    print("SAVE SYSTEM TEST")
    print("=" * 50)
    
    # Create save system
    save_system = SaveSystem()
    print(f"✓ Save system initialized")
    print(f"  Save directory: {save_system.save_dir}")
    print(f"  Backup directory: {save_system.backup_dir}")
    
    # Check existing saves
    print("\n📁 Checking existing saves...")
    all_saves = save_system.get_all_saves()
    
    for i, metadata in enumerate(all_saves):
        if metadata:
            print(f"\n  Slot {i+1}:")
            print(f"    Name: {metadata.name}")
            print(f"    Level: {metadata.level}")
            print(f"    Badges: {metadata.badges}")
            print(f"    Monsters: {metadata.monsters_caught}")
            hours = int(metadata.playtime // 3600)
            minutes = int((metadata.playtime % 3600) // 60)
            print(f"    Playtime: {hours:02d}:{minutes:02d}")
            print(f"    Location: {metadata.location}")
            print(f"    Version: {metadata.version}")
        else:
            print(f"  Slot {i+1}: Empty")
    
    # Test save functionality
    print("\n💾 Testing save functionality...")
    
    # Create test game data
    test_data = {
        'player': {
            'name': 'TestPlayer',
            'position': (100, 200),
            'current_map': 'test_map',
            'facing': 'down'
        },
        'party_manager': {
            'party': {
                'members': [
                    {'level': 10, 'species': 'TestMon', 'current_hp': 50, 'max_hp': 50}
                ]
            }
        },
        'story': {
            'flags': {
                'game_started': True,
                'trial_1_defeated': True
            }
        },
        'quests': {
            'active': [],
            'completed': []
        },
        'inventory': {
            'items': {},
            'money': 1000
        },
        'storage': {
            'boxes': []
        },
        'playtime': 3661  # 1 hour, 1 minute, 1 second
    }
    
    # Try to save to slot 3 (usually empty for testing)
    print("  Attempting to save to slot 3...")
    success = save_system.save_game(3, test_data, "TestSave")
    
    if success:
        print("  ✓ Save successful!")
        
        # Verify the save
        print("\n🔍 Verifying saved data...")
        loaded_data = save_system.load_game(3)
        
        if loaded_data:
            print("  ✓ Save loaded successfully!")
            
            # Check key data
            if loaded_data.get('player', {}).get('name') == 'TestPlayer':
                print("  ✓ Player data intact")
            else:
                print("  ✗ Player data mismatch")
            
            if loaded_data.get('inventory', {}).get('money') == 1000:
                print("  ✓ Inventory data intact")
            else:
                print("  ✗ Inventory data mismatch")
                
            # Check metadata
            new_metadata = save_system.get_save_metadata(3)
            if new_metadata:
                print(f"  ✓ Metadata created: {new_metadata.name}")
            else:
                print("  ✗ Metadata creation failed")
        else:
            print("  ✗ Failed to load saved game")
    else:
        print("  ✗ Save failed!")
    
    # Check save files
    print("\n📂 Checking save files...")
    save_dir = Path("saves")
    if save_dir.exists():
        save_files = list(save_dir.glob("*.sav"))
        print(f"  Found {len(save_files)} save files:")
        for save_file in save_files:
            size_kb = save_file.stat().st_size / 1024
            print(f"    - {save_file.name} ({size_kb:.2f} KB)")
        
        # Check backups
        backup_dir = save_dir / "backups"
        if backup_dir.exists():
            backup_files = list(backup_dir.glob("*.sav"))
            print(f"\n  Found {len(backup_files)} backup files:")
            for backup_file in backup_files[:5]:  # Show max 5
                size_kb = backup_file.stat().st_size / 1024
                print(f"    - {backup_file.name} ({size_kb:.2f} KB)")
    else:
        print("  ✗ Save directory does not exist!")
    
    # Test quick save
    print("\n⚡ Testing quick save...")
    quick_success = save_system.quick_save(test_data)
    if quick_success:
        print("  ✓ Quick save successful!")
        
        # Try to load
        quick_data = save_system.quick_load()
        if quick_data:
            print("  ✓ Quick load successful!")
        else:
            print("  ✗ Quick load failed!")
    else:
        print("  ✗ Quick save failed!")
    
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)
    
    return success

if __name__ == "__main__":
    try:
        success = test_save_system()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
