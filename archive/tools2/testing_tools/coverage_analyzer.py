#!/usr/bin/env python3
"""
Test-Coverage-Analyzer für Untold Story
Analysiert die Abdeckung von Tests und identifiziert ungetestete Bereiche
"""

import sys
import os
import json
import ast
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import argparse

# Projekt-Root zum Python-Pfad hinzufügen
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

@dataclass
class CodeElement:
    """Ein Code-Element (Funktion, Klasse, etc.)"""
    name: str
    type: str  # "function", "class", "method"
    line_number: int
    end_line: int
    file_path: str
    docstring: Optional[str] = None
    parameters: List[str] = field(default_factory=list)

@dataclass
class TestCoverage:
    """Test-Coverage für ein Code-Element"""
    element: CodeElement
    is_tested: bool = False
    test_files: List[str] = field(default_factory=list)
    test_coverage: float = 0.0  # 0.0 bis 1.0

@dataclass
class FileCoverage:
    """Test-Coverage für eine Datei"""
    file_path: str
    total_elements: int
    tested_elements: int
    coverage_percentage: float
    elements: List[TestCoverage] = field(default_factory=list)

@dataclass
class CoverageReport:
    """Vollständiger Coverage-Bericht"""
    timestamp: datetime = field(default_factory=datetime.now)
    total_files: int = 0
    total_elements: int = 0
    total_tested: int = 0
    overall_coverage: float = 0.0
    file_coverage: List[FileCoverage] = field(default_factory=list)
    untested_elements: List[CodeElement] = field(default_factory=list)
    critical_untested: List[CodeElement] = field(default_factory=list)

