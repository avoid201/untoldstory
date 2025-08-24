#!/usr/bin/env python3
"""
Einfacher Test für das Battle System
Minimale Abhängigkeiten, direkte Implementierung
"""

import sys
import os
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Pfad hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Teste die grundlegenden Imports"""
    print("=== BASIC IMPORT TEST ===")
    
    try:
        # Teste Battle System
        from engine.systems.battle.battle import BattleState, BattleType, BattlePhase
        print("✅ Battle System Import erfolgreich")
        
        # Teste Turn Logic
        from engine.systems.battle.turn_logic import BattleAction, ActionType
        print("✅ Turn Logic Import erfolgreich")
        
        # Teste Monster System  
        from engine.systems.monster_instance import MonsterInstance, StatusCondition, MonsterSpecies, MonsterRank
        print("✅ Monster System Import erfolgreich")
        
        # Teste Stats System
        from engine.systems.stats import BaseStats, StatStages, GrowthCurve
        print("✅ Stats System Import erfolgreich")
        
        # Teste Moves System
        from engine.systems.moves import Move, EffectKind, MoveCategory, MoveTarget, MoveEffect
        print("✅ Moves System Import erfolgreich")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Fehler: {e}")
        return False
    except Exception as e:
        print(f"❌ Allgemeiner Fehler: {e}")
        return False

def test_enum_functionality():
    """Teste die Enum-Funktionalität"""
    print("\n=== ENUM FUNCTIONALITY TEST ===")
    
    try:
        from engine.systems.battle.turn_logic import ActionType
        from engine.systems.moves import MoveCategory
        
        # Teste ActionType.from_string
        action_type = ActionType.from_string("attack")
        if action_type == ActionType.ATTACK:
            print("✅ ActionType.from_string funktioniert")
        else:
            print("❌ ActionType.from_string fehlgeschlagen")
            return False
        
        # Teste MoveCategory.from_string  
        category = MoveCategory.from_string("phys")
        if category == MoveCategory.PHYSICAL:
            print("✅ MoveCategory.from_string funktioniert")
        else:
            print("❌ MoveCategory.from_string fehlgeschlagen")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Enum Test Fehler: {e}")
        return False

def test_monster_creation():
    """Teste die Monster-Erstellung"""
    print("\n=== MONSTER CREATION TEST ===")
    
    try:
        from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank
        from engine.systems.stats import BaseStats, GrowthCurve
        
        # Erstelle einfache Base Stats
        base_stats = BaseStats(hp=100, atk=50, def_=50, mag=30, res=30, spd=70)
        print("✅ BaseStats erstellt")
        
        # Erstelle Monster Species
        species = MonsterSpecies(
            id=1,
            name="TestMonster",
            era="present", 
            rank=MonsterRank.E,
            types=["Bestie"],
            base_stats=base_stats,
            growth_curve=GrowthCurve.MEDIUM_FAST,
            base_exp_yield=64,
            capture_rate=45,
            traits=[],
            learnset=[],
            evolution=None,
            description="Test Monster"
        )
        print("✅ MonsterSpecies erstellt")
        
        # Erstelle Monster Instance
        monster = MonsterInstance(species=species, level=5, nickname="Testi")
        print(f"✅ MonsterInstance erstellt: {monster.name} Lv.{monster.level}")
        print(f"   HP: {monster.current_hp}/{monster.max_hp}")
        print(f"   Stats: {monster.stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Monster Creation Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_move_creation():
    """Teste die Move-Erstellung"""
    print("\n=== MOVE CREATION TEST ===")
    
    try:
        from engine.systems.moves import Move, MoveEffect, EffectKind, MoveCategory, MoveTarget
        
        # Erstelle Move Effect
        effect = MoveEffect(
            kind=EffectKind.DAMAGE,
            power=40,
            chance=100.0
        )
        print("✅ MoveEffect erstellt")
        
        # Erstelle Move
        move = Move(
            id="test_tackle",
            name="Tackle",
            type="Bestie",
            category=MoveCategory.PHYSICAL,
            power=40,
            accuracy=95,
            pp=15,
            max_pp=15,
            priority=0,
            targeting=MoveTarget.ENEMY,
            effects=[effect],
            description="Test Move"
        )
        print(f"✅ Move erstellt: {move.name} (Power: {move.power})")
        
        return True
        
    except Exception as e:
        print(f"❌ Move Creation Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_battle_creation():
    """Teste die Battle-Erstellung"""
    print("\n=== BATTLE CREATION TEST ===")
    
    try:
        from engine.systems.battle.battle import BattleState, BattleType
        from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank
        from engine.systems.stats import BaseStats, GrowthCurve
        
        # Erstelle zwei Test-Monster
        base_stats = BaseStats(hp=100, atk=50, def_=50, mag=30, res=30, spd=70)
        
        species1 = MonsterSpecies(
            id=1, name="Monster1", era="present", rank=MonsterRank.E,
            types=["Bestie"], base_stats=base_stats, growth_curve=GrowthCurve.MEDIUM_FAST,
            base_exp_yield=64, capture_rate=45, traits=[], learnset=[], 
            evolution=None, description="Test Monster 1"
        )
        
        species2 = MonsterSpecies(
            id=2, name="Monster2", era="present", rank=MonsterRank.E,
            types=["Bestie"], base_stats=base_stats, growth_curve=GrowthCurve.MEDIUM_FAST,
            base_exp_yield=64, capture_rate=45, traits=[], learnset=[],
            evolution=None, description="Test Monster 2"  
        )
        
        player_monster = MonsterInstance(species=species1, level=5)
        enemy_monster = MonsterInstance(species=species2, level=5)
        
        print("✅ Test-Monster erstellt")
        
        # Erstelle Battle State
        battle_state = BattleState(
            player_team=[player_monster],
            enemy_team=[enemy_monster],
            battle_type=BattleType.WILD
        )
        print("✅ BattleState erstellt")
        print(f"   Phase: {battle_state.phase.value}")
        print(f"   Spieler: {battle_state.player_active.name}")
        print(f"   Gegner: {battle_state.enemy_active.name}")
        
        # Teste Battle Validierung
        if battle_state.validate_battle_state():
            print("✅ Battle-Validierung erfolgreich")
        else:
            print("❌ Battle-Validierung fehlgeschlagen")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Battle Creation Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Hauptfunktion"""
    print("🚀 Starte Simple Battle System Test...")
    print()
    
    success = True
    
    # Führe Tests aus
    success &= test_basic_imports()
    success &= test_enum_functionality() 
    success &= test_monster_creation()
    success &= test_move_creation()
    success &= test_battle_creation()
    
    print("\n" + "="*50)
    if success:
        print("🎉 ALLE TESTS ERFOLGREICH!")
        print("Das Battle System funktioniert grundlegend!")
    else:
        print("❌ EINIGE TESTS SIND FEHLGESCHLAGEN!")
        print("Überprüfe die Fehler oben.")
    print("="*50)
    
    return success

if __name__ == "__main__":
    main()