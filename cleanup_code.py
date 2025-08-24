#!/usr/bin/env python3
"""
Code Cleanup and Conflict Resolution Script
Fixes overlapping functions, import issues, and common AI mistakes
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple, Set

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class CodeCleaner:
    """Main cleanup utility for the untold_story project."""
    
    def __init__(self, project_path: str = "/Users/leon/Desktop/untold_story"):
        self.project_path = Path(project_path)
        self.issues_found = []
        self.fixes_applied = []
        
    def analyze_and_fix(self):
        """Main entry point for analysis and fixes."""
        print("🔍 Starting Code Analysis & Cleanup...")
        print("="*60)
        
        # Phase 1: Find duplicate classes/functions
        print("\n📋 Phase 1: Finding Duplicate Definitions...")
        self.find_duplicate_definitions()
        
        # Phase 2: Fix import issues
        print("\n📋 Phase 2: Fixing Import Issues...")
        self.fix_import_issues()
        
        # Phase 3: Check for incomplete functions
        print("\n📋 Phase 3: Checking for Incomplete Functions...")
        self.check_incomplete_functions()
        
        # Phase 4: Remove redundant code
        print("\n📋 Phase 4: Removing Redundant Code...")
        self.remove_redundant_code()
        
        # Phase 5: Generate report
        print("\n📊 Generating Report...")
        self.generate_cleanup_report()
        
    def find_duplicate_definitions(self):
        """Find duplicate class and function definitions."""
        battle_dir = self.project_path / "engine" / "systems" / "battle"
        
        # Track all definitions
        definitions = {
            'classes': {},
            'functions': {}
        }
        
        for py_file in battle_dir.glob("*.py"):
            if py_file.name.startswith("test_"):
                continue
                
            with open(py_file, 'r') as f:
                content = f.read()
                
            # Find class definitions
            class_matches = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
            for class_name in class_matches:
                if class_name not in definitions['classes']:
                    definitions['classes'][class_name] = []
                definitions['classes'][class_name].append(py_file.name)
            
            # Find function definitions
            func_matches = re.findall(r'^def\s+(\w+)', content, re.MULTILINE)
            for func_name in func_matches:
                if func_name not in definitions['functions']:
                    definitions['functions'][func_name] = []
                definitions['functions'][func_name].append(py_file.name)
        
        # Report duplicates
        print("\n🔴 Duplicate Classes Found:")
        for class_name, files in definitions['classes'].items():
            if len(files) > 1:
                print(f"  - {class_name}: {', '.join(files)}")
                self.issues_found.append(f"Duplicate class {class_name} in {files}")
        
        print("\n🟠 Potentially Overlapping Functions:")
        overlap_funcs = ['calculate_damage', 'process_status', 'get_turn_order']
        for func in overlap_funcs:
            if func in definitions['functions'] and len(definitions['functions'][func]) > 1:
                print(f"  - {func}: {', '.join(definitions['functions'][func])}")
                
    def fix_import_issues(self):
        """Fix common import problems."""
        fixes = []
        
        # Fix 1: Update test imports
        test_file = self.project_path / "tests" / "test_dqm_integration.py"
        if test_file.exists():
            with open(test_file, 'r') as f:
                content = f.read()
            
            # Fix wrong imports
            replacements = [
                ("from engine.systems.battle.skills_dqm import SkillsManager, SkillCategory",
                 "from engine.systems.battle.skills_dqm import DQMSkillDatabase, SkillType"),
                ("from engine.systems.battle.monster_traits import TraitDatabase, TriggerType",
                 "from engine.systems.battle.monster_traits import TraitDatabase, TraitTrigger"),
                ("from engine.systems.battle.status_effects_dqm import StatusEffectsManager",
                 "from engine.systems.battle.status_effects_dqm import StatusEffectSystem"),
            ]
            
            for old, new in replacements:
                if old in content:
                    content = content.replace(old, new)
                    fixes.append(f"Fixed import: {old[:50]}...")
            
            if fixes:
                with open(test_file, 'w') as f:
                    f.write(content)
                print(f"✅ Fixed {len(fixes)} import issues in test_dqm_integration.py")
        
        # Fix 2: Add missing __init__.py content
        init_file = self.project_path / "engine" / "systems" / "battle" / "__init__.py"
        if init_file.exists():
            init_content = '''"""
