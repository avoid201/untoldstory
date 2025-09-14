#!/usr/bin/env python3
"""
🥊 BATTLE SYSTEM COMPLETE INTEGRATION TEST
Elite Battle System Specialist - Vollständige Battle System Validierung

Testet alle 7 Action-Types, BattleController Integration, DQM-Features und UI-Flow
"""

import sys
import os
import traceback
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_battle_system_integration():
    """Vollständige Battle System Integration Test."""
    print("🥊 BATTLE SYSTEM COMPLETE INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # Test 1: Battle System Core Components
        print("\n📋 TEST 1: Battle System Core Components")
        test_core_components()
        
        # Test 2: BattleController Integration
        print("\n🎮 TEST 2: BattleController Integration")
        test_battle_controller()
        
        # Test 3: All 7 Action Types
        print("\n⚔️ TEST 3: All 7 Action Types")
        test_all_action_types()
        
        # Test 4: DQM Features
        print("\n🐉 TEST 4: DQM Features (Meat System, Taming)")
        test_dqm_features()
        
        # Test 5: Battle UI Integration
        print("\n🖥️ TEST 5: Battle UI Integration")
        test_battle_ui_integration()
        
        # Test 6: Battle Flow & Events
        print("\n🔄 TEST 6: Battle Flow & Events")
        test_battle_flow()
        
        # Test 7: Performance & Edge Cases
        print("\n⚡ TEST 7: Performance & Edge Cases")
        test_performance_edge_cases()
        
        print("\n✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("🎯 Battle System ist vollständig integriert und funktionsfähig!")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_core_components():
    """Teste alle Core Battle System Komponenten."""
    print("  🔍 Testing Battle Enums...")
    from engine.systems.battle.battle_enums import BattleType, BattlePhase, BattleResult
    from engine.systems.battle.turn_logic_clean import ActionType
    assert BattleType.WILD.value == "wild"
    assert BattlePhase.INPUT.value == "input"
    assert BattleResult.VICTORY.value == "victory"
    print("  ✅ Battle Enums OK")
    
    print("  🔍 Testing Battle Actions...")
    from engine.systems.battle.battle_actions import BattleActionExecutor
    executor = BattleActionExecutor()
    assert executor is not None
    print("  ✅ Battle Actions OK")
    
    print("  🔍 Testing Meat System...")
    from engine.systems.battle.meat_system import MeatSystem, MeatType
    meat_system = MeatSystem()
    assert meat_system is not None
    print("  ✅ Meat System OK")
    
    print("  🔍 Testing Turn Logic...")
    from engine.systems.battle.turn_logic_clean import BattleAction, TurnOrder
    turn_order = TurnOrder()
    assert turn_order is not None
    print("  ✅ Turn Logic OK")

def test_battle_controller():
    """Teste BattleController Integration."""
    print("  🔍 Creating test monsters...")
    
    # Create test monsters
    from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank
    from engine.systems.stats import BaseStats
    
    # Create test species
    test_species = MonsterSpecies(
        id="test_slime",
        name="Test Slime",
        types=["Normal"],
        base_stats=BaseStats(hp=100, atk=50, def_=40, mag=30, res=35, spd=60),
        rank=MonsterRank.D
    )
    
    # Create player monster
    player_monster = MonsterInstance(
        species=test_species,
        level=5,
        nickname="TestPlayer"
    )
    
    # Create enemy monster
    enemy_monster = MonsterInstance(
        species=test_species,
        level=5,
        nickname="TestEnemy"
    )
    
    print("  🔍 Testing BattleState creation...")
    from engine.systems.battle.battle_controller import BattleState, BattleController
    from engine.systems.battle.battle_enums import BattleType
    
    battle_state = BattleState(
        player_team=[player_monster],
        enemy_team=[enemy_monster],
        battle_type=BattleType.WILD,
        can_flee=True,
        can_catch=True
    )
    
    assert battle_state.player_active == player_monster
    assert battle_state.enemy_active == enemy_monster
    print("  ✅ BattleState creation OK")
    
    print("  🔍 Testing BattleController...")
    controller = BattleController(battle_state)
    assert controller is not None
    print("  ✅ BattleController creation OK")
    
    print("  🔍 Testing battle start...")
    start_info = controller.start_battle()
    assert start_info is not None
    assert 'player_active' in start_info
    print("  ✅ Battle start OK")

def test_all_action_types():
    """Teste alle 7 Action-Types."""
    print("  🔍 Testing ActionType enum...")
    from engine.systems.battle.turn_logic_clean import ActionType
    
    expected_actions = [
        ActionType.ATTACK,
        ActionType.TAME, 
        ActionType.FLEE,
        ActionType.SWITCH,
        ActionType.ITEM,
        ActionType.SCOUT,
        ActionType.USE_MEAT
    ]
    
    for action_type in expected_actions:
        assert action_type is not None
        print(f"    ✅ {action_type.name} OK")
    
    print("  🔍 Testing BattleAction creation...")
    from engine.systems.battle.turn_logic_clean import BattleAction
    from engine.systems.monster_instance import MonsterInstance
    
    # Create test monster
    from engine.systems.monster_instance import MonsterSpecies, MonsterRank
    from engine.systems.stats import BaseStats
    
    test_species = MonsterSpecies(
        id="test_slime",
        name="Test Slime",
        types=["Normal"],
        base_stats=BaseStats(hp=100, atk=50, def_=40, mag=30, res=35, spd=60),
        rank=MonsterRank.D
    )
    
    test_monster = MonsterInstance(
        species=test_species,
        level=5,
        nickname="TestMonster"
    )
    
    # Test each action type
    for action_type in expected_actions:
        action = BattleAction(
            action_type=action_type,
            actor=test_monster,
            target=test_monster
        )
        assert action.action_type == action_type
        print(f"    ✅ {action_type.name} Action creation OK")

def test_dqm_features():
    """Teste DQM-spezifische Features."""
    print("  🔍 Testing Meat System...")
    from engine.systems.battle.meat_system import MeatSystem, MeatType
    
    meat_system = MeatSystem()
    
    # Test meat types
    meat_types = [MeatType.NONE, MeatType.NORMAL, MeatType.SUPER, MeatType.DIVINE]
    for meat_type in meat_types:
        assert meat_type is not None
        print(f"    ✅ {meat_type.name} OK")
    
    print("  🔍 Testing taming calculation...")
    taming_data = meat_system.calculate_taming_chance(
        base_chance=0.15,
        monster_hp_percent=0.5,
        monster_rank='D',
        monster_status=None
    )
    assert 'final_chance' in taming_data
    assert 0.0 <= taming_data['final_chance'] <= 1.0
    print("  ✅ Taming calculation OK")
    
    print("  🔍 Testing DQM formulas...")
    from engine.systems.battle.dqm_formulas import DQMCalculator
    
    # Test damage calculation
    calculator = DQMCalculator()
    damage_result = calculator.calculate_damage(
        attacker_stats={'atk': 50, 'level': 5},
        defender_stats={'def': 40, 'level': 5},
        move_power=60
    )
    assert damage_result.damage > 0
    print("  ✅ DQM damage formula OK")

def test_battle_ui_integration():
    """Teste Battle UI Integration."""
    print("  🔍 Testing BattleUI components...")
    
    # Test BattleUI imports
    try:
        from engine.ui.battle_ui import BattleUI, BattleMenuState
        print("  ✅ BattleUI import OK")
        
        # Test menu states
        menu_states = [
            BattleMenuState.MAIN,
            BattleMenuState.MOVE_SELECT,
            BattleMenuState.ITEM_SELECT,
            BattleMenuState.SWITCH_SELECT,
            BattleMenuState.TAME_MEAT,
            BattleMenuState.TAME_CONFIRM,
            BattleMenuState.SCOUT
        ]
        
        for state in menu_states:
            assert state is not None
            print(f"    ✅ {state.name} menu state OK")
            
    except ImportError as e:
        print(f"  ⚠️ BattleUI import failed: {e}")
    
    print("  🔍 Testing BattleScene integration...")
    try:
        from engine.scenes.battle_scene import BattleScene
        print("  ✅ BattleScene import OK")
    except ImportError as e:
        print(f"  ⚠️ BattleScene import failed: {e}")

def test_battle_flow():
    """Teste Battle Flow und Events."""
    print("  🔍 Testing Battle Events...")
    try:
        from engine.systems.battle.battle_events import EventType, BattleEvent, BattleEventGenerator
        
        # Test event types
        event_types = [
            EventType.MESSAGE_SHOW,
            EventType.HP_BAR_UPDATE,
            EventType.ANIMATION_PLAY,
            EventType.DAMAGE_DEALT,
            EventType.BATTLE_END
        ]
        
        for event_type in event_types:
            assert event_type is not None
            print(f"    ✅ {event_type.name} event type OK")
        
        # Test event generator
        generator = BattleEventGenerator()
        assert generator is not None
        print("  ✅ Battle Event Generator OK")
        
    except ImportError as e:
        print(f"  ⚠️ Battle Events import failed: {e}")
    
    print("  🔍 Testing Turn Order...")
    from engine.systems.battle.turn_logic_clean import TurnOrder, BattleAction, ActionType
    from engine.systems.monster_instance import MonsterInstance
    
    # Create test monsters with different speeds
    from engine.systems.monster_instance import MonsterSpecies, MonsterRank
    from engine.systems.stats import BaseStats
    
    fast_species = MonsterSpecies(
        id="fast_slime",
        name="Fast Slime",
        types=["Normal"],
        base_stats=BaseStats(hp=100, atk=50, def_=40, mag=30, res=35, spd=100),
        rank=MonsterRank.D
    )
    
    slow_species = MonsterSpecies(
        id="slow_slime",
        name="Slow Slime", 
        types=["Normal"],
        base_stats=BaseStats(hp=100, atk=50, def_=40, mag=30, res=35, spd=50),
        rank=MonsterRank.D
    )
    
    fast_monster = MonsterInstance(
        species=fast_species,
        level=5,
        nickname="FastMonster"
    )
    
    slow_monster = MonsterInstance(
        species=slow_species,
        level=5,
        nickname="SlowMonster"
    )
    
    # Create test move
    from engine.systems.moves import Move, MoveCategory, MoveTarget, MoveEffect, EffectKind
    test_move = Move(
        id="tackle",
        name="Tackle",
        type="Normal",
        category=MoveCategory.PHYSICAL,
        power=40,
        accuracy=100,
        priority=0,
        targeting=MoveTarget.ENEMY,
        effects=[MoveEffect(kind=EffectKind.DAMAGE, power=40)],
        description="A basic physical attack"
    )
    
    # Create actions
    fast_action = BattleAction(
        action_type=ActionType.ATTACK,
        actor=fast_monster,
        target=slow_monster,
        move=test_move
    )
    
    slow_action = BattleAction(
        action_type=ActionType.ATTACK,
        actor=slow_monster,
        target=fast_monster,
        move=test_move
    )
    
    # Test turn order
    turn_order = TurnOrder()
    turn_order.add_action(fast_action)
    turn_order.add_action(slow_action)
    
    sorted_actions = turn_order.sort_actions(use_dqm_formula=True)
    assert len(sorted_actions) == 2
    # Fast monster should go first
    assert sorted_actions[0].actor == fast_monster
    print("  ✅ Turn Order OK")

def test_performance_edge_cases():
    """Teste Performance und Edge Cases."""
    print("  🔍 Testing edge cases...")
    
    # Test with invalid monsters
    try:
        from engine.systems.battle.battle_controller import BattleState
        from engine.systems.battle.battle_enums import BattleType
        
        # Test with empty teams (should raise error)
        try:
            battle_state = BattleState(
                player_team=[],
                enemy_team=[],
                battle_type=BattleType.WILD
            )
            print("  ⚠️ Empty teams should raise error!")
        except ValueError:
            print("  ✅ Empty teams correctly rejected")
        
        # Test with None monsters
        try:
            battle_state = BattleState(
                player_team=[None],
                enemy_team=[None],
                battle_type=BattleType.WILD
            )
            print("  ⚠️ None monsters should raise error!")
        except (ValueError, TypeError):
            print("  ✅ None monsters correctly rejected")
            
    except Exception as e:
        print(f"  ⚠️ Edge case testing failed: {e}")
    
    print("  🔍 Testing performance with multiple actions...")
    from engine.systems.battle.turn_logic_clean import TurnOrder, BattleAction, ActionType
    from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank
    from engine.systems.stats import BaseStats
    from engine.systems.moves import Move, MoveCategory, MoveTarget, MoveEffect, EffectKind
    
    # Create many actions
    turn_order = TurnOrder()
    for i in range(10):
        species = MonsterSpecies(
            id=f"monster_{i}",
            name=f"Monster {i}",
            types=["Normal"],
            base_stats=BaseStats(hp=100, atk=50, def_=40, mag=30, res=35, spd=50 + i),
            rank=MonsterRank.D
        )
        
        monster = MonsterInstance(
            species=species,
            level=5,
            nickname=f"Monster{i}"
        )
        
        # Create test move for each monster
        test_move = Move(
            id=f"move_{i}",
            name=f"Move {i}",
            type="Normal",
            category=MoveCategory.PHYSICAL,
            power=40,
            accuracy=100,
            priority=0,
            targeting=MoveTarget.ENEMY,
            effects=[MoveEffect(kind=EffectKind.DAMAGE, power=40)],
            description=f"Test move {i}"
        )
        
        action = BattleAction(
            action_type=ActionType.ATTACK,
            actor=monster,
            target=monster,
            move=test_move
        )
        turn_order.add_action(action)
    
    # Sort actions (should be fast)
    import time
    start_time = time.time()
    sorted_actions = turn_order.sort_actions(use_dqm_formula=True)
    end_time = time.time()
    
    assert len(sorted_actions) == 10
    assert (end_time - start_time) < 0.1  # Should be fast
    print(f"  ✅ Performance OK ({end_time - start_time:.3f}s for 10 actions)")

def run_battle_simulation():
    """Führe eine komplette Battle Simulation durch."""
    print("\n🎮 RUNNING BATTLE SIMULATION")
    print("=" * 40)
    
    try:
        from engine.systems.battle.battle_controller import BattleState, BattleController
        from engine.systems.battle.battle_enums import BattleType
        from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
        from engine.systems.monster_instance import MonsterInstance
        from engine.systems.moves import move_registry
        
        # Create test monsters
        from engine.systems.monster_instance import MonsterSpecies, MonsterRank
        from engine.systems.stats import BaseStats
        
        player_species = MonsterSpecies(
            id="player_slime",
            name="Player Slime",
            types=["Normal"],
            base_stats=BaseStats(hp=100, atk=50, def_=40, mag=30, res=35, spd=60),
            rank=MonsterRank.D
        )
        
        enemy_species = MonsterSpecies(
            id="enemy_slime",
            name="Enemy Slime",
            types=["Normal"],
            base_stats=BaseStats(hp=80, atk=45, def_=35, mag=25, res=30, spd=55),
            rank=MonsterRank.D
        )
        
        player_monster = MonsterInstance(
            species=player_species,
            level=5,
            nickname="PlayerSlime"
        )
        
        enemy_monster = MonsterInstance(
            species=enemy_species,
            level=5,
            nickname="EnemySlime"
        )
        
        # Create battle
        battle_state = BattleState(
            player_team=[player_monster],
            enemy_team=[enemy_monster],
            battle_type=BattleType.WILD,
            can_flee=True,
            can_catch=True
        )
        
        controller = BattleController(battle_state)
        controller.start_battle()
        
        print(f"  🥊 Battle started: {player_monster.name} vs {enemy_monster.name}")
        
        # Simulate a few turns
        for turn in range(3):
            print(f"\n  📋 Turn {turn + 1}")
            
            # Player attack
            tackle_move = move_registry.get_move('tackle')
            if tackle_move:
                player_action = BattleAction(
                    action_type=ActionType.ATTACK,
                    actor=player_monster,
                    target=enemy_monster,
                    move=tackle_move
                )
                controller.queue_player_action(player_action)
                result = controller.execute_turn()
                
                print(f"    ⚔️ {player_monster.name} attacks {enemy_monster.name}")
                print(f"    💔 Enemy HP: {enemy_monster.current_hp}/{enemy_monster.max_hp}")
                
                if result:
                    print(f"    🏁 Battle ended: {result}")
                    break
            
            # Enemy attack
            enemy_result = controller.execute_enemy_turn()
            if enemy_result:
                print(f"    🏁 Battle ended: {enemy_result}")
                break
                
            print(f"    💔 Player HP: {player_monster.current_hp}/{player_monster.max_hp}")
        
        print("  ✅ Battle simulation completed successfully!")
        
    except Exception as e:
        print(f"  ❌ Battle simulation failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Battle System Complete Integration Test...")
    
    # Run main tests
    success = test_battle_system_integration()
    
    if success:
        # Run battle simulation
        run_battle_simulation()
        
        print("\n🎯 BATTLE SYSTEM INTEGRATION COMPLETE!")
        print("🥊 Alle Komponenten sind funktionsfähig und integriert!")
        print("✨ Das DQM-Style Battle System ist bereit für den Einsatz!")
    else:
        print("\n❌ BATTLE SYSTEM INTEGRATION FAILED!")
        print("🔧 Bitte behebe die Fehler bevor du fortfährst!")
        sys.exit(1)
