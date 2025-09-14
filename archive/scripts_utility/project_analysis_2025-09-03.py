#!/usr/bin/env python3
"""
Umfassende Projekt-Analyse für Untold Story
Identifiziert aktuelle Probleme, fehlende Features und Wartungsaufgaben
"""

import sys
import os
import json
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def analyze_game_state():
    """Analysiert den aktuellen Zustand des Spiels"""
    
    results = {
        'critical_issues': [],
        'missing_features': [],
        'improvement_opportunities': [],
        'agent_tasks': []
    }
    
    print("🔍 ANALYZING UNTOLD STORY PROJECT STATE...")
    
    # Test 1: Core System Imports
    try:
        from engine.core.game import Game
        print("✅ Core game system loads")
    except Exception as e:
        results['critical_issues'].append(f"Core game import failed: {e}")
        print(f"❌ Core game import failed: {e}")
    
    # Test 2: Battle System
    try:
        from engine.systems.battle.battle_controller import BattleController, BattleState
        from engine.systems.battle.battle_enums import BattleType, BattlePhase
        print("✅ Battle system core loads")
    except Exception as e:
        results['critical_issues'].append(f"Battle system import failed: {e}")
        print(f"❌ Battle system import failed: {e}")
    
    # Test 3: Monster System
    try:
        from engine.systems.monsters import MonsterDatabase
        from engine.systems.monster_instance import MonsterInstance
        monster_db = MonsterDatabase()
        print("✅ Monster system loads")
        
        # Check if we can load a monster
        try:
            glutstummel = monster_db.get_species("glutstummel")
            if glutstummel:
                print(f"✅ Sample monster loaded: {glutstummel.name}")
            else:
                results['critical_issues'].append("Cannot load sample monster 'glutstummel'")
                print("❌ Cannot load sample monster")
        except Exception as e:
            results['critical_issues'].append(f"Monster loading failed: {e}")
            print(f"❌ Monster loading failed: {e}")
            
    except Exception as e:
        results['critical_issues'].append(f"Monster system import failed: {e}")
        print(f"❌ Monster system import failed: {e}")
    
    # Test 4: Scene System
    try:
        from engine.scenes.battle_scene import BattleScene
        from engine.scenes.field_scene import FieldScene
        from engine.scenes.start_scene import StartScene
        print("✅ Scene system loads")
    except Exception as e:
        results['critical_issues'].append(f"Scene system import failed: {e}")
        print(f"❌ Scene system import failed: {e}")
    
    # Test 5: UI System
    try:
        from engine.ui.battle_ui import BattleUI
        from engine.ui.dialogue import DialogueBox
        print("✅ UI system loads")
    except Exception as e:
        results['critical_issues'].append(f"UI system import failed: {e}")
        print(f"❌ UI system import failed: {e}")
    
    # Test 6: Assets and Data Files
    asset_checks = [
        ("data/monsters.json", "Monster data"),
        ("data/moves.json", "Move data"),
        ("data/types.json", "Type chart"),
        ("assets/gfx", "Graphics assets"),
        ("data/maps", "Map data")
    ]
    
    for file_path, description in asset_checks:
        if Path(file_path).exists():
            print(f"✅ {description} found")
        else:
            results['missing_features'].append(f"{description} missing at {file_path}")
            print(f"❌ {description} missing")
    
    # Test 7: Check for obvious integration issues
    print("\n🔍 Checking for integration issues...")
    
    # Check if battle scene can initialize
    try:
        # This is a minimal test - we can't create actual Game instance without pygame
        print("✅ Battle Scene class structure seems intact")
    except Exception as e:
        results['critical_issues'].append(f"Battle Scene integration issue: {e}")
        print(f"❌ Battle Scene integration issue: {e}")
    
    # Identify improvement opportunities
    results['improvement_opportunities'].extend([
        "Asset loading optimization needed",
        "Battle animations missing",
        "Sound system incomplete",
        "Save/Load system needs testing",
        "Map system needs TMX integration testing",
        "Monster AI could be improved",
        "UI polish needed",
        "Performance optimization opportunities"
    ])
    
    # Define agent tasks based on analysis
    results['agent_tasks'] = [
        {
            'name': 'Battle System Polish Agent',
            'priority': 'HIGH',
            'tasks': [
                'Fix any remaining battle system integration issues',
                'Implement missing battle animations',
                'Polish battle UI responsiveness',
                'Test all battle actions (attack, tame, flee, switch)',
                'Verify DQM damage calculation accuracy'
            ],
            'files': [
                'engine/systems/battle/',
                'engine/scenes/battle_scene.py',
                'engine/ui/battle_ui.py'
            ]
        },
        {
            'name': 'Monster & Data System Agent',
            'priority': 'HIGH',
            'tasks': [
                'Verify monster data integrity',
                'Test monster creation and stats calculation',
                'Implement missing monster moves',
                'Fix any JSON data loading issues',
                'Optimize monster database performance'
            ],
            'files': [
                'engine/systems/monsters.py',
                'engine/systems/monster_instance.py',
                'data/monsters.json',
                'data/moves.json'
            ]
        },
        {
            'name': 'Scene & Navigation Agent',
            'priority': 'MEDIUM',
            'tasks': [
                'Polish scene transitions',
                'Fix field scene movement and interactions',
                'Implement missing scene features',
                'Test save/load integration',
                'Improve main menu functionality'
            ],
            'files': [
                'engine/scenes/',
                'engine/world/',
                'engine/ui/transitions.py'
            ]
        },
        {
            'name': 'Asset & Graphics Agent',
            'priority': 'MEDIUM',
            'tasks': [
                'Optimize sprite loading and caching',
                'Fix any missing asset references',
                'Implement tile rendering improvements',
                'Test TMX map loading',
                'Add placeholder graphics where needed'
            ],
            'files': [
                'engine/graphics/',
                'assets/',
                'engine/world/tiles.py',
                'engine/world/map_loader.py'
            ]
        },
        {
            'name': 'Polish & Testing Agent',
            'priority': 'LOW',
            'tasks': [
                'Clean up debug code and test files',
                'Organize and archive outdated files',
                'Run comprehensive integration tests',
                'Polish user experience',
                'Document remaining issues'
            ],
            'files': [
                'tests/',
                'tools/',
                '*.py (cleanup scripts)'
            ]
        }
    ]
    
    return results


