#!/usr/bin/env python3
"""
Quick-Fix für fehlende TYPE_CHECKING Imports
"""

import os
from pathlib import Path

def fix_type_checking_imports():
    """Fixt alle fehlenden TYPE_CHECKING Imports."""
    
    battle_path = Path("/Users/leon/Desktop/untold_story/engine/systems/battle")
    
    files_to_check = [
        "battle_validation.py",
        "battle_actions.py",
        "battle_ai.py"
    ]
    
    for filename in files_to_check:
        filepath = battle_path / filename
        if filepath.exists():
            print(f"Prüfe {filename}...")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prüfe ob TYPE_CHECKING verwendet wird aber nicht importiert
            if "if TYPE_CHECKING:" in content and "from typing import" in content:
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    # Finde typing import
                    if line.startswith("from typing import") and "TYPE_CHECKING" not in line:
                        # Füge TYPE_CHECKING hinzu
                        if line.rstrip().endswith(','):
                            lines[i] = line.rstrip() + ' TYPE_CHECKING'
                        else:
                            lines[i] = line.rstrip() + ', TYPE_CHECKING'
                        print(f"  ✅ TYPE_CHECKING zu {filename} hinzugefügt")
                        
                        # Schreibe zurück
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(lines))
                        break

if __name__ == "__main__":
    fix_type_checking_imports()
    print("✅ Alle TYPE_CHECKING Imports gefixt!")
