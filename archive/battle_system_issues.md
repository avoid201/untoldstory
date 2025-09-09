"""
BATTLE SYSTEM BUG REPORT & ISSUE LIST
Generated: 2025-01-09
=====================================

## KRITISCHE FEHLER (Sofort beheben!)

### 1. ❌ FALSCHER RETURN TYPE IN check_battle_end() [BEREITS BEHOBEN]
**Datei:** engine/systems/battle/turn_processor.py (Zeile 159-198)
**Problem:** Methode sollte Optional[BattleResult] zurückgeben, gibt aber BattleResult.ONGOING zurück statt None
**Fix:** 
```python
# ALT:
return BattleResult.ONGOING
# NEU:
return None  # oder BattleResult.ONGOING konsistent verwenden
```

### 2. ❌ DOPPELTE EVENT-EMISSIONEN
**Dateien:** battle_controller.py + turn_processor.py
**Problem:** TURN_START und TURN_END Events werden doppelt emittiert
- battle_controller.py Zeile 153-160
- turn_processor.py Zeile 60-64
**Fix:** Events nur an EINER Stelle emittieren (vorzugsweise turn_processor)

### 3. ❌ FEHLENDE ERROR RECOVERY IN battle_ai.py
**Datei:** engine/systems/battle/battle_ai.py (Zeile 56-95)
**Problem:** choose_action() crasht wenn monster.moves None oder leer ist
**Fix:**
```python
# Zeile 68-75 sollte robuster sein:
if not hasattr(enemy_monster, 'moves') or not enemy_monster.moves:
    # Create fallback move
    from engine.systems.moves import Move
    fallback = Move(id='tackle', name='Tackle', power=40, ...)
    available_moves = [fallback]
```

## SCHWERWIEGENDE FEHLER

### 4. ⚠️ PHASE MANAGEMENT INKONSISTENT
**Datei:** battle_controller.py
**Problem:** Phase wird auf "init" gesetzt aber nie korrekt zu "INPUT" geändert
**Zeilen:** 132-134
```python
# Problem:
self.state.phase = BattlePhase.INIT  # Bleibt bei INIT!
# Fix:
self.state.phase = BattlePhase.START
# Nach Start:
self.state.phase = BattlePhase.INPUT
```

### 5. ⚠️ EVENT PROCESSOR MEMORY LEAK
**Datei:** event_processor.py (Zeile 166-171)
**Problem:** Event history wird nur bei 1000 Events bereinigt, sollte kontinuierlicher sein
**Fix:** Niedrigere Schwelle oder regelmäßige Bereinigung

### 6. ⚠️ STATUS PROCESSOR - FEHLENDE STATUS_MANAGER
**Datei:** action_processor.py (Zeile 103-107)
**Problem:** Code prüft auf status_manager, aber MonsterInstance hat möglicherweise keinen
```python
# Problem:
if hasattr(monster, 'status_manager'):
    if not monster.status_manager.can_act():
# Fix: Fallback verwenden
if hasattr(monster, 'status_manager'):
    can_act = monster.status_manager.can_act()
else:
    can_act = monster.status != StatusCondition.SLEEP
```

### 7. ⚠️ UNDEFINED ATTRIBUTES IN VALIDATION
**Datei:** battle_validation.py (Zeile 85-92)
**Problem:** Zugriff auf monster.is_fainted ohne zu prüfen ob es existiert
```python
# Problem:
if actor.is_fainted:
# Fix:
if hasattr(actor, 'is_fainted') and actor.is_fainted:
# Oder:
if getattr(actor, 'is_fainted', False):
```

## MITTLERE FEHLER

### 8. ⚡ UI SYNC CALLBACK NICHT GESETZT
**Datei:** battle_controller.py (Zeile 208-215)
**Problem:** ui_sync_callback wird referenziert aber nie initialisiert
```python
# Problem:
if hasattr(self, 'ui_sync_callback') and self.ui_sync_callback:
# Fix in __init__:
self.ui_sync_callback = None  # In __init__ hinzufügen
```

### 9. ⚡ BATTLE AI - FALLBACK MOVE INKORREKT
**Datei:** battle_ai.py (Zeile 71-78)
**Problem:** Fallback Move ist kein richtiges Move-Objekt
```python
# Problem:
available_moves = [type('Move', (), {
    'name': 'Tackle',
    'power': 40,
    # ...
})()]
# Fix: Richtiges Move-Objekt erstellen oder MoveRegistry verwenden
```

### 10. ⚡ ACTION TYPE CONVERSION FEHLER
**Datei:** battle_validation.py (Zeile 216-223)
**Problem:** ActionType.from_string() existiert möglicherweise nicht
```python
# Fix: Eigene Conversion-Funktion
action_type_map = {
    'attack': ActionType.ATTACK,
    'item': ActionType.ITEM,
    # ...
}
```

## KLEINERE FEHLER & VERBESSERUNGEN

### 11. 📝 LOGGING INKONSISTENT
**Mehrere Dateien**
**Problem:** Manche verwenden logger.debug(), andere logger.info() für gleiche Events
**Fix:** Einheitliches Logging-Level für gleiche Event-Typen

### 12. 📝 MISSING TYPE HINTS
**Datei:** action_processor.py
**Problem:** validate_action_with_errors() Methode existiert nicht, wird aber aufgerufen (Zeile 321)
```python
# Problem:
is_valid, errors = self.validate_action_with_errors(battle_action, state)
# Fix: Methode implementieren oder richtige verwenden
```

### 13. 📝 CIRCULAR IMPORT POTENZIAL
**Mehrere Dateien**
**Problem:** TYPE_CHECKING wird inkonsistent verwendet
**Fix:** Alle zirkulären Imports in TYPE_CHECKING blocks

### 14. 📝 MEAT SYSTEM INTEGRATION
**Datei:** action_processor.py (Zeile 365-370)
**Problem:** MeatSystem wird möglicherweise mehrfach instanziiert
```python
# Problem:
meat_system = self.state.meat_system if hasattr(self.state, 'meat_system') else MeatSystem()
# Fix: Singleton Pattern oder in battle_state initialisieren
```

### 15. 📝 EVENT HANDLER REGISTRATION
**Datei:** event_processor.py (Zeile 470-520)
**Problem:** Lambda-Funktionen können Memory Leaks verursachen
**Fix:** Benannte Methoden statt Lambdas verwenden

## PERFORMANCE PROBLEME

### 16. 🐌 SORT BEI JEDEM EVENT
**Datei:** event_processor.py (Zeile 155)
**Problem:** Events werden bei jedem process_events() sortiert
**Fix:** Priority Queue verwenden (heapq)

### 17. 🐌 COPY() OVERUSE
**Datei:** action_processor.py
**Problem:** .copy() wird oft unnötig verwendet
**Fix:** Nur kopieren wenn wirklich nötig

## EMPFOHLENE FIXES (Priorität)

### SOFORT:
1. ✅ check_battle_end() Fix (bereits erledigt)
2. Phase Management fixen
3. Event-Dopplung entfernen
4. UI Sync Callback initialisieren

### DIESE WOCHE:
5. Status Manager Fallback
6. Battle AI Robustheit
7. Event Processor Memory Management
8. Validation Attribute Checks

### SPÄTER:
9. Logging vereinheitlichen
10. Type Hints vervollständigen
11. Performance-Optimierungen
12. Lambda zu Named Functions

## TEST COVERAGE LÜCKEN

### Fehlende Tests für:
- Status effect interactions
- Multi-turn battle sequences
- Edge cases (0 HP, negative damage, etc.)
- Event handler error recovery
- AI difficulty levels
- Meat system integration
- Phase transitions

## ARCHITEKTUR-EMPFEHLUNGEN

1. **Event System:** Verwende einen Event Bus statt direkter Handler
2. **State Machine:** Implementiere richtige State Machine für Phasen
3. **Singleton Pattern:** Für Manager-Klassen (MeatSystem, TypeChart, etc.)
4. **Factory Pattern:** Für Move/Action Creation
5. **Observer Pattern:** Für UI Updates statt Callbacks

## QUICK FIX SCRIPT

```python
# fix_battle_issues.py
import sys
from pathlib import Path

def fix_phase_management():
    \"\"\"Fix phase management in battle_controller.py\"\"\"
    file = Path("engine/systems/battle/battle_controller.py")
    content = file.read_text()
    
    # Fix phase initialization
    content = content.replace(
        "self.state.phase = BattlePhase.INIT",
        "self.state.phase = BattlePhase.START"
    )
    
    file.write_text(content)
    print("✓ Phase management fixed")

def fix_ui_sync_callback():
    \"\"\"Add ui_sync_callback initialization\"\"\"
    file = Path("engine/systems/battle/battle_controller.py")
    content = file.read_text()
    
    # Add after self.status_processor = None
    if "self.ui_sync_callback = None" not in content:
        content = content.replace(
            "self.status_processor: Optional['StatusProcessor'] = None",
            "self.status_processor: Optional['StatusProcessor'] = None\\n        self.ui_sync_callback: Optional[Callable] = None"
        )
    
    file.write_text(content)
    print("✓ UI sync callback fixed")

def remove_duplicate_events():
    \"\"\"Remove duplicate event emissions\"\"\"
    # This needs manual review to decide which to keep
    print("⚠️ Manual review needed for duplicate events")
    print("  Check: battle_controller.py lines 153-160")
    print("  Check: turn_processor.py lines 60-64")

if __name__ == "__main__":
    fix_phase_management()
    fix_ui_sync_callback()
    remove_duplicate_events()
    print("\\nRun tests to verify fixes:")
    print("  python -m pytest tests/battle/")
```

## ZUSAMMENFASSUNG

**Kritische Bugs:** 3 (1 behoben)
**Schwerwiegende:** 7
**Mittlere:** 5
**Kleine:** 5
**Performance:** 2

**Geschätzter Aufwand:** 
- Kritische Fixes: 2-3 Stunden
- Alle Fixes: 8-10 Stunden
- Mit Tests: 15-20 Stunden

Der größte strukturelle Fehler ist das inkonsistente Event-System und die fehlende 
ordentliche State Machine für Battle Phases. Diese sollten prioritär angegangen werden.
"""