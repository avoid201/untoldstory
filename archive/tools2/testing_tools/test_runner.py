#!/usr/bin/env python3
"""
Erweiterter Test-Runner für Untold Story
Führt alle Tests aus und generiert detaillierte Berichte
"""

import sys
import os
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import argparse

# Projekt-Root zum Python-Pfad hinzufügen
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

@dataclass
class TestResult:
    """Ergebnis eines einzelnen Tests"""
    name: str
    status: str  # "passed", "failed", "skipped", "error"
    duration: float
    error_message: Optional[str] = None
    traceback: Optional[str] = None
    category: str = "unknown"

@dataclass
class TestSuiteResult:
    """Ergebnis einer Test-Suite"""
    name: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    tests: List[TestResult] = field(default_factory=list)

@dataclass
class TestReport:
    """Vollständiger Test-Bericht"""
    timestamp: datetime = field(default_factory=datetime.now)
    total_suites: int = 0
    total_tests: int = 0
    total_passed: int = 0
    total_failed: int = 0
    total_skipped: int = 0
    total_errors: int = 0
    total_duration: float = 0.0
    suites: List[TestSuiteResult] = field(default_factory=list)
    
    def add_suite_result(self, suite_result: TestSuiteResult):
        """Fügt ein Suite-Ergebnis hinzu"""
        self.suites.append(suite_result)
        self.total_suites += 1
        self.total_tests += suite_result.total_tests
        self.total_passed += suite_result.passed
        self.total_failed += suite_result.failed
        self.total_skipped += suite_result.skipped
        self.total_errors += suite_result.errors
        self.total_duration += suite_result.duration
    
    def get_coverage_percentage(self) -> float:
        """Berechnet die Test-Coverage in Prozent"""
        if self.total_tests == 0:
            return 0.0
        return (self.total_passed / self.total_tests) * 100

