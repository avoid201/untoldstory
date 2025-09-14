#!/usr/bin/env python3
"""
Project Cleanup Script für Untold Story
- Archiviert Test-Dateien
- Entfernt Placeholder
- Bereinigt Legacy Code
"""

import os
import shutil
import re
from pathlib import Path
from datetime import datetime
import ast

# Projekt-Root
PROJECT_ROOT = Path(__file__).parent
ARCHIVE_DIR = PROJECT_ROOT / "archive"
ENGINE_DIR = PROJECT_ROOT / "engine"

# Archive subdirs
ARCHIVE_TEST = ARCHIVE_DIR / "test_files"
ARCHIVE_OLD_BATTLE = ARCHIVE_DIR / "old_battle"
ARCHIVE_LEGACY = ARCHIVE_DIR / "legacy_code"
ARCHIVE_BACKUPS = ARCHIVE_DIR / "backups"

# Erstelle Archive-Verzeichnisse
for dir in [ARCHIVE_TEST, ARCHIVE_OLD_BATTLE, ARCHIVE_LEGACY, ARCHIVE_BACKUPS]:
    dir.mkdir(parents=True, exist_ok=True)

def find_placeholder_methods(filepath):
    """Findet Placeholder-Methoden mit pass, TODO, oder NotImplemented."""
    placeholders = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content)
            
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check für placeholder patterns
                has_pass_only = False
                has_todo = False
                has_not_implemented = False
                
                # Prüfe Funktionskörper
                if len(node.body) == 1:
                    if isinstance(node.body[0], ast.Pass):
                        has_pass_only = True
                    elif isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if 'TODO' in str(node.body[0].value.value):
                                has_todo = True
                    elif isinstance(node.body[0], ast.Raise):
                        # Check for NotImplementedError
                        if hasattr(node.body[0].exc, 'func'):
                            if hasattr(node.body[0].exc.func, 'id'):
                                if 'NotImplemented' in node.body[0].exc.func.id:
                                    has_not_implemented = True
                
                if has_pass_only or has_todo or has_not_implemented:
                    placeholders.append({
                        'name': node.name,
                        'line': node.lineno,
                        'type': 'pass' if has_pass_only else 'todo' if has_todo else 'not_implemented'
                    })
                    
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
    
    return placeholders

def find_legacy_code(filepath):
    """Findet Legacy-Code mit LEGACY, DEPRECATED, OLD_ prefixes."""
    legacy_patterns = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines, 1):
            # Check for legacy markers
            if any(marker in line.upper() for marker in ['LEGACY', 'DEPRECATED', 'OLD_', 'UNUSED', 'OBSOLETE']):
                legacy_patterns.append({
                    'line': i,
                    'content': line.strip()[:100]  # First 100 chars
                })
                
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    
    return legacy_patterns

def archive_file(filepath, archive_subdir):
    """Verschiebt Datei ins Archiv mit Timestamp."""
    source = Path(filepath)
    if not source.exists():
        return False
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = archive_subdir / f"{source.stem}_{timestamp}{source.suffix}"
    
    try:
        shutil.move(str(source), str(dest))
        print(f"✓ Archiviert: {source.name} → {dest.relative_to(PROJECT_ROOT)}")
        return True
    except Exception as e:
        print(f"✗ Fehler beim Archivieren von {source.name}: {e}")
        return False

def cleanup_root_test_files():
    """Archiviert Test-Dateien aus dem Root-Verzeichnis."""
    test_files = [
        'battle_ui_critical_fixes.py',
        'clean_battle_scene.py',
        'comprehensive_fixer.py',
        'local_test.py',
        'simple_test.py',
        'simplify_battle.py',
        'test_battle_quick.py',
        'test_battle_system.py',
        'test_debug_battle.py',
        'test_debug_simple.py',
        'test_dqm_integration.py',
        'validatetest.py'
    ]
    
    print("\n📁 Archiviere Root-Test-Dateien...")
    archived = 0
    for file in test_files:
        filepath = PROJECT_ROOT / file
        if archive_file(filepath, ARCHIVE_TEST):
            archived += 1
    
    print(f"→ {archived}/{len(test_files)} Dateien archiviert")
    return archived

def cleanup_backup_files():
    """Archiviert alle .backup Dateien."""
    print("\n📁 Archiviere Backup-Dateien...")
    archived = 0
    
    for backup_file in PROJECT_ROOT.rglob("*.backup"):
        if archive_file(backup_file, ARCHIVE_BACKUPS):
            archived += 1
            
    print(f"→ {archived} Backup-Dateien archiviert")
    return archived

