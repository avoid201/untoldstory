#!/usr/bin/env python3
"""
Event Emission Audit Script
===========================
Findet alle Event-Emissionen im Battle System und identifiziert Duplikate.
"""

import ast
import glob
import os
from typing import Dict, List, Tuple
from collections import defaultdict


def find_event_emissions() -> Dict[str, List[Tuple[int, str]]]:
    """Finde alle Stellen wo Events emittiert werden."""
    emissions = defaultdict(list)
    
    # Suche in allen Python-Dateien im Battle System
    pattern = "engine/systems/battle/**/*.py"
    for file_path in glob.glob(pattern, recursive=True):
        if file_path.endswith('__pycache__'):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
                
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # Suche nach emit_event Aufrufen
                    if hasattr(node.func, 'attr') and node.func.attr == 'emit_event':
                        line_no = node.lineno
                        line_content = content.split('\n')[line_no - 1].strip()
                        emissions[file_path].append((line_no, line_content))
                    
                    # Suche nach EventType Verwendungen
                    elif isinstance(node.func, ast.Attribute) and node.func.attr == 'emit_event':
                        line_no = node.lineno
                        line_content = content.split('\n')[line_no - 1].strip()
                        emissions[file_path].append((line_no, line_content))
                        
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
    
    return dict(emissions)


def find_event_type_usage() -> Dict[str, List[Tuple[int, str]]]:
    """Finde alle EventType Verwendungen."""
    event_types = defaultdict(list)
    
    pattern = "engine/systems/battle/**/*.py"
    for file_path in glob.glob(pattern, recursive=True):
        if file_path.endswith('__pycache__'):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
                
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and hasattr(node.value, 'id') and node.value.id == 'EventType':
                    line_no = node.lineno
                    line_content = content.split('\n')[line_no - 1].strip()
                    event_types[file_path].append((line_no, line_content))
                    
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
    
    return dict(event_types)


def analyze_duplicates(emissions: Dict[str, List[Tuple[int, str]]]) -> Dict[str, List[str]]:
    """Analysiere Event-Duplikate."""
    duplicates = defaultdict(list)
    
    # Gruppiere nach Event-Type
    event_type_usage = defaultdict(list)
    
    for file_path, events in emissions.items():
        for line_no, line_content in events:
            # Extrahiere EventType aus der Zeile
            if 'EventType.' in line_content:
                try:
                    # Einfache Regex-ähnliche Extraktion
                    start = line_content.find('EventType.') + 9
                    end = line_content.find(',', start)
                    if end == -1:
                        end = line_content.find(')', start)
                    if end == -1:
                        end = len(line_content)
                    
                    event_type = line_content[start:end].strip()
                    event_type_usage[event_type].append(f"{file_path}:{line_no}")
                except:
                    pass
    
    # Finde Duplikate
    for event_type, locations in event_type_usage.items():
        if len(locations) > 1:
            duplicates[event_type] = locations
    
    return dict(duplicates)


def generate_audit_report():
    """Generiere den Event-Audit Report."""
    print("🔍 EVENT EMISSION AUDIT - Battle System")
    print("=" * 50)
    
    # Finde alle Event-Emissionen
    emissions = find_event_emissions()
    event_types = find_event_type_usage()
    duplicates = analyze_duplicates(emissions)
    
    print(f"\n📊 GEFUNDENE EVENT-EMISSIONEN: {sum(len(events) for events in emissions.values())}")
    print(f"📁 DATEIEN MIT EVENTS: {len(emissions)}")
    print(f"🎯 EVENT-TYPES GEFUNDEN: {len(event_types)}")
    print(f"⚠️  DUPLIKATE GEFUNDEN: {len(duplicates)}")
    
    print("\n📋 DETAILLIERTE AUFLISTUNG:")
    print("-" * 30)
    
    for file_path, events in emissions.items():
        print(f"\n📄 {file_path}")
        for line_no, line_content in events:
            print(f"  L{line_no:3d}: {line_content}")
    
    if duplicates:
        print("\n⚠️  DUPLIKATE GEFUNDEN:")
        print("-" * 30)
        for event_type, locations in duplicates.items():
            print(f"\n🎯 {event_type}:")
            for location in locations:
                print(f"  - {location}")
    
    print("\n✅ AUDIT ABGESCHLOSSEN")
    
    # Speichere Report
    with open("engine/systems/battle/EVENT_AUDIT_RESULTS.md", "w") as f:
        f.write("# Event Emission Audit Results\n\n")
        f.write(f"**Gefundene Event-Emissionen:** {sum(len(events) for events in emissions.values())}\n")
        f.write(f"**Dateien mit Events:** {len(emissions)}\n")
        f.write(f"**Event-Types gefunden:** {len(event_types)}\n")
        f.write(f"**Duplikate gefunden:** {len(duplicates)}\n\n")
        
        f.write("## Detaillierte Auflistung\n\n")
        for file_path, events in emissions.items():
            f.write(f"### {file_path}\n\n")
            for line_no, line_content in events:
                f.write(f"- L{line_no}: {line_content}\n")
            f.write("\n")
        
        if duplicates:
            f.write("## Duplikate\n\n")
            for event_type, locations in duplicates.items():
                f.write(f"### {event_type}\n\n")
                for location in locations:
                    f.write(f"- {location}\n")
                f.write("\n")


if __name__ == "__main__":
    generate_audit_report()
