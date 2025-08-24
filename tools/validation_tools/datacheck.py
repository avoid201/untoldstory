#!/usr/bin/env python3
"""
Data validation and consistency checker for Untold Story.
Validates JSON data files, checks references, and ensures data integrity.
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.core.config import DATA_DIR, MAPS_DIR


class ValidationLevel(Enum):
    """Validation severity levels."""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    level: ValidationLevel
    file: str
    message: str
    details: Optional[str] = None


class DataValidator:
    """Main data validation class."""
    
    def __init__(self, data_dir: Path = DATA_DIR):
        """
        Initialize data validator.
        
        Args:
            data_dir: Path to data directory
        """
        self.data_dir = Path(data_dir)
        self.results: List[ValidationResult] = []
        self.data_cache: Dict[str, Any] = {}
        
        # Load all data files
        self._load_data()
    
    def _load_data(self) -> None:
        """Load all JSON data files."""
        json_files = [
            "types.json",
            "moves.json", 
            "monsters.json",
            "items.json",
            "encounters.json"
        ]
        
        for filename in json_files:
            filepath = self.data_dir / filename
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.data_cache[filename] = json.load(f)
                except json.JSONDecodeError as e:
                    self.results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        file=filename,
                        message=f"Failed to parse JSON",
                        details=str(e)
                    ))
            else:
                self.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    file=filename,
                    message="File not found"
                ))
    
    def validate_all(self) -> List[ValidationResult]:
        """
        Run all validation checks.
        
        Returns:
            List of validation results
        """
        self.results.clear()
        
        # Validate each data type
        self.validate_types()
        self.validate_moves()
        self.validate_monsters()
        self.validate_items()
        self.validate_maps()
        self.validate_encounters()
        self.validate_cross_references()
        
        return self.results
    
    def validate_types(self) -> None:
        """Validate type system data."""
        if "types.json" not in self.data_cache:
            return
        
        data = self.data_cache["types.json"]
        
        # Check for required fields
        if "types" not in data:
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                file="types.json",
                message="Missing 'types' field"
            ))
            return
        
        types = data["types"]
        
        # Check type effectiveness chart
        if "chart" in data:
            for entry in data["chart"]:
                if "attacker" not in entry or "defender" not in entry:
                    self.results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        file="types.json",
                        message="Invalid type chart entry",
                        details=str(entry)
                    ))
                    continue
                
                # Check if types exist
                if entry["attacker"] not in types:
                    self.results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        file="types.json",
                        message=f"Unknown attacker type: {entry['attacker']}"
                    ))
                
                if entry["defender"] not in types:
                    self.results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        file="types.json",
                        message=f"Unknown defender type: {entry['defender']}"
                    ))
                
                # Check multiplier range
                multiplier = entry.get("multiplier", 1.0)
                if multiplier < 0 or multiplier > 4:
                    self.results.append(ValidationResult(
                        level=ValidationLevel.WARNING,
                        file="types.json",
                        message=f"Unusual type multiplier: {multiplier}",
                        details=f"{entry['attacker']} vs {entry['defender']}"
                    ))
    
    def validate_moves(self) -> None:
        """Validate moves data."""
        if "moves.json" not in self.data_cache:
            return
        
        data = self.data_cache["moves.json"]
        types = self.data_cache.get("types.json", {}).get("types", [])
        
        if "moves" not in data:
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                file="moves.json",
                message="Missing 'moves' field"
            ))
            return
        
        move_ids = set()
        
        for move in data["moves"]:
            # Check required fields
            required = ["id", "name", "type", "category", "power", "accuracy", "pp"]
            for field in required:
                if field not in move:
                    self.results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        file="moves.json",
                        message=f"Move missing required field: {field}",
                        details=f"Move: {move.get('id', 'unknown')}"
                    ))
            
            # Check for duplicate IDs
            move_id = move.get("id")
            if move_id in move_ids:
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    file="moves.json",
                    message=f"Duplicate move ID: {move_id}"
                ))
            move_ids.add(move_id)
            
            # Validate type
            if types and move.get("type") not in types:
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    file="moves.json",
                    message=f"Unknown move type: {move.get('type')}",
                    details=f"Move: {move_id}"
                ))
            
            # Validate category
            valid_categories = ["phys", "mag", "support"]
            if move.get("category") not in valid_categories:
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    file="moves.json",
                    message=f"Invalid move category: {move.get('category')}",
                    details=f"Move: {move_id}"
                ))
            
            # Validate power and accuracy ranges
            power = move.get("power", 0)
            if power < 0 or power > 250:
                self.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    file="moves.json",
                    message=f"Unusual move power: {power}",
                    details=f"Move: {move_id}"
                ))
            
            accuracy = move.get("accuracy", 100)
            if accuracy < -1 or accuracy > 100:
                self.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    file="moves.json",
                    message=f"Invalid accuracy: {accuracy}",
                    details=f"Move: {move_id}"
                ))
    
    def validate_monsters(self) -> None:
        """Validate monsters data."""
        if "monsters.json" not in self.data_cache:
            return
        
        data = self.data_cache["monsters.json"]
        types = self.data_cache.get("types.json", {}).get("types", [])
        moves = {m["id"] for m in self.data_cache.get("moves.json", {}).get("moves", [])}
        
        if "monsters" not in data:
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                file="monsters.json",
                message="Missing 'monsters' field"
            ))
            return
        
        monster_ids = set()
        
        for monster in data["monsters"]:
            # Check required fields
            required = ["id", "name", "types", "base_stats", "rank"]
            for field in required:
                if field not in monster:
                    self.results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        file="monsters.json",
                        message=f"Monster missing required field: {field}",
                        details=f"Monster: {monster.get('id', 'unknown')}"
                    ))
            
            monster_id = monster.get("id")
            
            # Check for duplicate IDs
            if monster_id in monster_ids:
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    file="monsters.json",
                    message=f"Duplicate monster ID: {monster_id}"
                ))
            monster_ids.add(monster_id)
            
            # Validate types
            for mon_type in monster.get("types", []):
                if types and mon_type not in types:
                    self.results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        file="monsters.json",
                        message=f"Unknown monster type: {mon_type}",
                        details=f"Monster: {monster_id}"
                    ))
            
            # Validate rank
            valid_ranks = ["F", "E", "D", "C", "B", "A", "S", "SS", "X"]
            if monster.get("rank") not in valid_ranks:
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    file="monsters.json",
                    message=f"Invalid rank: {monster.get('rank')}",
                    details=f"Monster: {monster_id}"
                ))
            
            # Validate base stats
            base_stats = monster.get("base_stats", {})
            required_stats = ["hp", "atk", "def", "mag", "res", "spd"]
            for stat in required_stats:
                if stat not in base_stats:
                    self.results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        file="monsters.json",
                        message=f"Missing base stat: {stat}",
                        details=f"Monster: {monster_id}"
                    ))
                else:
                    value = base_stats[stat]
                    if value < 1 or value > 255:
                        self.results.append(ValidationResult(
                            level=ValidationLevel.WARNING,
                            file="monsters.json",
                            message=f"Unusual stat value: {stat}={value}",
                            details=f"Monster: {monster_id}"
                        ))
            
            # Validate learnset
            for learn_entry in monster.get("learnset", []):
                move_id = learn_entry.get("move")
                if moves and move_id not in moves:
                    self.results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        file="monsters.json",
                        message=f"Unknown move in learnset: {move_id}",
                        details=f"Monster: {monster_id}"
                    ))
                
                level = learn_entry.get("level", 1)
                if level < 1 or level > 100:
                    self.results.append(ValidationResult(
                        level=ValidationLevel.WARNING,
                        file="monsters.json",
                        message=f"Invalid learn level: {level}",
                        details=f"Monster: {monster_id}, Move: {move_id}"
                    ))
            
            # Validate evolution
            evolution = monster.get("evolution")
            if evolution:
                evo_to = evolution.get("to")
                if evo_to and evo_to not in monster_ids and evo_to != monster_id:
                    # Note: This might be a forward reference
                    self.results.append(ValidationResult(
                        level=ValidationLevel.INFO,
                        file="monsters.json",
                        message=f"Evolution target not yet defined: {evo_to}",
                        details=f"Monster: {monster_id}"
                    ))
    
    def validate_items(self) -> None:
        """Validate items data."""
        if "items.json" not in self.data_cache:
            return
        
        data = self.data_cache["items.json"]
        
        if "items" not in data:
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                file="items.json",
                message="Missing 'items' field"
            ))
            return
        
        item_ids = set()
        
        for item in data["items"]:
            # Check required fields
            required = ["id", "name", "description", "type", "price"]
            for field in required:
                if field not in item:
                    self.results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        file="items.json",
                        message=f"Item missing required field: {field}",
                        details=f"Item: {item.get('id', 'unknown')}"
                    ))
            
            item_id = item.get("id")
            
            # Check for duplicate IDs
            if item_id in item_ids:
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    file="items.json",
                    message=f"Duplicate item ID: {item_id}"
                ))
            item_ids.add(item_id)
            
            # Validate item type
            valid_types = ["healing", "buff", "taming", "evolution", "key", "battle", "equipment", "misc"]
            if item.get("type") not in valid_types:
                self.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    file="items.json",
                    message=f"Unknown item type: {item.get('type')}",
                    details=f"Item: {item_id}"
                ))
            
            # Validate price
            price = item.get("price", 0)
            if price < 0:
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    file="items.json",
                    message=f"Invalid price: {price}",
                    details=f"Item: {item_id}"
                ))
    
    def validate_maps(self) -> None:
        """Validate map files."""
        maps_dir = self.data_dir / "maps"
        if not maps_dir.exists():
            self.results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                file="maps",
                message="Maps directory not found"
            ))
            return
        
        for map_file in maps_dir.glob("*.json"):
            try:
                with open(map_file, 'r', encoding='utf-8') as f:
                    map_data = json.load(f)
                
                # Validate map structure
                self._validate_map_structure(map_file.name, map_data)
                
            except json.JSONDecodeError as e:
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    file=map_file.name,
                    message="Failed to parse map JSON",
                    details=str(e)
                ))
    
    def _validate_map_structure(self, filename: str, map_data: Dict) -> None:
        """Validate individual map structure."""
        # Check required fields
        required = ["id", "size", "layers"]
        for field in required:
            if field not in map_data:
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    file=filename,
                    message=f"Map missing required field: {field}"
                ))
        
        # Validate size
        size = map_data.get("size", {})
        if "w" not in size or "h" not in size:
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                file=filename,
                message="Invalid map size format"
            ))
        
        width = size.get("w", 0)
        height = size.get("h", 0)
        
        # Validate layers
        layers = map_data.get("layers", {})
        for layer_name, layer_data in layers.items():
            if isinstance(layer_data, list):
                # Check layer dimensions
                if len(layer_data) != height:
                    self.results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        file=filename,
                        message=f"Layer '{layer_name}' height mismatch",
                        details=f"Expected {height}, got {len(layer_data)}"
                    ))
                
                for row in layer_data:
                    if len(row) != width:
                        self.results.append(ValidationResult(
                            level=ValidationLevel.ERROR,
                            file=filename,
                            message=f"Layer '{layer_name}' width mismatch",
                            details=f"Expected {width}, got {len(row)}"
                        ))
        
        # Validate warps
        for warp in map_data.get("warps", []):
            if "to" not in warp:
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    file=filename,
                    message="Warp missing destination",
                    details=str(warp)
                ))
    
    def validate_encounters(self) -> None:
        """Validate encounter tables."""
        if "encounters.json" not in self.data_cache:
            return
        
        data = self.data_cache["encounters.json"]
        monsters = {m["id"] for m in self.data_cache.get("monsters.json", {}).get("monsters", [])}
        
        for area_id, encounters in data.items():
            for terrain, encounter_list in encounters.items():
                for encounter in encounter_list:
                    monster_id = encounter.get("monster")
                    
                    if monsters and monster_id not in monsters:
                        self.results.append(ValidationResult(
                            level=ValidationLevel.ERROR,
                            file="encounters.json",
                            message=f"Unknown monster in encounters: {monster_id}",
                            details=f"Area: {area_id}, Terrain: {terrain}"
                        ))
                    
                    # Validate level range
                    min_level = encounter.get("min_level", 1)
                    max_level = encounter.get("max_level", 100)
                    
                    if min_level < 1 or max_level > 100 or min_level > max_level:
                        self.results.append(ValidationResult(
                            level=ValidationLevel.WARNING,
                            file="encounters.json",
                            message=f"Invalid level range: {min_level}-{max_level}",
                            details=f"Monster: {monster_id}, Area: {area_id}"
                        ))
                    
                    # Validate weight
                    weight = encounter.get("weight", 1)
                    if weight <= 0:
                        self.results.append(ValidationResult(
                            level=ValidationLevel.ERROR,
                            file="encounters.json",
                            message=f"Invalid encounter weight: {weight}",
                            details=f"Monster: {monster_id}, Area: {area_id}"
                        ))
    
    def validate_cross_references(self) -> None:
        """Validate cross-references between data files."""
        # This is where we'd check things like:
        # - Evolution targets exist
        # - Item effects reference valid moves/monsters
        # - Quest rewards reference valid items
        # etc.
        pass
    
    def print_results(self) -> None:
        """Print validation results to console."""
        if not self.results:
            print("✅ All validation checks passed!")
            return
        
        # Count by level
        errors = [r for r in self.results if r.level == ValidationLevel.ERROR]
        warnings = [r for r in self.results if r.level == ValidationLevel.WARNING]
        infos = [r for r in self.results if r.level == ValidationLevel.INFO]
        
        # Print summary
        print("\n" + "="*60)
        print("DATA VALIDATION REPORT")
        print("="*60)
        print(f"Errors:   {len(errors)}")
        print(f"Warnings: {len(warnings)}")
        print(f"Info:     {len(infos)}")
        print("="*60 + "\n")
        
        # Print errors first
        if errors:
            print("❌ ERRORS:")
            print("-"*40)
            for result in errors:
                self._print_result(result)
        
        # Then warnings
        if warnings:
            print("\n⚠️  WARNINGS:")
            print("-"*40)
            for result in warnings:
                self._print_result(result)
        
        # Then info
        if infos:
            print("\nℹ️  INFO:")
            print("-"*40)
            for result in infos:
                self._print_result(result)
        
        # Final summary
        print("\n" + "="*60)
        if errors:
            print(f"❌ Validation failed with {len(errors)} errors")
        else:
            print("✅ Validation passed (with warnings)" if warnings else "✅ Validation passed")
    
    def _print_result(self, result: ValidationResult) -> None:
        """Print a single validation result."""
        print(f"  [{result.file}] {result.message}")
        if result.details:
            print(f"    Details: {result.details}")
    
    def save_report(self, filepath: Path) -> None:
        """
        Save validation report to file.
        
        Args:
            filepath: Path to save report to
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("DATA VALIDATION REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated: {Path.ctime(Path())}\n")
            f.write("=" * 60 + "\n\n")
            
            # Count by level
            errors = [r for r in self.results if r.level == ValidationLevel.ERROR]
            warnings = [r for r in self.results if r.level == ValidationLevel.WARNING]
            infos = [r for r in self.results if r.level == ValidationLevel.INFO]
            
            f.write(f"Summary:\n")
            f.write(f"  Errors:   {len(errors)}\n")
            f.write(f"  Warnings: {len(warnings)}\n")
            f.write(f"  Info:     {len(infos)}\n")
            f.write("\n")
            
            # Write detailed results
            if errors:
                f.write("ERRORS:\n")
                f.write("-" * 40 + "\n")
                for result in errors:
                    f.write(f"[{result.file}] {result.message}\n")
                    if result.details:
                        f.write(f"  Details: {result.details}\n")
                f.write("\n")
            
            if warnings:
                f.write("WARNINGS:\n")
                f.write("-" * 40 + "\n")
                for result in warnings:
                    f.write(f"[{result.file}] {result.message}\n")
                    if result.details:
                        f.write(f"  Details: {result.details}\n")
                f.write("\n")
            
            if infos:
                f.write("INFO:\n")
                f.write("-" * 40 + "\n")
                for result in infos:
                    f.write(f"[{result.file}] {result.message}\n")
                    if result.details:
                        f.write(f"  Details: {result.details}\n")


