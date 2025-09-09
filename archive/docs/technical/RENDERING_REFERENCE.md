# 🎮 RENDERING-SYSTEM REFERENZ - UNTOLD STORY

## 📁 ORDNERSTRUKTUR

### **ENGINE/GRAPHICS/ - Rendering-Core**
```
engine/graphics/
├── sprite_manager.py      # 🎨 Sprite-Verwaltung & Cache
├── tile_renderer.py       # 🧱 Tile-Rendering & Layer-System
├── render_manager.py      # 🎬 Haupt-Rendering-Koordinator
└── __init__.py
```

### **ENGINE/WORLD/ - Welt & Maps**
```
engine/world/
├── area.py               # 🗺️ Map-Definition & Rendering
├── camera.py             # 📷 Kamera-System & Viewport
├── entity.py             # 👤 Spieler/NPC-Entitäten
└── __init__.py
```

### **ASSETS/GFX/ - 16x16 Grafik-Assets**
```
assets/gfx/
├── tiles/                # 🧱 16×16 Basis-Tiles  
│   ├── grass.png
│   ├── path.png
│   ├── wall.png
│   └── ...
├── objects/              # 🏠 16×16 Möbel & Deko
│   ├── chair.png
│   ├── table.png
│   ├── tv.png
│   └── ...
├── player/               # 🎮 16×16 Player-Sprites
│   ├── player_down.png
│   ├── player_up.png
│   ├── player_left.png
│   └── player_right.png
├── npc/                  # 👥 16×16 NPC-Sprites
│   ├── npcA_down.png
│   ├── npcA_up.png
│   └── ...
└── monster/              # 🐉 16×16 Monster-Sprites
    ├── 1.png bis 151.png
    └── ...
```

### **DATA/ - Spiel-Daten**
```
data/
├── maps/                 # 🗺️ Map-Definitionen
│   ├── player_house.json
│   ├── kohlenstadt.json
│   └── ...
├── tile_mapping.json     # 🔗 Tile-ID ↔ Sprite-Zuordnung
└── ...
```

## 🔄 RENDERING-PIPELINE

### **1. Sprite-Laden (SpriteManager)**
```
SpriteManager.load_all_sprites()
├── load_base_tiles()     # Basis-Tiles (Gras, Wege, Böden)
├── load_tile_mappings()  # Tile-ID ↔ Sprite-Datei
├── load_monster_sprites() # Monster (1-151)
├── load_npc_sprites()    # NPCs
└── load_player_sprite()  # Spieler
```

### **2. Map-Laden (Area)**
```
Area.__init__()
├── SpriteManager()       # Lazy Loading
├── RenderManager()       # Lazy Loading
└── Map-Daten laden       # JSON → Python-Objekte
```

### **3. Rendering (RenderManager)**
```
RenderManager.render_scene()
├── TileRenderer.render_layer()  # Tiles rendern
├── Entity-Rendering            # Spieler/NPCs
└── UI-Rendering               # Interface
```

## 🎯 WICHTIGE DATEIEN & ZWECKE

### **sprite_manager.py**
- **Hauptaufgabe:** Sprite-Cache & Asset-Management
- **Schlüssel-Methoden:**
  - `load_all_sprites()` - Lädt alle Sprites
  - `get_tile_sprite(tile_id)` - Holt Tile-Sprite
  - `get_cache_info()` - Cache-Status
  - `load_missing_sprites_for_maps()` - Lädt fehlende Sprites

### **tile_renderer.py**
- **Hauptaufgabe:** Tile-Layer-Rendering
- **Schlüssel-Methoden:**
  - `render_layer()` - Rendert Map-Layer
  - `_render_tile()` - Einzelne Tile
  - Debug-Modus (TAB-Taste)
  - `_render_placeholder()` - Rote Platzhalter für fehlende Tiles

### **render_manager.py**
- **Hauptaufgabe:** Rendering-Koordination
- **Schlüssel-Methoden:**
  - `render_scene()` - Haupt-Rendering
  - `set_debug_mode()` - Debug aktivieren
  - `get_sprite_cache_info()` - Sprite-Status

### **area.py**
- **Hauptaufgabe:** Map-Definition & -Verwaltung
- **Schlüssel-Methoden:**
  - `render()` - Map rendern
  - `get_tile_at()` - Tile-Info abrufen
  - Lazy Loading für RenderManager
  - `is_tile_solid()` - Kollisionsprüfung

