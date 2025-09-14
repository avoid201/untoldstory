#!/usr/bin/env python3
"""
🔄 Monster Learnset zu Talent-System Migration
Konvertiert bestehende Monster-Learnsets zu DQM-Talent-System
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Set

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LearnsetToTalentMigrator:
    """Migriert Monster-Learnsets zu Talent-System"""
    
    def __init__(self):
        self.move_to_talent_mapping = self._create_move_to_talent_mapping()
        self.type_to_talent_mapping = self._create_type_to_talent_mapping()
        self.migrated_monsters = 0
        self.migrated_moves = 0
    
    def _create_move_to_talent_mapping(self) -> Dict[str, str]:
        """Erstelle Mapping von Move-IDs zu Talent-IDs"""
        return {
            # Feuer-Moves
            "Kratzer": "physical_i",
            "Funken": "fire_i", 
            "Feuerball": "fire_i",
            "Flammenwurf": "fire_i",
            "Glut": "fire_i",
            "Frizz": "fire_i",
            "Frizzle": "fire_i",
            "Kafrizz": "fire_i",
            "Kazfrizzle": "fire_i",
            "Sizz": "fire_group",
            "Sizzle": "fire_group",
            "Kasizz": "fire_group",
            "Kasizzle": "fire_group",
            
            # Eis-Moves
            "Crack": "ice_i",
            "Crackle": "ice_i",
            "Kacrack": "ice_i",
            "Kacrackle": "ice_i",
            
            # Blitz-Moves
            "Zap": "thunder_i",
            "Zapple": "thunder_i",
            "Kazap": "thunder_i",
            "Kazapple": "thunder_i",
            "Zammle": "thunder_group",
            "Thwack": "thunder_group",
            "Kathwack": "thunder_group",
            
            # Wind-Moves
            "Woosh": "wind_i",
            "Swoosh": "wind_i",
            "Kaswoosh": "wind_i",
            "Kaswooshle": "wind_i",
            "Windstoß": "wind_i",
            "Orkan": "wind_i",
            
            # Explosion-Moves
            "Bang": "explosion_i",
            "Boom": "explosion_i",
            "Kaboom": "explosion_i",
            "Kaboomle": "explosion_i",
            
            # Dunkelheit-Moves
            "Zam": "dark_i",
            "Zammle": "dark_i",
            "Kazam": "dark_i",
            "Kazammle": "dark_i",
            "Finsterpuls": "dark_i",
            
            # Heil-Moves
            "Heilung": "heal_i",
            "Heal": "heal_i",
            "Midheal": "heal_i",
            "Fullheal": "heal_i",
            "Omniheal": "heal_i",
            "Multiheal": "multiheal",
            "Moreheal": "multiheal",
            
            # Buff-Moves
            "Härtung": "buff_i",
            "Buff": "buff_i",
            "Kabuff": "buff_i",
            "Oomph": "buff_i",
            "Insulatle": "buff_i",
            "Acceleratle": "speed_buff",
            "Accelerate": "speed_buff",
            
            # Debuff-Moves
            "Knurren": "debuff_i",
            "Sap": "debuff_i",
            "Kasap": "debuff_i",
            "Blunt": "debuff_i",
            "Decelerate": "slow_debuff",
            "Deceleratle": "slow_debuff",
            
            # Status-Moves
            "Verwirrung": "status_i",
            "Snooze": "status_i",
            "Kasnooze": "status_i",
            
            # Atem-Moves
            "Feueratem": "fire_breath",
            "Flame Breath": "fire_breath",
            "Inferno": "fire_breath",
            "Scorch": "fire_breath",
            "Eisatem": "ice_breath",
            "Cool Breath": "ice_breath",
            "Ice Breath": "ice_breath",
            "Blizzard Breath": "ice_breath",
            "Cold Breath": "ice_breath",
            
            # Physical-Moves
            "Rempler": "physical_i",
            "Tackle": "physical_i",
            "Biss": "physical_i",
            "Kopfnuss": "physical_i",
            "Body Slam": "physical_i",
            "Mega Punch": "physical_i",
            
            # Erde-Moves
            "Lehmklatscher": "earth_i",
            "Erdbeben": "earth_i",
            "Steinwurf": "earth_i",
            "Sandsturm": "earth_i",
            
            # Wasser-Moves
            "Wasserpistole": "water_i",
            "Wasserstrahl": "water_i",
            "Bubble Beam": "water_i",
            "Hydropumpe": "water_i",
            "Tsunami": "water_i",
            
            # Pflanze-Moves
            "Rankenhieb": "plant_i",
            "Vine Whip": "plant_i",
            "Razor Leaf": "plant_i",
            "Solar Beam": "plant_i",
            "Petal Dance": "plant_i",
            
            # Bestie-Moves
            "Brüllen": "beast_i",
            "Roar": "beast_i",
            "Claw Slash": "beast_i",
            "Feral Rage": "beast_i",
            "Beast Roar": "beast_i",
            
            # Energie-Moves
            "Energieball": "energy_i",
            "Plasma Beam": "energy_i",
            "Nuclear Blast": "energy_i",
            "Cosmic Ray": "energy_i",
            
            # Chaos-Moves
            "Chaoswelle": "chaos_i",
            "Chaos Bolt": "chaos_i",
            "Entropy Wave": "chaos_i",
            "Reality Tear": "chaos_i",
            "Void Storm": "chaos_i",
            
            # Seuche-Moves
            "Giftstachel": "plague_i",
            "Poison Gas": "plague_i",
            "Toxic Cloud": "plague_i",
            "Plague Wind": "plague_i",
            "Death Breath": "plague_i",
            
            # Mystik-Moves
            "Mystic Bolt": "mystic_i",
            "Arcane Blast": "mystic_i",
            "Spell Weave": "mystic_i",
            "Reality Shift": "mystic_i",
            
            # Gottheit-Moves
            "Göttliches Licht": "divine_i",
            "Holy Light": "divine_i",
            "Divine Judgment": "divine_i",
            "Celestial Beam": "divine_i",
            "Apocalypse": "divine_i",
            
            # Teufel-Moves
            "Hellfire": "demon_i",
            "Demon Claw": "demon_i",
            "Soul Rend": "demon_i",
            "Infernal Storm": "demon_i",
            
            # Tanz-Moves
            "Sultry Dance": "dance",
            "Hustle Dance": "dance",
            "Death Dance": "dance",
            
            # Schnitt-Moves
            "Dragon Slash": "slash",
            "Metal Slash": "slash",
            "Falcon Slash": "slash",
            "Gigaslash": "slash"
        }
    
    def _create_type_to_talent_mapping(self) -> Dict[str, List[str]]:
        """Erstelle Mapping von Monster-Types zu Standard-Talents"""
        return {
            "Feuer": ["fire_i", "fire_breath"],
            "Eis": ["ice_i", "ice_breath"],
            "Blitz": ["thunder_i"],
            "Wind": ["wind_i"],
            "Erde": ["earth_i", "explosion_i"],
            "Pflanze": ["plant_i", "heal_i"],
            "Bestie": ["beast_i", "physical_i"],
            "Energie": ["energy_i", "thunder_i"],
            "Chaos": ["chaos_i", "dark_i"],
            "Seuche": ["plague_i"],
            "Mystik": ["mystic_i", "heal_i"],
            "Gottheit": ["divine_i", "heal_i"],
            "Teufel": ["demon_i", "dark_i"],
            "Wasser": ["water_i", "heal_i"]
        }
    
    def migrate_monster(self, monster_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migriere ein einzelnes Monster von Learnset zu Talent-System"""
        monster_id = monster_data.get("id", "unknown")
        monster_name = monster_data.get("name", "Unknown")
        monster_types = monster_data.get("types", [])
        learnset = monster_data.get("learnset", [])
        
        logger.info(f"Migriere Monster: {monster_name} (ID: {monster_id})")
        
        # Sammle alle Talents die durch Moves benötigt werden
        required_talents = set()
        
        # Jedes Monster bekommt Physical I als Basis
        required_talents.add("physical_i")
        
        # Füge Type-spezifische Talents hinzu
        for monster_type in monster_types:
            if monster_type in self.type_to_talent_mapping:
                required_talents.update(self.type_to_talent_mapping[monster_type])
        
        # Analysiere Learnset und füge entsprechende Talents hinzu
        for learn_entry in learnset:
            move_name = learn_entry.get("move", "")
            if move_name in self.move_to_talent_mapping:
                talent_id = self.move_to_talent_mapping[move_name]
                required_talents.add(talent_id)
                self.migrated_moves += 1
            else:
                logger.warning(f"Move '{move_name}' nicht in Talent-Mapping gefunden")
        
        # Konvertiere zu Talent-Liste
        talents = []
        for talent_id in sorted(required_talents):
            talents.append({
                "talent_id": talent_id,
                "learned_at_level": 1,  # Alle Start-Talents
                "current_tier": 1,
                "experience": 0
            })
        
        # Erstelle neues Monster-Daten-Format
        migrated_monster = monster_data.copy()
        migrated_monster["talents"] = talents
        
        # Entferne altes Learnset (optional - für Rückwärtskompatibilität behalten)
        # migrated_monster.pop("learnset", None)
        
        self.migrated_monsters += 1
        logger.info(f"  -> {len(talents)} Talents zugewiesen: {[t['talent_id'] for t in talents]}")
        
        return migrated_monster
    
    def migrate_monsters_file(self, input_file: str, output_file: str = None):
        """Migriere komplette monsters.json Datei"""
        if output_file is None:
            output_file = input_file.replace(".json", "_talents.json")
        
        logger.info(f"Lade Monster-Daten aus: {input_file}")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                monsters_data = json.load(f)
        except Exception as e:
            logger.error(f"Fehler beim Laden der Monster-Daten: {e}")
            return
        
        logger.info(f"Gefunden: {len(monsters_data)} Monster")
        
        # Migriere alle Monster
        migrated_monsters = []
        for monster_data in monsters_data:
            try:
                migrated_monster = self.migrate_monster(monster_data)
                migrated_monsters.append(migrated_monster)
            except Exception as e:
                logger.error(f"Fehler bei Migration von Monster {monster_data.get('name', 'Unknown')}: {e}")
                # Füge Original-Monster hinzu bei Fehlern
                migrated_monsters.append(monster_data)
        
        # Speichere migrierte Daten
        logger.info(f"Speichere migrierte Daten in: {output_file}")
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(migrated_monsters, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Migration erfolgreich!")
            logger.info(f"   - {self.migrated_monsters} Monster migriert")
            logger.info(f"   - {self.migrated_moves} Moves zu Talents zugeordnet")
            logger.info(f"   - Ausgabedatei: {output_file}")
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern: {e}")
    
    def create_migration_report(self, input_file: str, output_file: str = None):
        """Erstelle detaillierten Migrationsbericht"""
        if output_file is None:
            output_file = input_file.replace(".json", "_migration_report.txt")
        
        logger.info(f"Erstelle Migrationsbericht: {output_file}")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                monsters_data = json.load(f)
        except Exception as e:
            logger.error(f"Fehler beim Laden der Monster-Daten: {e}")
            return
        
        # Analysiere alle Moves und Talents
        all_moves = set()
        all_talents = set()
        type_talent_usage = {}
        move_talent_usage = {}
        
        for monster_data in monsters_data:
            monster_types = monster_data.get("types", [])
            learnset = monster_data.get("learnset", [])
            
            # Sammle Moves
            for learn_entry in learnset:
                move_name = learn_entry.get("move", "")
                all_moves.add(move_name)
                
                if move_name in self.move_to_talent_mapping:
                    talent_id = self.move_to_talent_mapping[move_name]
                    all_talents.add(talent_id)
                    
                    # Zähle Talent-Verwendung
                    if talent_id not in move_talent_usage:
                        move_talent_usage[talent_id] = 0
                    move_talent_usage[talent_id] += 1
            
            # Zähle Type-Talent-Verwendung
            for monster_type in monster_types:
                if monster_type in self.type_to_talent_mapping:
                    for talent_id in self.type_to_talent_mapping[monster_type]:
                        all_talents.add(talent_id)
                        if talent_id not in type_talent_usage:
                            type_talent_usage[talent_id] = 0
                        type_talent_usage[talent_id] += 1
        
        # Erstelle Bericht
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("🔄 MONSTER LEARNSET ZU TALENT-SYSTEM MIGRATIONSBERICHT\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"📊 STATISTIKEN:\n")
            f.write(f"   - Monster analysiert: {len(monsters_data)}\n")
            f.write(f"   - Einzigartige Moves: {len(all_moves)}\n")
            f.write(f"   - Benötigte Talents: {len(all_talents)}\n")
            f.write(f"   - Move-zu-Talent-Mappings: {len(self.move_to_talent_mapping)}\n\n")
            
            f.write("🎯 TALENT-VERWENDUNG (nach Moves):\n")
            for talent_id, count in sorted(move_talent_usage.items(), key=lambda x: x[1], reverse=True):
                f.write(f"   - {talent_id}: {count} Moves\n")
            f.write("\n")
            
            f.write("🏷️ TALENT-VERWENDUNG (nach Types):\n")
            for talent_id, count in sorted(type_talent_usage.items(), key=lambda x: x[1], reverse=True):
                f.write(f"   - {talent_id}: {count} Monster-Types\n")
            f.write("\n")
            
            f.write("❓ NICHT-ZUGEWIESENE MOVES:\n")
            unmapped_moves = all_moves - set(self.move_to_talent_mapping.keys())
            if unmapped_moves:
                for move in sorted(unmapped_moves):
                    f.write(f"   - {move}\n")
            else:
                f.write("   - Alle Moves erfolgreich zugeordnet! ✅\n")
            f.write("\n")
            
            f.write("📋 ALLE BENÖTIGTEN TALENTS:\n")
            for talent_id in sorted(all_talents):
                f.write(f"   - {talent_id}\n")
        
        logger.info(f"✅ Migrationsbericht erstellt: {output_file}")


def main():
    """Hauptfunktion für Migration"""
    migrator = LearnsetToTalentMigrator()
    
    # Pfade
    input_file = "data/monsters.json"
    output_file = "data/monsters_with_talents.json"
    report_file = "data/monsters_migration_report.txt"
    
    # Prüfe ob Eingabedatei existiert
    if not Path(input_file).exists():
        logger.error(f"Eingabedatei nicht gefunden: {input_file}")
        return
    
    # Erstelle Migrationsbericht
    migrator.create_migration_report(input_file, report_file)
    
    # Führe Migration durch
    migrator.migrate_monsters_file(input_file, output_file)
    
    print("\n🎉 MIGRATION ABGESCHLOSSEN!")
    print(f"   - Eingabedatei: {input_file}")
    print(f"   - Ausgabedatei: {output_file}")
    print(f"   - Bericht: {report_file}")


if __name__ == "__main__":
    main()
