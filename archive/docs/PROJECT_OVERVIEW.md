# Untold Story - Projektübersicht

## 🎮 Projekt-Beschreibung
Untold Story ist ein 2D Top-Down RPG im Ruhrpott-Setting, inspiriert von Pokémon und Dragon Quest Monsters. Das Spiel verwendet Pygame für die Engine und Tiled Map Editor für die Level-Erstellung.

## 🏗️ Architektur

### Engine-Komponenten
- **Core**: Game-Loop, Input-Handling, State-Management
- **World**: Map-System (TMX/TSX), Tile-Management, Entity-System
- **Graphics**: Sprite-Management, Rendering, UI
- **Battle**: Kampfsystem (Monster, Skills, Items)
- **Story**: Dialog-System, Quest-Management

### Datenformat
- **Maps**: Tiled Editor (TMX/TSX Format)
- **Game-Daten**: JSON-basiert (NPCs, Warps, Dialoge)
- **Sprites**: PNG-Dateien mit automatischem Caching

## ✅ Aktuelle Features
- [x] Grundlegendes Map-Rendering mit TMX-Support
- [x] Spieler-Bewegung und Kamera-System
- [x] Sprite-Management mit Caching
- [x] Dialog-System (Grundlagen)
- [x] NPC-System (Grundlagen)
- [x] Warp-System zwischen Maps
- [x] Save/Load System
- [ ] Vollständige TMX-Integration mit allen Layern
- [ ] Pathfinding für NPCs
- [ ] Kampfsystem
- [ ] Quest-System
- [ ] Inventar-System

## 🐛 Bekannte Issues
1. **TMX-Rendering**: Tile-IDs werden manchmal falsch gemappt (Tiled zählt ab 1, Engine ab 0)
2. **Pathfinding**: Noch nicht implementiert
3. **Externe Daten**: JSON-Dateien für NPCs/Warps/Dialoge fehlen noch
4. **Performance**: Layer-Rendering könnte optimiert werden

## 📁 Projekt-Struktur
```
untold_story/
├── main.py                    # Haupteinstiegspunkt
├── engine/                    # Game Engine
│   ├── core/                 # Kern-Komponenten
│   ├── world/                # Map und Entity-System
│   ├── graphics/             # Rendering
│   ├── battle/               # Kampfsystem
│   └── story/                # Story und Dialoge
├── data/
│   ├── maps/                 # Tiled Maps (TMX/TSX)
│   ├── game_data/           # JSON-Konfigurationen
│   └── saves/               # Spielstände
├── assets/
│   └── gfx/                 # Grafiken und Sprites
├── archive/                  # Alte/ungenutzte Dateien
└── tools/                    # Entwickler-Tools
```

## 🗺️ Map-System

### Verfügbare Maps
- `player_house.tmx` - Spielerhaus
- `rival_house.tmx` - Rivalenhaus
- `kohlenstadt.tmx` - Hauptstadt (Kohlenstadt)
- `bergmannsheil.tmx` - Krankenhaus-Bereich
- `museum.tmx` - Museum
- `penny.tmx` - Penny-Markt
- `route1.tmx` - Route 1

### Layer-Struktur
1. **ground** - Basis-Tiles (Gras, Wege, etc.)
2. **decor** - Dekorative Elemente
3. **collision** - Kollisions-Layer (nicht sichtbar)
4. **furniture** - Möbel und Objekte
5. **overlay** - Überlagerungen (Schatten, etc.)

## 🎯 Nächste Schritte
1. ✅ TMX-Parser fertigstellen und Tile-ID-Mapping korrigieren
2. ⏳ Pathfinding-System implementieren
3. ⏳ Externe JSON-Dateien erstellen und integrieren
4. ⏳ NPC-Bewegungsmuster implementieren
5. ⏳ Kampfsystem aktivieren
6. ⏳ Quest-System implementieren

## 🔧 Technische Details

### Dependencies
- Python 3.13+
- pygame-ce 2.5+
- xml.etree (Standard Library)
- pathlib (Standard Library)

### Performance-Ziele
- 60 FPS konstant
- Schnelle Map-Wechsel (<500ms)
- Effizientes Sprite-Caching
- Viewport-Culling für große Maps

## 💬 Ruhrpott-Setting
Das Spiel spielt im Ruhrgebiet mit authentischem Dialekt:
- NPCs sprechen Ruhrpott-Deutsch
- Locations basieren auf echten Orten (Kohlenstadt = Essen, etc.)
- Monster sind industriell/bergbau-inspiriert

## 🐞 Debug-Befehle
- **F1**: Collision-Overlay anzeigen
- **F2**: Tile-IDs anzeigen
- **F3**: FPS-Counter
- **F4**: NPC-Pfade visualisieren
- **F5**: Quick-Save
- **F9**: Quick-Load

## 📝 Entwickler-Notizen
- Immer `python3` verwenden (macOS)
- Virtual Environment aktivieren: `source .venv/bin/activate`
- Tests ausführen: `python3 test_main_game.py`
- Map validieren: `python3 map_validator.py`

---
*Letzte Aktualisierung: August 2025*