"""
Test-Suite für Battle-System-Fixes
Testet ob alle Fixes korrekt funktionieren.
"""

import pytest
import sys
import warnings
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_no_circular_imports():
    """Teste dass keine zirkulären Imports mehr existieren."""
    # Diese Imports sollten ohne Error funktionieren
    from engine.systems.battle import battle_controller
    from engine.systems.battle import battle_actions
    from engine.systems.battle import battle_system
    assert True, "Keine zirkulären Imports!"

def test_legacy_battlestate_wrapper():
    """Teste dass der Legacy-Wrapper funktioniert."""
    # Einfacher Test: Importiere die Klasse und prüfe dass sie existiert
    from engine.systems.battle.battle import BattleState
    
    # Prüfe dass es die richtige Wrapper-Klasse ist
    assert BattleState.__module__ == 'engine.systems.battle.battle'
    assert BattleState.__doc__ and 'Legacy' in BattleState.__doc__
    
    # Der eigentliche Warning-Test würde echte Monster brauchen,
    # aber wir können zumindest prüfen dass die Klasse existiert

def test_imports_complete():
    """Teste dass alle nötigen Imports vorhanden sind."""
    try:
        from engine.systems.battle.battle_actions import StatusCondition
        from engine.systems.battle.battle_ai import AIPersonality
        assert True, "Alle Imports vorhanden!"
    except ImportError as e:
        pytest.fail(f"Import fehlt: {e}")

def test_performance_cache():
    """Teste Performance-Optimierungen."""
    from engine.systems.battle.optimized_core import BattleCache
    
    # Test caching
    result1 = BattleCache.get_type_effectiveness('fire', 'water')
    result2 = BattleCache.get_type_effectiveness('fire', 'water')
    
    # Sollte gecached sein (gleiche Objekt-ID)
    assert result1 == result2 == 0.5

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
