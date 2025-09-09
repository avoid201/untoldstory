#!/usr/bin/env python3
"""
Test-Skript für das bereinigte Battle-System
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.systems.battle import UnifiedBattleManager, BattleType
from engine.systems.monster_instance import MonsterInstance
from engine.systems.battle.turn_logic import BattleAction, ActionType
from dataclasses import dataclass
from typing import Dict, Any

# Mock Move Klasse
@dataclass
class MockMove:
    name: str = "Tackle"
    power: int = 40
    priority: int = 0
    accuracy: int = 100
    type: str = "Normal"

def create_test_monster(name: str, level: int = 5) -> MonsterInstance:
    """Erstelle ein Test-Monster."""
    monster = MonsterInstance(
        monster_id=f"test_{name.lower()}",
        level=level,
        nickname=name
    )
    
    # Setze Stats
    monster.stats = {
        'hp': 100,
        'atk': 50,
        'def': 45,
        'mat': 40,
        'mdf': 45,
        'spd': 50
    }
    monster.max_hp = 100
    monster.current_hp = 100
    monster.max_mp = 50
    monster.current_mp = 50
    monster.moves = [MockMove()]
    monster.is_fainted = False
    
    return monster

def test_battle_system():
    """Teste das bereinigte Battle-System."""
    print("=" * 60)
    print("UNTOLD STORY - Battle System Test")
    print("=" * 60)
    
    # Erstelle Test-Monster
    print("\n1. Erstelle Test-Monster...")
    player_monster = create_test_monster("Ruhrpott-Raupe", level=5)
    enemy_monster = create_test_monster("Wilder Kohlenpicker", level=4)
    
    print(f"   ✓ Spieler: {player_monster.name} (Lv.{player_monster.level})")
    print(f"   ✓ Gegner: {enemy_monster.name} (Lv.{enemy_monster.level})")
    
    # Initialisiere Battle Manager
    print("\n2. Initialisiere Battle Manager...")
    battle_manager = UnifiedBattleManager(None)
    print("   ✓ Battle Manager erstellt")
    
    # Starte Kampf
    print("\n3. Starte Kampf...")
    success = battle_manager.start_battle(
        player_team=[player_monster],
        enemy_team=[enemy_monster],
        battle_type=BattleType.WILD
    )
    
    if success:
        print("   ✓ Kampf erfolgreich gestartet!")
    else:
        print("   ✗ Fehler beim Start!")
        return
    
    # Zeige Battle Status
    print("\n4. Battle Status:")
    status = battle_manager.get_status()
    print(f"   Phase: {status['phase']}")
    print(f"   Spieler aktiv: {status['player_active']}")
    print(f"   Gegner aktiv: {status['enemy_active']}")
    
    # Erstelle Aktionen
    print("\n5. Erstelle Battle-Aktionen...")
    
    # Spieler-Aktion
    player_action = BattleAction(
        actor=player_monster,
        action_type=ActionType.ATTACK,
        target=enemy_monster,
        move=player_monster.moves[0]
    )
    
    # Gegner-Aktion
    enemy_action = BattleAction(
        actor=enemy_monster,
        action_type=ActionType.ATTACK,
        target=player_monster,
        move=enemy_monster.moves[0]
    )
    
    print("   ✓ Aktionen erstellt")
    
    # Füge Aktionen zur Queue hinzu
    print("\n6. Füge Aktionen zur Queue hinzu...")
    battle_manager.queue_action(player_action)
    battle_manager.queue_action(enemy_action)
    print(f"   ✓ {len(battle_manager.action_queue)} Aktionen in Queue")
    
    # Führe Runde aus
    print("\n7. Führe Kampfrunde aus...")
    result = battle_manager.resolve_turn()
    
    if 'error' not in result:
        print(f"   ✓ Runde {result['turn']} abgeschlossen")
        print(f"   Phase: {result['phase']}")
        if result.get('results'):
            print(f"   Aktionen ausgeführt: {len(result['results'])}")
    else:
        print(f"   ✗ Fehler: {result['error']}")
    
    # Zeige Nachrichten
    print("\n8. Battle-Nachrichten:")
    messages = battle_manager.get_messages()
    for msg in messages:
        print(f"   → {msg}")
    
    # Zeige HP-Status
    print("\n9. Monster-Status:")
    print(f"   {player_monster.name}: {player_monster.current_hp}/{player_monster.max_hp} HP")
    print(f"   {enemy_monster.name}: {enemy_monster.current_hp}/{enemy_monster.max_hp} HP")
    
    print("\n" + "=" * 60)
    print("✅ Test abgeschlossen!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_battle_system()
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
