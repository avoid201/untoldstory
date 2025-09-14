#!/usr/bin/env python3
"""
Interaktiver Test des Battle Systems
Simuliert einen echten Kampf mit Benutzer-Input
"""

import sys
import os
import pygame
import time
from typing import List, Dict, Any

# Füge den Projektpfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.systems.battle.battle_system import BattleState, BattleType, BattlePhase
from engine.systems.battle.turn_logic_clean import ActionType, BattleAction
from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, StatusCondition
from engine.systems.stats import BaseStats, StatStages
from engine.systems.moves import Move, MoveCategory, MoveTarget
from engine.ui.battle_ui import BattleUI, BattleMenuState
from engine.scenes.battle_scene import BattleScene
from engine.core.config import Colors, LOGICAL_WIDTH, LOGICAL_HEIGHT

class MockGame:
    """Mock Game-Objekt für Tests."""
    def __init__(self):
        self.party_manager = MockPartyManager()
        self.current_map = 'test_map'
        self.player_pos = (5, 5)
    
    def pop_scene(self):
        print("🎬 Scene wird geschlossen - zurück zum Feld")
    
    def push_scene(self, scene):
        print(f"🎬 Scene wird geöffnet: {type(scene).__name__}")

class MockPartyManager:
    """Mock Party Manager für Tests."""
    def __init__(self):
        self.party = MockParty()

class MockParty:
    """Mock Party für Tests."""
    def __init__(self):
        self.members = [create_test_monster("Feuerwolf", 8)]
    
    def get_conscious_members(self):
        return [m for m in self.members if not m.is_fainted]

def create_test_monster(name: str, level: int) -> MonsterInstance:
    """Erstellt ein Test-Monster für Tests."""
    try:
        # Erstelle Basis-Stats
        base_stats = BaseStats(hp=120, atk=65, def_=55, mag=40, res=35, spd=80)
        
        # Erstelle Stat-Stages
        stat_stages = StatStages()
        
        # Erstelle Spezies
        species = MonsterSpecies(
            id=1, 
            name=name, 
            base_stats=base_stats,
            types=["Feuer", "Bestie"]
        )
        
        # Erstelle Monster-Instanz
        monster = MonsterInstance(
            species=species,
            level=level,
            nickname=name
        )
        
        # Füge Moves hinzu
        moves = [
            create_test_move("Feuerzahn", "Feuer", 65),
            create_test_move("Tackle", "Normal", 40),
            create_test_move("Schutz", "Normal", 0),
            create_test_move("Heilung", "Normal", 0)
        ]
        monster.moves = moves
        
        return monster
        
    except Exception as e:
        print(f"Fehler beim Erstellen des Test-Monsters: {str(e)}")
        return create_simple_monster(name, level)

def create_simple_monster(name: str, level: int) -> MonsterInstance:
    """Erstellt ein einfaches Test-Monster als Fallback."""
    class SimpleMonster:
        def __init__(self, name, level):
            self.name = name
            self.level = level
            self.is_fainted = False
            self.current_hp = 120
            self.max_hp = 120
            self.stats = {"hp": 120, "atk": 65, "def": 55, "mag": 40, "res": 35, "spd": 80}
            self.stat_stages = SimpleStatStages()
            self.moves = [create_test_move("Tackle", "Normal", 40)]
            self.status = StatusCondition.NONE
            self.experience = 0
            self.id = 1
        
        def process_status(self):
            return {"skip_turn": False, "message": ""}
    
    class SimpleStatStages:
        def __init__(self):
            self.stages = {"hp": 0, "atk": 0, "def": 0, "mag": 0, "res": 0, "spd": 0}
        
        def get(self, stat, default=0):
            return self.stages.get(stat, default)
        
        def reset(self):
            for stat in self.stages:
                self.stages[stat] = 0
    
    return SimpleMonster(name, level)

def create_test_move(name: str, move_type: str, power: int) -> Move:
    """Erstellt einen Test-Move."""
    try:
        from engine.systems.moves import MoveEffect, EffectKind
        
        effects = []
        if power > 0:
            effects.append(MoveEffect(
                kind=EffectKind.DAMAGE,
                power=power,
                chance=100.0
            ))
        else:
            effects.append(MoveEffect(
                kind=EffectKind.BUFF,
                chance=100.0
            ))
        
        return Move(
            id=name.lower(),
            name=name,
            type=move_type,
            category=MoveCategory.PHYSICAL if power > 0 else MoveCategory.SUPPORT,
            power=power,
            accuracy=90,
            pp=15,
            max_pp=15,
            priority=0,
            targeting=MoveTarget.ENEMY,
            effects=effects,
            description=f"Test-Move: {name}"
        )
        
    except Exception as e:
        print(f"Fehler beim Erstellen des Test-Moves: {str(e)}")
        return create_simple_move(name, move_type, power)