def main():
    """Main entry point for data validation tool."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate Untold Story game data files"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=str(DATA_DIR),
        help="Path to data directory"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Save report to file"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only show errors"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    # Run validation
    validator = DataValidator(Path(args.data_dir))
    results = validator.validate_all()
    
    # Filter results if quiet mode
    if args.quiet:
        results = [r for r in results if r.level == ValidationLevel.ERROR]
        validator.results = results
    
    # Output results
    if args.json:
        # JSON output
        import json
        output = {
            "results": [
                {
                    "level": r.level.value,
                    "file": r.file,
                    "message": r.message,
                    "details": r.details
                }
                for r in results
            ],
            "summary": {
                "errors": len([r for r in results if r.level == ValidationLevel.ERROR]),
                "warnings": len([r for r in results if r.level == ValidationLevel.WARNING]),
                "info": len([r for r in results if r.level == ValidationLevel.INFO])
            }
        }
        print(json.dumps(output, indent=2))
    else:
        # Console output
        validator.print_results()
    
    # Save report if requested
    if args.output:
        validator.save_report(Path(args.output))
        print(f"\nReport saved to: {args.output}")
    
    # Exit with error code if errors found
    error_count = len([r for r in results if r.level == ValidationLevel.ERROR])
    sys.exit(1 if error_count > 0 else 0)


if __name__ == "__main__":
    main()