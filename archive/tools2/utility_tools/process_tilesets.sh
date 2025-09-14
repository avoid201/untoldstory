#!/bin/bash

# Untold Story - Tileset zu Einzeltiles Konvertierung
# Automatisiertes Skript für die komplette Verarbeitung

echo "🎮 Untold Story - Tileset Cutter"
echo "================================"
echo ""

# Setze Arbeitsverzeichnis
cd /Users/leon/Desktop/untold_story

# Erstelle Eingabeordner falls nicht vorhanden
mkdir -p tilesets_to_cut

echo "📁 Bitte platziere deine Tileset-Bilder in:"
echo "   /Users/leon/Desktop/untold_story/tilesets_to_cut/"
echo ""
echo "Drücke ENTER wenn die Dateien bereit sind..."
read

# Prüfe ob Dateien vorhanden sind
if [ -z "$(ls -A tilesets_to_cut/*.png 2>/dev/null)" ]; then
    echo "❌ Keine PNG-Dateien gefunden in tilesets_to_cut/"
    echo "Bitte füge deine Tileset-Bilder hinzu und starte das Skript erneut."
    exit 1
fi

echo "✅ Gefundene Tilesets:"
ls -la tilesets_to_cut/*.png
echo ""

# Führe das Tileset-Cutter Skript aus
echo "✂️ Schneide Tilesets in einzelne Tiles..."
python3 tools/advanced_tileset_cutter.py

# Prüfe ob erfolgreich
if [ $? -eq 0 ]; then
    echo ""
    echo "🎯 Tiles erfolgreich geschnitten!"
    
    # Generiere Tiled-Dateien
    echo ""
    echo "🗺️ Generiere Tiled TSX-Dateien..."
    python3 tools/generate_tiled_tilesets.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Alle Dateien wurden erfolgreich erstellt!"
        echo ""
        echo "📦 Ausgabe:"
        echo "  - Individual Tiles: assets/gfx/individual_tiles/"
        echo "  - ZIP-Datei: individual_tiles.zip"
        echo "  - Tiled TSX-Dateien: assets/gfx/tiles/*.tsx"
        echo ""
        echo "🎮 Du kannst jetzt in Tiled mit den einzelnen Tiles arbeiten!"
    else
        echo "⚠️ Fehler beim Generieren der Tiled-Dateien"
    fi
else
    echo "❌ Fehler beim Schneiden der Tilesets"
    exit 1
fi

# Zeige Statistik
if [ -f "assets/gfx/individual_tiles/statistics.json" ]; then
    echo ""
    echo "📊 Statistik:"
    python3 -c "
import json
with open('assets/gfx/individual_tiles/statistics.json', 'r') as f:
    stats = json.load(f)
    print(f'  Total Tiles: {stats[\"total_tiles\"]}')
    for cat, count in stats['categories'].items():
        print(f'  {cat}: {count} tiles')
    if stats.get('duplicates_found', 0) > 0:
        print(f'  Duplikate gefunden: {stats[\"duplicates_found\"]}')
"
fi

echo ""
echo "🎉 Fertig!"
