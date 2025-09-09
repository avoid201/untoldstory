#!/usr/bin/env python3
"""
UNTOLD STORY - ELITE CONFLICT RESOLVER
=======================================
Löst AI-generierte Konflikte im Kampfsystem und erstellt Agent-Prompts für Cursor.

Author: Elite Game Designer & Pro Prompt Engineer
"""

import os
import ast
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import re
from collections import defaultdict

# ================================
# KONFLIKT-ANALYSE ENGINE
# ================================

class ConflictType(Enum):
    """Typen von Code-Konflikten."""
    DUPLICATE_CLASS = "duplicate_class"
    DUPLICATE_FUNCTION = "duplicate_function"
    IMPORT_CONFLICT = "import_conflict"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    MISSING_DEPENDENCY = "missing_dependency"
    TYPE_MISMATCH = "type_mismatch"
    INCONSISTENT_STATE = "inconsistent_state"
    DEPRECATED_CODE = "deprecated_code"
    REDUNDANT_CODE = "redundant_code"
    BROKEN_REFERENCE = "broken_reference"

@dataclass
class CodeConflict:
    """Repräsentiert einen Code-Konflikt."""
    type: ConflictType
    file_path: str
    line_number: int
    description: str
    severity: str  # "critical", "high", "medium", "low"
    ai_generated: bool = True
    suggested_fix: str = ""
    related_files: List[str] = field(default_factory=list)

@dataclass
class BattleSystemAnalysis:
    """Analyse-Ergebnis des Kampfsystems."""
    conflicts: List[CodeConflict]
    dependencies: Dict[str, List[str]]
    duplicates: Dict[str, List[Tuple[str, int]]]
    unused_code: List[Tuple[str, str]]
    performance_issues: List[Dict[str, Any]]
    architecture_problems: List[str]

