#!/usr/bin/env python3
"""
Finaler Fix für Untold Story - behebt alle verbleibenden Probleme
"""

import sys
import json
from pathlib import Path

def fix_map_layers():
    """Korrigiert Layer-Namen in den Map-Dateien"""
    print("🔧 Korrigiere Map-Layer-Namen...")
    
    maps_dir = Path("data/maps")
    maps_to_fix = ["player_house.json", "kohlenstadt.json", "museum.json"]
    
    for map_file in maps_to_fix:
        map_path = maps_dir / map_file
        if not map_path.exists():
            continue
            
        with open(map_path, 'r') as f:
            data = json.load(f)
        
        # Finde und benenne Tile Layer 1 zu "ground"
        modified = False
        for layer in data.get("layers", []):
            if layer.get("name") == "Tile Layer 1":
                layer["name"] = "ground"
                modified = True
                print(f"  ✅ {map_file}: 'Tile Layer 1' → 'ground'")
        
        if modified:
            # Backup
            backup_path = map_path.with_suffix('.json.backup')
            map_path.rename(backup_path)
            
            # Speichere korrigierte Version
            with open(map_path, 'w') as f:
                json.dump(data, f, indent=2)

def ensure_collision_layers():
    """Fügt fehlende Collision-Layer hinzu"""
    print("🔧 Füge Collision-Layer hinzu...")
    
    maps_dir = Path("data/maps")
    
    for map_file in maps_dir.glob("*.json"):
        # Skip backups and non-map files
        if "backup" in map_file.name or "tileset" in map_file.name:
            continue
            
        with open(map_file, 'r') as f:
            data = json.load(f)
        
        # Check if it's a Tiled map
        if "tiledversion" not in data:
            continue
        
        # Check if collision layer exists
        has_collision = False
        for layer in data.get("layers", []):
            if "collision" in layer.get("name", "").lower():
                has_collision = True
                break
        
        if not has_collision:
            # Add empty collision layer
            width = data.get("width", 20)
            height = data.get("height", 15)
            
            collision_layer = {
                "data": [0] * (width * height),
                "height": height,
                "id": len(data.get("layers", [])) + 1,
                "name": "collision",
                "opacity": 1,
                "type": "tilelayer",
                "visible": False,
                "width": width,
                "x": 0,
                "y": 0
            }
            
            data["layers"].append(collision_layer)
            
            # Save
            with open(map_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"  ✅ {map_file.name}: Collision-Layer hinzugefügt")

def create_quick_launcher():
    """Erstellt einen Quick-Launcher für das Spiel"""
    launcher_content = """#!/usr/bin/env python3
'''
Quick Launcher für Untold Story
Startet das Spiel mit optimalen Einstellungen
'''

import os
import sys
import subprocess

# Setze Umgebungsvariablen für bessere Performance
os.environ['SDL_VIDEO_ALLOW_SCREENSAVER'] = '1'
os.environ['SDL_HINT_RENDER_SCALE_QUALITY'] = '0'  # Pixel-perfect

# Starte das Spiel
try:
    subprocess.run([sys.executable, 'main.py'], check=True)
except KeyboardInterrupt:
    print("\\nSpiel beendet.")
except Exception as e:
    print(f"Fehler: {e}")
    input("Drücke Enter zum Beenden...")
"""
    
    launcher_path = Path("start_game.py")
    launcher_path.write_text(launcher_content)
    launcher_path.chmod(0o755)
    print("✅ Quick-Launcher erstellt: start_game.py")

def main():
    print("=" * 50)
    print("🔧 UNTOLD STORY - FINALER FIX")
    print("=" * 50)
    
    # Fixes anwenden
    fix_map_layers()
    ensure_collision_layers()
    create_quick_launcher()
    
    print("\n" + "=" * 50)
    print("✅ ALLE FIXES ANGEWENDET!")
    print("\nDas Spiel sollte jetzt vollständig funktionieren.")
    print("\nStarte mit:")
    print("  python3 start_game.py")
    print("oder:")
    print("  python3 main.py")
    print("=" * 50)

if __name__ == "__main__":
    main()
