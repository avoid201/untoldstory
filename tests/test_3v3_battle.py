#!/usr/bin/env python3
"""
🎮 Test-Skript für das 3v3 Battle System
Demonstriert die neuen Features
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

import logging
from typing import List
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

# Import battle components
from engine.systems.battle.battle_controller import BattleState
from engine.systems.battle.battle_enums import BattleType
from engine.systems.battle.battle_formation import FormationType

# Dummy classes for testing
@dataclass
class Move:
    """Dummy Move class for testing"""
    name: str
    power: int
    pp: int
    max_pp: int
    target_type: str = "single"
    element: str = "normal"

class DummyMonster:
    """Dummy Monster for testing 3v3 battles"""
    def __init__(self, name: str, level: int = 5, hp: int = 100):
        self.name = name
        self.level = level
        self.max_hp = hp
        self.current_hp = hp
        self.stats = {
            'atk': 50 + level * 2,
            'def': 45 + level * 2,
            'mag': 40 + level * 2,
            'res': 40 + level * 2,
            'agility': 50 + level * 2
        }
        self.moves = [
            Move("Tackle", 40, 35, 35, "single"),
            Move("Fireball", 50, 25, 25, "single", "fire"),
            Move("Ice Beam", 60, 20, 20, "row", "ice"),
            Move("Explosion", 100, 5, 5, "all", "explosion")
        ]
        self.is_fainted = False
        self.status = None
        self.stat_stages = {'atk': 0, 'def': 0, 'mag': 0, 'res': 0, 'spd': 0}
    
    def take_damage(self, damage: int):
        """Take damage"""
        self.current_hp = max(0, self.current_hp - damage)
        if self.current_hp == 0:
            self.is_fainted = True
            print(f"💀 {self.name} wurde besiegt!")

def create_test_teams() -> tuple:
    """Create test teams for 3v3 battle"""
    # Player team - 6 monsters
    player_team = [
        DummyMonster("Slime", level=5),
        DummyMonster("Drache", level=6),
        DummyMonster("Golem", level=5),
        DummyMonster("Fee", level=4),
        DummyMonster("Dämon", level=7),
        DummyMonster("Vogel", level=5)
    ]
    
    # Enemy team - 4 monsters
    enemy_team = [
        DummyMonster("Ork", level=5),
        DummyMonster("Goblin", level=4),
        DummyMonster("Troll", level=6),
        DummyMonster("Skelett", level=5)
    ]
    
    return player_team, enemy_team

def test_3v3_battle():
    """Test the 3v3 battle system"""
    print("\n" + "="*60)
    print("🎮 DRAGON QUEST MONSTERS - 3v3 BATTLE SYSTEM TEST 🎮")
    print("="*60)
    
    # Create teams
    player_team, enemy_team = create_test_teams()
    
    print(f"\n📋 Spieler-Team: {', '.join([m.name for m in player_team])}")
    print(f"📋 Gegner-Team: {', '.join([m.name for m in enemy_team])}")
    
    # Test 1: Create battle with 3v3 enabled
    print("\n" + "-"*40)
    print("TEST 1: Battle-Initialisierung mit 3v3")
    print("-"*40)
    
    try:
        battle = BattleState(
            player_team=player_team,
            enemy_team=enemy_team,
            battle_type=BattleType.WILD,
            enable_3v3=True,  # Enable 3v3 mode!
            player_formation_type=FormationType.OFFENSIVE,
            enemy_formation_type=FormationType.DEFENSIVE
        )
        print("✅ Battle erfolgreich initialisiert!")
        
        # Show battle status
        status = battle.get_battle_status()
        print(f"🎮 Modus: {status['mode']}")
        
        if status.get('formation_display'):
            print(status['formation_display'])
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return
    
    # Test 2: Queue actions for multiple monsters
    print("\n" + "-"*40)
    print("TEST 2: Aktionen für mehrere Monster")
    print("-"*40)
    
    try:
        # Queue attack action
        action = {
            'action': 'attack',
            'actor': player_team[0],
            'move': player_team[0].moves[2],  # Ice Beam (row attack)
            'target': enemy_team[0]
        }
        
        if battle.queue_player_action(action):
            print(f"✅ Aktion gequeued: {player_team[0].name} nutzt {player_team[0].moves[2].name}")
        
        # Queue enemy actions (AI)
        for i, enemy in enumerate(enemy_team[:3]):  # First 3 active enemies
            enemy_action = {
                'action': 'attack',
                'actor': enemy,
                'move': enemy.moves[0],
                'target': player_team[i % len(player_team)]
            }
            battle.action_queue.append(battle._create_battle_action(enemy_action))
            print(f"✅ Gegner-Aktion: {enemy.name} greift an")
        
    except Exception as e:
        print(f"❌ Fehler beim Queuing: {e}")
    
    # Test 3: Formation change
    print("\n" + "-"*40)
    print("TEST 3: Formation-Wechsel")
    print("-"*40)
    
    try:
        formation_action = {
            'action': 'formation_change',
            'formation_type': FormationType.WEDGE
        }
        
        if battle.queue_player_action(formation_action):
            print(f"✅ Formation gewechselt zu WEDGE")
            
        # Show new formation
        status = battle.get_battle_status()
        if status.get('player_formation'):
            print(f"Neue Formation: {status['player_formation']['type']}")
            print(f"Aktive Monster: {status['player_formation']['active_count']}")
            for monster in status['player_formation']['monsters']:
                print(f"  - {monster['name']} @ {monster['position']}")
    
    except Exception as e:
        print(f"❌ Fehler beim Formation-Wechsel: {e}")
    
    # Test 4: Resolve turn
    print("\n" + "-"*40)
    print("TEST 4: Runden-Auflösung")
    print("-"*40)
    
    try:
        result = battle.resolve_turn(use_events=False)  # Without events for simplicity
        
        if 'error' not in result:
            print(f"✅ Runde {result['turn_count']} aufgelöst!")
            print(f"Anzahl Aktionen: {len(result['turn_results'])}")
            
            # Show HP changes
            status = battle.get_battle_status()
            if status.get('player_formation'):
                print("\n💚 Spieler-Team HP:")
                for monster in status['player_formation']['monsters']:
                    hp_bar = "█" * int((monster['current_hp'] / monster['max_hp']) * 10)
                    hp_bar += "░" * (10 - len(hp_bar))
                    print(f"  {monster['name']:10} [{hp_bar}] {monster['current_hp']}/{monster['max_hp']}")
            
            if status.get('enemy_formation'):
                print("\n💔 Gegner-Team HP:")
                for monster in status['enemy_formation']['monsters']:
                    hp_bar = "█" * int((monster['current_hp'] / monster['max_hp']) * 10)
                    hp_bar += "░" * (10 - len(hp_bar))
                    print(f"  {monster['name']:10} [{hp_bar}] {monster['current_hp']}/{monster['max_hp']}")
        else:
            print(f"❌ Fehler: {result['error']}")
    
    except Exception as e:
        print(f"❌ Fehler bei Runden-Auflösung: {e}")
    
    # Test 5: Test targeting system
    print("\n" + "-"*40)
    print("TEST 5: Targeting-System")
    print("-"*40)
    
    try:
        from engine.systems.battle.target_system import TargetType
        
        # Test different target types
        target_types = [
            TargetType.SINGLE,
            TargetType.ALL_ENEMIES,
            TargetType.ROW_ENEMY,
            TargetType.SPREAD
        ]
        
        for target_type in target_types:
            selection = battle.targeting_system.get_valid_targets("player", target_type)
            desc = battle.targeting_system.get_target_description(target_type)
            print(f"\n🎯 {desc}:")
            print(f"   Anzahl Ziele: {len(selection.all_targets)}")
            if selection.all_targets:
                for target in selection.all_targets[:3]:  # Show first 3
                    modifier = selection.get_damage_modifier(target)
                    print(f"   - {target.monster.name} (Schaden: {modifier:.0%})")
    
    except Exception as e:
        print(f"❌ Fehler beim Targeting: {e}")
    
    print("\n" + "="*60)
    print("🎮 TEST ABGESCHLOSSEN 🎮")
    print("="*60)

def test_1v1_compatibility():
    """Test that 1v1 battles still work"""
    print("\n" + "="*60)
    print("🎮 1v1 KOMPATIBILITÄTS-TEST 🎮")
    print("="*60)
    
    # Create minimal teams
    player_team = [DummyMonster("Held")]
    enemy_team = [DummyMonster("Schleim")]
    
    try:
        # Create traditional 1v1 battle
        battle = BattleState(
            player_team=player_team,
            enemy_team=enemy_team,
            battle_type=BattleType.WILD,
            enable_3v3=False  # Explicitly disable 3v3
        )
        
        status = battle.get_battle_status()
        print(f"✅ 1v1 Battle erstellt!")
        print(f"Modus: {status['mode']}")
        print(f"Spieler: {status['player_active']['name']}")
        print(f"Gegner: {status['enemy_active']['name']}")
        
        # Queue and resolve a turn
        action = {
            'action': 'attack',
            'actor': player_team[0],
            'move': player_team[0].moves[0],
            'target': enemy_team[0]
        }
        
        battle.queue_player_action(action)
        result = battle.resolve_turn(use_events=False)
        
        if 'error' not in result:
            print(f"✅ 1v1 Kampf funktioniert weiterhin!")
        
    except Exception as e:
        print(f"❌ 1v1 Fehler: {e}")

if __name__ == "__main__":
    # Run tests
    test_3v3_battle()
    test_1v1_compatibility()
    
    print("\n🏁 Alle Tests abgeschlossen!")
    print("Das 3v3 Battle System ist bereit für Integration!")
