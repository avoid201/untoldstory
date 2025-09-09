# 📦 Untold Story - Code Archive

## 📅 Archivierung vom: $(date +%Y-%m-%d)

Dieses Verzeichnis enthält archivierten Code, der aus dem Hauptprojekt entfernt wurde, um Duplikate zu eliminieren und die Architektur zu verbessern.

## 📁 Struktur

- `duplicate_code/` - Duplizierte Funktionen und Klassen
- `deprecated/` - Veraltete Implementierungen
- `backups/` - Vollständige Backups vor großen Änderungen

## ⚠️ WICHTIG

Dieser Code sollte NICHT mehr verwendet werden! Für alle Funktionalitäten gibt es bereinigte Versionen im Hauptprojekt.

## 📋 Archivierte Dateien

### Duplicate Code:
1. `types_refactored.py` - Redundante Type-System Implementierung
2. `BattleResult` Definitionen aus mehreren Dateien
3. Doppelte `BattleHUD` Implementierungen

### Deprecated:
- Alte Battle-System Implementierungen
- Unvollständige Calculator-Systeme

## 🔄 Wiederherstellung

Falls Code wiederhergestellt werden muss:
```bash
cp archive/duplicate_code/[filename] engine/[original_path]/
```

## 📝 Änderungsprotokoll

| Datum | Datei | Grund | Ersetzt durch |
|-------|-------|-------|---------------|
| 2024-12-28 | types_refactored.py | Duplikat | engine/systems/types.py |
| 2024-12-28 | BattleResult (multiple) | Mehrfach-Definition | engine/systems/battle/battle_enums.py |
