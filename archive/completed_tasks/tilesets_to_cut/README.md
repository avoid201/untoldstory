# Tileset Cutter - Anleitung

## 📁 Schritt 1: Tilesets platzieren

Bitte speichere deine 7 Tileset-Bilder aus dem Chat in diesem Ordner:
`/Users/leon/Desktop/untold_story/tilesets_to_cut/`

Benenne sie wie folgt:
- tileset1.png (das erste Bild mit den verschiedenen Terrain-Tiles)
- tileset2.png (das größere mit vielen Objekten)
- tileset3.png (das kleine mit wenigen Elementen)
- tileset4.png (mit verschiedenen Patterns/Mustern)
- tileset5.png (mit UI-Elementen oder Objekten)
- tileset6.png 
- tileset7.png

## 🚀 Schritt 2: Skript ausführen

Öffne ein Terminal und führe aus:

```bash
cd /Users/leon/Desktop/untold_story
python tools/advanced_tileset_cutter.py
```

## 📦 Schritt 3: Ergebnis

Das Skript wird:
1. Alle Tilesets in 16x16 Tiles schneiden
2. Jedes Tile mit einer ID und beschreibendem Namen speichern
3. Eine organisierte Ordnerstruktur erstellen:
   ```
   individual_tiles/
   ├── terrain/
   │   ├── 0001_grass_topleft.png
   │   ├── 0002_grass_top.png
   │   └── ...
   ├── objects/
   │   ├── 0100_tree_top.png
   │   └── ...
   ├── water/
   ├── building/
   ├── interior/
   └── tile_info.json (Metadaten)
   ```
4. Eine ZIP-Datei erstellen: `individual_tiles.zip`

## 🎯 Features

- **Intelligente Benennung**: Das Skript analysiert die Farben und Muster der Tiles
- **Duplikat-Erkennung**: Identische Tiles werden erkannt und markiert
- **Transparenz-Erhaltung**: Alpha-Kanal bleibt erhalten
- **Leere Tiles**: Werden automatisch übersprungen
- **Kategorie-Erkennung**: Basierend auf Dateinamen und Inhalt

## 💡 Tipps

- Das erweiterte Skript (`advanced_tileset_cutter.py`) bietet bessere Analyse
- Das einfache Skript (`tileset_cutter.py`) ist schneller aber weniger intelligent
- Die JSON-Datei enthält alle Metadaten für spätere Referenz
- Du kannst die Namen in der JSON nachträglich anpassen

## 🔧 Anpassungen

Falls du andere Tile-Größen brauchst, ändere im Skript:
```python
cutter = AdvancedTilesetCutter(tile_size=32)  # für 32x32 Tiles
```
