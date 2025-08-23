#!/usr/bin/env python3
"""
Fix für die Pathfinding-Integration zwischen TileManager und Area
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def fix_area_pathfinding():
    """
    Integriert TileManager Pathfinding in Area.py
    """
    area_file = PROJECT_ROOT / "engine/world/area.py"
    
    # Backup erstellen
    import shutil
    backup_file = area_file.with_suffix('.py.backup')
    shutil.copy(area_file, backup_file)
    print(f"✅ Backup erstellt: {backup_file}")
    
    # Area.py lesen
    with open(area_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Neue Pathfinding-Methoden hinzufügen
    pathfinding_integration = '''
    def find_path_with_tile_manager(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Verwendet den TileManager für Pathfinding.
        
        Args:
            start: Start-Position (x, y) in Tiles
            goal: Ziel-Position (x, y) in Tiles
            
        Returns:
            Liste von Positionen oder leere Liste wenn kein Pfad
        """
        from engine.world.tile_manager import tile_manager
        
        # Stelle sicher, dass TileManager die aktuelle Map kennt
        if not tile_manager.collision_map or \
           len(tile_manager.collision_map) != self.height or \
           (tile_manager.collision_map and len(tile_manager.collision_map[0]) != self.width):
            # Baue Collision-Map aus Area-Daten
            tile_manager.map_width = self.width
            tile_manager.map_height = self.height
            tile_manager.collision_map = []
            
            for y in range(self.height):
                row = []
                for x in range(self.width):
                    # Verwende Area's is_tile_solid Methode
                    row.append(self.is_tile_solid(x, y))
                tile_manager.collision_map.append(row)
        
        # Verwende TileManager's Pathfinding
        return tile_manager.find_path(start, goal)
    
    def find_diagonal_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Findet einen Pfad mit diagonaler Bewegung.
        
        Args:
            start: Start-Position (x, y) in Tiles
            goal: Ziel-Position (x, y) in Tiles
            
        Returns:
            Liste von Positionen oder leere Liste wenn kein Pfad
        """
        from engine.world.tile_manager import tile_manager
        
        # Synchronisiere Collision-Map
        self.find_path_with_tile_manager(start, goal)  # Aktualisiert collision_map
        
        return tile_manager.find_path_diagonal(start, goal)
'''
    
    # Check ob die Methoden schon existieren
    if "find_path_with_tile_manager" not in content:
        # Füge die neuen Methoden vor der letzten schließenden Klammer ein
        import_section = "from typing import Dict, List, Optional, Tuple"
        if import_section in content:
            # Stelle sicher, dass Tuple importiert wird
            pass
        
        # Finde das Ende der Area-Klasse
        class_end = content.rfind('\n\n')
        if class_end > 0:
            content = content[:class_end] + pathfinding_integration + content[class_end:]
            
            # Speichere die aktualisierte Datei
            with open(area_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Area.py aktualisiert mit TileManager-Pathfinding-Integration")
        else:
            print("❌ Konnte Area-Klasse nicht korrekt updaten")
    else:
        print("ℹ️  Pathfinding-Integration bereits vorhanden")

def fix_npc_pathfinding():
    """
    Stellt sicher, dass NPCs das korrekte Pathfinding verwenden
    """
    npc_file = PROJECT_ROOT / "engine/world/npc_improved.py"
    
    if not npc_file.exists():
        print("⚠️  npc_improved.py nicht gefunden")
        return
    
    # Backup erstellen
    import shutil
    backup_file = npc_file.with_suffix('.py.backup')
    shutil.copy(npc_file, backup_file)
    print(f"✅ Backup erstellt: {backup_file}")
    
    # NPC-Datei lesen
    with open(npc_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Suche nach der _find_path Methode und ersetze sie
    modified = False
    for i, line in enumerate(lines):
        if "def _find_path" in line:
            # Finde das Ende der Methode
            indent = len(line) - len(line.lstrip())
            method_end = i + 1
            while method_end < len(lines):
                next_line = lines[method_end]
                if next_line.strip() and not next_line.startswith(' ' * (indent + 4)):
                    break
                method_end += 1
            
            # Ersetze die Methode
            new_method = f'''    def _find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Findet einen Pfad mit dem TileManager"""
        from engine.world.tile_manager import tile_manager
        
        # Setze die Map-Dimensionen
        if self.area:
            tile_manager.map_width = self.area.width
            tile_manager.map_height = self.area.height
            
            # Baue Collision-Map
            if not tile_manager.collision_map or \
               len(tile_manager.collision_map) != self.area.height:
                tile_manager.collision_map = []
                for y in range(self.area.height):
                    row = []
                    for x in range(self.area.width):
                        row.append(self.area.is_tile_solid(x, y))
                    tile_manager.collision_map.append(row)
        
        # Verwende TileManager's optimiertes Pathfinding
        if self.movement_pattern == MovementPattern.WANDER:
            return tile_manager.find_path_diagonal(start, goal)
        else:
            return tile_manager.find_path(start, goal)