class BattleSystemAnalyzer:
    """Analysiert das Kampfsystem auf Konflikte und Probleme."""
    
    def __init__(self, project_root: str = "/Users/leon/Desktop/untold_story"):
        self.project_root = Path(project_root)
        self.battle_path = self.project_root / "engine" / "systems" / "battle"
        self.conflicts: List[CodeConflict] = []
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.class_definitions: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        self.function_definitions: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        self.imports: Dict[str, Set[str]] = defaultdict(set)
        
    def analyze(self) -> BattleSystemAnalysis:
        """Führt vollständige Analyse durch."""
        print("🔍 Starte Kampfsystem-Analyse...")
        
        # Phase 1: Sammle alle Definitionen
        self._collect_definitions()
        
        # Phase 2: Finde Konflikte
        self._find_duplicate_classes()
        self._find_duplicate_functions()
        self._find_import_conflicts()
        self._find_circular_dependencies()
        self._find_missing_dependencies()
        self._find_state_inconsistencies()
        self._find_deprecated_code()
        
        # Phase 3: Performance-Analyse
        performance_issues = self._analyze_performance()
        
        # Phase 4: Architektur-Analyse
        architecture_problems = self._analyze_architecture()
        
        return BattleSystemAnalysis(
            conflicts=self.conflicts,
            dependencies=dict(self.dependencies),
            duplicates=self._get_duplicates(),
            unused_code=self._find_unused_code(),
            performance_issues=performance_issues,
            architecture_problems=architecture_problems
        )
    
    def _collect_definitions(self):
        """Sammelt alle Klassen- und Funktionsdefinitionen."""
        for py_file in self.battle_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content, filename=str(py_file))
                    
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        self.class_definitions[node.name].append(
                            (str(py_file), node.lineno)
                        )
                    elif isinstance(node, ast.FunctionDef):
                        self.function_definitions[node.name].append(
                            (str(py_file), node.lineno)
                        )
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            self.imports[str(py_file)].add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self.imports[str(py_file)].add(node.module)
                            
            except Exception as e:
                print(f"⚠️  Fehler beim Parsen von {py_file}: {e}")
    
    def _find_duplicate_classes(self):
        """Findet duplizierte Klassendefinitionen."""
        for class_name, locations in self.class_definitions.items():
            if len(locations) > 1:
                self.conflicts.append(CodeConflict(
                    type=ConflictType.DUPLICATE_CLASS,
                    file_path=locations[0][0],
                    line_number=locations[0][1],
                    description=f"Klasse '{class_name}' ist {len(locations)}x definiert",
                    severity="critical",
                    suggested_fix=f"Verwende nur eine Definition von {class_name}",
                    related_files=[loc[0] for loc in locations]
                ))
    
    def _find_duplicate_functions(self):
        """Findet duplizierte Funktionsdefinitionen."""
        # Gruppiere nach Datei
        file_functions = defaultdict(list)
        for func_name, locations in self.function_definitions.items():
            for file_path, line_no in locations:
                file_functions[file_path].append((func_name, line_no))
        
        # Finde Duplikate innerhalb derselben Datei
        for file_path, functions in file_functions.items():
            func_counts = defaultdict(list)
            for func_name, line_no in functions:
                func_counts[func_name].append(line_no)
            
            for func_name, lines in func_counts.items():
                if len(lines) > 1:
                    self.conflicts.append(CodeConflict(
                        type=ConflictType.DUPLICATE_FUNCTION,
                        file_path=file_path,
                        line_number=lines[0],
                        description=f"Funktion '{func_name}' ist {len(lines)}x in derselben Datei",
                        severity="high",
                        suggested_fix=f"Entferne duplizierte Definitionen von {func_name}"
                    ))
    
    def _find_import_conflicts(self):
        """Findet Import-Konflikte."""
        # Prüfe battle.py vs battle_system.py
        battle_file = self.battle_path / "battle.py"
        battle_system_file = self.battle_path / "battle_system.py"
        
        if battle_file.exists() and battle_system_file.exists():
            # Diese beiden definieren ähnliche Klassen
            self.conflicts.append(CodeConflict(
                type=ConflictType.IMPORT_CONFLICT,
                file_path=str(battle_file),
                line_number=1,
                description="battle.py und battle_system.py definieren überlappende Funktionalität",
                severity="critical",
                suggested_fix="Verwende battle_system.py als Haupt-Modul, battle.py als Legacy-Wrapper",
                related_files=[str(battle_system_file)]
            ))
    
    def _find_circular_dependencies(self):
        """Findet zirkuläre Abhängigkeiten."""
        # Vereinfachte Analyse
        for file_path, imports in self.imports.items():
            for imported in imports:
                if "battle" in imported and "battle" in file_path:
                    # Potenzielle zirkuläre Abhängigkeit
                    if imported in str(file_path):
                        self.conflicts.append(CodeConflict(
                            type=ConflictType.CIRCULAR_DEPENDENCY,
                            file_path=file_path,
                            line_number=1,
                            description=f"Mögliche zirkuläre Abhängigkeit: {Path(file_path).name} -> {imported}",
                            severity="medium",
                            suggested_fix="Refaktoriere Imports oder verwende lazy imports"
                        ))
    
    def _find_missing_dependencies(self):
        """Findet fehlende Abhängigkeiten."""
        required_modules = {
            'MonsterInstance': 'engine.systems.monster_instance',
            'Move': 'engine.systems.moves',
            'StatusCondition': 'engine.systems.monster_instance',
            'BattleAction': 'engine.systems.battle.turn_logic'
        }
        
        for py_file in self.battle_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for class_name, module in required_modules.items():
                    if class_name in content:
                        # Prüfe ob Import vorhanden
                        if module not in self.imports.get(str(py_file), set()):
                            if f"from {module}" not in content and f"import {module}" not in content:
                                self.conflicts.append(CodeConflict(
                                    type=ConflictType.MISSING_DEPENDENCY,
                                    file_path=str(py_file),
                                    line_number=1,
                                    description=f"Verwendet '{class_name}' ohne Import von {module}",
                                    severity="high",
                                    suggested_fix=f"Füge 'from {module} import {class_name}' hinzu"
                                ))
            except Exception:
                pass
    
    def _find_state_inconsistencies(self):
        """Findet inkonsistente State-Verwaltung."""
        state_patterns = [
            (r'self\.player_active\s*=', 'player_active Zuweisung'),
            (r'self\.enemy_active\s*=', 'enemy_active Zuweisung'),
            (r'self\.phase\s*=', 'phase Zuweisung'),
            (r'self\.action_queue', 'action_queue Verwendung')
        ]
        
        for py_file in self.battle_path.rglob("*.py"):
            if py_file.name in ['battle.py', 'battle_controller.py', 'battle_system.py']:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    for pattern, desc in state_patterns:
                        matches = re.findall(pattern, content)
                        if len(matches) > 3:  # Zu viele State-Änderungen
                            self.conflicts.append(CodeConflict(
                                type=ConflictType.INCONSISTENT_STATE,
                                file_path=str(py_file),
                                line_number=1,
                                description=f"Zu viele direkte State-Änderungen: {desc} ({len(matches)}x)",
                                severity="medium",
                                suggested_fix="Verwende zentrale State-Management-Methoden"
                            ))
                except Exception:
                    pass
    
    def _find_deprecated_code(self):
        """Findet veralteten Code."""
        deprecated_patterns = [
            (r'print\s*\(', 'print statements (use logger)'),
            (r'except\s*:', 'bare except clause'),
            (r'type\s*\(.*\)\s*==', 'type() comparison'),
            (r'\.keys\(\)\s*\[', 'dict.keys() indexing')
        ]
        
        for py_file in self.battle_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for i, line in enumerate(lines, 1):
                    for pattern, desc in deprecated_patterns:
                        if re.search(pattern, line):
                            self.conflicts.append(CodeConflict(
                                type=ConflictType.DEPRECATED_CODE,
                                file_path=str(py_file),
                                line_number=i,
                                description=f"Veralteter Code: {desc}",
                                severity="low",
                                suggested_fix=f"Modernisiere: {desc}"
                            ))
            except Exception:
                pass
    
    def _get_duplicates(self) -> Dict[str, List[Tuple[str, int]]]:
        """Gibt alle Duplikate zurück."""
        duplicates = {}
        for name, locations in self.class_definitions.items():
            if len(locations) > 1:
                duplicates[f"class_{name}"] = locations
        for name, locations in self.function_definitions.items():
            if len(locations) > 1:
                duplicates[f"func_{name}"] = locations
        return duplicates
    
    def _find_unused_code(self) -> List[Tuple[str, str]]:
        """Findet ungenutzten Code."""
        unused = []
        
        # Sammle alle Referenzen
        all_references = set()
        for py_file in self.battle_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Einfache Referenz-Sammlung
                    words = re.findall(r'\b\w+\b', content)
                    all_references.update(words)
            except Exception:
                pass
        
        # Prüfe ungenutzte Funktionen
        for func_name in self.function_definitions:
            if func_name.startswith('_'):  # Private Funktionen überspringen
                continue
            # Count occurrences properly
            count = sum(1 for ref in all_references if ref == func_name)
            if count <= 1:  # Only defined, never called
                locations = self.function_definitions[func_name]
                if locations:
                    unused.append(("function", func_name))
        
        return unused
    
    def _analyze_performance(self) -> List[Dict[str, Any]]:
        """Analysiert Performance-Probleme."""
        issues = []
        
        performance_patterns = [
            (r'for .* in .*:\s*for .* in', 'Nested loops', 'high'),
            (r'isinstance\(.*\).*isinstance\(', 'Multiple isinstance calls', 'low'),
            (r'try:.*except.*pass', 'Silent exception handling', 'medium'),
            (r'global\s+', 'Global variable usage', 'medium')
        ]
        
        for py_file in self.battle_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern, desc, severity in performance_patterns:
                    matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                    if matches:
                        issues.append({
                            'file': str(py_file),
                            'issue': desc,
                            'severity': severity,
                            'count': len(matches)
                        })
            except Exception:
                pass
        
        return issues
    
    def _analyze_architecture(self) -> List[str]:
        """Analysiert Architektur-Probleme."""
        problems = []
        
        # Prüfe Datei-Größen
        for py_file in self.battle_path.rglob("*.py"):
            try:
                size = py_file.stat().st_size
                if size > 50000:  # > 50KB
                    problems.append(f"Datei zu groß: {py_file.name} ({size/1024:.1f}KB)")
                    
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                    if lines > 1000:
                        problems.append(f"Datei zu lang: {py_file.name} ({lines} Zeilen)")
            except Exception:
                pass
        
        # Prüfe Modul-Struktur
        if (self.battle_path / "battle.py").exists() and (self.battle_path / "battle_system.py").exists():
            problems.append("Redundante Haupt-Module: battle.py und battle_system.py")
        
        # Prüfe fehlende __init__.py
        if not (self.battle_path / "__init__.py").exists():
            problems.append("Fehlende __init__.py im battle Verzeichnis")
        
        return problems

