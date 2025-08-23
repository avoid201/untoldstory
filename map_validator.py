#!/usr/bin/env python3
"""
Map Validator für Untold Story
===============================
Validiert die migrierten Maps auf Konsistenz und Fehler
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class ValidationError:
    """Repräsentiert einen Validierungsfehler"""
    map_name: str
    error_type: str
    message: str
    severity: str  # "error", "warning", "info"
    location: str = ""

class MapValidator:
    """Validiert Maps auf Konsistenz und Korrektheit"""
    
    def __init__(self, maps_dir: str = "data/maps"):
        self.maps_dir = Path(maps_dir)
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.info: List[ValidationError] = []
        
        # Erwartete Layer
        self.required_layers = ["ground", "collision"]
        self.optional_layers = ["decor", "furniture", "decoration"]
        
        # Bekannte Maps für Warp-Validierung
        self.known_maps: Set[str] = set()
        
    def load_map(self, filepath: Path) -> Dict[str, Any]:
        """Lädt eine Map-JSON Datei"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            self.add_error(filepath.stem, "JSON_ERROR", f"Fehlerhafte JSON-Syntax: {str(e)}")
            return None
        except Exception as e:
            self.add_error(filepath.stem, "FILE_ERROR", f"Datei konnte nicht geladen werden: {str(e)}")
            return None
    
    def add_error(self, map_name: str, error_type: str, message: str, location: str = ""):
        """Fügt einen Fehler hinzu"""
        self.errors.append(ValidationError(map_name, error_type, message, "error", location))
    
    def add_warning(self, map_name: str, error_type: str, message: str, location: str = ""):
        """Fügt eine Warnung hinzu"""
        self.warnings.append(ValidationError(map_name, error_type, message, "warning", location))
    
    def add_info(self, map_name: str, error_type: str, message: str, location: str = ""):
        """Fügt eine Info-Meldung hinzu"""
        self.info.append(ValidationError(map_name, error_type, message, "info", location))
    
    def validate_structure(self, map_name: str, map_data: Dict[str, Any]) -> bool:
        """Validiert die grundlegende Map-Struktur"""
        if not map_data:
            return False
        
        # Prüfe ob ID vorhanden und korrekt
        if "id" not in map_data:
            self.add_error(map_name, "MISSING_ID", "Map hat keine ID")
        elif map_data["id"] != map_name:
            self.add_warning(map_name, "ID_MISMATCH", 
                           f"Map-ID '{map_data['id']}' stimmt nicht mit Dateiname '{map_name}' überein")
        
        # Prüfe ob Name vorhanden
        if "name" not in map_data:
            self.add_warning(map_name, "MISSING_NAME", "Map hat keinen Namen")
        
        # Prüfe ob Dimensionen vorhanden
        if "width" not in map_data or "height" not in map_data:
            self.add_error(map_name, "MISSING_DIMENSIONS", "Map-Dimensionen fehlen")
            return False
        
        return True
    
    def validate_layers(self, map_name: str, map_data: Dict[str, Any]) -> bool:
        """Validiert die Layer-Struktur"""
        if "layers" not in map_data:
            self.add_error(map_name, "MISSING_LAYERS", "Keine Layer vorhanden")
            return False
        
        layers = map_data["layers"]
        width = map_data.get("width", 0)
        height = map_data.get("height", 0)
        
        # Prüfe erforderliche Layer
        for layer_name in self.required_layers:
            if layer_name not in layers:
                self.add_error(map_name, "MISSING_LAYER", f"Erforderlicher Layer '{layer_name}' fehlt")
                continue
            
            # Prüfe Layer-Dimensionen
            layer = layers[layer_name]
            if not isinstance(layer, list):
                self.add_error(map_name, "INVALID_LAYER", f"Layer '{layer_name}' ist kein Array")
                continue
            
            if len(layer) != height:
                self.add_error(map_name, "LAYER_SIZE", 
                             f"Layer '{layer_name}' hat falsche Höhe: {len(layer)} statt {height}")
            
            for y, row in enumerate(layer):
                if len(row) != width:
                    self.add_error(map_name, "LAYER_SIZE",
                                 f"Layer '{layer_name}' Zeile {y} hat falsche Breite: {len(row)} statt {width}")
                    break
        
        # Info über optionale Layer
        for layer_name in self.optional_layers:
            if layer_name not in layers:
                self.add_info(map_name, "OPTIONAL_LAYER", f"Optionaler Layer '{layer_name}' nicht vorhanden")
        
        return True
    
    def validate_warps(self, map_name: str, map_data: Dict[str, Any]) -> bool:
        """Validiert Warp-Punkte"""
        if "warps" not in map_data:
            self.add_info(map_name, "NO_WARPS", "Keine Warps definiert")
            return True
        
        warps = map_data["warps"]
        width = map_data.get("width", 0)
        height = map_data.get("height", 0)
        
        warp_pairs = defaultdict(list)
        
        for i, warp in enumerate(warps):
            # Prüfe Warp-Struktur
            required_fields = ["x", "y", "to"]
            for field in required_fields:
                if field not in warp:
                    self.add_error(map_name, "INVALID_WARP", 
                                 f"Warp {i} fehlt Feld '{field}'", f"warp[{i}]")
            
            # Prüfe Position
            x, y = warp.get("x", -1), warp.get("y", -1)
            if not (0 <= x < width and 0 <= y < height):
                self.add_error(map_name, "WARP_OUT_OF_BOUNDS",
                             f"Warp bei ({x},{y}) außerhalb der Map", f"warp[{i}]")
            
            # Prüfe Ziel-Map
            target_map = warp.get("to", "")
            if target_map and target_map not in self.known_maps:
                self.add_warning(map_name, "UNKNOWN_TARGET",
                               f"Warp zeigt auf unbekannte Map '{target_map}'", f"warp[{i}]")
            
            # Sammle für Paar-Validierung
            if target_map:
                warp_pairs[target_map].append((x, y))
        
        # Prüfe ob Türen paarweise Warps haben
        for target, positions in warp_pairs.items():
            if len(positions) % 2 != 0:
                self.add_warning(map_name, "UNPAIRED_WARP",
                               f"Ungerade Anzahl von Warps nach '{target}' ({len(positions)})")
        
        return True
    
    def validate_npcs(self, map_name: str, map_data: Dict[str, Any]) -> bool:
        """Validiert NPCs"""
        if "npcs" not in map_data:
            self.add_info(map_name, "NO_NPCS", "Keine NPCs definiert")
            return True
        
        npcs = map_data["npcs"]
        width = map_data.get("width", 0)
        height = map_data.get("height", 0)
        collision_layer = map_data.get("layers", {}).get("collision", [])
        
        npc_positions = set()
        
        for i, npc in enumerate(npcs):
            # Prüfe NPC-Struktur
            if "id" not in npc:
                self.add_error(map_name, "NPC_NO_ID", f"NPC {i} hat keine ID", f"npc[{i}]")
            
            if "name" not in npc:
                self.add_warning(map_name, "NPC_NO_NAME", f"NPC {i} hat keinen Namen", f"npc[{i}]")
            
            # Prüfe Position
            x, y = npc.get("x", -1), npc.get("y", -1)
            if not (0 <= x < width and 0 <= y < height):
                self.add_error(map_name, "NPC_OUT_OF_BOUNDS",
                             f"NPC '{npc.get('name', 'unnamed')}' bei ({x},{y}) außerhalb der Map", 
                             f"npc[{i}]")
            
            # Prüfe ob Position blockiert ist
            if collision_layer and 0 <= y < len(collision_layer) and 0 <= x < len(collision_layer[y]):
                if collision_layer[y][x] == 1:
                    self.add_warning(map_name, "NPC_ON_COLLISION",
                                   f"NPC '{npc.get('name', 'unnamed')}' steht auf blockiertem Feld ({x},{y})",
                                   f"npc[{i}]")
            
            # Prüfe auf doppelte Positionen
            if (x, y) in npc_positions:
                self.add_warning(map_name, "DUPLICATE_NPC_POS",
                               f"Mehrere NPCs auf Position ({x},{y})", f"npc[{i}]")
            npc_positions.add((x, y))
            
            # Prüfe Dialog
            if "dialogue" not in npc or not npc["dialogue"]:
                self.add_info(map_name, "NPC_NO_DIALOGUE",
                            f"NPC '{npc.get('name', 'unnamed')}' hat keinen Dialog", f"npc[{i}]")
        
        return True
    
    def validate_triggers(self, map_name: str, map_data: Dict[str, Any]) -> bool:
        """Validiert Trigger (Schilder, Examine-Objekte)"""
        if "triggers" not in map_data:
            self.add_info(map_name, "NO_TRIGGERS", "Keine Trigger definiert")
            return True
        
        triggers = map_data["triggers"]
        width = map_data.get("width", 0)
        height = map_data.get("height", 0)
        
        for i, trigger in enumerate(triggers):
            # Prüfe Trigger-Struktur
            if "event" not in trigger:
                self.add_error(map_name, "TRIGGER_NO_EVENT",
                             f"Trigger {i} hat kein Event", f"trigger[{i}]")
            
            if "text" not in trigger:
                self.add_warning(map_name, "TRIGGER_NO_TEXT",
                               f"Trigger {i} hat keinen Text", f"trigger[{i}]")
            
            # Prüfe Position
            x, y = trigger.get("x", -1), trigger.get("y", -1)
            if not (0 <= x < width and 0 <= y < height):
                self.add_error(map_name, "TRIGGER_OUT_OF_BOUNDS",
                             f"Trigger bei ({x},{y}) außerhalb der Map", f"trigger[{i}]")
            
            # Prüfe Event-Typ
            event_type = trigger.get("event", "")
            valid_events = ["sign", "interact", "examine", "cutscene", "battle"]
            if event_type and event_type not in valid_events:
                self.add_warning(map_name, "UNKNOWN_EVENT",
                               f"Unbekannter Event-Typ '{event_type}'", f"trigger[{i}]")
        
        return True
    
    def cross_validate_warps(self, all_maps: Dict[str, Dict[str, Any]]) -> None:
        """Prüft ob Warps bidirektional korrekt verknüpft sind"""
        print("\n🔗 Cross-Validierung der Warps...")
        
        for map_name, map_data in all_maps.items():
            if not map_data or "warps" not in map_data:
                continue
            
            for warp in map_data["warps"]:
                target_map = warp.get("to", "")
                if not target_map or target_map not in all_maps:
                    continue
                
                target_x = warp.get("to_x", -1)
                target_y = warp.get("to_y", -1)
                
                # Suche Rück-Warp in Ziel-Map
                target_data = all_maps[target_map]
                if "warps" not in target_data:
                    self.add_warning(map_name, "NO_RETURN_WARP",
                                   f"Ziel-Map '{target_map}' hat keine Warps zurück")
                    continue
                
                found_return = False
                for target_warp in target_data["warps"]:
                    if (target_warp.get("to") == map_name and
                        abs(target_warp.get("x", -999) - target_x) <= 1 and
                        abs(target_warp.get("y", -999) - target_y) <= 1):
                        found_return = True
                        break
                
                if not found_return:
                    self.add_info(map_name, "MISSING_RETURN_WARP",
                                f"Kein Rück-Warp von '{target_map}' bei ({target_x},{target_y})")
    
    def validate_all(self) -> Tuple[int, int, int]:
        """
        Validiert alle Maps im Verzeichnis
        
        Returns:
            Tuple (Anzahl Fehler, Anzahl Warnungen, Anzahl Infos)
        """
        # Reset
        self.errors = []
        self.warnings = []
        self.info = []
        
        # Sammle alle Map-Dateien
        map_files = list(self.maps_dir.glob("*.json"))
        self.known_maps = {f.stem for f in map_files}
        
        print(f"🔍 Validiere {len(map_files)} Maps in {self.maps_dir}")
        print("=" * 50)
        
        all_maps = {}
        
        # Validiere jede Map einzeln
        for map_file in map_files:
            map_name = map_file.stem
            print(f"\n📋 Validiere: {map_name}")
            
            map_data = self.load_map(map_file)
            if map_data:
                all_maps[map_name] = map_data
                
                self.validate_structure(map_name, map_data)
                self.validate_layers(map_name, map_data)
                self.validate_warps(map_name, map_data)
                self.validate_npcs(map_name, map_data)
                self.validate_triggers(map_name, map_data)
        
        # Cross-Validierung
        self.cross_validate_warps(all_maps)
        
        return len(self.errors), len(self.warnings), len(self.info)
    
    def print_report(self) -> None:
        """Gibt einen formatierten Report aus"""
        print("\n" + "=" * 60)
        print("📊 VALIDIERUNGSBERICHT")
        print("=" * 60)
        
        # Fehler
        if self.errors:
            print(f"\n❌ FEHLER ({len(self.errors)}):")
            print("-" * 40)
            for error in self.errors:
                location = f" [{error.location}]" if error.location else ""
                print(f"  • {error.map_name}: {error.message}{location}")
        
        # Warnungen
        if self.warnings:
            print(f"\n⚠️  WARNUNGEN ({len(self.warnings)}):")
            print("-" * 40)
            for warning in self.warnings:
                location = f" [{warning.location}]" if warning.location else ""
                print(f"  • {warning.map_name}: {warning.message}{location}")
        
        # Infos
        if self.info:
            print(f"\nℹ️  INFORMATIONEN ({len(self.info)}):")
            print("-" * 40)
            for info_msg in self.info[:10]:  # Nur erste 10 Infos zeigen
                location = f" [{info_msg.location}]" if info_msg.location else ""
                print(f"  • {info_msg.map_name}: {info_msg.message}{location}")
            if len(self.info) > 10:
                print(f"  ... und {len(self.info) - 10} weitere Infos")
        
        # Zusammenfassung
        print("\n" + "=" * 60)
        if not self.errors:
            print("✅ Keine kritischen Fehler gefunden!")
        else:
            print(f"❌ {len(self.errors)} kritische Fehler müssen behoben werden!")
        
        if self.warnings:
            print(f"⚠️  {len(self.warnings)} Warnungen sollten überprüft werden.")
        
        print("=" * 60)
    
    def export_report(self, filepath: str = "validation_report.json") -> None:
        """Exportiert den Report als JSON"""
        report = {
            "summary": {
                "errors": len(self.errors),
                "warnings": len(self.warnings),
                "info": len(self.info)
            },
            "errors": [vars(e) for e in self.errors],
            "warnings": [vars(w) for w in self.warnings],
            "info": [vars(i) for i in self.info]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Report exportiert nach: {filepath}")

def main():
    """Hauptfunktion"""
    import sys
    
    # Verzeichnis aus Argumenten oder Standard
    maps_dir = sys.argv[1] if len(sys.argv) > 1 else "data/maps"
    
    # Validator initialisieren
    validator = MapValidator(maps_dir)
    
    # Validierung durchführen
    errors, warnings, infos = validator.validate_all()
    
    # Report ausgeben
    validator.print_report()
    
    # Optional: Report exportieren
    if "--export" in sys.argv:
        validator.export_report()
    
    # Exit-Code basierend auf Fehlern
    sys.exit(1 if errors > 0 else 0)

if __name__ == "__main__":
    main()