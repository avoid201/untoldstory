#!/usr/bin/env python3
"""
Test-Skript für TMX-Rendering
"""

import pygame
import sys
from pathlib import Path

# Füge Projekt-Root zum Path hinzu
sys.path.insert(0, str(Path.cwd()))

from engine.world.area import Area
from engine.graphics.sprite_manager import SpriteManager

def test_tmx_rendering():
    """Testet das TMX-Rendering mit der gepatchten Area-Klasse"""
    
    # Initialisiere Pygame
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("TMX Rendering Test")
    clock = pygame.time.Clock()
    
    # Initialisiere SpriteManager
    sprite_manager = SpriteManager.get()
    
    # Lade Test-Map
    print("Lade player_house Map...")
    area = Area("player_house")
    
    # Kamera-Position
    camera_x = 0
    camera_y = 0
    
    # Game Loop
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Kamera-Steuerung
        keys = pygame.key.get_pressed()
        camera_speed = 200 * dt  # Pixel pro Sekunde
        
        if keys[pygame.K_LEFT]:
            camera_x -= camera_speed
        if keys[pygame.K_RIGHT]:
            camera_x += camera_speed
        if keys[pygame.K_UP]:
            camera_y -= camera_speed
        if keys[pygame.K_DOWN]:
            camera_y += camera_speed
        
        # Update
        area.update(dt)
        
        # Draw
        screen.fill((0, 0, 0))
        area.draw(screen, camera_x, camera_y)
        
        # Info-Text
        font = pygame.font.Font(None, 36)
        text = font.render(f"TMX Test - Pfeiltasten zum Bewegen", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        
        pygame.display.flip()
    
    pygame.quit()
    print("Test beendet.")

if __name__ == "__main__":
    test_tmx_rendering()
