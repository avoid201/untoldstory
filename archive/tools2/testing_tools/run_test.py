#!/usr/bin/env python3
"""
Schnelltest für TMX-Rendering Fix
"""

import subprocess
import sys
from pathlib import Path

def run_test():
    print("🎮 TMX Rendering Test Runner")
    print("=" * 60)
    
    options = """
Was möchtest du testen?

1. Debug Tilesets (prüft ob alle Dateien vorhanden sind)
2. Test TMX Rendering (zeigt die Map mit Fixes)
3. Hauptspiel starten
4. Tileset Vorschau (zeigt die Tileset-Bilder)

Wähle eine Option (1-4): """
    
    choice = input(options).strip()
    
    commands = {
        "1": "python debug_tilesets.py",
        "2": "python test_tmx_rendering.py", 
        "3": "python main.py",
        "4": "python -c \"import debug_tilesets; debug_tilesets.show_tileset_preview()\""
    }
    
    if choice in commands:
        print(f"\n▶️ Führe aus: {commands[choice]}\n")
        subprocess.run(commands[choice], shell=True)
    else:
        print("❌ Ungültige Auswahl")

if __name__ == "__main__":
    run_test()
