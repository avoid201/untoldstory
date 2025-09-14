#!/usr/bin/env python3
"""
Test script for DQM Systems Integration
Tests all the integrated DQM systems and their connections.
"""

import sys
import os
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_dqm_integration():
    """Test the complete DQM integration."""
    try:
        logger.info("=== Testing DQM Systems Integration ===")
        
        # Test 1: Setup DQM systems
        logger.info("1. Testing DQM systems setup...")
        from engine.systems.battle.dqm_integration import setup_dqm_systems
        setup_dqm_systems()
        logger.info("✓ DQM systems setup completed")
        
        # Test 2: Test meat system
        logger.info("2. Testing meat system...")
        from engine.systems.battle.meat_system import get_meat_system
        meat_system = get_meat_system()
        
        # Test meat inventory
        available_meat = meat_system.get_available_meat()
        logger.info(f"✓ Available meat types: {list(available_meat.keys())}")
        
        # Test 3: Test meat-item bridge
        logger.info("3. Testing meat-item bridge...")
        from engine.systems.battle.meat_system import get_meat_system
        
        # Test meat system integration
        meat_system = get_meat_system()
        meat_type = meat_system.get_meat_type_from_item_id('fleisch')
        logger.info(f"✓ 'fleisch' maps to: {meat_type}")
        
        is_meat = meat_system.is_meat_item('fleisch')
        logger.info(f"✓ 'fleisch' is meat item: {is_meat}")
        
        # Test 4: Test move system with DQM defaults
        logger.info("4. Testing move system with DQM defaults...")
        from engine.systems.moves import move_registry
        
        # Test move creation with DQM fields
        test_move_data = {
            "id": "test_dqm_move",
            "name": "Test DQM Move",
            "type": "Feuer",
            "category": "mag",
            "power": 50,
            "accuracy": 100,
            "priority": 0,
            "targeting": "enemy",
            "effects": [],
            "description": "A test move with DQM fields",
            "drain_percent": 0.25,  # 25% drain
            "recoil_percent": 0.1,  # 10% recoil
            "multi_hit_min": 2,
            "multi_hit_max": 5
        }
        
        from engine.systems.moves import Move, MoveCategory, MoveTarget, MoveEffect, EffectKind
        test_move = Move.from_dict(test_move_data)
        logger.info(f"✓ Created test move with drain_percent: {test_move.drain_percent}")
        logger.info(f"✓ Created test move with recoil_percent: {test_move.recoil_percent}")
        logger.info(f"✓ Created test move with multi_hit: {test_move.multi_hit_min}-{test_move.multi_hit_max}")
        
        # Test 5: Test monster database with traits
        logger.info("5. Testing monster database with traits...")
        from engine.systems.monsters import get_monster_database
        monster_db = get_monster_database()
        
        # Test species creation with traits
        test_species_data = {
            "id": "999",
            "name": "Test Monster",
            "types": ["Feuer", "Bestie"],
            "base_stats": {"hp": 100, "atk": 80, "def": 70, "mag": 90, "res": 75, "spd": 85},
            "rank": "C",
            "description": "A test monster with traits",
            "traits": ["Metal Body", "Fire Immunity"],
            "abilities": ["Test Ability"],
            "catch_rate": 100,
            "era": "present"
        }
        
        from engine.systems.monster_instance import MonsterSpecies
        test_species = MonsterSpecies(
            id=test_species_data["id"],
            name=test_species_data["name"],
            types=test_species_data["types"],
            base_stats=test_species_data["base_stats"],
            rank=test_species_data["rank"],
            description=test_species_data["description"],
            traits=test_species_data["traits"],
            abilities=test_species_data["abilities"],
            catch_rate=test_species_data["catch_rate"],
            era=test_species_data["era"]
        )
        
        logger.info(f"✓ Created test species with traits: {test_species.traits}")
        logger.info(f"✓ Created test species with abilities: {test_species.abilities}")
        
        # Test 6: Test DQM skills integration
        logger.info("6. Testing DQM skills integration...")
        from engine.systems.battle.skills_dqm_integrated import get_skill_database
        skill_db = get_skill_database()
        
        # Test skill family creation
        skill_family = skill_db.get_skill_family_from_talent("fire_i")
        if skill_family:
            logger.info(f"✓ Created skill family: {skill_family.family_name}")
            logger.info(f"✓ Skill family element: {skill_family.element}")
            logger.info(f"✓ Skill family type: {skill_family.skill_type}")
            logger.info(f"✓ Number of tiers: {len(skill_family.tiers)}")
        else:
            logger.warning("⚠ No fire_i talent found - this is expected if talents.json is not loaded")
        
        # Test 7: Test items system with meat integration
        logger.info("7. Testing items system with meat integration...")
        from engine.systems.items import ItemManager, Inventory
        
        # Create test inventory
        test_inventory = Inventory()
        test_inventory.add_item("fleisch", 3)
        test_inventory.add_item("edelfleisch", 1)
        
        # Create item manager
        item_manager = ItemManager(test_inventory)
        
        # Test meat inventory sync
        item_manager.sync_meat_inventory()
        logger.info("✓ Meat inventory synced with item inventory")
        
        logger.info("=== All DQM Integration Tests Completed Successfully! ===")
        return True
        
    except Exception as e:
        logger.error(f"❌ DQM Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance():
    """Test performance of the integrated systems."""
    import time
    
    logger.info("=== Testing Performance ===")
    
    # Test monster database performance
    start_time = time.time()
    from engine.systems.monsters import get_monster_database
    monster_db = get_monster_database()
    load_time = time.time() - start_time
    
    logger.info(f"✓ Monster database load time: {load_time:.3f}s")
    
    # Test performance stats
    perf_stats = monster_db.get_performance_stats()
    logger.info(f"✓ Total species loaded: {perf_stats['total_species']}")
    logger.info(f"✓ Cache hit rate: {perf_stats['cache_hit_rate']:.2%}")
    
    # Test move registry performance
    start_time = time.time()
    from engine.systems.moves import move_registry
    move_count = len(move_registry.get_all_moves())
    load_time = time.time() - start_time
    
    logger.info(f"✓ Move registry load time: {load_time:.3f}s")
    logger.info(f"✓ Total moves loaded: {move_count}")

if __name__ == "__main__":
    success = test_dqm_integration()
    test_performance()
    
    if success:
        print("\n🎉 All DQM integration tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some DQM integration tests failed!")
        sys.exit(1)
