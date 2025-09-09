#!/usr/bin/env python3
"""
Comprehensive World Navigation Test für Untold Story
Testet alle World & Scene Systeme: Field Scene, Player Movement, NPCs, Camera, Transitions
"""

import sys
import os
import pygame
import time
import traceback
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.core.game import Game
from engine.scenes.field_scene import FieldScene
from engine.scenes.starter_scene import StarterScene
from engine.world.player import Player
from engine.world.area import Area
from engine.world.npc import NPC, MovementPattern
from engine.world.camera import Camera, CameraConfig
from engine.ui.transitions import TransitionManager, TransitionType
from engine.core.resources import resources


class WorldNavigationTest:
    """Comprehensive test for World Navigation & Scene Management"""
    
    def __init__(self):
        self.game = None
        self.test_results = {}
        self.start_time = time.time()
        
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all world navigation tests"""
        print("🗺️  STARTE COMPREHENSIVE WORLD NAVIGATION TESTS")
        print("=" * 60)
        
        try:
            # Initialize game
            self._test_game_initialization()
            
            # Test Field Scene
            self._test_field_scene()
            
            # Test Player Movement
            self._test_player_movement()
            
            # Test Map System
            self._test_map_system()
            
            # Test NPC System
            self._test_npc_system()
            
            # Test Camera System
            self._test_camera_system()
            
            # Test Scene Transitions
            self._test_scene_transitions()
            
            # Test Story Integration
            self._test_story_integration()
            
            # Performance Tests
            self._test_performance()
            
        except Exception as e:
            print(f"❌ KRITISCHER FEHLER: {e}")
            traceback.print_exc()
            return {"critical_error": False}
        
        finally:
            if self.game:
                self.game.quit()
        
        # Print results
        self._print_test_results()
        return self.test_results
    
    def _test_game_initialization(self):
        """Test game initialization"""
        print("\n🎮 Test 1: Game Initialization")
        try:
            # Create a minimal pygame display for testing
            pygame.display.set_mode((320, 180))
            
            # Create game with proper parameters
            screen = pygame.display.get_surface()
            logical_surface = pygame.Surface((320, 180))
            logical_size = (320, 180)
            window_size = (1280, 720)
            scale_factor = 4.0
            
            self.game = Game(screen, logical_surface, logical_size, window_size, scale_factor)
            self.game.initialize()
            
            # Check required managers
            required_managers = ['resources', 'party_manager', 'story_manager', 'sprite_manager']
            for manager in required_managers:
                if not hasattr(self.game, manager):
                    raise Exception(f"Manager {manager} nicht gefunden")
            
            self.test_results["game_initialization"] = True
            print("✅ Game erfolgreich initialisiert")
            
        except Exception as e:
            self.test_results["game_initialization"] = False
            print(f"❌ Game Initialization fehlgeschlagen: {e}")
    
    def _test_field_scene(self):
        """Test Field Scene functionality"""
        print("\n🗺️  Test 2: Field Scene")
        try:
            # Create Field Scene
            field_scene = FieldScene(self.game)
            
            # Test scene properties
            assert hasattr(field_scene, 'player'), "Player nicht gefunden"
            assert hasattr(field_scene, 'camera'), "Camera nicht gefunden"
            assert hasattr(field_scene, 'current_area'), "Current Area nicht gefunden"
            
            # Test map loading
            field_scene.load_map("player_house")
            assert field_scene.current_area is not None, "Area nicht geladen"
            assert field_scene.map_id == "player_house", "Map ID falsch"
            
            # Test player initialization
            assert field_scene.player is not None, "Player nicht initialisiert"
            assert field_scene.player.name == "Player", "Player Name falsch"
            
            self.test_results["field_scene"] = True
            print("✅ Field Scene funktioniert korrekt")
            
        except Exception as e:
            self.test_results["field_scene"] = False
            print(f"❌ Field Scene Test fehlgeschlagen: {e}")
    
    def _test_player_movement(self):
        """Test Player Movement System"""
        print("\n🎮 Test 3: Player Movement")
        try:
            field_scene = FieldScene(self.game)
            field_scene.load_map("player_house")
            player = field_scene.player
            
            # Test initial position
            initial_x, initial_y = player.get_tile_position()
            assert isinstance(initial_x, int), "Tile X muss int sein"
            assert isinstance(initial_y, int), "Tile Y muss int sein"
            
            # Test movement states
            from engine.world.movement_states import MovementState
            assert player.movement_state == MovementState.IDLE, "Initial state falsch"
            
            # Test tile position setting
            player.set_tile_position(10, 10)
            new_x, new_y = player.get_tile_position()
            assert new_x == 10 and new_y == 10, "Tile Position nicht gesetzt"
            
            # Test movement locking
            player.lock_movement(True)
            assert player.movement_state == MovementState.LOCKED, "Movement nicht gesperrt"
            
            player.lock_movement(False)
            assert player.movement_state == MovementState.IDLE, "Movement nicht entsperrt"
            
            # Test teleport
            player.teleport(100, 100)
            assert player.x == 100 and player.y == 100, "Teleport funktioniert nicht"
            
            self.test_results["player_movement"] = True
            print("✅ Player Movement funktioniert korrekt")
            
        except Exception as e:
            self.test_results["player_movement"] = False
            print(f"❌ Player Movement Test fehlgeschlagen: {e}")
    
    def _test_map_system(self):
        """Test Map System Integration"""
        print("\n🗺️  Test 4: Map System")
        try:
            # Test Area creation
            area = Area("player_house")
            assert area.map_id == "player_house", "Area ID falsch"
            assert area.width > 0, "Area Breite muss > 0 sein"
            assert area.height > 0, "Area Höhe muss > 0 sein"
            
            # Test collision detection
            collision_result = area.get_collision_at(0, 0)
            assert isinstance(collision_result, bool), "Collision muss bool sein"
            
            # Test tile type detection
            tile_type = area.get_tile_type(0, 0)
            assert isinstance(tile_type, int), "Tile Type muss int sein"
            
            # Test performance stats
            stats = area.get_performance_stats()
            assert isinstance(stats, dict), "Performance Stats müssen dict sein"
            assert 'render_time' in stats, "Render Time fehlt"
            assert 'cache_hits' in stats, "Cache Hits fehlen"
            
            self.test_results["map_system"] = True
            print("✅ Map System funktioniert korrekt")
            
        except Exception as e:
            self.test_results["map_system"] = False
            print(f"❌ Map System Test fehlgeschlagen: {e}")
    
    def _test_npc_system(self):
        """Test NPC System with AI Patterns"""
        print("\n👥 Test 5: NPC System")
        try:
            # Test NPC creation
            from engine.world.npc import NPCConfig
            config = NPCConfig(
                name="Test NPC",
                sprite_name="villager_m",
                position=(5, 5),
                dialogue_id="test_dialogue",
                movement_pattern=MovementPattern.STATIC
            )
            
            npc = NPC(config)
            assert npc.name == "Test NPC", "NPC Name falsch"
            assert npc.movement_pattern == MovementPattern.STATIC, "Movement Pattern falsch"
            
            # Test different movement patterns
            patterns = [MovementPattern.STATIC, MovementPattern.RANDOM, 
                       MovementPattern.PATROL, MovementPattern.WANDER,
                       MovementPattern.FOLLOW, MovementPattern.FLEE]
            
            for pattern in patterns:
                npc.movement_pattern = pattern
                assert npc.movement_pattern == pattern, f"Pattern {pattern} nicht gesetzt"
            
            # Test NPC interaction
            player = Player(0, 0)
            can_interact = npc.can_interact_with_player((5, 5))
            assert isinstance(can_interact, bool), "Interaction Check muss bool sein"
            
            self.test_results["npc_system"] = True
            print("✅ NPC System funktioniert korrekt")
            
        except Exception as e:
            self.test_results["npc_system"] = False
            print(f"❌ NPC System Test fehlgeschlagen: {e}")
    
    def _test_camera_system(self):
        """Test Camera System"""
        print("\n📷 Test 6: Camera System")
        try:
            # Test camera creation
            config = CameraConfig()
            camera = Camera(320, 180, 640, 360, config)
            
            assert camera.viewport_width == 320, "Viewport Width falsch"
            assert camera.viewport_height == 180, "Viewport Height falsch"
            
            # Test camera positioning
            camera.set_position(100, 100)
            assert camera.x == 100 and camera.y == 100, "Camera Position nicht gesetzt"
            
            # Test camera centering
            camera.center_on(200, 200)
            expected_x = 200 - 320 // 2
            expected_y = 200 - 180 // 2
            assert camera.x == expected_x and camera.y == expected_y, "Camera Center falsch"
            
            # Test camera shake
            camera.start_shake(5.0, 1.0)
            assert camera.shake_intensity == 5.0, "Shake Intensity nicht gesetzt"
            assert camera.shake_duration == 1.0, "Shake Duration nicht gesetzt"
            
            # Test coordinate conversion
            world_x, world_y = camera.screen_to_world(160, 90)
            assert isinstance(world_x, float), "World X muss float sein"
            assert isinstance(world_y, float), "World Y muss float sein"
            
            self.test_results["camera_system"] = True
            print("✅ Camera System funktioniert korrekt")
            
        except Exception as e:
            self.test_results["camera_system"] = False
            print(f"❌ Camera System Test fehlgeschlagen: {e}")
    
    def _test_scene_transitions(self):
        """Test Scene Transitions"""
        print("\n🔄 Test 7: Scene Transitions")
        try:
            # Test transition creation
            field_scene = FieldScene(self.game)
            starter_scene = StarterScene(self.game)
            
            # Test different transition types
            transitions = [
                TransitionType.FADE,
                TransitionType.WIPE_LEFT,
                TransitionType.RADIAL,
                TransitionType.BATTLE_SWIRL
            ]
            
            for transition_type in transitions:
                transition = TransitionManager.create_transition(
                    transition_type, self.game, field_scene, starter_scene
                )
                assert transition is not None, f"Transition {transition_type} nicht erstellt"
            
            # Test map transition
            map_transition = TransitionManager.create_map_transition(
                self.game, field_scene, starter_scene, "fade"
            )
            assert map_transition is not None, "Map Transition nicht erstellt"
            
            # Test battle transition
            battle_transition = TransitionManager.create_battle_transition(
                self.game, field_scene, starter_scene
            )
            assert battle_transition is not None, "Battle Transition nicht erstellt"
            
            self.test_results["scene_transitions"] = True
            print("✅ Scene Transitions funktionieren korrekt")
            
        except Exception as e:
            self.test_results["scene_transitions"] = False
            print(f"❌ Scene Transitions Test fehlgeschlagen: {e}")
    
    def _test_story_integration(self):
        """Test Story Integration"""
        print("\n📖 Test 8: Story Integration")
        try:
            # Test story manager
            story_manager = self.game.story_manager
            assert story_manager is not None, "Story Manager nicht gefunden"
            
            # Test flag setting
            story_manager.set_flag("test_flag", True)
            flag_value = story_manager.get_flag("test_flag")
            assert flag_value == True, "Flag nicht gesetzt"
            
            # Test story phases
            if hasattr(story_manager, 'current_phase'):
                phase = story_manager.current_phase
                assert isinstance(phase, str), "Phase muss string sein"
            
            # Test quest system
            if hasattr(story_manager, 'active_quests'):
                quests = story_manager.active_quests
                assert isinstance(quests, list), "Quests müssen list sein"
            
            self.test_results["story_integration"] = True
            print("✅ Story Integration funktioniert korrekt")
            
        except Exception as e:
            self.test_results["story_integration"] = False
            print(f"❌ Story Integration Test fehlgeschlagen: {e}")
    
    def _test_performance(self):
        """Test Performance"""
        print("\n⚡ Test 9: Performance")
        try:
            # Test area performance
            area = Area("player_house")
            stats = area.get_performance_stats()
            
            assert stats['render_time'] >= 0, "Render Time muss >= 0 sein"
            assert stats['cache_hits'] >= 0, "Cache Hits müssen >= 0 sein"
            assert stats['cache_misses'] >= 0, "Cache Misses müssen >= 0 sein"
            
            # Test multiple area creation (cache test)
            start_time = time.time()
            for i in range(5):
                test_area = Area("player_house")
            end_time = time.time()
            
            creation_time = end_time - start_time
            assert creation_time < 2.0, f"Area Creation zu langsam: {creation_time:.2f}s"
            
            # Test camera performance
            camera = Camera(320, 180, 640, 360)
            start_time = time.time()
            for i in range(100):
                camera.update(0.016)  # 60 FPS
            end_time = time.time()
            
            update_time = end_time - start_time
            assert update_time < 0.1, f"Camera Update zu langsam: {update_time:.3f}s"
            
            self.test_results["performance"] = True
            print("✅ Performance Tests bestanden")
            
        except Exception as e:
            self.test_results["performance"] = False
            print(f"❌ Performance Test fehlgeschlagen: {e}")
    
    def _print_test_results(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("🗺️  WORLD NAVIGATION TEST RESULTS")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDetailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name}: {status}")
        
        elapsed_time = time.time() - self.start_time
        print(f"\nTotal Test Time: {elapsed_time:.2f} seconds")
        
        if failed_tests == 0:
            print("\n🎉 ALLE TESTS BESTANDEN! World Navigation System ist bereit!")
        else:
            print(f"\n⚠️  {failed_tests} Tests fehlgeschlagen. Überprüfe die Fehler oben.")


def main():
    """Main test function"""
    print("🗺️  UNTOLD STORY - WORLD NAVIGATION COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Initialize pygame
    pygame.init()
    
    try:
        # Run tests
        test_runner = WorldNavigationTest()
        results = test_runner.run_all_tests()
        
        # Exit with appropriate code
        failed_tests = sum(1 for result in results.values() if not result)
        sys.exit(failed_tests)
        
    except KeyboardInterrupt:
        print("\n⚠️  Test durch Benutzer abgebrochen")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {e}")
        traceback.print_exc()
        sys.exit(1)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
