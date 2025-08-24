# Story-Implementierung - Untold Story

## Übersicht

Diese Implementierung fügt ein vollständiges Story-System zu "Untold Story" hinzu, einschließlich:
- Story Manager für Quest- und Flag-Verwaltung
- NPC-System mit Professor Budde und Rival Klaus
- Cutscene-System für skriptbasierte Ereignisse
- Starter-Monster-Auswahl
- Integrierte Story-Events in der Field Scene

## Implementierte Systeme

### 1. Story Manager (`engine/systems/story_manager.py`)

**Funktionalitäten:**
- Verwaltet Story-Flags und Quest-Fortschritt
- Automatische Quest-Fortschritte basierend auf Flags
- Speichern/Laden des Story-Status

**Wichtige Flags:**
- `game_started`: Spiel hat begonnen
- `has_starter`: Spieler hat Starter-Monster
- `met_rival`: Spieler hat Rivalen getroffen
- `rival_first_battle`: Erster Kampf mit Rivalen abgeschlossen
- `visited_museum`: Museum besucht

**Quests:**
- `main_story`: Hauptstory-Quest mit 5 Objectives
- `starter_quest`: Starter-Monster-Quest

### 2. NPC System (`engine/world/npc.py`)

**NPCs:**
- **Professor Budde**: Gibt dem Spieler das Starter-Monster
- **Rival Klaus**: Fordert den Spieler zum Kampf heraus

**Features:**
- Kontextabhängige Dialoge basierend auf Story-Flags
- Interaktions-Callbacks
- Dynamische Dialog-Generierung

### 3. Cutscene System (`engine/systems/cutscene.py`)

**Cutscenes:**
- `awakening`: Spielbeginn-Aufwach-Cutscene
- `receive_starter`: Starter-Erhalt-Cutscene
- `rival_intro`: Rivalen-Einführung

**Action-Typen:**
- `dialogue`: Dialog anzeigen
- `fade`: Ein-/Ausblenden
- `spawn`: Entity spawnen
- `move`: Entity bewegen
- `scene_change`: Szene wechseln

### 4. Starter Selection Scene (`engine/scenes/starter_selection_scene.py`)

**Features:**
- Drei Starter-Optionen (Feuer, Wasser, Pflanze)
- Visuelle Auswahl mit Pfeiltasten
- Integration mit Party Manager
- Story-Flag-Updates

### 5. Erweiterte Field Scene

**Neue Methoden:**
- `_check_story_events()`: Prüft Story-Trigger
- `_start_professor_intro()`: Startet Professor-Dialog
- `_spawn_rival_outside_museum()`: Spawnt Rivalen
- `_start_rival_battle()`: Startet Rivalen-Kampf
- `_on_rival_victory/defeat()`: Kampf-Ergebnis-Callbacks

## Spielablauf

### 1. Spielbeginn
1. Spieler erwacht im Haus
2. `awakening` Cutscene wird abgespielt
3. Spieler verlässt Haus → `left_house_first_time` Flag wird gesetzt

### 2. Professor Budde
1. Spieler betritt Museum → `visited_museum` Flag wird gesetzt
2. Professor-Dialog startet automatisch
3. Wechsel zur Starter-Auswahl-Szene
4. Spieler wählt Starter → `has_starter` Flag wird gesetzt

### 3. Rivalen-Kampf
1. Spieler verlässt Museum mit Starter
2. Rivalen-Spawn wird geprüft (`should_spawn_rival()`)
3. Rival Klaus erscheint vor dem Museum
4. Dialog und Kampf starten automatisch
5. Nach Kampf: `rival_first_battle` Flag wird gesetzt

### 4. Story-Fortschritt
- Quest-Objectives werden automatisch fortgeschritten
- Neue Gebiete werden freigeschaltet
- Story-Flags steuern weitere Events

## Technische Details

### Flag-System
```python
# Flag setzen
story_manager.set_flag('has_starter', True)

# Flag prüfen
if story_manager.get_flag('visited_museum'):
    # Museum wurde besucht
```

### Quest-System
```python
# Quest voranschreiten
story_manager.advance_quest('main_story')

# Aktuelles Ziel abrufen
objective = story_manager.get_current_objective()
```

### NPC-Integration
```python
# NPC erstellen
professor = ProfessorBudde(x, y)
professor.set_dialogue(pages)

# Dialog abrufen
dialogue = professor.get_dialogue(story_manager)
```

### Cutscene-System
```python
# Cutscene abspielen
cutscene_manager.play('awakening', callback=on_complete)

# Cutscene aktualisieren
cutscene_manager.update(dt)
```

## Map-Integration

### Spawn-Punkte
- `player_house`: `bed` (x:2, y:3)
- `museum`: `entrance` (x:5, y:8), `professor` (x:5, y:2)
- `kohlenstadt`: `rival_spawn` (x:10, y:8) für Rivalen

### Warps
- Haus ↔ Kohlenstadt
- Museum ↔ Kohlenstadt
- Kohlenstadt ↔ Route 1

## Erweiterte Features

### Story-Event-Trigger
- Position-basierte Event-Auslösung
- Automatische Flag-Updates
- Kontextabhängige NPC-Spawns

### Dynamische Dialoge
- NPCs reagieren auf Story-Fortschritt
- Verschiedene Dialoge je nach Situation
- Callback-basierte Dialog-Ketten

### Kampf-Integration
- Automatische Rivalen-Kampf-Erstellung
- Typ-Vorteil-System (Feuer > Pflanze > Wasser > Feuer)
- Kampf-Ergebnis-Callbacks

## Nächste Schritte

### Geplante Erweiterungen
1. **Route 1 Implementation**: Wild-Monster-Encounters
2. **Schachtstadt**: Neue Stadt mit weiteren NPCs
3. **Gym-System**: Trainer-Kämpfe und Badges
4. **Item-System**: Pokeballs, Heil-Items, etc.
5. **Save/Load**: Spielstand speichern/laden

### Verbesserungen
1. **Cutscene-Actions**: Vollständige Action-Implementierung
2. **Sound-Integration**: Musik und Soundeffekte
3. **Animationen**: Smooth Transitions zwischen Szenen
4. **UI-Polish**: Bessere Starter-Auswahl-Interface

## Debugging

### Häufige Probleme
1. **Import-Fehler**: Stelle sicher, dass alle Module korrekt importiert werden
2. **Flag-Timing**: Flags müssen in der richtigen Reihenfolge gesetzt werden
3. **NPC-Spawns**: Überprüfe Koordinaten und Map-Referenzen
4. **Callback-Ketten**: Stelle sicher, dass alle Callbacks korrekt verketten

### Debug-Ausgaben
```python
# Story-Flag-Änderungen werden geloggt
print(f"Story Flag gesetzt: {flag_name} = {value}")

# Quest-Fortschritte werden geloggt
print(f"Quest '{quest_id}' fortgeschritten!")
```

## Fazit

Das Story-System ist vollständig implementiert und bietet:
- Einen strukturierten Spielablauf
- Flexible Story-Flag-Verwaltung
- Integrierte NPC-Interaktionen
- Skriptbasierte Cutscenes
- Nahtlose Integration mit dem bestehenden Spiel

Das System ist erweiterbar und kann einfach um neue Story-Elemente, NPCs und Quests erweitert werden.
