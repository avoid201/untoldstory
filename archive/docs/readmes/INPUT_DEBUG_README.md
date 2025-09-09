# 🔍 Input Debug System - Untold Story

## Übersicht
Das Input Debug System bietet umfassende Debug-Funktionen für alle Keyboard-Inputs im Spiel. Es zeichnet jeden Tastendruck auf, analysiert Input-Muster und hilft bei der Fehleranalyse.

## 🚀 Aktivierung
Der Input-Debug ist **automatisch aktiviert** und läuft im Hintergrund. Alle Tastendrücke werden in der Konsole geloggt, auch die, die keine Aktion auslösen.

## ⌨️ Debug Hotkeys

### Grundlegende Debug-Funktionen
- **TAB**: Debug-Overlay ein/ausschalten
- **G** (mit Debug-Overlay): Grid anzeigen/verstecken

### Input-Debug Hotkeys
- **F1**: Input-Log Zusammenfassung anzeigen
- **F2**: Input-Log löschen
- **F3**: Input-Debug ein/ausschalten
- **F4**: Aktueller Input-Status anzeigen

### Erweiterte Debug-Funktionen
- **F5**: Input-Analyse in JSON-Datei exportieren
- **F6**: Unbehandelte Inputs finden
- **F7**: Performance-Probleme finden (>16ms Verarbeitungszeit)

## 📊 Debug-Overlay Informationen

Das Debug-Overlay (TAB) zeigt folgende Informationen an:

### Obere Anzeige (Grün)
- Aktuelle Scene
- Scene-Stack-Größe
- Spielzeit
- Frame-Nummer
- Mausposition
- Aktuell gedrückte Tasten
- Movement-Vector
- Input-Debug Status

### Untere Anzeige (Gelb)
- Alle verfügbaren Debug-Hotkeys

## 🔍 Konsolen-Ausgabe

### Standard Input-Log
Jeder Tastendruck wird in folgendem Format geloggt:
```
🔍 INPUT: KEYDOWN   | w            (Code: 119) -> MOVE_UP
🔍 INPUT: KEYUP     | w            (Code: 119) -> RELEASED
🔍 INPUT: REPEAT    | w            (Code: 119) -> REPEAT: MOVE_UP
```

### Event-Typen
- **KEYDOWN**: Taste wurde gedrückt
- **KEYUP**: Taste wurde losgelassen
- **REPEAT**: Taste wird wiederholt gehalten

### Aktionen
- **MOVE_UP/DOWN/LEFT/RIGHT**: Bewegung
- **CONFIRM/INTERACT**: Bestätigung/Interaktion
- **CANCEL/RUN**: Abbrechen/Laufen
- **MENU**: Menü öffnen
- **QUICK_ACCESS**: Schnellzugriff
- **PAUSE**: Pause
- **DEBUG_TOGGLE**: Debug umschalten
- **KEINE_AKTION**: Keine definierte Aktion

## 📈 Erweiterte Analyse

### F1 - Input-Log Summary
Zeigt eine Zusammenfassung aller aufgezeichneten Events:
- Gesamtanzahl Events
- Verteilung nach Event-Typ
- Verteilung nach Aktion
- Letzte 10 Events

### F5 - Export Input-Analysis
Exportiert eine detaillierte Analyse in `input_analysis.json`:
- Vollständige Statistiken
- Performance-Metriken
- Letzte 100 Events
- Export-Zeitstempel

### F6 - Unbehandelte Inputs
Findet alle Input-Events, die von keiner Scene verarbeitet wurden:
- Event-Typ
- Taste
- Aktion
- Frame-Nummer

### F7 - Performance-Probleme
Findet Events mit Verarbeitungszeiten > 16ms (1 Frame bei 60 FPS):
- Event-Details
- Verarbeitungszeit in Millisekunden
- Performance-Warnungen

## 🛠️ Konfiguration

### Input-Debug ein/ausschalten
```python
# Über F3 oder programmatisch
self.input_manager.debug_enabled = False
```

### Bestimmte Tasten ignorieren
```python
# Taste wird nicht geloggt
self.input_manager.add_ignored_key(pygame.K_CAPSLOCK)

# Taste wird wieder geloggt
self.input_manager.remove_ignored_key(pygame.K_CAPSLOCK)
```

### Event-Filter setzen
```python
# Nur bestimmte Event-Typen aufzeichnen
self.input_debugger.set_filter(event_types={'KEYDOWN', 'KEYUP'})

# Nur bestimmte Tasten aufzeichnen
self.input_debugger.set_filter(keys={pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d})

# Alle Filter entfernen
self.input_debugger.clear_filter()
```

## 📁 Dateien

### Core-Dateien
- `engine/core/input_manager.py`: Erweiterter Input Manager mit Debug
- `engine/core/game.py`: Game-Loop mit Input-Debug-Integration
- `engine/devtools/input_debug.py`: Erweiterte Debug-Funktionen

### Export-Dateien
- `input_analysis.json`: Exportierte Input-Analyse

## 🔧 Fehleranalyse

### Häufige Probleme identifizieren

1. **Unbehandelte Inputs (F6)**
   - Tasten die keine Aktion auslösen
   - Fehlende Event-Handler in Scenes

2. **Performance-Probleme (F7)**
   - Langsame Event-Verarbeitung
   - Bottlenecks in der Input-Pipeline

3. **Input-Muster (F1)**
   - Häufig verwendete Tasten
   - Event-Verteilung über Zeit

### Debug-Workflow

1. **Spiel starten** - Debug läuft automatisch
2. **Problem reproduzieren** - Alle Inputs werden geloggt
3. **F1 drücken** - Übersicht über Input-Muster
4. **F6 drücken** - Unbehandelte Inputs finden
5. **F7 drücken** - Performance-Probleme identifizieren
6. **F5 drücken** - Analyse exportieren für weitere Untersuchung

## 💡 Tipps

- **F2** regelmäßig drücken um Log zu löschen
- **F3** nutzen um Debug bei Bedarf auszuschalten
- **F5** vor dem Beenden drücken um Analyse zu speichern
- Debug-Overlay (TAB) aktiviert halten für Live-Informationen
- Performance-Probleme bei Events > 16ms untersuchen

## 🐛 Bekannte Probleme

- Einige Tasten können als "UNKNOWN" angezeigt werden
- Performance-Tracking kann bei sehr schnellen Events ungenau sein
- Export kann bei sehr vielen Events Speicher verbrauchen

## 📞 Support

Bei Problemen mit dem Input-Debug-System:
1. Konsolen-Ausgabe überprüfen
2. `input_analysis.json` analysieren
3. Debug-Logs mit F1-F7 durchgehen
4. Event-Filter für spezifische Probleme nutzen
