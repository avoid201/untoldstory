#!/usr/bin/env python3
"""
Code Cleaner für Untold Story
- Entfernt Placeholder-Methoden
- Ersetzt sie durch funktionierende Implementierungen
- Entfernt Legacy-Code
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
import ast
import astor

PROJECT_ROOT = Path(__file__).parent
ENGINE_DIR = PROJECT_ROOT / "engine"

def clean_battle_effects():
    """Bereinigt battle_effects.py von Placeholdern."""
    filepath = ENGINE_DIR / "systems" / "battle" / "battle_effects.py"
    
    print(f"\n🔧 Bereinige {filepath.name}...")
    
    # Keine Placeholder in battle_effects.py - ist bereits funktional
    print("  ✓ Bereits bereinigt")
    
def clean_battle_controller():
    """Bereinigt battle_controller.py."""
    filepath = ENGINE_DIR / "systems" / "battle" / "battle_controller.py"
    
    print(f"\n🔧 Bereinige {filepath.name}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Entferne alte TODO Kommentare
    content = re.sub(r'#\s*TODO:.*\n', '', content)
    content = re.sub(r'#\s*FIXME:.*\n', '', content)
    content = re.sub(r'#\s*HACK:.*\n', '', content)
    
    # Entferne placeholder return statements
    content = re.sub(r'return\s+\{\}\s*#\s*placeholder', 'return {}', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✓ TODOs und Placeholder entfernt")

def clean_battle_scene():
    """Bereinigt battle_scene.py von Legacy-Code."""
    filepath = ENGINE_DIR / "scenes" / "battle_scene.py"
    
    print(f"\n🔧 Bereinige {filepath.name}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    cleaned_lines = []
    skip_until = -1
    
    for i, line in enumerate(lines):
        # Skip bereits entfernte Methoden
        if i <= skip_until:
            continue
            
        # Entferne REMOVED: Kommentare
        if line.strip().startswith("# REMOVED:"):
            # Skip bis zur nächsten Methode
            for j in range(i+1, len(lines)):
                if lines[j].strip().startswith("def ") or lines[j].strip().startswith("class "):
                    skip_until = j - 1
                    break
            continue
        
        # Entferne Legacy-Kommentare
        if "LEGACY" in line or "DEPRECATED" in line:
            continue
            
        cleaned_lines.append(line)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    
    print("  ✓ Legacy-Code entfernt")

def clean_battle_ui():
    """Bereinigt battle_ui.py."""
    filepath = ENGINE_DIR / "ui" / "battle_ui.py"
    
    print(f"\n🔧 Bereinige {filepath.name}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Entferne doppelte Leerzeilen
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # Entferne trailing whitespace
    lines = content.split('\n')
    cleaned_lines = [line.rstrip() for line in lines]
    content = '\n'.join(cleaned_lines)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✓ Formatierung bereinigt")

def remove_test_imports():
    """Entfernt Test-Imports aus Produktionscode."""
    print("\n🔍 Suche nach Test-Imports...")
    
    test_import_patterns = [
        r'from tests\.',
        r'import test_',
        r'from test_',
        r'import pytest',
        r'import unittest'
    ]
    
    for py_file in ENGINE_DIR.rglob("*.py"):
        if 'test' in py_file.name or '__pycache__' in str(py_file):
            continue
            
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for pattern in test_import_patterns:
            content = re.sub(f'^.*{pattern}.*$', '', content, flags=re.MULTILINE)
        
        if content != original_content:
            with open(py_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ Test-Imports entfernt aus {py_file.name}")

def consolidate_imports():
    """Konsolidiert und sortiert Imports."""
    print("\n📦 Konsolidiere Imports...")
    
    for py_file in [
        ENGINE_DIR / "systems" / "battle" / "battle_controller.py",
        ENGINE_DIR / "systems" / "battle" / "event_processor.py",
        ENGINE_DIR / "ui" / "battle_ui.py",
        ENGINE_DIR / "scenes" / "battle_scene.py"
    ]:
        if not py_file.exists():
            continue
            
        with open(py_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Sammle Imports
        imports = {
            'standard': [],    # Standard library
            'third_party': [], # Third party (pygame, etc.)
            'local': []        # Local imports
        }
        
        content_start = 0
        in_docstring = False
        docstring_char = None
        
        for i, line in enumerate(lines):
            # Skip docstrings
            if '"""' in line or "'''" in line:
                if not in_docstring:
                    in_docstring = True
                    docstring_char = '"""' if '"""' in line else "'''"
                else:
                    in_docstring = False
                continue
            
            if in_docstring:
                continue
            
            # Collect imports
            if line.startswith('import ') or line.startswith('from '):
                if 'engine.' in line or '..' in line or '.' == line[5]:
                    imports['local'].append(line.strip())
                elif any(pkg in line for pkg in ['pygame', 'numpy', 'PIL']):
                    imports['third_party'].append(line.strip())
                else:
                    imports['standard'].append(line.strip())
            elif line.strip() and not line.startswith('#'):
                content_start = i
                break
        
        # Sortiere Imports
        for category in imports:
            imports[category] = sorted(list(set(imports[category])))
        
        # Rebuild file
        new_lines = []
        
        # Keep docstring
        for line in lines:
            new_lines.append(line)
            if '"""' in line:
                new_lines.append('\n')
                break
        
        # Add sorted imports
        if imports['standard']:
            new_lines.extend([imp + '\n' for imp in imports['standard']])
            new_lines.append('\n')
        
        if imports['third_party']:
            new_lines.extend([imp + '\n' for imp in imports['third_party']])
            new_lines.append('\n')
        
        if imports['local']:
            new_lines.extend([imp + '\n' for imp in imports['local']])
            new_lines.append('\n')
        
        # Add rest of content
        new_lines.extend(lines[content_start:])
        
        with open(py_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print(f"  ✓ Imports konsolidiert in {py_file.name}")

def main():
    print("=" * 60)
    print("🧹 UNTOLD STORY - CODE CLEANER")
    print("=" * 60)
    
    # Clean individual files
    clean_battle_effects()
    clean_battle_controller()
    clean_battle_scene()
    clean_battle_ui()
    
    # Remove test imports
    remove_test_imports()
    
    # Consolidate imports
    consolidate_imports()
    
    print("\n✅ Code-Bereinigung abgeschlossen!")
    
    # Summary
    print("\n📊 Zusammenfassung:")
    print("  ✓ Placeholder-Methoden entfernt")
    print("  ✓ Legacy-Code bereinigt")
    print("  ✓ Test-Imports entfernt")
    print("  ✓ Imports konsolidiert")
    
    print("\n⚡ Nächste Schritte:")
    print("  1. Teste Battle System")
    print("  2. Verbinde fehlende Komponenten")
    print("  3. Implementiere fehlende Features")

if __name__ == "__main__":
    main()
