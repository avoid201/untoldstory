#!/usr/bin/env python3
"""
Konvertiert Tiled-JSON Maps zum Engine-Format
"""

import json
from pathlib import Path
from typing import Dict, List, Any

def convert_tiled_to_engine(tiled_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Konvertiert eine Tiled-JSON Map zum Engine-Format.
    
    Args:
        tiled_json: Tiled JSON-Daten
        
    Returns:
        Engine-kompatible Map-Daten
    """
    width = tiled_json.get("width", 20)
    height = tiled_json.get("height", 15)
    
    # Initialisiere Layer-Arrays
    ground_layer = [[0 for _ in range(width)] for _ in range(height)]
    collision_layer = [[0 for _ in range(width)] for _ in range(height)]
    
    # Konvertiere Tile-Layer
    for layer in tiled_json.get("layers", []):
        if layer.get("type") == "tilelayer":
            layer_name = layer.get("name", "").lower()
            data = layer.get("data", [])
            
            # Konvertiere 1D-Array zu 2D
            for y in range(height):
                for x in range(width):
                    idx = y * width + x
                    if idx < len(data):
                        tile_gid = data[idx]
                        # Konvertiere GID (1-basiert) zu Tile-ID (0-basiert)
                        tile_id = tile_gid - 1 if tile_gid > 0 else 0
                        
                        if "collision" in layer_name:
                            collision_layer[y][x] = 1 if tile_id > 0 else 0
                        else:
                            ground_layer[y][x] = tile_id
    
    # Erstelle Engine-Format
    engine_map = {
        "id": Path(tiled_json.get("tiledversion", "unknown")).stem,
        "name": "Converted Map",
        "width": width,
        "height": height,
        "tile_size": 16,
        "layers": {
            "ground": ground_layer,
            "collision": collision_layer
        },
        "warps": [],
        "triggers": [],
        "properties": {}
    }
    
    return engine_map

def convert_map_file(input_path: Path, output_path: Path):
    """
    Konvertiert eine Map-Datei.
    
    Args:
        input_path: Pfad zur Tiled-JSON
        output_path: Pfad zur Engine-JSON
    """
    print(f"Konvertiere {input_path.name}...")
    
    # Lade Tiled-JSON
    with open(input_path, 'r') as f:
        tiled_data = json.load(f)
    
    # Konvertiere
    engine_data = convert_tiled_to_engine(tiled_data)
    
    # Setze Map-spezifische Eigenschaften
    map_name = input_path.stem
    engine_data["id"] = map_name
    engine_data["name"] = map_name.replace('_', ' ').title()
    
    # Backup erstellen falls Datei existiert
    if output_path.exists():
        backup_path = output_path.with_suffix('.json.backup')
        output_path.rename(backup_path)
        print(f"  Backup erstellt: {backup_path.name}")
    
    # Speichere Engine-JSON
    with open(output_path, 'w') as f:
        json.dump(engine_data, f, indent=2)
    
    print(f"  ✅ Konvertiert zu {output_path.name}")

def main():
    """Hauptfunktion"""
    maps_dir = Path("data/maps")
    
    # Maps die konvertiert werden sollen
    maps_to_convert = [
        "player_house",
        "kohlenstadt",
        "museum",
        "rival_house",
        "route1"
    ]
    
    print("🔄 Starte Map-Konvertierung...")
    print("-" * 40)
    
    for map_name in maps_to_convert:
        tiled_path = maps_dir / f"{map_name}.json"
        engine_path = maps_dir / f"{map_name}_engine.json"
        
        if tiled_path.exists():
            convert_map_file(tiled_path, engine_path)
        else:
            print(f"⚠️ {map_name}.json nicht gefunden")
    
    print("-" * 40)
    print("✅ Konvertierung abgeschlossen!")
    print("\nHinweis: Die konvertierten Maps haben '_engine' im Namen.")
    print("Benenne sie um oder passe den MapLoader an.")

if __name__ == "__main__":
    main()
