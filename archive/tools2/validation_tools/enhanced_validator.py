#!/usr/bin/env python3
"""
Erweiterter Validator für Untold Story
Umfassende Validierung aller Spielsysteme und Daten
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import xml.etree.ElementTree as ET
from datetime import datetime
import hashlib

# Projekt-Root zum Python-Pfad hinzufügen
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class ValidationSeverity(Enum):
    """Validierungs-Schweregrade"""
    CRITICAL = "CRITICAL"    # Spiel kann nicht gestartet werden
    ERROR = "ERROR"          # Funktionalität beeinträchtigt
    WARNING = "WARNING"      # Mögliche Probleme
    INFO = "INFO"           # Informative Nachrichten
    SUCCESS = "SUCCESS"     # Erfolgreiche Validierung

@dataclass
class ValidationIssue:
    """Einzelnes Validierungsproblem"""
    severity: ValidationSeverity
    category: str
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    details: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ValidationReport:
    """Vollständiger Validierungsbericht"""
    timestamp: datetime = field(default_factory=datetime.now)
    issues: List[ValidationIssue] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=dict)
    total_checks: int = 0
    passed_checks: int = 0
    
    def add_issue(self, issue: ValidationIssue):
        """Fügt ein Problem zum Bericht hinzu"""
        self.issues.append(issue)
        
    def get_issues_by_severity(self, severity: ValidationSeverity) -> List[ValidationIssue]:
        """Gibt alle Probleme einer bestimmten Schwere zurück"""
        return [issue for issue in self.issues if issue.severity == severity]
    
    def generate_summary(self):
        """Generiert Zusammenfassung der Validierung"""
        self.summary = {
            "total_issues": len(self.issues),
            "critical": len(self.get_issues_by_severity(ValidationSeverity.CRITICAL)),
            "errors": len(self.get_issues_by_severity(ValidationSeverity.ERROR)),
            "warnings": len(self.get_issues_by_severity(ValidationSeverity.WARNING)),
            "info": len(self.get_issues_by_severity(ValidationSeverity.INFO)),
            "success": len(self.get_issues_by_severity(ValidationSeverity.SUCCESS))
        }
        
        self.passed_checks = self.total_checks - self.summary["critical"] - self.summary["errors"]

class EnhancedValidator:
    """Erweiterter Validator für alle Spielsysteme"""
    
    def __init__(self, project_root: Path = PROJECT_ROOT):
        self.project_root = Path(project_root)
        self.report = ValidationReport()
        self.data_cache: Dict[str, Any] = {}
        self.reference_cache: Dict[str, Set[str]] = {}
        
    def validate_project_structure(self) -> None:
        """Validiert die Projektstruktur"""
        print("🏗️ Validiere Projektstruktur...")
        
        required_dirs = [
            "engine",
            "data",
            "assets",
            "tests",
            "tools"
        ]
        
        required_files = [
            "main.py",
            "requirements.txt",
            "README.md"
        ]
        
        for directory in required_dirs:
            dir_path = self.project_root / directory
            if dir_path.exists() and dir_path.is_dir():
                self.report.add_issue(ValidationIssue(
                    severity=ValidationSeverity.SUCCESS,
                    category="Project Structure",
                    message=f"Verzeichnis '{directory}' gefunden",
                    file_path=str(dir_path)
                ))
            else:
                self.report.add_issue(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category="Project Structure",
                    message=f"Erforderliches Verzeichnis '{directory}' fehlt",
                    file_path=str(dir_path),
                    suggestions=["Verzeichnis erstellen", "Git-Repository überprüfen"]
                ))
        
        for file in required_files:
            file_path = self.project_root / file
            if file_path.exists():
                self.report.add_issue(ValidationIssue(
                    severity=ValidationSeverity.SUCCESS,
                    category="Project Structure",
                    message=f"Datei '{file}' gefunden",
                    file_path=str(file_path)
                ))
            else:
                self.report.add_issue(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="Project Structure",
                    message=f"Erforderliche Datei '{file}' fehlt",
                    file_path=str(file_path),
                    suggestions=["Datei erstellen", "Git-Repository überprüfen"]
                ))
    
    def validate_python_modules(self) -> None:
        """Validiert alle Python-Module"""
        print("🐍 Validiere Python-Module...")
        
        engine_dir = self.project_root / "engine"
        if not engine_dir.exists():
            return
        
        # Sammle alle Python-Dateien
        python_files = list(engine_dir.rglob("*.py"))
        
        for py_file in python_files:
            try:
                # Versuche Import
                module_path = py_file.relative_to(self.project_root)
                module_name = str(module_path).replace("/", ".").replace("\\", ".").replace(".py", "")
                
                # Überspringe __init__.py
                if module_name.endswith("__init__"):
                    continue
                
                # Teste Syntax
                with open(py_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), str(py_file), 'exec')
                
                self.report.add_issue(ValidationIssue(
                    severity=ValidationSeverity.SUCCESS,
                    category="Python Modules",
                    message=f"Modul '{module_name}' Syntax OK",
                    file_path=str(py_file)
                ))
                
            except SyntaxError as e:
                self.report.add_issue(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="Python Modules",
                    message=f"Syntax-Fehler in '{py_file.name}'",
                    file_path=str(py_file),
                    line_number=e.lineno,
                    details=str(e),
                    suggestions=["Syntax-Fehler beheben", "Python-Version überprüfen"]
                ))
            except Exception as e:
                self.report.add_issue(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="Python Modules",
                    message=f"Unbekannter Fehler in '{py_file.name}'",
                    file_path=str(py_file),
                    details=str(e)
                ))
    
    def validate_data_files(self) -> None:
        """Validiert alle JSON-Datendateien"""
        print("📊 Validiere Datendateien...")
        
        data_dir = self.project_root / "data"
        if not data_dir.exists():
            return
        
        json_files = list(data_dir.rglob("*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Validiere JSON-Struktur
                if isinstance(data, dict):
                    self.report.add_issue(ValidationIssue(
                        severity=ValidationSeverity.SUCCESS,
                        category="Data Files",
                        message=f"JSON-Datei '{json_file.name}' gültig",
                        file_path=str(json_file),
                        details=f"{len(data)} Einträge gefunden"
                    ))
                    
                    # Cache für Cross-Referenz-Validierung
                    self.data_cache[json_file.name] = data
                    
                elif isinstance(data, list):
                    self.report.add_issue(ValidationIssue(
                        severity=ValidationSeverity.SUCCESS,
                        category="Data Files",
                        message=f"JSON-Liste '{json_file.name}' gültig",
                        file_path=str(json_file),
                        details=f"{len(data)} Einträge gefunden"
                    ))
                    
                    self.data_cache[json_file.name] = data
                    
            except json.JSONDecodeError as e:
                self.report.add_issue(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="Data Files",
                    message=f"JSON-Fehler in '{json_file.name}'",
                    file_path=str(json_file),
                    line_number=e.lineno,
                    details=str(e),
                    suggestions=["JSON-Syntax korrigieren", "Online JSON-Validator verwenden"]
                ))
            except Exception as e:
                self.report.add_issue(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="Data Files",
                    message=f"Fehler beim Lesen von '{json_file.name}'",
                    file_path=str(json_file),
                    details=str(e)
                ))
    
    def validate_tmx_files(self) -> None:
        """Validiert TMX-Kartendateien"""
        print("🗺️ Validiere TMX-Dateien...")
        
        maps_dir = self.project_root / "data" / "maps"
        if not maps_dir.exists():
            return
        
        tmx_files = list(maps_dir.glob("*.tmx"))
        
        for tmx_file in tmx_files:
            try:
                tree = ET.parse(tmx_file)
                root = tree.getroot()
                
                # Validiere TMX-Struktur
                width = int(root.get('width', 0))
                height = int(root.get('height', 0))
                tile_size = int(root.get('tilewidth', 16))
                
                if width > 0 and height > 0:
                    self.report.add_issue(ValidationIssue(
                        severity=ValidationSeverity.SUCCESS,
                        category="TMX Files",
                        message=f"TMX-Datei '{tmx_file.name}' gültig",
                        file_path=str(tmx_file),
                        details=f"Größe: {width}x{height}, Tile-Größe: {tile_size}"
                    ))
                    
                    # Validiere Layer
                    layers = root.findall('.//layer')
                    if layers:
                        for layer in layers:
                            layer_name = layer.get('name', 'Unbekannt')
                            layer_width = int(layer.get('width', 0))
                            layer_height = int(layer.get('height', 0))
                            
                            if layer_width != width or layer_height != height:
                                self.report.add_issue(ValidationIssue(
                                    severity=ValidationSeverity.WARNING,
                                    category="TMX Files",
                                    message=f"Layer '{layer_name}' hat andere Größe als Karte",
                                    file_path=str(tmx_file),
                                    details=f"Layer: {layer_width}x{layer_height}, Karte: {width}x{height}",
                                    suggestions=["Layer-Größe anpassen", "Karte neu erstellen"]
                                ))
                else:
                    self.report.add_issue(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category="TMX Files",
                        message=f"Ungültige Karten-Größe in '{tmx_file.name}'",
                        file_path=str(tmx_file),
                        details=f"Breite: {width}, Höhe: {height}",
                        suggestions=["Karten-Größe korrigieren", "Tiled-Editor verwenden"]
                    ))
                    
            except ET.ParseError as e:
                self.report.add_issue(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="TMX Files",
                    message=f"XML-Parse-Fehler in '{tmx_file.name}'",
                    file_path=str(tmx_file),
                    details=str(e),
                    suggestions=["XML-Syntax korrigieren", "Tiled-Editor verwenden"]
                ))
            except Exception as e:
                self.report.add_issue(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="TMX Files",
                    message=f"Fehler beim Lesen von '{tmx_file.name}'",
                    file_path=str(tmx_file),
                    details=str(e)
                ))
    
    def validate_asset_files(self) -> None:
        """Validiert Asset-Dateien (Bilder, Audio)"""
        print("🎨 Validiere Asset-Dateien...")
        
        assets_dir = self.project_root / "assets"
        if not assets_dir.exists():
            return
        
        # Überprüfe Bilddateien
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(assets_dir.rglob(f"*{ext}"))
        
        for image_file in image_files:
            try:
                # Überprüfe Dateigröße
                file_size = image_file.stat().st_size
                
                if file_size > 0:
                    self.report.add_issue(ValidationIssue(
                        severity=ValidationSeverity.SUCCESS,
                        category="Asset Files",
                        message=f"Bilddatei '{image_file.name}' OK",
                        file_path=str(image_file),
                        details=f"Größe: {file_size} Bytes"
                    ))
                else:
                    self.report.add_issue(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category="Asset Files",
                        message=f"Leere Bilddatei '{image_file.name}'",
                        file_path=str(image_file),
                        suggestions=["Datei neu erstellen", "Asset-Quelle überprüfen"]
                    ))
                    
            except Exception as e:
                self.report.add_issue(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="Asset Files",
                    message=f"Fehler beim Überprüfen von '{image_file.name}'",
                    file_path=str(image_file),
                    details=str(e)
                ))
    
    def validate_cross_references(self) -> None:
        """Validiert Cross-Referenzen zwischen Datendateien"""
        print("🔗 Validiere Cross-Referenzen...")
        
        if not self.data_cache:
            return
        
        # Validiere Monster-Move-Referenzen
        if 'monsters.json' in self.data_cache and 'moves.json' in self.data_cache:
            monsters = self.data_cache['monsters.json']
            moves = self.data_cache['moves.json']
            
            available_moves = set(moves.keys())
            
            for monster_id, monster_data in monsters.items():
                if 'moves' in monster_data:
                    monster_moves = monster_data['moves']
                    for move_id in monster_moves:
                        if move_id not in available_moves:
                            self.report.add_issue(ValidationIssue(
                                severity=ValidationSeverity.ERROR,
                                category="Cross References",
                                message=f"Monster '{monster_id}' verweist auf unbekannten Move '{move_id}'",
                                details=f"Move existiert nicht in moves.json",
                                suggestions=["Move hinzufügen", "Referenz korrigieren"]
                            ))
        
        # Validiere Type-Referenzen
        if 'monsters.json' in self.data_cache and 'types.json' in self.data_cache:
            monsters = self.data_cache['monsters.json']
            types = self.data_cache['types.json']
            
            available_types = set(types.keys())
            
            for monster_id, monster_data in monsters.items():
                if 'types' in monster_data:
                    monster_types = monster_data['types']
                    for type_name in monster_types:
                        if type_name not in available_types:
                            self.report.add_issue(ValidationIssue(
                                severity=ValidationSeverity.ERROR,
                                category="Cross References",
                                message=f"Monster '{monster_id}' hat unbekannten Typ '{type_name}'",
                                details=f"Typ existiert nicht in types.json",
                                suggestions=["Typ hinzufügen", "Typ-Referenz korrigieren"]
                            ))
    
    def validate_all(self) -> ValidationReport:
        """Führt alle Validierungen durch"""
        print("🚀 Starte umfassende Validierung...")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Alle Validierungen durchführen
        self.validate_project_structure()
        self.validate_python_modules()
        self.validate_data_files()
        self.validate_tmx_files()
        self.validate_asset_files()
        self.validate_cross_references()
        
        # Bericht generieren
        self.report.generate_summary()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n⏱️ Validierung abgeschlossen in {duration.total_seconds():.2f} Sekunden")
        print("=" * 60)
        
        return self.report
    
    def print_report(self) -> None:
        """Gibt den Validierungsbericht aus"""
        if not self.report.issues:
            print("✅ Keine Probleme gefunden!")
            return
        
        # Gruppiere nach Schweregrad
        for severity in ValidationSeverity:
            issues = self.get_issues_by_severity(severity)
            if issues:
                print(f"\n{severity.value}:")
                print("-" * len(severity.value))
                
                for issue in issues:
                    print(f"  • {issue.message}")
                    if issue.file_path:
                        print(f"    Datei: {issue.file_path}")
                    if issue.details:
                        print(f"    Details: {issue.details}")
                    if issue.suggestions:
                        print(f"    Vorschläge: {', '.join(issue.suggestions)}")
                    print()
        
        # Zusammenfassung
        print("📊 ZUSAMMENFASSUNG:")
        print("=" * 40)
        for key, value in self.report.summary.items():
            print(f"  {key}: {value}")
        
        # Empfehlung
        if self.report.summary["critical"] > 0:
            print("\n❌ KRITISCHE FEHLER GEFUNDEN!")
            print("Das Spiel kann nicht gestartet werden.")
        elif self.report.summary["errors"] > 0:
            print("\n⚠️ FEHLER GEFUNDEN!")
            print("Das Spiel funktioniert möglicherweise nicht korrekt.")
        elif self.report.summary["warnings"] > 0:
            print("\n⚠️ WARNUNGEN GEFUNDEN!")
            print("Das Spiel sollte funktionieren, aber es gibt Probleme.")
        else:
            print("\n✅ ALLE VALIDIERUNGEN BESTANDEN!")
            print("Das Spiel ist bereit zum Starten.")

def main():
    """Hauptfunktion"""
    validator = EnhancedValidator()
    report = validator.validate_all()
    validator.print_report()
    
    # Exit-Code basierend auf Schweregrad
    if report.summary["critical"] > 0:
        return 2
    elif report.summary["errors"] > 0:
        return 1
    else:
        return 0

if __name__ == "__main__":
    sys.exit(main())