class CoverageAnalyzer:
    """Analysiert Test-Coverage des Projekts"""
    
    def __init__(self, project_root: Path = PROJECT_ROOT):
        self.project_root = Path(project_root)
        self.report = CoverageReport()
        self.code_elements: List[CodeElement] = []
        self.test_files: Set[str] = set()
        
        # Wichtige Verzeichnisse
        self.source_dirs = ["engine", "data"]
        self.test_dirs = ["tests", "tools/testing_tools"]
        
        # Kritische Module (sollten gut getestet sein)
        self.critical_modules = [
            "engine/systems/battle",
            "engine/systems/monsters",
            "engine/systems/moves",
            "engine/core/game",
            "engine/world/area"
        ]
    
    def analyze_source_code(self) -> None:
        """Analysiert den Quellcode nach Code-Elementen"""
        print("🔍 Analysiere Quellcode...")
        
        for source_dir in self.source_dirs:
            source_path = self.project_root / source_dir
            if not source_path.exists():
                continue
            
            # Alle Python-Dateien durchgehen
            python_files = list(source_path.rglob("*.py"))
            
            for py_file in python_files:
                self._analyze_python_file(py_file)
        
        print(f"  📊 {len(self.code_elements)} Code-Elemente gefunden")
    
    def _analyze_python_file(self, file_path: Path) -> None:
        """Analysiert eine einzelne Python-Datei"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # AST parsen
            tree = ast.parse(content)
            
            # Datei-relative Pfad
            relative_path = file_path.relative_to(self.project_root)
            
            # Klassen analysieren
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._analyze_class(node, relative_path)
                elif isinstance(node, ast.FunctionDef):
                    self._analyze_function(node, relative_path)
                elif isinstance(node, ast.AsyncFunctionDef):
                    self._analyze_async_function(node, relative_path)
                    
        except Exception as e:
            print(f"  ⚠️ Fehler beim Analysieren von {file_path}: {e}")
    
    def _analyze_class(self, node: ast.ClassDef, file_path: str) -> None:
        """Analysiert eine Klasse"""
        # Klasse selbst
        class_element = CodeElement(
            name=node.name,
            type="class",
            line_number=node.lineno,
            end_line=node.end_lineno or node.lineno,
            file_path=str(file_path),
            docstring=ast.get_docstring(node)
        )
        
        self.code_elements.append(class_element)
        
        # Methoden der Klasse
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self._analyze_method(item, file_path, node.name)
            elif isinstance(item, ast.AsyncFunctionDef):
                self._analyze_async_method(item, file_path, node.name)
    
    def _analyze_function(self, node: ast.FunctionDef, file_path: str) -> None:
        """Analysiert eine Funktion"""
        # Parameter extrahieren
        parameters = [arg.arg for arg in node.args.args]
        
        function_element = CodeElement(
            name=node.name,
            type="function",
            line_number=node.lineno,
            end_line=node.end_lineno or node.lineno,
            file_path=str(file_path),
            docstring=ast.get_docstring(node),
            parameters=parameters
        )
        
        self.code_elements.append(function_element)
    
    def _analyze_async_function(self, node: ast.AsyncFunctionDef, file_path: str) -> None:
        """Analysiert eine asynchrone Funktion"""
        parameters = [arg.arg for arg in node.args.args]
        
        function_element = CodeElement(
            name=node.name,
            type="function",
            line_number=node.lineno,
            end_line=node.end_lineno or node.lineno,
            file_path=str(file_path),
            docstring=ast.get_docstring(node),
            parameters=parameters
        )
        
        self.code_elements.append(function_element)
    
    def _analyze_method(self, node: ast.FunctionDef, file_path: str, class_name: str) -> None:
        """Analysiert eine Methode"""
        parameters = [arg.arg for arg in node.args.args]
        
        method_element = CodeElement(
            name=f"{class_name}.{node.name}",
            type="method",
            line_number=node.lineno,
            end_line=node.end_lineno or node.lineno,
            file_path=str(file_path),
            docstring=ast.get_docstring(node),
            parameters=parameters
        )
        
        self.code_elements.append(method_element)
    
    def _analyze_async_method(self, node: ast.AsyncFunctionDef, file_path: str, class_name: str) -> None:
        """Analysiert eine asynchrone Methode"""
        parameters = [arg.arg for arg in node.args.args]
        
        method_element = CodeElement(
            name=f"{class_name}.{node.name}",
            type="function",
            line_number=node.lineno,
            end_line=node.end_lineno or node.lineno,
            file_path=str(file_path),
            docstring=ast.get_docstring(node),
            parameters=parameters
        )
        
        self.code_elements.append(method_element)
    
    def discover_test_files(self) -> None:
        """Entdeckt alle Test-Dateien"""
        print("🧪 Entdecke Test-Dateien...")
        
        for test_dir in self.test_dirs:
            test_path = self.project_root / test_dir
            if not test_path.exists():
                continue
            
            # Alle Python-Test-Dateien
            test_files = list(test_path.rglob("test_*.py"))
            test_files.extend(list(test_path.rglob("*_test.py")))
            
            for test_file in test_files:
                self.test_files.add(str(test_file.relative_to(self.project_root)))
        
        print(f"  📁 {len(self.test_files)} Test-Dateien gefunden")
    
    def analyze_test_coverage(self) -> None:
        """Analysiert die Test-Coverage"""
        print("📊 Analysiere Test-Coverage...")
        
        # Gruppiere Code-Elemente nach Datei
        elements_by_file: Dict[str, List[CodeElement]] = {}
        for element in self.code_elements:
            if element.file_path not in elements_by_file:
                elements_by_file[element.file_path] = []
            elements_by_file[element.file_path].append(element)
        
        # Analysiere jede Datei
        for file_path, elements in elements_by_file.items():
            file_coverage = self._analyze_file_coverage(file_path, elements)
            self.report.file_coverage.append(file_coverage)
        
        # Gesamt-Statistiken berechnen
        self._calculate_overall_coverage()
        
        # Ungetestete Elemente identifizieren
        self._identify_untested_elements()
    
    def _analyze_file_coverage(self, file_path: str, elements: List[CodeElement]) -> FileCoverage:
        """Analysiert Coverage für eine einzelne Datei"""
        tested_elements = 0
        element_coverage: List[TestCoverage] = []
        
        for element in elements:
            # Prüfe, ob das Element getestet wird
            is_tested, test_files = self._is_element_tested(element)
            
            if is_tested:
                tested_elements += 1
            
            coverage = TestCoverage(
                element=element,
                is_tested=is_tested,
                test_files=test_files,
                test_coverage=1.0 if is_tested else 0.0
            )
            
            element_coverage.append(coverage)
        
        coverage_percentage = (tested_elements / len(elements)) * 100 if elements else 0
        
        return FileCoverage(
            file_path=file_path,
            total_elements=len(elements),
            tested_elements=tested_elements,
            coverage_percentage=coverage_percentage,
            elements=element_coverage
        )
    
    def _is_element_tested(self, element: CodeElement) -> Tuple[bool, List[str]]:
        """Prüft, ob ein Code-Element getestet wird"""
        test_files = []
        
        # Suche nach Tests für dieses Element
        for test_file in self.test_files:
            if self._test_file_covers_element(test_file, element):
                test_files.append(test_file)
        
        return len(test_files) > 0, test_files
    
    def _test_file_covers_element(self, test_file: str, element: CodeElement) -> bool:
        """Prüft, ob eine Test-Datei ein Code-Element abdeckt"""
        try:
            test_path = self.project_root / test_file
            
            with open(test_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Einfache Heuristik: Suche nach dem Element-Namen
            element_name = element.name.split('.')[-1]  # Nur der letzte Teil
            
            # Überspringe __init__ und andere spezielle Namen
            if element_name in ['__init__', '__main__', 'main']:
                return False
            
            # Suche nach dem Namen im Test
            if element_name in content:
                return True
            
            # Suche nach Import-Statements
            if f"from {element.file_path.replace('/', '.')}" in content:
                return True
            
            if f"import {element.file_path.replace('/', '.')}" in content:
                return True
            
            return False
            
        except Exception:
            return False
    
    def _calculate_overall_coverage(self) -> None:
        """Berechnet die Gesamt-Coverage"""
        total_elements = sum(fc.total_elements for fc in self.report.file_coverage)
        total_tested = sum(fc.tested_elements for fc in self.report.file_coverage)
        
        self.report.total_files = len(self.report.file_coverage)
        self.report.total_elements = total_elements
        self.report.total_tested = total_tested
        
        if total_elements > 0:
            self.report.overall_coverage = (total_tested / total_elements) * 100
        else:
            self.report.overall_coverage = 0.0
    
    def _identify_untested_elements(self) -> None:
        """Identifiziert ungetestete Code-Elemente"""
        for file_coverage in self.report.file_coverage:
            for element_coverage in file_coverage.elements:
                if not element_coverage.is_tested:
                    self.report.untested_elements.append(element_coverage.element)
                    
                    # Prüfe, ob es sich um ein kritisches Modul handelt
                    if self._is_critical_module(element_coverage.element.file_path):
                        self.report.critical_untested.append(element_coverage.element)
    
    def _is_critical_module(self, file_path: str) -> bool:
        """Prüft, ob es sich um ein kritisches Modul handelt"""
        for critical_module in self.critical_modules:
            if critical_module in file_path:
                return True
        return False
    
    def generate_report(self) -> CoverageReport:
        """Generiert den vollständigen Coverage-Bericht"""
        print("📋 Generiere Coverage-Bericht...")
        
        self.analyze_source_code()
        self.discover_test_files()
        self.analyze_test_coverage()
        
        return self.report
    
    def print_report(self) -> None:
        """Gibt den Coverage-Bericht aus"""
        print("\n" + "=" * 80)
        print("📊 TEST-COVERAGE-BERICHT")
        print("=" * 80)
        
        # Übersicht
        print(f"📁 Gesamt-Dateien: {self.report.total_files}")
        print(f"🔧 Gesamt-Code-Elemente: {self.report.total_elements}")
        print(f"✅ Getestete Elemente: {self.report.total_tested}")
        print(f"❌ Ungetestete Elemente: {len(self.report.untested_elements)}")
        print(f"📈 Gesamt-Coverage: {self.report.overall_coverage:.1f}%")
        
        # Coverage nach Datei
        print("\n📋 COVERAGE NACH DATEI:")
        print("-" * 80)
        
        # Sortiere nach Coverage (niedrigste zuerst)
        sorted_files = sorted(self.report.file_coverage, key=lambda x: x.coverage_percentage)
        
        for file_coverage in sorted_files:
            status_icon = "✅" if file_coverage.coverage_percentage >= 80 else "⚠️" if file_coverage.coverage_percentage >= 50 else "❌"
            
            print(f"{status_icon} {file_coverage.file_path}: {file_coverage.coverage_percentage:.1f}% "
                  f"({file_coverage.tested_elements}/{file_coverage.total_elements})")
        
        # Ungetestete kritische Elemente
        if self.report.critical_untested:
            print(f"\n🚨 KRITISCH UNGETESTETE ELEMENTE ({len(self.report.critical_untested)}):")
            print("-" * 80)
            
            for element in self.report.critical_untested[:10]:  # Zeige nur erste 10
                print(f"  • {element.name} ({element.type}) in {element.file_path}:{element.line_number}")
            
            if len(self.report.critical_untested) > 10:
                print(f"  ... und {len(self.report.critical_untested) - 10} weitere")
        
        # Empfehlungen
        print(f"\n💡 EMPFEHLUNGEN:")
        print("-" * 80)
        
        if self.report.overall_coverage >= 90:
            print("🎉 Ausgezeichnete Test-Coverage! Das Projekt ist sehr gut getestet.")
        elif self.report.overall_coverage >= 80:
            print("👍 Gute Test-Coverage. Einige Bereiche könnten mehr Tests vertragen.")
        elif self.report.overall_coverage >= 60:
            print("⚠️ Mittlere Test-Coverage. Erwäge, mehr Tests hinzuzufügen.")
        else:
            print("❌ Niedrige Test-Coverage. Das Projekt benötigt deutlich mehr Tests.")
        
        if self.report.critical_untested:
            print(f"🔧 Priorität: Teste zuerst die kritischen Module ({len(self.report.critical_untested)} Elemente)")
        
        # Dateien mit niedriger Coverage
        low_coverage_files = [fc for fc in self.report.file_coverage if fc.coverage_percentage < 50]
        if low_coverage_files:
            print(f"📝 Fokus: {len(low_coverage_files)} Dateien haben weniger als 50% Coverage")
    
    def save_report(self, filename: str = "coverage_report.json") -> None:
        """Speichert den Coverage-Bericht als JSON"""
        report_data = {
            "timestamp": self.report.timestamp.isoformat(),
            "total_files": self.report.total_files,
            "total_elements": self.report.total_elements,
            "total_tested": self.report.total_tested,
            "overall_coverage": self.report.overall_coverage,
            "file_coverage": [],
            "untested_elements": [],
            "critical_untested": []
        }
        
        # Datei-Coverage
        for fc in self.report.file_coverage:
            fc_data = {
                "file_path": fc.file_path,
                "total_elements": fc.total_elements,
                "tested_elements": fc.tested_elements,
                "coverage_percentage": fc.coverage_percentage,
                "elements": []
            }
            
            for ec in fc.elements:
                ec_data = {
                    "name": ec.element.name,
                    "type": ec.element.type,
                    "line_number": ec.element.line_number,
                    "is_tested": ec.is_tested,
                    "test_files": ec.test_files
                }
                fc_data["elements"].append(ec_data)
            
            report_data["file_coverage"].append(fc_data)
        
        # Ungetestete Elemente
        for element in self.report.untested_elements:
            element_data = {
                "name": element.name,
                "type": element.type,
                "line_number": element.line_number,
                "file_path": element.file_path
            }
            report_data["untested_elements"].append(element_data)
        
        # Kritische ungetestete Elemente
        for element in self.report.critical_untested:
            element_data = {
                "name": element.name,
                "type": element.type,
                "line_number": element.line_number,
                "file_path": element.file_path
            }
            report_data["critical_untested"].append(element_data)
        
        report_file = self.project_root / filename
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Coverage-Bericht gespeichert: {report_file}")

def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(description="Test-Coverage-Analyzer für Untold Story")
    parser.add_argument("--save-report", action="store_true", help="Speichert den Coverage-Bericht als JSON")
    parser.add_argument("--report-file", default="coverage_report.json", help="Dateiname für den Coverage-Bericht")
    parser.add_argument("--verbose", "-v", action="store_true", help="Ausführliche Ausgabe")
    
    args = parser.parse_args()
    
    # Coverage-Analyzer starten
    analyzer = CoverageAnalyzer()
    
    try:
        # Coverage analysieren
        report = analyzer.generate_report()
        
        # Bericht ausgeben
        analyzer.print_report()
        
        # Bericht speichern falls gewünscht
        if args.save_report:
            analyzer.save_report(args.report_file)
        
        # Exit-Code basierend auf Coverage
        if report.overall_coverage < 50:
            return 1  # Niedrige Coverage
        elif report.overall_coverage < 80:
            return 2  # Mittlere Coverage
        else:
            return 0  # Gute Coverage
            
    except KeyboardInterrupt:
        print("\n⏹️ Coverage-Analyse durch Benutzer abgebrochen")
        return 130
    except Exception as e:
        print(f"\n💥 Kritischer Fehler: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