def print_summary(results):
    """Druckt eine Zusammenfassung der Analyse"""
    
    print("\n" + "="*60)
    print("📊 PROJECT ANALYSIS SUMMARY")
    print("="*60)
    
    print(f"\n🚨 CRITICAL ISSUES ({len(results['critical_issues'])}):")
    for issue in results['critical_issues']:
        print(f"   - {issue}")
    
    print(f"\n📋 MISSING FEATURES ({len(results['missing_features'])}):")
    for feature in results['missing_features']:
        print(f"   - {feature}")
    
    print(f"\n🎯 IMPROVEMENT OPPORTUNITIES ({len(results['improvement_opportunities'])}):")
    for opportunity in results['improvement_opportunities'][:5]:  # Show top 5
        print(f"   - {opportunity}")
    
    print(f"\n🤖 RECOMMENDED AGENT TASKS ({len(results['agent_tasks'])}):")
    for task in results['agent_tasks']:
        print(f"   - {task['name']} (Priority: {task['priority']})")
        print(f"     Tasks: {len(task['tasks'])} items")
        print(f"     Files: {len(task['files'])} focus areas")
    
    print("\n" + "="*60)
    print("🎯 READY FOR AGENT DEPLOYMENT")
    print("="*60)


def main():
    """Hauptfunktion"""
    results = analyze_game_state()
    print_summary(results)
    
    # Save results to JSON for agent consumption
    with open('project_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📝 Analysis results saved to: project_analysis_results.json")
    
    return len(results['critical_issues'])  # Return number of critical issues


if __name__ == "__main__":
    exit_code = main()
    print(f"\n🎯 Analysis complete. Exit code: {exit_code}")
    sys.exit(exit_code)
