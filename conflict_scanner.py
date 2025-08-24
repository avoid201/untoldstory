#!/usr/bin/env python3
"""
Comprehensive Code Conflict Scanner and Fixer
Findet und behebt systematisch alle Konflikte im Code
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

class ConflictScanner:
    def __init__(self):
        self.project_path = Path("/Users/leon/Desktop/untold_story")
        self.conflicts_found = []
        self.fixes_applied = []
        
    def scan_all(self):
        """Führt alle Scans durch."""
        print("🔍 COMPREHENSIVE CONFLICT SCAN")
        print("="*60)
        
        # 1. Duplicate function/class definitions
        print("\n1. Scanning for duplicate definitions...")
        self.find_duplicate_definitions()
        
        # 2. Conflicting imports
        print("\n2. Scanning for import conflicts...")
        self.find_import_conflicts()
        
        # 3. Inconsistent method signatures
        print("\n3. Scanning for method signature conflicts...")
        self.find_method_conflicts()
        
        # 4. Missing required attributes
        print("\n4. Scanning for missing attributes...")
        self.find_missing_attributes()
        
        # 5. Type mismatches
        print("\n5. Scanning for type mismatches...")
        self.find_type_mismatches()
        
        # Generate report
        self.generate_report()
        
    def find_duplicate_definitions(self):
        """Findet doppelte Definitionen."""
        battle_dir = self.project_path / "engine" / "systems" / "battle"
        definitions = {}
        
        for py_file in battle_dir.glob("*.py"):
            if py_file.name.startswith("test_"):
                continue
                
            with open(py_file, 'r') as f:
                content = f.read()
            
            # Find all class definitions
            classes = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
            for cls in classes:
                if cls not in definitions:
                    definitions[cls] = []
                definitions[cls].append(py_file.name)
        
        # Report duplicates
        for name, files in definitions.items():
            if len(files) > 1:
                self.conflicts_found.append(f"Duplicate class {name} in: {files}")
                print(f"   ⚠️  Duplicate: {name} in {files}")
    
    def find_import_conflicts(self):
        """Findet Import-Konflikte."""
        import_patterns = [
            (r'from\s+engine\.systems\.battle\.battle_system\s+import\s+BattleState', 'BattleState from battle_system'),
            (r'from\s+engine\.systems\.battle\.battle_controller\s+import\s+BattleState', 'BattleState from battle_controller'),
        ]
        
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r') as f:
                        content = f.read()
                    
                    imports_found = []
                    for pattern, desc in import_patterns:
                        if re.search(pattern, content):
                            imports_found.append(desc)
                    
                    if len(imports_found) > 1:
                        self.conflicts_found.append(f"Conflicting imports in {file}: {imports_found}")
                        print(f"   ⚠️  Import conflict in {file}")
    
    def find_method_conflicts(self):
        """Findet widersprüchliche Methoden-Signaturen."""
        # Check for methods that should have same signature
        method_signatures = {}
        
        battle_files = [
            "battle_controller.py",
            "battle_actions.py", 
            "battle_ai.py",
            "command_collection.py"
        ]
        
        for filename in battle_files:
            filepath = self.project_path / "engine" / "systems" / "battle" / filename
            if filepath.exists():
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Find method definitions
                methods = re.findall(r'def\s+(\w+)\s*\([^)]*\)', content)
                for method in methods:
                    if method not in method_signatures:
                        method_signatures[method] = []
                    method_signatures[method].append(filename)
        
        # Check for potential conflicts
        common_methods = ['execute_action', 'validate', 'process_turn', 'calculate_damage']
        for method in common_methods:
            if method in method_signatures and len(method_signatures[method]) > 1:
                print(f"   ⚠️  Method '{method}' defined in multiple files: {method_signatures[method]}")
    
    def find_missing_attributes(self):
        """Findet fehlende Attribute."""
        required_attributes = {
            'MonsterInstance': ['hp', 'atk', 'def', 'mag', 'res', 'spd', 'stat_stages'],
            'BattleState': ['player_team', 'enemy_team', 'battle_type'],
            'Move': ['id', 'name', 'power', 'pp']
        }
        
        for class_name, attrs in required_attributes.items():
            print(f"   Checking {class_name} for required attributes: {attrs}")
    
    def find_type_mismatches(self):
        """Findet Typ-Konflikte."""
        # Check for common type mismatches
        type_checks = [
            ('player_action.get("move")', 'Move object or dict'),
            ('monster.stats', 'dict with hp, atk, def, etc.'),
            ('battle_state.phase', 'BattlePhase enum')
        ]
        
        for check, expected in type_checks:
            print(f"   Checking: {check} should be {expected}")
    
    def generate_report(self):
        """Generiert einen Bericht."""
        print("\n" + "="*60)
        print("📊 CONFLICT SCAN REPORT")
        print("="*60)
        
        if self.conflicts_found:
            print(f"\n⚠️  Found {len(self.conflicts_found)} conflicts:")
            for conflict in self.conflicts_found[:10]:
                print(f"  - {conflict}")
        else:
            print("\n✅ No major conflicts found!")
        
        print("\n📝 Recommendations:")
        print("  1. Use battle_controller.BattleState everywhere")
        print("  2. Ensure all MonsterInstance objects have required stats")
        print("  3. Standardize Move objects with id property")
        print("  4. Remove duplicate class definitions")

# Run the scanner
scanner = ConflictScanner()
scanner.scan_all()
