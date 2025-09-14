"""
Simple test to verify that imports work correctly in the isolated test environment.
"""

import pytest
import sys
from pathlib import Path

def test_project_root_in_path():
    """Test that project root is in Python path."""
    project_root = Path(__file__).parent.parent.parent
    assert str(project_root) in sys.path

def test_engine_imports():
    """Test that we can import from engine package."""
    try:
        from engine.systems.battle import BattleState, BattleType, BattlePhase
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import from engine.systems.battle: {e}")

def test_monster_instance_import():
    """Test that we can import MonsterInstance."""
    try:
        from engine.systems.monster_instance import MonsterInstance
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import MonsterInstance: {e}")

def test_unified_damage_calculator_import():
    """Test that we can import UnifiedDamageCalculator."""
    try:
        from engine.systems.unified_damage_calculator import UnifiedDamageCalculator
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import UnifiedDamageCalculator: {e}")

def test_types_import():
    """Test that we can import from types module."""
    try:
        from engine.systems.types import TypeChart
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import TypeChart: {e}")
