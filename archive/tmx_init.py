#!/usr/bin/env python3
"""
TMX Map Loading Initialization
Lädt TMX-Tilesets beim Start des Spiels
"""

from pathlib import Path
from engine.graphics.sprite_manager import SpriteManager


def initialize_tmx_support():
    """
    Initialisiert TMX-Support durch Vorladen aller Tilesets
    WICHTIG: Lädt nur player_house.tmx um GID-Konflikte zu vermeiden!
    """
    sprite_manager = SpriteManager.get()
    
    # WICHTIG: Erst sicherstellen dass die GID-Mappings leer sind
    sprite_manager.gid_to_surface = {}
    sprite_manager._loaded_tilesets = set()
    
    # TEMPORÄR: Lade NUR player_house.tmx um Konflikte zu vermeiden
    # TODO: Später muss das pro Map gelöst werden
    tmx_file = Path("data/maps/player_house.tmx")
    
    print(f"🗺️ Initialisiere TMX-Support für player_house...")
    
    try:
        print(f"  📋 Lade Tilesets für: {tmx_file.name}")
        sprite_manager.load_tmx_tilesets(tmx_file)
    except Exception as e:
        print(f"  ⚠️ Fehler beim Laden von {tmx_file.name}: {e}")
        import traceback
        traceback.print_exc()
    
    # Zeige geladene GIDs
    if hasattr(sprite_manager, 'gid_to_surface'):
        gid_count = len(sprite_manager.gid_to_surface)
        print(f"✅ TMX-Support initialisiert: {gid_count} GIDs geladen")
        
        # Debug: Zeige erste paar GIDs
        sorted_gids = sorted(sprite_manager.gid_to_surface.keys())[:10]
        if sorted_gids:
            print(f"   Beispiel-GIDs: {sorted_gids}")
    
    return sprite_manager


if __name__ == "__main__":
    # Test
    initialize_tmx_support()
