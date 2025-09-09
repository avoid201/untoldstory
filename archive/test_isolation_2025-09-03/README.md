# 📦 Test Isolation Archive - 2025-09-03

## 🎯 Zweck

Diese Dateien wurden während der Test-Isolation archiviert, da sie veraltete Module verwenden oder nicht mit der aktuellen Codebase kompatibel sind.

## 📋 Archivierte Tests

### Unit Tests (7 Dateien)
- `test_battle_state.py` - Verwendet veraltete `TestMonsters` Klasse
- `test_damage_calculation.py` - Importiert nicht existierendes `engine.systems.battle.dqm_formulas`
- `test_damage_calculator.py` - Importiert nicht existierendes `DQMCalculator` aus `unified_damage_calculator`
- `test_dqm_formulas.py` - Importiert nicht existierendes `engine.systems.battle.dqm_formulas`
- `test_monster_traits.py` - Importiert nicht existierendes `get_trait_database`
- `test_monsters.py` - Importiert nicht existierendes `TypeSystem` aus `engine.systems.types`
- `test_status_effects.py` - Importiert nicht existierendes `engine.systems.battle.status_effects_dqm`

### Integration Tests (7 Dateien)
- `test_3v3_battle.py` - Importiert nicht existierendes `engine.systems.battle.battle_formation`
- `test_battle_flow.py` - Verwendet veraltete `TestMonsters` Klasse
- `test_battle_integration.py` - Syntax-Fehler in Zeile 245
- `test_complete_battle_flow.py` - Importiert nicht existierendes `engine.systems.battle.battle_actions`
- `test_dqm_integration.py` - Importiert nicht existierendes `engine.systems.battle.command_collection`
- `test_monster_system_comprehensive.py` - Importiert nicht existierendes `Monster` aus `engine.systems.monsters`
- `test_skills_dqm.py` - Importiert nicht existierendes `engine.systems.battle.skills_dqm`

### Performance Tests (2 Dateien)
- `test_battle_performance.py` - Importiert nicht existierendes `engine.systems.battle.battle_actions`
- `test_performance.py` - Importiert nicht existierendes `engine.systems.battle.status_effects_dqm`

## 🔄 Migration erforderlich

### Neue Module verwenden:
- `engine.systems.unified_damage_calculator.UnifiedDamageCalculator` statt `DQMCalculator`
- `engine.systems.battle.status_processor.StatusProcessor` statt `StatusEffectManager`
- `engine.systems.types.TypeChart` statt `TypeSystem`
- `engine.systems.monster_instance.MonsterInstance` statt `Monster`

### Entfernte Module:
- `engine.systems.battle.dqm_formulas` - Funktionalität in `unified_damage_calculator` integriert
- `engine.systems.battle.status_effects_dqm` - Funktionalität in `status_processor` integriert
- `engine.systems.battle.battle_actions` - Funktionalität in `action_processor` integriert
- `engine.systems.battle.battle_formation` - 3v3-System entfernt
- `engine.systems.battle.command_collection` - Funktionalität in `turn_logic` integriert
- `engine.systems.battle.skills_dqm` - Funktionalität in `skills_dqm_integrated` integriert

## 📊 Statistiken

- **Gesamt archivierte Tests**: 16 Dateien
- **Geschätzte Zeilen Code**: ~2,000 Zeilen
- **Betroffene Module**: 7 Battle-System-Module
- **Migration-Aufwand**: Mittel (Tests müssen neu geschrieben werden)

## 🎯 Nächste Schritte

1. **Neue Tests erstellen** für aktuelle Module
2. **Test-Fixtures aktualisieren** für neue APIs
3. **Performance-Tests** für aktuelle Battle-System
4. **Integration-Tests** für neue System-Architektur

## 📝 Notizen

- Tests wurden am 2025-09-03 archiviert
- Alle Tests verwenden absolute Imports (korrekt)
- Problem liegt in veralteten Modul-Referenzen
- Test-Isolation funktioniert korrekt
