#!/usr/bin/env python3
"""
Monster JSON Cleanup Tool
Bereinigt die monsters.json Datei von Learnset-Referenzen und fügt Talents hinzu.
"""

import json
import sys
from typing import Dict, List, Any, Optional
from collections import defaultdict

class MonsterJSONCleanup:
    """Bereinigt die monsters.json Datei"""
    
    def __init__(self, input_file: str = "data/monsters.json", output_file: str = "data/monsters_cleaned.json"):
        self.input_file = input_file
        self.output_file = output_file
        self.monsters = []
        self.cleanup_stats = {
            'total_monsters': 0,
            'learnsets_removed': 0,
            'talents_added': 0,
            'errors': 0
        }
    
    def load_monsters(self) -> bool:
        """Lade die Monster-Daten"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                self.monsters = json.load(f)
            self.cleanup_stats['total_monsters'] = len(self.monsters)
            print(f"✅ {len(self.monsters)} Monster geladen")
            return True
        except Exception as e:
            print(f"❌ Fehler beim Laden: {e}")
            return False
    
    def get_default_talents_for_types(self, types: List[str]) -> List[Dict[str, Any]]:
        """Erstelle Standard-Talents basierend auf Monster-Types"""
        talents = []
        
        # Type-zu-Talent-Mapping
        type_talent_mapping = {
            'Feuer': [
                {'talent_id': 'fire_i', 'learned_at_level': 1, 'current_tier': 1, 'experience': 0}
            ],
            'Wasser': [
                {'talent_id': 'water_i', 'learned_at_level': 1, 'current_tier': 1, 'experience': 0}
            ],
            'Pflanze': [
                {'talent_id': 'nature_i', 'learned_at_level': 1, 'current_tier': 1, 'experience': 0}
            ],
            'Elektro': [
                {'talent_id': 'thunder_i', 'learned_at_level': 1, 'current_tier': 1, 'experience': 0}
            ],
            'Eis': [
                {'talent_id': 'ice_i', 'learned_at_level': 1, 'current_tier': 1, 'experience': 0}
            ],
            'Kampf': [
                {'talent_id': 'physical_i', 'learned_at_level': 1, 'current_tier': 1, 'experience': 0}
            ],
            'Gift': [
                {'talent_id': 'poison_i', 'learned_at_level': 1, 'current_tier': 1, 'experience': 0}
            ],
            'Boden': [
                {'talent_id': 'earth_i', 'learned_at_level': 1, 'current_tier': 1, 'experience': 0}
            ],
            'Flug': [
                {'talent_id': 'air_i', 'learned_at_level': 1, 'current_tier': 1, 'experience': 0}
            ],
            'Psycho': [
                {'talent_id': 'psychic_i', 'learned_at_level': 1, 'current_tier': 1, 'experience': 0}
            ],
            'Geist': [
                {'talent_id': 'spirit_i', 'learned_at_level': 1, 'current_tier': 1, 'experience': 0}
            ],
            'Drache': [
                {'talent_id': 'dragon_i', 'learned_at_level': 1, 'current_tier': 1, 'experience': 0}
            ],
            'Stahl': [
                {'talent_id': 'metal_i', 'learned_at_level': 1, 'current_tier': 1, 'experience': 0}
            ],
            'Normal': [
                {'talent_id': 'physical_i', 'learned_at_level': 1, 'current_tier': 1, 'experience': 0}
            ]
        }
        
        # Füge Talents für jeden Type hinzu
        for monster_type in types:
            if monster_type in type_talent_mapping:
                talents.extend(type_talent_mapping[monster_type])
        
        # Füge immer ein Basis-Physical-Talent hinzu
        if not any(t['talent_id'] == 'physical_i' for t in talents):
            talents.append({'talent_id': 'physical_i', 'learned_at_level': 1, 'current_tier': 1, 'experience': 0})
        
        return talents
    
    def cleanup_monster(self, monster: Dict[str, Any]) -> Dict[str, Any]:
        """Bereinige ein einzelnes Monster"""
        cleaned_monster = monster.copy()
        
        # Entferne Learnset
        if 'learnset' in cleaned_monster:
            del cleaned_monster['learnset']
            self.cleanup_stats['learnsets_removed'] += 1
        
        # Füge Talents hinzu (nur wenn noch keine vorhanden)
        if 'talents' not in cleaned_monster or not cleaned_monster['talents']:
            types = cleaned_monster.get('types', ['Normal'])
            talents = self.get_default_talents_for_types(types)
            cleaned_monster['talents'] = talents
            self.cleanup_stats['talents_added'] += 1
        
        return cleaned_monster
    
    def cleanup_all_monsters(self) -> bool:
        """Bereinige alle Monster"""
        print("🧹 Starte Bereinigung...")
        
        cleaned_monsters = []
        
        for i, monster in enumerate(self.monsters):
            try:
                cleaned_monster = self.cleanup_monster(monster)
                cleaned_monsters.append(cleaned_monster)
                
                if (i + 1) % 50 == 0:
                    print(f"  Verarbeitet: {i + 1}/{len(self.monsters)}")
                    
            except Exception as e:
                print(f"❌ Fehler bei Monster {i + 1}: {e}")
                self.cleanup_stats['errors'] += 1
                # Füge Original-Monster hinzu bei Fehlern
                cleaned_monsters.append(monster)
        
        self.monsters = cleaned_monsters
        print(f"✅ Bereinigung abgeschlossen: {len(cleaned_monsters)} Monster")
        return True
    
    def save_cleaned_monsters(self) -> bool:
        """Speichere die bereinigten Monster"""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.monsters, f, indent=2, ensure_ascii=False)
            print(f"✅ Bereinigte Monster gespeichert: {self.output_file}")
            return True
        except Exception as e:
            print(f"❌ Fehler beim Speichern: {e}")
            return False
    
    def create_backup(self) -> bool:
        """Erstelle Backup der Original-Datei"""
        try:
            import shutil
            backup_file = f"{self.input_file}.backup"
            shutil.copy2(self.input_file, backup_file)
            print(f"✅ Backup erstellt: {backup_file}")
            return True
        except Exception as e:
            print(f"❌ Fehler beim Backup: {e}")
            return False
    
    def show_cleanup_stats(self):
        """Zeige Bereinigungs-Statistiken"""
        print("\n📊 BEREINIGUNGS-STATISTIKEN")
        print("=" * 40)
        print(f"Gesamt Monster: {self.cleanup_stats['total_monsters']}")
        print(f"Learnsets entfernt: {self.cleanup_stats['learnsets_removed']}")
        print(f"Talents hinzugefügt: {self.cleanup_stats['talents_added']}")
        print(f"Fehler: {self.cleanup_stats['errors']}")
        
        if self.cleanup_stats['errors'] == 0:
            print("🎉 Bereinigung erfolgreich!")
        else:
            print("⚠️  Bereinigung mit Fehlern abgeschlossen")
    
    def run_cleanup(self):
        """Führe die vollständige Bereinigung durch"""
        print("🎮 MONSTER JSON CLEANUP TOOL")
        print("=" * 50)
        
        # Lade Monster
        if not self.load_monsters():
            return False
        
        # Erstelle Backup
        if not self.create_backup():
            print("⚠️  Backup fehlgeschlagen, aber fortfahren...")
        
        # Bereinige Monster
        if not self.cleanup_all_monsters():
            return False
        
        # Speichere bereinigte Monster
        if not self.save_cleaned_monsters():
            return False
        
        # Zeige Statistiken
        self.show_cleanup_stats()
        
        return True

def main():
    """Hauptfunktion"""
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "data/monsters.json"
    
    output_file = input_file.replace('.json', '_cleaned.json')
    
    cleanup = MonsterJSONCleanup(input_file, output_file)
    success = cleanup.run_cleanup()
    
    if success:
        print(f"\n✅ Bereinigung abgeschlossen!")
        print(f"📁 Original: {input_file}")
        print(f"📁 Bereinigt: {output_file}")
        print(f"📁 Backup: {input_file}.backup")
    else:
        print("\n❌ Bereinigung fehlgeschlagen!")
        sys.exit(1)

if __name__ == "__main__":
    main()
