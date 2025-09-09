#!/usr/bin/env python3
"""
🧹 Untold Story - Automatisches Projekt-Aufräum-Script
Organisiert und räumt die Projektstruktur auf.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import json

# ANSI Color codes für schöne Ausgabe
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")

def print_section(text):
    print(f"\n{Colors.CYAN}▶ {text}{Colors.ENDC}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

class ProjectOrganizer:
    def __init__(self, project_root):
        self.root = Path(project_root)
        self.moved_files = []
        self.errors = []
        
        # Definiere Ziel-Struktur
        self.structure = {
            'docs/reports': [],
            'docs/guides': [],
            'docs/architecture': [],
            'tests/unit': [],
            'tests/integration': [],
            'tests/performance': [],
            'scripts/fixes': [],
            'scripts/cleanup': [],
            'scripts/debug': [],
            'scripts/startup': [],
            'tools/generators': [],
            'tools/analyzers': [],
            'tools/migration': [],
            'archive/legacy_reports': [],
            'archive/old_tests': [],
            'archive/deprecated': [],
        }
        
        # File-Mapping Regeln
        self.file_mappings = {
            # Reports -> docs/reports/
            'BATTLESCENE_*.md': 'docs/reports',
            'BATTLE_SYSTEM_*.md': 'docs/reports',
            'CLEANUP_*.md': 'docs/reports',
            '*_REPORT.md': 'docs/reports',
            '*_SUCCESS.md': 'docs/reports',
            '*_ANALYSE*.md': 'docs/reports',
            'MASTERMAP_*.md': 'docs/reports',
            'IMPLEMENTATION_*.md': 'docs/reports',
            'PHASE*_*.md': 'docs/reports',
            '*_ABGESCHLOSSEN.md': 'docs/reports',
            'VOLLSTAENDIGKEITS*.md': 'docs/reports',
            
            # Tests -> tests/
            'test_battle*.py': 'tests/integration',
            'test_*.py': 'tests/integration',
            'demo_*.py': 'tests/integration',
            'quick_test*.py': 'tests/integration',
            'test_performance*.py': 'tests/performance',
            
            # Fix Scripts -> scripts/fixes/
            'fix_*.py': 'scripts/fixes',
            '*_fix.py': 'scripts/fixes',
            '*_fixer.py': 'scripts/fixes',
            'cleanup_*.py': 'scripts/cleanup',
            'clean_*.py': 'scripts/cleanup',
            'refactor_*.py': 'scripts/fixes',
            'simplify_*.py': 'scripts/fixes',
            'complete_*.py': 'scripts/fixes',
            'auto_fix.py': 'scripts/fixes',
            'conflict_*.py': 'scripts/fixes',
            'final_*.py': 'scripts/fixes',
            
            # Startup Scripts -> scripts/startup/
            'run_*.py': 'scripts/startup',
            'start_*.py': 'scripts/startup',
            'local_*.py': 'scripts/startup',
            'simple_test.py': 'scripts/startup',
            '*.sh': 'scripts/startup',
            
            # Tools -> tools/
            'mastermap_generator.py': 'tools/generators',
            'enhanced_mastermap_generator.py': 'tools/generators',
            'validate_*.py': 'tools/migration',
            'verify_*.py': 'tools/migration',
            'code_analysis.json': 'tools/analyzers',
            
            # Documentation
            'PROMPT_*.md': 'archive/deprecated',
            'untold-story-battle-system.md': 'archive/deprecated',
            'code_analysis_report.md': 'archive/deprecated',
            
            # Special handling
            'install_dependencies.py': 'scripts/startup',
        }
    
    def create_directory_structure(self):
        """Erstelle die neue Ordner-Struktur."""
        print_section("Erstelle neue Ordner-Struktur...")
        
        for dir_path in self.structure.keys():
            full_path = self.root / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                print_success(f"Erstellt: {dir_path}/")
    
    def backup_project(self):
        """Erstelle ein Backup des gesamten Projekts."""
        print_section("Erstelle Backup...")
        
        backup_name = f"untold_story_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.root.parent / backup_name
        
        try:
            # Kopiere nur wichtige Dateien (ohne .git, .venv, __pycache__)
            shutil.copytree(
                self.root,
                backup_path,
                ignore=shutil.ignore_patterns('.git', '.venv', '__pycache__', '*.pyc', '.DS_Store')
            )
            print_success(f"Backup erstellt: {backup_path}")
            return True
        except Exception as e:
            print_error(f"Backup fehlgeschlagen: {e}")
            return False
    
    def clean_pycache_and_ds_store(self):
        """Entferne alle __pycache__ und .DS_Store Dateien."""
        print_section("Räume Cache-Dateien auf...")
        
        # Finde und lösche __pycache__
        pycache_dirs = list(self.root.rglob('__pycache__'))
        for pycache in pycache_dirs:
            try:
                shutil.rmtree(pycache)
                print_success(f"Gelöscht: {pycache.relative_to(self.root)}")
            except Exception as e:
                print_warning(f"Konnte nicht löschen: {pycache}")
        
        # Finde und lösche .DS_Store
        ds_store_files = list(self.root.rglob('.DS_Store'))
        for ds_store in ds_store_files:
            try:
                ds_store.unlink()
                print_success(f"Gelöscht: {ds_store.relative_to(self.root)}")
            except Exception as e:
                print_warning(f"Konnte nicht löschen: {ds_store}")
    
    def move_file(self, source, destination):
        """Verschiebe eine Datei in den Zielordner."""
        source_path = Path(source)
        dest_dir = self.root / destination
        dest_path = dest_dir / source_path.name
        
        # Skip wenn Datei schon am richtigen Ort
        if source_path.parent == dest_dir:
            return False
        
        try:
            # Erstelle Zielordner falls nicht vorhanden
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Verschiebe Datei
            shutil.move(str(source_path), str(dest_path))
            
            # Log
            self.moved_files.append({
                'from': str(source_path.relative_to(self.root)),
                'to': str(dest_path.relative_to(self.root))
            })
            
            print_success(f"Verschoben: {source_path.name} → {destination}/")
            return True
            
        except Exception as e:
            self.errors.append(f"Fehler beim Verschieben von {source_path.name}: {e}")
            print_error(f"Fehler: {source_path.name} - {e}")
            return False
    
    def organize_files(self):
        """Organisiere alle Dateien nach den definierten Regeln."""
        print_section("Organisiere Dateien...")
        
        # Sammle alle Dateien im Root
        root_files = [f for f in self.root.iterdir() if f.is_file()]
        
        moved_count = 0
        for file_path in root_files:
            file_name = file_path.name
            
            # Skip wichtige Root-Dateien
            if file_name in ['README.md', 'requirements.txt', 'requirements-testing.txt', 
                           'settings.toml', 'main.py', '.cursorrules', '.gitignore']:
                continue
            
            # Finde passendes Ziel
            moved = False
            for pattern, destination in self.file_mappings.items():
                # Simple Pattern Matching
                if '*' in pattern:
                    # Wildcard matching
                    pattern_parts = pattern.replace('*', '')
                    if pattern.startswith('*') and pattern.endswith('*'):
                        # *text* - enthält
                        if pattern_parts in file_name:
                            if self.move_file(file_path, destination):
                                moved_count += 1
                                moved = True
                                break
                    elif pattern.startswith('*'):
                        # *suffix - endet mit
                        if file_name.endswith(pattern_parts):
                            if self.move_file(file_path, destination):
                                moved_count += 1
                                moved = True
                                break
                    elif pattern.endswith('*'):
                        # prefix* - beginnt mit
                        if file_name.startswith(pattern_parts):
                            if self.move_file(file_path, destination):
                                moved_count += 1
                                moved = True
                                break
                else:
                    # Exakter Match
                    if file_name == pattern:
                        if self.move_file(file_path, destination):
                            moved_count += 1
                            moved = True
                            break
            
            # Wenn nicht verschoben und ist Python/MD Datei -> Archive
            if not moved and file_path.suffix in ['.py', '.md']:
                if file_name != 'CLEANUP_ARCHITECTURE_PLAN.md':
                    print_warning(f"Unbekannte Datei: {file_name} → archive/")
                    if self.move_file(file_path, 'archive/deprecated'):
                        moved_count += 1
        
        print_success(f"✓ {moved_count} Dateien organisiert")
    
    def create_readme_files(self):
        """Erstelle README.md Dateien für wichtige Ordner."""
        print_section("Erstelle Dokumentation...")
        
        readme_contents = {
            'docs/README.md': """# 📚 Dokumentation

