# Running Shoes & Map Transitions

## Übersicht

Dieses Dokument beschreibt zwei wichtige Systeme für Untold Story:
1. **Running Shoes Item** - Ermöglicht dem Spieler das Rennen
2. **Map Transition System** - Smooth transitions zwischen Maps

## 1. Running Shoes System

### Übersicht

Das Running Shoes System ist ein optionales Feature, das es dem Spieler ermöglicht, mit der B-Taste zu rennen, ähnlich wie in Pokémon-Spielen.

### Funktionalität

#### Grundfunktionen

- **Rennen aktivieren**: Mit der B-Taste oder Shift-Taste
- **Geschwindigkeits-Boost**: 50% schneller als normales Gehen
- **Story-Integration**: Kann über Story-Flags gesteuert werden
- **Tutorial-System**: Zeigt dem Spieler wie man rennt

#### Methoden

```python
from engine.items.running_shoes import RunningShoes

# Running Shoes geben
RunningShoes.give_running_shoes(game)

# Prüfen ob Rennen möglich
can_run = RunningShoes.can_run(game)

# Prüfen ob Running Shoes erhalten wurden
has_shoes = RunningShoes.check_running_shoes_obtained(game)

# Tutorial anzeigen
RunningShoes.show_running_tutorial(game)

# Geschwindigkeits-Multiplikator abrufen
speed_mult = RunningShoes.get_running_speed_multiplier(game)
```

### Integration

#### In Player.py

```python
# Running Shoes werden automatisch in handle_input() geprüft
run_key_pressed = game.is_key_pressed('run') or game.keys_pressed.get(pygame.K_LSHIFT, False)
self.is_running = run_key_pressed and RunningShoes.can_run(game)
```

#### In Story Events

```python
# Running Shoes als Belohnung geben
def give_running_shoes_reward(game):
    RunningShoes.give_running_shoes(game)
    
    # Optional: Tutorial anzeigen
    RunningShoes.show_running_tutorial(game)
```

### Konfiguration

#### Story Flags

```python
# In story_manager.py
game.story_manager.set_flag('has_running_shoes', True)
game.story_manager.get_flag('has_running_shoes', False)
```

#### Input Mapping

```python
# In input_manager.py
'run': [pygame.K_q, pygame.K_LSHIFT]  # B-Taste oder Shift
```

## 2. Map Transition System

### Übersicht

Das Map Transition System ermöglicht smooth transitions zwischen verschiedenen Maps mit verschiedenen Effekten.

### Transition-Typen

#### 1. Fade Transition (Standard)
- **Verwendung**: Allgemeine Map-Wechsel
- **Effekt**: Fade out → Map wechseln → Fade in
- **Konfiguration**: `transition_type: "fade"`

#### 2. Slide Transition
- **Verwendung**: Seamless route transitions
- **Effekt**: Slide in Bewegungsrichtung
- **Konfiguration**: `transition_type: "slide"`

#### 3. Door Transition
- **Verwendung**: Gebäude betreten/verlassen
- **Effekt**: Tür-Animation + Fade
- **Konfiguration**: `transition_type: "door"`

#### 4. Instant Transition
- **Verwendung**: Schnelle Map-Wechsel
- **Effekt**: Keine Animation
- **Konfiguration**: `transition_type: "instant"`

### Verwendung

#### Grundlegende Transition

```python
from engine.world.map_transition import MapTransition

# Fade transition
MapTransition.fade_transition(game, "map1", "map2", warp_data)

# Slide transition
MapTransition.slide_transition(game, Direction.DOWN, "route1")

# Door transition
MapTransition.door_transition(game, "building1", "entrance")

# Instant transition
MapTransition.instant_transition(game, "map3", spawn_data)
```

#### Automatische Transition-Auswahl

```python
# Transition-Typ wird automatisch aus warp_data bestimmt
warp_data = {
    'target_map': 'route1',
    'transition_type': 'slide',
    'direction': Direction.DOWN,
    'spawn_point': 'south_edge'
}

MapTransition.execute_transition(game, warp_data)
```

### Warp-Konfiguration

#### JSON-Format

```json
{
  "warps": [
    {
      "x": 10,
      "y": 5,
      "to_map": "route1",
      "to_x": 5,
      "to_y": 15,
      "direction": "DOWN",
      "transition_type": "slide",
      "spawn_point": "south_edge"
    },
    {
      "x": 15,
      "y": 8,
      "to_map": "building1",
      "to_x": 8,
      "to_y": 12,
      "direction": "UP",
      "transition_type": "door",
      "spawn_point": "entrance"
    }
  ]
}
```

#### Python-Objekte