## 🔧 TECHNISCHE DETAILS

### **Tile-Größen**
- **Alle Sprites:** 16×16 Pixel (GBC-Stil)
- **Monster:** 16×16 Pixel
- **Tiles/Objects:** 16×16 Pixel
- **Player/NPCs:** 16×16 Pixel

### **Tile-ID-System**
- **IDs 1-20:** Basis-Tiles (Gras, Wege, Böden)
- **IDs 21+:** Möbel & Deko (separate Sprite-Dateien)
- **ID 0:** Leerer Tile (durchlässig)

### **Sprite-Cache-Schlüssel**
- **Tiles:** Nach Namen ("grass", "path", "wall")
- **Objects:** Nach Namen ("chair", "table", "tv", "sign")
- **Player:** Nach Richtung ("up", "down", "left", "right")
- **NPCs:** Nach ID und Richtung ("npcA_down", "npcB_up")
- **Monster:** Nach Dex-ID ("1", "2", ..., "151")

### **Fallback-System**
- **Primär:** 16x16 Sprites aus gfx/ Ordnern
- **Fallback:** Magenta Platzhalter für fehlende Sprites
- **Debug:** Sprite-Name wird bei Fehlern ausgegeben

## 🚀 SCHNELLSTART FÜR NEUE CHATS

```python
# Schnellstart für Rendering-System
from engine.graphics.sprite_manager import SpriteManager
from engine.world.area import Area
from engine.graphics.render_manager import RenderManager
import json

# Sprites laden
sm = SpriteManager()
print(f"Sprites geladen: {sm.get_cache_info()['total_sprites']}")

# Map laden
with open('data/maps/player_house.json', 'r') as f:
    map_data = json.load(f)
area = Area(**map_data)

# Rendering starten
rm = RenderManager()
rm.set_debug_mode(True)  # Debug aktivieren
```

## 🗺️ AKTUELLE MAPS

### **Player House ("Dein Zuhause")**
- **Größe:** 10×8 Tiles
- **Tile-IDs:** [1, 7, 9]
  - **ID 1:** Gras (grass.png - 16x16)
  - **ID 7:** Boden (wood_floor.png - 16x16)
  - **ID 9:** Boden (carpet.png - 16x16)

### **Kohlenstadt**
- **Größe:** 32×32 Tiles
- **Tile-IDs:** [1, 2, 4]
  - **ID 1:** Gras (grass.png - 16x16)
  - **ID 2:** Weg (path.png - 16x16)
  - **ID 4:** Kiesweg (gravel.png - 16x16)

## 🔍 DEBUG & FEHLERSUCHE

### **Debug-Modus aktivieren**
```python
rm = RenderManager()
rm.set_debug_mode(True)  # TAB-Taste für Debug-Info
```

### **Sprite-Cache prüfen**
```python
sm = SpriteManager()
info = sm.get_cache_info()
print(f"Gesamt: {info['total_sprites']} Sprites")
print(f"Tile-Mappings: {info['tile_mappings']}")
print(f"Monster: {info['monster_sprites']}")
print(f"NPCs: {info['npc_sprites']}")
```

### **Fehlende Tiles identifizieren**
```python
# Prüfe fehlende Tiles für Maps
sm.load_missing_sprites_for_maps()
```

## ⚠️ BEKANNTE PROBLEME & LÖSUNGEN

### **Zirkulärer Import**
- **Problem:** `area.py` importiert `render_manager.py`
- **Lösung:** Lazy Loading mit `@property` implementiert

### **Fehlende Sprites**
- **Problem:** Sprites nicht im gfx/ Ordner gefunden
- **Lösung:** Automatisches Fallback zu Magenta-Platzhalter

### **pygame.display nicht initialisiert**
- **Problem:** Sprites können nicht geladen werden
- **Lösung:** Robuste Sprite-Lade-Logik implementiert

## 📝 WICHTIGE ERINNERUNGEN

- **Alle Sprites werden automatisch geladen** beim Start
- **Fallback-System** für fehlende Sprites
- **Debug-Modus** mit TAB-Taste
- **Lazy Loading** für RenderManager
- **271+ Sprites** im Cache verfügbar

---

**Letzte Aktualisierung:** $(date)
**Status:** ✅ Rendering-System funktionsfähig
**Nächster Schritt:** Spiel starten und Maps rendern
