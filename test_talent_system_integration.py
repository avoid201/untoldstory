#!/usr/bin/env python3
"""
Test für das neue Talent-basierte DQM-System
Validiert Monster-Talent-Integration und passive Fähigkeiten
"""

import sys
import os
import json
from pathlib import Path

# Füge den Projekt-Pfad hinzu
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_talent_system():
    """Teste das Talent-System"""
    print("🎯 Teste Talent-basiertes DQM-System...")
    
    try:
        # Importiere die Systeme
        from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank
        from engine.systems.stats import BaseStats
        from engine.systems.talent_manager import get_talent_manager
        from engine.systems.talent_system import get_talent_database
        
        print("✅ Imports erfolgreich")
        
        # Erstelle Test-Monster
        test_species = MonsterSpecies(
            id="test_slime",
            name="Test-Schleim",
            types=["Feuer"],
            base_stats=BaseStats(40, 50, 40, 30, 30, 50),
            rank=MonsterRank.F,
            talents=[
                {
                    "talent_id": "fire_i",
                    "learned_at_level": 1,
                    "current_tier": 1,
                    "experience": 0
                },
                {
                    "talent_id": "physical_i", 
                    "learned_at_level": 1,
                    "current_tier": 1,
                    "experience": 0
                }
            ]
        )
        
        monster = test_species.create_instance(level=5)
        print(f"✅ Monster erstellt: {monster.name} (Level {monster.level})")
        
        # Teste Talent-System
        print(f"📚 Monster hat {len(monster.talents)} Talents:")
        for talent_instance in monster.talents:
            print(f"  - {talent_instance.talent_id} (Tier {talent_instance.current_tier.value})")
        
        # Teste Moves
        moves = monster.get_available_moves()
        print(f"⚔️ Verfügbare Moves: {len(moves)}")
        for move in moves:
            print(f"  - {move.name} ({move.type})")
        
        # Teste passive Fähigkeiten
        passive_abilities = monster.get_passive_abilities()
        print(f"🛡️ Passive Fähigkeiten: {len(passive_abilities)}")
        for ability in passive_abilities:
            print(f"  - {ability['name']}: {ability['description']}")
        
        # Teste Talent-Manager
        talent_manager = get_talent_manager()
        print(f"🎯 Talent-Manager geladen: {len(talent_manager.learning_rules)} Learning-Regeln")
        
        # Teste lernbare Talents
        learnable = monster.get_learnable_talents()
        print(f"📖 Lernbare Talents: {len(learnable)}")
        for talent_id in learnable:
            print(f"  - {talent_id}")
        
        # Teste Talent-Info
        if learnable:
            talent_info = monster.get_talent_info(learnable[0])
            if talent_info:
                print(f"ℹ️ Talent-Info für {learnable[0]}:")
                print(f"  - Name: {talent_info['name']}")
                print(f"  - Kategorie: {talent_info['category']}")
                print(f"  - Kann gelernt werden: {talent_info['can_learn']}")
        
        print("✅ Alle Tests erfolgreich!")
        return True
        
    except Exception as e:
        print(f"❌ Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_files():
    """Teste die Daten-Dateien"""
    print("\n📁 Teste Daten-Dateien...")
    
    try:
        # Teste moves.json
        moves_file = Path("data/moves.json")
        if moves_file.exists():
            with open(moves_file, 'r', encoding='utf-8') as f:
                moves_data = json.load(f)
            print(f"✅ moves.json: {len(moves_data['moves'])} Moves")
        else:
            print("❌ moves.json nicht gefunden")
        
        # Teste talents.json
        talents_file = Path("data/talents.json")
        if talents_file.exists():
            with open(talents_file, 'r', encoding='utf-8') as f:
                talents_data = json.load(f)
            print(f"✅ talents.json: {len(talents_data['talents'])} Talents")
        else:
            print("❌ talents.json nicht gefunden")
        
        # Teste passive_abilities.json
        passive_file = Path("data/passive_abilities.json")
        if passive_file.exists():
            with open(passive_file, 'r', encoding='utf-8') as f:
                passive_data = json.load(f)
            print(f"✅ passive_abilities.json: {len(passive_data['passive_abilities'])} passive Fähigkeiten")
        else:
            print("❌ passive_abilities.json nicht gefunden")
        
        # Teste talent_learning.json
        learning_file = Path("data/talent_learning.json")
        if learning_file.exists():
            with open(learning_file, 'r', encoding='utf-8') as f:
                learning_data = json.load(f)
            print(f"✅ talent_learning.json: Learning-Regeln geladen")
        else:
            print("❌ talent_learning.json nicht gefunden")
        
        # Teste monsters.json
        monsters_file = Path("data/monsters.json")
        if monsters_file.exists():
            with open(monsters_file, 'r', encoding='utf-8') as f:
                monsters_data = json.load(f)
            print(f"✅ monsters.json: {len(monsters_data)} Monster")
            
            # Prüfe ob Monster Talents haben
            monsters_with_talents = 0
            for monster in monsters_data:
                if 'talents' in monster and monster['talents']:
                    monsters_with_talents += 1
            
            print(f"  - {monsters_with_talents} Monster haben Talents definiert")
        else:
            print("❌ monsters.json nicht gefunden")
        
        return True
        
    except Exception as e:
        print(f"❌ Daten-Test fehlgeschlagen: {e}")
        return False

def main():
    """Hauptfunktion"""
    print("🚀 Starte Talent-System-Integration-Test")
    print("=" * 50)
    
    # Teste Daten-Dateien
    data_success = test_data_files()
    
    # Teste Talent-System
    system_success = test_talent_system()
    
    print("\n" + "=" * 50)
    if data_success and system_success:
        print("🎉 Alle Tests erfolgreich! Talent-System ist einsatzbereit.")
        return 0
    else:
        print("💥 Einige Tests fehlgeschlagen. Bitte Fehler beheben.")
        return 1

if __name__ == "__main__":
    exit(main())
