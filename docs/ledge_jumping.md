# Ledge Jumping System

## Übersicht

Das Ledge Jumping System ist ein optionales Feature für Untold Story, das es dem Spieler ermöglicht, über bestimmte Klippen (Ledges) zu springen, ähnlich wie in Pokémon-Spielen.

## Funktionalität

### Ledge-Tile-IDs

Das System verwendet spezielle Tile-IDs in der Collision-Layer:

- **20**: LEDGE_DOWN - Klippe nach unten
- **21**: LEDGE_LEFT - Klippe nach links  
- **22**: LEDGE_RIGHT - Klippe nach rechts
- **23**: LEDGE_UP - Klippe nach oben

### Funktionsweise

1. **Erkennung**: Der Spieler kann nur in die richtige Richtung über eine Klippe springen
2. **Animation**: Der Sprung verwendet eine parabolische Kurve für realistische Bewegung
3. **Geschwindigkeit**: Ledge-Jumps sind 50% schneller als normales Rennen
4. **Landung**: Nach dem Sprung landet der Spieler 2 Tiles in Sprungrichtung

## Verwendung

### In Maps

```json
{
  "layers": {
    "collision": [
      [0, 0, 0, 0],
      [0, 0, 20, 0],  // Klippe nach unten
      [0, 0, 0, 0],
      [0, 0, 0, 0]
    ]
  }
}
```

### Im Code

```python
from engine.world.ledge_handler import LedgeHandler

# Prüfen ob Ledge-Jump möglich
can_jump = LedgeHandler.can_jump_ledge(
    player_tile=(5, 5),
    direction=Direction.DOWN,
    collision_layer=collision_layer
)

# Ledge-Jump ausführen
if can_jump:
    LedgeHandler.execute_ledge_jump(player, target_x, target_y)
```

## Konfiguration

### Sprite-Animationen

Füge Jump-Animationen zu deinem Player-Spritesheet hinzu:

```python
animations={
    'jump_down': [16, 17, 18, 19],   # Jump frames
    'jump_up': [20, 21, 22, 23],
    'jump_left': [24, 25, 26, 27],
    'jump_right': [28, 29, 30, 31],
}
```

### Geschwindigkeit anpassen

```python
# In Player.__init__()
self.jump_speed = self.run_speed * 1.5  # Standard: 50% schneller
```

## Erweiterte Features

### Sound-Effekte

```python
def execute_ledge_jump(player, target_x, target_y):
    # Jump sound abspielen
    resources.play_sound("jump.wav")
    
    # Standard-Ledge-Jump ausführen
    LedgeHandler.execute_ledge_jump(player, target_x, target_y)
```

### Partikel-Effekte

```python
def execute_ledge_jump(player, target_x, target_y):
    # Dust particles beim Landen
    if hasattr(player.game, 'particle_system'):
        player.game.particle_system.create_dust_cloud(
            target_x * TILE_SIZE, 
            target_y * TILE_SIZE
        )
    
    LedgeHandler.execute_ledge_jump(player, target_x, target_y)
```

## Fehlerbehebung

### Häufige Probleme

1. **Spieler springt nicht**: Prüfe ob Ledge-Tile-IDs korrekt gesetzt sind
2. **Animation springt**: Stelle sicher dass Jump-Sprites im Spritesheet vorhanden sind
3. **Kollision nach Sprung**: Prüfe ob Landing-Tile frei ist

### Debug-Modus

```python
# In Player._can_jump_ledge()
print(f"Checking ledge jump: tile=({x}, {y}), direction={direction}")
print(f"Front tile: {front_tile}")
```

## Beispiele

### Einfache Klippe

```
[0] [0] [0]
[0] [P] [20]  # P = Player, 20 = Ledge Down
[0] [0] [0]
```

### Mehrere Klippen

```
[0] [21] [0] [0]  # 21 = Ledge Left
[0] [P]  [0] [0]  # P = Player
[0] [0]  [20] [0] # 20 = Ledge Down
[0] [0]  [0] [0]
```

Das System ist vollständig optional und kann einfach aktiviert/deaktiviert werden, indem die entsprechenden Tile-IDs in der Collision-Layer gesetzt werden.
