# Archive Manifest - Untold Story

## Übersicht
Dieses Manifest listet alle archivierten Dateien im Projekt auf, die während der Refaktorierung des Battle-Systems und anderer Systeme erstellt wurden.

**Erstellt:** 2025-01-03  
**Letzte Aktualisierung:** 2025-09-03

## Battle System Archive

### Hauptsysteme
- `archive/battle/dqm_formulas_old.py` - Alte DQM-Formeln (ersetzt durch unified_damage_calculator.py)
- `archive/battle_system_old_20250903_173259/battle_system.py` - Altes Battle-System (ersetzt durch battle_controller.py)
- `archive/battle_system_old_20250903_173259/battle_actions.py` - Alte Battle-Actions (ersetzt durch action_processor.py)
- `archive/battle_system_old_20250903_173259/battle_events.py` - Alte Battle-Events (ersetzt durch event_processor.py)

### Status System
- `archive/battle_old_2025_01_03/status_effects_dqm.py` - Alte Status-Effekte (ersetzt durch status_processor.py)
- `archive/deprecated/battle_system/status_system_wrapper.py` - Status-System Wrapper (nicht mehr benötigt)

### Legacy Cleanup (2025-09-03)
- `archive/legacy_cleanup_20250903_180215/legacy_battle_ui_compatibility.py`
- `archive/legacy_cleanup_20250903_180215/legacy_monster_instance_methods.py`
- `archive/legacy_cleanup_20250903_180215/legacy_stats_damage_calculator.py`
- `archive/legacy_cleanup_20250903_180215/legacy_unified_damage_calculator_wrappers.py`
- `archive/legacy_cleanup_20250903_180215/legacy_dqm_integration_functions.py`

### Deprecated Battle System
- `archive/deprecated/battle_system/battle_events.py`
- `archive/deprecated/battle_system/command_collection.py`
- `archive/deprecated/battle_system/meat_item_bridge.py`
- `archive/deprecated/battle_system/monster_traits_complex.py`

## 3v3 System Backup
- `archive/3v3_system_backup/battle_formation.py` - 3v3 Formation System (nicht implementiert)
- `archive/3v3_system_backup/target_system.py` - 3v3 Target System (nicht implementiert)

## Tension System
- `archive/tension_system_backup/battle_tension.py` - Tension System (nicht implementiert)

## Duplicate Code
- `archive/duplicate_code/BattleResult_from_battle_manager.py`
- `archive/duplicate_code/BattleResult_from_battle_scene.py`
- `archive/duplicate_code/types_refactored.py`

## Test Files
- `archive/backup_battle_cleanup_20250824/battle/simple_compatibility_test.py`
- `archive/backup_battle_cleanup_20250824/battle/test_battle_compatibility.py`
- `archive/backup_battle_cleanup_20250824_214926/simple_compatibility_test.py`
- `archive/backup_battle_cleanup_20250824_214926/test_battle_compatibility.py`
- `archive/backups/backup_20250824_205019/battle/simple_compatibility_test.py`
- `archive/backups/backup_20250824_205019/battle/test_battle_compatibility.py`
- `archive/old_tests/test_battle_refactored.py`

## Other Systems
- `archive/conditions_old.py` - Alte Conditions (ersetzt durch status_processor.py)
- `archive/old_battle_systems/simple_battle_manager.py` - Einfacher Battle Manager
- `archive/completed_tasks/examples/item_usage_examples.py` - Item Usage Examples

## Archivierungsrichtlinien

### Header Format
Alle archivierten Dateien enthalten einen Header im Format:
```python
# ARCHIVED: [Datum] - Replaced by [neue_datei]
```

### Archivierungsgrund
- **Refaktorierung:** Dateien wurden durch neue, bessere Implementierungen ersetzt
- **Duplikate:** Doppelte Funktionalität wurde entfernt
- **Legacy:** Alte Systeme wurden durch neue ersetzt
- **Nicht implementiert:** Features die nicht umgesetzt wurden

### Wichtige Hinweise
- KEINE Dateien wurden gelöscht ohne Archivierung
- Alle Archive sind in `archive/` mit entsprechender Unterstruktur
- Bei Fragen zu archivierten Dateien, siehe entsprechende README-Dateien
- Archivierte Dateien dienen nur als Referenz und sollten nicht mehr verwendet werden

## Battle UI Modularization (2025-09-03)

### Modulare Battle UI
- `archive/battle_ui_modularization_20250903_235053/battle_ui_old.py` - Original monolithische battle_ui.py (2029 Zeilen)
- `archive/battle_ui_modularization_20250903_235053/ARCHIVE_README.md` - Archivierungs-Dokumentation
- `archive/battle_ui_modularization_20250903_235053/MODULARIZATION_REPORT.md` - Detaillierter Bericht
- `archive/battle_ui_modularization_20250903_235053/MODULAR_STRUCTURE.md` - Struktur-Übersicht

**Grund:** Modularisierung der monolithischen battle_ui.py (2029 Zeilen, Komplexität 258) in 5 wartbare Module
**Ergebnis:** 80% Reduktion der Komplexität, SOLID Principles befolgt, API-kompatibel

## Statistik
- **Gesamt archivierte Python-Dateien:** 32
- **Battle-System Dateien:** 15
- **Battle UI Dateien:** 1
- **Test-Dateien:** 7
- **Legacy/Duplicate Dateien:** 9

---
*Dieses Manifest wird bei jeder größeren Archivierung aktualisiert.*
