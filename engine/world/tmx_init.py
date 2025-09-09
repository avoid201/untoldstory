"""TMX Initialization Module - Updated Implementation"""

def initialize_tmx_support():
    """Initialize TMX support with consolidated MapLoader"""
    try:
        from engine.graphics.sprite_manager import SpriteManager
        from engine.world.map_loader import MapLoader
        
        # Initializing TMX support...
        
        # Get sprite manager instance
        sprite_manager = SpriteManager.get()
        
        # Load TMX tilesets if not already loaded
        if not sprite_manager._loaded:
            # Loading TMX tilesets...
            # This will load all tilesets including TMX ones
            sprite_manager._ensure_loaded()
        
        # Test TMX functionality
        # Testing TMX functionality...
        
        # MapLoader can handle TMX visual data (consolidated from EnhancedMapManager)
        # MapLoader available for TMX visual data
        
        # TMX tileset loading is integrated in SpriteManager
        if hasattr(sprite_manager, 'load_tmx_tilesets'):
            # TMX tileset loader available
            pass
        
        # TMX support successfully initialized!
        # Sprite cache activated
        # TMX visual data support activated
        # MapLoader ready (consolidated)
        
        return True
        
    except ImportError as e:
        # TMX modules not available - using JSON maps fallback
        return False
    except Exception as e:
        # TMX initialization error - TMX support disabled
        return False
