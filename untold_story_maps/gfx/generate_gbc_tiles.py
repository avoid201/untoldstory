#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Generate 16x16 Game Boy Color–style tiles using Pokémon Crystal daytime palettes.
# Palette values are adapted from the pokecrystal disassembly (tilesets/day.pal).
# Outputs individual PNGs, a preview spritesheet, and a ZIP archive.
from PIL import Image, ImageDraw
import os, zipfile, math

def rgb5_to_rgb8(c):
    return tuple(int(round(v * 255 / 31)) for v in c)

# Daytime palette (8 palettes × 4 colors), 5-bit RGB triplets
day_pal_5bit = [
    (27,31,27),(21,21,21),(13,13,13),(7,7,7),
    (27,31,27),(31,19,24),(30,10,6),(7,7,7),
    (22,31,10),(12,25,1),(5,14,0),(7,7,7),
    (31,31,31),(8,12,31),(1,4,31),(7,7,7),
    (27,31,27),(31,31,7),(31,16,1),(7,7,7),
    (27,31,27),(24,18,7),(20,15,3),(7,7,7),
    (27,31,27),(15,31,31),(5,17,31),(7,7,7),
    (31,31,16),(31,31,16),(14,9,0),(0,0,0),
]
day_pal_8bit = [rgb5_to_rgb8(c) for c in day_pal_5bit]
tile_palettes = [day_pal_8bit[i*4:(i+1)*4] for i in range(8)]

TILE = 16

def new_tile(palette_index, transparent=False):
    mode = "RGBA" if transparent else "RGB"
    base = Image.new(mode, (TILE, TILE), (0,0,0,0) if transparent else tile_palettes[palette_index][0])
    return base

