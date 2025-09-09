# 🧪 Isolated Test Suite - Untold Story

## 📋 Übersicht

Diese Test-Suite ist vollständig vom Produktivcode isoliert und organisiert Tests nach Typ:

- **`unit/`** - Unit Tests für einzelne Komponenten
- **`integration/`** - Integration Tests für System-Interaktionen  
- **`performance/`** - Performance und Benchmark Tests
- **`fixtures/`** - Test-Daten und Fixtures

## 🚀 Verwendung

### Alle Tests ausführen
```bash
cd tests_isolated
python3 run_tests.py
```

### Nur Unit Tests
```bash
python3 run_tests.py --type unit
```

### Nur Integration Tests
```bash
python3 run_tests.py --type integration
```

### Mit Coverage
```bash
python3 run_tests.py --coverage
```

### Mit pytest direkt
```bash
python3 -m pytest unit/ -v
python3 -m pytest integration/ -v
```

## 📁 Struktur

```
tests_isolated/
├── __init__.py              # Package initialization
├── conftest.py              # Pytest configuration
├── run_tests.py             # Standalone test runner
├── README.md                # Diese Datei
├── unit/                    # Unit Tests
│   ├── __init__.py
│   └── test_simple_imports.py
├── integration/             # Integration Tests
│   ├── __init__.py
│   ├── test_final.py
│   ├── test_integration.py
│   └── ... (weitere Tests)
├── performance/             # Performance Tests
│   ├── __init__.py
│   └── (leer - Tests archiviert)
└── fixtures/                # Test Fixtures
    ├── __init__.py
    └── conftest.py
```

## 🔧 Konfiguration

### Pytest Markers
- `@pytest.mark.unit` - Unit Tests
- `@pytest.mark.integration` - Integration Tests  
- `@pytest.mark.performance` - Performance Tests
- `@pytest.mark.slow` - Langsame Tests

### Fixtures
- `project_root_path` - Projekt-Root-Pfad
- `engine_path` - Engine-Package-Pfad
- `data_path` - Daten-Verzeichnis-Pfad

## 📊 Test-Status

### ✅ Funktionsfähige Tests
- **Unit Tests**: 5 Tests (Import-Validierung)
- **Integration Tests**: 32 Tests laufen erfolgreich

### ⚠️ Archivierte Tests
Viele Tests wurden archiviert, da sie veraltete Module verwenden:
- `archive/test_isolation_2025-09-03/` - Veraltete Tests

### 🔄 Migration erforderlich
Tests müssen aktualisiert werden, um neue Module zu verwenden:
- `engine.systems.unified_damage_calculator` statt `engine.systems.battle.dqm_formulas`
- `engine.systems.battle.status_processor` statt `engine.systems.battle.status_effects_dqm`
- `engine.systems.types.TypeChart` statt `engine.systems.types.TypeSystem`

## 🎯 Nächste Schritte

1. **Neue Tests erstellen** für aktuelle Module
2. **Veraltete Tests migrieren** zu neuen APIs
3. **Performance-Tests** für aktuelle Battle-System
4. **Coverage-Reporting** implementieren

## 📝 Notizen

- Alle Tests verwenden absolute Imports von `engine.*`
- Projekt-Root wird automatisch zu `sys.path` hinzugefügt
- Tests laufen unabhängig vom Produktivcode
- Klare Trennung zwischen Test- und Produktions-Umgebung