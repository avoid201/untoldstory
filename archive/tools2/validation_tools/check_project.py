#!/usr/bin/env python3
"""
Projekt-Überprüfung für Untold Story
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def check_imports():
    """Überprüft, ob alle wichtigen Module importierbar sind"""
    print("🔍 ÜBERPRÜFE IMPORTS")
    print("=" * 60)
    
    modules_to_check = [
        ("engine.core.game", "Game"),
        ("engine.world.tile_manager", "TileManager"),
        ("engine.graphics.sprite_manager", "SpriteManager"),
        ("engine.world.area", "Area"),
        ("engine.world.map_loader", "MapLoader"),
        ("engine.world.npc_improved", "NPC"),
        ("engine.scenes.start_scene", "StartScene"),
        ("engine.world.interaction_manager", "InteractionManager"),
        ("engine.world.npc_manager", "NPCManager"),
        ("engine.systems.monsters", "Monster"),
        ("engine.systems.moves", "Move"),
        ("engine.systems.types", "TypeSystem"),
        ("engine.systems.battle.battle_system", "BattleSystem"),
        ("engine.ui.battle_ui", "BattleUI"),
    ]
    
    results = []
    for module_name, class_name in modules_to_check:
        try:
            module = __import__(module_name, fromlist=[class_name])
            if hasattr(module, class_name):
                print(f"✅ {module_name}.{class_name}")
                results.append(True)
            else:
                print(f"❌ {module_name}.{class_name} - Klasse nicht gefunden")
                results.append(False)
        except ImportError as e:
            print(f"❌ {module_name} - Import fehlgeschlagen: {e}")
            results.append(False)
        except Exception as e:
            print(f"❌ {module_name} - Fehler: {e}")
            results.append(False)
    
    return all(results)

def check_data_files():
    """Überprüft, ob alle wichtigen Datendateien existieren"""
    print("\n📁 ÜBERPRÜFE DATENDATEIEN")
    print("=" * 60)
    
    files_to_check = [
        "data/maps/player_house.tmx",
        "data/maps/kohlenstadt.tmx",
        "data/maps/museum.tmx",
        "data/game_data/npcs.json",
        "data/game_data/warps.json",
        "data/game_data/dialogues.json",
        "data/maps/interactions/player_house.json",
        "data/maps/interactions/kohlenstadt.json",
        "assets/gfx/tilesets/tileset.png",
    ]
    
    results = []
    for file_path in files_to_check:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
            results.append(True)
        else:
            print(f"❌ {file_path} - Datei fehlt")
            results.append(False)
    
    return all(results)

def check_tmx_files():
    """Überprüft TMX-Dateien auf Konsistenz"""
    print("\n🗺️ ÜBERPRÜFE TMX-DATEIEN")
    print("=" * 60)
    
    maps_dir = PROJECT_ROOT / "data" / "maps"
    tmx_files = list(maps_dir.glob("*.tmx"))
    
    print(f"Gefundene TMX-Dateien: {len(tmx_files)}")
    
    for tmx_file in tmx_files[:5]:  # Zeige nur erste 5
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(tmx_file)
            root = tree.getroot()
            
            width = root.get('width', 'N/A')
            height = root.get('height', 'N/A')
            layers = len(root.findall('.//layer'))
            
            print(f"  ✅ {tmx_file.name}: {width}x{height}, {layers} Layer")
        except Exception as e:
            print(f"  ❌ {tmx_file.name}: Fehler beim Lesen - {e}")
    
    return len(tmx_files) > 0

def check_json_data():
    """Überprüft JSON-Daten auf Korrektheit"""
    print("\n📋 ÜBERPRÜFE JSON-DATEN")
    print("=" * 60)
    
    import json
    
    json_files = {
        "NPCs": PROJECT_ROOT / "data" / "game_data" / "npcs.json",
        "Warps": PROJECT_ROOT / "data" / "game_data" / "warps.json",
        "Dialogues": PROJECT_ROOT / "data" / "game_data" / "dialogues.json",
    }
    
    results = []
    for name, file_path in json_files.items():
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"✅ {name}: {len(data)} Einträge")
                    results.append(True)
            except json.JSONDecodeError as e:
                print(f"❌ {name}: JSON-Fehler - {e}")
                results.append(False)
        else:
            print(f"❌ {name}: Datei fehlt")
            results.append(False)
    
    return all(results)

def check_pygame():
    """Überprüft Pygame-Installation"""
    print("\n🎮 ÜBERPRÜFE PYGAME")
    print("=" * 60)
    
    try:
        import pygame
        pygame.init()
        
        version = pygame.version.ver
        print(f"✅ Pygame Version: {version}")
        
        # Teste Display
        test_surface = pygame.Surface((100, 100))
        print(f"✅ Surface-Erstellung funktioniert")
        
        pygame.quit()
        return True
    except Exception as e:
        print(f"❌ Pygame-Fehler: {e}")
        return False

def main():
    """Hauptfunktion"""
    print("🎮 UNTOLD STORY - PROJEKT-ÜBERPRÜFUNG")
    print("=" * 60)
    
    results = []
    
    # Führe alle Checks durch
    results.append(("Imports", check_imports()))
    results.append(("Datendateien", check_data_files()))
    results.append(("TMX-Dateien", check_tmx_files()))
    results.append(("JSON-Daten", check_json_data()))
    results.append(("Pygame", check_pygame()))
    
    # Zusammenfassung
    print("\n" + "=" * 60)
    print("📊 ZUSAMMENFASSUNG")
    print("=" * 60)
    
    all_passed = True
    for check_name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ALLE CHECKS BESTANDEN!")
        print("Das Projekt ist bereit zum Starten.")
        print("\nStarte das Spiel mit: python3 main.py")
    else:
        print("\n⚠️ EINIGE CHECKS FEHLGESCHLAGEN!")
        print("Bitte behebe die Fehler vor dem Start.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
