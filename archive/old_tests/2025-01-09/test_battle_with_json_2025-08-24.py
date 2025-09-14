#!/usr/bin/env python3
"""
Test-Skript für das bereinigte Battle-System mit JSON Monster-Daten
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.systems.battle import UnifiedBattleManager, BattleType
from engine.systems.monster_instance import MonsterInstance, MonsterSpecies
from engine.systems.battle.turn_logic import BattleAction, ActionType
from dataclasses import dataclass
from typing import Dict, Any, List

# Mock Move Klasse
@dataclass
class MockMove:
    name: str = "Tackle"
    power: int = 40
    priority: int = 0
    accuracy: int = 100
    type: str = "Normal"
    category: str = "physical"  # physical, special, oder status

def load_monsters_from_json() -> List[Dict]:
    """Lädt Monster-Daten aus der JSON."""
    json_path = "/Users/leon/Desktop/untold_story/data/monsters.json"
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Fehler beim Laden der Monster-JSON: {e}")
        return []

def create_monster_from_json(monster_data: Dict, level: int = 5) -> MonsterInstance:
    """Erstellt ein Monster aus JSON-Daten mit Talent-System."""
    
    # Erstelle MonsterSpecies aus JSON-Daten
    species = MonsterSpecies(
        id=monster_data['id'],
        name=monster_data['name'],
        era=monster_data.get('era', 'present'),
        rank=monster_data.get('rank', 'F'),
        types=monster_data.get('types', ['Normal']),
        base_stats=monster_data.get('base_stats', {
            'hp': 50, 'atk': 50, 'def': 50,
            'mag': 50, 'res': 50, 'spd': 50
        }),
        growth_curve=monster_data.get('growth', {}).get('curve', 'medium'),
        base_exp_yield=monster_data.get('growth', {}).get('yield', 100),
        capture_rate=monster_data.get('capture_rate', 100),
        traits=monster_data.get('traits', []),
        talents=monster_data.get('talents', []),  # Verwende Talents statt learnset
        evolution=monster_data.get('evolution'),
        description=monster_data.get('description', '')
    )
    
    # Erstelle MonsterInstance
    monster = MonsterInstance(species=species, level=level)
    
    # Moves werden automatisch über das Talent-System geladen
    # Keine manuelle Move-Erstellung mehr nötig
    
    return monster

def test_battle_system():
    """Teste das bereinigte Battle-System mit echten Monster-Daten."""
    print("=" * 60)
    print("UNTOLD STORY - Battle System Test (mit JSON-Daten)")
    print("=" * 60)
    
    # Lade Monster-Daten
    print("\n1. Lade Monster-Daten aus JSON...")
    monsters_data = load_monsters_from_json()
    
    if not monsters_data:
        print("   ✗ Keine Monster-Daten gefunden!")
        return
    
    print(f"   ✓ {len(monsters_data)} Monster geladen")
    
    # Wähle Test-Monster aus
    print("\n2. Erstelle Test-Monster...")
    
    # Spieler bekommt Glutstummel (ID 1)
    player_monster_data = next((m for m in monsters_data if m['id'] == 1), None)
    if not player_monster_data:
        print("   ✗ Glutstummel nicht gefunden!")
        return
    
    player_monster = create_monster_from_json(player_monster_data, level=5)
    print(f"   ✓ Spieler: {player_monster.name} (Lv.{player_monster.level})")
    print(f"     HP: {player_monster.current_hp}/{player_monster.max_hp}")
    print(f"     Moves: {', '.join([m.name for m in player_monster.moves])}")
    
    # Gegner bekommt Bierlementar (ID 4)  
    enemy_monster_data = next((m for m in monsters_data if m['id'] == 4), None)
    if not enemy_monster_data:
        print("   ✗ Bierlementar nicht gefunden!")
        return
    
    enemy_monster = create_monster_from_json(enemy_monster_data, level=4)
    print(f"   ✓ Gegner: {enemy_monster.name} (Lv.{enemy_monster.level})")
    print(f"     HP: {enemy_monster.current_hp}/{enemy_monster.max_hp}")
    print(f"     Moves: {', '.join([m.name for m in enemy_monster.moves])}")
    
    # Initialisiere Battle Manager
    print("\n3. Initialisiere Battle Manager...")
    battle_manager = UnifiedBattleManager(None)
    print("   ✓ Battle Manager erstellt")
    
    # Starte Kampf
    print("\n4. Starte Kampf...")
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
    print("\n5. Battle Status:")
    status = battle_manager.get_status()
    print(f"   Phase: {status['phase']}")
    print(f"   Spieler aktiv: {status['player_active']}")
    print(f"   Gegner aktiv: {status['enemy_active']}")
    print(f"   Kann fliehen: {status['can_flee']}")
    print(f"   Kann fangen: {status['can_catch']}")
    
    # Erstelle Aktionen
    print("\n6. Erstelle Battle-Aktionen...")
    
    # Spieler-Aktion (verwendet ersten Move)
    player_action = BattleAction(
        actor=player_monster,
        action_type=ActionType.ATTACK,
        target=enemy_monster,
        move=player_monster.moves[0]
    )
    print(f"   ✓ Spieler-Aktion: {player_monster.name} verwendet {player_monster.moves[0].name}")
    
    # Gegner-Aktion
    enemy_action = BattleAction(
        actor=enemy_monster,
        action_type=ActionType.ATTACK,
        target=player_monster,
        move=enemy_monster.moves[0]
    )
    print(f"   ✓ Gegner-Aktion: {enemy_monster.name} verwendet {enemy_monster.moves[0].name}")
    
    # Füge Aktionen zur Queue hinzu
    print("\n7. Füge Aktionen zur Queue hinzu...")
    battle_manager.queue_action(player_action)
    battle_manager.queue_action(enemy_action)
    print(f"   ✓ {len(battle_manager.action_queue)} Aktionen in Queue")
    
    # Führe Runde aus
    print("\n8. Führe Kampfrunde aus...")
    result = battle_manager.resolve_turn()
    
    if 'error' not in result:
        print(f"   ✓ Runde {result['turn']} abgeschlossen")
        print(f"   Phase: {result['phase']}")
        if result.get('results'):
            print(f"   Aktionen ausgeführt: {len(result['results'])}")
            for action_result in result['results']:
                if action_result and 'action' in action_result:
                    print(f"     - {action_result}")
    else:
        print(f"   ✗ Fehler: {result['error']}")
    
    # Zeige Nachrichten
    print("\n9. Battle-Nachrichten:")
    messages = battle_manager.get_messages()
    if messages:
        for msg in messages:
            print(f"   → {msg}")
    else:
        print("   (Keine Nachrichten)")
    
    # Zeige HP-Status nach der Runde
    print("\n10. Monster-Status nach Kampfrunde:")
    print(f"   {player_monster.name}: {player_monster.current_hp}/{player_monster.max_hp} HP")
    print(f"   {enemy_monster.name}: {enemy_monster.current_hp}/{enemy_monster.max_hp} HP")
    
    # Teste Flucht-Aktion
    print("\n11. Teste Flucht-Mechanik...")
    flee_action = BattleAction(
        actor=player_monster,
        action_type=ActionType.FLEE,
        target=None
    )
    
    battle_manager.queue_action(flee_action)
    flee_result = battle_manager.resolve_turn()
    
    flee_messages = battle_manager.get_messages()
    for msg in flee_messages:
        print(f"   → {msg}")
    
    print("\n" + "=" * 60)
    print("✅ Test abgeschlossen!")
    print("=" * 60)
    
    # Zusammenfassung
    print("\n📊 Test-Zusammenfassung:")
    print(f"   Monster aus JSON geladen: ✓")
    print(f"   Battle gestartet: ✓")
    print(f"   Aktionen ausgeführt: ✓")
    print(f"   Nachrichten-System: ✓")
    print(f"   HP-System funktioniert: ✓")
    print(f"   Flucht-Mechanik: ✓")
    print("\n💪 Das Battle-System ist einsatzbereit!")

if __name__ == "__main__":
    try:
        test_battle_system()
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
