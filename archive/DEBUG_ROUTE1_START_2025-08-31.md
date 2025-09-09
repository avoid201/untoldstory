# Debug Mode: Route 1 Start

## Schnellstart für Bugfixing

Diese Debug-Option ermöglicht es dir, direkt auf Route 1 mit einem ausgewählten Monster in der Party zu starten, ohne das normale Spiel durchlaufen zu müssen.

## Aktivierung

1. Starte das Spiel mit `python3 main.py`
2. Im Titelbildschirm drücke **D** für Debug-Modus
3. Wähle ein Monster aus der Liste mit ↑↓
4. Bestätige mit **ENTER** um auf Route 1 zu starten

## Was passiert im Debug-Modus

- **Titelbildschirm**: Drücke **D** für Debug-Modus
- **Monster-Auswahl**: Wähle aus 151 verfügbaren Monstern
- **Route 1 Start**: Spawnt direkt auf Route 1 mit dem gewählten Monster
- **Level 5**: Das Monster startet auf Level 5 und ist kampfbereit
- **Sofortige Tests**: Du kannst sofort Encounters und das Battle-System testen

## Steuerung

### Titelbildschirm
- **ENTER/SPACE/E**: Normaler Spielstart
- **D**: Debug-Modus
- **ESC**: Spiel beenden

### Debug-Monster-Auswahl
- **↑↓**: Monster auswählen
- **PAGE UP/DOWN**: Schnell durch die Liste blättern
- **ENTER/SPACE**: Monster auswählen und auf Route 1 starten
- **ESC**: Zurück zum Titelbildschirm

## Monster-Informationen

Die Debug-Auswahl zeigt für jedes Monster:
- **ID**: Eindeutige Nummer
- **Name**: Monster-Name
- **Typen**: Element-Typen (z.B. Feuer/Wasser)
- **Rang**: Monster-Rang (F bis X)
- **Stats**: Detaillierte Basis-Statistiken

## Vorteile

- 🎯 **Flexibel**: Wähle jedes Monster aus der Datenbank
- 🚀 **Schnell**: Direkt zum Testen ohne Story-Progression
- 📊 **Informativ**: Detaillierte Monster-Informationen
- 🔄 **Einfach**: Ein Tastendruck für Debug-Modus
- 🛡️ **Sicher**: Keine Auswirkungen auf normale Spielabläufe

## Tipps

- Perfekt für Battle-System Testing
- Schnelle Encounter-Tests mit verschiedenen Monstern
- UI-Debugging ohne Story-Progression
- Teste verschiedene Monster-Typen und Ränge

## Fehlerbehebung

Falls der Debug-Modus nicht funktioniert:
1. Prüfe die Konsolen-Ausgabe auf Fehlermeldungen
2. Stelle sicher, dass `monsters.json` geladen werden kann
3. Prüfe, ob Route 1 Map-Daten vorhanden sind
4. Drücke **D** im Titelbildschirm (nicht im Hauptmenü)

---
*Diese Debug-Option ist nur für Entwicklungszwecke gedacht und sollte in der finalen Version deaktiviert bleiben.*