'''
            
            # Ersetze die alten Zeilen
            lines = lines[:i] + [new_method + '\n'] + lines[method_end:]
            modified = True
            break
    
    if modified:
        # Speichere die aktualisierte Datei
        with open(npc_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("✅ npc_improved.py aktualisiert mit TileManager-Pathfinding")
    else:
        print("⚠️  Konnte _find_path Methode nicht finden")

def verify_tileset_paths():
    """
    Überprüft und korrigiert Tileset-Pfade in TSX-Dateien
    """
    import xml.etree.ElementTree as ET
    
    maps_dir = PROJECT_ROOT / "data/maps"
    tsx_files = list(maps_dir.glob("*.tsx"))
    
    print(f"\n📋 Überprüfe {len(tsx_files)} TSX-Dateien...")
    
    for tsx_file in tsx_files:
        try:
            tree = ET.parse(tsx_file)
            root = tree.getroot()
            
            image_elem = root.find('image')
            if image_elem is not None:
                source = image_elem.get('source', '')
                
                # Konstruiere den absoluten Pfad
                if source.startswith('../../'):
                    rel_path = source.replace('../../', '')
                    abs_path = PROJECT_ROOT / rel_path
                else:
                    abs_path = tsx_file.parent / source
                
                if not abs_path.exists():
                    print(f"❌ Tileset nicht gefunden: {tsx_file.name} -> {source}")
                    
                    # Versuche alternative Pfade
                    alternatives = [
                        PROJECT_ROOT / "assets/gfx/tiles/tilesets" / abs_path.name,
                        PROJECT_ROOT / "assets/gfx/tilesets" / abs_path.name,
                        PROJECT_ROOT / "data/tilesets" / abs_path.name,
                    ]
                    
                    for alt in alternatives:
                        if alt.exists():
                            # Berechne relativen Pfad von TSX zu Tileset
                            try:
                                rel_path = "../../" + str(alt.relative_to(PROJECT_ROOT))
                                image_elem.set('source', rel_path)
                                tree.write(tsx_file, encoding='UTF-8', xml_declaration=True)
                                print(f"✅ Korrigiert: {tsx_file.name} -> {rel_path}")
                                break
                            except ValueError:
                                pass
                else:
                    print(f"✅ OK: {tsx_file.name}")
                    
        except Exception as e:
            print(f"❌ Fehler bei {tsx_file.name}: {e}")

def create_test_map():
    """
    Erstellt eine einfache Test-Map für Debugging
    """
    test_map = PROJECT_ROOT / "data/maps/test_map.tmx"
    
    tmx_content = '''<?xml version="1.0" encoding="UTF-8"?>
<map version="1.10" tiledversion="1.10.0" orientation="orthogonal" renderorder="right-down" width="20" height="15" tilewidth="16" tileheight="16" infinite="0" nextlayerid="4" nextobjectid="1">
 <tileset firstgid="1" source="test_tileset.tsx"/>
 <layer id="1" name="ground" width="20" height="15">
  <data encoding="csv">
1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,
1,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,1,
1,2,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,2,1,
1,2,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,2,1,
1,2,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,2,1,
1,2,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,2,1,
1,2,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,2,1,
1,2,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,2,1,
1,2,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,2,1,
1,2,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,2,1,
1,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,1,
1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,
1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1
</data>
 </layer>
 <layer id="2" name="collision" width="20" height="15" visible="0">
  <data encoding="csv">
1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
</data>
 </layer>
</map>'''
    
    with open(test_map, 'w', encoding='utf-8') as f:
        f.write(tmx_content)
    
    print(f"✅ Test-Map erstellt: {test_map}")

def main():
    print("🔧 PATHFINDING & INTEGRATION FIX")
    print("=" * 50)
    
    # 1. Fix Area Pathfinding
    print("\n1. Fixe Area Pathfinding-Integration...")
    fix_area_pathfinding()
    
    # 2. Fix NPC Pathfinding
    print("\n2. Fixe NPC Pathfinding...")
    fix_npc_pathfinding()
    
    # 3. Verify Tileset Paths
    print("\n3. Überprüfe Tileset-Pfade...")
    verify_tileset_paths()
    
    # 4. Create Test Map
    print("\n4. Erstelle Test-Map...")
    create_test_map()
    
    print("\n✅ Fixes angewendet!")
    print("\nNächste Schritte:")
    print("1. Führe 'python3 comprehensive_test.py' aus")
    print("2. Teste das Spiel mit 'python3 main.py'")
    print("3. Überprüfe die test_map.tmx in Tiled")

if __name__ == "__main__":
    main()
