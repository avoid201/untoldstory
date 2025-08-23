# Archive - Alte und ungenutzte Dateien

## Zweck
Dieser Ordner enthält alte, ungenutzte oder überholte Dateien, die aus dem Hauptprojekt entfernt wurden, aber für historische Zwecke oder als Referenz aufbewahrt werden.

## Struktur

### old_tests/
Enthält alte Test- und Debug-Dateien vom TMX-Integration-Prozess:
- `analyze_gid_problem.py` - Analyse des GID-Mapping-Problems
- `debug_*.py` - Verschiedene Debug-Skripte
- `fix_*.py` - Temporäre Fix-Skripte
- `test_*.py` - Alte Test-Dateien
- `integrate_*.py` - Alte Integrations-Versuche
- `patch_*.py` - Patch-Skripte
- `quick_*.py` - Quick-Test-Skripte
- `tmx_integration_complete.py` - Alter Integrationsversuch
- `visual_tmx_test.py` - Visueller TMX-Test

## Hinweise
- Diese Dateien werden NICHT mehr aktiv genutzt
- Bei Bedarf können sie als Referenz dienen
- Neue Tests sollten im `tests/` Ordner erstellt werden
- Neue Tools sollten im `tools/` Ordner erstellt werden

## Wiederherstellung
Falls eine Datei wieder benötigt wird:
```bash
# Beispiel: Datei zurück ins Hauptverzeichnis
mv archive/old_tests/DATEINAME.py ../
```

---
*Archiviert: August 2025*