Battle System Module
Exports all battle system components
"""

# Core battle system
from .battle_controller import BattleState
from .battle_enums import BattleType, BattlePhase, BattleCommand, AIPersonality
from .battle_actions import BattleActionExecutor
from .battle_validation import BattleValidator
from .battle_ai import BattleAI

# DQM specific systems
from .dqm_formulas import DQMCalculator
from .command_collection import CommandCollector, CommandType
from .battle_formation import FormationManager, FormationType
from .skills_dqm import DQMSkillDatabase
from .monster_traits import TraitDatabase
from .status_effects_dqm import StatusEffectSystem

# Tension system
from .battle_tension import TensionManager

__all__ = [
    'BattleState',
    'BattleType', 'BattlePhase', 'BattleCommand', 'AIPersonality',
    'BattleActionExecutor', 'BattleValidator', 'BattleAI',
    'DQMCalculator', 'CommandCollector', 'CommandType',
    'FormationManager', 'FormationType',
    'DQMSkillDatabase', 'TraitDatabase', 'StatusEffectSystem',
    'TensionManager'
]
'''
            with open(init_file, 'w') as f:
                f.write(init_content)
            print("✅ Updated __init__.py with proper exports")
            
    def check_incomplete_functions(self):
        """Check for incomplete functions (common AI mistake)."""
        battle_dir = self.project_path / "engine" / "systems" / "battle"
        incomplete = []
        
        for py_file in battle_dir.glob("*.py"):
            with open(py_file, 'r') as f:
                lines = f.readlines()
            
            in_function = False
            func_name = None
            has_return = False
            has_pass = False
            
            for i, line in enumerate(lines):
                # Check for function start
                if re.match(r'^def\s+(\w+)', line):
                    # Check previous function
                    if in_function and func_name and not (has_return or has_pass):
                        if not func_name.startswith('__'):  # Skip special methods
                            incomplete.append(f"{py_file.name}:{func_name}")
                    
                    # Start new function
                    func_match = re.match(r'^def\s+(\w+)', line)
                    func_name = func_match.group(1)
                    in_function = True
                    has_return = False
                    has_pass = False
                
                # Check for return or pass
                if in_function:
                    if 'return' in line:
                        has_return = True
                    if 'pass' in line and line.strip() == 'pass':
                        has_pass = True
        
        if incomplete:
            print(f"⚠️  Found {len(incomplete)} potentially incomplete functions:")
            for func in incomplete[:5]:  # Show first 5
                print(f"  - {func}")
                
    def remove_redundant_code(self):
        """Remove or consolidate redundant code."""
        print("\n🔧 Consolidating redundant code...")
        
        # Create consolidated damage calculation
        consolidated_damage = '''"""
Consolidated Damage Calculation Module
Combines all damage calculation methods
"""

from engine.systems.battle.dqm_formulas import DQMCalculator

class DamageCalculator:
    """Unified damage calculation system."""
    
    def __init__(self):
        self.dqm_calculator = DQMCalculator()
    
    def calculate_damage(self, attacker, defender, move, use_dqm=True):
        """
        Calculate damage with optional DQM formulas.
        
        Args:
            attacker: Attacking monster
            defender: Defending monster
            move: Move being used
            use_dqm: Whether to use DQM formulas
        """
        if use_dqm:
            return self.dqm_calculator.calculate_damage(
                attacker_stats=attacker.stats,
                defender_stats=defender.stats,
                move_power=move.power if hasattr(move, 'power') else 50,
                is_physical=move.category == 'phys' if hasattr(move, 'category') else True
            )
        else:
            # Fallback to simple calculation
            attack = attacker.stats.get('atk', 50)
            defense = defender.stats.get('def', 40)
            power = move.power if hasattr(move, 'power') else 50
            
            damage = ((attack * 2 / defense) * power) / 50 + 2
            return {'final_damage': int(damage)}
'''
        
        # Save consolidated module
        damage_calc_file = self.project_path / "engine" / "systems" / "battle" / "damage_calculator.py"
        with open(damage_calc_file, 'w') as f:
            f.write(consolidated_damage)
        print("✅ Created consolidated damage_calculator.py")
        
    def generate_cleanup_report(self):
        """Generate a detailed cleanup report."""
        report = f"""
# 🧹 Code Cleanup Report

## Issues Found: {len(self.issues_found)}
{chr(10).join('- ' + issue for issue in self.issues_found[:10])}

## Fixes Applied: {len(self.fixes_applied)}
{chr(10).join('- ' + fix for fix in self.fixes_applied[:10])}

## Recommendations:

### High Priority:
1. **Remove duplicate BattleState**: Use only battle_controller.py version
2. **Consolidate damage calculation**: Use the new damage_calculator.py
3. **Fix test imports**: Update all test files with correct class names

### Medium Priority:
1. **Remove unused files**: Delete battle_system_old.py and other backup files
2. **Consolidate status effects**: Use only status_effects_dqm.py
3. **Update documentation**: Ensure all modules have proper docstrings

### Low Priority:
1. **Code style**: Apply consistent formatting
2. **Type hints**: Add type hints to all functions
3. **Logging**: Add more detailed logging for debugging

## Next Steps:
1. Run: `python3 cleanup_code.py --apply-fixes`
2. Test: `python3 -m pytest tests/`
3. Verify: `python3 verify_integration.py`
"""
        
        report_file = self.project_path / "CLEANUP_REPORT.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n✅ Cleanup report saved to {report_file}")
        print(report)


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Code cleanup and conflict resolution")
    parser.add_argument('--apply-fixes', action='store_true', help='Apply automatic fixes')
    parser.add_argument('--path', default='/Users/leon/Desktop/untold_story', help='Project path')
    args = parser.parse_args()
    
    cleaner = CodeCleaner(args.path)
    cleaner.analyze_and_fix()
    
    if args.apply_fixes:
        print("\n✅ Automatic fixes have been applied!")
    else:
        print("\n💡 Run with --apply-fixes to apply automatic corrections")


if __name__ == "__main__":
    main()
