#!/usr/bin/env python3
"""
Test script for Item System Battle Integration
Tests the integrated item functionality in battles
"""

import sys
import os
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import pygame
from engine.core.game import Game
from engine.scenes.battle_scene import BattleScene
from engine.systems.monster_instance import MonsterInstance, MonsterSpecies
from engine.systems.stats import BaseStats
from engine.systems.items import item_registry, Inventory

def create_test_monster(name: str, level: int, hp_percent: float = 1.0) -> MonsterInstance:
    """Create a test monster for battle."""
    species = MonsterSpecies(
        id=name.lower(),
        name=name,
        types=["Bestie"],
        base_stats=BaseStats(hp=60, atk=50, def_=45, mag=40, res=40, spd=55)
    )
    
    monster = MonsterInstance(species=species, level=level)
    monster.current_hp = int(monster.max_hp * hp_percent)
    return monster

def test_item_system():
    """Test the item system integration."""
    print("=" * 60)
    print("ITEM SYSTEM INTEGRATION TEST")
    print("=" * 60)
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    logical_surface = pygame.Surface((320, 180))
    
    # Create game
    game = Game(screen, logical_surface, (320, 180), (1280, 720), 4)
    game.debug_mode = True
    
    # Test 1: Check item registry
    print("\n1. Testing Item Registry...")
    print(f"   Total items loaded: {len(item_registry.items)}")
    
    # Show some items
    healing_items = []
    for item_id, item in item_registry.items.items():
        if item.category.name == 'HEALING' and item.use_in_battle:
            healing_items.append(item)
            if len(healing_items) <= 3:
                print(f"   - {item.name}: {item.description}")
    
    # Test 2: Check inventory system
    print("\n2. Testing Inventory System...")
    inventory = game.inventory
    
    # Add test items
    inventory.add_item('trank', 5)
    inventory.add_item('supertrank', 3)
    inventory.add_item('gegengift', 2)
    inventory.add_item('fleisch', 1)
    
    print(f"   Items in inventory: {len(inventory.items)}")
    for item_id, count in inventory.get_all_items():
        item = item_registry.get_item(item_id)
        if item:
            print(f"   - {item.name} x{count}")
    
    # Test 3: Create battle with injured monster
    print("\n3. Setting up Battle Scene...")
    
    # Create teams
    player_team = [
        create_test_monster("Ruhri", 10, hp_percent=0.5),  # 50% HP
        create_test_monster("Potti", 8, hp_percent=1.0)
    ]
    enemy_team = [create_test_monster("Wildes Viech", 7)]
    
    print(f"   Player Monster: {player_team[0].name} - {player_team[0].current_hp}/{player_team[0].max_hp} HP")
    print(f"   Enemy Monster: {enemy_team[0].name} - {enemy_team[0].current_hp}/{enemy_team[0].max_hp} HP")
    
    # Push battle scene
    try:
        game.push_scene(
            BattleScene,
            player_team=player_team,
            enemy_team=enemy_team,
            is_wild=True
        )
        print("   Battle scene created successfully!")
    except Exception as e:
        print(f"   ERROR creating battle scene: {e}")
        return
    
    # Test 4: Test item effects
    print("\n4. Testing Item Effects...")
    
    from engine.systems.items import ItemEffectExecutor
    executor = ItemEffectExecutor()
    
    # Test healing item
    trank = item_registry.get_item('trank')
    if trank:
        print(f"   Testing {trank.name} on {player_team[0].name}...")
        old_hp = player_team[0].current_hp
        messages = executor.execute_item_effects(
            item=trank,
            target=player_team[0]
        )
        new_hp = player_team[0].current_hp
        print(f"   HP: {old_hp} -> {new_hp} ({new_hp - old_hp:+d})")
        for msg in messages:
            if msg:
                print(f"   Message: {msg}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)
    print("\nInstructions for manual testing:")
    print("1. Press '3' or 'I' to open item menu")
    print("2. Use arrow keys to navigate categories")
    print("3. Select an item with Enter to use it")
    print("4. Items should heal your monster and consume from inventory")
    print("\nPress ESC to exit the test")
    
    # Run a few frames to ensure everything is loaded
    clock = pygame.time.Clock()
    for _ in range(5):
        game._process_events()
        game._update(0.016)
        game._draw()
        game._present()
        clock.tick(60)
    
    # Keep window open for manual testing
    print("\nWindow is open for manual testing...")
    try:
        while game.running:
            dt = clock.tick(60) / 1000.0
            game._process_events()
            game._update(dt)
            game._draw()
            game._present()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    
    pygame.quit()
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_item_system()