## Ordner-Struktur
- `reports/` - Entwicklungs-Reports und Analysen
- `guides/` - Entwickler-Guides und Tutorials
- `architecture/` - Architektur-Dokumentation
""",
            'tests/README.md': """# 🧪 Tests

## Test-Kategorien
- `unit/` - Unit-Tests für einzelne Komponenten
- `integration/` - Integration-Tests für Systeme
- `performance/` - Performance- und Benchmark-Tests

## Tests ausführen
```bash
pytest tests/
```
""",
            'scripts/README.md': """# 📜 Scripts

## Kategorien
- `fixes/` - Bug-Fix und Patch Scripts
- `cleanup/` - Code-Cleanup und Refactoring
- `debug/` - Debug und Analyse Scripts
- `startup/` - Start und Run Scripts
""",
            'tools/README.md': """# 🔧 Development Tools

## Tool-Kategorien
- `generators/` - Code- und Asset-Generatoren
- `analyzers/` - Code-Analyse Tools
- `migration/` - Migrations- und Update-Tools
""",
        }
        
        for path, content in readme_contents.items():
            readme_path = self.root / path
            readme_path.parent.mkdir(parents=True, exist_ok=True)
            readme_path.write_text(content)
            print_success(f"Erstellt: {path}")
    
    def generate_report(self):
        """Generiere einen Aufräum-Report."""
        print_section("Generiere Report...")
        
        report = f"""# 🧹 Aufräum-Report
