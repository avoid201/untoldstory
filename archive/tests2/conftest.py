#!/usr/bin/env python3
"""
Pytest-Konfiguration für Untold Story Tests
Gemeinsame Fixtures und Test-Setup
"""

import pytest
import pygame
import sys
import os
from pathlib import Path
from typing import Generator, Dict, Any
from unittest.mock import Mock, patch

# Projekt-Root zum Python-Pfad hinzufügen
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Test-Konfiguration
TEST_CONFIG = {
    "screen_width": 320,
    "screen_height": 180,
    "test_save_file": "test_save.json",
    "test_data_dir": "test_data"
}

@pytest.fixture(scope="session")
def pygame_init():
    """Initialisiert Pygame für alle Tests"""
    pygame.init()
    yield
    pygame.quit()

@pytest.fixture(scope="session")
def test_config():
    """Gibt Test-Konfiguration zurück"""
    return TEST_CONFIG.copy()

@pytest.fixture(scope="function")
def mock_screen():
    """Erstellt einen Mock-Screen für Tests"""
    with patch('pygame.display.set_mode') as mock_display:
        mock_surface = Mock()
        mock_surface.get_size.return_value = (320, 180)
        mock_display.return_value = mock_surface
        yield mock_surface

@pytest.fixture(scope="function")
def mock_clock():
    """Erstellt einen Mock-Clock für Tests"""
    with patch('pygame.time.Clock') as mock_clock_class:
        mock_clock = Mock()
        mock_clock.tick.return_value = 16  # 60 FPS
        mock_clock_class.return_value = mock_clock
        yield mock_clock

@pytest.fixture(scope="function")
def test_data():
    """Test-Daten für Monster, Moves, etc."""
    return {
        "monsters": {
            "test_monster": {
                "id": "test_monster",
                "name": "Test Monster",
                "types": ["Normal"],
                "base_stats": {"hp": 50, "attack": 30, "defense": 25, "speed": 20},
                "moves": ["tackle", "growl"]
            }
        },
        "moves": {
            "tackle": {
                "id": "tackle",
                "name": "Tackle",
                "type": "Normal",
                "power": 40,
                "accuracy": 100,
                "pp": 35
            },
            "growl": {
                "id": "growl",
                "name": "Growl",
                "type": "Normal",
                "power": 0,
                "accuracy": 100,
                "pp": 40,
                "effect": "attack_down"
            }
        },
        "types": {
            "Normal": {
                "name": "Normal",
                "effectiveness": {
                    "Rock": 0.5,
                    "Ghost": 0.0
                }
            }
        }
    }

@pytest.fixture(scope="function")
def mock_file_system():
    """Mock für Dateisystem-Operationen"""
    with patch('builtins.open') as mock_open, \
         patch('pathlib.Path.exists') as mock_exists, \
         patch('pathlib.Path.mkdir') as mock_mkdir:
        
        mock_exists.return_value = True
        mock_mkdir.return_value = None
        
        # Mock für JSON-Dateien
        mock_file = Mock()
        mock_file.__enter__.return_value = mock_file
        mock_file.__exit__.return_value = None
        mock_file.read.return_value = '{"test": "data"}'
        mock_file.write.return_value = None
        
        mock_open.return_value = mock_file
        
        yield {
            'open': mock_open,
            'exists': mock_exists,
            'mkdir': mock_mkdir
        }

@pytest.fixture(scope="function")
def clean_test_environment():
    """Bereinigt Test-Umgebung nach jedem Test"""
    # Vor dem Test
    yield
    
    # Nach dem Test - Cleanup
    # Lösche temporäre Test-Dateien
    test_files = [
        "test_save.json",
        "test_save_backup.json",
        "test_log.txt"
    ]
    
    for test_file in test_files:
        test_path = PROJECT_ROOT / test_file
        if test_path.exists():
            test_path.unlink()

@pytest.fixture(scope="function")
def deterministic_random():
    """Stellt deterministische Zufallszahlen für Tests bereit"""
    with patch('random.seed') as mock_seed, \
         patch('random.randint') as mock_randint, \
         patch('random.choice') as mock_choice:
        
        # Setze Seed für reproduzierbare Tests
        mock_seed.return_value = None
        
        # Mock für deterministische Zufallszahlen
        mock_randint.return_value = 50  # Immer 50
        mock_choice.side_effect = lambda seq: seq[0] if seq else None
        
        yield {
            'seed': mock_seed,
            'randint': mock_randint,
            'choice': mock_choice
        }

# Test-Markierungen
def pytest_configure(config):
    """Konfiguriert pytest-Markierungen"""
    config.addinivalue_line(
        "markers", "slow: mark test as slow to run"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "battle: mark test as battle system test"
    )
    config.addinivalue_line(
        "markers", "world: mark test as world system test"
    )

# Test-Sammlung anpassen
def pytest_collection_modifyitems(config, items):
    """Passt Test-Sammlung an"""
    for item in items:
        # Markiere Tests basierend auf Dateinamen
        if "battle" in item.nodeid:
            item.add_marker(pytest.mark.battle)
        elif "world" in item.nodeid:
            item.add_marker(pytest.mark.world)
        elif "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)
