"""
Battle System Integration Tests
==============================
Comprehensive integration tests for the complete battle system flow.
Tests the interaction between all battle system components.

Version: 1.0.0
Author: Performance Engineer Agent 5
"""

import pytest
import time
from typing import List, Dict, Any
from unittest.mock import Mock, patch

# Import battle system components
from engine.systems.battle.battle_controller import BattleController
from engine.systems.battle.battle_state import BattleState
from engine.systems.battle.battle_enums import BattlePhase, BattleType, BattleResult
from engine.systems.battle.turn_logic import ActionType
from engine.systems.battle.turn_logic import BattleAction
from engine.systems.battle.event_processor import EventProcessor
from engine.systems.battle.performance_monitor import get_performance_monitor
# from engine.systems.battle.turn_processor import TurnProcessor
# from engine.systems.battle.action_processor import ActionProcessor
from engine.systems.battle.battle_ai import BattleAI

# Import monster system
from engine.systems.monster_instance import MonsterInstance
from engine.systems.monsters import MonsterDatabase
from engine.systems.moves import Move

# Import UI components (mocked)
# from engine.systems.battle.battle_ui_core import BattleUICore

# Test data setup
def create_test_monster(name: str = "TestMonster", level: int = 10, hp: int = 100) -> MonsterInstance:
    """Create a test monster for integration testing."""
    from engine.systems.monster_instance import MonsterSpecies
    
    from engine.systems.stats import BaseStats
    from engine.systems.monster_instance import MonsterRank
    from engine.systems.experience_system import GrowthCurve
    
    # Create a simple monster species
    species = MonsterSpecies(
        id=name.lower(),
        name=name,
        types=["Normal"],
        base_stats=BaseStats(
            hp=hp,
            atk=50,
            def_=50,
            mag=50,
            res=50,
            spd=50
        ),
        rank=MonsterRank.F,
        growth_curve=GrowthCurve.MEDIUM_FAST,
        talents=[
            {"talent_id": "physical_i", "learned_at_level": 1, "current_tier": 1, "experience": 0}
        ]
    )
    
    # Create monster instance with correct parameters
    monster = MonsterInstance(
        species=species,
        level=level,
        nickname=name
    )
    
    # Set current HP
    monster.current_hp = hp
    
    return monster


def create_test_skill(name: str = "TestSkill", power: int = 50) -> Move:
    """Create a test skill for integration testing."""
    from engine.systems.moves import MoveCategory, MoveTarget, MoveEffect, EffectKind
    
    return Move(
        id=name.lower(),
        name=name,
        type="Normal",
        category=MoveCategory.PHYSICAL,
        power=power,
        accuracy=100,
        priority=0,
        targeting=MoveTarget.ENEMY,
        effects=[MoveEffect(kind=EffectKind.DAMAGE, power=power)],
        description="Test skill for integration testing"
    )


def create_test_battle_with_teams(player_team: List[MonsterInstance], enemy_team: List[MonsterInstance]) -> BattleController:
    """Create a test battle with specific teams."""
    return BattleController(player_team, enemy_team)