Generiert: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Statistiken
- Dateien verschoben: {len(self.moved_files)}
- Fehler: {len(self.errors)}

## 📁 Verschobene Dateien
"""
        
        # Gruppiere nach Zielordner
        moves_by_dest = {}
        for move in self.moved_files:
            dest = move['to'].rsplit('/', 1)[0]
            if dest not in moves_by_dest:
                moves_by_dest[dest] = []
            moves_by_dest[dest].append(move['from'])
        
        for dest, files in sorted(moves_by_dest.items()):
            report += f"\n### {dest}/\n"
            for file in sorted(files):
                report += f"- {file}\n"
        
        if self.errors:
            report += "\n## ⚠️ Fehler\n"
            for error in self.errors:
                report += f"- {error}\n"
        
        # Speichere Report
        report_path = self.root / 'CLEANUP_EXECUTION_REPORT.md'
        report_path.write_text(report)
        print_success(f"Report gespeichert: CLEANUP_EXECUTION_REPORT.md")
        
        # Speichere auch als JSON für spätere Verwendung
        json_report = {
            'timestamp': datetime.now().isoformat(),
            'moved_files': self.moved_files,
            'errors': self.errors
        }
        json_path = self.root / 'cleanup_log.json'
        with open(json_path, 'w') as f:
            json.dump(json_report, f, indent=2)
    
    def run(self, create_backup=True):
        """Führe die komplette Aufräum-Aktion durch."""
        print_header("UNTOLD STORY - PROJEKT AUFRÄUMEN")
        
        # Schritt 1: Backup
        if create_backup:
            if not self.backup_project():
                response = input("\n⚠️  Backup fehlgeschlagen. Trotzdem fortfahren? (j/N): ")
                if response.lower() != 'j':
                    print("Abgebrochen.")
                    return
        
        # Schritt 2: Cache aufräumen
        self.clean_pycache_and_ds_store()
        
        # Schritt 3: Ordner-Struktur erstellen
        self.create_directory_structure()
        
        # Schritt 4: Dateien organisieren
        self.organize_files()
        
        # Schritt 5: README-Dateien erstellen
        self.create_readme_files()
        
        # Schritt 6: Report generieren
        self.generate_report()
        
        print_header("AUFRÄUMEN ABGESCHLOSSEN")
        print(f"\n{Colors.GREEN}✓ Projekt erfolgreich aufgeräumt!{Colors.ENDC}")
        print(f"  - {len(self.moved_files)} Dateien verschoben")
        print(f"  - {len(self.errors)} Fehler")
        print(f"\nDetails siehe: CLEANUP_EXECUTION_REPORT.md")


def main():
    """Hauptfunktion."""
    import sys
    
    # Projekt-Root ermitteln
    project_root = Path(__file__).parent
    
    print(f"Projekt-Root: {project_root}")
    print(f"\n{Colors.WARNING}⚠️  WARNUNG: Dieses Script wird viele Dateien verschieben!{Colors.ENDC}")
    print("Es wird automatisch ein Backup erstellt.\n")
    
    response = input("Möchten Sie fortfahren? (j/N): ")
    if response.lower() != 'j':
        print("Abgebrochen.")
        sys.exit(0)
    
    # Erstelle Organizer und führe aus
    organizer = ProjectOrganizer(project_root)
    organizer.run(create_backup=True)


if __name__ == "__main__":
    main()
