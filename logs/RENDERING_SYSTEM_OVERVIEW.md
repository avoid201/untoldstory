# 🎮 **RENDERING-SYSTEM ÜBERSICHT - UNTOLD STORY**

## 📁 **ORDNERSTRUKTUR**

```
untold_story/
├── engine/
│   ├── graphics/           # 🎨 Rendering-Engine
│   │   ├── sprite_manager.py      # Sprite-Verwaltung
│   │   ├── tile_renderer.py       # Tile-Rendering
│   │   ├── render_manager.py      # Rendering-Koordination
│   │   └── test_sprite_manager.py # Tests
│   ├── scenes/             # 🎭 Spielszenen
│   │   ├── field_scene.py         # Hauptspielwelt
│   │   ├── battle_scene.py        # Kampfszenen
│   │   ├── start_scene.py         # Startbildschirm
│   │   ├── main_menu_scene.py     # Hauptmenü
│   │   ├── pause_scene.py         # Pause-Menü
│   │   └── starter_scene.py       # Starter-Auswahl
│   └── world/              # 🌍 Spielwelt
│       ├── area.py                # Gebietsverwaltung
│       ├── entity.py              # Spielobjekte
│       └── camera.py              # Kamera-System
├── sprites/                 # 🖼️ Sprite-Assets
│   ├── Constructed/         # Möbel & Deko (21-189)
│   ├── monsters/            # Monster-Sprites
│   ├── npcs/                # NPC-Sprites
│   ├── player.png           # Spieler-Sprite
│   └── *_large.png          # Basis-Tiles (1-20)
├── assets/                  # 🎵 Medien-Assets
│   ├── gfx/                 # Grafiken
│   ├── bgm/                 # Hintergrundmusik
│   └── sfx/                 # Soundeffekte
└── data/                    # 📊 Spieledaten
    ├── tile_mapping.json    # Tile-ID ↔ Sprite-Mapping
    ├── maps/                # Kartendaten
    ├── monsters.json        # Monster-Daten
    └── moves.json           # Angriffs-Daten
```

## 🔧 **RENDERING-ARCHITEKTUR**

### **1. SpriteManager (Zentrale Sprite-Verwaltung)**
```python
# engine/graphics/sprite_manager.py
class SpriteManager:
    """Verwaltet alle Sprites und Tiles für das Spiel"""
    
    # Singleton-Pattern für globale Sprite-Verwaltung
    _instance = None
    
    # Sprite-Caches
    sprite_cache: Dict[str, pygame.Surface]        # Alle Sprites
    tile_mappings: Dict[str, TileInfo]             # Tile-Informationen
    monster_sprites: Dict[str, pygame.Surface]     # Monster-Sprites
    npc_sprites: Dict[str, pygame.Surface]         # NPC-Sprites
    
    # Konfiguration
    tile_size = 64                                 # Tile-Größe in Pixeln
```

**Funktionen:**
- ✅ **280 Sprites geladen** (Basis-Tiles + Constructed + Monster + NPCs)
- ✅ **98 Tile-Mappings** aus `tile_mapping.json`
- ✅ **Automatisches Sprite-Loading** aus allen Unterordnern
- ✅ **Fallback-System** für fehlende Sprites

### **2. TileRenderer (Tile-Rendering-Engine)**
```python
# engine/graphics/tile_renderer.py
class TileRenderer:
    """Rendert Tiles aus dem SpriteManager"""
    
    def render_layer(self, screen, layer_data, camera_offset, layer_name):
        # Rendert eine Map-Layer mit dem neuen Sprite-System
        # Optimiert: Nur sichtbare Tiles werden gerendert
        # Fallback: Platzhalter für fehlende Tiles
```

**Funktionen:**
- ✅ **Optimiertes Rendering** (nur sichtbare Tiles)
- ✅ **Kamera-Offset-Unterstützung**
- ✅ **Platzhalter-System** für fehlende Tiles
- ✅ **Debug-Modus** für Entwicklung

### **3. RenderManager (Rendering-Koordination)**
```python
# engine/graphics/render_manager.py
class RenderManager:
    """Verwaltet alle Rendering-Operationen mit korrekter Z-Order-Behandlung"""
    
    # Rendering-Layer mit Z-Index
    layers = {
        "background": 0,      # Hintergrund
        "ground": 100,        # Boden
        "decor": 200,         # Dekoration
        "furniture": 300,     # Möbel
        "entities": 400,      # Spieler, NPCs
        "overhang": 500,      # Überhang (Bäume, etc.)
        "decoration": 600,    # Dekoration
        "ui": 1000,           # UI-Elemente
        "dialogue": 1100      # Dialog-Boxen
    }
```

**Funktionen:**
- ✅ **Z-Order-Management** für korrekte Überlagerung
- ✅ **Layer-basierte Rendering** für verschiedene Spielobjekte
- ✅ **Entity-Management** für bewegliche Objekte
- ✅ **UI-Integration** für Benutzeroberfläche

## 🎯 **TILE-SYSTEM**

### **Tile-Kategorien:**
1. **Basis-Tiles (ID 1-20)**: Grundlegende Landschaft
   - `1`: Gras (Grass-flat_large.png)
   - `2`: Weg (Path_large.png)
   - `5`: Schrank (Cabnet-00_large.png)
   - `7`: TV (TV-type-01-00_large.png)

2. **Constructed-Sprites (ID 21-189)**: Möbel & Deko
   - `21-24`: Computer-Set
   - `25-28`: Bücherregal-Set
   - `29-32`: Zimmerpflanzen-Set
   - `70-73`: Hocker-Set
   - `90-93`: Herd-Set
   - `150-157`: Bett-Set

