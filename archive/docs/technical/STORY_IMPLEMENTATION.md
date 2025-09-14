# 🎮 Untold Story - Ruhrpott Story Implementation

## ✅ Was wurde implementiert?

### 1. **MainMenuScene** - Neues Spiel mit Story-Integration
- Reset des Story-Managers bei neuem Spiel
- Party wird geleert für frischen Start  
- Spieler startet im `player_house` am Spawn-Point `bed`
- Story-Flags werden korrekt initialisiert

### 2. **StoryManager** - Erweiterte Story-Verwaltung
- `reset()` Methode für Neustart
- Alle wichtigen Story-Flags:
  - `first_awakening` - Erstes Aufwachen
  - `left_house_first_time` - Haus zum ersten Mal verlassen
  - `professor_intro_started` - Professor-Intro gestartet
  - `rival_first_encounter` - Erste Begegnung mit Klaus
  - `has_starter` - Starter-Monster erhalten

### 3. **FieldScene** - Story-Events mit Ruhrpott-Vibe
- **Event 1:** Interner Monolog beim ersten Verlassen des Hauses
- **Event 2:** Professor-Intro beim Betreten des Museums
- **Event 3:** Klaus spawnt nach Museum-Verlassen mit Starter
- **Event 4:** Zeitrisse (für späteren Content vorbereitet)

#### Neue Methoden:
- `_show_internal_monologue()` - Zeigt Spieler-Gedanken
- `_trigger_professor_fossil_intro()` - Professor's derbe Einführung
- `_spawn_klaus_for_battle()` - Klaus spawnt und provoziert
- `_create_rival_monster()` - Klaus' Monster mit Typ-Vorteil
- `_on_klaus_victory/defeat()` - Dialoge nach Kampf

### 4. **Dialogues.json** - Authentische Ruhrpott-Dialoge
Neue Story-Dialoge hinzugefügt:
- `mom_morning_wake` - Mutter weckt den Spieler derb auf
- `professor_fossil_intro` - Professor's verrückte Fossil-Präsentation
- `klaus_first_battle` - Klaus provoziert zum ersten Kampf
- `fossil_glutkohle/tropfstein/lehmling/windei` - Fossil-Erklärungen

### 5. **StarterScene** - Fossil-Auswahl mit Attitude
- Derbe Einführung vom Professor
- Spezifische Erklärungen für jedes Fossil-Monster
- Ruhrpott-typische Bestätigungsdialoge
- Klaus wird als Rivale erwähnt

## 🎯 Story-Flow

```
1. SPIELSTART
   ↓
2. AUFWACHEN IM SPIELERHAUS
   ├── Optional: Mit Mutter reden
   ↓
3. HAUS VERLASSEN → KOHLENSTADT
   ├── Interner Monolog über die Stadt
   ↓
4. MUSEUM BETRETEN
   ├── Professor Budde Intro
   ├── Derbe Fossil-Erklärung
   ↓
5. STARTER AUSWÄHLEN
   ├── Glutkohle (Feuer)
   ├── Tropfstein (Wasser)
   ├── Lehmling (Erde)
   ├── Windei (Luft)
   ↓
6. MUSEUM VERLASSEN
   ├── Klaus spawnt
   ├── Provokation
   ├── KAMPF!
   ↓
7. FREIE ERKUNDUNG
```

## 🎮 Testen der Implementation

### Quick-Test:
```bash
python test_story_flow.py
```

### Vollständiger Test:
```bash
python main.py
```

### Test-Ablauf:
1. **Hauptmenü** → "Neues Spiel"
2. **Spielerhaus** → Mit WASD bewegen, Haus verlassen
3. **Kohlenstadt** → Interner Monolog sollte erscheinen
4. **Museum betreten** → Professor-Dialog triggert automatisch
5. **Starter wählen** → A/D zum Wechseln, E zum Bestätigen
6. **Museum verlassen** → Klaus spawnt und fordert zum Kampf
7. **Nach dem Kampf** → Freie Erkundung möglich

## 🔧 Debug-Befehle

Im Spiel **TAB** drücken für Debug-Modus, dann:
- **G** - Grid anzeigen
- **C** - Kollisionen anzeigen
- **E** - Entity-Info
- **B** - Kampf erzwingen (nur im Debug-Modus)

## 🗣️ Ruhrpott-Sprache Highlights

### Professor Budde:
> "Ach, da bisse ja endlich, du Schlafmütze!"
> "Die Dinger sind der absolute Hammer! Stärker als der ganze moderne Dreck!"

### Klaus der Rivale:
> "Ey, Alter! Na, auch endlich wach geworden?"
> "Komm, lass uns kloppen! Ich mach dich fertig!"

### Mutter:
> "Ey, Junge! Pennst du immer noch, du faule Socke?"
> "Mach hinne, sonst kriegste kein Frühstück mehr!"

## 📝 Noch zu implementieren

- [ ] Weitere NPCs mit Ruhrpott-Dialogen
- [ ] Die 10 Trials/Prüfungen
- [ ] Zeitriss-Events (Mid-Game)
- [ ] Team Temporal als Antagonisten
- [ ] 11 Legendäre Monster
- [ ] Synthese-System
- [ ] Weitere Städte und Routen

## 🐛 Bekannte Issues

1. **Player.last_map** wird noch nicht getrackt → Events triggern möglicherweise mehrfach
2. **Spawn-Points** in Maps müssen noch definiert werden
3. **Monster-Sprites** für Starter fehlen noch → Fallback auf farbige Rechtecke

## 💡 Tipps für Weiterentwicklung

1. **Story-Flags** immer über `story_manager.set_flag()` setzen
2. **Dialoge** in `dialogues.json` pflegen für Konsistenz
3. **Ruhrpott-Slang** durchgehend verwenden für Authentizität
4. **Debug-Modus** nutzen für schnelles Testen

---

**Viel Spaß mit dem Ruhrpott-RPG! Glück auf!** ⛏️
