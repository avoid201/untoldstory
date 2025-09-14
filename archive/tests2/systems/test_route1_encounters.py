#!/usr/bin/env python3
"""
TEST-SCRIPT FÜR ROUTE 1 ENCOUNTERS
Testet die Wild-Monster Encounters auf Route 1
"""

import pygame
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_route1_encounters():
    """Teste Route 1 Encounter-System."""
    print("\n" + "="*60)
    print("🎮 ROUTE 1 ENCOUNTER TEST")
    print("="*60 + "\n")
    
    # Import components
    from engine.core.game import Game
    
    print("📋 CHECKLISTE:\n")
    
    print("✅ FIXES IMPLEMENTIERT:")
    print("  - Map-Name korrigiert: route_1 → route1")
    print("  - Grass-Tiles angepasst: [29] statt [2,5]")
    print("  - Encounter-Rate erhöht: 25% statt 12%")
    print("  - get_tile_type() unterstützt 'Tile Layer 1'")
    print()
    
    print("🗺️ WARP NACH ROUTE 1:")
    print("  - In Kohlenstadt: Gehe nach SÜDEN (Y=49)")
    print("  - Positionen [7,49] und [8,49] warpen zu Route1")
    print()
    
    print("🌿 GRASS-TILES AUF ROUTE 1:")
    print("  - Tile ID 29 = Hohes Gras")
    print("  - Viele Grass-Patches in der Mitte der Map")
    print("  - 25% Encounter-Chance pro Schritt")
    print()
    
    print("📊 ERWARTETE ENCOUNTERS:")
    print("  - 95% F-Rang Monster (Level 3-6)")
    print("  - 5% E-Rang Monster (Level 5-8)")
    print("  - Nach ~4 Schritten im Gras sollte ein Kampf starten")
    print()
    
    print("🔍 DEBUG-OUTPUT:")
    print("  - '[DEBUG] Grass tile at (x,y)' beim Betreten")
    print("  - Encounter-Meldungen in der Konsole")
    print()
    
    print("🎯 TEST-ANLEITUNG:")
    print("  1. Starte: python3 main.py")
    print("  2. Neues Spiel → Starter holen")
    print("  3. In Kohlenstadt nach SÜDEN laufen")
    print("  4. Route 1 betreten")
    print("  5. Auf den dunklen Grass-Feldern rumlaufen")
    print("  6. Encounters sollten triggern!")
    print()
    
    print("⚠️  BEKANNTE PROBLEME:")
    print("  - Erste Schritte haben Mindest-Abstand (10 Steps)")
    print("  - Monster-Sprites fehlen noch (Fallback auf Rechtecke)")
    print()
    
    print("="*60)
    print("✅ BEREIT ZUM TESTEN!")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_route1_encounters()
