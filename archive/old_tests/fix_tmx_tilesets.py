#!/usr/bin/env python3
"""
Fix TMX Tileset References
Korrigiert die Pfad-Referenzen in TMX-Dateien
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import shutil

def fix_tmx_tileset_references():
    """Korrigiert die Tileset-Referenzen in allen TMX-Dateien"""
    
    print("=" * 60)
    print("🔧 TMX TILESET REFERENCE FIXER")
    print("=" * 60)
    
    # Pfade
    maps_dir = Path("data/maps")
    tiles_dir = Path("assets/gfx/tiles")
    
    # 1. Verschiebe TSX-Dateien an die richtige Stelle
    print("\n1️⃣ Verschiebe TSX-Dateien:")
    tsx_files = list(maps_dir.glob("*.tsx"))
    
    for tsx_file in tsx_files:
        target_path = tiles_dir / tsx_file.name
        
        # Prüfe ob Datei bereits existiert
        if target_path.exists():
            print(f"   ✅ {tsx_file.name} existiert bereits in assets/gfx/tiles/")
        else:
            # Kopiere TSX-Datei
            shutil.copy2(tsx_file, target_path)
            print(f"   📋 Kopiert: {tsx_file.name} -> assets/gfx/tiles/")
    
    # 2. Korrigiere TMX-Dateien
    print("\n2️⃣ Korrigiere TMX-Dateien:")
    tmx_files = list(maps_dir.glob("*.tmx"))
    
    for tmx_file in tmx_files:
        print(f"\n   📄 {tmx_file.name}:")
        
        try:
            # Parse TMX
            tree = ET.parse(tmx_file)
            root = tree.getroot()
            
            # Finde alle Tileset-Referenzen
            tilesets = root.findall("tileset")
            
            for tileset in tilesets:
                source = tileset.get("source", "")
                
                if not source:
                    continue
                
                # Extrahiere TSX-Dateiname
                tsx_name = Path(source).name
                
                # Bestimme korrekten Pfad
                if tsx_name.startswith("tiles_"):
                    # Sollte in assets/gfx/tiles/ sein
                    new_source = f"../../assets/gfx/tiles/{tsx_name}"
                elif tsx_name.startswith("objects"):
                    # Objects TSX bleibt im maps-Ordner
                    new_source = tsx_name
                else:
                    # Unbekannt - behalte relativen Pfad
                    new_source = tsx_name
                
                # Update nur wenn nötig
                if source != new_source:
                    tileset.set("source", new_source)
                    print(f"      ✏️  {source} -> {new_source}")
                else:
                    print(f"      ✅ {source} (korrekt)")
            
            # Speichere korrigierte TMX
            tree.write(tmx_file, encoding="UTF-8", xml_declaration=True)
            
        except Exception as e:
            print(f"      ❌ Fehler: {e}")
    
    # 3. Erstelle Backup der originalen TMX-Dateien
    print("\n3️⃣ Erstelle Backups:")
    backup_dir = maps_dir / "backup_tmx"
    backup_dir.mkdir(exist_ok=True)
    
    for tmx_file in tmx_files:
        backup_file = backup_dir / tmx_file.name
        if not backup_file.exists():
            shutil.copy2(tmx_file, backup_file)
            print(f"   💾 Backup: {tmx_file.name}")
    
    print("\n" + "=" * 60)
    print("✅ FERTIG!")
    print("=" * 60)
    print("\nNächste Schritte:")
    print("1. Teste das Spiel mit: python3 main.py")
    print("2. Bei Problemen: Restore aus data/maps/backup_tmx/")

if __name__ == "__main__":
    fix_tmx_tileset_references()
