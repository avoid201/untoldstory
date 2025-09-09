# Battle System Archive

## Archivierte Dateien

### dqm_formulas_old.py
- **Datum der Archivierung**: 2025-01-27
- **Grund**: Vereinheitlichung aller Damage Calculator zu einem System
- **Ersetzt durch**: `engine/systems/unified_damage_calculator.py`
- **Status**: DEPRECATED - Alle Funktionen wurden in UnifiedDamageCalculator integriert

### damage_calc.py
- **Status**: Bereits entfernt (nur noch .pyc vorhanden)
- **Ersetzt durch**: `engine/systems/unified_damage_calculator.py`

## Migration

Alle Damage-Berechnungen verwenden jetzt den `UnifiedDamageCalculator` als Single Source of Truth:

```python
from engine.systems.unified_damage_calculator import unified_damage_calculator

# Einheitliche Damage-Berechnung
result = unified_damage_calculator.calculate_damage(attacker, defender, move)
```

## Backward Compatibility

Die alten Klassen sind noch verfügbar für Backward Compatibility:
- `DQMCalculator` - delegiert an UnifiedDamageCalculator
- `DQMSkillCalculator` - delegiert an UnifiedDamageCalculator  
- `DQMDamageStage` - delegiert an UnifiedDamageCalculator

## Vorteile der Vereinheitlichung

1. **Single Source of Truth**: Alle Damage-Berechnungen an einem Ort
2. **Konsistente DQM-Formeln**: Authentische Dragon Quest Monsters Mechaniken
3. **Performance-Tracking**: Eingebaute Performance-Metriken
4. **Erweiterbarkeit**: Einfache Erweiterung um neue Damage-Typen
5. **Wartbarkeit**: Weniger Code-Duplikation
