#!/usr/bin/env python3
"""
Migration Script für Monster-Talent-System
Konvertiert die aktuelle Talent-Struktur in die neue DQM-basierte Struktur
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

def load_json_file(file_path: str) -> Any:
    """Lade JSON-Datei sicher."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Fehler beim Laden von {file_path}: {e}")
        return None

def save_json_file(file_path: str, data: Any) -> bool:
    """Speichere JSON-Datei sicher."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Fehler beim Speichern von {file_path}: {e}")
        return False

def extract_starting_talents(talents: List[Dict]) -> List[str]:
    """Extrahiere Starting Talents (Level 1)."""
    starting = []
    for talent in talents:
        if talent.get('learned_at_level', 0) == 1:
            starting.append(talent['talent_id'])
    return starting

def extract_learnable_talents(talents: List[Dict]) -> List[str]:
    """Extrahiere learnable Talents (Level > 1)."""
    learnable = []
    for talent in talents:
        if talent.get('learned_at_level', 0) > 1:
            learnable.append(talent['talent_id'])
    return learnable

def extract_talent_learning_levels(talents: List[Dict]) -> Dict[str, int]:
    """Extrahiere Talent Learning Levels."""
    levels = {}
    for talent in talents:
        if talent.get('learned_at_level', 0) > 1:
            levels[talent['talent_id']] = talent['learned_at_level']
    return levels

def migrate_monster(monster: Dict) -> Dict:
    """Migriere ein einzelnes Monster."""
    # Kopiere alle Felder außer 'talents'
    migrated = {k: v for k, v in monster.items() if k != 'talents'}
    
    # Extrahiere Talent-Informationen
    talents = monster.get('talents', [])
    
    migrated['starting_talents'] = extract_starting_talents(talents)
    migrated['learnable_talents'] = extract_learnable_talents(talents)
    migrated['talent_learning_levels'] = extract_talent_learning_levels(talents)
    
    return migrated

def add_default_talents(monster: Dict) -> Dict:
    """Füge Standard-Talents hinzu, falls keine vorhanden."""
    if not monster.get('starting_talents'):
        # Basierend auf Typen Standard-Talents hinzufügen
        types = monster.get('types', [])
        starting_talents = []
        
        for monster_type in types:
            if monster_type == "Feuer":
                starting_talents.append("fire_i")
            elif monster_type == "Wasser":
                starting_talents.append("water_i")
            elif monster_type == "Erde":
                starting_talents.append("earth_i")
            elif monster_type == "Luft":
                starting_talents.append("wind_i")
            elif monster_type == "Pflanze":
                starting_talents.append("plant_i")
            elif monster_type == "Bestie":
                starting_talents.append("physical_i")
            elif monster_type == "Energie":
                starting_talents.append("energy_i")
            elif monster_type == "Chaos":
                starting_talents.append("chaos_i")
            elif monster_type == "Seuche":
                starting_talents.append("poison_i")
            elif monster_type == "Mystik":
                starting_talents.append("mystic_i")
            elif monster_type == "Gottheit":
                starting_talents.append("divine_i")
            elif monster_type == "Teufel":
                starting_talents.append("devil_i")
        
        # Füge immer physical_i hinzu, falls nicht vorhanden
        if "physical_i" not in starting_talents:
            starting_talents.append("physical_i")
        
        monster['starting_talents'] = starting_talents
    
    if not monster.get('learnable_talents'):
        # Standard learnable talents basierend auf Rank
        rank = monster.get('rank', 'F')
        learnable_talents = []
        
        if rank in ['E', 'D']:
            learnable_talents.extend(["defense_i", "heal_i"])
        elif rank in ['C', 'B']:
            learnable_talents.extend(["defense_i", "heal_i", "support_i"])
        elif rank in ['A', 'S']:
            learnable_talents.extend(["defense_i", "heal_i", "support_i", "buff_i"])
        elif rank in ['SS', 'X']:
            learnable_talents.extend(["defense_i", "heal_i", "support_i", "buff_i", "ultimate_i"])
        
        monster['learnable_talents'] = learnable_talents
    
    if not monster.get('talent_learning_levels'):
        # Standard learning levels
        levels = {}
        for i, talent in enumerate(monster.get('learnable_talents', [])):
            levels[talent] = 10 + (i * 5)  # 10, 15, 20, 25, 30...
        monster['talent_learning_levels'] = levels
    
    return monster

def main():
    """Hauptfunktion für die Migration."""
    print("🔄 Starte Monster-Talent-Migration...")
    
    # Lade aktuelle Monster-Daten
    monsters_data = load_json_file('data/monsters.json')
    if not monsters_data:
        print("❌ Konnte monsters.json nicht laden")
        return False
    
    print(f"📊 Gefunden: {len(monsters_data)} Monster")
    
    # Migriere alle Monster
    migrated_monsters = []
    for i, monster in enumerate(monsters_data):
        print(f"🔄 Migriere Monster {i+1}/{len(monsters_data)}: {monster.get('name', 'Unknown')}")
        
        # Migriere Monster
        migrated = migrate_monster(monster)
        
        # Füge Standard-Talents hinzu, falls nötig
        migrated = add_default_talents(migrated)
        
        migrated_monsters.append(migrated)
    
    # Erstelle Backup der originalen Datei
    backup_path = 'data/monsters_backup_talents.json'
    if save_json_file(backup_path, monsters_data):
        print(f"💾 Backup erstellt: {backup_path}")
    
    # Speichere migrierte Daten
    if save_json_file('data/monsters.json', migrated_monsters):
        print("✅ Migration erfolgreich abgeschlossen!")
        print(f"📁 Migrierte {len(migrated_monsters)} Monster")
        return True
    else:
        print("❌ Fehler beim Speichern der migrierten Daten")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
