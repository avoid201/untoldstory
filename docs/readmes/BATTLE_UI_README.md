# Battle UI & Logging System - Untold Story

Ein umfassendes Battle UI und Logging-System für das 2D RPG "Untold Story" mit pygame-ce.

## 🎯 Übersicht

Das System besteht aus drei Hauptkomponenten:
1. **BattleUI** - Modulare UI-Komponenten für Kampf-Interfaces
2. **BattleLog** - Umfassendes Logging-System mit Ruhrpott-Slang
3. **BattleStyles** - CSS-ähnliche Style-Konfiguration

## 🚀 Features

### BattleUI
- **BattleHUD**: HP/PP-Balken, Level, Status-Icons
- **BattleMenu**: Navigation durch Kampf-Optionen
- **MoveSelector**: Angriffsauswahl mit Typ-Farben
- **TargetSelector**: Zielauswahl mit Hervorhebung
- **DamageNumbers**: Schwebe-Schadenszahlen mit Effekten

### BattleLog
- **Kategorisierte Nachrichten** (Angriff, Schaden, Status, etc.)
- **Prioritätsstufen** (Kritisch, Normal, Detail, Debug)
- **Ruhrpott-Slang Templates** für authentische Atmosphäre
- **Auto-Scroll** mit Navigationssteuerung
- **Export-Funktionen** (TXT, JSON)

### BattleStyles
- **Vordefinierte Themes** (Default, Dark, Light, Retro, Modern)
- **CSS-ähnliche Konfiguration** für einfache Anpassung
- **Responsive Design** für verschiedene Auflösungen

## 📁 Dateistruktur

```
engine/ui/
├── battle_ui.py          # Haupt-Battle UI System
├── battle_log.py         # Battle Logging System
└── battle_styles.py      # Style-Konfiguration

test_battle_ui.py         # Demo-Anwendung
BATTLE_UI_README.md       # Diese Datei
```

## 🔧 Installation & Integration

### 1. Abhängigkeiten
Das System benötigt:
- Python 3.13.5+
- pygame-ce 2.5+
- Standard Python-Bibliotheken (dataclasses, typing, pathlib)

### 2. Integration in bestehende Battle-Scene

```python
# In engine/scenes/battle_scene.py
from engine.ui.battle_ui import BattleUI
from engine.ui.battle_log import BattleLog

class BattleScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        
        # Battle UI System
        self.battle_ui = BattleUI(game)
        self.battle_log = BattleLog()
        
        # ... rest of initialization
    
    def update(self, dt):
        # Update UI components
        self.battle_ui.update(dt)
        
        # ... rest of update logic
    
    def draw(self, surface):
        # Draw battle UI
        self.battle_ui.draw(surface)
        
        # Draw battle log
        self.battle_log.draw(surface)
        
        # ... rest of drawing logic
```

### 3. Battle-Logging integrieren

```python
# Nach einem Angriff
def execute_attack(self, attacker, target, move, damage):
    # ... attack logic ...
    
    # Log the attack
    self.battle_log.add_attack_message(
        attacker.name, target.name, move.name, damage,
        is_critical=is_critical,
        is_super_effective=is_super_effective
    )
    
    # Add damage number effect
    self.battle_ui.add_damage_number(
        damage, target.position,
        is_critical=is_critical,
        is_super_effective=is_super_effective
    )
    
    # Trigger visual effects
    if is_critical:
        self.battle_ui.trigger_screen_shake(5, 0.4)
    if is_super_effective:
        self.battle_ui.trigger_flash_effect(0.5)
```

## 🎮 Verwendung

### Grundlegende Battle UI

```python
# Battle UI initialisieren
battle_ui = BattleUI(game)

# Battle starten
battle_ui.init_battle(player_monsters, enemy_monsters)

# Menu-Zustand ändern
battle_ui.set_menu_state(BattleMenuState.MOVE_SELECT)

# Input verarbeiten
result = battle_ui.handle_input(key)
if result:
    if result['action'] == 'move_select':
        move_index = result['move_index']
        # Handle move selection
```

### Battle Logging

```python
# Battle Log initialisieren
battle_log = BattleLog()

# Nachrichten hinzufügen
battle_log.add_message("Ein wilder Monster erscheint!")

# Template-Nachrichten verwenden
battle_log.add_attack_message("Feuerdrache", "Steingolem", "Feuerstoß", 25)

# Status-Effekte loggen
battle_log.add_status_message("Steingolem", "Verbrennung", True)

# Zähmungsversuche loggen
battle_log.add_taming_message("Feuerdrache", "Steingolem", True)

# Export
battle_log.export_to_file("battle_log.txt")
battle_log.export_to_json("battle_log.json")
```

### Styling anpassen

