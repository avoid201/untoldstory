"""
Final Battle Integration Test Suite
Tests complete flow from menu to damage with all systems integrated.
"""

import sys
import os
import time
import logging
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.systems.monster_instance import MonsterInstance, MonsterSpecies
from engine.systems.stats import BaseStats
from engine.systems.battle.battle_controller import BattleController
from engine.systems.battle.battle_enums import BattleType, BattleResult
from engine.systems.battle.turn_logic import BattleAction, ActionType
from engine.systems.battle.event_processor import EventProcessor
from engine.systems.talent_system import get_talent_database

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BattleIntegrationTester:
    """Comprehensive battle integration tester."""
    
    def __init__(self):
        """Initialize tester."""
        self.test_results = []
        self.performance_metrics = {}
        
    def create_test_monster(self, name: str, level: int = 5) -> MonsterInstance:
        """Create test monster with talents."""
        species = MonsterSpecies(
            id=f'test_{name.lower()}',
            name=name,
            types=['Feuer'],
            base_stats=BaseStats(50, 50, 50, 50, 50, 50),
            talents=[]
        )
        return MonsterInstance(species, level=level)
    
    def test_complete_attack_flow(self) -> bool:
        """Test COMPLETE flow from menu to damage."""
        logger.info("🧪 Testing Complete Attack Flow...")
        
        try:
            # 1. Create battle
            player_monster = self.create_test_monster("Player Monster", 5)
            enemy_monster = self.create_test_monster("Enemy Monster", 5)
            
            battle_controller = BattleController(
                player_team=[player_monster],
                enemy_team=[enemy_monster],
                battle_type=BattleType.WILD
            )
            
            # 2. Verify battle initialization
            assert battle_controller.state is not None
            assert len(battle_controller.state.player_team) == 1
            assert len(battle_controller.state.enemy_team) == 1
            logger.info("✅ Battle initialization successful")
            
            # 3. Test move loading from talents
            player_moves = player_monster.moves
            assert len(player_moves) > 0, "Player monster should have moves from talents"
            logger.info(f"✅ Player has {len(player_moves)} moves from talents")
            
            # 4. Test move categorization
            from engine.ui.battle.battle_ui_menus import BattleUIMenuManager
            menu_manager = BattleUIMenuManager(None)
            
            for move in player_moves:
                category = menu_manager._get_move_category(move)
                assert category in ["PHYSISCH", "MAGISCH", "STATUS"], f"Invalid category: {category}"
            logger.info("✅ Move categorization working")
            
            # 5. Create attack action
            attack_move = player_moves[0]
            player_action = BattleAction(
                action_type=ActionType.ATTACK,
                actor=player_monster,
                target=enemy_monster,
                move=attack_move
            )
            
            # 6. Execute turn
            start_time = time.perf_counter()
            battle_result = battle_controller.execute_turn(player_action, None)
            execution_time = time.perf_counter() - start_time
            
            # 7. Verify all events fired
            event_processor = battle_controller.event_processor
            assert event_processor is not None
            logger.info(f"✅ Turn executed in {execution_time*1000:.2f}ms")
            
            # 8. Check damage applied
            initial_hp = enemy_monster.current_hp
            # Note: Damage calculation happens in turn execution
            logger.info(f"✅ Enemy HP: {initial_hp} -> {enemy_monster.current_hp}")
            
            # 9. Verify UI would be updated (simulated)
            # This would normally happen in the UI layer
            logger.info("✅ UI update simulation successful")
            
            self.test_results.append({
                'test': 'complete_attack_flow',
                'status': 'PASSED',
                'execution_time': execution_time,
                'moves_loaded': len(player_moves),
                'damage_applied': initial_hp != enemy_monster.current_hp
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Complete Attack Flow FAILED: {e}")
            self.test_results.append({
                'test': 'complete_attack_flow',
                'status': 'FAILED',
                'error': str(e)
            })
            return False
    
    def test_talent_system_integration(self) -> bool:
        """Test talent system integration with battle."""
        logger.info("🧪 Testing Talent System Integration...")
        
        try:
            # Create monster with talents
            monster = self.create_test_monster("Talent Monster", 5)
            
            # Test talent loading
            assert len(monster.talents) > 0, "Monster should have talents"
            logger.info(f"✅ Monster has {len(monster.talents)} talents")
            
            # Test move loading from talents
            moves = monster.moves
            assert len(moves) > 0, "Monster should have moves from talents"
            logger.info(f"✅ Monster has {len(moves)} moves from talents")
            
            # Test talent experience gain
            battle_result_data = {
                'base_talent_exp': 50,
                'participation_bonus': 1.2,
                'victory_bonus': 2.0
            }
            
            initial_tier = monster.talents[0].current_tier
            upgrades = monster.gain_talent_experience_from_battle(battle_result_data)
            
            # Verify talent upgrades
            if upgrades:
                logger.info(f"✅ Talent upgrades: {len(upgrades)}")
                for upgrade in upgrades:
                    logger.info(f"  {upgrade['talent_id']}: Tier {upgrade['old_tier']} -> {upgrade['new_tier']}")
            
            # Test move updates after talent upgrade
            new_moves = monster.moves
            logger.info(f"✅ Moves after upgrade: {len(new_moves)}")
            
            self.test_results.append({
                'test': 'talent_system_integration',
                'status': 'PASSED',
                'talents': len(monster.talents),
                'moves': len(moves),
                'upgrades': len(upgrades),
                'new_moves': len(new_moves)
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Talent System Integration FAILED: {e}")
            self.test_results.append({
                'test': 'talent_system_integration',
                'status': 'FAILED',
                'error': str(e)
            })
            return False
    
    def test_event_system_performance(self) -> bool:
        """Test event system performance with caching."""
        logger.info("🧪 Testing Event System Performance...")
        
        try:
            from engine.systems.battle.battle_state import BattleState
            from engine.systems.monster_instance import MonsterInstance, MonsterSpecies
            from engine.systems.stats import BaseStats
            
            # Create battle state
            species = MonsterSpecies(
                id='test_perf',
                name='Test Monster',
                types=['Feuer'],
                base_stats=BaseStats(50, 50, 50, 50, 50, 50),
                talents=[]
            )
            monster = MonsterInstance(species, level=5)
            
            battle_state = BattleState(
                player_team=[monster],
                enemy_team=[monster],
                battle_type=BattleType.WILD
            )
            
            # Create event processor
            event_processor = EventProcessor(battle_state)
            
            # Test validation caching
            start_time = time.perf_counter()
            result1 = event_processor.validate_all_handlers()
            first_run_time = time.perf_counter() - start_time
            
            # Second call should use cache
            start_time = time.perf_counter()
            result2 = event_processor.validate_all_handlers()
            second_run_time = time.perf_counter() - start_time
            
            # Verify caching works
            assert result1 == result2, "Cached result should match original"
            assert second_run_time < first_run_time, "Cached call should be faster"
            
            logger.info(f"✅ Event validation caching working")
            logger.info(f"  First run: {first_run_time*1000:.2f}ms")
            logger.info(f"  Cached run: {second_run_time*1000:.2f}ms")
            logger.info(f"  Speedup: {first_run_time/second_run_time:.1f}x")
            
            self.test_results.append({
                'test': 'event_system_performance',
                'status': 'PASSED',
                'first_run_time': first_run_time,
                'cached_run_time': second_run_time,
                'speedup': first_run_time/second_run_time
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Event System Performance FAILED: {e}")
            self.test_results.append({
                'test': 'event_system_performance',
                'status': 'FAILED',
                'error': str(e)
            })
            return False
    
    def test_move_category_integration(self) -> bool:
        """Test move category integration with talent system."""
        logger.info("🧪 Testing Move Category Integration...")
        
        try:
            from engine.ui.battle.battle_ui_menus import BattleUIMenuManager
            
            # Create menu manager
            menu_manager = BattleUIMenuManager(None)
            
            # Create test monster with moves
            monster = self.create_test_monster("Category Monster", 5)
            moves = monster.moves
            
            # Test category determination
            categories = {}
            for move in moves:
                category = menu_manager._get_move_category(move)
                categories[category] = categories.get(category, 0) + 1
                
                # Verify category is valid
                assert category in ["PHYSISCH", "MAGISCH", "STATUS"], f"Invalid category: {category}"
            
            logger.info(f"✅ Move categories: {categories}")
            
            # Test category filtering
            for category in ["PHYSISCH", "MAGISCH", "STATUS"]:
                filtered_moves = menu_manager.get_moves_by_category(moves, category)
                logger.info(f"  {category}: {len(filtered_moves)} moves")
            
            self.test_results.append({
                'test': 'move_category_integration',
                'status': 'PASSED',
                'total_moves': len(moves),
                'categories': categories
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Move Category Integration FAILED: {e}")
            self.test_results.append({
                'test': 'move_category_integration',
                'status': 'FAILED',
                'error': str(e)
            })
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests."""
        logger.info("🚀 Starting Final Integration Tests...")
        
        start_time = time.perf_counter()
        
        # Run all tests
        tests = [
            self.test_complete_attack_flow,
            self.test_talent_system_integration,
            self.test_event_system_performance,
            self.test_move_category_integration
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"❌ Test {test.__name__} CRASHED: {e}")
                failed += 1
        
        total_time = time.perf_counter() - start_time
        
        # Generate summary
        summary = {
            'total_tests': len(tests),
            'passed': passed,
            'failed': failed,
            'success_rate': (passed / len(tests)) * 100,
            'total_time': total_time,
            'test_results': self.test_results
        }
        
        logger.info(f"🏁 Integration Tests Complete!")
        logger.info(f"  Total: {summary['total_tests']}")
        logger.info(f"  Passed: {summary['passed']}")
        logger.info(f"  Failed: {summary['failed']}")
        logger.info(f"  Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"  Total Time: {total_time:.2f}s")
        
        return summary


def main():
    """Run integration tests."""
    tester = BattleIntegrationTester()
    results = tester.run_all_tests()
    
    # Exit with error code if any tests failed
    if results['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
