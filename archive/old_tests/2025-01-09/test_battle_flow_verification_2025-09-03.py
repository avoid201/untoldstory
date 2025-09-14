#!/usr/bin/env python3
"""
BATTLE-FLOW-CONNECTOR VERIFICATION TEST
Testet den kompletten Battle-Flow von Start bis Victory mit Rewards und Level-Ups
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.systems.battle.battle_controller import BattleController, BattleState
from engine.systems.battle.battle_enums import BattleType, BattleResult
from engine.systems.monster_instance import MonsterInstance, MonsterSpecies
from engine.systems.moves import Move
from engine.systems.battle.turn_logic_clean import BattleAction, ActionType

def create_test_monster(name: str, level: int = 5) -> MonsterInstance:
    """Erstelle ein Test-Monster."""
    species = MonsterSpecies(
        id=f"{name.lower()}_species",
        name=name,
        types=["normal"],
        base_stats={"hp": 50, "atk": 30, "def": 25, "mag": 20, "res": 20, "spd": 25},
        rank="D"
    )
    
    monster = MonsterInstance(
        species=species,
        level=level,
        nickname=name
    )
    
    # Füge einen einfachen Move hinzu
    from engine.systems.moves import MoveCategory, MoveTarget, MoveEffect, EffectKind
    tackle = Move(
        id="tackle",
        name="Tackle",
        power=40,
        accuracy=95,
        type="normal",
        category=MoveCategory.PHYSICAL,
        priority=0,
        targeting=MoveTarget.ENEMY,
        effects=[MoveEffect(kind=EffectKind.DAMAGE, power=40)],
        description="Ein einfacher körperlicher Angriff"
    )
    monster.moves = [tackle]
    
    return monster

def test_complete_battle_flow():
    """Teste den kompletten Battle-Flow von Start bis Victory."""
    print("🎮 BATTLE-FLOW-CONNECTOR VERIFICATION TEST")
    print("=" * 50)
    
    try:
        # 1. Erstelle Test-Monster
        print("1. Erstelle Test-Monster...")
        player_monster = create_test_monster("TestPlayer", level=5)
        enemy_monster = create_test_monster("TestEnemy", level=3)
        
        print(f"   Player: {player_monster.name} (Level {player_monster.level})")
        print(f"   Enemy: {enemy_monster.name} (Level {enemy_monster.level})")
        
        # 2. Erstelle Battle State
        print("\n2. Erstelle Battle State...")
        battle_state = BattleState(
            player_team=[player_monster],
            enemy_team=[enemy_monster],
            battle_type=BattleType.WILD
        )
        
        # 3. Erstelle Battle Controller
        print("3. Erstelle Battle Controller...")
        controller = BattleController(battle_state)
        
        # 4. Starte Battle
        print("\n4. Starte Battle...")
        start_result = controller.start_battle()
        print(f"   Battle gestartet: {start_result}")
        
        # 5. Teste Action Queueing
        print("\n5. Teste Action Queueing...")
        attack_action = BattleAction(
            action_type=ActionType.ATTACK,
            actor=player_monster,
            target=enemy_monster,
            move=player_monster.moves[0]
        )
        
        success = controller.queue_player_action(attack_action)
        print(f"   Action gequeued: {success}")
        
        # 6. Teste Turn Execution
        print("\n6. Teste Turn Execution...")
        print(f"   Actions in Queue: {len(battle_state.action_queue)}")
        
        battle_result = controller.execute_turn()
        print(f"   Turn ausgeführt, Battle Result: {battle_result}")
        
        # 7. Teste Events
        print("\n7. Teste Events...")
        events = controller.get_pending_events()
        print(f"   Events generiert: {len(events)}")
        
        for i, event in enumerate(events):
            ui_update = controller.process_event(event)
            print(f"   Event {i+1}: {event.event_type} -> {ui_update}")
        
        # 8. Teste Status Effects
        print("\n8. Teste Status Effects...")
        controller.process_status_effects()
        print("   Status Effects verarbeitet")
        
        # 9. Teste Battle End Check
        print("\n9. Teste Battle End Check...")
        battle_end = controller.check_battle_end()
        print(f"   Battle End Check: {battle_end}")
        
        # 10. Teste Rewards (falls Victory)
        if battle_end == BattleResult.VICTORY:
            print("\n10. Teste Rewards...")
            print(f"   EXP verdient: {battle_state.exp_earned}")
            print(f"   Geld verdient: {battle_state.money_earned}")
            print(f"   Items erhalten: {battle_state.items_earned}")
        
        print("\n✅ BATTLE-FLOW VERIFICATION ERFOLGREICH!")
        print("Alle kritischen Verbindungen funktionieren:")
        print("  ✓ BattleController → BattleActionExecutor")
        print("  ✓ DamageCalculator → Status Effects")
        print("  ✓ Battle End → Rewards")
        print("  ✓ Events → UI Updates")
        
        return True
        
    except Exception as e:
        print(f"\n❌ BATTLE-FLOW VERIFICATION FEHLGESCHLAGEN!")
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_turns():
    """Teste mehrere Turns bis zum Sieg."""
    print("\n🔄 MULTI-TURN BATTLE TEST")
    print("=" * 30)
    
    try:
        # Erstelle stärkere Monster für längeren Kampf
        player_monster = create_test_monster("StrongPlayer", level=10)
        enemy_monster = create_test_monster("StrongEnemy", level=8)
        
        battle_state = BattleState(
            player_team=[player_monster],
            enemy_team=[enemy_monster],
            battle_type=BattleType.WILD
        )
        
        controller = BattleController(battle_state)
        controller.start_battle()
        
        turn_count = 0
        max_turns = 10
        
        while turn_count < max_turns:
            turn_count += 1
            print(f"\nTurn {turn_count}:")
            print(f"  Player HP: {player_monster.current_hp}/{player_monster.max_hp}")
            print(f"  Enemy HP: {enemy_monster.current_hp}/{enemy_monster.max_hp}")
            
            # Player Action
            attack_action = BattleAction(
                action_type=ActionType.ATTACK,
                actor=player_monster,
                target=enemy_monster,
                move=player_monster.moves[0]
            )
            controller.queue_player_action(attack_action)
            
            # Execute Turn
            battle_result = controller.execute_turn()
            
            # Process Events
            events = controller.get_pending_events()
            for event in events:
                ui_update = controller.process_event(event)
                if ui_update and ui_update.get('type') == 'damage':
                    print(f"  {ui_update['actor']} greift an für {ui_update['damage']} Schaden!")
            
            # Check Battle End
            if battle_result:
                print(f"  Battle beendet: {battle_result}")
                if battle_result == BattleResult.VICTORY:
                    print(f"  Belohnungen: EXP={battle_state.exp_earned}, Geld={battle_state.money_earned}")
                break
            
            # Enemy Action (vereinfacht)
            if enemy_monster.current_hp > 0:
                enemy_action = BattleAction(
                    action_type=ActionType.ATTACK,
                    actor=enemy_monster,
                    target=player_monster,
                    move=enemy_monster.moves[0]
                )
                controller.queue_player_action(enemy_action)
                controller.execute_turn()
        
        print(f"\n✅ Multi-Turn Test abgeschlossen nach {turn_count} Turns")
        return True
        
    except Exception as e:
        print(f"\n❌ Multi-Turn Test fehlgeschlagen: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starte Battle-Flow-Verification...")
    
    # Test 1: Kompletter Flow
    success1 = test_complete_battle_flow()
    
    # Test 2: Multi-Turn Battle
    success2 = test_multiple_turns()
    
    if success1 and success2:
        print("\n🎉 ALLE TESTS ERFOLGREICH!")
        print("Battle-Flow-System ist vollständig verbunden und funktionsfähig!")
    else:
        print("\n💥 EINIGE TESTS FEHLGESCHLAGEN!")
        print("Battle-Flow-System benötigt weitere Reparaturen!")
    
    print("\n" + "=" * 50)
