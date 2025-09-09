#!/usr/bin/env python3
"""
Validiert die Talent-System-Migration
"""

import json
import sys
from pathlib import Path

def load_json_file(file_path: str):
    """Lade JSON-Datei sicher."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Fehler beim Laden von {file_path}: {e}")
        return None

def validate_monster_migration():
    """Validiere Monster-Migration."""
    print("🔍 Validiere Monster-Migration...")
    
    monsters = load_json_file('data/monsters.json')
    if not monsters:
        print("❌ Konnte monsters.json nicht laden")
        return False
    
    # Prüfe neue Felder
    required_fields = ['starting_talents', 'learnable_talents', 'talent_learning_levels']
    missing_fields = []
    
    for i, monster in enumerate(monsters[:5]):  # Prüfe erste 5 Monster
        print(f"  Monster {i+1}: {monster.get('name', 'Unknown')}")
        
        for field in required_fields:
            if field not in monster:
                missing_fields.append(f"{monster.get('name', 'Unknown')}: {field}")
            else:
                value = monster[field]
                if field == 'starting_talents' and not isinstance(value, list):
                    missing_fields.append(f"{monster.get('name', 'Unknown')}: {field} ist nicht eine Liste")
                elif field == 'learnable_talents' and not isinstance(value, list):
                    missing_fields.append(f"{monster.get('name', 'Unknown')}: {field} ist nicht eine Liste")
                elif field == 'talent_learning_levels' and not isinstance(value, dict):
                    missing_fields.append(f"{monster.get('name', 'Unknown')}: {field} ist nicht ein Dict")
    
    if missing_fields:
        print("❌ Fehlende oder falsche Felder:")
        for field in missing_fields:
            print(f"  - {field}")
        return False
    
    print("✅ Monster-Migration erfolgreich validiert")
    return True

def validate_talent_system():
    """Validiere Talent-System."""
    print("🔍 Validiere Talent-System...")
    
    talents = load_json_file('data/talents.json')
    if not talents:
        print("❌ Konnte talents.json nicht laden")
        return False
    
    # Prüfe passive Fähigkeiten
    talents_list = talents.get('talents', [])
    talents_with_passives = 0
    
    for talent in talents_list:
        if 'passive_abilities' in talent:
            talents_with_passives += 1
    
    print(f"  Talente mit passiven Fähigkeiten: {talents_with_passives}/{len(talents_list)}")
    
    if talents_with_passives == 0:
        print("❌ Keine Talente haben passive Fähigkeiten")
        return False
    
    print("✅ Talent-System erfolgreich validiert")
    return True

def validate_passive_abilities():
    """Validiere passive Fähigkeiten."""
    print("🔍 Validiere passive Fähigkeiten...")
    
    passives = load_json_file('data/passive_abilities.json')
    if not passives:
        print("❌ Konnte passive_abilities.json nicht laden")
        return False
    
    abilities = passives.get('passive_abilities', [])
    print(f"  Passive Fähigkeiten: {len(abilities)}")
    
    # Prüfe Struktur
    required_fields = ['id', 'name', 'description', 'category', 'effect_type', 'effect_value']
    missing_fields = []
    
    for ability in abilities[:5]:  # Prüfe erste 5
        for field in required_fields:
            if field not in ability:
                missing_fields.append(f"{ability.get('id', 'Unknown')}: {field}")
    
    if missing_fields:
        print("❌ Fehlende Felder in passiven Fähigkeiten:")
        for field in missing_fields:
            print(f"  - {field}")
        return False
    
    print("✅ Passive Fähigkeiten erfolgreich validiert")
    return True

def validate_talent_learning():
    """Validiere Talent-Learning-System."""
    print("🔍 Validiere Talent-Learning-System...")
    
    learning = load_json_file('data/talent_learning.json')
    if not learning:
        print("❌ Konnte talent_learning.json nicht laden")
        return False
    
    # Prüfe Hauptstrukturen
    required_sections = ['talent_learning_rules', 'talent_categories', 'learning_conditions', 'synthesis_rules']
    missing_sections = []
    
    for section in required_sections:
        if section not in learning:
            missing_sections.append(section)
    
    if missing_sections:
        print("❌ Fehlende Sektionen in talent_learning.json:")
        for section in missing_sections:
            print(f"  - {section}")
        return False
    
    print("✅ Talent-Learning-System erfolgreich validiert")
    return True

def validate_save_system():
    """Validiere Save-System-Erweiterung."""
    print("🔍 Validiere Save-System-Erweiterung...")
    
    save_file = Path('engine/systems/save.py')
    if not save_file.exists():
        print("❌ save.py nicht gefunden")
        return False
    
    with open(save_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Prüfe auf Talent-Unterstützung
    talent_keywords = ['talent', 'TalentInstance', 'serialize_monster', 'deserialize_monster']
    found_keywords = []
    
    for keyword in talent_keywords:
        if keyword in content:
            found_keywords.append(keyword)
    
    if len(found_keywords) < 3:
        print("❌ Save-System hat nicht genügend Talent-Unterstützung")
        print(f"  Gefundene Keywords: {found_keywords}")
        return False
    
    print("✅ Save-System erfolgreich validiert")
    return True

def main():
    """Hauptfunktion."""
    print("🔍 Validiere Talent-System-Migration...")
    print("=" * 50)
    
    validations = [
        validate_monster_migration,
        validate_talent_system,
        validate_passive_abilities,
        validate_talent_learning,
        validate_save_system
    ]
    
    passed = 0
    total = len(validations)
    
    for validation in validations:
        try:
            if validation():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Fehler bei Validierung: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 Validierung abgeschlossen: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("✅ Alle Validierungen erfolgreich!")
        return True
    else:
        print("❌ Einige Validierungen fehlgeschlagen")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
