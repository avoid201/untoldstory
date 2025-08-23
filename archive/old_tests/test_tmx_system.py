#!/usr/bin/env python3
"""
Test TMX System - Testet das neue TMX-System direkt
"""

import pygame
import sys
from pathlib import Path

# Füge Projekt-Root zum Python-Path hinzu
sys.path.insert(0, str(Path.cwd()))

from tmx_integration_complete import ModernMapSystem

def test_tmx_system():
    """Testet das TMX-System mit der player_house Map"""
    
    print("\n" + "="*60)
    print("🎮 TMX SYSTEM TEST")
    print("="*60)
    
    # Pygame initialisieren
    pygame.init()
    screen = pygame.display.set_mode((320, 240))
    pygame.display.set_caption("TMX System Test - Player House")
    clock = pygame.time.Clock()
    
    # Fake Game-Objekt für Test
    class FakeGame:
        def __init__(self):
            self.story_manager = type('obj', (object,), {
                'get_flag': lambda self, flag: False,
                'set_flag': lambda self, flag, value: None
            })()
    
    game = FakeGame()
    
    # Map-System erstellen
    map_system = ModernMapSystem(game)
    
    # Lade player_house
    print("\n📋 Lade Map: player_house")
    tmx_map = map_system.load_map("player_house")
    
    if not tmx_map:
        print("❌ Fehler: Map konnte nicht geladen werden!")
        pygame.quit()
        return
    
    print(f"\n✅ Map erfolgreich geladen!")
    print(f"   Größe: {tmx_map.width}x{tmx_map.height} Tiles")
    print(f"   Layers: {list(tmx_map.layers.keys())}")
    print(f"   NPCs: {len(map_system.get_npcs())}")
    
    # Kamera-Position
    camera_x = 0
    camera_y = 0
    
    # Info-Text
    font = pygame.font.Font(None, 16)
    
    print("\n🎮 STEUERUNG:")
    print("   Pfeiltasten - Kamera bewegen")
    print("   SPACE - Warp-Test")
    print("   I - Interaktions-Info")
    print("   ESC - Beenden")
    print("\n" + "="*60)
    
    running = True
    show_info = True
    
    while running:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_LEFT:
                    camera_x = max(0, camera_x - 16)
                elif event.key == pygame.K_RIGHT:
                    camera_x = min((tmx_map.width - 20) * 16, camera_x + 16)
                elif event.key == pygame.K_UP:
                    camera_y = max(0, camera_y - 16)
                elif event.key == pygame.K_DOWN:
                    camera_y = min((tmx_map.height - 15) * 16, camera_y + 16)
                elif event.key == pygame.K_SPACE:
                    # Test Warp an Position 4,5 (Tür)
                    warp = map_system.check_warp(4, 5)
                    if warp:
                        print(f"✅ Warp gefunden: {warp['destination']['map']}")
                    else:
                        print("❌ Kein Warp an dieser Position")
                elif event.key == pygame.K_i:
                    show_info = not show_info
        
        # Clear
        screen.fill((20, 20, 30))
        
        # Rendere Map
        map_system.render(screen, camera_x, camera_y)
        
        # Rendere NPCs
        for npc in map_system.get_npcs():
            # Simple NPC-Darstellung (rotes Quadrat)
            npc_screen_x = npc.x - camera_x
            npc_screen_y = npc.y - camera_y
            if 0 <= npc_screen_x < 320 and 0 <= npc_screen_y < 240:
                pygame.draw.rect(screen, (255, 100, 100), 
                               (npc_screen_x, npc_screen_y, 14, 14))
                # NPC Name
                name_text = font.render(npc.name, True, (255, 255, 255))
                screen.blit(name_text, (npc_screen_x - 10, npc_screen_y - 15))
        
        # Info-Overlay
        if show_info:
            # Hintergrund
            info_surf = pygame.Surface((320, 60), pygame.SRCALPHA)
            info_surf.fill((0, 0, 0, 180))
            screen.blit(info_surf, (0, 0))
            
            # Text
            info_lines = [
                f"Map: player_house ({tmx_map.width}x{tmx_map.height})",
                f"Kamera: ({camera_x//16}, {camera_y//16})",
                f"NPCs: {len(map_system.get_npcs())} | Layers: {len(tmx_map.layers)}"
            ]
            
            y = 5
            for line in info_lines:
                text = font.render(line, True, (255, 255, 255))
                screen.blit(text, (5, y))
                y += 18
        
        # Hilfe-Text
        help_text = font.render("Pfeiltasten: Bewegen | I: Info | ESC: Beenden", True, (200, 200, 200))
        screen.blit(help_text, (5, 220))
        
        # Update
        pygame.display.flip()
        clock.tick(60)
    
    print("\n✅ Test beendet!")
    pygame.quit()

if __name__ == "__main__":
    test_tmx_system()
