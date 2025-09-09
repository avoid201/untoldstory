#!/usr/bin/env python3
"""
Pathfinding Fix für Untold Story
Korrigiert Pathfinding-Probleme in Area und NPC-Klassen
"""

import sys
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).parent if __file__ else Path.cwd()
sys.path.insert(0, str(PROJECT_ROOT))

from engine.world.tile_manager import TileManager

def fix_area_pathfinding():
    """
    Korrigiert Pathfinding in der Area-Klasse.
    Fügt find_path_with_tile_manager und find_diagonal_path Methoden hinzu.
    """
    
    # Import-Statement für die neue Methode
    import_section = "from engine.world.tile_manager import TileManager"
    
    # Neue Methode für TileManager-Pathfinding
    find_path_with_tile_manager_method = '''
    def find_path_with_tile_manager(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Verwendet den TileManager für Pathfinding.
        
        Args:
            start: Start-Position (x, y) in Tiles
            goal: Ziel-Position (x, y) in Tiles
            
        Returns:
            Liste von Positionen oder leere Liste wenn kein Pfad
        """
        tile_manager = TileManager.get_instance()
        
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
'''
    
    # Neue Methode für diagonalen Pfad
    find_diagonal_path_method = '''
    def find_diagonal_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Findet einen Pfad mit diagonaler Bewegung.
        
        Args:
            start: Start-Position (x, y) in Tiles
            goal: Ziel-Position (x, y) in Tiles
            
        Returns:
            Liste von Positionen oder leere Liste wenn kein Pfad
        """
        tile_manager = TileManager.get_instance()
        
        # Synchronisiere Collision-Map
        self.find_path_with_tile_manager(start, goal)  # Aktualisiert collision_map
        
        return tile_manager.find_path_diagonal(start, goal)
'''
    
    print("✅ Pathfinding-Fixes für Area-Klasse generiert")
    print("Füge diese Methoden zur Area-Klasse hinzu:")
    print(find_path_with_tile_manager_method)
    print(find_diagonal_path_method)

def fix_npc_pathfinding():
    """
    Korrigiert Pathfinding in der NPC-Klasse.
    Fügt TileManager-Integration hinzu.
    """
    
    # Import-Statement
    import_section = "from engine.world.tile_manager import TileManager"
    
    # Neue Methode für NPC-Pathfinding
    npc_pathfinding_method = '''
    def find_path_with_tile_manager(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Verwendet den TileManager für Pathfinding.
        
        Args:
            start: Start-Position (x, y) in Tiles
            goal: Ziel-Position (x, y) in Tiles
            
        Returns:
            Liste von Positionen oder leere Liste wenn kein Pfad
        """
        tile_manager = TileManager.get_instance()
        
        # Stelle sicher, dass TileManager die aktuelle Map kennt
        if not tile_manager.collision_map or \
           len(tile_manager.collision_map) != self.area.height:
            # Baue Collision-Map aus Area-Daten
            tile_manager.map_width = self.area.width
            tile_manager.map_height = self.area.height
            tile_manager.collision_map = []
            
            for y in range(self.area.height):
                row = []
                for x in range(self.area.width):
                    # Verwende Area's is_tile_solid Methode
                    row.append(self.area.is_tile_solid(x, y))
                tile_manager.collision_map.append(row)
        
        # Verwende TileManager's Pathfinding
        if hasattr(tile_manager, 'find_path_diagonal'):
            return tile_manager.find_path_diagonal(start, goal)
        else:
            return tile_manager.find_path(start, goal)
'''
    
    print("✅ Pathfinding-Fixes für NPC-Klasse generiert")
    print("Füge diese Methode zur NPC-Klasse hinzu:")
    print(npc_pathfinding_method)

def main():
    """Hauptfunktion"""
    print("🔧 PATHFINDING FIX GENERATOR")
    print("=" * 50)
    
    fix_area_pathfinding()
    print()
    fix_npc_pathfinding()
    
    print("\n📝 ANLEITUNG:")
    print("1. Füge die generierten Methoden zu den entsprechenden Klassen hinzu")
    print("2. Ersetze alte Pathfinding-Aufrufe durch die neuen Methoden")
    print("3. Teste das System mit 'python3 test_integration.py'")

if __name__ == "__main__":
    main()