```python
# In map_loader.py
class Warp:
    def __init__(self, x: int, y: int, to_map: str, to_x: int, to_y: int, 
                 direction: str = None, transition_type: str = "fade", 
                 spawn_point: str = "default"):
        self.x = x
        self.y = y
        self.to_map = to_map
        self.to_x = to_x
        self.to_y = to_y
        self.direction = direction
        self.transition_type = transition_type
        self.spawn_point = spawn_point
```

### Integration in Field Scene

#### Automatische Transition-Ausführung

```python
def _execute_warp(self, warp: Warp) -> None:
    # Prepare warp data for transition system
    warp_data = {
        'target_map': warp.to_map,
        'spawn_x': warp.to_x,
        'spawn_y': warp.to_y,
        'direction': warp.direction,
        'transition_type': getattr(warp, 'transition_type', 'fade'),
        'spawn_point': getattr(warp, 'spawn_point', 'default')
    }
    
    # Execute transition based on warp type
    MapTransition.execute_transition(self.game, warp_data)
```

### Erweiterte Features

#### Custom Transition-Effekte

```python
class CustomTransition:
    @staticmethod
    def matrix_transition(game, from_map, to_map):
        """Matrix-style transition effect"""
        # Implementiere custom Matrix-Effekt
        pass

# Integration
MapTransition.matrix_transition = CustomTransition.matrix_transition
```

#### Sound-Effekte

```python
def door_transition(game, to_map, spawn_point):
    # Door opening sound
    game.audio_manager.play_sound("door_open.wav")
    
    # Door closing sound
    game.audio_manager.play_sound("door_close.wav")
```

#### Partikel-Effekte

```python
def slide_transition(game, direction, to_map):
    # Dust particles während des Slides
    game.particle_system.create_dust_trail(direction)
```

### Performance-Optimierung

#### Transition-Caching

```python
class TransitionCache:
    def __init__(self):
        self.cached_transitions = {}
    
    def get_transition(self, transition_type):
        if transition_type not in self.cached_transitions:
            self.cached_transitions[transition_type] = self.create_transition(transition_type)
        return self.cached_transitions[transition_type]
```

#### Async Loading

```python
def fade_transition(game, from_map, to_map, warp_data):
    # Start fade out
    game.transition_manager.start_fade_out()
    
    # Load new map in background
    import asyncio
    asyncio.create_task(game.load_map_async(to_map, warp_data))
    
    # Wait for both to complete
    game.transition_manager.wait_for_fade_out()
    game.wait_for_map_load()
    
    # Start fade in
    game.transition_manager.start_fade_in()
```

## Beispiele

### Running Shoes Tutorial

```python
def start_running_tutorial(game):
    # Zeige Tutorial-Dialog
    game.current_scene.dialogue_box.show_text(
        "Tipp: Halte B gedrückt um zu rennen!",
        callback=lambda _: complete_tutorial(game)
    )

def complete_tutorial(game):
    # Gebe Running Shoes
    RunningShoes.give_running_shoes(game)
    
    # Zeige Bestätigung
    game.current_scene.dialogue_box.show_text(
        "Du hast die TURBOSCHUHE erhalten!"
    )
```

### Route Transition

```python
# Seamless transition zwischen Route 1 und Route 2
warp_data = {
    'target_map': 'route2',
    'transition_type': 'slide',
    'direction': Direction.DOWN,
    'spawn_point': 'north_edge'
}

MapTransition.execute_transition(game, warp_data)
```

### Building Entry

```python
# Gebäude betreten mit Tür-Animation
warp_data = {
    'target_map': 'pokemon_center',
    'transition_type': 'door',
    'spawn_point': 'entrance'
}

MapTransition.execute_transition(game, warp_data)
```

## Fehlerbehebung

### Häufige Probleme

1. **Running Shoes funktionieren nicht**: Prüfe Story-Flags und Input-Mapping
2. **Transitions stürzen ab**: Stelle sicher dass alle erforderlichen Methoden implementiert sind
3. **Player landet falsch**: Prüfe spawn_point und spawn_data Konfiguration

### Debug-Modus

```python
# Enable debug output
import logging
logging.basicConfig(level=logging.DEBUG)

# Debug-Informationen in Transitions
print(f"Executing transition: {transition_type}")
print(f"Warp data: {warp_data}")
```

## Fazit

Beide Systeme sind vollständig optional und können einfach aktiviert/deaktiviert werden:

- **Running Shoes**: Fügt authentische Pokémon-Mechanik hinzu
- **Map Transitions**: Ermöglicht professionelle Map-Wechsel

Die Systeme sind modular aufgebaut und können einfach erweitert oder angepasst werden.
