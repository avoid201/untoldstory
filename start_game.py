#!/usr/bin/env python3
'''
Quick Launcher für Untold Story
Startet das Spiel mit optimalen Einstellungen
'''

import os
import sys
import subprocess

# Setze Umgebungsvariablen für bessere Performance
os.environ['SDL_VIDEO_ALLOW_SCREENSAVER'] = '1'
os.environ['SDL_HINT_RENDER_SCALE_QUALITY'] = '0'  # Pixel-perfect

# Starte das Spiel
try:
    subprocess.run([sys.executable, 'main.py'], check=True)
except KeyboardInterrupt:
    print("\nSpiel beendet.")
except Exception as e:
    print(f"Fehler: {e}")
    input("Drücke Enter zum Beenden...")