class TestRunner:
    """Hauptklasse für das Ausführen von Tests"""
    
    def __init__(self, project_root: Path = PROJECT_ROOT):
        self.project_root = Path(project_root)
        self.report = TestReport()
        self.test_dirs = [
            "tests/systems",
            "tests/battle", 
            "tests/story",
            "tools/testing_tools"
        ]
        
    def run_pytest_on_directory(self, test_dir: str) -> TestSuiteResult:
        """Führt pytest auf einem Verzeichnis aus"""
        full_path = self.project_root / test_dir
        
        if not full_path.exists():
            return TestSuiteResult(
                name=test_dir,
                total_tests=0,
                passed=0,
                failed=0,
                skipped=0,
                errors=0,
                duration=0.0
            )
        
        print(f"\n🧪 Teste {test_dir}...")
        
        # Pytest-Kommando vorbereiten
        cmd = [
            sys.executable, "-m", "pytest",
            str(full_path),
            "--tb=short",
            "--json-report",
            "--json-report-file=none",
            "-v"
        ]
        
        start_time = time.time()
        
        try:
            # Pytest ausführen
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300  # 5 Minuten Timeout
            )
            
            duration = time.time() - start_time
            
            # Ergebnis parsen
            suite_result = self._parse_pytest_output(test_dir, result, duration)
            
            return suite_result
            
        except subprocess.TimeoutExpired:
            print(f"  ⏰ Timeout nach 5 Minuten für {test_dir}")
            return TestSuiteResult(
                name=test_dir,
                total_tests=0,
                passed=0,
                failed=0,
                skipped=0,
                errors=1,
                duration=300.0
            )
        except Exception as e:
            print(f"  ❌ Fehler beim Ausführen von {test_dir}: {e}")
            return TestSuiteResult(
                name=test_dir,
                total_tests=0,
                passed=0,
                failed=0,
                skipped=0,
                errors=1,
                duration=0.0
            )
    
    def _parse_pytest_output(self, test_dir: str, result: subprocess.CompletedProcess, duration: float) -> TestSuiteResult:
        """Parst die pytest-Ausgabe"""
        suite_result = TestSuiteResult(
            name=test_dir,
            total_tests=0,
            passed=0,
            failed=0,
            skipped=0,
            errors=0,
            duration=duration,
            tests=[]
        )
        
        # Einfache Ausgabe-Analyse
        output_lines = result.stdout.split('\n')
        
        for line in output_lines:
            if line.strip():
                if "::" in line and "PASSED" in line:
                    suite_result.passed += 1
                    suite_result.total_tests += 1
                    test_name = line.split("::")[-1].split()[0]
                    suite_result.tests.append(TestResult(
                        name=test_name,
                        status="passed",
                        duration=0.0,
                        category=self._get_test_category(test_dir)
                    ))
                elif "::" in line and "FAILED" in line:
                    suite_result.failed += 1
                    suite_result.total_tests += 1
                    test_name = line.split("::")[-1].split()[0]
                    suite_result.tests.append(TestResult(
                        name=test_name,
                        status="failed",
                        duration=0.0,
                        error_message="Test failed",
                        category=self._get_test_category(test_dir)
                    ))
                elif "::" in line and "SKIPPED" in line:
                    suite_result.skipped += 1
                    suite_result.total_tests += 1
                    test_name = line.split("::")[-1].split()[0]
                    suite_result.tests.append(TestResult(
                        name=test_name,
                        status="skipped",
                        duration=0.0,
                        category=self._get_test_category(test_dir)
                    ))
        
        # Fehler aus stderr
        if result.stderr:
            error_lines = result.stderr.split('\n')
            for line in error_lines:
                if "ERROR" in line and "::" in line:
                    suite_result.errors += 1
                    suite_result.total_tests += 1
                    test_name = line.split("::")[-1].split()[0]
                    suite_result.tests.append(TestResult(
                        name=test_name,
                        status="error",
                        duration=0.0,
                        error_message=line.strip(),
                        category=self._get_test_category(test_dir)
                    ))
        
        return suite_result
    
    def _get_test_category(self, test_dir: str) -> str:
        """Bestimmt die Test-Kategorie basierend auf dem Verzeichnis"""
        if "battle" in test_dir:
            return "battle"
        elif "story" in test_dir:
            return "story"
        elif "systems" in test_dir:
            return "systems"
        elif "testing_tools" in test_dir:
            return "tools"
        else:
            return "unknown"
    
    def run_all_tests(self) -> TestReport:
        """Führt alle Tests aus"""
        print("🚀 STARTE VOLLSTÄNDIGE TEST-SUITE")
        print("=" * 60)
        print(f"Projekt: {self.project_root}")
        print(f"Zeitstempel: {self.report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Alle Test-Verzeichnisse durchgehen
        for test_dir in self.test_dirs:
            suite_result = self.run_pytest_on_directory(test_dir)
            self.report.add_suite_result(suite_result)
            
            # Zwischenbericht
            print(f"  📊 {test_dir}: {suite_result.passed}/{suite_result.total_tests} bestanden")
        
        total_duration = time.time() - start_time
        self.report.total_duration = total_duration
        
        print("\n" + "=" * 60)
        print("🏁 TEST-SUITE ABGESCHLOSSEN")
        print("=" * 60)
        
        return self.report
    
    def print_report(self) -> None:
        """Gibt den Test-Bericht aus"""
        print("\n📊 TEST-BERICHT")
        print("=" * 60)
        
        # Zusammenfassung
        coverage = self.report.get_coverage_percentage()
        print(f"Gesamt-Tests: {self.report.total_tests}")
        print(f"Bestanden: {self.report.total_passed} ✅")
        print(f"Fehlgeschlagen: {self.report.total_failed} ❌")
        print(f"Übersprungen: {self.report.total_skipped} ⏭️")
        print(f"Fehler: {self.report.total_errors} 💥")
        print(f"Coverage: {coverage:.1f}%")
        print(f"Gesamt-Dauer: {self.report.total_duration:.2f}s")
        
        # Detaillierte Suite-Ergebnisse
        print("\n📋 SUITE-ERGEBNISSE:")
        print("-" * 40)
        
        for suite in self.report.suites:
            if suite.total_tests > 0:
                suite_coverage = (suite.passed / suite.total_tests) * 100
                status_icon = "✅" if suite_coverage == 100 else "⚠️" if suite_coverage >= 80 else "❌"
                
                print(f"{status_icon} {suite.name}:")
                print(f"  Tests: {suite.passed}/{suite.total_tests} ({suite_coverage:.1f}%)")
                print(f"  Dauer: {suite.duration:.2f}s")
                
                # Fehlgeschlagene Tests anzeigen
                failed_tests = [t for t in suite.tests if t.status in ["failed", "error"]]
                if failed_tests:
                    print(f"  Fehlgeschlagene Tests:")
                    for test in failed_tests:
                        print(f"    • {test.name}: {test.status}")
                        if test.error_message:
                            print(f"      Fehler: {test.error_message}")
        
        # Empfehlungen
        print("\n💡 EMPFEHLUNGEN:")
        print("-" * 40)
        
        if coverage >= 90:
            print("🎉 Ausgezeichnete Test-Coverage! Das Projekt ist gut getestet.")
        elif coverage >= 80:
            print("👍 Gute Test-Coverage. Einige Bereiche könnten mehr Tests vertragen.")
        elif coverage >= 60:
            print("⚠️ Mittlere Test-Coverage. Erwäge, mehr Tests hinzuzufügen.")
        else:
            print("❌ Niedrige Test-Coverage. Das Projekt benötigt deutlich mehr Tests.")
        
        if self.report.total_failed > 0:
            print(f"🔧 {self.report.total_failed} Tests müssen repariert werden.")
        
        if self.report.total_errors > 0:
            print(f"💥 {self.report.total_errors} Tests haben kritische Fehler.")
    
    def save_report(self, filename: str = "test_report.json") -> None:
        """Speichert den Test-Bericht als JSON"""
        report_data = {
            "timestamp": self.report.timestamp.isoformat(),
            "total_suites": self.report.total_suites,
            "total_tests": self.report.total_tests,
            "total_passed": self.report.total_passed,
            "total_failed": self.report.total_failed,
            "total_skipped": self.report.total_skipped,
            "total_errors": self.report.total_errors,
            "total_duration": self.report.total_duration,
            "coverage_percentage": self.report.get_coverage_percentage(),
            "suites": []
        }
        
        for suite in self.report.suites:
            suite_data = {
                "name": suite.name,
                "total_tests": suite.total_tests,
                "passed": suite.passed,
                "failed": suite.failed,
                "skipped": suite.skipped,
                "errors": suite.errors,
                "duration": suite.duration,
                "coverage_percentage": (suite.passed / suite.total_tests * 100) if suite.total_tests > 0 else 0,
                "tests": []
            }
            
            for test in suite.tests:
                test_data = {
                    "name": test.name,
                    "status": test.status,
                    "duration": test.duration,
                    "category": test.category
                }
                if test.error_message:
                    test_data["error_message"] = test.error_message
                if test.traceback:
                    test_data["traceback"] = test.traceback
                
                suite_data["tests"].append(test_data)
            
            report_data["suites"].append(suite_data)
        
        report_file = self.project_root / filename
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Test-Bericht gespeichert: {report_file}")

def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(description="Test-Runner für Untold Story")
    parser.add_argument("--save-report", action="store_true", help="Speichert den Test-Bericht als JSON")
    parser.add_argument("--report-file", default="test_report.json", help="Dateiname für den Test-Bericht")
    parser.add_argument("--verbose", "-v", action="store_true", help="Ausführliche Ausgabe")
    
    args = parser.parse_args()
    
    # Test-Runner starten
    runner = TestRunner()
    
    try:
        # Alle Tests ausführen
        report = runner.run_all_tests()
        
        # Bericht ausgeben
        runner.print_report()
        
        # Bericht speichern falls gewünscht
        if args.save_report:
            runner.save_report(args.report_file)
        
        # Exit-Code basierend auf Testergebnissen
        if report.total_failed > 0 or report.total_errors > 0:
            return 1
        else:
            return 0
            
    except KeyboardInterrupt:
        print("\n⏹️ Tests durch Benutzer abgebrochen")
        return 130
    except Exception as e:
        print(f"\n💥 Kritischer Fehler: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
