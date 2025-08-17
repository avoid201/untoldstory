"""
Tile ID Konstanten für das Untold Story Spiel.
Alle IDs basieren auf der tile_mapping.json und dem manifest.json.
"""

# =============================================================================
# GROUND TILES (IDs 0-18)
# =============================================================================

# Grass Varianten
GRASS_1 = 0
GRASS_2 = 1
GRASS_3 = 2
GRASS_4 = 3
GRASS = 4

# Tall Grass Varianten
TALL_GRASS_1 = 5
TALL_GRASS_2 = 6
TALL_GRASS = 7

# Dirt Varianten
DIRT_1 = 8
DIRT_2 = 9

# Path Varianten
PATH_1 = 10
PATH_2 = 11
PATH = 12

# Gravel Varianten
GRAVEL_1 = 13
GRAVEL_2 = 14
GRAVEL = 15

# Sand Varianten
SAND_1 = 16
SAND_2 = 17

# Snow
SNOW = 18

# =============================================================================
# INTERIOR TILES (IDs 19-21)
# =============================================================================

WOOD_FLOOR = 19
STONE_FLOOR = 20
CARPET = 21

# =============================================================================
# TERRAIN TILES (IDs 22-35)
# =============================================================================

# Bush Varianten
BUSH_1 = 22
BUSH_2 = 23
BUSH = 24

# Rock Varianten
ROCK_1 = 25
ROCK_2 = 26
ROCK = 27

# Flowers
FLOWER_RED = 28
FLOWER_BLUE = 29

# Terrain Features
STUMP = 30
LEDGE = 31
CLIFF_FACE = 32

# Stairs
STAIRS_H = 33
STAIRS_V = 34
STAIRS = 35

# =============================================================================
# WATER TILES (IDs 36-45)
# =============================================================================

# Water Varianten
WATER_1 = 36
WATER_2 = 37

# Water Edges
WATER_EDGE_N = 38
WATER_EDGE_S = 39
WATER_EDGE_W = 40
WATER_EDGE_E = 41

# Water Corners
WATER_CORNER_NE = 42
WATER_CORNER_NW = 43
WATER_CORNER_SE = 44
WATER_CORNER_SW = 45

# =============================================================================
# BUILDING TILES (IDs 46-53)
# =============================================================================

# Walls
WALL_BRICK = 46
WALL_PLASTER = 47
WALL = 48

# Roofs
ROOF_RED = 49
ROOF_BLUE = 50
ROOF_RIDGE = 51
ROOF = 52

# Special
WARP_CARPET = 53

# =============================================================================
# OBJECTS (IDs 100-118)
# =============================================================================

# Terrain Objects
FENCE_H = 100
FENCE_V = 101

# Building Objects
WINDOW = 102
DOOR = 103
SIGN = 104

# Interior Objects
TABLE = 105
CHAIR = 106
BED = 107
BOOKSHELF = 108
TV = 109
POTTED_PLANT = 110

# Misc Objects
CRATE = 111
BARREL = 112
LAMP_POST = 113
MAILBOX = 114
WELL = 115
GRAVESTONE = 116
BOULDER = 117
TREE_SMALL = 118

# =============================================================================
# SPRITES (IDs 200+)
# =============================================================================

# Player Sprites
PLAYER_DOWN = 200
PLAYER_UP = 201
PLAYER_LEFT = 202
PLAYER_RIGHT = 203

# NPC Base IDs (jeweils 4 Richtungen: down, up, left, right)
NPC_VILLAGER_M_BASE = 210
NPC_VILLAGER_F_BASE = 214
NPC_GUARD_BASE = 218
NPC_SCIENTIST_BASE = 222
NPC_NURSE_BASE = 226
NPC_MERCHANT_BASE = 230
NPC_FISHER_BASE = 234
NPC_BIKER_BASE = 238
NPC_RANGER_BASE = 242
NPC_MINER_BASE = 246
NPC_MONK_BASE = 250
NPC_KID_BASE = 254
NPC_A_BASE = 258
NPC_B_BASE = 262

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_npc_sprite_id(npc_type: str, direction: str) -> int:
    """Gibt die Sprite-ID für einen NPC-Typ und eine Richtung zurück."""
    npc_bases = {
        "villager_m": NPC_VILLAGER_M_BASE,
        "villager_f": NPC_VILLAGER_F_BASE,
        "guard": NPC_GUARD_BASE,
        "scientist": NPC_SCIENTIST_BASE,
        "nurse": NPC_NURSE_BASE,
        "merchant": NPC_MERCHANT_BASE,
        "fisher": NPC_FISHER_BASE,
        "biker": NPC_BIKER_BASE,
        "ranger": NPC_RANGER_BASE,
        "miner": NPC_MINER_BASE,
        "monk": NPC_MONK_BASE,
        "kid": NPC_KID_BASE,
        "npcA": NPC_A_BASE,
        "npcB": NPC_B_BASE
    }
    
    direction_offsets = {
        "down": 0,
        "up": 1,
        "left": 2,
        "right": 3
    }
    
    if npc_type not in npc_bases:
        raise ValueError(f"Unbekannter NPC-Typ: {npc_type}")
    
    if direction not in direction_offsets:
        raise ValueError(f"Unbekannte Richtung: {direction}")
    
    return npc_bases[npc_type] + direction_offsets[direction]

def is_solid_tile(tile_id: int) -> bool:
    """Prüft, ob ein Tile begehbar ist (nicht solid)."""
    solid_tiles = {
        TALL_GRASS_1, TALL_GRASS_2, TALL_GRASS,
        BUSH_1, BUSH_2, BUSH,
        ROCK_1, ROCK_2, ROCK,
        STUMP, LEDGE, CLIFF_FACE,
        WATER_1, WATER_2,
        WATER_EDGE_N, WATER_EDGE_S, WATER_EDGE_W, WATER_EDGE_E,
        WATER_CORNER_NE, WATER_CORNER_NW, WATER_CORNER_SE, WATER_CORNER_SW,
        WALL_BRICK, WALL_PLASTER, WALL,
        ROOF_RED, ROOF_BLUE, ROOF_RIDGE, ROOF,
        FENCE_H, FENCE_V,
        TABLE, CHAIR, BED, BOOKSHELF, TV, POTTED_PLANT,
        CRATE, BARREL, LAMP_POST, MAILBOX, WELL, GRAVESTONE, BOULDER, TREE_SMALL
    }
    return tile_id in solid_tiles

def is_transparent_tile(tile_id: int) -> bool:
    """Prüft, ob ein Tile transparent ist (als Object gerendert wird)."""
    transparent_tiles = {
        FENCE_H, FENCE_V,
        WINDOW, DOOR, SIGN,
        TABLE, CHAIR, BED, BOOKSHELF, TV, POTTED_PLANT,
        CRATE, BARREL, LAMP_POST, MAILBOX, WELL, GRAVESTONE, BOULDER, TREE_SMALL
    }
    return tile_id in transparent_tiles

def get_tile_category(tile_id: int) -> str:
    """Gibt die Kategorie eines Tiles zurück."""
    if 0 <= tile_id <= 18:
        return "ground"
    elif 19 <= tile_id <= 21:
        return "interior"
    elif 22 <= tile_id <= 35:
        return "terrain"
    elif 36 <= tile_id <= 45:
        return "water"
    elif 46 <= tile_id <= 53:
        return "building"
    elif 100 <= tile_id <= 118:
        return "object"
    elif 200 <= tile_id <= 265:
        return "sprite"
    else:
        return "unknown"
