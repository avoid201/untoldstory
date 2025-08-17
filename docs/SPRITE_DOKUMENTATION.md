# Sprite & Tile Dokumentation - Untold Story

Diese Dokumentation listet alle verfügbaren Sprites und Tiles im Spiel auf, außer den Monstern.

## 📋 Übersicht der ID-Bereiche

- **0-53**: Grundtiles (Ground, Interior, Terrain, Water, Building)
- **100-118**: Objekte (transparent, werden über Tiles gerendert)
- **200-203**: Player Sprites
- **210-265**: NPC Sprites (alle 4 Richtungen)

---

## 🟢 GROUND TILES (IDs 0-18)

### Grass Varianten
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 0 | Grass_1 | `grass_1.png` | Gras Variante 1 - begehbar |
| 1 | Grass_2 | `grass_2.png` | Gras Variante 2 - begehbar |
| 2 | Grass_3 | `grass_3.png` | Gras Variante 3 - begehbar |
| 3 | Grass_4 | `grass_4.png` | Gras Variante 4 - begehbar |
| 4 | Grass | `grass.png` | Gras - begehbar |

### Tall Grass Varianten
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 5 | Tall_Grass_1 | `tall_grass_1.png` | Hohes Gras Variante 1 - **nicht begehbar** |
| 6 | Tall_Grass_2 | `tall_grass_2.png` | Hohes Gras Variante 2 - **nicht begehbar** |
| 7 | Tall_Grass | `tall_grass.png` | Hohes Gras - **nicht begehbar** |

### Dirt Varianten
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 8 | Dirt_1 | `dirt_1.png` | Erde Variante 1 - begehbar |
| 9 | Dirt_2 | `dirt_2.png` | Erde Variante 2 - begehbar |

### Path Varianten
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 10 | Path_1 | `path_1.png` | Weg Variante 1 - begehbar |
| 11 | Path_2 | `path_2.png` | Weg Variante 2 - begehbar |
| 12 | Path | `path.png` | Weg - begehbar |

### Gravel Varianten
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 13 | Gravel_1 | `gravel_1.png` | Kies Variante 1 - begehbar |
| 14 | Gravel_2 | `gravel_2.png` | Kies Variante 2 - begehbar |
| 15 | Gravel | `gravel.png` | Kies - begehbar |

### Sand & Snow
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 16 | Sand_1 | `sand_1.png` | Sand Variante 1 - begehbar |
| 17 | Sand_2 | `sand_2.png` | Sand Variante 2 - begehbar |
| 18 | Snow | `snow.png` | Schnee - begehbar |

---

## 🏠 INTERIOR TILES (IDs 19-21)

| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 19 | Wood_Floor | `wood_floor.png` | Holzboden - begehbar |
| 20 | Stone_Floor | `stone_floor.png` | Steinboden - begehbar |
| 21 | Carpet | `carpet.png` | Teppich - begehbar |

---

## 🌲 TERRAIN TILES (IDs 22-35)

### Bush Varianten
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 22 | Bush_1 | `bush_1.png` | Busch Variante 1 - **nicht begehbar** |
| 23 | Bush_2 | `bush_2.png` | Busch Variante 2 - **nicht begehbar** |
| 24 | Bush | `bush.png` | Busch - **nicht begehbar** |

### Rock Varianten
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 25 | Rock_1 | `rock_1.png` | Fels Variante 1 - **nicht begehbar** |
| 26 | Rock_2 | `rock_2.png` | Fels Variante 2 - **nicht begehbar** |
| 27 | Rock | `rock.png` | Fels - **nicht begehbar** |

### Flowers
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 28 | Flower_Red | `flower_red.png` | Rote Blume - begehbar |
| 29 | Flower_Blue | `flower_blue.png` | Blaue Blume - begehbar |

### Terrain Features
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 30 | Stump | `stump.png` | Baumstumpf - **nicht begehbar** |
| 31 | Ledge | `ledge.png` | Klippe - **nicht begehbar** (außer Sprung) |
| 32 | Cliff_Face | `cliff_face.png` | Klippenwand - **nicht begehbar** |

### Stairs
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 33 | Stairs_H | `stairs_h.png` | Treppe horizontal - begehbar |
| 34 | Stairs_V | `stairs_v.png` | Treppe vertikal - begehbar |
| 35 | Stairs | `stairs.png` | Treppe - begehbar |

---

## 💧 WATER TILES (IDs 36-45)

### Water Varianten
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 36 | Water_1 | `water_1.png` | Wasser Variante 1 - **nicht begehbar** |
| 37 | Water_2 | `water_2.png` | Wasser Variante 2 - **nicht begehbar** |

### Water Edges
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 38 | Water_Edge_N | `water_edge_n.png` | Wasserrand Nord - **nicht begehbar** |
| 39 | Water_Edge_S | `water_edge_s.png` | Wasserrand Süd - **nicht begehbar** |
| 40 | Water_Edge_W | `water_edge_w.png` | Wasserrand West - **nicht begehbar** |
| 41 | Water_Edge_E | `water_edge_e.png` | Wasserrand Ost - **nicht begehbar** |

