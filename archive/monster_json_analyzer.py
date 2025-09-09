#!/usr/bin/env python3
"""
Monster JSON Analyzer
Analysiert die monsters.json Datei und zeigt detaillierte Informationen an.
Hilft bei der Überprüfung der Talent-Migration und Datenstruktur.
"""

import json
import sys
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict
from dataclasses import dataclass

@dataclass
class MonsterInfo:
    """Informationen über ein Monster"""
    id: str
    name: str
    types: List[str]
    has_learnset: bool
    has_talents: bool
    learnset_count: int
    talents_count: int
    level_range: tuple
    rank: str
    era: str

class MonsterJSONAnalyzer:
    """Analysiert die monsters.json Datei"""
    
    def __init__(self, filepath: str = "data/monsters.json"):
        self.filepath = filepath
        self.monsters = []
        self.analysis_results = {}
        
    def load_data(self) -> bool:
        """Lade die Monster-Daten"""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.monsters = json.load(f)
            print(f"✅ {len(self.monsters)} Monster geladen aus {self.filepath}")
            return True
        except Exception as e:
            print(f"❌ Fehler beim Laden der Datei: {e}")
            return False
    
    def analyze_structure(self) -> Dict[str, Any]:
        """Analysiere die Datenstruktur"""
        print("\n🔍 ANALYSE DER DATENSTRUKTUR")
        print("=" * 50)
        
        if not self.monsters:
            return {}
        
        # Analysiere erste 3 Monster als Beispiel
        sample_monsters = self.monsters[:3]
        
        for i, monster in enumerate(sample_monsters):
            print(f"\n📋 MONSTER {i+1} BEISPIEL:")
            print(f"  ID: {monster.get('id', 'N/A')}")
            print(f"  Name: {monster.get('name', 'N/A')}")
            print(f"  Types: {monster.get('types', [])}")
            print(f"  Rank: {monster.get('rank', 'N/A')}")
            print(f"  Era: {monster.get('era', 'N/A')}")
            
            # Prüfe Learnset
            learnset = monster.get('learnset', [])
            print(f"  Learnset: {len(learnset)} Einträge")
            if learnset:
                print(f"    Beispiel: {learnset[0] if learnset else 'N/A'}")
            
            # Prüfe Talents
            talents = monster.get('talents', [])
            print(f"  Talents: {len(talents)} Einträge")
            if talents:
                print(f"    Beispiel: {talents[0] if talents else 'N/A'}")
            
            # Zeige alle verfügbaren Felder
            print(f"  Verfügbare Felder: {list(monster.keys())}")
        
        return {
            'total_monsters': len(self.monsters),
            'sample_fields': list(sample_monsters[0].keys()) if sample_monsters else []
        }
    
    def analyze_migration_status(self) -> Dict[str, Any]:
        """Analysiere den Status der Talent-Migration"""
        print("\n🎯 MIGRATIONS-STATUS ANALYSE")
        print("=" * 50)
        
        migration_stats = {
            'total_monsters': len(self.monsters),
            'with_learnset': 0,
            'with_talents': 0,
            'migrated': 0,
            'not_migrated': 0,
            'learnset_only': 0,
            'talents_only': 0,
            'both': 0
        }
        
        learnset_monsters = []
        talent_monsters = []
        not_migrated = []
        
        for monster in self.monsters:
            has_learnset = 'learnset' in monster and monster['learnset']
            has_talents = 'talents' in monster and monster['talents']
            
            if has_learnset:
                migration_stats['with_learnset'] += 1
                learnset_monsters.append(monster)
            
            if has_talents:
                migration_stats['with_talents'] += 1
                talent_monsters.append(monster)
            
            if has_learnset and has_talents:
                migration_stats['both'] += 1
                migration_stats['migrated'] += 1
            elif has_talents and not has_learnset:
                migration_stats['talents_only'] += 1
                migration_stats['migrated'] += 1
            elif has_learnset and not has_talents:
                migration_stats['learnset_only'] += 1
                migration_stats['not_migrated'] += 1
            else:
                migration_stats['not_migrated'] += 1
                not_migrated.append(monster)
        
        # Zeige Statistiken
        print(f"📊 GESAMTSTATISTIKEN:")
        print(f"  Gesamt Monster: {migration_stats['total_monsters']}")
        print(f"  Mit Learnset: {migration_stats['with_learnset']}")
        print(f"  Mit Talents: {migration_stats['with_talents']}")
        print(f"  Migriert: {migration_stats['migrated']}")
        print(f"  Nicht migriert: {migration_stats['not_migrated']}")
        print(f"  Nur Learnset: {migration_stats['learnset_only']}")
        print(f"  Nur Talents: {migration_stats['talents_only']}")
        print(f"  Beide: {migration_stats['both']}")
        
        # Zeige nicht migrierte Monster
        if not_migrated:
            print(f"\n⚠️  NICHT MIGRIERTE MONSTER ({len(not_migrated)}):")
            for monster in not_migrated[:10]:  # Zeige nur erste 10
                print(f"  - {monster.get('name', 'Unbekannt')} (ID: {monster.get('id', 'N/A')})")
            if len(not_migrated) > 10:
                print(f"  ... und {len(not_migrated) - 10} weitere")
        
        # Zeige Learnset-only Monster
        if learnset_monsters:
            learnset_only = [m for m in learnset_monsters if 'talents' not in m or not m['talents']]
            if learnset_only:
                print(f"\n🔴 NUR LEARNSET ({len(learnset_only)}):")
                for monster in learnset_only[:10]:
                    print(f"  - {monster.get('name', 'Unbekannt')} (ID: {monster.get('id', 'N/A')})")
                if len(learnset_only) > 10:
                    print(f"  ... und {len(learnset_only) - 10} weitere")
        
        return migration_stats
    
    def analyze_learnsets(self) -> Dict[str, Any]:
        """Analysiere die Learnset-Struktur"""
        print("\n📚 LEARNSET ANALYSE")
        print("=" * 50)
        
        learnset_stats = {
            'total_learnsets': 0,
            'total_moves': 0,
            'level_ranges': [],
            'move_frequency': Counter(),
            'learnset_sizes': []
        }
        
        for monster in self.monsters:
            learnset = monster.get('learnset', [])
            if not learnset:
                continue
            
            learnset_stats['total_learnsets'] += 1
            learnset_stats['learnset_sizes'].append(len(learnset))
            learnset_stats['total_moves'] += len(learnset)
            
            for move_entry in learnset:
                if isinstance(move_entry, dict):
                    move_name = move_entry.get('move', move_entry.get('name', 'Unknown'))
                    level = move_entry.get('level', 0)
                    learnset_stats['level_ranges'].append(level)
                    learnset_stats['move_frequency'][move_name] += 1
                elif isinstance(move_entry, str):
                    learnset_stats['move_frequency'][move_entry] += 1
        
        # Zeige Statistiken
        print(f"📊 LEARNSET STATISTIKEN:")
        print(f"  Monster mit Learnset: {learnset_stats['total_learnsets']}")
        print(f"  Gesamt Moves: {learnset_stats['total_moves']}")
        print(f"  Durchschnitt Moves pro Monster: {learnset_stats['total_moves'] / max(learnset_stats['total_learnsets'], 1):.1f}")
        
        if learnset_stats['level_ranges']:
            print(f"  Level-Bereich: {min(learnset_stats['level_ranges'])} - {max(learnset_stats['level_ranges'])}")
        
        # Zeige häufigste Moves
        print(f"\n🔥 HÄUFIGSTE MOVES:")
        for move, count in learnset_stats['move_frequency'].most_common(10):
            print(f"  {move}: {count}x")
        
        return learnset_stats
    
    def analyze_talents(self) -> Dict[str, Any]:
        """Analysiere die Talent-Struktur"""
        print("\n🎭 TALENT ANALYSE")
        print("=" * 50)
        
        talent_stats = {
            'total_talents': 0,
            'talent_frequency': Counter(),
            'talent_categories': Counter(),
            'talent_tiers': Counter(),
            'monster_talent_counts': []
        }
        
        for monster in self.monsters:
            talents = monster.get('talents', [])
            if not talents:
                continue
            
            talent_stats['total_talents'] += len(talents)
            talent_stats['monster_talent_counts'].append(len(talents))
            
            for talent in talents:
                if isinstance(talent, dict):
                    talent_id = talent.get('talent_id', talent.get('id', 'Unknown'))
                    category = talent.get('category', 'Unknown')
                    tier = talent.get('current_tier', talent.get('tier', 'Unknown'))
                    
                    talent_stats['talent_frequency'][talent_id] += 1
                    talent_stats['talent_categories'][category] += 1
                    talent_stats['talent_tiers'][tier] += 1
                elif isinstance(talent, str):
                    talent_stats['talent_frequency'][talent] += 1
        
        # Zeige Statistiken
        print(f"📊 TALENT STATISTIKEN:")
        print(f"  Gesamt Talents: {talent_stats['total_talents']}")
        print(f"  Monster mit Talents: {len(talent_stats['monster_talent_counts'])}")
        if talent_stats['monster_talent_counts']:
            print(f"  Durchschnitt Talents pro Monster: {sum(talent_stats['monster_talent_counts']) / len(talent_stats['monster_talent_counts']):.1f}")
        
        # Zeige häufigste Talents
        print(f"\n🔥 HÄUFIGSTE TALENTS:")
        for talent, count in talent_stats['talent_frequency'].most_common(10):
            print(f"  {talent}: {count}x")
        
        # Zeige Talent-Kategorien
        if talent_stats['talent_categories']:
            print(f"\n📂 TALENT-KATEGORIEN:")
            for category, count in talent_stats['talent_categories'].most_common():
                print(f"  {category}: {count}x")
        
        return talent_stats
    
    def find_issues(self) -> List[Dict[str, Any]]:
        """Finde potentielle Probleme in den Daten"""
        print("\n🔍 PROBLEM-SUCHE")
        print("=" * 50)
        
        issues = []
        
        for i, monster in enumerate(self.monsters):
            monster_id = monster.get('id', f'Index {i}')
            monster_name = monster.get('name', 'Unbekannt')
            
            # Prüfe auf fehlende Felder
            required_fields = ['id', 'name', 'types']
            for field in required_fields:
                if field not in monster or not monster[field]:
                    issues.append({
                        'type': 'missing_field',
                        'monster': monster_name,
                        'id': monster_id,
                        'field': field
                    })
            
            # Prüfe auf leere Learnset/Talents
            learnset = monster.get('learnset', [])
            talents = monster.get('talents', [])
            
            if not learnset and not talents:
                issues.append({
                    'type': 'no_moves',
                    'monster': monster_name,
                    'id': monster_id,
                    'message': 'Weder Learnset noch Talents vorhanden'
                })
            
            # Prüfe auf ungültige Learnset-Einträge
            for j, move_entry in enumerate(learnset):
                if isinstance(move_entry, dict):
                    if 'move' not in move_entry and 'name' not in move_entry:
                        issues.append({
                            'type': 'invalid_learnset_entry',
                            'monster': monster_name,
                            'id': monster_id,
                            'entry_index': j,
                            'message': 'Learnset-Eintrag ohne Move-Name'
                        })
            
            # Prüfe auf ungültige Talent-Einträge
            for j, talent in enumerate(talents):
                if isinstance(talent, dict):
                    if 'talent_id' not in talent and 'id' not in talent:
                        issues.append({
                            'type': 'invalid_talent_entry',
                            'monster': monster_name,
                            'id': monster_id,
                            'entry_index': j,
                            'message': 'Talent-Eintrag ohne Talent-ID'
                        })
        
        # Zeige gefundene Probleme
        if issues:
            print(f"⚠️  GEFUNDENE PROBLEME ({len(issues)}):")
            for issue in issues[:20]:  # Zeige nur erste 20
                print(f"  - {issue['type'].upper()}: {issue['monster']} (ID: {issue['id']})")
                if 'message' in issue:
                    print(f"    {issue['message']}")
            if len(issues) > 20:
                print(f"  ... und {len(issues) - 20} weitere")
        else:
            print("✅ Keine Probleme gefunden!")
        
        return issues
    
    def generate_report(self) -> str:
        """Generiere einen detaillierten Bericht"""
        report = []
        report.append("🎮 MONSTER JSON ANALYSE BERICHT")
        report.append("=" * 60)
        report.append(f"Datum: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Datei: {self.filepath}")
        report.append("")
        
        # Struktur-Analyse
        structure = self.analyze_structure()
        report.append("📋 DATENSTRUKTUR:")
        report.append(f"  Gesamt Monster: {structure.get('total_monsters', 0)}")
        report.append(f"  Verfügbare Felder: {', '.join(structure.get('sample_fields', []))}")
        report.append("")
        
        # Migrations-Status
        migration = self.analyze_migration_status()
        report.append("🎯 MIGRATIONS-STATUS:")
        report.append(f"  Migriert: {migration.get('migrated', 0)}")
        report.append(f"  Nicht migriert: {migration.get('not_migrated', 0)}")
        report.append(f"  Nur Learnset: {migration.get('learnset_only', 0)}")
        report.append(f"  Nur Talents: {migration.get('talents_only', 0)}")
        report.append("")
        
        # Learnset-Analyse
        learnset = self.analyze_learnsets()
        report.append("📚 LEARNSET ANALYSE:")
        report.append(f"  Monster mit Learnset: {learnset.get('total_learnsets', 0)}")
        report.append(f"  Gesamt Moves: {learnset.get('total_moves', 0)}")
        report.append("")
        
        # Talent-Analyse
        talents = self.analyze_talents()
        report.append("🎭 TALENT ANALYSE:")
        report.append(f"  Gesamt Talents: {talents.get('total_talents', 0)}")
        report.append(f"  Monster mit Talents: {len(talents.get('monster_talent_counts', []))}")
        report.append("")
        
        # Probleme
        issues = self.find_issues()
        report.append("🔍 PROBLEME:")
        report.append(f"  Gefundene Probleme: {len(issues)}")
        for issue in issues[:10]:
            report.append(f"  - {issue['type']}: {issue['monster']}")
        report.append("")
        
        return "\n".join(report)
    
    def run_full_analysis(self):
        """Führe eine vollständige Analyse durch"""
        print("🎮 MONSTER JSON ANALYSER")
        print("=" * 60)
        
        if not self.load_data():
            return
        
        # Führe alle Analysen durch
        self.analyze_structure()
        self.analyze_migration_status()
        self.analyze_learnsets()
        self.analyze_talents()
        self.find_issues()
        
        # Generiere Bericht
        report = self.generate_report()
        
        # Speichere Bericht
        with open('monster_analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 Detaillierter Bericht gespeichert: monster_analysis_report.txt")
        print("\n🎉 Analyse abgeschlossen!")

def main():
    """Hauptfunktion"""
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "data/monsters.json"
    
    analyzer = MonsterJSONAnalyzer(filepath)
    analyzer.run_full_analysis()

if __name__ == "__main__":
    main()