def checker(draw, c1, c2, size=2):
    for y in range(0, TILE, size):
        for x in range(0, TILE, size):
            draw.rectangle([x, y, x+size-1, y+size-1], fill=c1 if ((x//size + y//size) % 2 == 0) else c2)

def horiz_stripes(draw, c1, c2, band=2):
    for y in range(0, TILE, band):
        draw.rectangle([0, y, TILE-1, y+band-1], fill=c1 if (y//band) % 2 == 0 else c2)

def diag_stitch(draw, c, step=3):
    for y in range(0, TILE, step):
        for x in range(0, TILE, step):
            if 0 <= x+y < TILE*2:
                draw.point((x, (y+x) % TILE), fill=c)

def border(draw, c, w=1):
    draw.rectangle([0,0,TILE-1,TILE-1], outline=c, width=w)

def scatter_pixels(draw, c, density=0.2, seed=0):
    import random
    rnd = random.Random(seed)
    total = int(TILE*TILE*density)
    for _ in range(total):
        draw.point((rnd.randrange(TILE), rnd.randrange(TILE)), fill=c)

def draw_ledge(draw, pal):
    highlight, mid, dark, shadow = pal[0], pal[1], pal[2], pal[3]
    draw.rectangle([0,0,TILE-1,5], fill=highlight)
    draw.line([0,5,TILE-1,5], fill=mid)
    draw.rectangle([0,6,TILE-1,12], fill=mid)
    for x in range(0, TILE, 2):
        draw.point((x, 10), fill=dark)
    draw.line([0,13,TILE-1,13], fill=shadow)

def stairs(draw, pal, vertical=False):
    c0,c1,c2,c3 = pal
    step_h = 4
    if vertical:
        for x in range(0, TILE, step_h):
            draw.rectangle([x,0,x+step_h-1,TILE-1], fill=c1 if (x//step_h)%2==0 else c2)
            draw.line([x,0,x,TILE-1], fill=c3)
    else:
        for y in range(0, TILE, step_h):
            draw.rectangle([0,y,TILE-1,y+step_h-1], fill=c1 if (y//step_h)%2==0 else c2)
            draw.line([0,y,TILE-1,y], fill=c3)

def simple_table(draw, pal):
    wood_l, wood_m, wood_d, shadow = pal
    draw.rectangle([1,5,14,10], fill=wood_m, outline=wood_d)
    draw.rectangle([2,11,4,15], fill=wood_d)
    draw.rectangle([11,11,13,15], fill=wood_d)
    draw.line([2,6,13,6], fill=wood_l)

def simple_chair(draw, pal):
    wood_l, wood_m, wood_d, shadow = pal
    draw.rectangle([5,8,10,14], fill=wood_m, outline=wood_d)
    draw.rectangle([6,4,9,8], fill=wood_m, outline=wood_d)
    draw.point((6,5), fill=wood_l)
    draw.point((8,9), fill=wood_l)

def simple_tv(draw, pal, screen_pal):
    body_l, body_m, body_d, shadow = pal
    draw.rectangle([2,3,13,12], fill=body_d, outline=shadow)
    draw.rectangle([3,4,12,10], fill=screen_pal[1])
    draw.rectangle([3,4,12,4], fill=screen_pal[0])
    draw.point((11,11), fill=screen_pal[2])

def simple_sign(draw, pal):
    light, mid, dark, shadow = pal
    draw.rectangle([2,4,13,10], fill=mid, outline=dark)
    draw.rectangle([7,11,8,15], fill=dark)
    draw.line([4,6,11,6], fill=light)
    draw.line([4,8,11,8], fill=light)

tiles_specs = [
    ("grass",        2, False, "grass"),
    ("tall_grass",   2, False, "tall_grass"),
    ("gravel",       5, False, "gravel"),
    ("path",         4, False, "path"),
    ("bush",         2, False, "bush"),
    ("rock",         5, False, "rock"),
    ("ledge",        5, False, "ledge"),
    ("stairs",       5, False, "stairs"),
    ("wall",         0, False, "wall"),
    ("roof",         7, False, "roof"),
    ("door",         0, True, "door"),
    ("wood_floor",   5, False, "wood_floor"),
    ("carpet",       3, False, "carpet"),
    ("table",        5, True,  "table"),
    ("chair",        5, True,  "chair"),
    ("tv",           0, True,  "tv"),
    ("sign",         0, True,  "sign"),
]

def render_tile(name, pal_idx, transparent, kind, out_dir):
    pal = tile_palettes[pal_idx]
    img = new_tile(pal_idx, transparent=transparent)
    d = ImageDraw.Draw(img)

    if kind == "grass":
        checker(d, pal[1], pal[0], size=2)
        scatter_pixels(d, pal[2], density=0.07, seed=1)
    elif kind == "tall_grass":
        checker(d, pal[1], pal[0], size=2)
        for x in range(0, TILE, 2):
            d.line([x, 0, x, TILE-1], fill=pal[2])
        scatter_pixels(d, pal[3], density=0.05, seed=2)
    elif kind == "gravel":
        checker(d, pal[1], pal[0], size=2)
        scatter_pixels(d, pal[2], density=0.12, seed=3)
        diag_stitch(d, pal[3], step=4)
    elif kind == "path":
        horiz_stripes(d, pal[1], pal[0], band=3)
        scatter_pixels(d, pal[2], density=0.08, seed=4)
    elif kind == "bush":
        checker(d, pal[1], pal[0], size=2)
        d.ellipse([2,2,13,13], fill=pal[1], outline=pal[2])
        d.point((5,6), fill=pal[0])
        d.point((9,7), fill=pal[0])
    elif kind == "rock":
        d.polygon([(3,12),(2,8),(5,4),(10,3),(13,6),(12,11)], fill=pal[1], outline=pal[2])
        d.line([5,6,9,5], fill=pal[0])
        d.line([7,7,10,9], fill=pal[3])
    elif kind == "ledge":
        draw_ledge(d, pal)
    elif kind == "stairs":
        stairs(d, pal, vertical=False)
    elif kind == "wall":
        brick_h=5
        for y in range(0,TILE,brick_h):
            d.rectangle([0,y,TILE-1,y+brick_h-1], fill=pal[1] if (y//brick_h)%2==0 else pal[0])
            d.line([0,y,TILE-1,y], fill=pal[3])
            offset = 0 if (y//brick_h)%2==0 else brick_h//2
            for x in range(offset, TILE, brick_h):
                d.line([x,y,x,y+brick_h-1], fill=pal[3])
    elif kind == "roof":
        for y in range(0,TILE,4):
            for x in range(0,TILE,4):
                d.rectangle([x,y,x+3,y+3], fill=pal[1] if ((x+y)//4)%2==0 else pal[0], outline=pal[2])
    elif kind == "door":
        d.rectangle([3,1,12,14], fill=pal[1], outline=pal[2])
        d.rectangle([4,2,11,10], outline=pal[3])
        d.point((10,8), fill=pal[3])
    elif kind == "wood_floor":
        for x in range(0,TILE,4):
            d.rectangle([x,0,x+3,TILE-1], fill=pal[1] if (x//4)%2==0 else pal[0])
            d.line([x,0,x,TILE-1], fill=pal[2])
        diag_stitch(d, pal[3], step=4)
    elif kind == "carpet":
        checker(d, pal[1], pal[0], size=2)
        border(d, pal[2], w=1)
        d.rectangle([3,3,12,12], outline=pal[3])
    elif kind == "table":
        simple_table(d, pal)
    elif kind == "chair":
        simple_chair(d, pal)
    elif kind == "tv":
        simple_tv(d, pal, tile_palettes[3])
    elif kind == "sign":
        simple_sign(d, pal)
    else:
        checker(d, pal[1], pal[0], size=2)

    os.makedirs(out_dir, exist_ok=True)
    img.save(os.path.join(out_dir, f"{name}.png"), "PNG")
    return img

def run(output_root="/mnt/data/gbc_tiles"):
    os.makedirs(output_root, exist_ok=True)
    generated = []
    for fname, pidx, transp, kind in tiles_specs:
        img = render_tile(fname, pidx, transp, kind, output_root)
        generated.append((fname, img))

    cols = 8
    rows = math.ceil(len(generated)/cols)
    sheet = Image.new("RGBA", (cols*TILE, rows*TILE), (0,0,0,0))
    for i,(name, img) in enumerate(generated):
        x = (i % cols) * TILE
        y = (i // cols) * TILE
        sheet.paste(img, (x,y), mask=img if img.mode=="RGBA" else None)
    sheet_path = os.path.join(output_root, "preview.png")
    sheet.save(sheet_path, "PNG")

    zip_path = "/mnt/data/gbc_tiles_pokemon_crystal_style.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname, _ in generated:
            zf.write(os.path.join(output_root, f"{fname}.png"), arcname=f"{fname}.png")
        zf.write(sheet_path, arcname="preview.png")
    return zip_path, sheet_path

if __name__ == "__main__":
    run()

# -------- Sprite generation (16x16, 4-directions) --------
def new_sprite(palette_index):
    # transparent background sprite canvas
    return Image.new("RGBA", (TILE, TILE), (0,0,0,0)), tile_palettes[palette_index]

def draw_chibi_base(d, pal, facing="down"):
    # Very simple 16x16 chibi using 3 tones.
    light, mid, dark, shadow = pal

    # HEAD (oval-ish)
    d.ellipse([4,2,11,8], fill=light, outline=dark)

    # HAIR/HAT band
    d.rectangle([4,2,11,3], fill=mid)
    d.point((5,4), fill=mid); d.point((9,4), fill=mid)

    # EYES / face depending on facing
    if facing == "down":
        d.point((6,6), fill=dark)
        d.point((9,6), fill=dark)
        d.point((7,7), fill=dark)  # mouth
    elif facing == "up":
        d.point((6,5), fill=mid); d.point((8,5), fill=mid)
        d.line([5,4,10,4], fill=mid)
    elif facing == "left":
        d.point((6,6), fill=dark)
    elif facing == "right":
        d.point((9,6), fill=dark)

    # BODY (torso)
    d.rectangle([5,9,10,12], fill=mid, outline=dark)
    # ARMS
    d.point((4,10), fill=mid); d.point((11,10), fill=mid)

    # LEGS
    if facing in ("down","up"):
        d.rectangle([5,13,7,15], fill=dark)   # left leg
        d.rectangle([8,13,10,15], fill=dark)  # right leg
    elif facing == "left":
        d.rectangle([6,13,8,15], fill=dark)
        d.rectangle([4,13,5,15], fill=shadow)
    else:  # right
        d.rectangle([7,13,9,15], fill=dark)
        d.rectangle([10,13,11,15], fill=shadow)

def make_character_set(name_prefix, pal_idx_char, out_dir):
    directions = ["down","up","left","right"]
    os.makedirs(out_dir, exist_ok=True)
    for facing in directions:
        img, pal = new_sprite(pal_idx_char)
        d = ImageDraw.Draw(img)
        draw_chibi_base(d, pal, facing=facing)
        img.save(os.path.join(out_dir, f"{name_prefix}_{facing}.png"), "PNG")

def run_sprites(output_root="/mnt/data/gbc_tiles"):
    # Player uses teal palette (6), NPCs use two variants
    make_character_set("player", 6, output_root)
    make_character_set("npcA", 5, output_root)  # earthy
    make_character_set("npcB", 1, output_root)  # red-brown
    return [
        os.path.join(output_root, f"{p}_{d}.png")
        for p in ("player","npcA","npcB")
        for d in ("down","up","left","right")
    ]

def run_all(output_root="/mnt/data/gbc_tiles"):
    # tiles
    zip_path, sheet_path = run(output_root)
    # sprites
    sprite_paths = run_sprites(output_root)
    # extend ZIP with sprites
    import zipfile
    with zipfile.ZipFile("/mnt/data/gbc_tiles_pokemon_crystal_style.zip", "a", zipfile.ZIP_DEFLATED) as zf:
        for sp in sprite_paths:
            zf.write(sp, arcname=os.path.basename(sp))
    return zip_path, sheet_path, sprite_paths

if __name__ == "__main__":
    run_all()