### Water Corners
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 42 | Water_Corner_NE | `water_corner_ne.png` | Wasserecke Nordost - **nicht begehbar** |
| 43 | Water_Corner_NW | `water_corner_nw.png` | Wasserecke Nordwest - **nicht begehbar** |
| 44 | Water_Corner_SE | `water_corner_se.png` | Wasserecke Südost - **nicht begehbar** |
| 45 | Water_Corner_SW | `water_corner_sw.png` | Wasserecke Südwest - **nicht begehbar** |

---

## 🏗️ BUILDING TILES (IDs 46-53)

### Walls
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 46 | Wall_Brick | `wall_brick.png` | Ziegelwand - **nicht begehbar** |
| 47 | Wall_Plaster | `wall_plaster.png` | Putzwand - **nicht begehbar** |
| 48 | Wall | `wall.png` | Wand - **nicht begehbar** |

### Roofs
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 49 | Roof_Red | `roof_red.png` | Rotes Dach - **nicht begehbar** |
| 50 | Roof_Blue | `roof_blue.png` | Blaues Dach - **nicht begehbar** |
| 51 | Roof_Ridge | `roof_ridge.png` | Dachfirst - **nicht begehbar** |
| 52 | Roof | `roof.png` | Dach - **nicht begehbar** |

### Special
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 53 | Warp_Carpet | `warp_carpet.png` | Warp-Teppich - begehbar |

---

## 🎯 OBJECTS (IDs 100-118) - Transparent

### Terrain Objects
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 100 | Fence_H | `fence_h.png` | Zaun horizontal - **nicht begehbar**, transparent |
| 101 | Fence_V | `fence_v.png` | Zaun vertikal - **nicht begehbar**, transparent |

### Building Objects
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 102 | Window | `window.png` | Fenster - begehbar, transparent |
| 103 | Door | `door.png` | Tür - begehbar, transparent |
| 104 | Sign | `sign.png` | Schild - begehbar, transparent |

### Interior Objects
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 105 | Table | `table.png` | Tisch - **nicht begehbar**, transparent |
| 106 | Chair | `chair.png` | Stuhl - **nicht begehbar**, transparent |
| 107 | Bed | `bed.png` | Bett - **nicht begehbar**, transparent |
| 108 | Bookshelf | `bookshelf.png` | Bücherregal - **nicht begehbar**, transparent |
| 109 | TV | `tv.png` | Fernseher - **nicht begehbar**, transparent |
| 110 | Potted_Plant | `potted_plant.png` | Topfpflanze - **nicht begehbar**, transparent |

### Misc Objects
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 111 | Crate | `crate.png` | Kiste - **nicht begehbar**, transparent |
| 112 | Barrel | `barrel.png` | Fass - **nicht begehbar**, transparent |
| 113 | Lamp_Post | `lamp_post.png` | Laternenpfahl - **nicht begehbar**, transparent |
| 114 | Mailbox | `mailbox.png` | Briefkasten - **nicht begehbar**, transparent |
| 115 | Well | `well.png` | Brunnen - **nicht begehbar**, transparent |
| 116 | Gravestone | `gravestone.png` | Grabstein - **nicht begehbar**, transparent |
| 117 | Boulder | `boulder.png` | Felsbrocken - **nicht begehbar**, transparent |
| 118 | Tree_Small | `tree_small.png` | Kleiner Baum - **nicht begehbar**, transparent |

---

## 👤 SPRITES (IDs 200+)

### Player Sprites
| ID | Name | Datei | Beschreibung |
|----|------|--------|--------------|
| 200 | Player_Down | `player_down.png` | Spieler schaut nach unten |
| 201 | Player_Up | `player_up.png` | Spieler schaut nach oben |
| 202 | Player_Left | `player_left.png` | Spieler schaut nach links |
| 203 | Player_Right | `player_right.png` | Spieler schaut nach rechts |

### NPC Sprites (alle 4 Richtungen: down, up, left, right)

#### Villager M (IDs 210-213)
| ID | Richtung | Datei |
|----|----------|--------|
| 210 | Down | `villager_m_down.png` |
| 211 | Up | `villager_m_up.png` |
| 212 | Left | `villager_m_left.png` |
| 213 | Right | `villager_m_right.png` |

#### Villager F (IDs 214-217)
| ID | Richtung | Datei |
|----|----------|--------|
| 214 | Down | `villager_f_down.png` |
| 215 | Up | `villager_f_up.png` |
| 216 | Left | `villager_f_left.png` |
| 217 | Right | `villager_f_right.png` |

#### Guard (IDs 218-221)
| ID | Richtung | Datei |
|----|----------|--------|
| 218 | Down | `guard_down.png` |
| 219 | Up | `guard_up.png` |
| 220 | Left | `guard_left.png` |
| 221 | Right | `guard_right.png` |

#### Scientist (IDs 222-225)
| ID | Richtung | Datei |
|----|----------|--------|
| 222 | Down | `scientist_down.png` |
| 223 | Up | `scientist_up.png` |
| 224 | Left | `scientist_left.png` |
| 225 | Right | `scientist_right.png` |