class TestCompleteBattleFlow:
    """Test complete battle flow from start to finish."""
    
    def test_complete_battle_flow(self):
        """Test complete battle from start to finish."""
        # Setup
        player_team = [create_test_monster("PlayerMon", 10, 100)]
        enemy_team = [create_test_monster("EnemyMon", 10, 100)]
        
        battle = create_test_battle_with_teams(player_team, enemy_team)
        monitor = get_performance_monitor()
        monitor.reset_metrics()
        
        # Start battle
        battle.start_battle()
        assert battle.state.phase == BattlePhase.START
        
        # Simulate complete battle
        turn_count = 0
        max_turns = 50
        
        while not battle.is_battle_over() and turn_count < max_turns:
            # Create actions
            player_action = BattleAction(
                ActionType.ATTACK,
                battle.state.player_active,
                battle.state.enemy_active,
                move=create_test_skill("Attack", 30)
            )
            
            # Enemy AI decides action
            from engine.systems.battle.battle_ai import BattleAI
            ai = BattleAI()
            enemy_action_dict = ai.choose_action(battle.state)
            
            # Convert AI action to BattleAction
            enemy_action = BattleAction(
                ActionType.ATTACK,
                battle.state.enemy_active,
                battle.state.player_active,
                move=create_test_skill("EnemyAttack", 30)
            )
            
            # Process turn
            start_time = time.perf_counter()
            result = battle.turn_processor.process_turn(player_action, enemy_action)
            turn_time = time.perf_counter() - start_time
            
            # Record performance metrics
            monitor.record_turn_time(turn_time)
            monitor.record_memory_growth()
            
            # Verify turn was processed
            assert result is not None, f"Turn {turn_count} failed to process"
            
            turn_count += 1
        
        # Verify battle ended properly
        assert battle.is_battle_over(), f"Battle didn't end after {max_turns} turns"
        assert battle.state.battle_result is not None, "No battle result"
        
        # Check performance
        report = monitor.get_performance_report()
        assert report['overall_status'] != 'needs_optimization', "Battle performance issues detected"
    
    def test_battle_with_monster_switching(self):
        """Test battle with monster switching."""
        # Setup team with multiple monsters
        player_team = [
            create_test_monster("Monster1", 10, 50),
            create_test_monster("Monster2", 10, 50),
            create_test_monster("Monster3", 10, 50)
        ]
        enemy_team = [create_test_monster("EnemyMon", 10, 100)]
        
        battle = create_test_battle_with_teams(player_team, enemy_team)
        battle.start_battle()
        
        # Switch monsters during battle
        for i in range(3):
            # Attack with current monster
            player_action = BattleAction(
                ActionType.ATTACK,
                battle.state.player_active,
                battle.state.enemy_active,
                move=create_test_skill("Attack", 20)
            )
            
            enemy_action = BattleAction(
                ActionType.ATTACK,
                battle.state.enemy_active,
                battle.state.player_active,
                move=create_test_skill("Attack", 20)
            )
            
            battle.process_turn(player_action, enemy_action)
            
            # Switch to next monster if available
            if i < len(player_team) - 1:
                battle.switch_monster(player_team[i + 1])
        
        # Verify battle state is consistent
        assert battle.state.player_active is not None
        assert battle.state.enemy_active is not None
    
    def test_battle_with_status_effects(self):
        """Test battle with status effects."""
        player_team = [create_test_monster("PlayerMon", 10, 100)]
        enemy_team = [create_test_monster("EnemyMon", 10, 100)]
        
        battle = create_test_battle_with_teams(player_team, enemy_team)
        battle.start_battle()
        
        # Apply status effect to enemy
        enemy_monster = battle.state.enemy_active
        enemy_monster.status_conditions.append("POISON")
        
        # Process several turns
        for i in range(5):
            player_action = BattleAction(
                ActionType.ATTACK,
                battle.state.player_active,
                battle.state.enemy_active,
                move=create_test_skill("Attack", 10)
            )
            
            enemy_action = BattleAction(
                ActionType.ATTACK,
                battle.state.enemy_active,
                battle.state.player_active,
                move=create_test_skill("Attack", 10)
            )
            
            battle.process_turn(player_action, enemy_action)
            
            # Check if poison damage was applied
            if i > 0:  # Poison doesn't apply on first turn
                assert enemy_monster.current_hp < 100, "Poison damage not applied"
    
    def test_battle_with_different_phases(self):
        """Test battle phase transitions."""
        player_team = [create_test_monster("PlayerMon", 10, 100)]
        enemy_team = [create_test_monster("EnemyMon", 10, 100)]
        
        battle = create_test_battle_with_teams(player_team, enemy_team)
        
        # Test phase transitions
        phases = [BattlePhase.INIT, BattlePhase.START, BattlePhase.INPUT, 
                 BattlePhase.EXECUTION, BattlePhase.AFTERMATH, BattlePhase.END]
        
        for phase in phases:
            success = battle.transition_phase(phase)
            assert success, f"Failed to transition to {phase}"
            assert battle.state.phase == phase, f"Phase not set to {phase}"
    
    def test_battle_error_recovery(self):
        """Test battle system error recovery."""
        player_team = [create_test_monster("PlayerMon", 10, 100)]
        enemy_team = [create_test_monster("EnemyMon", 10, 100)]
        
        battle = create_test_battle_with_teams(player_team, enemy_team)
        battle.start_battle()
        
        # Test with invalid actions
        invalid_action = BattleAction(
            ActionType.ATTACK,
            None,  # Invalid attacker
            battle.state.enemy_active,
            move=create_test_skill("Attack", 30)
        )
        
        # Should not crash, should handle error gracefully
        try:
            result = battle.process_turn(invalid_action, invalid_action)
            # If it doesn't crash, that's good
        except Exception as e:
            # Should be a handled error, not a crash
            assert "battle" in str(e).lower() or "action" in str(e).lower()


