# Test-Dokumentation für Untold Story

## Übersicht

Dieses Verzeichnis enthält alle Tests für das 2D-RPG "Untold Story". Die Tests sind nach Funktionsbereichen organisiert und verwenden pytest als Test-Framework.

## Test-Struktur

```
tests/
├── conftest.py                    # Pytest-Konfiguration und gemeinsame Fixtures
├── systems/                       # Tests für Spielsysteme
│   ├── test_monster_system_comprehensive.py
│   ├── test_battle_system.py
│   ├── test_world_system.py
│   └── ...
├── battle/                        # Tests für Kampfsystem
│   ├── test_battle_fixes.py
│   ├── test_battle_ui.py
│   └── ...
├── story/                         # Tests für Story-System
│   ├── test_story_integration.py
│   ├── test_story_flow.py
│   └── ...
└── README.md                      # Diese Datei
```

## Test-Kategorien

### 1. Unit Tests (`@pytest.mark.unit`)
- Testen einzelne Funktionen und Klassen
- Schnelle Ausführung
- Keine externen Abhängigkeiten

### 2. Integration Tests (`@pytest.mark.integration`)
- Testen Zusammenspiel mehrerer Komponenten
- Mittlere Ausführungszeit
- Können externe Abhängigkeiten haben

### 3. System Tests (`@pytest.mark.systems`)
- Testen komplette Spielsysteme
- Langsamere Ausführung
- Vollständige Spielumgebung

### 4. Battle Tests (`@pytest.mark.battle`)
- Spezifisch für Kampfsystem
- Testen Kampf-Mechaniken und UI

### 5. World Tests (`@pytest.mark.world`)
- Testen Welt-Systeme
- Karten, NPCs, Interaktionen

## Test-Ausführung

### Alle Tests ausführen
```bash
# Im Projekt-Root-Verzeichnis
python -m pytest tests/

# Mit detaillierter Ausgabe
python -m pytest tests/ -v

# Mit Coverage-Report
python -m pytest tests/ --cov=engine --cov-report=html
```

### Spezifische Test-Kategorien
```bash
# Nur Unit Tests
python -m pytest tests/ -m unit

# Nur Battle Tests
python -m pytest tests/ -m battle

# Nur System Tests
python -m pytest tests/ -m systems
```

### Einzelne Test-Dateien
```bash
# Spezifische Test-Datei
python -m pytest tests/systems/test_monster_system.py

# Spezifischer Test
python -m pytest tests/systems/test_monster_system.py::TestMonsterSystem::test_monster_creation
```

### Mit Test-Runner
```bash
# Vollständige Test-Suite
python tools/testing_tools/test_runner.py

# Mit Bericht-Speicherung
python tools/testing_tools/test_runner.py --save-report
```

## Test-Fixtures

### pygame_init
```python
@pytest.fixture(scope="session")
def pygame_init():
    """Initialisiert Pygame für alle Tests"""
    pygame.init()
    yield
    pygame.quit()
```

### test_config
```python
@pytest.fixture(scope="function")
def test_config():
    """Gibt Test-Konfiguration zurück"""
    return TEST_CONFIG.copy()
```

### mock_screen
```python
@pytest.fixture(scope="function")
def mock_screen():
    """Erstellt einen Mock-Screen für Tests"""
    with patch('pygame.display.set_mode') as mock_display:
        mock_surface = Mock()
        mock_surface.get_size.return_value = (320, 180)
        mock_display.return_value = mock_surface
        yield mock_surface
```

### test_data
```python
@pytest.fixture(scope="function")
def test_data():
    """Test-Daten für Monster, Moves, etc."""
    return {
        "monsters": {...},
        "moves": {...},
        "types": {...}
    }
```

## Test-Best Practices

### 1. Test-Namen
- Verwende beschreibende Namen
- Format: `test_<was_getestet_wird>_<unter_was_bedingungen>`
- Beispiel: `test_monster_creation_with_valid_data`

