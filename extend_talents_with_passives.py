#!/usr/bin/env python3
"""
Erweitert das Talent-System um passive Fähigkeiten
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

def save_json_file(file_path: str, data):
    """Speichere JSON-Datei sicher."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Fehler beim Speichern von {file_path}: {e}")
        return False

def add_passive_abilities_to_talents(talents_data):
    """Füge passive Fähigkeiten zu Talenten hinzu."""
    
    # Mapping von Talent-Kategorien zu passiven Fähigkeiten
    talent_passive_mapping = {
        "fire_i": ["fire_resistance"],
        "fire_ii": ["fire_resistance", "burn_immunity"],
        "fire_iii": ["fire_resistance", "burn_immunity", "attack_boost"],
        "fire_iv": ["fire_resistance", "burn_immunity", "attack_boost", "elemental_mastery"],
        
        "water_i": ["water_resistance"],
        "water_ii": ["water_resistance", "freeze_immunity"],
        "water_iii": ["water_resistance", "freeze_immunity", "defense_boost"],
        "water_iv": ["water_resistance", "freeze_immunity", "defense_boost", "regeneration"],
        
        "earth_i": ["earth_resistance"],
        "earth_ii": ["earth_resistance", "defense_boost"],
        "earth_iii": ["earth_resistance", "defense_boost", "hp_boost"],
        "earth_iv": ["earth_resistance", "defense_boost", "hp_boost", "guardian"],
        
        "wind_i": ["wind_resistance"],
        "wind_ii": ["wind_resistance", "speed_boost"],
        "wind_iii": ["wind_resistance", "speed_boost", "evasion_boost"],
        "wind_iv": ["wind_resistance", "speed_boost", "evasion_boost", "accuracy_boost"],
        
        "plant_i": ["plant_resistance"],
        "plant_ii": ["plant_resistance", "poison_immunity"],
        "plant_iii": ["plant_resistance", "poison_immunity", "regeneration"],
        "plant_iv": ["plant_resistance", "poison_immunity", "regeneration", "hp_boost"],
        
        "beast_i": ["beast_resistance"],
        "beast_ii": ["beast_resistance", "attack_boost"],
        "beast_iii": ["beast_resistance", "attack_boost", "critical_boost"],
        "beast_iv": ["beast_resistance", "attack_boost", "critical_boost", "physical_mastery"],
        
        "energy_i": ["energy_resistance"],
        "energy_ii": ["energy_resistance", "paralysis_immunity"],
        "energy_iii": ["energy_resistance", "paralysis_immunity", "magic_boost"],
        "energy_iv": ["energy_resistance", "paralysis_immunity", "magic_boost", "mana_regeneration"],
        
        "chaos_i": ["chaos_resistance"],
        "chaos_ii": ["chaos_resistance", "confusion_immunity"],
        "chaos_iii": ["chaos_resistance", "confusion_immunity", "berserker"],
        "chaos_iv": ["chaos_resistance", "confusion_immunity", "berserker", "damage_reflection"],
        
        "poison_i": ["poison_resistance"],
        "poison_ii": ["poison_resistance", "poison_immunity"],
        "poison_iii": ["poison_resistance", "poison_immunity", "life_steal"],
        "poison_iv": ["poison_resistance", "poison_immunity", "life_steal", "mana_steal"],
        
        "mystic_i": ["mystic_resistance"],
        "mystic_ii": ["mystic_resistance", "sleep_immunity"],
        "mystic_iii": ["mystic_resistance", "sleep_immunity", "resistance_boost"],
        "mystic_iv": ["mystic_resistance", "sleep_immunity", "resistance_boost", "magic_mastery"],
        
        "divine_i": ["divine_resistance"],
        "divine_ii": ["divine_resistance", "status_immunity"],
        "divine_iii": ["divine_resistance", "status_immunity", "regeneration"],
        "divine_iv": ["divine_resistance", "status_immunity", "regeneration", "elemental_mastery"],
        
        "devil_i": ["devil_resistance"],
        "devil_ii": ["devil_resistance", "status_immunity"],
        "devil_iii": ["devil_resistance", "status_immunity", "berserker"],
        "devil_iv": ["devil_resistance", "status_immunity", "berserker", "damage_reflection"],
        
        "physical_i": ["attack_boost"],
        "physical_ii": ["attack_boost", "critical_boost"],
        "physical_iii": ["attack_boost", "critical_boost", "accuracy_boost"],
        "physical_iv": ["attack_boost", "critical_boost", "accuracy_boost", "physical_mastery"],
        
        "defense_i": ["defense_boost"],
        "defense_ii": ["defense_boost", "hp_boost"],
        "defense_iii": ["defense_boost", "hp_boost", "evasion_boost"],
        "defense_iv": ["defense_boost", "hp_boost", "evasion_boost", "guardian"],
        
        "heal_i": ["regeneration"],
        "heal_ii": ["regeneration", "mana_regeneration"],
        "heal_iii": ["regeneration", "mana_regeneration", "hp_boost"],
        "heal_iv": ["regeneration", "mana_regeneration", "hp_boost", "status_immunity"],
        
        "support_i": ["speed_boost"],
        "support_ii": ["speed_boost", "accuracy_boost"],
        "support_iii": ["speed_boost", "accuracy_boost", "evasion_boost"],
        "support_iv": ["speed_boost", "accuracy_boost", "evasion_boost", "mana_regeneration"],
        
        "buff_i": ["magic_boost"],
        "buff_ii": ["magic_boost", "resistance_boost"],
        "buff_iii": ["magic_boost", "resistance_boost", "mana_regeneration"],
        "buff_iv": ["magic_boost", "resistance_boost", "mana_regeneration", "magic_mastery"],
        
        "ultimate_i": ["status_immunity"],
        "ultimate_ii": ["status_immunity", "elemental_mastery"],
        "ultimate_iii": ["status_immunity", "elemental_mastery", "physical_mastery"],
        "ultimate_iv": ["status_immunity", "elemental_mastery", "physical_mastery", "magic_mastery"]
    }
    
    # Erweitere jedes Talent um passive Fähigkeiten
    for talent in talents_data.get("talents", []):
        talent_id = talent.get("id", "")
        
        # Füge passive Fähigkeiten basierend auf Talent-ID hinzu
        if talent_id in talent_passive_mapping:
            talent["passive_abilities"] = talent_passive_mapping[talent_id]
        else:
            talent["passive_abilities"] = []
        
        # Füge Tier-basierte passive Fähigkeiten hinzu
        max_tier = talent.get("max_tier", 1)
        current_passives = talent.get("passive_abilities", [])
        
        # Füge zusätzliche passive Fähigkeiten basierend auf Tier hinzu
        if max_tier >= 2:
            if "attack_boost" not in current_passives and "defense_boost" not in current_passives:
                current_passives.append("attack_boost")
        
        if max_tier >= 3:
            if "critical_boost" not in current_passives:
                current_passives.append("critical_boost")
        
        if max_tier >= 4:
            if "status_immunity" not in current_passives:
                current_passives.append("status_immunity")
        
        talent["passive_abilities"] = current_passives
    
    return talents_data

def main():
    """Hauptfunktion."""
    print("🔄 Erweitere Talent-System um passive Fähigkeiten...")
    
    # Lade aktuelle Talent-Daten
    talents_data = load_json_file('data/talents.json')
    if not talents_data:
        print("❌ Konnte talents.json nicht laden")
        return False
    
    print(f"📊 Gefunden: {len(talents_data.get('talents', []))} Talente")
    
    # Erweitere Talente um passive Fähigkeiten
    extended_talents = add_passive_abilities_to_talents(talents_data)
    
    # Erstelle Backup
    backup_path = 'data/talents_backup_passives.json'
    if save_json_file(backup_path, talents_data):
        print(f"💾 Backup erstellt: {backup_path}")
    
    # Speichere erweiterte Talente
    if save_json_file('data/talents.json', extended_talents):
        print("✅ Talent-System erfolgreich erweitert!")
        print(f"📁 {len(extended_talents.get('talents', []))} Talente mit passiven Fähigkeiten")
        return True
    else:
        print("❌ Fehler beim Speichern der erweiterten Talente")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
