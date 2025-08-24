# 🎮 Test-Anleitung für das neue TMX-Integrationssystem

## Das Spiel läuft jetzt mit dem neuen System!

### Was ist neu?

✅ **NPCs werden aus JSON-Dateien geladen** (nicht mehr hardcoded)
✅ **Dialoge kommen aus separaten Dateien** 
✅ **Warps sind in JSON definiert**
✅ **Interaktive Objekte sind datengetrieben**

### 🧪 Was Sie testen sollten:

## 1. Im Spielerhaus (Start-Location)

- **Sprechen Sie mit Ihrer Mutter** (Position: Mitte des Raums)
  - Sie sollte verschiedene Dialoge haben
  - Der Dialog ändert sich, wenn Sie ein Starter-Monster haben

- **Interagieren Sie mit dem Bett** (oben links)
  - Sollte fragen, ob Sie sich ausruhen möchten
  - Heilt Ihr Team (wenn Sie Monster haben)

- **Untersuchen Sie das Bücherregal** (oben rechts)
  - Zeigt Text über Ruhrgebiet-Geschichte

- **Verlassen Sie das Haus** durch die Tür (unten)
  - Sollte Sie nach Kohlenstadt warpen

## 2. In Kohlenstadt

- **NPCs zum Testen:**
  - **Ruhrpott Karl** - sollte über wilde Monster sprechen
  - **Info Lady** - gibt Tipps
  - **Youngster Tim** - bewegt sich zufällig herum

- **Warps zum Testen:**
  - Zurück ins Spielerhaus
  - Museum (Professor Budde)
  - Rival-Haus
  - Penny-Markt

## 3. Im Museum

- **Professor Budde** sollte erscheinen
  - Unterschiedlicher Dialog je nach Story-Status
  - Bietet Starter-Monster an (wenn noch keins vorhanden)

- **Fossil-Displays** untersuchen
  - Jedes Display hat eigenen Text

## 4. Debug-Befehle

Drücken Sie **TAB** um den Debug-Modus zu aktivieren, dann:
- **G** - Grid anzeigen
- **C** - Kollisionen anzeigen
- **E** - Entity-Infos
- **T** - Tile-Infos

## 5. Was funktioniert noch NICHT:

- ❌ Cutscenes (System vorbereitet aber nicht implementiert)
- ❌ Speichern/Laden von Interaktionszuständen
- ❌ Komplexe NPC-Bewegungsmuster
- ❌ Bedingte Warps

## 📝 Fehler gefunden?

Schauen Sie in die Terminal-Ausgabe für Debugging-Informationen:
- `[EnhancedMapManager]` - Zeigt Map-Lade-Aktivitäten
- `[InteractionManager]` - Zeigt geladene Interaktionen
- `[NPCManager]` - Zeigt gespawnte NPCs

## 🔧 System deaktivieren

Falls Probleme auftreten, können Sie das alte System wiederherstellen:
1. Öffnen Sie `engine/scenes/field_scene.py`
2. Setzen Sie `self.use_enhanced_manager = False`
3. Starten Sie das Spiel neu

## ✨ Vorteile des neuen Systems:

1. **Keine Code-Änderungen für neue NPCs** - Einfach JSON bearbeiten
2. **Designer-freundlich** - Nicht-Programmierer können Inhalte hinzufügen
3. **Versionskontrolle** - JSON-Dateien sind diff-freundlich
4. **Wartbarkeit** - Klare Trennung von Visuals und Logik

Viel Spaß beim Testen! 🎮