def create_simple_move(name: str, move_type: str, power: int):
    """Erstellt einen einfachen Test-Move als Fallback."""
    class SimpleMove:
        def __init__(self, name, move_type, power):
            self.name = name
            self.type = move_type
            self.power = power
            self.accuracy = 90
            self.pp = 15
            self.max_pp = 15
            self.priority = 0
        
        def can_use(self):
            return self.pp > 0
        
        def use(self):
            if self.pp > 0:
                self.pp -= 1
                return True
            return False
    
    return SimpleMove(name, move_type, power)

def create_enemy_monster(name: str, level: int) -> MonsterInstance:
    """Erstellt ein Gegner-Monster."""
    try:
        # Erstelle Basis-Stats
        base_stats = BaseStats(hp=100, atk=55, def_=45, mag=35, res=30, spd=70)
        
        # Erstelle Stat-Stages
        stat_stages = StatStages()
        
        # Erstelle Spezies
        species = MonsterSpecies(
            id=2, 
            name=name, 
            base_stats=base_stats,
            types=["Wasser"]
        )
        
        # Erstelle Monster-Instanz
        monster = MonsterInstance(
            species=species,
            level=level,
            nickname=name
        )
        
        # Füge Moves hinzu
        moves = [
            create_test_move("Aqua-Jet", "Wasser", 60),
            create_test_move("Tackle", "Normal", 40),
            create_test_move("Schutz", "Normal", 0)
        ]
        monster.moves = moves
        
        return monster
        
    except Exception as e:
        print(f"Fehler beim Erstellen des Gegner-Monsters: {str(e)}")
        return create_simple_monster(name, level)

def print_battle_status(battle_state: BattleState):
    """Zeigt den aktuellen Kampfstatus an."""
    print("\n" + "="*50)
    print("🎯 KAMPFSTATUS")
    print("="*50)
    
    # Spieler-Monster
    player = battle_state.player_active
    if player:
        hp_percent = (player.current_hp / player.max_hp) * 100
        hp_bar = "█" * int(hp_percent / 10) + "░" * (10 - int(hp_percent / 10))
        print(f"👤 {player.name} Lv.{player.level}")
        print(f"   HP: [{hp_bar}] {player.current_hp}/{player.max_hp} ({hp_percent:.1f}%)")
        
        # Zeige Moves an
        if hasattr(player, 'moves') and player.moves:
            print("   Attacken:")
            for i, move in enumerate(player.moves):
                pp_status = f"{move.pp}/{move.max_pp}" if hasattr(move, 'pp') else "∞"
                print(f"     {i+1}. {move.name} ({move.type}) - PP: {pp_status}")
    
    # Gegner-Monster
    enemy = battle_state.enemy_active
    if enemy:
        hp_percent = (enemy.current_hp / enemy.max_hp) * 100
        hp_bar = "█" * int(hp_percent / 10) + "░" * (10 - int(hp_percent / 10))
        print(f"👹 {enemy.name} Lv.{enemy.level}")
        print(f"   HP: [{hp_bar}] {enemy.current_hp}/{enemy.max_hp} ({hp_percent:.1f}%)")
    
    print(f"Phase: {battle_state.phase.value}")
    print(f"Runde: {battle_state.turn_count}")
    print("="*50)

def print_battle_menu():
    """Zeigt das Battle-Menü an."""
    print("\n🎮 BATTLE-MENÜ")
    print("WASD - Navigation, Enter - Bestätigen, ESC - Zurück")
    print("1. Kämpfen")
    print("2. Zähmen")
    print("3. Items")
    print("4. Team")
    print("5. Spähen")
    print("6. Fliehen")

def print_move_menu(moves: List):
    """Zeigt das Move-Auswahl-Menü an."""
    print("\n⚔️ MOVE-AUSWAHL")
    print("WASD - Navigation, Enter - Bestätigen, ESC - Zurück")
    for i, move in enumerate(moves):
        pp_status = f"{move.pp}/{move.max_pp}" if hasattr(move, 'pp') else "∞"
        print(f"{i+1}. {move.name} ({move.type}) - PP: {pp_status}")

def get_user_input(prompt: str, valid_options: List[str] = None) -> str:
    """Holt Benutzer-Input."""
    while True:
        user_input = input(prompt).strip().lower()
        if valid_options is None or user_input in valid_options:
            return user_input
        print(f"Ungültige Eingabe. Gültige Optionen: {', '.join(valid_options)}")

