# Event- und Status-System

## Übersicht

Das Event- und Status-System wurde in zwei separate, fokussierte Klassen aufgeteilt:

- **EventProcessor**: Verwaltet nur Events und deren Verarbeitung
- **StatusProcessor**: Verwaltet nur Status-Effekte

## EventProcessor

### Verwendung

```python
from engine.systems.battle.event_processor import EventProcessor, EventType

# EventProcessor erstellen
event_processor = EventProcessor(battle_state)

# Event-Handler registrieren
def message_handler(event):
    print(f"Nachricht: {event.data['message']}")

event_processor.register_handler(EventType.MESSAGE_SHOW, message_handler)

# Events emittieren
event_processor.emit_message_event("Test-Nachricht!")
event_processor.emit_damage_event(target, 50, attacker)
event_processor.emit_status_event(monster, "burn", True)

# Events verarbeiten
ui_updates = event_processor.process_events()
```

### Wichtige Methoden

- `emit_event(event)`: Event emittieren
- `process_events()`: Alle Events verarbeiten und UI-Updates zurückgeben
- `register_handler(event_type, handler)`: Event-Handler registrieren
- `get_pending_events()`: Ausstehende Events abrufen
- `clear_events()`: Alle Events löschen

## StatusProcessor

### Verwendung

```python
from engine.systems.battle.status_processor import StatusProcessor

# StatusProcessor erstellen
status_processor = StatusProcessor(battle_state)

# Status anwenden
result = status_processor.apply_status(monster, "burn")
if result.success:
    print(result.message)

# Status-Effekte verarbeiten (Ende der Runde)
result = status_processor.process_status_effects(monster)
if result.damage_dealt > 0:
    print(f"Status-Schaden: {result.damage_dealt}")

# Status-Modifikatoren abrufen
modifiers = status_processor.get_status_modifiers(monster)
```

### Wichtige Methoden

- `apply_status(monster, status)`: Status anwenden
- `process_status_effects(monster)`: Status-Effekte verarbeiten
- `remove_status(monster, status)`: Status entfernen
- `get_status_modifiers(monster)`: Status-Modifikatoren abrufen
- `can_act(monster)`: Prüfen ob Monster handeln kann

## Status-Definitionen

### Verfügbare Status-Effekte

- **burn**: 1/8 HP Schaden pro Runde, reduziert Angriff um 50%
- **poison**: 1/16 HP Schaden pro Runde
- **badly_poisoned**: Zunehmender Schaden pro Runde
- **freeze**: Verhindert Aktionen, 20% Chance aufzutauen
- **paralysis**: Reduziert Initiative um 50%, 25% Chance Aktion zu verhindern
- **sleep**: Verhindert Aktionen für 1-3 Runden
- **confusion**: Kann sich selbst schaden für 1-3 Runden

### Typ-Immunitäten

- **burn**: Feuer-Typen sind immun
- **freeze**: Feuer- und Luft-Typen sind immun
- **poison**: Seuche- und Teufel-Typen sind immun
- **paralysis**: Energie-Typen sind immun

## Integration

Die beiden Systeme arbeiten zusammen:

```python
# Status anwenden
status_result = status_processor.apply_status(monster, "burn")
if status_result.success:
    # Event für UI emittieren
    event_processor.emit_status_event(monster, "burn", True)

# Status-Schaden verarbeiten
status_result = status_processor.process_status_effects(monster)
if status_result.damage_dealt > 0:
    # Schaden-Event emittieren
    event_processor.emit_damage_event(monster, status_result.damage_dealt, monster)

# Alle Events verarbeiten
ui_updates = event_processor.process_events()
```

## Migration von altem System

Die Logik wurde aus den bestehenden Klassen übernommen:

- **EventProcessor** übernimmt Logik von `BattleEventGenerator` und `EventQueue`
- **StatusProcessor** übernimmt Logik von `StatusEffects` Klasse

Die neuen Klassen sind kompatibel mit dem bestehenden Battle-System und können schrittweise integriert werden.
