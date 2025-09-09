#!/usr/bin/env python3
"""
Map Fixer für Untold Story
===========================
Behebt häufige Probleme nach der TMX-Migration
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any

class MapFixer:
    """Behebt typische Probleme in migrierten Maps"""
    
    def __init__(self, maps_dir: str = "data/maps"):
        self.maps_dir = Path(maps_dir)
        self.fixes_applied = []
        
    def load_map(self, filepath: Path) -> Dict[str, Any]:
        """Lädt eine Map-JSON Datei"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def save_map(self, map_data: Dict[str, Any], filepath: Path):
        """Speichert eine Map-JSON Datei"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(map_data, f, indent=2, ensure_ascii=False)
    
    def fix_layer_names(self, map_data: Dict[str, Any], map_name: str) -> bool:
        """
        Korrigiert Layer-Namen (case-insensitive matching)
        """
        if "layers" not in map_data:
            return False
        
        layers = map_data["layers"]
        fixed = False
        
        # Mapping von möglichen Namen zu Standard-Namen
        layer_mappings = {
            "ground": ["Ground", "floor", "Floor", "base", "Base", "boden", "Boden"],
            "collision": ["Collision", "collisions", "Collisions", "solid", "Solid", 
                         "walls", "Walls", "blocked", "Blocked", "kollision", "Kollision"],
            "decor": ["Decor", "decoration", "Decoration", "deco", "Deco", "dekoration", "Dekoration"],
        }
        
        new_layers = {}
        
        for standard_name, alternatives in layer_mappings.items():
            # Prüfe ob Standard-Name bereits existiert
            if standard_name in layers:
                new_layers[standard_name] = layers[standard_name]
                continue
            
            # Suche nach Alternativen
            found = False
            for alt_name in alternatives:
                if alt_name in layers:
                    new_layers[standard_name] = layers[alt_name]
                    self.fixes_applied.append(f"{map_name}: Layer '{alt_name}' → '{standard_name}'")
                    fixed = True
                    found = True
                    break
            
            # Falls nicht gefunden und essentiell, erstelle leeren Layer
            if not found and standard_name in ["ground", "collision"]:
                # Versuche Dimensionen zu ermitteln
                width = map_data.get("width", 0)
                height = map_data.get("height", 0)
                
                if width > 0 and height > 0:
                    if standard_name == "ground":
                        # Erstelle Basis-Ground-Layer (z.B. alles Gras)
                        new_layers[standard_name] = [[1] * width for _ in range(height)]
                    else:  # collision
                        # Erstelle leeren Collision-Layer
                        new_layers[standard_name] = [[0] * width for _ in range(height)]
                    
                    self.fixes_applied.append(f"{map_name}: Layer '{standard_name}' erstellt")
                    fixed = True
        
        # Übrige Layer übernehmen
        for layer_name, layer_data in layers.items():
            if layer_name not in new_layers and not any(layer_name in alts for alts in layer_mappings.values()):
                new_layers[layer_name] = layer_data
        
        map_data["layers"] = new_layers
        return fixed
    
    def fix_dimensions(self, map_data: Dict[str, Any], map_name: str) -> bool:
        """
        Fügt fehlende Dimensionen hinzu basierend auf Layer-Größen
        """
        fixed = False
        
        if "width" not in map_data or "height" not in map_data:
            # Versuche Dimensionen aus Layern zu ermitteln
            if "layers" in map_data:
                for layer_name, layer_data in map_data["layers"].items():
                    if isinstance(layer_data, list) and len(layer_data) > 0:
                        height = len(layer_data)
                        width = len(layer_data[0]) if isinstance(layer_data[0], list) else 0
                        
                        if width > 0 and height > 0:
                            map_data["width"] = width
                            map_data["height"] = height
                            self.fixes_applied.append(f"{map_name}: Dimensionen gesetzt ({width}x{height})")
                            fixed = True
                            break
        
        return fixed
    
    def fix_out_of_bounds(self, map_data: Dict[str, Any], map_name: str) -> bool:
        """
        Entfernt oder korrigiert Objekte außerhalb der Map-Grenzen
        """
        width = map_data.get("width", 0)
        height = map_data.get("height", 0)
        
        if width == 0 or height == 0:
            return False
        
        fixed = False
        
        # Warps korrigieren
        if "warps" in map_data:
            valid_warps = []
            for warp in map_data["warps"]:
                x, y = warp.get("x", 0), warp.get("y", 0)
                
                # Clamp to bounds
                if x >= width:
                    warp["x"] = width - 1
                    fixed = True
                if y >= height:
                    warp["y"] = height - 1
                    fixed = True
                
                if 0 <= warp["x"] < width and 0 <= warp["y"] < height:
                    valid_warps.append(warp)
                else:
                    self.fixes_applied.append(f"{map_name}: Warp bei ({x},{y}) entfernt")
                    fixed = True
            
            map_data["warps"] = valid_warps
        
        # NPCs korrigieren
        if "npcs" in map_data:
            valid_npcs = []
            for npc in map_data["npcs"]:
                x, y = npc.get("x", 0), npc.get("y", 0)
                
                if x >= width:
                    npc["x"] = width - 1
                    fixed = True
                if y >= height:
                    npc["y"] = height - 1
                    fixed = True
                
                if 0 <= npc["x"] < width and 0 <= npc["y"] < height:
                    valid_npcs.append(npc)
                else:
                    self.fixes_applied.append(f"{map_name}: NPC bei ({x},{y}) entfernt")
                    fixed = True
            
            map_data["npcs"] = valid_npcs
        
        # Trigger korrigieren
        if "triggers" in map_data:
            valid_triggers = []
            for trigger in map_data["triggers"]:
                x, y = trigger.get("x", 0), trigger.get("y", 0)
                
                if x >= width:
                    trigger["x"] = width - 1
                    fixed = True
                if y >= height:
                    trigger["y"] = height - 1
                    fixed = True
                
                if 0 <= trigger["x"] < width and 0 <= trigger["y"] < height:
                    valid_triggers.append(trigger)
                else:
                    self.fixes_applied.append(f"{map_name}: Trigger bei ({x},{y}) entfernt")
                    fixed = True
            
            map_data["triggers"] = valid_triggers
        
        return fixed
    
    def add_missing_data(self, map_data: Dict[str, Any], map_name: str) -> bool:
        """
        Fügt fehlende aber wichtige Felder hinzu
        """
        fixed = False
        
        # ID hinzufügen falls fehlend
        if "id" not in map_data:
            map_data["id"] = map_name
            self.fixes_applied.append(f"{map_name}: ID hinzugefügt")
            fixed = True
        
        # Name hinzufügen falls fehlend
        if "name" not in map_data:
            map_data["name"] = map_name.replace('_', ' ').title()
            self.fixes_applied.append(f"{map_name}: Name hinzugefügt")
            fixed = True
        
        # Tile-Size setzen falls fehlend
        if "tile_size" not in map_data:
            map_data["tile_size"] = 16
            fixed = True
        
        # Leere Arrays für fehlende Spieldaten
        for field in ["warps", "npcs", "triggers"]:
            if field not in map_data:
                map_data[field] = []
                fixed = True
        
        if "spawn_points" not in map_data:
            map_data["spawn_points"] = {}
            fixed = True
        
        # Placeholder-Texte für Trigger ohne Text
        if "triggers" in map_data:
            for trigger in map_data["triggers"]:
                if "text" not in trigger or not trigger["text"]:
                    trigger["text"] = "..."
                    fixed = True
        
        # Standard-Namen für NPCs ohne Namen
        if "npcs" in map_data:
            for i, npc in enumerate(map_data["npcs"]):
                if "name" not in npc or not npc["name"]:
                    npc["name"] = f"Person {i+1}"
                    fixed = True
                if "id" not in npc or not npc["id"]:
                    npc["id"] = f"npc_{i}"
                    fixed = True
        
        return fixed
    
    def remove_test_maps(self):
        """Entfernt Test-Maps aus dem Verzeichnis"""
        test_patterns = ["test_", "copy", "backup", ".bak"]
        
        for map_file in self.maps_dir.glob("*.json"):
            map_name = map_file.stem.lower()
            
            if any(pattern in map_name for pattern in test_patterns):
                print(f"   🗑️  Entferne Test-Map: {map_file.name}")
                map_file.unlink()
                self.fixes_applied.append(f"Test-Map '{map_file.name}' entfernt")
    
    def fix_all_maps(self, skip_test_maps: bool = True):
        """
        Behebt alle gefundenen Probleme in allen Maps
        """
        print("🔧 Starte Map-Reparatur...")
        print("=" * 50)
        
        # Optional: Test-Maps entfernen
        if skip_test_maps:
            self.remove_test_maps()
        
        # Alle Maps durchgehen
        map_files = list(self.maps_dir.glob("*.json"))
        
        for map_file in map_files:
            map_name = map_file.stem
            
            # Skip test maps if not already removed
            if skip_test_maps and any(x in map_name.lower() for x in ["test", "copy"]):
                continue
            
            print(f"\n📝 Prüfe: {map_name}")
            
            map_data = self.load_map(map_file)
            if not map_data:
                print(f"   ❌ Konnte Map nicht laden")
                continue
            
            # Fixes anwenden
            fixes_made = False
            
            if self.fix_layer_names(map_data, map_name):
                fixes_made = True
            
            if self.fix_dimensions(map_data, map_name):
                fixes_made = True
            
            if self.fix_out_of_bounds(map_data, map_name):
                fixes_made = True
            
            if self.add_missing_data(map_data, map_name):
                fixes_made = True
            
            # Speichern wenn Änderungen gemacht wurden
            if fixes_made:
                self.save_map(map_data, map_file)
                print(f"   ✅ Map repariert und gespeichert")
            else:
                print(f"   ✓ Keine Reparaturen nötig")
        
        # Zusammenfassung
        print("\n" + "=" * 50)
        print("📊 REPARATUR ABGESCHLOSSEN")
        print("=" * 50)
        
        if self.fixes_applied:
            print(f"\n✅ {len(self.fixes_applied)} Fixes angewendet:")
            for fix in self.fixes_applied[:20]:  # Erste 20 anzeigen
                print(f"   • {fix}")
            if len(self.fixes_applied) > 20:
                print(f"   ... und {len(self.fixes_applied) - 20} weitere")
        else:
            print("✨ Keine Reparaturen waren nötig!")
        
        print("\n💡 Nächste Schritte:")
        print("   1. Validierung erneut ausführen: python map_validator.py")
        print("   2. Spiel testen: python main.py")

def main():
    """Hauptfunktion"""
    import sys
    
    # Optionen aus Argumenten
    skip_test = "--keep-test" not in sys.argv
    
    # Fixer initialisieren und ausführen
    fixer = MapFixer("data/maps")
    fixer.fix_all_maps(skip_test_maps=skip_test)

if __name__ == "__main__":
    main()