def find_duplicate_scenes():
    """Findet duplizierte Scene-Dateien."""
    scenes_dir = ENGINE_DIR / "scenes"
    duplicates = []
    
    # Bekannte Duplikate
    known_duplicates = [
        ('battle_scene.py', 'battle_scene_optimized.py'),
    ]
    
    for original, duplicate in known_duplicates:
        orig_path = scenes_dir / original
        dup_path = scenes_dir / duplicate
        
        if orig_path.exists() and dup_path.exists():
            duplicates.append(dup_path)
            
    return duplicates

def analyze_battle_system():
    """Analysiert das Battle System für Bereinigung."""
    battle_dir = ENGINE_DIR / "systems" / "battle"
    
    print("\n📊 Analysiere Battle System...")
    
    analysis = {
        'total_files': 0,
        'placeholders': {},
        'legacy': {},
        'file_sizes': {}
    }
    
    for py_file in battle_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
            
        analysis['total_files'] += 1
        
        # Dateigröße
        size = py_file.stat().st_size
        analysis['file_sizes'][py_file.name] = size
        
        # Placeholder-Methoden
        placeholders = find_placeholder_methods(py_file)
        if placeholders:
            analysis['placeholders'][py_file.name] = placeholders
            
        # Legacy Code
        legacy = find_legacy_code(py_file)
        if legacy:
            analysis['legacy'][py_file.name] = legacy
    
    # Report
    print(f"\n📈 Battle System Analyse:")
    print(f"  Dateien: {analysis['total_files']}")
    print(f"  Mit Placeholders: {len(analysis['placeholders'])}")
    print(f"  Mit Legacy Code: {len(analysis['legacy'])}")
    
    if analysis['placeholders']:
        print("\n⚠️ Placeholder-Methoden gefunden:")
        for file, methods in analysis['placeholders'].items():
            print(f"  {file}:")
            for method in methods[:3]:  # Zeige max 3
                print(f"    - {method['name']} (Line {method['line']}, Type: {method['type']})")
                
    if analysis['legacy']:
        print("\n⚠️ Legacy Code gefunden:")
        for file, patterns in analysis['legacy'].items():
            print(f"  {file}:")
            for pattern in patterns[:3]:  # Zeige max 3
                print(f"    - Line {pattern['line']}: {pattern['content'][:50]}...")
    
    return analysis

def generate_cleanup_report():
    """Erstellt einen detaillierten Cleanup-Report."""
    report = []
    report.append("# 🧹 UNTOLD STORY - CLEANUP REPORT\n")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # Root Test Files
    test_count = cleanup_root_test_files()
    report.append(f"## Root Test Files\n")
    report.append(f"✓ {test_count} Test-Dateien archiviert\n\n")
    
    # Backup Files
    backup_count = cleanup_backup_files()
    report.append(f"## Backup Files\n")
    report.append(f"✓ {backup_count} Backup-Dateien archiviert\n\n")
    
    # Duplicate Scenes
    duplicates = find_duplicate_scenes()
    if duplicates:
        report.append(f"## Duplicate Scenes\n")
        for dup in duplicates:
            report.append(f"- {dup.relative_to(PROJECT_ROOT)}\n")
        report.append("\n")
    
    # Battle System Analysis
    battle_analysis = analyze_battle_system()
    report.append(f"## Battle System Analysis\n")
    report.append(f"- Total Files: {battle_analysis['total_files']}\n")
    report.append(f"- Files with Placeholders: {len(battle_analysis['placeholders'])}\n")
    report.append(f"- Files with Legacy Code: {len(battle_analysis['legacy'])}\n\n")
    
    # Empfehlungen
    report.append("## 🎯 Empfehlungen\n\n")
    
    if duplicates:
        report.append("### Duplikate entfernen:\n")
        for dup in duplicates:
            report.append(f"- Archiviere: {dup.name}\n")
        report.append("\n")
        
    if battle_analysis['placeholders']:
        report.append("### Placeholder ersetzen in:\n")
        for file in list(battle_analysis['placeholders'].keys())[:5]:
            report.append(f"- {file}\n")
        report.append("\n")
        
    if battle_analysis['legacy']:
        report.append("### Legacy Code bereinigen in:\n")
        for file in list(battle_analysis['legacy'].keys())[:5]:
            report.append(f"- {file}\n")
        report.append("\n")
    
    # Report speichern
    report_path = PROJECT_ROOT / "CLEANUP_REPORT.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.writelines(report)
    
    print(f"\n📄 Report gespeichert: {report_path}")
    
    return report

if __name__ == "__main__":
    print("=" * 60)
    print("🧹 UNTOLD STORY - PROJECT CLEANUP")
    print("=" * 60)
    
    # Führe Cleanup durch
    generate_cleanup_report()
    
    print("\n✅ Cleanup abgeschlossen!")
    print("\n⚡ Nächste Schritte:")
    print("1. Prüfe CLEANUP_REPORT.md für Details")
    print("2. Entscheide über Duplikate")
    print("3. Ersetze Placeholder-Methoden")
    print("4. Entferne Legacy-Code")
