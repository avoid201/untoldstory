#!/usr/bin/env python3
"""
COMPLETE BATTLE FLOW TEST
Testet alle Battle-System Features systematisch
"""

import sys
import os
import time
import traceback
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import battle system components
from engine.systems.battle.battle_controller import BattleState, BattleController
from engine.systems.battle.battle_enums import BattleResult, BattlePhase, BattleType
from engine.systems.battle.battle_actions import BattleActionExecutor, UnifiedAction
from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
from engine.systems.battle.meat_system import MeatSystem, MeatType
from engine.systems.monster_instance import MonsterInstance
from engine.systems.monsters import MonsterDatabase
from engine.systems.moves import MoveRegistry

class BattleFlowTester:
    """Umfassender Battle-System Tester"""
    
    def __init__(self):
        self.test_results = []
        self.issues_found = []
        self.performance_data = {}
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Logge Test-Ergebnis"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
    
    def log_issue(self, file_path: str, line: int, issue: str, solution: str):
        """Logge gefundenes Problem"""
        issue_data = {
            'file': file_path,
            'line': line,
            'issue': issue,
            'solution': solution
        }
        self.issues_found.append(issue_data)
        print(f"🚨 ISSUE: {file_path}:{line} - {issue}")
        print(f"    Lösung: {solution}")
    
    def create_test_monsters(self) -> tuple:
        """Erstelle Test-Monster"""
        try:
            # Get species from database
            from engine.systems.monsters import MonsterDatabase
            db = MonsterDatabase()
            species = db.get_species(1)  # Use ID 1 for slime
            
            if not species:
                # Create fallback species
                from engine.systems.monsters import MonsterSpecies
                species = MonsterSpecies(
                    id="slime",
                    name="Test Slime",
                    rank="D",
                    types=["normal"],
                    base_stats={'atk': 50, 'def': 40, 'mag': 45, 'res': 35, 'spd': 55}
                )
            
            # Player Monster
            player_monster = MonsterInstance(species=species, level=5, nickname="TestPlayer")
            player_monster.current_hp = 100
            player_monster.max_hp = 100
            
            # Enemy Monster
            enemy_monster = MonsterInstance(species=species, level=5, nickname="TestEnemy")
            enemy_monster.current_hp = 80
            enemy_monster.max_hp = 80
            
            return [player_monster], [enemy_monster]
            
        except Exception as e:
            self.log_issue("test_complete_battle_flow.py", 0, f"Monster creation failed: {e}", "Fix MonsterInstance constructor")
            return [], []
    
    def test_battle_initialization(self) -> bool:
        """Test 1: Battle Initialization"""
        try:
            player_team, enemy_team = self.create_test_monsters()
            if not player_team or not enemy_team:
                return False
            
            # Create battle state
            battle_state = BattleState(
                player_team=player_team,
                enemy_team=enemy_team,
                battle_type=BattleType.WILD,
                can_flee=True,
                can_catch=True
            )
            
            # Create controller - BattleController takes teams directly
            controller = BattleController(
                player_team=player_team,
                enemy_team=enemy_team,
                battle_type=BattleType.WILD,
                can_flee=True,
                can_catch=True
            )
            
            # Test initialization
            success = (
                battle_state.player_active is not None and
                battle_state.enemy_active is not None and
                battle_state.phase == BattlePhase.INIT and
                battle_state.can_flee and
                battle_state.can_catch
            )
            
            self.log_test("Battle Initialization", success, 
                         f"Player: {battle_state.player_active.name}, Enemy: {battle_state.enemy_active.name}")
            
            return success
            
        except Exception as e:
            self.log_issue("test_complete_battle_flow.py", 0, f"Battle init failed: {e}", "Check BattleState constructor")
            return False
    
    def test_battle_start(self) -> bool:
        """Test 2: Battle Start"""
        try:
            player_team, enemy_team = self.create_test_monsters()
            battle_state = BattleState(player_team, enemy_team, BattleType.WILD, True, True)
            controller = BattleController(player_team, enemy_team, BattleType.WILD, True, True)
            
            # Start battle
            start_time = time.time()
            battle_info = controller.start_battle()
            start_duration = time.time() - start_time
            
            self.performance_data['battle_start'] = start_duration
            
            success = (
                battle_info is not None and
                'player_active' in battle_info and
                'enemy_active' in battle_info and
                battle_state.phase == BattlePhase.INPUT
            )
            
            self.log_test("Battle Start", success, f"Duration: {start_duration:.3f}s")
            
            if start_duration > 0.1:
                self.log_issue("test_complete_battle_flow.py", 0, 
                             f"Battle start too slow: {start_duration:.3f}s", 
                             "Optimize battle initialization")
            
            return success
            
        except Exception as e:
            self.log_issue("test_complete_battle_flow.py", 0, f"Battle start failed: {e}", "Check start_battle method")
            return False
    
    def test_attack_action(self) -> bool:
        """Test 3: Attack Action"""
        try:
            player_team, enemy_team = self.create_test_monsters()
            battle_state = BattleState(player_team, enemy_team, BattleType.WILD, True, True)
            controller = BattleController(player_team, enemy_team, BattleType.WILD, True, True)
            controller.start_battle()
            
            # Create attack action
            from engine.systems.moves import Move, MoveCategory, MoveTarget
            test_move = Move(
                id="test_attack",
                name="Test Attack",
                type="normal",
                category=MoveCategory.PHYSICAL,
                power=30,
                accuracy=90,
                priority=0,
                targeting=MoveTarget.ENEMY,
                effects=[]
            )
            
            attack_action = BattleAction(
                action_type=ActionType.ATTACK,
                actor=battle_state.player_active,
                target=battle_state.enemy_active,
                move=test_move
            )
            
            # Execute attack
            start_time = time.time()
            controller.queue_player_action(attack_action)
            result = controller.execute_turn()
            attack_duration = time.time() - start_time
            
            self.performance_data['attack_action'] = attack_duration
            
            # Check if damage was dealt
            enemy_hp_before = 80  # Initial HP
            enemy_hp_after = battle_state.enemy_active.current_hp
            damage_dealt = enemy_hp_before - enemy_hp_after
            
            success = damage_dealt > 0 and result is not None
            
            self.log_test("Attack Action", success, 
                         f"Damage: {damage_dealt}, Duration: {attack_duration:.3f}s")
            
            if attack_duration > 0.05:
                self.log_issue("test_complete_battle_flow.py", 0,
                             f"Attack too slow: {attack_duration:.3f}s",
                             "Optimize damage calculation")
            
            return success
            
        except Exception as e:
            self.log_issue("test_complete_battle_flow.py", 0, f"Attack failed: {e}", "Check attack execution")
            return False
    
    def test_meat_system(self) -> bool:
        """Test 4: Meat System"""
        try:
            player_team, enemy_team = self.create_test_monsters()
            battle_state = BattleState(player_team, enemy_team, BattleType.WILD, True, True)
            controller = BattleController(player_team, enemy_team, BattleType.WILD, True, True)
            controller.start_battle()
            
            # Test meat usage
            meat_action = BattleAction(
                action_type=ActionType.USE_MEAT,
                actor=battle_state.player_active,
                target=battle_state.player_active,
                meat_type=MeatType.SUPER
            )
            
            start_time = time.time()
            controller.queue_player_action(meat_action)
            result = controller.execute_turn()
            meat_duration = time.time() - start_time
            
            self.performance_data['meat_usage'] = meat_duration
            
            # Check meat system state
            meat_active = battle_state.meat_system.get_active_meat_name()
            meat_bonus = battle_state.meat_system.get_taming_bonus()
            
            success = (
                meat_active is not None and
                meat_bonus > 0 and
                result is not None
            )
            
            self.log_test("Meat System", success,
                         f"Active: {meat_active}, Bonus: {meat_bonus}%, Duration: {meat_duration:.3f}s")
            
            return success
            
        except Exception as e:
            self.log_issue("test_complete_battle_flow.py", 0, f"Meat system failed: {e}", "Check MeatSystem implementation")
            return False
    
    def test_taming_action(self) -> bool:
        """Test 5: Taming Action"""
        try:
            player_team, enemy_team = self.create_test_monsters()
            battle_state = BattleState(player_team, enemy_team, BattleType.WILD, True, True)
            controller = BattleController(player_team, enemy_team, BattleType.WILD, True, True)
            controller.start_battle()
            
            # Use meat first
            meat_action = BattleAction(
                action_type=ActionType.USE_MEAT,
                actor=battle_state.player_active,
                target=battle_state.player_active,
                meat_type=MeatType.SUPER
            )
            controller.queue_player_action(meat_action)
            controller.execute_turn()
            
            # Now try taming
            tame_action = BattleAction(
                action_type=ActionType.TAME,
                actor=battle_state.player_active,
                target=battle_state.enemy_active,
                meat_system=battle_state.meat_system
            )
            
            start_time = time.time()
            controller.queue_player_action(tame_action)
            result = controller.execute_turn()
            tame_duration = time.time() - start_time
            
            self.performance_data['taming'] = tame_duration
            
            # Check if taming was attempted (success is random)
            success = result is not None
            
            self.log_test("Taming Action", success, f"Duration: {tame_duration:.3f}s")
            
            return success
            
        except Exception as e:
            self.log_issue("test_complete_battle_flow.py", 0, f"Taming failed: {e}", "Check taming implementation")
            return False
    
    def test_scout_action(self) -> bool:
        """Test 6: Scout Action"""
        try:
            player_team, enemy_team = self.create_test_monsters()
            battle_state = BattleState(player_team, enemy_team, BattleType.WILD, True, True)
            controller = BattleController(player_team, enemy_team, BattleType.WILD, True, True)
            controller.start_battle()
            
            # Create scout action
            scout_action = BattleAction(
                action_type=ActionType.SCOUT,
                actor=battle_state.player_active,
                target=battle_state.enemy_active
            )
            
            start_time = time.time()
            controller.queue_player_action(scout_action)
            result = controller.execute_turn()
            scout_duration = time.time() - start_time
            
            self.performance_data['scout'] = scout_duration
            
            # Check if scout info was generated
            battle_log_has_scout = any("späht" in log or "scout" in log.lower() for log in battle_state.battle_log)
            
            success = result is not None and battle_log_has_scout
            
            self.log_test("Scout Action", success, f"Duration: {scout_duration:.3f}s")
            
            return success
            
        except Exception as e:
            self.log_issue("test_complete_battle_flow.py", 0, f"Scout failed: {e}", "Check scout implementation")
            return False
    
    def test_status_effects(self) -> bool:
        """Test 7: Status Effects"""
        try:
            player_team, enemy_team = self.create_test_monsters()
            battle_state = BattleState(player_team, enemy_team, BattleType.WILD, True, True)
            controller = BattleController(player_team, enemy_team, BattleType.WILD, True, True)
            controller.start_battle()
            
            # Apply status effect manually for testing
            from engine.systems.monster_instance import StatusCondition
            battle_state.enemy_active.apply_status(StatusCondition.POISON)
            
            # Process status effects
            start_time = time.time()
            controller._process_status_effects()
            status_duration = time.time() - start_time
            
            self.performance_data['status_effects'] = status_duration
            
            # Check if status was processed
            has_poison = battle_state.enemy_active.status == StatusCondition.POISON
            
            success = has_poison and status_duration < 0.01
            
            self.log_test("Status Effects", success, f"Duration: {status_duration:.3f}s")
            
            if status_duration > 0.01:
                self.log_issue("test_complete_battle_flow.py", 0,
                             f"Status effects too slow: {status_duration:.3f}s",
                             "Optimize status effect processing")
            
            return success
            
        except Exception as e:
            self.log_issue("test_complete_battle_flow.py", 0, f"Status effects failed: {e}", "Check status system")
            return False
    
    def test_battle_end_conditions(self) -> bool:
        """Test 8: Battle End Conditions"""
        try:
            player_team, enemy_team = self.create_test_monsters()
            battle_state = BattleState(player_team, enemy_team, BattleType.WILD, True, True)
            controller = BattleController(player_team, enemy_team, BattleType.WILD, True, True)
            controller.start_battle()
            
            # Test victory condition
            battle_state.enemy_active.current_hp = 0
            battle_state.enemy_active.is_fainted = True
            
            start_time = time.time()
            result = controller.check_battle_end()
            end_duration = time.time() - start_time
            
            self.performance_data['battle_end_check'] = end_duration
            
            success = result == BattleResult.VICTORY
            
            self.log_test("Battle End Conditions", success, f"Result: {result}, Duration: {end_duration:.3f}s")
            
            return success
            
        except Exception as e:
            self.log_issue("test_complete_battle_flow.py", 0, f"Battle end check failed: {e}", "Check battle end logic")
            return False
    
    def test_rewards_system(self) -> bool:
        """Test 9: Rewards System"""
        try:
            player_team, enemy_team = self.create_test_monsters()
            battle_state = BattleState(player_team, enemy_team, BattleType.WILD, True, True)
            controller = BattleController(player_team, enemy_team, BattleType.WILD, True, True)
            controller.start_battle()
            
            # Simulate victory
            battle_state.enemy_active.current_hp = 0
            battle_state.enemy_active.is_fainted = True
            
            start_time = time.time()
            controller._calculate_rewards()
            rewards_duration = time.time() - start_time
            
            self.performance_data['rewards_calculation'] = rewards_duration
            
            # Check if rewards were calculated
            has_exp = battle_state.exp_earned > 0
            has_money = battle_state.money_earned > 0
            
            success = has_exp and has_money
            
            self.log_test("Rewards System", success,
                         f"EXP: {battle_state.exp_earned}, Money: {battle_state.money_earned}, Duration: {rewards_duration:.3f}s")
            
            return success
            
        except Exception as e:
            self.log_issue("test_complete_battle_flow.py", 0, f"Rewards failed: {e}", "Check reward system")
            return False
    
    def test_performance_bottlenecks(self) -> bool:
        """Test 10: Performance Analysis"""
        try:
            # Analyze performance data
            slow_operations = []
            
            for operation, duration in self.performance_data.items():
                if duration > 0.05:  # 50ms threshold
                    slow_operations.append((operation, duration))
            
            if slow_operations:
                self.log_issue("test_complete_battle_flow.py", 0,
                             f"Slow operations: {slow_operations}",
                             "Optimize slow battle operations")
                success = False
            else:
                success = True
            
            self.log_test("Performance Analysis", success,
                         f"All operations under 50ms threshold")
            
            return success
            
        except Exception as e:
            self.log_issue("test_complete_battle_flow.py", 0, f"Performance analysis failed: {e}", "Check performance monitoring")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Führe alle Tests aus"""
        print("🚀 STARTING COMPLETE BATTLE FLOW TESTS")
        print("=" * 50)
        
        tests = [
            self.test_battle_initialization,
            self.test_battle_start,
            self.test_attack_action,
            self.test_meat_system,
            self.test_taming_action,
            self.test_scout_action,
            self.test_status_effects,
            self.test_battle_end_conditions,
            self.test_rewards_system,
            self.test_performance_bottlenecks
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ FAIL {test.__name__} - Exception: {e}")
                traceback.print_exc()
        
        print("=" * 50)
        print(f"📊 RESULTS: {passed}/{total} tests passed")
        print(f"🚨 ISSUES FOUND: {len(self.issues_found)}")
        
        return {
            'passed': passed,
            'total': total,
            'success_rate': passed / total,
            'issues': self.issues_found,
            'performance': self.performance_data
        }

def main():
    """Main test function"""
    tester = BattleFlowTester()
    results = tester.run_all_tests()
    
    # Save results to file
    import json
    with open('/Users/leon/Desktop/untold_story/BATTLE_TEST_RESULTS.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to BATTLE_TEST_RESULTS.json")
    
    return results['success_rate'] > 0.8

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