class TestTalentMoveIntegration:
    """Test that moves from talents work in battle."""
    
    def test_talent_move_integration(self):
        """Test that moves from talents work in battle."""
        # Create monster with talents
        monster = MonsterInstance(
            monster_id="talentmonster",
            level=10,
            current_hp=100,
            stat_stages={},
            status_conditions=[],
            talents=[]  # Will be populated with test talent
        )
        
        # Create talent with moves
        talent_skill = create_test_skill("TalentMove", 60)
        
        # Create battle
        player_team = [monster]
        enemy_team = [create_test_monster("EnemyMon", 10, 100)]
        
        battle = create_test_battle_with_teams(player_team, enemy_team)
        battle.start_battle()
        
        # Get available moves from talents
        moves = monster.get_available_moves()
        assert len(moves) > 0, "No moves from talents!"
        
        # Try to use each move
        for move in moves:
            action = BattleAction(
                ActionType.ATTACK,
                monster,
                battle.state.enemy_active,
                move=move
            )
            
            result = battle.execute_action(action)
            assert result['success'], f"Move {move.id} from talent failed!"
    
    def test_talent_system_performance(self):
        """Test performance of talent system in battle."""
        # Create monster with many talents
        from engine.systems.monster_instance import MonsterSpecies
        from engine.systems.stats import BaseStats
        from engine.systems.monster_instance import MonsterRank
        from engine.systems.experience_system import GrowthCurve
        
        monster_data = MonsterSpecies(
            id="multitalentmonster",
            name="MultiTalentMonster",
            types=["Normal"],
            base_stats=BaseStats(
                hp=100,
                atk=50,
                def_=50,
                spd=50,
                mag=50,
                res=50
            ),
            rank=MonsterRank.C,
            growth_curve=GrowthCurve.MEDIUM_FAST,
            description="Monster with many talents"
        )
        
        # Create many talents
        talents = [create_test_skill(f"Talent{i}", 30 + i) for i in range(10)]
        
        monster = MonsterInstance(
            monster_data=monster_data,
            level=10,
            current_hp=100,
            stat_stages={},
            status_conditions=[],
            talents=talents
        )
        
        # Benchmark talent move retrieval
        start_time = time.perf_counter()
        for _ in range(1000):
            moves = monster.get_available_moves()
        elapsed = time.perf_counter() - start_time
        
        # Should be fast even with many talents
        assert elapsed < 0.1, f"Talent move retrieval too slow: {elapsed*1000:.1f}ms"


class TestEventSystemIntegration:
    """Test event system integration with battle components."""
    
    def test_event_flow_integration(self):
        """Test complete event flow through battle system."""
        player_team = [create_test_monster("PlayerMon", 10, 100)]
        enemy_team = [create_test_monster("EnemyMon", 10, 100)]
        
        battle = create_test_battle_with_teams(player_team, enemy_team)
        
        # Mock UI to capture events
        mock_ui = Mock()
        battle.ui = mock_ui
        
        # Start battle and check events
        battle.start_battle()
        
        # Process a turn and check events
        player_action = BattleAction(
            ActionType.ATTACK,
            battle.state.player_active,
            battle.state.enemy_active,
            move=create_test_skill("Attack", 30)
        )
        
        enemy_action = BattleAction(
            ActionType.ATTACK,
            battle.state.enemy_active,
            battle.state.player_active,
            move=create_test_skill("Attack", 30)
        )
        
        battle.process_turn(player_action, enemy_action)
        
        # Verify events were emitted
        assert mock_ui.update.called or mock_ui.handle_event.called, "UI not receiving events"
    
    def test_event_queue_processing(self):
        """Test event queue processing during battle."""
        # Create test battle
        player_team = [create_test_monster("PlayerMon", 10, 100)]
        enemy_team = [create_test_monster("EnemyMon", 10, 100)]
        battle = BattleController()
        battle.initialize(player_team, enemy_team)
        event_processor = battle.event_processor
        
        # Emit many events
        for i in range(100):
            event_processor.emit_event("DAMAGE_DEALT", {'damage': i, 'target': 'enemy'})
            event_processor.emit_event("MESSAGE_SHOW", {'message': f'Turn {i}'})
        
        # Process events
        start_time = time.perf_counter()
        event_processor.process_events()
        process_time = time.perf_counter() - start_time
        
        # Should process quickly
        assert process_time < 0.1, f"Event processing too slow: {process_time*1000:.1f}ms"
        assert len(event_processor.event_queue) == 0, "Events not fully processed"


