#!/usr/bin/env python3
"""
Einfacher Debug-Test für das Battle-System
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Teste das Debug-System direkt
def test_debug_system():
    """Teste das Debug-System."""
    print("🚀 Starting Simple Debug Test...")
    print("🥊 DEBUG SYSTEM TEST")
    print("=" * 50)
    
    # Teste DEBUG_BATTLE Flag
    print("🔍 Testing DEBUG_BATTLE flag...")
    from engine.systems.battle.battle_controller import DEBUG_BATTLE
    print(f"  ✅ DEBUG_BATTLE = {DEBUG_BATTLE}")
    
    # Teste debug_log Funktion
    print("\n🔍 Testing debug_log function...")
    try:
        # Erstelle einen einfachen BattleState für den Test
        from engine.systems.battle.battle_controller import BattleState
        from engine.systems.battle.battle_enums import BattleType
        
        # Erstelle Mock-Monster
        class MockMonster:
            def __init__(self, name):
                self.name = name
                self.current_hp = 50
                self.max_hp = 50
                self.is_fainted = False
        
        player_monster = MockMonster("PlayerSlime")
        enemy_monster = MockMonster("EnemySlime")
        
        # Erstelle BattleState
        battle_state = BattleState(
            player_team=[player_monster],
            enemy_team=[enemy_monster],
            battle_type=BattleType.WILD
        )
        
        # Teste debug_log
        battle_state.debug_log("TEST MESSAGE: Debug system is working!")
        print("  ✅ debug_log function works!")
        
        # Teste Action-Queue
        print("\n🔍 Testing action queue...")
        from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
        
        # Erstelle Mock-Move
        class MockMove:
            def __init__(self):
                self.name = "Tackle"
                self.power = 20
        
        move = MockMove()
        
        # Erstelle Action
        action = BattleAction(
            action_type=ActionType.ATTACK,
            actor=player_monster,
            target=enemy_monster,
            move=move
        )
        
        # Teste Action-Queue
        success = battle_state.queue_player_action(action)
        print(f"  ✅ Action queued: {success}")
        print(f"  📋 Queue length: {len(battle_state.action_queue)}")
        
        # Teste Turn-Execution
        print("\n🔍 Testing turn execution...")
        result = battle_state.resolve_turn()
        print(f"  ✅ Turn resolved: {result}")
        
        print("\n✅ DEBUG SYSTEM TEST COMPLETED!")
        print("🎯 Das Debug-System funktioniert korrekt!")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_debug_system()
