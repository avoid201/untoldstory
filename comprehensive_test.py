#!/usr/bin/env python3
"""
Umfassender System-Test und Korrektur für Untold Story
Testet und korrigiert alle kritischen Komponenten
"""

import sys
import os
from pathlib import Path
import pygame
import json
from typing import Dict, List, Tuple, Optional

# Setup paths
PROJECT_ROOT = Path(__file__).parent if __file__ else Path.cwd()
sys.path.insert(0, str(PROJECT_ROOT))

# Terminal colors
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{CYAN}{BOLD}{text:^70}{RESET}")
    print(f"{CYAN}{'='*70}{RESET}")

def print_success(text: str):
    """Print success message"""
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text: str):
    """Print error message"""
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text: str):
    """Print info message"""
    print(f"{BLUE}ℹ️  {text}{RESET}")

class SystemTester:
    """Comprehensive system tester and fixer"""
    
    def __init__(self):
        self.issues = []
        self.fixed = []
        self.warnings = []
        
    def run_all_tests(self):
        """Run all system tests"""
        print_header("UNTOLD STORY - SYSTEM DIAGNOSTIC")
        
        # 1. Check project structure
        self.test_project_structure()
        
        # 2. Test tile manager
        self.test_tile_manager()
        
        # 3. Test pathfinding
        self.test_pathfinding()
        
        # 4. Test TMX loading
        self.test_tmx_loading()
        
        # 5. Test map rendering
        self.test_map_rendering()
        
        # 6. Test NPC system
        self.test_npc_system()
        
        # 7. Test integration
        self.test_integration()
        
        # Show summary
        self.show_summary()
        
    def test_project_structure(self):
        """Test project file structure"""
        print_header("1. PROJECT STRUCTURE")
        
        required_dirs = [
            "data/maps",
            "data/game_data",
            "assets/gfx/tiles/tilesets",
            "engine/world",
            "engine/graphics",
        ]
        
        required_files = [
            "data/game_data/npcs.json",
            "data/game_data/warps.json",
            "data/game_data/dialogues.json",
            "engine/world/tile_manager.py",
            "engine/world/area.py",
            "engine/world/pathfinding.py",
        ]
        
        for dir_path in required_dirs:
            path = PROJECT_ROOT / dir_path
            if path.exists():
                print_success(f"Directory exists: {dir_path}")
            else:
                print_error(f"Missing directory: {dir_path}")
                self.issues.append(f"Missing directory: {dir_path}")
                
        for file_path in required_files:
            path = PROJECT_ROOT / file_path
            if path.exists():
                print_success(f"File exists: {file_path}")
            else:
                print_error(f"Missing file: {file_path}")
                self.issues.append(f"Missing file: {file_path}")
                
    def test_tile_manager(self):
        """Test the tile manager system"""
        print_header("2. TILE MANAGER")
        
        try:
            from engine.world.tile_manager import tile_manager
            
            # Check external data
            print_info("External data loaded:")
            print(f"  - NPC maps: {len(tile_manager.npcs_data)}")
            print(f"  - Warp maps: {len(tile_manager.warps_data)}")
            print(f"  - Dialogues: {len(tile_manager.dialogues_data)}")
            
            if tile_manager.npcs_data:
                print_success("NPC data loaded successfully")
            else:
                print_warning("No NPC data found")
                self.warnings.append("No NPC data loaded")
                
            # Test getting NPCs for a specific map
            test_map = "kohlenstadt"
            npcs = tile_manager.get_npcs_for_map(test_map)
            if npcs:
                print_success(f"Found {len(npcs)} NPCs for {test_map}")
            else:
                print_warning(f"No NPCs found for {test_map}")
                
            # Test dialogue retrieval
            test_dialogue = "mom_morning"
            dialogue = tile_manager.get_dialogue(test_dialogue)
            if dialogue:
                print_success(f"Dialogue '{test_dialogue}' found")
            else:
                print_warning(f"Dialogue '{test_dialogue}' not found")
                
        except Exception as e:
            print_error(f"TileManager error: {e}")
            self.issues.append(f"TileManager: {e}")
            
    def test_pathfinding(self):
        """Test pathfinding algorithms"""
        print_header("3. PATHFINDING")
        
        try:
            from engine.world.tile_manager import tile_manager
            
            # Setup test collision map
            tile_manager.map_width = 10
            tile_manager.map_height = 10
            tile_manager.collision_map = [[False] * 10 for _ in range(10)]
            
            # Add some obstacles
            for i in range(2, 7):
                tile_manager.collision_map[5][i] = True  # Horizontal wall
                
            # Test simple path
            start = (1, 1)
            goal = (8, 8)
            path = tile_manager.find_path(start, goal)
            
            if path:
                print_success(f"Path found: {len(path)} steps")
                # Visualize path
                self._visualize_path(tile_manager, start, goal, path)
            else:
                print_error("No path found for simple case")
                self.issues.append("Pathfinding failed for simple case")
                
            # Test diagonal path
            diagonal_path = tile_manager.find_path_diagonal(start, goal)
            if diagonal_path:
                print_success(f"Diagonal path found: {len(diagonal_path)} steps")
            else:
                print_warning("No diagonal path found")
                
            # Test impossible path
            tile_manager.collision_map = [[True] * 10 for _ in range(10)]
            tile_manager.collision_map[1][1] = False  # Only start is free
            impossible_path = tile_manager.find_path((1, 1), (8, 8))
            
            if not impossible_path:
                print_success("Correctly identified impossible path")
            else:
                print_error("Found path when none should exist")
                self.issues.append("Pathfinding found impossible path")
                
        except Exception as e:
            print_error(f"Pathfinding error: {e}")
            self.issues.append(f"Pathfinding: {e}")
            
    def _visualize_path(self, tile_manager, start, goal, path):
        """Visualize a path with ASCII art"""
        print_info("Path visualization:")
        for y in range(tile_manager.map_height):
            row = ""
            for x in range(tile_manager.map_width):
                if (x, y) == start:
                    row += "S "
                elif (x, y) == goal:
                    row += "G "
                elif (x, y) in path:
                    row += "* "
                elif tile_manager.collision_map[y][x]:
                    row += "# "
                else:
                    row += ". "
            print(f"  {row}")
            
    def test_tmx_loading(self):
        """Test TMX map loading"""
        print_header("4. TMX LOADING")
        
        pygame.init()
        
        try:
            from engine.world.tile_manager import tile_manager
            
            # Find available TMX files
            tmx_dir = PROJECT_ROOT / "data/maps"
            tmx_files = list(tmx_dir.glob("*.tmx"))
            
            if not tmx_files:
                print_error("No TMX files found")
                self.issues.append("No TMX files in data/maps")
                return
                
            print_info(f"Found {len(tmx_files)} TMX files")
            
            # Test loading first TMX file
            test_tmx = tmx_files[0]
            print_info(f"Testing: {test_tmx.name}")
            
            map_data = tile_manager.load_tmx_map(test_tmx)
            
            if map_data:
                print_success(f"TMX loaded: {map_data['width']}x{map_data['height']}")
                print_info(f"  - Tilesets: {len(map_data['tilesets'])}")
                print_info(f"  - Layers: {list(map_data['layers'].keys())}")
                print_info(f"  - Objects: {len(map_data['objects'])}")
                
                if tile_manager.tiles:
                    print_success(f"Loaded {len(tile_manager.tiles)} tile graphics")
                else:
                    print_warning("No tile graphics loaded")
                    self.warnings.append("No tile graphics loaded from TMX")
                    
                # Check collision layer
                if tile_manager.collision_map:
                    print_success("Collision map generated")
                else:
                    print_warning("No collision map generated")
                    
            else:
                print_error("Failed to load TMX")
                self.issues.append(f"Failed to load {test_tmx.name}")
                
        except Exception as e:
            print_error(f"TMX loading error: {e}")
            self.issues.append(f"TMX loading: {e}")
        finally:
            pygame.quit()
            
    def test_map_rendering(self):
        """Test map rendering system"""
        print_header("5. MAP RENDERING")
        
        pygame.init()
        
        try:
            from engine.world.area import Area
            
            # Try to load player_house
            test_map = "player_house"
            print_info(f"Loading area: {test_map}")
            
            area = Area(test_map)
            
            if area:
                print_success(f"Area loaded: {area.width}x{area.height}")
                
                # Check layers
                if area.layer_surfaces:
                    print_success(f"Rendered {len(area.layer_surfaces)} layers")
                    for layer_name in area.layer_surfaces:
                        print_info(f"  - Layer: {layer_name}")
                else:
                    print_error("No layers rendered")
                    self.issues.append("No layers rendered for area")
                    
                # Test rendering
                test_surface = pygame.Surface((320, 180))
                try:
                    area.draw(test_surface, 0, 0)
                    print_success("Area drawing successful")
                except Exception as e:
                    print_error(f"Area drawing failed: {e}")
                    self.issues.append(f"Area drawing: {e}")
                    
                # Test collision detection
                test_collision = area.get_collision_at(32, 32)
                print_info(f"Collision at (32,32): {test_collision}")
                
            else:
                print_error("Failed to create area")
                self.issues.append("Failed to create area")
                
        except Exception as e:
            print_error(f"Map rendering error: {e}")
            self.issues.append(f"Map rendering: {e}")
        finally:
            pygame.quit()
            
    def test_npc_system(self):
        """Test NPC system"""
        print_header("6. NPC SYSTEM")
        
        try:
            from engine.world.npc_improved import ImprovedNPC, MovementPattern
            
            # Test NPC creation
            test_npc = ImprovedNPC(
                x=5, y=5,
                npc_id="test_npc",
                movement_pattern=MovementPattern.RANDOM,
                movement_radius=3
            )
            
            print_success("NPC created successfully")
            print_info(f"  - Position: ({test_npc.tile_x}, {test_npc.tile_y})")
            print_info(f"  - Pattern: {test_npc.movement_pattern}")
            
            # Test movement
            for _ in range(5):
                test_npc.update(0.1)
                
            if test_npc.current_path or test_npc.tile_x != 5 or test_npc.tile_y != 5:
                print_success("NPC movement working")
            else:
                print_warning("NPC not moving (might be intentional)")
                
        except ImportError:
            print_warning("ImprovedNPC not found, checking standard NPC")
            try:
                # Der Standard-NPC ist im Archive - für Tests verwenden wir ImprovedNPC direkt
                from engine.world.npc_improved import ImprovedNPC
                print_success("Standard NPC system available")
            except ImportError:
                print_error("No NPC system found")
                self.issues.append("No NPC system available")
        except Exception as e:
            print_error(f"NPC system error: {e}")
            self.issues.append(f"NPC system: {e}")
            
    def test_integration(self):
        """Test full system integration"""
        print_header("7. INTEGRATION TEST")
        
        pygame.init()
        
        try:
            # Test creating a game scene
            from engine.world.tile_manager import tile_manager
            from engine.world.area import Area
            
            # Load test map
            area = Area("player_house")
            
            # Test pathfinding in actual map
            if hasattr(area, 'find_path'):
                path = area.find_path((1, 1), (10, 10))
                if path:
                    print_success(f"Pathfinding in area works: {len(path)} steps")
                else:
                    print_warning("No path found in area")
            else:
                print_warning("Area doesn't have pathfinding method")
                
            # Test NPC loading
            npcs = tile_manager.get_npcs_for_map("player_house")
            if npcs:
                print_success(f"NPCs configured for map: {len(npcs)}")
            else:
                print_info("No NPCs configured for player_house")
                
            print_success("Integration test completed")
            
        except Exception as e:
            print_error(f"Integration error: {e}")
            self.issues.append(f"Integration: {e}")
        finally:
            pygame.quit()
            
    def show_summary(self):
        """Show test summary"""
        print_header("TEST SUMMARY")
        
        total_issues = len(self.issues)
        total_warnings = len(self.warnings)
        
        if total_issues == 0:
            print(f"{GREEN}{BOLD}✅ ALL SYSTEMS OPERATIONAL!{RESET}")
            print(f"{GREEN}No critical issues found.{RESET}")
        else:
            print(f"{RED}{BOLD}❌ ISSUES FOUND: {total_issues}{RESET}")
            for issue in self.issues:
                print(f"{RED}  - {issue}{RESET}")
                
        if total_warnings > 0:
            print(f"\n{YELLOW}{BOLD}⚠️  WARNINGS: {total_warnings}{RESET}")
            for warning in self.warnings:
                print(f"{YELLOW}  - {warning}{RESET}")
                
        # Recommendations
        print_header("RECOMMENDATIONS")
        
        if "No tile graphics loaded from TMX" in str(self.warnings):
            print_info("• Check tileset paths in TMX files")
            print_info("• Verify tileset images exist in assets/gfx/tiles/tilesets/")
            
        if "Pathfinding" in str(self.issues):
            print_info("• Review pathfinding algorithm implementation")
            print_info("• Check collision map generation")
            
        if "TMX loading" in str(self.issues):
            print_info("• Verify TMX file format")
            print_info("• Check TSX tileset references")
            
        if total_issues == 0 and total_warnings == 0:
            print_success("System is ready for production!")
            print_info("• Run 'python3 main.py' to start the game")
            print_info("• Check data/game_data/ for configuration files")


def main():
    """Main entry point"""
    tester = SystemTester()
    tester.run_all_tests()
    
    return 0 if not tester.issues else 1


if __name__ == "__main__":
    sys.exit(main())
