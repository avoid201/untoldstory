#!/usr/bin/env python3
"""
BATTLE PERFORMANCE TEST
Detaillierte Performance-Analyse des Battle-Systems
"""

import sys
import os
import time
import cProfile
import pstats
from typing import Dict, Any, List
import statistics

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.systems.battle.battle_controller import BattleState, BattleController
from engine.systems.battle.battle_enums import BattleResult, BattlePhase, BattleType
from engine.systems.battle.battle_actions import BattleActionExecutor, UnifiedAction
from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
from engine.systems.battle.meat_system import MeatSystem, MeatType
from engine.systems.monster_instance import MonsterInstance
from engine.systems.monsters import MonsterDatabase
from engine.systems.moves import MoveRegistry

class BattlePerformanceTester:
    """Detaillierte Performance-Analyse"""
    
    def __init__(self):
        self.performance_data = {}
        self.bottlenecks = []
        
    def create_test_monsters(self) -> tuple:
        """Erstelle Test-Monster für Performance-Tests"""
        try:
            from engine.systems.monsters import MonsterDatabase
            db = MonsterDatabase()
            species = db.get_species(1)
            
            if not species:
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
            print(f"Monster creation failed: {e}")
            return [], []
    
    def measure_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """Messe die Performance einer Operation"""
        times = []
        
        # Warmup
        for _ in range(3):
            try:
                operation_func(*args, **kwargs)
            except:
                pass
        
        # Actual measurement
        for _ in range(10):
            start_time = time.perf_counter()
            try:
                result = operation_func(*args, **kwargs)
                end_time = time.perf_counter()
                times.append(end_time - start_time)
            except Exception as e:
                print(f"Operation {operation_name} failed: {e}")
                times.append(float('inf'))
        
        # Calculate statistics
        valid_times = [t for t in times if t != float('inf')]
        if valid_times:
            self.performance_data[operation_name] = {
                'min': min(valid_times),
                'max': max(valid_times),
                'mean': statistics.mean(valid_times),
                'median': statistics.median(valid_times),
                'std': statistics.stdev(valid_times) if len(valid_times) > 1 else 0,
                'samples': len(valid_times)
            }
            
            # Check for bottlenecks
            if statistics.mean(valid_times) > 0.05:  # 50ms threshold
                self.bottlenecks.append({
                    'operation': operation_name,
                    'avg_time': statistics.mean(valid_times),
                    'max_time': max(valid_times)
                })
        else:
            self.performance_data[operation_name] = {
                'error': 'All operations failed'
            }
    
    def test_battle_initialization_performance(self):
        """Test Battle Initialization Performance"""
        print("🔧 Testing Battle Initialization Performance...")
        
        def init_battle():
            player_team, enemy_team = self.create_test_monsters()
            battle_state = BattleState(player_team, enemy_team, BattleType.WILD, True, True)
            controller = BattleController(player_team, enemy_team, BattleType.WILD, True, True)
            return battle_state, controller
        
        self.measure_operation("Battle Initialization", init_battle)
    
    def test_battle_start_performance(self):
        """Test Battle Start Performance"""
        print("🚀 Testing Battle Start Performance...")
        
        def start_battle():
            player_team, enemy_team = self.create_test_monsters()
            battle_state = BattleState(player_team, enemy_team, BattleType.WILD, True, True)
            controller = BattleController(player_team, enemy_team, BattleType.WILD, True, True)
            return controller.start_battle()
        
        self.measure_operation("Battle Start", start_battle)
    
    def test_action_execution_performance(self):
        """Test Action Execution Performance"""
        print("⚔️ Testing Action Execution Performance...")
        
        def execute_attack():
            player_team, enemy_team = self.create_test_monsters()
            battle_state = BattleState(player_team, enemy_team, BattleType.WILD, True, True)
            controller = BattleController(player_team, enemy_team, BattleType.WILD, True, True)
            controller.start_battle()
            
            # Create attack action
            from engine.systems.moves import Move, MoveCategory, MoveTarget
            test_move = Move(
                id="test_attack",
                name="Test Attack",
                description="Test attack move",
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
            
            controller.queue_player_action(attack_action)
            return controller.execute_turn()
        
        self.measure_operation("Attack Execution", execute_attack)
    
    def test_meat_system_performance(self):
        """Test Meat System Performance"""
        print("🥩 Testing Meat System Performance...")
        
        def use_meat():
            player_team, enemy_team = self.create_test_monsters()
            battle_state = BattleState(player_team, enemy_team, BattleType.WILD, True, True)
            controller = BattleController(player_team, enemy_team, BattleType.WILD, True, True)
            controller.start_battle()
            
            meat_action = BattleAction(
                action_type=ActionType.USE_MEAT,
                actor=battle_state.player_active,
                target=battle_state.player_active,
                meat_type=MeatType.SUPER
            )
            
            controller.queue_player_action(meat_action)
            return controller.execute_turn()
        
        self.measure_operation("Meat Usage", use_meat)
    
    def test_taming_performance(self):
        """Test Taming Performance"""
        print("🎣 Testing Taming Performance...")
        
        def attempt_taming():
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
            
            # Then tame
            tame_action = BattleAction(
                action_type=ActionType.TAME,
                actor=battle_state.player_active,
                target=battle_state.enemy_active,
                meat_system=battle_state.meat_system
            )
            
            controller.queue_player_action(tame_action)
            return controller.execute_turn()
        
        self.measure_operation("Taming Attempt", attempt_taming)
    
    def test_scout_performance(self):
        """Test Scout Performance"""
        print("🔍 Testing Scout Performance...")
        
        def scout_enemy():
            player_team, enemy_team = self.create_test_monsters()
            battle_state = BattleState(player_team, enemy_team, BattleType.WILD, True, True)
            controller = BattleController(player_team, enemy_team, BattleType.WILD, True, True)
            controller.start_battle()
            
            scout_action = BattleAction(
                action_type=ActionType.SCOUT,
                actor=battle_state.player_active,
                target=battle_state.enemy_active
            )
            
            controller.queue_player_action(scout_action)
            return controller.execute_turn()
        
        self.measure_operation("Scout Action", scout_enemy)
    
    def test_battle_end_performance(self):
        """Test Battle End Performance"""
        print("🏁 Testing Battle End Performance...")
        
        def check_battle_end():
            player_team, enemy_team = self.create_test_monsters()
            battle_state = BattleState(player_team, enemy_team, BattleType.WILD, True, True)
            controller = BattleController(player_team, enemy_team, BattleType.WILD, True, True)
            controller.start_battle()
            
            # Simulate victory
            battle_state.enemy_active.current_hp = 0
            battle_state.enemy_active.is_fainted = True
            
            return controller.check_battle_end()
        
        self.measure_operation("Battle End Check", check_battle_end)
    
    def test_damage_calculation_performance(self):
        """Test Damage Calculation Performance"""
        print("💥 Testing Damage Calculation Performance...")
        
        def calculate_damage():
            player_team, enemy_team = self.create_test_monsters()
            battle_state = BattleState(player_team, enemy_team, BattleType.WILD, True, True)
            controller = BattleController(player_team, enemy_team, BattleType.WILD, True, True)
            controller.start_battle()
            
            from engine.systems.moves import Move, MoveCategory, MoveTarget
            test_move = Move(
                id="test_attack",
                name="Test Attack",
                description="Test attack move",
                type="normal",
                category=MoveCategory.PHYSICAL,
                power=30,
                accuracy=90,
                priority=0,
                targeting=MoveTarget.ENEMY,
                effects=[]
            )
            
            return controller.calculate_dqm_damage(
                battle_state.player_active,
                battle_state.enemy_active,
                test_move
            )
        
        self.measure_operation("Damage Calculation", calculate_damage)
    
    def test_turn_resolution_performance(self):
        """Test Turn Resolution Performance"""
        print("🔄 Testing Turn Resolution Performance...")
        
        def resolve_turn():
            player_team, enemy_team = self.create_test_monsters()
            battle_state = BattleState(player_team, enemy_team, BattleType.WILD, True, True)
            controller = BattleController(player_team, enemy_team, BattleType.WILD, True, True)
            controller.start_battle()
            
            # Queue multiple actions
            from engine.systems.moves import Move, MoveCategory, MoveTarget
            test_move = Move(
                id="test_attack",
                name="Test Attack",
                description="Test attack move",
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
            
            controller.queue_player_action(attack_action)
            return controller.execute_turn()
        
        self.measure_operation("Turn Resolution", resolve_turn)
    
    def profile_battle_system(self):
        """Profile das gesamte Battle-System"""
        print("📊 Profiling Battle System...")
        
        def full_battle_flow():
            player_team, enemy_team = self.create_test_monsters()
            battle_state = BattleState(player_team, enemy_team, BattleType.WILD, True, True)
            controller = BattleController(player_team, enemy_team, BattleType.WILD, True, True)
            
            # Start battle
            controller.start_battle()
            
            # Execute attack
            from engine.systems.moves import Move, MoveCategory, MoveTarget
            test_move = Move(
                id="test_attack",
                name="Test Attack",
                description="Test attack move",
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
            
            controller.queue_player_action(attack_action)
            controller.execute_turn()
            
            # Check battle end
            battle_state.enemy_active.current_hp = 0
            battle_state.enemy_active.is_fainted = True
            controller.check_battle_end()
        
        # Profile the function
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            full_battle_flow()
        except Exception as e:
            print(f"Profiling failed: {e}")
        
        profiler.disable()
        
        # Save profile results
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # Top 20 functions
        
        # Save to file
        stats.dump_stats('/Users/leon/Desktop/untold_story/battle_performance.prof')
        print("📄 Profile saved to battle_performance.prof")
    
    def analyze_bottlenecks(self):
        """Analysiere Performance-Bottlenecks"""
        print("\n🔍 BOTTLENECK ANALYSIS")
        print("=" * 50)
        
        if not self.bottlenecks:
            print("✅ No bottlenecks found - all operations under 50ms")
            return
        
        print("⚠️ BOTTLENECKS FOUND:")
        for bottleneck in sorted(self.bottlenecks, key=lambda x: x['avg_time'], reverse=True):
            print(f"  🐌 {bottleneck['operation']}: {bottleneck['avg_time']:.3f}s avg, {bottleneck['max_time']:.3f}s max")
    
    def generate_performance_report(self):
        """Generiere Performance-Report"""
        print("\n📊 PERFORMANCE REPORT")
        print("=" * 50)
        
        for operation, data in self.performance_data.items():
            if 'error' in data:
                print(f"❌ {operation}: {data['error']}")
                continue
            
            print(f"⏱️ {operation}:")
            print(f"    Min: {data['min']:.3f}s")
            print(f"    Max: {data['max']:.3f}s")
            print(f"    Mean: {data['mean']:.3f}s")
            print(f"    Median: {data['median']:.3f}s")
            print(f"    Std: {data['std']:.3f}s")
            print(f"    Samples: {data['samples']}")
            
            # Performance rating
            if data['mean'] < 0.01:
                rating = "🚀 Excellent"
            elif data['mean'] < 0.05:
                rating = "✅ Good"
            elif data['mean'] < 0.1:
                rating = "⚠️ Acceptable"
            else:
                rating = "🐌 Poor"
            
            print(f"    Rating: {rating}")
            print()
    
    def run_all_tests(self):
        """Führe alle Performance-Tests aus"""
        print("🚀 STARTING BATTLE PERFORMANCE TESTS")
        print("=" * 50)
        
        tests = [
            self.test_battle_initialization_performance,
            self.test_battle_start_performance,
            self.test_action_execution_performance,
            self.test_meat_system_performance,
            self.test_taming_performance,
            self.test_scout_performance,
            self.test_battle_end_performance,
            self.test_damage_calculation_performance,
            self.test_turn_resolution_performance
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test failed: {e}")
        
        # Profile the system
        self.profile_battle_system()
        
        # Generate reports
        self.generate_performance_report()
        self.analyze_bottlenecks()
        
        # Save results
        import json
        with open('/Users/leon/Desktop/untold_story/BATTLE_PERFORMANCE_RESULTS.json', 'w') as f:
            json.dump({
                'performance_data': self.performance_data,
                'bottlenecks': self.bottlenecks
            }, f, indent=2, default=str)
        
        print(f"\n📄 Results saved to BATTLE_PERFORMANCE_RESULTS.json")

def main():
    """Main test function"""
    tester = BattlePerformanceTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