# ================================
# HAUPTPROGRAMM
# ================================

def main():
    """Hauptprogramm des Conflict Resolvers."""
    print("""
╔══════════════════════════════════════════════════════╗
║  UNTOLD STORY - ELITE CONFLICT RESOLVER              ║
║  Ruhrpott JRPG Battle System Fixer                   ║
╚══════════════════════════════════════════════════════╝
    """)
    
    # Analysiere Battle-System
    analyzer = BattleSystemAnalyzer()
    analysis = analyzer.analyze()
    
    # Report
    print("\n📊 ANALYSE-ERGEBNIS:")
    print(f"  🔴 Kritische Konflikte: {sum(1 for c in analysis.conflicts if c.severity == 'critical')}")
    print(f"  🟠 Hohe Priorität: {sum(1 for c in analysis.conflicts if c.severity == 'high')}")
    print(f"  🟡 Mittlere Priorität: {sum(1 for c in analysis.conflicts if c.severity == 'medium')}")
    print(f"  🟢 Niedrige Priorität: {sum(1 for c in analysis.conflicts if c.severity == 'low')}")
    print(f"  📁 Betroffene Dateien: {len(set(c.file_path for c in analysis.conflicts))}")
    
    # Kritische Konflikte
    print("\n🚨 KRITISCHE KONFLIKTE:")
    for conflict in analysis.conflicts:
        if conflict.severity == 'critical':
            print(f"  ❌ {conflict.description}")
            print(f"     📍 {Path(conflict.file_path).name}:{conflict.line_number}")
            print(f"     💡 {conflict.suggested_fix}")
    
    # Architektur-Probleme
    if analysis.architecture_problems:
        print("\n🏗️ ARCHITEKTUR-PROBLEME:")
        for problem in analysis.architecture_problems:
            print(f"  ⚠️  {problem}")
    
    # Performance-Issues
    if analysis.performance_issues:
        print("\n⚡ PERFORMANCE-PROBLEME:")
        for issue in analysis.performance_issues:
            if issue['severity'] == 'high':
                print(f"  🔥 {issue['issue']} in {Path(issue['file']).name} ({issue['count']}x)")
    
    print("\n✅ ANALYSE ABGESCHLOSSEN!")
    print("\n🎮 Nächste Schritte:")
    print("  1. Nutze die Agent-Prompts in Cursor")
    print("  2. Refaktoriere battle.py zu einem Wrapper")
    print("  3. Teste das Battle-System gründlich")
    print("\n💪 Glück auf! Das Kampfsystem wird wieder sauber laufen!")

if __name__ == "__main__":
    main()
