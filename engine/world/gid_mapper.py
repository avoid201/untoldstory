"""
GID Mapper für TMX-Maps
Mappt Global IDs aus TMX-Dateien auf die richtigen Tiles
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Tuple

class GIDMapper:
    """Mappt TMX GIDs auf Tileset-Tiles"""
    
    def __init__(self):
        self.gid_to_tileset: Dict[int, Tuple[str, int]] = {}
        self.tileset_firstgids: Dict[str, int] = {}
    
    def load_tmx(self, tmx_path: Path):
        """Lade GID-Mapping aus TMX-Datei"""
        tree = ET.parse(tmx_path)
        root = tree.getroot()
        
        # Lade alle Tilesets
        for tileset_elem in root.findall('tileset'):
            firstgid = int(tileset_elem.get('firstgid', 1))
            source = tileset_elem.get('source', '')
            
            if source:
                tileset_name = source.replace('.tsx', '')
                self.tileset_firstgids[tileset_name] = firstgid
                
                # Lade Tileset-Info
                tsx_path = Path("assets/gfx/tiles") / source
                if not tsx_path.exists():
                    tsx_path = Path("data/maps") / source
                
                if tsx_path.exists():
                    tileset_info = self._load_tileset_info(tsx_path)
                    tile_count = tileset_info.get('tile_count', 0)
                    
                    # Mappe alle GIDs dieses Tilesets
                    for local_id in range(tile_count):
                        global_id = firstgid + local_id
                        self.gid_to_tileset[global_id] = (tileset_name, local_id)
    
    def _load_tileset_info(self, tsx_path: Path) -> Dict:
        """Lade Tileset-Informationen aus TSX"""
        tree = ET.parse(tsx_path)
        root = tree.getroot()
        
        return {
            'name': root.get('name', ''),
            'tile_width': int(root.get('tilewidth', 16)),
            'tile_height': int(root.get('tileheight', 16)),
            'tile_count': int(root.get('tilecount', 0)),
            'columns': int(root.get('columns', 1))
        }
    
    def get_tileset_and_id(self, gid: int) -> Tuple[str, int]:
        """Hole Tileset-Name und lokale ID für eine GID"""
        # Entferne Flip-Flags
        clean_gid = self.clear_flip_flags(gid)
        return self.gid_to_tileset.get(clean_gid, ('unknown', 0))
    
    def clear_flip_flags(self, gid: int) -> int:
        """Entferne Flip-Flags von einer GID"""
        FLIPPED_HORIZONTALLY = 0x80000000
        FLIPPED_VERTICALLY = 0x40000000
        FLIPPED_DIAGONALLY = 0x20000000
        
        return gid & ~(FLIPPED_HORIZONTALLY | FLIPPED_VERTICALLY | FLIPPED_DIAGONALLY)