def simulate_battle():
    """Simuliert einen kompletten Kampf."""
    print("🚀 Starte interaktiven Battle-Test...")
    print("Du wirst gegen ein wildes Monster antreten!")
    
    # Erstelle Monster
    player_monster = create_test_monster("Feuerwolf", 8)
    enemy_monster = create_enemy_monster("Aqua-Ratte", 7)
    
    print(f"\n👤 Dein Monster: {player_monster.name} Lv.{player_monster.level}")
    print(f"👹 Gegner: {enemy_monster.name} Lv.{enemy_monster.level}")
    
    # Erstelle Battle State
    battle_state = BattleState(
        player_team=[player_monster],
        enemy_team=[enemy_monster],
        battle_type=BattleType.WILD
    )
    
    # Starte Kampf
    start_result = battle_state.start_battle()
    print(f"\n🔥 {start_result.get('message', 'Kampf beginnt!')}")
    
    # Kampf-Loop
    while battle_state.is_valid() and battle_state.phase != BattlePhase.END:
        # Zeige Status
        print_battle_status(battle_state)
        
        # Zeige Menü
        print_battle_menu()
        
        # Hole Spieler-Input
        choice = get_user_input("Wähle eine Option (1-6): ", ['1', '2', '3', '4', '5', '6'])
        
        if choice == '1':  # Kämpfen
            # Zeige Moves
            if hasattr(player_monster, 'moves') and player_monster.moves:
                print_move_menu(player_monster.moves)
                move_choice = get_user_input("Wähle einen Move (1-4): ", ['1', '2', '3', '4'])
                
                try:
                    move_index = int(move_choice) - 1
                    if 0 <= move_index < len(player_monster.moves):
                        move = player_monster.moves[move_index]
                        
                        # Erstelle Battle Action
                        action = BattleAction(
                            actor=player_monster,
                            action_type=ActionType.ATTACK,
                            move=move,
                            target=enemy_monster
                        )
                        
                        # Queue Action
                        success = battle_state.queue_player_action(action)
                        if success:
                            print(f"\n⚔️ {player_monster.name} setzt {move.name} ein!")
                            
                            # Resolve Turn
                            turn_results = battle_state.resolve_turn()
                            print(f"Runde {turn_results.get('turn', '?')} abgeschlossen!")
                            
                            # Zeige Ergebnisse
                            for action_result in turn_results.get('actions', []):
                                if action_result.get('success'):
                                    if 'damage' in action_result:
                                        print(f"💥 {action_result['actor']} macht {action_result['damage']} Schaden!")
                                    if 'messages' in action_result:
                                        for msg in action_result['messages']:
                                            print(f"📢 {msg}")
                                else:
                                    print(f"❌ {action_result.get('message', 'Aktion fehlgeschlagen')}")
                            
                            # Kurze Pause
                            time.sleep(1)
                        else:
                            print("❌ Aktion konnte nicht ausgeführt werden!")
                    else:
                        print("❌ Ungültiger Move-Index!")
                except ValueError:
                    print("❌ Ungültige Eingabe!")
            
        elif choice == '2':  # Zähmen
            print("🎣 Zähmen wird noch nicht implementiert...")
            time.sleep(1)
            
        elif choice == '3':  # Items
            print("🎒 Items werden noch nicht implementiert...")
            time.sleep(1)
            
        elif choice == '4':  # Team
            print("👥 Team-Wechsel wird noch nicht implementiert...")
            time.sleep(1)
            
        elif choice == '5':  # Spähen
            print("🔍 Spähen wird noch nicht implementiert...")
            time.sleep(1)
            
        elif choice == '6':  # Fliehen
            print("🏃‍♂️ Flucht wird noch nicht implementiert...")
            time.sleep(1)
    
    # Kampf-Ende
    print_battle_status(battle_state)
    battle_result = battle_state.get_battle_result()
    
    print("\n🏁 KAMPF BEENDET!")
    print(f"Gewinner: {battle_result.get('winner', 'Unbekannt')}")
    print(f"Geld gewonnen: {battle_result.get('money_earned', 0)}€")
    print(f"Runden gespielt: {battle_result.get('turns', 0)}")
    
    if battle_result.get('winner') == 'player':
        print("🎉 Glückwunsch! Du hast gewonnen!")
    else:
        print("💀 Du wurdest besiegt...")

def main():
    """Hauptfunktion."""
    print("🎮 INTERAKTIVER BATTLE-TEST")
    print("="*50)
    print("Dieser Test simuliert einen echten Kampf!")
    print("Du kannst alle Battle-Funktionen ausprobieren.")
    print("="*50)
    
    try:
        simulate_battle()
    except KeyboardInterrupt:
        print("\n\n⏹️ Test abgebrochen vom Benutzer")
    except Exception as e:
        print(f"\n💥 Fehler beim Test: {str(e)}")
    
    print("\n👋 Test beendet!")

if __name__ == "__main__":
    main()