### **Tile-Mapping-System:**
```json
// data/tile_mapping.json
{
  "1": {
    "name": "Grass-flat",
    "sprite_file": "Grass-flat_large.png",
    "category": "terrain",
    "description": "Flaches Gras"
  },
  "21": {
    "name": "Computer-type-01-00",
    "sprite_file": "Computer-type-01-00_large.png",
    "category": "furniture",
    "description": "Computer Teil 1"
  }
}
```

## 🗺️ **MAP-RENDERING**

### **Map-Struktur:**
```json
// data/maps/player_house.json
{
  "name": "Dein Zuhause",
  "size": [10, 8],
  "layers": {
    "ground": [[1,1,1,1,1,1,1,1,1,1], ...],
    "decor": [[0,0,0,0,0,0,0,0,0,0], ...],
    "collision": [[0,0,0,0,0,0,0,0,0,0], ...]
  },
  "furniture_placement": [...],
  "decoration": [...]
}
```

### **Rendering-Pipeline:**
1. **Map laden** → JSON-Daten parsen
2. **Layer rendern** → Ground → Decor → Collision
3. **Möbel platzieren** → Furniture-Placement-Array
4. **Dekorationen** → Decoration-Array
5. **Entities** → Spieler, NPCs, Monster

## 🖼️ **SPRITE-LOADING-SYSTEM**

### **Automatisches Sprite-Loading:**
```python
def load_all_sprites(self):
    """Lädt alle Sprites automatisch"""
    
    # 1. Tile-Mappings laden
    self.load_tile_mappings()           # 98 Mappings
    
    # 2. Basis-Tiles laden
    self.load_base_tiles()              # 13 Basis-Tiles
    
    # 3. Constructed-Sprites laden
    self.load_constructed_sprites()     # 83 Möbel/Deko
    
    # 4. Monster-Sprites laden
    self.load_monster_sprites()         # 151 Monster
    
    # 5. NPC-Sprites laden
    self.load_npc_sprites()             # 10 NPCs
    
    # 6. Player-Sprite laden
    self.load_player_sprite()           # 1 Spieler
```

### **Sprite-Cache-Struktur:**
```python
sprite_cache = {
    # Tile-IDs als Strings
    "1": Grass-flat_large.png,
    "21": Computer-type-01-00_large.png,
    
    # Dateinamen als Fallback
    "Grass-flat_large.png": Grass-flat_large.png,
    "Computer-type-01-00_large.png": Computer-type-01-00_large.png,
    
    # Spezielle Sprites
    "player": player.png,
    "monster_001": monster_001.png
}
```

## 🚀 **PERFORMANCE-OPTIMIERUNGEN**

### **Rendering-Optimierungen:**
1. **Viewport-Culling**: Nur sichtbare Tiles werden gerendert
2. **Sprite-Caching**: Alle Sprites werden einmal geladen und gecacht
3. **Layer-System**: Effiziente Z-Order-Behandlung
4. **Batch-Rendering**: Tiles werden in Gruppen gerendert

### **Memory-Management:**
1. **Singleton-Pattern**: Ein SpriteManager für das gesamte Spiel
2. **Lazy-Loading**: Sprites werden bei Bedarf geladen
3. **Automatic Cleanup**: Platzhalter werden automatisch erstellt
4. **Error-Handling**: Graceful Degradation bei fehlenden Assets

## 🔍 **DEBUG-FEATURES**

### **Debug-Modi:**
- **SpriteManager Debug**: Zeigt geladene Sprites an
- **TileRenderer Debug**: Zeigt Rendering-Informationen
- **RenderManager Debug**: Zeigt Layer-Informationen
- **Performance-Monitoring**: FPS und Rendering-Zeiten

### **Fallback-System:**
- **Platzhalter-Tiles**: Magenta-Tiles mit Tile-ID für fehlende Sprites
- **Ähnliche Dateien**: Zeigt verfügbare Alternativen an
- **Automatische Reparatur**: Versucht fehlende Sprites zu finden

## 📊 **STATISTIKEN**

- **Gesamt-Sprites**: 280
- **Tile-Mappings**: 98
- **Basis-Tiles**: 13
- **Constructed-Sprites**: 83
- **Monster-Sprites**: 151
- **NPC-Sprites**: 10
- **Player-Sprites**: 1
- **Tile-Größe**: 64x64 Pixel
- **Unterstützte Formate**: PNG
- **Cache-System**: Vollständig im RAM

## 🎯 **VERWENDETE TECHNOLOGIEN**

- **Python 3.13.5**: Moderne Python-Version
- **pygame-ce 2.5+**: Optimierte pygame-Version
- **JSON**: Datenformat für Konfiguration
- **PNG**: Grafikformat für Sprites
- **Singleton-Pattern**: Globale Ressourcenverwaltung
- **Layer-System**: Z-Order-Management
- **Viewport-Culling**: Performance-Optimierung

## 🔧 **ENTWICKLUNGS-FEATURES**

- **Debug-Modi**: Für Entwicklung und Fehlersuche
- **Fallback-System**: Graceful Degradation
- **Performance-Monitoring**: Überwachung der Rendering-Performance
- **Automatische Reparatur**: Versucht Probleme selbst zu lösen
- **Umfangreiche Logging**: Detaillierte Informationen über den Ladevorgang

---

**Das Rendering-System ist vollständig funktional und optimiert für 2D-RPGs mit pygame-ce! 🎮✨**

*Erstellt für Untold Story - Ein 2D-RPG im Ruhrpott-Setting*