### 2. Arrange-Act-Assert Pattern
```python
def test_monster_attack():
    # Arrange
    monster = MonsterInstance(test_monster, level=5)
    target = MonsterInstance(test_target, level=5)
    initial_hp = target.current_hp
    
    # Act
    damage = monster.attack(target)
    
    # Assert
    assert target.current_hp < initial_hp
    assert damage > 0
```

### 3. Mocking
- Mocke externe Abhängigkeiten
- Verwende `unittest.mock.patch`
- Teste isolierte Funktionalität

### 4. Edge Cases
- Teste ungültige Eingaben
- Teste Grenzwerte
- Teste Fehlerbehandlung

### 5. Test-Daten
- Verwende Fixtures für Test-Daten
- Halte Test-Daten minimal
- Verwende deterministische Werte

## Coverage-Analyse

### Coverage-Report generieren
```bash
python tools/testing_tools/coverage_analyzer.py --save-report
```

### Coverage-Ziele
- **Kritische Module**: ≥90%
- **Wichtige Module**: ≥80%
- **Gesamt-Projekt**: ≥70%

### Coverage-Interpretation
- **90%+**: Ausgezeichnet
- **80-89%**: Gut
- **70-79%**: Akzeptabel
- **<70%**: Verbesserung erforderlich

## Debugging Tests

### Fehlgeschlagene Tests debuggen
```bash
# Mit Debugger
python -m pytest tests/ -s --pdb

# Mit detaillierter Ausgabe
python -m pytest tests/ -vvv

# Einzelnen Test mit Debugger
python -m pytest tests/systems/test_monster_system.py::test_monster_creation --pdb
```

### Logging aktivieren
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_with_logging():
    logger.debug("Test startet")
    # Test-Logik
    logger.debug("Test beendet")
```

## Performance-Tests

### Langsame Tests markieren
```python
@pytest.mark.slow
def test_expensive_operation():
    # Langsamer Test
    pass
```

### Nur schnelle Tests
```bash
python -m pytest tests/ -m "not slow"
```

## Continuous Integration

### GitHub Actions
Tests werden automatisch bei jedem Push ausgeführt:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python -m pytest tests/ -v
```

### Pre-commit Hooks
```bash
# Tests vor Commit ausführen
pre-commit install

# Manuell ausführen
pre-commit run --all-files
```

## Test-Daten

### Test-Monster
```python
test_monster = {
    "id": "test_monster",
    "name": "Test Monster",
    "types": ["Normal"],
    "base_stats": {
        "hp": 50,
        "attack": 30,
        "defense": 25,
        "speed": 20
    },
    "moves": ["tackle", "growl"]
}
```

### Test-Moves
```python
test_moves = {
    "tackle": {
        "id": "tackle",
        "name": "Tackle",
        "type": "Normal",
        "power": 40,
        "accuracy": 100,
        "pp": 35
    }
}
```

## Häufige Probleme

### 1. Import-Fehler
```python
# Falsch
from engine.systems.monsters import Monster

# Richtig (in Tests)
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from engine.systems.monsters import Monster
```

### 2. Pygame-Initialisierung
```python
# Immer pygame_init Fixture verwenden
def test_with_pygame(pygame_init):
    # Test-Logik
    pass
```

### 3. Datei-Pfade
```python
# Verwende Path-Objekte
from pathlib import Path
test_file = PROJECT_ROOT / "tests" / "data" / "test.json"
```

## Nächste Schritte

### Kurzfristig
1. Alle kritischen Module auf ≥80% Coverage bringen
2. Edge Cases für bestehende Tests hinzufügen
3. Performance-Tests für langsame Operationen

### Mittelfristig
1. Integration-Tests für alle Spielsysteme
2. Automatisierte UI-Tests
3. Load-Tests für große Datenmengen

### Langfristig
1. Vollständige End-to-End-Tests
2. Cross-Platform-Tests
3. Accessibility-Tests

## Kontakt

Bei Fragen zu Tests oder Coverage:
- Erstelle ein Issue im Repository
- Dokumentiere den Fehler detailliert
- Füge relevante Logs hinzu

---

**Letzte Aktualisierung**: {{ datetime.now().strftime('%Y-%m-%d') }}
**Test-Coverage**: {{ coverage_percentage }}%
**Status**: {{ test_status }}