#### Nurse (IDs 226-229)
| ID | Richtung | Datei |
|----|----------|--------|
| 226 | Down | `nurse_down.png` |
| 227 | Up | `nurse_up.png` |
| 228 | Left | `nurse_left.png` |
| 229 | Right | `nurse_right.png` |

#### Merchant (IDs 230-233)
| ID | Richtung | Datei |
|----|----------|--------|
| 230 | Down | `merchant_down.png` |
| 231 | Up | `merchant_up.png` |
| 232 | Left | `merchant_left.png` |
| 233 | Right | `merchant_right.png` |

#### Fisher (IDs 234-237)
| ID | Richtung | Datei |
|----|----------|--------|
| 234 | Down | `fisher_down.png` |
| 235 | Up | `fisher_up.png` |
| 236 | Left | `fisher_left.png` |
| 237 | Right | `fisher_right.png` |

#### Biker (IDs 238-241)
| ID | Richtung | Datei |
|----|----------|--------|
| 238 | Down | `biker_down.png` |
| 239 | Up | `biker_up.png` |
| 240 | Left | `biker_left.png` |
| 241 | Right | `biker_right.png` |

#### Ranger (IDs 242-245)
| ID | Richtung | Datei |
|----|----------|--------|
| 242 | Down | `ranger_down.png` |
| 243 | Up | `ranger_up.png` |
| 244 | Left | `ranger_left.png` |
| 245 | Right | `ranger_right.png` |

#### Miner (IDs 246-249)
| ID | Richtung | Datei |
|----|----------|--------|
| 246 | Down | `miner_down.png` |
| 247 | Up | `miner_up.png` |
| 248 | Left | `miner_left.png` |
| 249 | Right | `miner_right.png` |

#### Monk (IDs 250-253)
| ID | Richtung | Datei |
|----|----------|--------|
| 250 | Down | `monk_down.png` |
| 251 | Up | `monk_up.png` |
| 252 | Left | `monk_left.png` |
| 253 | Right | `monk_right.png` |

#### Kid (IDs 254-257)
| ID | Richtung | Datei |
|----|----------|--------|
| 254 | Down | `kid_down.png` |
| 255 | Up | `kid_up.png` |
| 256 | Left | `kid_left.png` |
| 257 | Right | `kid_right.png` |

#### NPC A (IDs 258-261)
| ID | Richtung | Datei |
|----|----------|--------|
| 258 | Down | `npcA_down.png` |
| 259 | Up | `npcA_up.png` |
| 260 | Left | `npcA_left.png` |
| 261 | Right | `npcA_right.png` |

#### NPC B (IDs 262-265)
| ID | Richtung | Datei |
|----|----------|--------|
| 262 | Down | `npcB_down.png` |
| 263 | Up | `npcB_up.png` |
| 264 | Left | `npcB_left.png` |
| 265 | Right | `npcB_right.png` |

---

## 🔧 Verwendung im Code

### Python Konstanten importieren
```python
from engine.world.tile_ids import (
    GRASS_1, TALL_GRASS, WALL_BRICK,
    PLAYER_DOWN, NPC_VILLAGER_M_BASE
)
```

### NPC Sprite ID berechnen
```python
from engine.world.tile_ids import get_npc_sprite_id

# NPC nach unten schauend
npc_id = get_npc_sprite_id("villager_m", "down")  # Gibt 210 zurück

# NPC nach rechts schauend
npc_id = get_npc_sprite_id("guard", "right")      # Gibt 221 zurück
```

### Tile-Eigenschaften prüfen
```python
from engine.world.tile_ids import is_solid_tile, is_transparent_tile, get_tile_category

# Prüfen ob Tile begehbar ist
if is_solid_tile(GRASS_1):      # False (begehbar)
    print("Nicht begehbar")

if is_solid_tile(TALL_GRASS):   # True (nicht begehbar)
    print("Nicht begehbar")

# Prüfen ob Tile transparent ist
if is_transparent_tile(WINDOW):  # True
    print("Wird als Object gerendert")

# Kategorie ermitteln
category = get_tile_category(GRASS_1)  # "ground"
```

---

## 📁 Dateistruktur

```
assets/gfx/
├── tiles/          # Grundtiles (IDs 0-53)
├── objects/        # Transparente Objekte (IDs 100-118)
├── player/         # Player Sprites (IDs 200-203)
├── npc/            # NPC Sprites (IDs 210-265)
└── monster/        # Monster Sprites (nicht in dieser Dokumentation)
```

---

## 🎨 Rendering-Layers

1. **Base Layer**: Grundtiles aus `tiles/` Ordner
2. **Object Layer**: Transparente Objekte aus `objects/` Ordner (werden über Tiles gerendert)
3. **Sprite Layer**: Player und NPCs (werden über allem anderen gerendert)

---

## 📝 Hinweise

- **Transparente Tiles** (IDs 100-118) werden als separate Layer über den Grundtiles gerendert
- **Nicht begehbare Tiles** sind für Pathfinding relevant
- **Alle Sprites** haben 4 Richtungen (down, up, left, right)
- **Monster-Sprites** sind nicht in dieser Dokumentation enthalten
