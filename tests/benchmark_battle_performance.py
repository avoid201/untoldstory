"""
Battle Performance Benchmark Suite
Measures turn execution time and system performance.
"""

import sys
import os
import time
import statistics
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
from engine.systems.battle.battle_state import BattleState

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BattlePerformanceBenchmark:
    """Comprehensive battle performance benchmark."""
    
    def __init__(self):
        """Initialize benchmark."""
        self.results = {}
        self.target_turn_time = 0.1  # 100ms target
        
    def create_test_monster(self, name: str, level: int = 5) -> MonsterInstance:
        """Create test monster."""
        species = MonsterSpecies(
            id=f'bench_{name.lower()}',
            name=name,
            types=['Feuer'],
            base_stats=BaseStats(50, 50, 50, 50, 50, 50),
            talents=[]
        )
        return MonsterInstance(species, level=level)
    
    def benchmark_turn_execution(self, iterations: int = 100) -> Dict[str, Any]:
        """Benchmark turn execution time."""
        logger.info(f"🏃 Benchmarking Turn Execution ({iterations} iterations)...")
        
        try:
            # Create battle
            player_monster = self.create_test_monster("Player", 5)
            enemy_monster = self.create_test_monster("Enemy", 5)
            
            battle_controller = BattleController(
                player_team=[player_monster],
                enemy_team=[enemy_monster],
                battle_type=BattleType.WILD
            )
            
            # Create test action
            attack_move = player_monster.moves[0]
            player_action = BattleAction(
                action_type=ActionType.ATTACK,
                actor=player_monster,
                target=enemy_monster,
                move=attack_move
            )
            
            # Benchmark turn execution
            times = []
            for i in range(iterations):
                start = time.perf_counter()
                battle_result = battle_controller.execute_turn(player_action, None)
                times.append(time.perf_counter() - start)
                
                # Reset monster HP for consistent testing
                enemy_monster.current_hp = enemy_monster.max_hp
                
                if (i + 1) % 20 == 0:
                    logger.info(f"  Completed {i + 1}/{iterations} iterations")
            
            # Calculate statistics
            mean_time = statistics.mean(times)
            median_time = statistics.median(times)
            min_time = min(times)
            max_time = max(times)
            std_dev = statistics.stdev(times) if len(times) > 1 else 0
            
            # Performance analysis
            under_target = sum(1 for t in times if t < self.target_turn_time)
            performance_ratio = under_target / len(times)
            
            result = {
                'iterations': iterations,
                'mean_time': mean_time,
                'median_time': median_time,
                'min_time': min_time,
                'max_time': max_time,
                'std_dev': std_dev,
                'under_target': under_target,
                'performance_ratio': performance_ratio,
                'target_met': mean_time < self.target_turn_time,
                'all_times': times
            }
            
            logger.info(f"✅ Turn Execution Benchmark Complete")
            logger.info(f"  Mean: {mean_time*1000:.2f}ms")
            logger.info(f"  Median: {median_time*1000:.2f}ms")
            logger.info(f"  Min: {min_time*1000:.2f}ms")
            logger.info(f"  Max: {max_time*1000:.2f}ms")
            logger.info(f"  Std Dev: {std_dev*1000:.2f}ms")
            logger.info(f"  Under {self.target_turn_time*1000}ms: {under_target}/{iterations} ({performance_ratio*100:.1f}%)")
            logger.info(f"  Target Met: {'✅' if result['target_met'] else '❌'}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Turn Execution Benchmark FAILED: {e}")
            return {'error': str(e)}
    
    def benchmark_event_validation_caching(self, iterations: int = 50) -> Dict[str, Any]:
        """Benchmark event validation caching performance."""
        logger.info(f"🏃 Benchmarking Event Validation Caching ({iterations} iterations)...")
        
        try:
            # Create battle state and event processor
            species = MonsterSpecies(
                id='bench_event',
                name='Event Monster',
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
            
            event_processor = EventProcessor(battle_state)
            
            # Benchmark first run (no cache)
            first_run_times = []
            for i in range(iterations // 2):
                start = time.perf_counter()
                event_processor.validate_all_handlers()
                first_run_times.append(time.perf_counter() - start)
            
            # Benchmark cached runs
            cached_run_times = []
            for i in range(iterations // 2):
                start = time.perf_counter()
                event_processor.validate_all_handlers()
                cached_run_times.append(time.perf_counter() - start)
            
            # Calculate statistics
            first_mean = statistics.mean(first_run_times)
            cached_mean = statistics.mean(cached_run_times)
            speedup = first_mean / cached_mean if cached_mean > 0 else 0
            
            result = {
                'iterations': iterations,
                'first_run_mean': first_mean,
                'cached_run_mean': cached_mean,
                'speedup': speedup,
                'first_run_times': first_run_times,
                'cached_run_times': cached_run_times
            }
            
            logger.info(f"✅ Event Validation Caching Benchmark Complete")
            logger.info(f"  First Run Mean: {first_mean*1000:.2f}ms")
            logger.info(f"  Cached Run Mean: {cached_mean*1000:.2f}ms")
            logger.info(f"  Speedup: {speedup:.1f}x")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Event Validation Caching Benchmark FAILED: {e}")
            return {'error': str(e)}
    
    def benchmark_move_category_determination(self, iterations: int = 100) -> Dict[str, Any]:
        """Benchmark move category determination performance."""
        logger.info(f"🏃 Benchmarking Move Category Determination ({iterations} iterations)...")
        
        try:
            from engine.ui.battle.battle_ui_menus import BattleUIMenuManager
            
            # Create menu manager
            menu_manager = BattleUIMenuManager(None)
            
            # Create test monster with moves
            monster = self.create_test_monster("Category Monster", 5)
            moves = monster.moves
            
            # Benchmark category determination
            times = []
            for i in range(iterations):
                start = time.perf_counter()
                for move in moves:
                    category = menu_manager._get_move_category(move)
                times.append(time.perf_counter() - start)
            
            # Calculate statistics
            mean_time = statistics.mean(times)
            median_time = statistics.median(times)
            min_time = min(times)
            max_time = max(times)
            
            result = {
                'iterations': iterations,
                'moves_per_iteration': len(moves),
                'mean_time': mean_time,
                'median_time': median_time,
                'min_time': min_time,
                'max_time': max_time,
                'time_per_move': mean_time / len(moves)
            }
            
            logger.info(f"✅ Move Category Determination Benchmark Complete")
            logger.info(f"  Mean: {mean_time*1000:.2f}ms for {len(moves)} moves")
            logger.info(f"  Per Move: {(mean_time/len(moves))*1000:.2f}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Move Category Determination Benchmark FAILED: {e}")
            return {'error': str(e)}
    
    def benchmark_talent_system_performance(self, iterations: int = 50) -> Dict[str, Any]:
        """Benchmark talent system performance."""
        logger.info(f"🏃 Benchmarking Talent System Performance ({iterations} iterations)...")
        
        try:
            # Create test monster
            monster = self.create_test_monster("Talent Monster", 5)
            
            # Benchmark move loading
            move_loading_times = []
            for i in range(iterations):
                start = time.perf_counter()
                moves = monster.moves
                move_loading_times.append(time.perf_counter() - start)
            
            # Benchmark talent experience gain
            exp_gain_times = []
            battle_result_data = {
                'base_talent_exp': 50,
                'participation_bonus': 1.2,
                'victory_bonus': 2.0
            }
            
            for i in range(iterations):
                start = time.perf_counter()
                upgrades = monster.gain_talent_experience_from_battle(battle_result_data)
                exp_gain_times.append(time.perf_counter() - start)
            
            # Calculate statistics
            move_loading_mean = statistics.mean(move_loading_times)
            exp_gain_mean = statistics.mean(exp_gain_times)
            
            result = {
                'iterations': iterations,
                'move_loading_mean': move_loading_mean,
                'exp_gain_mean': exp_gain_mean,
                'total_talents': len(monster.talents),
                'total_moves': len(monster.moves)
            }
            
            logger.info(f"✅ Talent System Performance Benchmark Complete")
            logger.info(f"  Move Loading: {move_loading_mean*1000:.2f}ms")
            logger.info(f"  EXP Gain: {exp_gain_mean*1000:.2f}ms")
            logger.info(f"  Talents: {len(monster.talents)}")
            logger.info(f"  Moves: {len(monster.moves)}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Talent System Performance Benchmark FAILED: {e}")
            return {'error': str(e)}
    
    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all performance benchmarks."""
        logger.info("🚀 Starting Battle Performance Benchmarks...")
        
        start_time = time.perf_counter()
        
        # Run all benchmarks
        benchmarks = {
            'turn_execution': self.benchmark_turn_execution(100),
            'event_validation_caching': self.benchmark_event_validation_caching(50),
            'move_category_determination': self.benchmark_move_category_determination(100),
            'talent_system_performance': self.benchmark_talent_system_performance(50)
        }
        
        total_time = time.perf_counter() - start_time
        
        # Generate summary
        summary = {
            'total_time': total_time,
            'benchmarks': benchmarks,
            'performance_summary': self._generate_performance_summary(benchmarks)
        }
        
        logger.info(f"🏁 Performance Benchmarks Complete!")
        logger.info(f"  Total Time: {total_time:.2f}s")
        
        return summary
    
    def _generate_performance_summary(self, benchmarks: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance summary."""
        summary = {
            'turn_execution_target_met': False,
            'event_caching_working': False,
            'overall_performance': 'UNKNOWN'
        }
        
        # Check turn execution performance
        if 'turn_execution' in benchmarks and 'target_met' in benchmarks['turn_execution']:
            summary['turn_execution_target_met'] = benchmarks['turn_execution']['target_met']
        
        # Check event caching performance
        if 'event_validation_caching' in benchmarks and 'speedup' in benchmarks['event_validation_caching']:
            summary['event_caching_working'] = benchmarks['event_validation_caching']['speedup'] > 1.0
        
        # Overall performance assessment
        if summary['turn_execution_target_met'] and summary['event_caching_working']:
            summary['overall_performance'] = 'EXCELLENT'
        elif summary['turn_execution_target_met'] or summary['event_caching_working']:
            summary['overall_performance'] = 'GOOD'
        else:
            summary['overall_performance'] = 'NEEDS_IMPROVEMENT'
        
        return summary


def main():
    """Run performance benchmarks."""
    benchmark = BattlePerformanceBenchmark()
    results = benchmark.run_all_benchmarks()
    
    # Print performance summary
    print("\n" + "="*60)
    print("🎯 PERFORMANCE SUMMARY")
    print("="*60)
    
    perf_summary = results['performance_summary']
    print(f"Turn Execution Target Met: {'✅' if perf_summary['turn_execution_target_met'] else '❌'}")
    print(f"Event Caching Working: {'✅' if perf_summary['event_caching_working'] else '❌'}")
    print(f"Overall Performance: {perf_summary['overall_performance']}")
    
    # Exit with error code if performance is poor
    if perf_summary['overall_performance'] == 'NEEDS_IMPROVEMENT':
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
