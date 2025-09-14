#!/usr/bin/env python3
"""
Debug Battle Test
Testet das neue Debug-System für Battle-Actions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.systems.battle.battle_controller import BattleState, BattleController
from engine.systems.battle.battle_enums import BattleType
from engine.systems.monster_instance import MonsterInstance
from engine.systems.battle.turn_logic import BattleAction, ActionType
from engine.systems.moves import MoveRegistry

def create_test_monster(name: str, hp: int = 50) -> MonsterInstance:
    """Erstelle einen Test-Monster."""
    # Erstelle einen einfachen Species-Objekt
    class SimpleSpecies:
        def __init__(self, name):
            self.name = name
            self.rank = 'F'
            self.types = ['normal']
    
    species = SimpleSpecies(name)
    monster = MonsterInstance(species)
    monster.name = name
    monster.current_hp = hp
    monster.max_hp = hp
    monster.level = 5
    monster.is_fainted = False
    
    # Füge einen Move hinzu
    move_registry = MoveRegistry()
    move = move_registry.get_move("tackle")
    if move:
        monster.moves = [move]
    else:
        # Fallback Move
        from engine.systems.moves import Move
        move = Move()
        move.name = "Tackle"
        move.power = 20
        move.accuracy = 100
        move.type = "normal"
        monster.moves = [move]
    
    return monster

def test_debug_battle():
    """Teste das Debug-System mit einem einfachen Battle."""
    print("🚀 Starting Debug Battle Test...")
    print("🥊 DEBUG BATTLE TEST")
    print("=" * 50)
    
    # Erstelle Test-Monster
    print("🔍 Creating test monsters...")
    player_monster = create_test_monster("PlayerSlime", 50)
    enemy_monster = create_test_monster("EnemySlime", 50)
    
    print(f"  ✅ Player: {player_monster.name} (HP: {player_monster.current_hp})")
    print(f"  ✅ Enemy: {enemy_monster.name} (HP: {enemy_monster.current_hp})")
    
    # Erstelle Battle
    print("\n🔍 Creating battle...")
    battle_state = BattleState(
        player_team=[player_monster],
        enemy_team=[enemy_monster],
        battle_type=BattleType.WILD
    )
    
    battle_controller = BattleController(battle_state)
    print("  ✅ Battle created successfully")
    
    # Starte Battle
    print("\n🔍 Starting battle...")
    start_result = battle_controller.start_battle()
    print(f"  ✅ Battle started: {start_result}")
    
    # Teste Player Action
    print("\n🔍 Testing player action...")
    if player_monster.moves:
        move = player_monster.moves[0]
        action = BattleAction(
            action_type=ActionType.ATTACK,
            actor=player_monster,
            target=enemy_monster,
            move=move
        )
        
        print(f"  📋 Action: {action.action_type.name} von {action.actor.name}")
        print(f"  📋 Move: {action.move.name}")
        print(f"  📋 Target: {action.target.name}")
        
        # Queue Action
        success = battle_controller.queue_player_action(action)
        print(f"  ✅ Action queued: {success}")
        
        # Execute Turn
        print("\n🔍 Executing turn...")
        result = battle_controller.execute_turn()
        print(f"  ✅ Turn result: {result}")
        
        # Check HP
        print(f"\n📊 After turn:")
        print(f"  💔 Player HP: {player_monster.current_hp}/{player_monster.max_hp}")
        print(f"  💔 Enemy HP: {enemy_monster.current_hp}/{enemy_monster.max_hp}")
    
    # Teste Enemy Turn
    print("\n🔍 Testing enemy turn...")
    enemy_result = battle_controller.execute_enemy_turn()
    print(f"  ✅ Enemy turn result: {enemy_result}")
    
    # Check HP after enemy turn
    print(f"\n📊 After enemy turn:")
    print(f"  💔 Player HP: {player_monster.current_hp}/{player_monster.max_hp}")
    print(f"  💔 Enemy HP: {enemy_monster.current_hp}/{enemy_monster.max_hp}")
    
    print("\n✅ DEBUG BATTLE TEST COMPLETED!")
    print("🎯 Das Debug-System zeigt alle Action-Flows!")

if __name__ == "__main__":
    test_debug_battle()
