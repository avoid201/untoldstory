# Tile-Integration in Untold Story

## Übersicht
Diese Implementierung integriert alle verfügbaren Sprites und Tiles aus dem `sprites`-Ordner in das Spiel. Es wurden neue Layer-Systeme für Möbel und Dekoration hinzugefügt, die es ermöglichen, detaillierte Innenräume und Außenbereiche zu erstellen.

## Neue Features

### 1. Erweiterte Sprite-Verwaltung
- **Zentralisierter SpriteManager**: Lädt und verwaltet alle Sprites aus dem `sprites`-Ordner
- **Automatisches Laden**: Alle verfügbaren Sprites werden beim Spielstart automatisch geladen
- **Kategorisierte Sprites**: Monster, NPCs, Möbel, Gebäude, Wasser-Animationen und mehr

### 2. Neue Map-Layer
- **Furniture Layer**: Für Möbel und Einrichtungsgegenstände
- **Decoration Layer**: Für Kunstwerke und Dekorationen
- **Erweiterte Layer-Reihenfolge**: `ground` → `decor` → `furniture` → `decoration`

### 3. Neue Tile-IDs
- **21-24**: Computer-Varianten
- **25-28**: Bücherregal-Varianten  
- **29-32**: Zimmerpflanzen-Varianten
- **33-38**: Kunstwerke und Wanddekoration

## Implementierte Dateien

### Core-System
- `engine/graphics/sprite_manager.py` - Zentraler Sprite-Manager
- `engine/graphics/tile_renderer.py` - Erweiterter Tile-Renderer
- `engine/core/game.py` - Integration in die Game-Klasse
- `main.py` - Initialisierung des Sprite-Systems

### Map-Daten
- `data/maps/bergmannsheil.json` - Aktualisierte Karte mit neuen Layern
- `data/maps/kohlenstadt.json` - Erweiterte Karte mit Möbel-Placement
- `data/maps/test_tiles.json` - Test-Karte für neue Features

### Dokumentation
- `SPRITE_DOKUMENTATION.md` - Vollständige Sprite-Dokumentation
- `TILE_INTEGRATION_README.md` - Diese Datei

## Verwendung

### 1. Neue Tiles in Maps hinzufügen
```json
{
  "furniture_placement": [
    {"x": 5, "y": 3, "tile_id": 21, "name": "Computer"}
  ],
  "decoration": [
    {"x": 5, "y": 2, "tile_id": 33, "name": "Kunst"}
  ]
}
```

### 2. Neue Layer in bestehenden Maps
```json
{
  "layers": {
    "furniture": [[0,0,0,0], [0,0,0,0]],
    "decoration": [[0,0,0,0], [0,0,0,0]]
  }
}
```

### 3. Sprite-System im Code verwenden
```python
# Sprite abrufen
sprite = game.sprite_manager.get_sprite("Computer-type-01-00.png")

# Monster-Sprite abrufen
monster_sprite = game.sprite_manager.get_monster_sprite("1")
```

## Technische Details

### Sprite-Loading
- Alle Sprites werden beim Spielstart geladen
- Automatische Skalierung auf 16x16 Pixel
- Fehlerbehandlung für fehlende Assets
- Caching für bessere Performance

### Rendering-Pipeline
- Camera-Culling für effizientes Rendering
- Layer-basierte Rendering-Reihenfolge
- Unterstützung für verschiedene Sprite-Formate (PNG, GIF)

### Tile-Mapping
- Direkte Mapping von Tile-IDs zu Sprite-Namen
- Erweiterbar für neue Tile-Typen
- Fallback auf Placeholder-Tiles

## Debug-Features

### Debug-Modus aktivieren
```python
# In der Game-Klasse
game.tile_renderer.set_debug(True)
```

### Verfügbare Debug-Informationen
- Sprite-Loading-Status
- Tile-Rendering-Details
- Layer-Informationen
- Performance-Metriken

## Nächste Schritte

### Kurzfristig
- [ ] Weitere Maps mit neuen Layern aktualisieren
- [ ] Zusätzliche Sprite-Varianten hinzufügen
- [ ] Animation-System für Wasser-Tiles

### Langfristig
- [ ] Dynamic Sprite-Loading für große Welten
- [ ] Sprite-Atlas-Optimierung
- [ ] Shader-basierte Effekte

## Bekannte Probleme

1. **Sprite-Größen**: Einige Sprites sind größer als 16x16 und werden skaliert
2. **Performance**: Große Maps mit vielen Sprites können Performance-Probleme verursachen
3. **Memory**: Alle Sprites werden im Speicher gehalten

## Support

Bei Problemen oder Fragen zur Tile-Integration:
1. Debug-Modus aktivieren
2. Logs überprüfen
3. Sprite-Dateien auf Korrektheit prüfen
4. Map-JSON-Syntax validieren
