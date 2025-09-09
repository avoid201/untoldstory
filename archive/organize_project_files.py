#!/usr/bin/env python3
"""
Organisiert alle Log-, Test- und Analyse-Dateien in separate Ordner
und benennt sie nach dem Änderungsdatum um für bessere Übersicht.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
import json

def get_file_modification_date(file_path):
    """Holt das Änderungsdatum einer Datei und formatiert es als String."""
    try:
        timestamp = os.path.getmtime(file_path)
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
    except OSError:
        return "unknown"

def create_directory_if_not_exists(dir_path):
    """Erstellt einen Ordner falls er nicht existiert."""
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    print(f"✓ Ordner erstellt: {dir_path}")

def organize_files():
    """Organisiert alle Dateien in die entsprechenden Ordner."""
    
    base_dir = Path("/Users/leon/Desktop/untold_story")
    
    # Definiere die Ordnerstruktur
    folders = {
        "logs": "Log- und Report-Dateien (.md)",
        "tests_standalone": "Standalone Test-Dateien (test_*.py)",
        "fixes_standalone": "Standalone Fix-Dateien (fix_*.py, *_fix.py)",
        "analysis": "Analyse-Ergebnisse (.json)",
        "scripts_utility": "Utility-Scripts (organize_*.py, cleanup_*.py, etc.)",
        "documentation": "Dokumentation und Guides"
    }
    
    # Erstelle alle Ordner
    for folder_name, description in folders.items():
        folder_path = base_dir / folder_name
        create_directory_if_not_exists(folder_path)
        print(f"  → {description}")
    
    print("\n" + "="*60)
    print("ORGANISIERE DATEIEN...")
    print("="*60)
    
    moved_files = 0
    
    # Organisiere .md Report-Dateien
    print("\n📋 ORGANISIERE REPORT-DATEIEN (.md):")
    md_files = list(base_dir.glob("*.md"))
    for file_path in md_files:
        if file_path.name in ["README.md"]:  # README.md im Root lassen
            continue
            
        date_str = get_file_modification_date(file_path)
        new_name = f"{file_path.stem}_{date_str}.md"
        new_path = base_dir / "logs" / new_name
        
        try:
            shutil.move(str(file_path), str(new_path))
            print(f"  ✓ {file_path.name} → logs/{new_name}")
            moved_files += 1
        except Exception as e:
            print(f"  ✗ Fehler bei {file_path.name}: {e}")
    
    # Organisiere Test-Dateien
    print("\n🧪 ORGANISIERE TEST-DATEIEN:")
    test_files = list(base_dir.glob("test_*.py"))
    for file_path in test_files:
        date_str = get_file_modification_date(file_path)
        new_name = f"{file_path.stem}_{date_str}.py"
        new_path = base_dir / "tests_standalone" / new_name
        
        try:
            shutil.move(str(file_path), str(new_path))
            print(f"  ✓ {file_path.name} → tests_standalone/{new_name}")
            moved_files += 1
        except Exception as e:
            print(f"  ✗ Fehler bei {file_path.name}: {e}")
    
    # Organisiere Fix-Dateien
    print("\n🔧 ORGANISIERE FIX-DATEIEN:")
    fix_patterns = ["fix_*.py", "*_fix.py", "cleanup_*.py", "refactor_*.py", 
                   "complete_*.py", "emergency_*.py", "quick_*.py", "final_*.py",
                   "validate_*.py", "verify_*.py", "conflict_*.py"]
    
    for pattern in fix_patterns:
        fix_files = list(base_dir.glob(pattern))
        for file_path in fix_files:
            date_str = get_file_modification_date(file_path)
            new_name = f"{file_path.stem}_{date_str}.py"
            new_path = base_dir / "fixes_standalone" / new_name
            
            try:
                shutil.move(str(file_path), str(new_path))
                print(f"  ✓ {file_path.name} → fixes_standalone/{new_name}")
                moved_files += 1
            except Exception as e:
                print(f"  ✗ Fehler bei {file_path.name}: {e}")
    
    # Organisiere JSON Analyse-Dateien
    print("\n📊 ORGANISIERE ANALYSE-DATEIEN (.json):")
    json_files = list(base_dir.glob("*.json"))
    for file_path in json_files:
        date_str = get_file_modification_date(file_path)
        new_name = f"{file_path.stem}_{date_str}.json"
        new_path = base_dir / "analysis" / new_name
        
        try:
            shutil.move(str(file_path), str(new_path))
            print(f"  ✓ {file_path.name} → analysis/{new_name}")
            moved_files += 1
        except Exception as e:
            print(f"  ✗ Fehler bei {file_path.name}: {e}")
    
    # Organisiere Utility-Scripts
    print("\n🛠️  ORGANISIERE UTILITY-SCRIPTS:")
    utility_patterns = ["organize_*.py", "cleanup_*.py", "project_*.py", 
                       "mastermap_*.py", "enhanced_*.py", "demo_*.py",
                       "install_*.py", "run_*.py", "start_*.py"]
    
    for pattern in utility_patterns:
        utility_files = list(base_dir.glob(pattern))
        for file_path in utility_files:
            if file_path.name == "organize_project_files.py":  # Dieses Script nicht verschieben
                continue
                
            date_str = get_file_modification_date(file_path)
            new_name = f"{file_path.stem}_{date_str}.py"
            new_path = base_dir / "scripts_utility" / new_name
            
            try:
                shutil.move(str(file_path), str(new_path))
                print(f"  ✓ {file_path.name} → scripts_utility/{new_name}")
                moved_files += 1
            except Exception as e:
                print(f"  ✗ Fehler bei {file_path.name}: {e}")
    
    # Organisiere Dokumentation
    print("\n📚 ORGANISIERE DOKUMENTATION:")
    doc_files = list(base_dir.glob("*.toml")) + list(base_dir.glob("*.txt"))
    for file_path in doc_files:
        if file_path.name in ["requirements.txt", "requirements-testing.txt", "settings.toml"]:
            continue  # Diese im Root lassen
            
        date_str = get_file_modification_date(file_path)
        new_name = f"{file_path.stem}_{date_str}{file_path.suffix}"
        new_path = base_dir / "documentation" / new_name
        
        try:
            shutil.move(str(file_path), str(new_path))
            print(f"  ✓ {file_path.name} → documentation/{new_name}")
            moved_files += 1
        except Exception as e:
            print(f"  ✗ Fehler bei {file_path.name}: {e}")
    
    print("\n" + "="*60)
    print(f"✅ ORGANISATION ABGESCHLOSSEN!")
    print(f"📁 {moved_files} Dateien wurden organisiert")
    print("="*60)
    
    # Erstelle eine Übersichtsdatei
    create_overview_file(base_dir, folders)

def create_overview_file(base_dir, folders):
    """Erstellt eine Übersichtsdatei mit der neuen Struktur."""
    overview_path = base_dir / "PROJEKT_ORGANISATION_ÜBERSICHT.md"
    
    with open(overview_path, 'w', encoding='utf-8') as f:
        f.write("# 📁 Projekt Organisation - Übersicht\n\n")
        f.write("Alle Log-, Test- und Analyse-Dateien wurden in separate Ordner organisiert.\n\n")
        f.write("## 📂 Ordnerstruktur\n\n")
        
        for folder_name, description in folders.items():
            folder_path = base_dir / folder_name
            if folder_path.exists():
                files = list(folder_path.glob("*"))
                f.write(f"### 📁 {folder_name}/\n")
                f.write(f"**Beschreibung:** {description}\n")
                f.write(f"**Anzahl Dateien:** {len(files)}\n\n")
                
                if files:
                    f.write("**Dateien:**\n")
                    for file in sorted(files):
                        f.write(f"- {file.name}\n")
                    f.write("\n")
        
        f.write("## 📝 Hinweise\n\n")
        f.write("- Alle Dateien wurden nach dem Änderungsdatum benannt (YYYY-MM-DD)\n")
        f.write("- Wichtige Dateien wie README.md, requirements.txt und settings.toml blieben im Root\n")
        f.write("- Die bestehende tests/ Ordnerstruktur wurde beibehalten\n")
        f.write("- Logs/ Ordner war bereits vorhanden und wurde erweitert\n\n")
        f.write(f"**Organisiert am:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

if __name__ == "__main__":
    print("🚀 STARTE PROJEKT-ORGANISATION...")
    print("="*60)
    
    try:
        organize_files()
        print("\n🎉 Alle Dateien wurden erfolgreich organisiert!")
        print("📋 Siehe 'PROJEKT_ORGANISATION_ÜBERSICHT.md' für Details")
        
    except Exception as e:
        print(f"\n❌ Fehler bei der Organisation: {e}")
        import traceback
        traceback.print_exc()