```python
# Theme wechseln
from engine.ui.battle_styles import set_battle_theme

set_battle_theme('dark')      # Dark theme
set_battle_theme('retro')     # Retro gaming theme
set_battle_theme('modern')    # Modern flat design

# Individuelle Anpassungen
from engine.ui.battle_styles import customize_style

customize_style(
    background_color=(30, 30, 40),
    border_color=(100, 100, 120),
    padding=8
)
```

## 🎨 Anpassung

### Neue Nachrichten-Templates hinzufügen

```python
# In battle_log.py, _init_message_templates()
'custom_action': [
    "{actor} führt {action} aus!",
    "Spezialaktion! {actor} macht {action}!",
    "Das war {action} von {actor}!"
]

# Verwendung
battle_log.add_template_message('custom_action', 
                               actor="Feuerdrache", 
                               action="Feuerwirbel")
```

### Neue UI-Komponenten erstellen

```python
class CustomUIComponent:
    def __init__(self, style):
        self.style = style
    
    def draw(self, surface):
        # Custom drawing logic
        pygame.draw.rect(surface, self.style.background_color, 
                        (x, y, width, height))
    
    def handle_input(self, key):
        # Custom input handling
        pass
```

## 🧪 Testing

### Demo starten

```bash
python test_battle_ui.py
```

### Demo-Steuerung
- **SPACE**: Nächste Demo-Aktion
- **TAB**: Menu-Zustände durchlaufen
- **1-5**: Themes wechseln
- **E**: Log als TXT exportieren
- **J**: Log als JSON exportieren
- **Pfeiltasten**: Menus navigieren
- **ESC**: Demo beenden

## 🔍 Debugging

### Battle Log durchsuchen

```python
# Nachrichten nach Kategorie filtern
attack_messages = battle_log.get_messages_by_category(MessageCategory.ATTACK)

# Nachrichten nach Priorität filtern
critical_messages = battle_log.get_messages_by_priority(MessagePriority.CRITICAL)

# Nachrichten durchsuchen
search_results = battle_log.search_messages("Feuerstoß")
```

### UI-Zustand überprüfen

```python
# Aktuellen Menu-Zustand abfragen
current_state = battle_ui.menu_state

# Nachrichtenanzahl abfragen
message_count = battle_log.get_message_count()

# Style-Informationen abrufen
current_style = get_current_style()
```

## 📊 Performance

### Optimierungen
- **Nachrichten-Limit**: Standardmäßig 100 Nachrichten im Speicher
- **Efficient Rendering**: Nur sichtbare Nachrichten werden gezeichnet
- **Animation Caching**: Effiziente Timer-Verwaltung

### Skalierung
- **Responsive Design**: Funktioniert mit verschiedenen Auflösungen
- **Font-Skalierung**: Automatische Anpassung an Display-Größe
- **Memory Management**: Automatische Bereinigung alter Nachrichten

## 🐛 Bekannte Probleme & Lösungen

### Problem: UI-Komponenten werden nicht angezeigt
**Lösung**: Stellen Sie sicher, dass `battle_ui.draw()` und `battle_log.draw()` aufgerufen werden.

### Problem: Nachrichten werden nicht geloggt
**Lösung**: Überprüfen Sie, ob das BattleLog-Objekt korrekt initialisiert wurde.

### Problem: Styles werden nicht angewendet
**Lösung**: Verwenden Sie `set_battle_theme()` vor der UI-Initialisierung.

## 🔮 Zukünftige Erweiterungen

- **Sound-Integration**: Audio-Feedback für UI-Aktionen
- **Animation-System**: Erweiterte visuelle Effekte
- **Multiplayer-Support**: UI für Online-Kämpfe
- **Accessibility**: Barrierefreie Bedienung
- **Localization**: Mehrsprachige Unterstützung

## 📝 Changelog

### Version 1.0.0
- Grundlegendes Battle UI System
- Battle Logging mit Ruhrpott-Slang
- Style-System mit vordefinierten Themes
- Demo-Anwendung
- Vollständige Dokumentation

## 🤝 Beitragen

1. Fork das Repository
2. Erstelle einen Feature-Branch
3. Implementiere deine Änderungen
4. Teste mit der Demo-Anwendung
5. Erstelle einen Pull Request

## 📄 Lizenz

Dieses Projekt ist Teil von "Untold Story" und unterliegt den gleichen Lizenzbedingungen.

## 🆘 Support

Bei Fragen oder Problemen:
1. Überprüfe diese Dokumentation
2. Teste mit der Demo-Anwendung
3. Überprüfe die Logs auf Fehlermeldungen
4. Erstelle ein Issue im Repository

---

**Entwickelt für Untold Story - Ein 2D RPG im Ruhrpott-Stil** 🎮
