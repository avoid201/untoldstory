#!/usr/bin/env python3
"""
Quick Battle Test - Testet ob das Battle-System jetzt funktioniert
Nach den Agent-Fixes sollte alles laufen!
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pygame
from engine.core.game import Game
from engine.systems.monster_instance import MonsterInstance
from engine.systems.monsters import MonsterDatabase

def create_test_monster(name="TestMonster", level=5):
    """Erstelle ein Test-Monster"""
    db = MonsterDatabase()
    
    # Versuche ein echtes Monster zu laden
    species = db.get_species_by_name("Glutstummel")  # Verwende get_species_by_name
    if species:
        monster = species.create_instance(level=level)
        monster.name = name
    else:
        # Fallback: Erstelle manuell
        monster = MonsterInstance(
            species_id=1,
            level=level,
            name=name
        )
        monster.max_hp = 100
        monster.current_hp = 100
        monster.stats = {
            'atk': 50, 'def': 40, 'mag': 30, 
            'res': 30, 'spd': 45
        }
        
        # Füge einen Move hinzu
        from engine.systems.moves import move_registry
        tackle = move_registry.get_move('tackle')
        if tackle:
            monster.moves = [tackle]
        else:
            print("WARNING: Kein Tackle-Move gefunden!")
    
    return monster

def test_battle_flow():
    """Teste den kompletten Battle-Flow"""
    print("\n" + "="*50)
    print("UNTOLD STORY - BATTLE SYSTEM TEST")
    print("="*50)
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    logical_surface = pygame.Surface((320, 180))
    
    print("\n[1] Initialisiere Game...")
    game = Game(
        screen=screen,
        logical_surface=logical_surface,
        logical_size=(320, 180),
        window_size=(1280, 720),
        scale_factor=4
    )
    game.debug_mode = True  # Enable debug output
    
    print("\n[2] Erstelle Test-Monster...")
    player_monster = create_test_monster("Glutstummel", 10)
    enemy_monster = create_test_monster("Kohlekumpel", 8)
    
    print(f"   Player: {player_monster.name} Lv.{player_monster.level} HP:{player_monster.current_hp}/{player_monster.max_hp}")
    print(f"   Enemy: {enemy_monster.name} Lv.{enemy_monster.level} HP:{enemy_monster.current_hp}/{enemy_monster.max_hp}")
    
    print("\n[3] Starte Battle Scene...")
    from engine.scenes.battle_scene import BattleScene
    battle_scene = BattleScene(game)
    
    # Start the battle
    battle_scene.on_enter(
        player_team=[player_monster],
        enemy_team=[enemy_monster],
        is_wild=True,
        can_flee=True
    )
    
    print("\n[4] Simuliere Battle-Actions...")
    print("   -> Player wählt Attack")
    
    # Simulate player action
    from engine.systems.battle.turn_logic import BattleAction, ActionType
    from engine.systems.moves import move_registry
    
    # Get a move
    move = move_registry.get_move('tackle') or list(move_registry._moves.values())[0]
    
    if move:
        print(f"   -> Nutze Move: {move.name}")
        
        # Create attack action
        battle_action = BattleAction(
            action_type=ActionType.ATTACK,
            actor=player_monster,
            target=enemy_monster,
            move=move
        )
        
        # Process the action through battle_scene
        battle_scene._process_battle_action(battle_action)
        
        print("\n[5] Check Battle State...")
        if battle_scene.battle_controller:
            state = battle_scene.battle_controller.get_battle_state()
            print(f"   Turn Count: {state.get('turn_count', 'N/A')}")
            print(f"   Action Queue Length: {len(state.get('action_queue', []))}")
            print(f"   Battle Log: {state.get('battle_log', [])[-3:] if state.get('battle_log') else 'Empty'}")
            
            # Check if damage was dealt
            if enemy_monster.current_hp < enemy_monster.max_hp:
                print(f"\n✅ SUCCESS! Damage wurde ausgeteilt!")
                print(f"   Enemy HP: {enemy_monster.current_hp}/{enemy_monster.max_hp}")
            else:
                print(f"\n⚠️  WARNING: Kein Damage ausgeteilt!")
        else:
            print("\n❌ ERROR: Kein BattleController gefunden!")
    else:
        print("\n❌ ERROR: Keine Moves gefunden!")
    
    print("\n[6] Cleanup...")
    pygame.quit()
    
    print("\n" + "="*50)
    print("TEST ABGESCHLOSSEN")
    print("="*50)

if __name__ == "__main__":
    try:
        test_battle_flow()
    except Exception as e:
        print(f"\n❌ KRITISCHER FEHLER: {e}")
        import traceback
        traceback.print_exc()
