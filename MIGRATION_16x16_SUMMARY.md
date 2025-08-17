# Migration auf 16x16 Assets - Zusammenfassung

## Abgeschlossene Änderungen

### ✅ 1. Tile-System auf 16x16 umgestellt
- `engine/world/tiles.py`: TILE_SIZE = 16 (war vorher variabel)
- Alle Grid/Position-Berechnungen verwenden jetzt einheitlich TILE_SIZE

### ✅ 2. SpriteManager für neue Asset-Struktur
- `engine/graphics/sprite_manager.py`: Komplett überarbeitet
- Lädt automatisch aus `assets/gfx/tiles/`, `objects/`, `player/`, `npc/`, `monster/`
- Player-Richtungen: `get_player("up"/"down"/"left"/"right")`
- NPCs: `get_npc("npcA", "right")`
- Tiles/Objects: `get_tile("grass")`, `get_object("tv")`
- Monster: `get_monster("25")` für Dex-ID

### ✅ 3. Player-System angepasst
- `engine/world/player.py`: Verwendet neue SpriteManager-API
- Automatische Sprite-Aktualisierung bei Richtungsänderung
- Hitbox von 56x56 auf 14x14 reduziert (für 16x16 Tiles)
- Geschwindigkeiten angepasst: move_speed=4.0, run_speed=6.0

### ✅ 4. Entity-System aktualisiert
- `engine/world/entity.py`: Frame-Größen von 64x64 auf 16x16 ✅
- Standard-Hitbox von 56x56 auf 14x14 reduziert
- Geschwindigkeit von 240.0 auf 60.0 angepasst
- Fallback-Rechteck von 32x32 auf 16x16

### ✅ 5. Tile-Mapping erneuert
- `data/tile_mapping.json`: Auf neue Asset-Namen angepasst
- Entfernt `_large.png` Suffixe, verwendet direkte Namen ✅
- Vereinfachte Struktur: "grass.png" statt "Grass-flat_large.png" ✅
- Alle 64x64 Referenzen entfernt ✅
- Backup der alten Version als `tile_mapping_old.json`

## Asset-Struktur (bereits vorhanden)
```
assets/gfx/
├── tiles/*.png      # grass, path, wall, roof, ...
├── objects/*.png    # tv, sign, chair, table
├── player/player_{up,down,left,right}.png
├── npc/npc{A,B}_{up,down,left,right}.png
└── monster/<id>.png # 1.png bis 151.png
```

## API-Nutzung im Code

### Tiles/Objects laden:
```python
from engine.graphics.sprite_manager import SpriteManager
sm = SpriteManager.get()

grass_sprite = sm.get_tile("grass")
tv_sprite = sm.get_object("tv")
```

### Player-Richtungen:
```python
# Bei Richtungsänderung:
self.direction = Direction.LEFT
self._update_sprite_for_direction()  # Automatisch im Player implementiert
```

### NPCs:
```python
npc_sprite = sm.get_npc("npcA", "down")
```

### Monster:
```python
pikachu_sprite = sm.get_monster(25)  # oder sm.get_monster("25")
```

## Status: ✅ Komplett
Alle Haupt-Systeme sind auf das einheitliche 16x16 System umgestellt. Das Spiel läuft mit den neuen Assets.
