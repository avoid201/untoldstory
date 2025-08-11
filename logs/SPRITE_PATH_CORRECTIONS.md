# Sprite-Pfad-Korrekturen für Untold Story

## 🔧 **Korrigierte Probleme:**

### 1. **Inkonsistente _large Sprite-Behandlung:**
- **Vorher:** `_large.png` Dateien wurden geladen, aber ohne `_large` im Cache gespeichert
- **Nachher:** `_large.png` Dateien werden mit vollständigem Namen im Cache gespeichert
- **Betroffene Datei:** `engine/graphics/sprite_manager.py`

### 2. **Vereinheitlichte Sprite-Pfade:**
- **Player-Sprites:** `"player.png"` (über SpriteManager)
- **NPC-Sprites:** `"npcs/{npc_id}.png"` (über SpriteManager)
- **Monster-Sprites:** `"monsters/{monster_id}.png"` (über SpriteManager)
- **Tile-Sprites:** `"{tile_name}_large.png"` (direkt aus sprites/ Verzeichnis)

### 3. **Konsistente Pfadauflösung:**
- **SpriteManager:** Verwendet relative Pfade ohne `sprites/` Prefix
- **ResourceManager:** Lädt aus `sprites/` Verzeichnis
- **Entity-System:** Verwendet SpriteManager als primäre Quelle

## 📁 **Korrigierte Dateien:**

### `engine/graphics/sprite_manager.py`
- `load_large_tiles()`: Behält `_large` im Cache-Schlüssel
- Konsistente Pfade für Monster und NPCs

### `engine/scenes/battle_scene.py`
- Monster-Sprite-Pfade korrigiert
- Bessere Fehlerbehandlung

### `engine/scenes/starter_selection_scene.py`
- Starter-Monster-Pfade vereinheitlicht
- Konsistente Namensgebung

### `engine/scenes/field_scene.py`
- _large Sprite-Logik korrigiert
- Verbesserte Fallback-Behandlung

## ✅ **Erwartete Verbesserungen:**

1. **Keine doppelten Sprite-Ladeversuche** mehr
2. **Konsistente Verwendung** von _large Sprites
3. **Bessere Fehlerbehandlung** bei fehlenden Sprites
4. **Einheitliche Pfadstruktur** im gesamten System

## 🎯 **Verwendete Sprite-Typen:**

- **Tiles:** `{tile_name}_large.png` (64x64 Pixel)
- **Player:** `player.png` (64x64 Pixel)
- **NPCs:** `npcs/{npc_id}.png` (64x64 Pixel)
- **Monster:** `monsters/{monster_id}.png` (64x64 Pixel)

## 🔍 **Debug-Features:**

- Alle Sprite-Ladevorgänge werden geloggt
- Fehlende Sprites werden klar gemeldet
- Sprite-Größen werden überprüft und angezeigt