class TestBattleAIIntegration:
    """Test battle AI integration."""
    
    def test_ai_decision_making(self):
        """Test AI decision making in battle."""
        player_team = [create_test_monster("PlayerMon", 10, 100)]
        enemy_team = [create_test_monster("EnemyMon", 10, 100)]
        
        battle = create_test_battle_with_teams(player_team, enemy_team)
        battle.start_battle()
        
        # Test AI decisions
        for i in range(10):
            action = battle.ai.decide_action(battle.state)
            assert action is not None, f"AI failed to decide action on turn {i}"
            assert action.action_type == ActionType.ATTACK, "AI should choose attack"
            assert action.attacker == battle.state.enemy_active, "AI should attack with active monster"
    
    def test_ai_performance(self):
        """Test AI decision making performance."""
        player_team = [create_test_monster("PlayerMon", 10, 100)]
        enemy_team = [create_test_monster("EnemyMon", 10, 100)]
        
        battle = create_test_battle_with_teams(player_team, enemy_team)
        battle.start_battle()
        
        # Benchmark AI decisions
        start_time = time.perf_counter()
        for _ in range(1000):
            action = battle.ai.decide_action(battle.state)
        elapsed = time.perf_counter() - start_time
        
        decisions_per_second = 1000 / elapsed
        assert decisions_per_second > 1000, f"AI decision making too slow: {decisions_per_second:.0f} decisions/sec"


class TestBattleSystemStress:
    """Test battle system under stress conditions."""
    
    def test_rapid_battle_creation(self):
        """Test rapid battle creation and destruction."""
        for i in range(100):
            player_team = [create_test_monster(f"Player{i}", 10, 100)]
            enemy_team = [create_test_monster(f"Enemy{i}", 10, 100)]
            
            battle = create_test_battle_with_teams(player_team, enemy_team)
            battle.start_battle()
            
            # Process one turn
            player_action = BattleAction(
                ActionType.ATTACK,
                battle.state.player_active,
                battle.state.enemy_active,
                move=create_test_skill("Attack", 30)
            )
            
            enemy_action = BattleAction(
                ActionType.ATTACK,
                battle.state.enemy_active,
                battle.state.player_active,
                move=create_test_skill("Attack", 30)
            )
            
            battle.process_turn(player_action, enemy_action)
            
            # Battle should be cleaned up automatically
            del battle
    
    def test_memory_usage_during_long_battle(self):
        """Test memory usage during long battle."""
        import psutil
        import gc
        
        player_team = [create_test_monster("PlayerMon", 10, 1000)]  # High HP for long battle
        enemy_team = [create_test_monster("EnemyMon", 10, 1000)]
        
        battle = create_test_battle_with_teams(player_team, enemy_team)
        battle.start_battle()
        
        initial_memory = psutil.Process().memory_info().rss
        
        # Process many turns
        for i in range(200):
            player_action = BattleAction(
                ActionType.ATTACK,
                battle.state.player_active,
                battle.state.enemy_active,
                move=create_test_skill("Attack", 5)  # Low damage for long battle
            )
            
            enemy_action = BattleAction(
                ActionType.ATTACK,
                battle.state.enemy_active,
                battle.state.player_active,
                move=create_test_skill("Attack", 5)
            )
            
            battle.process_turn(player_action, enemy_action)
            
            # Force garbage collection every 50 turns
            if i % 50 == 0:
                gc.collect()
        
        final_memory = psutil.Process().memory_info().rss
        memory_growth = (final_memory - initial_memory) / 1024 / 1024
        
        # Memory growth should be reasonable
        assert memory_growth < 100, f"Memory grew by {memory_growth:.2f}MB during long battle"


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "--tb=short"])
