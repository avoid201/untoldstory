#!/usr/bin/env python3
"""
Test-Skript für das Input-System
"""

import pygame
import sys
import os

# Füge das Projekt-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.core.input_manager import InputManager, InputConfig

def test_input():
    """Test das Input-System"""
    pygame.init()
    screen = pygame.display.set_mode((320, 240))
    pygame.display.set_caption("Input Test")
    clock = pygame.time.Clock()
    
    # Erstelle Input-Manager
    input_manager = InputManager(InputConfig())
    
    print("🎮 Input-Test gestartet!")
    print("Verwende WASD oder Pfeiltasten zum Testen")
    print("ESC zum Beenden")
    
    running = True
    while running:
        # Events verarbeiten
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Input-Manager aktualisieren
        input_manager.update()
        
        # Teste Input
        movement_detected = False
        if input_manager.is_pressed('move_up'):
            print("↑ UP gedrückt")
            movement_detected = True
        if input_manager.is_pressed('move_down'):
            print("↓ DOWN gedrückt")
            movement_detected = True
        if input_manager.is_pressed('move_left'):
            print("← LEFT gedrückt")
            movement_detected = True
        if input_manager.is_pressed('move_right'):
            print("→ RIGHT gedrückt")
            movement_detected = True
        
        if input_manager.is_pressed('pause'):
            print("ESC gedrückt - Beende...")
            running = False
        
        # Screen clearen
        screen.fill((0, 0, 0))
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("Input-Test beendet!")

if __name__ == "__main__":
    test_input()
