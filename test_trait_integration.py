#!/usr/bin/env python3
"""
Test der Monster-Trait-Integration in der Schadensberechnung
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'engine'))

from engine.systems.battle.damage_calc import DamageCalculator, DamageResult
from engine.systems.battle.monster_traits import get_trait_database
from engine.systems.monster_instance import MonsterInstance
from engine.systems.monsters import MonsterSpecies
from engine.systems.moves import Move

def create_test_monster(name, traits=None, stats=None):
    """Erstelle ein Test-Monster."""
    if traits is None:
        traits = []
    if stats is None:
        stats = {'hp': 100, 'atk': 50, 'def': 50, 'mag': 50, 'res': 50, 'spd': 50}
    
    species = MonsterSpecies(
        name=name,
        types=['Normal'],
        base_stats=stats,
        moves=[],
        description="Test monster"
    )
    
    monster = MonsterInstance(species, level=10)
    monster.traits = traits
    monster.current_hp = monster.max_hp
    
    return monster

def create_test_move(name, power=50, category='phys', move_type='Normal'):
    """Erstelle einen Test-Move."""
    return Move(
        name=name,
        power=power,
        accuracy=100,
        pp=10,
        category=category,
        type=move_type,
        description="Test move"
    )

def test_metal_body_trait():
    """Teste den Metal Body Trait."""
    print("🧪 Teste Metal Body Trait...")
    
    # Monster ohne Traits
    attacker = create_test_monster("Attacker", stats={'hp': 100, 'atk': 100, 'def': 50, 'mag': 50, 'res': 50, 'spd': 50})
    
    # Monster mit Metal Body Trait
    defender = create_test_monster("Metal Defender", traits=["Metal Body"], stats={'hp': 100, 'atk': 50, 'def': 50, 'mag': 50, 'res': 50, 'spd': 50})
    
    move = create_test_move("Strong Attack", power=100)
    
    calculator = DamageCalculator()
    result = calculator.calculate(attacker, defender, move)
    
    print(f"  Schaden ohne Metal Body: {result.damage}")
    print(f"  Schaden mit Metal Body: {result.damage}")
    print(f"  Modifiers: {result.modifiers_applied}")
    
    # Metal Body sollte den Schaden auf 0-1 reduzieren
    assert result.damage <= 2, f"Metal Body sollte Schaden reduzieren, aber Schaden ist {result.damage}"
    print("  ✅ Metal Body funktioniert korrekt!")

def test_critical_master_trait():
    """Teste den Critical Master Trait."""
    print("🧪 Teste Critical Master Trait...")
    
    # Monster mit Critical Master Trait
    attacker = create_test_monster("Critical Attacker", traits=["Critical Master"], stats={'hp': 100, 'atk': 100, 'def': 50, 'mag': 50, 'res': 50, 'spd': 50})
    
    # Monster ohne besondere Traits
    defender = create_test_monster("Normal Defender", stats={'hp': 100, 'atk': 50, 'def': 50, 'mag': 50, 'res': 50, 'spd': 50})
    
    move = create_test_move("Normal Attack", power=50)
    
    calculator = DamageCalculator()
    
    # Teste mehrere Angriffe, um Critical Hits zu finden
    critical_hits = 0
    total_tests = 100
    
    for i in range(total_tests):
        result = calculator.calculate(attacker, defender, move)
        if result.is_critical:
            critical_hits += 1
    
    critical_rate = critical_hits / total_tests
    print(f"  Critical Hit Rate: {critical_rate:.3f} ({critical_hits}/{total_tests})")
    
    # Critical Master sollte die Crit-Chance erhöhen
    assert critical_rate > 0.03, f"Critical Master sollte Crit-Chance erhöhen, aber Rate ist {critical_rate}"
    print("  ✅ Critical Master funktioniert korrekt!")

def test_attack_boost_trait():
    """Teste den Attack Boost Trait."""
    print("🧪 Teste Attack Boost Trait...")
    
    # Monster ohne Traits
    attacker_normal = create_test_monster("Normal Attacker", stats={'hp': 100, 'atk': 100, 'def': 50, 'mag': 50, 'res': 50, 'spd': 50})
    
    # Monster mit Attack Boost Trait
    attacker_boosted = create_test_monster("Boosted Attacker", traits=["Attack Boost"], stats={'hp': 100, 'atk': 100, 'def': 50, 'mag': 50, 'res': 50, 'spd': 50})
    
    defender = create_test_monster("Normal Defender", stats={'hp': 100, 'atk': 50, 'def': 50, 'mag': 50, 'res': 50, 'spd': 50})
    
    move = create_test_move("Physical Attack", power=50, category='phys')
    
    calculator = DamageCalculator()
    
    # Teste ohne Trait
    result_normal = calculator.calculate(attacker_normal, defender, move)
    
    # Teste mit Trait
    result_boosted = calculator.calculate(attacker_boosted, defender, move)
    
    print(f"  Schaden ohne Attack Boost: {result_normal.damage}")
    print(f"  Schaden mit Attack Boost: {result_boosted.damage}")
    print(f"  Modifiers normal: {result_normal.modifiers_applied}")
    print(f"  Modifiers boosted: {result_boosted.modifiers_applied}")
    
    # Attack Boost sollte den Schaden erhöhen
    assert result_boosted.damage > result_normal.damage, "Attack Boost sollte Schaden erhöhen"
    print("  ✅ Attack Boost funktioniert korrekt!")

def test_defense_boost_trait():
    """Teste den Defense Boost Trait."""
    print("🧪 Teste Defense Boost Trait...")
    
    attacker = create_test_monster("Attacker", stats={'hp': 100, 'atk': 100, 'def': 50, 'mag': 50, 'res': 50, 'spd': 50})
    
    # Monster ohne Traits
    defender_normal = create_test_monster("Normal Defender", stats={'hp': 100, 'atk': 50, 'def': 100, 'mag': 50, 'res': 50, 'spd': 50})
    
    # Monster mit Defense Boost Trait
    defender_boosted = create_test_monster("Boosted Defender", traits=["Defense Boost"], stats={'hp': 100, 'atk': 50, 'def': 100, 'mag': 50, 'res': 50, 'spd': 50})
    
    move = create_test_move("Physical Attack", power=50, category='phys')
    
    calculator = DamageCalculator()
    
    # Teste ohne Trait
    result_normal = calculator.calculate(attacker, defender_normal, move)
    
    # Teste mit Trait
    result_boosted = calculator.calculate(attacker, defender_boosted, move)
    
    print(f"  Schaden ohne Defense Boost: {result_normal.damage}")
    print(f"  Schaden mit Defense Boost: {result_boosted.damage}")
    print(f"  Modifiers normal: {result_normal.modifiers_applied}")
    print(f"  Modifiers boosted: {result_boosted.modifiers_applied}")
    
    # Defense Boost sollte den Schaden reduzieren
    assert result_boosted.damage < result_normal.damage, "Defense Boost sollte Schaden reduzieren"
    print("  ✅ Defense Boost funktioniert korrekt!")

def test_elemental_resistances():
    """Teste Elementar-Resistanz Traits."""
    print("🧪 Teste Elementar-Resistanz Traits...")
    
    attacker = create_test_monster("Attacker", stats={'hp': 100, 'atk': 100, 'def': 50, 'mag': 50, 'res': 50, 'spd': 50})
    
    # Monster ohne Traits
    defender_normal = create_test_monster("Normal Defender", stats={'hp': 100, 'atk': 50, 'def': 50, 'mag': 50, 'res': 50, 'spd': 50})
    
    # Monster mit Fire Breath Guard Trait
    defender_fire_guard = create_test_monster("Fire Guard Defender", traits=["Fire Breath Guard"], stats={'hp': 100, 'atk': 50, 'def': 50, 'mag': 50, 'res': 50, 'spd': 50})
    
    # Feuer-Angriff
    fire_move = create_test_move("Fire Attack", power=50, move_type='fire')
    
    calculator = DamageCalculator()
    
    # Teste ohne Trait
    result_normal = calculator.calculate(attacker, defender_normal, fire_move)
    
    # Teste mit Fire Breath Guard
    result_guarded = calculator.calculate(attacker, defender_fire_guard, fire_move)
    
    print(f"  Schaden ohne Fire Breath Guard: {result_normal.damage}")
    print(f"  Schaden mit Fire Breath Guard: {result_guarded.damage}")
    print(f"  Modifiers normal: {result_normal.modifiers_applied}")
    print(f"  Modifiers guarded: {result_guarded.modifiers_applied}")
    
    # Fire Breath Guard sollte den Schaden reduzieren
    assert result_guarded.damage < result_normal.damage, "Fire Breath Guard sollte Feuer-Schaden reduzieren"
    print("  ✅ Elementar-Resistanz funktioniert korrekt!")

def test_counter_trait():
    """Teste den Counter Trait."""
    print("🧪 Teste Counter Trait...")
    
    attacker = create_test_monster("Attacker", stats={'hp': 100, 'atk': 100, 'def': 50, 'mag': 50, 'res': 50, 'spd': 50})
    
    # Monster mit Counter Trait
    defender = create_test_monster("Counter Defender", traits=["Counter"], stats={'hp': 100, 'atk': 50, 'def': 50, 'mag': 50, 'res': 50, 'spd': 50})
    
    move = create_test_move("Normal Attack", power=50)
    
    calculator = DamageCalculator()
    
    # Teste mehrere Angriffe, um Counter zu finden
    counter_activations = 0
    total_tests = 100
    
    for i in range(total_tests):
        result = calculator.calculate(attacker, defender, move)
        if hasattr(defender, 'pending_counter') and defender.pending_counter:
            counter_activations += 1
            defender.pending_counter = None  # Reset für nächsten Test
    
    counter_rate = counter_activations / total_tests
    print(f"  Counter Activation Rate: {counter_rate:.3f} ({counter_activations}/{total_tests})")
    
    # Counter sollte gelegentlich aktiviert werden
    assert counter_rate > 0.1, f"Counter sollte aktiviert werden, aber Rate ist {counter_rate}"
    print("  ✅ Counter Trait funktioniert korrekt!")

def main():
    """Hauptfunktion für alle Tests."""
    print("🚀 Starte Monster-Trait-Integration Tests...\n")
    
    try:
        test_metal_body_trait()
        print()
        
        test_critical_master_trait()
        print()
        
        test_attack_boost_trait()
        print()
        
        test_defense_boost_trait()
        print()
        
        test_elemental_resistances()
        print()
        
        test_counter_trait()
        print()
        
        print("🎉 Alle Tests erfolgreich abgeschlossen!")
        
    except Exception as e:
        print(f"❌ Test fehlgeschlagen: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
