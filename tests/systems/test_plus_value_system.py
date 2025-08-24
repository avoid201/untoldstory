#!/usr/bin/env python3
"""
Test Suite für das Plus-Value System
Testet alle neuen Features der MonsterInstance-Klasse
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank
from engine.systems.stats import BaseStats, GrowthCurve
from engine.systems.moves import Move, move_registry


def create_test_species() -> MonsterSpecies:
    """Erstellt eine Test-Spezies für Tests."""
    base_stats = BaseStats(
        hp=50, atk=45, def_=40, mag=35, res=30, spd=55
    )
    
    learnset = [
        (1, "Tackle"),
        (5, "Growl"),
        (10, "Water Gun"),
        (15, "Bubble"),
        (20, "Water Pulse"),
        (25, "Aqua Jet"),
        (30, "Hydro Pump")
    ]
    
    return MonsterSpecies(
        id=999,
        name="TestMonster",
        rank=MonsterRank.C,
        types=["Wasser", "Bestie"],
        base_stats=base_stats,
        growth_curve=GrowthCurve.MEDIUM_FAST,
        base_exp_yield=64,
        learnset=learnset
    )


def test_plus_value_initialization():
    """Testet die Initialisierung des Plus-Value-Systems."""
    print("🧪 Teste Plus-Value Initialisierung...")
    
    species = create_test_species()
    
    # Test Standard-Initialisierung
    monster = MonsterInstance(species, level=10)
    assert monster.plus_value == 0, f"Standard Plus-Value sollte 0 sein, ist aber {monster.plus_value}"
    
    # Test mit Plus-Value
    monster_plus = MonsterInstance(species, level=10, plus_value=25)
    assert monster_plus.plus_value == 25, f"Plus-Value sollte 25 sein, ist aber {monster_plus.plus_value}"
    
    # Test Grenzwerte
    monster_max = MonsterInstance(species, level=10, plus_value=150)
    assert monster_max.plus_value == 99, f"Plus-Value sollte auf 99 begrenzt werden, ist aber {monster_max.plus_value}"
    
    monster_min = MonsterInstance(species, level=10, plus_value=-10)
    assert monster_min.plus_value == 0, f"Plus-Value sollte auf 0 begrenzt werden, ist aber {monster_min.plus_value}"
    
    print("✅ Plus-Value Initialisierung erfolgreich!")


def test_max_level_calculation():
    """Testet die Berechnung des maximalen Levels."""
    print("🧪 Teste Max-Level Berechnung...")
    
    species = create_test_species()
    
    # Test verschiedene Plus-Values
    test_cases = [
        (0, 100),    # +0 = Level 100
        (10, 105),   # +10 = Level 105
        (20, 110),   # +20 = Level 110
        (50, 125),   # +50 = Level 125
        (99, 149),   # +99 = Level 149
    ]
    
    for plus_value, expected_max in test_cases:
        monster = MonsterInstance(species, level=1, plus_value=plus_value)
        actual_max = monster.max_level
        assert actual_max == expected_max, f"Plus-Value {plus_value}: Erwartet Level {expected_max}, bekommen {actual_max}"
    
    print("✅ Max-Level Berechnung erfolgreich!")


def test_plus_value_display():
    """Testet die Plus-Value-Anzeige."""
    print("🧪 Teste Plus-Value Anzeige...")
    
    species = create_test_species()
    
    # Test verschiedene Plus-Values
    test_cases = [
        (0, ""),      # +0 = leerer String
        (5, "+5"),    # +5 = "+5"
        (25, "+25"),  # +25 = "+25"
        (99, "+99"),  # +99 = "+99"
    ]
    
    for plus_value, expected_display in test_cases:
        monster = MonsterInstance(species, level=1, plus_value=plus_value)
        actual_display = monster.plus_value_display
        assert actual_display == expected_display, f"Plus-Value {plus_value}: Erwartet '{expected_display}', bekommen '{actual_display}'"
    
    print("✅ Plus-Value Anzeige erfolgreich!")


def test_plus_value_manipulation():
    """Testet das Erhöhen und Verringern von Plus-Values."""
    print("🧪 Teste Plus-Value Manipulation...")
    
    species = create_test_species()
    monster = MonsterInstance(species, level=1, plus_value=25)
    
    # Test Erhöhung
    assert monster.increase_plus_value(5), "Erhöhung um 5 sollte erfolgreich sein"
    assert monster.plus_value == 30, f"Plus-Value sollte 30 sein, ist aber {monster.plus_value}"
    
    # Test Verringerung
    assert monster.decrease_plus_value(3), "Verringerung um 3 sollte erfolgreich sein"
    assert monster.plus_value == 27, f"Plus-Value sollte 27 sein, ist aber {monster.plus_value}"
    
    # Test Grenzwerte
    assert not monster.increase_plus_value(100), "Erhöhung über 99 sollte fehlschlagen"
    assert monster.plus_value == 27, "Plus-Value sollte unverändert bleiben"
    
    assert not monster.decrease_plus_value(100), "Verringerung unter 0 sollte fehlschlagen"
    assert monster.plus_value == 27, "Plus-Value sollte unverändert bleiben"
    
    print("✅ Plus-Value Manipulation erfolgreich!")


def test_stat_calculation_with_plus_value():
    """Testet die Stat-Berechnung mit Plus-Value-Boni."""
    print("🧪 Teste Stat-Berechnung mit Plus-Value...")
    
    species = create_test_species()
    
    # Test ohne Plus-Value
    monster_base = MonsterInstance(species, level=50, plus_value=0)
    base_stats = monster_base.calculate_stats()
    
    # Test mit Plus-Value
    monster_plus = MonsterInstance(species, level=50, plus_value=30)
    plus_stats = monster_plus.calculate_stats()
    
    # Plus-Value 30 sollte +6 HP und +9% andere Stats geben
    hp_bonus = plus_stats["hp"] - base_stats["hp"]
    atk_bonus_percent = ((plus_stats["atk"] / base_stats["atk"]) - 1) * 100
    
    assert hp_bonus >= 6, f"HP-Bonus sollte mindestens 6 sein, ist aber {hp_bonus}"
    assert atk_bonus_percent >= 9, f"ATK-Bonus sollte mindestens 9% sein, ist aber {atk_bonus_percent:.1f}%"
    
    print("✅ Stat-Berechnung mit Plus-Value erfolgreich!")


def test_experience_gain_with_plus_value():
    """Testet das Erfahrungssystem mit Plus-Value."""
    print("🧪 Teste Erfahrungssystem mit Plus-Value...")
    
    species = create_test_species()
    
    # Monster mit Plus-Value 20 (Max Level 110)
    monster = MonsterInstance(species, level=105, plus_value=20)
    
    # Versuche über Max Level zu kommen
    result = monster.gain_exp(1000000)  # Sehr viel EXP
    
    assert result["max_level_reached"], "Max Level sollte erreicht werden"
    assert monster.level == 110, f"Level sollte 110 sein, ist aber {monster.level}"
    assert monster.exp == monster.species.growth_curve.get_exp_for_level(110), "EXP sollte auf Max Level gesetzt werden"
    
    print("✅ Erfahrungssystem mit Plus-Value erfolgreich!")


def test_automatic_plus_value_increase():
    """Testet die automatische Plus-Value-Erhöhung alle 10 Level."""
    print("🧪 Teste automatische Plus-Value-Erhöhung...")
    
    species = create_test_species()
    monster = MonsterInstance(species, level=5, plus_value=0)
    
    # Level 5 → 10 (sollte +1 Plus-Value geben)
    result = monster.gain_exp(100000)  # Genug EXP für Level 10
    
    assert result["leveled_up"], "Level-Up sollte stattfinden"
    assert result["plus_value_increased"], "Plus-Value sollte erhöht werden"
    assert monster.plus_value == 1, f"Plus-Value sollte 1 sein, ist aber {monster.plus_value}"
    
    print("✅ Automatische Plus-Value-Erhöhung erfolgreich!")


def test_save_load_compatibility():
    """Testet die Speicher-/Lade-Kompatibilität."""
    print("🧪 Teste Speicher-/Lade-Kompatibilität...")
    
    species = create_test_species()
    original_monster = MonsterInstance(species, level=50, plus_value=25)
    
    # Speichern
    save_data = original_monster.to_dict()
    
    # Prüfen ob plus_value gespeichert wurde
    assert "plus_value" in save_data, "plus_value sollte im Speicherformat enthalten sein"
    assert save_data["plus_value"] == 25, f"Gespeicherter Plus-Value sollte 25 sein, ist aber {save_data['plus_value']}"
    
    # Laden
    loaded_monster = MonsterInstance.from_dict(save_data, species)
    
    # Prüfen ob alle Werte korrekt geladen wurden
    assert loaded_monster.plus_value == 25, f"Geladener Plus-Value sollte 25 sein, ist aber {loaded_monster.plus_value}"
    assert loaded_monster.level == 50, f"Geladenes Level sollte 50 sein, ist aber {loaded_monster.level}"
    
    print("✅ Speicher-/Lade-Kompatibilität erfolgreich!")


def test_legacy_save_compatibility():
    """Testet die Kompatibilität mit alten Speicherdateien ohne plus_value."""
    print("🧪 Teste Legacy-Speicher-Kompatibilität...")
    
    species = create_test_species()
    
    # Alte Speicherdatei ohne plus_value
    legacy_data = {
        "species_id": 999,
        "level": 50,
        "exp": 100000,
        "ivs": {"hp": 15, "atk": 20, "def": 18, "mag": 12, "res": 14, "spd": 22},
        "evs": {"hp": 0, "atk": 0, "def": 0, "mag": 0, "res": 0, "spd": 0},
        "nature": "Hardy",
        "current_hp": 120,
        "status": "none",
        "moves": [],
        "traits": [],
        "held_item": None,
        "original_trainer": None,
        "capture_location": None,
        "capture_level": 5
    }
    
    # Laden sollte funktionieren
    loaded_monster = MonsterInstance.from_dict(legacy_data, species)
    
    # Plus-Value sollte auf 0 gesetzt werden
    assert loaded_monster.plus_value == 0, f"Legacy-Monster sollte Plus-Value 0 haben, hat aber {loaded_monster.plus_value}"
    assert loaded_monster.level == 50, f"Legacy-Monster sollte Level 50 haben, hat aber {loaded_monster.level}"
    
    print("✅ Legacy-Speicher-Kompatibilität erfolgreich!")


def test_move_learning_with_plus_value():
    """Testet das Move-Learning-System mit Plus-Value."""
    print("🧪 Teste Move-Learning mit Plus-Value...")
    
    species = create_test_species()
    monster = MonsterInstance(species, level=1, plus_value=0)
    
    # Starte mit Level 1
    assert len(monster.moves) >= 1, "Monster sollte mindestens 1 Move haben"
    
    # Level auf 15 erhöhen (sollte 4 Moves lernen)
    result = monster.gain_exp(100000)
    
    assert result["leveled_up"], "Level-Up sollte stattfinden"
    assert len(monster.moves) >= 4, f"Monster sollte mindestens 4 Moves haben, hat aber {len(monster.moves)}"
    
    print("✅ Move-Learning mit Plus-Value erfolgreich!")


def test_repr_and_debugging():
    """Testet die Debug-Ausgaben und Repräsentation."""
    print("🧪 Teste Debug-Ausgaben...")
    
    species = create_test_species()
    monster = MonsterInstance(species, level=50, plus_value=25)
    
    # Test __repr__
    repr_string = repr(monster)
    assert "TestMonster" in repr_string, "Repr sollte Spezies-Name enthalten"
    assert "plus_value=25" in repr_string, "Repr sollte Plus-Value enthalten"
    assert "hp=" in repr_string, "Repr sollte HP-Information enthalten"
    
    # Test EXP-Progress
    progress = monster.get_exp_progress()
    assert 0.0 <= progress <= 1.0, f"EXP-Progress sollte zwischen 0.0 und 1.0 liegen, ist aber {progress}"
    
    # Test EXP bis nächstes Level
    exp_to_next = monster.get_exp_to_next_level()
    assert exp_to_next >= 0, f"EXP bis nächstes Level sollte >= 0 sein, ist aber {exp_to_next}"
    
    print("✅ Debug-Ausgaben erfolgreich!")


def run_all_tests():
    """Führt alle Tests aus."""
    print("🚀 Starte Plus-Value System Tests...\n")
    
    try:
        test_plus_value_initialization()
        test_max_level_calculation()
        test_plus_value_display()
        test_plus_value_manipulation()
        test_stat_calculation_with_plus_value()
        test_experience_gain_with_plus_value()
        test_automatic_plus_value_increase()
        test_save_load_compatibility()
        test_legacy_save_compatibility()
        test_move_learning_with_plus_value()
        test_repr_and_debugging()
        
        print("\n🎉 Alle Tests erfolgreich bestanden!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
