#!/usr/bin/env python3
"""
🎮 Untold Story - Monster Migration Script
Konvertiert monsters.json von learnset-basiert zu talent-basiert

Dieses Script migriert alle Monster von Pokémon-style Learnsets
zu DQM-style Talents basierend auf den Type-Mappings.
"""

import json
import logging
from typing import Dict, List, Any, Set
from pathlib import Path

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MonsterTalentMigrator:
    """Migriert Monster von Learnsets zu Talents"""
    
    def __init__(self):
        self.type_talent_mapping = {
            "Feuer": ["fire_i"],
            "Wasser": ["water_i"], 
            "Erde": ["earth_i"],
            "Luft": ["air_i"],
            "Pflanze": ["plant_i"],
            "Bestie": ["beast_i"],
            "Energie": ["energy_i"],
            "Chaos": ["chaos_i"],
            "Seuche": ["plague_i"],
            "Mystisch": ["mystic_i"],
            "Gottheit": ["divine_i"],
            "Teufel": ["demon_i"]
        }
        
        # Move-zu-Talent Mapping (vereinfacht)
        self.move_talent_mapping = {
            # Feuer Moves
            "Kratzer": "physical_i",
            "Funken": "fire_i", 
            "Feuerball": "fire_i",
            "Flammenwurf": "fire_i",
            "Glut": "fire_i",
            
            # Wasser Moves
            "Aquaknarre": "water_i",
            "Blubbstrahl": "water_i", 
            "Hydropumpe": "water_i",
            "Tsunami": "water_i",
            
            # Erde Moves
            "Steinwurf": "earth_i",
            "Erdbeben": "earth_i",
            "Lehmschuss": "earth_i",
            "Sandsturm": "earth_i",
            
            # Pflanze Moves
            "Rankenhieb": "plant_i",
            "Rasierblatt": "plant_i",
            "Solarstrahl": "plant_i",
            "Blättertanz": "plant_i",
            
            # Bestie Moves
            "Brüllen": "beast_i",
            "Klauenhieb": "beast_i",
            "Wilder Zorn": "beast_i",
            "Bestienbrüllen": "beast_i",
            
            # Energie Moves
            "Donnerschock": "energy_i",
            "Blitzschlag": "energy_i",
            "Gewaltiger Blitz": "energy_i",
            "Göttlicher Blitz": "energy_i",
            
            # Support Moves
            "Heuler": "physical_i",
            "Härtner": "support_i",
            "Heil": "heal_i",
            "Antidot": "heal_i"
        }
        
        self.migrated_count = 0
        self.error_count = 0
        
    def migrate_monster(self, monster_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migriert ein einzelnes Monster von learnset zu talents"""
        try:
            # Kopiere Monster-Daten
            migrated_monster = monster_data.copy()
            
            # Bestimme Start-Talents basierend auf Types
            start_talents = self._determine_start_talents(monster_data)
            
            # Erstelle talents-Array
            talents = []
            for talent_id in start_talents:
                talents.append({
                    "talent_id": talent_id,
                    "learned_at_level": 1,
                    "current_tier": 1,
                    "experience": 0
                })
            
            # Füge talents hinzu
            migrated_monster["talents"] = talents
            
            # Entferne learnset (optional - für Rückwärtskompatibilität behalten)
            # migrated_monster.pop("learnset", None)
            
            # Validiere Migration
            if len(talents) != 2:
                logger.warning(f"Monster {monster_data.get('name', 'Unknown')} hat {len(talents)} Talents statt 2")
            
            self.migrated_count += 1
            logger.info(f"✅ {monster_data.get('name', 'Unknown')}: {[t['talent_id'] for t in talents]}")
            
            return migrated_monster
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Migration von {monster_data.get('name', 'Unknown')}: {e}")
            self.error_count += 1
            return monster_data
    
    def _determine_start_talents(self, monster_data: Dict[str, Any]) -> List[str]:
        """Bestimmt Start-Talents für ein Monster"""
        talents = set()
        
        # Jedes Monster bekommt physical_i als Basis
        talents.add("physical_i")
        
        # Type-spezifische Talents
        types = monster_data.get("types", [])
        for monster_type in types:
            if monster_type in self.type_talent_mapping:
                talents.update(self.type_talent_mapping[monster_type])
        
        # Falls kein Type-Talent gefunden, füge ein generisches hinzu
        if len(talents) == 1:  # Nur physical_i
            # Füge ein passendes Talent basierend auf dem ersten Type hinzu
            if types:
                first_type = types[0]
                if first_type in self.type_talent_mapping:
                    talents.update(self.type_talent_mapping[first_type])
                else:
                    # Fallback für unbekannte Types
                    talents.add("physical_i")  # Duplikat, aber sicher
        
        return list(talents)[:2]  # Maximal 2 Talents
    
    def migrate_monsters_file(self, input_file: str, output_file: str = None):
        """Migriert komplette monsters.json Datei"""
        try:
            # Lade Monster-Daten
            with open(input_file, 'r', encoding='utf-8') as f:
                monsters_data = json.load(f)
            
            # Handle verschiedene JSON-Formate
            if isinstance(monsters_data, dict) and "monsters" in monsters_data:
                monsters_list = monsters_data["monsters"]
            elif isinstance(monsters_data, list):
                monsters_list = monsters_data
            else:
                raise ValueError("Ungültiges JSON-Format")
            
            logger.info(f"📖 Lade {len(monsters_list)} Monster aus {input_file}")
            
            # Migriere alle Monster
            migrated_monsters = []
            for monster_data in monsters_list:
                migrated_monster = self.migrate_monster(monster_data)
                migrated_monsters.append(migrated_monster)
            
            # Bestimme Output-Datei
            if output_file is None:
                input_path = Path(input_file)
                output_file = input_path.parent / f"{input_path.stem}_migrated{input_path.suffix}"
            
            # Speichere migrierte Daten
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(migrated_monsters, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Migrierte Monster gespeichert in {output_file}")
            logger.info(f"📊 Migration abgeschlossen: {self.migrated_count} erfolgreich, {self.error_count} Fehler")
            
            return output_file
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Datei-Migration: {e}")
            raise
    
    def validate_migration(self, monsters_file: str) -> bool:
        """Validiert die Migration"""
        try:
            with open(monsters_file, 'r', encoding='utf-8') as f:
                monsters_data = json.load(f)
            
            if isinstance(monsters_data, dict) and "monsters" in monsters_data:
                monsters_list = monsters_data["monsters"]
            elif isinstance(monsters_data, list):
                monsters_list = monsters_data
            else:
                return False
            
            validation_errors = []
            
            for monster_data in monsters_list:
                # Prüfe ob talents-Feld vorhanden
                if "talents" not in monster_data:
                    validation_errors.append(f"Monster {monster_data.get('name', 'Unknown')} hat kein talents-Feld")
                    continue
                
                talents = monster_data["talents"]
                
                # Prüfe Anzahl der Talents
                if len(talents) != 2:
                    validation_errors.append(f"Monster {monster_data.get('name', 'Unknown')} hat {len(talents)} Talents statt 2")
                
                # Prüfe Talent-Struktur
                for talent in talents:
                    required_fields = ["talent_id", "learned_at_level", "current_tier", "experience"]
                    for field in required_fields:
                        if field not in talent:
                            validation_errors.append(f"Monster {monster_data.get('name', 'Unknown')} Talent fehlt Feld: {field}")
            
            if validation_errors:
                logger.error("❌ Validierung fehlgeschlagen:")
                for error in validation_errors:
                    logger.error(f"  - {error}")
                return False
            else:
                logger.info("✅ Validierung erfolgreich - alle Monster haben korrekte Talent-Struktur")
                return True
                
        except Exception as e:
            logger.error(f"❌ Fehler bei Validierung: {e}")
            return False

def main():
    """Hauptfunktion für Command-Line Usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migriert Monster von Learnsets zu Talents")
    parser.add_argument("input_file", help="Eingabe monsters.json Datei")
    parser.add_argument("-o", "--output", help="Ausgabe-Datei (optional)")
    parser.add_argument("-v", "--validate", action="store_true", help="Validiere Migration")
    
    args = parser.parse_args()
    
    migrator = MonsterTalentMigrator()
    
    try:
        # Migration durchführen
        output_file = migrator.migrate_monsters_file(args.input_file, args.output)
        
        # Validierung falls gewünscht
        if args.validate:
            migrator.validate_migration(output_file)
        
        print(f"\n🎉 Migration abgeschlossen!")
        print(f"📁 Ausgabe: {output_file}")
        print(f"📊 Statistiken: {migrator.migrated_count} Monster migriert, {migrator.error_count} Fehler")
        
    except Exception as e:
        logger.error(f"❌ Migration fehlgeschlagen: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
