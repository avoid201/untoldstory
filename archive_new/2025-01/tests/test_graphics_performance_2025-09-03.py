#!/usr/bin/env python3
"""
Graphics Performance Test für Untold Story
Testet alle optimierten Graphics-Systeme und gibt detaillierte Performance-Berichte aus.
"""

import pygame
import time
import sys
from pathlib import Path
from typing import Dict, Any, List
import json

# Füge den Projektpfad hinzu
sys.path.insert(0, str(Path(__file__).parent))

from engine.graphics.sprite_manager import SpriteManager
from engine.graphics.render_manager import RenderManager
from engine.graphics.tile_renderer import TileRenderer
from engine.core.resources import resources
from engine.graphics.optimized_renderer import OptimizedRenderer

class GraphicsPerformanceTest:
    """Umfassender Performance-Test für alle Graphics-Systeme."""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Untold Story - Graphics Performance Test")
        
        # Test-Ergebnisse
        self.test_results = {}
        
        # Performance-Tracking
        self.clock = pygame.time.Clock()
        self.fps_history = []
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Führt alle Performance-Tests aus."""
        print("🎨 GRAPHICS PERFORMANCE TEST STARTET")
        print("=" * 50)
        
        # Test 1: SpriteManager Performance
        self.test_sprite_manager()
        
        # Test 2: Resources Performance
        self.test_resources()
        
        # Test 3: TileRenderer Performance
        self.test_tile_renderer()
        
        # Test 4: RenderManager Performance
        self.test_render_manager()
        
        # Test 5: OptimizedRenderer Performance
        self.test_optimized_renderer()
        
        # Test 6: Monster-Sprite Loading
        self.test_monster_sprite_loading()
        
        # Test 7: Asset Validation
        self.test_asset_validation()
        
        # Test 8: Memory Usage
        self.test_memory_usage()
        
        # Test 9: FPS Performance
        self.test_fps_performance()
        
        # Generiere Bericht
        return self.generate_report()
    
    def test_sprite_manager(self):
        """Testet SpriteManager Performance."""
        print("\n📊 Test 1: SpriteManager Performance")
        print("-" * 30)
        
        start_time = time.time()
        
        # Initialisiere SpriteManager
        sprite_manager = SpriteManager()
        
        # Teste Lazy Loading
        load_start = time.time()
        sprite_manager._ensure_loaded()
        load_time = time.time() - load_start
        
        # Teste Sprite-Zugriff
        access_start = time.time()
        for i in range(100):
            sprite_manager.get_monster_sprite(str(i % 151 + 1))
            sprite_manager.get_player_sprite("down")
            sprite_manager.get_tile("grass")
        access_time = time.time() - access_start
        
        # Hole Performance-Statistiken
        stats = sprite_manager.get_performance_stats()
        
        self.test_results['sprite_manager'] = {
            'load_time_ms': load_time * 1000,
            'access_time_ms': access_time * 1000,
            'total_sprites': stats['total_sprites'],
            'memory_usage_mb': stats['memory_usage_mb'],
            'cache_hit_rate': stats['cache_hit_rate'],
            'monster_sprites': stats['monster_sprites'],
            'tile_sprites': stats['tile_sprites'],
            'object_sprites': stats['object_sprites'],
            'npc_sprites': stats['npc_sprites'],
            'player_sprites': stats['player_sprites']
        }
        
        print(f"✅ Load Time: {load_time*1000:.2f}ms")
        print(f"✅ Access Time (100x): {access_time*1000:.2f}ms")
        print(f"✅ Total Sprites: {stats['total_sprites']}")
        print(f"✅ Memory Usage: {stats['memory_usage_mb']:.2f}MB")
        print(f"✅ Cache Hit Rate: {stats['cache_hit_rate']*100:.1f}%")
    
    def test_resources(self):
        """Testet Resources Performance."""
        print("\n📊 Test 2: Resources Performance")
        print("-" * 30)
        
        start_time = time.time()
        
        # Teste Asset-Loading
        load_start = time.time()
        for i in range(1, 21):  # Erste 20 Monster
            resources.load_monster_sprite(i, (56, 56), True)
        load_time = time.time() - load_start
        
        # Teste Cache-Performance
        cache_start = time.time()
        for i in range(1, 21):
            resources.load_monster_sprite(i, (56, 56), True)  # Sollte aus Cache kommen
        cache_time = time.time() - cache_start
        
        # Hole Cache-Statistiken
        cache_stats = resources.get_cache_stats()
        monster_stats = resources.get_monster_sprite_cache_stats()
        
        self.test_results['resources'] = {
            'load_time_ms': load_time * 1000,
            'cache_time_ms': cache_time * 1000,
            'cache_speedup': load_time / cache_time if cache_time > 0 else 0,
            'image_cache_size': cache_stats['counts']['images'],
            'monster_cache_size': monster_stats['cached_sprites'],
            'monster_memory_mb': monster_stats['total_memory_mb']
        }
        
        print(f"✅ Load Time (20 Monster): {load_time*1000:.2f}ms")
        print(f"✅ Cache Time (20 Monster): {cache_time*1000:.2f}ms")
        print(f"✅ Cache Speedup: {load_time/cache_time if cache_time > 0 else 0:.1f}x")
        print(f"✅ Image Cache Size: {cache_stats['counts']['images']}")
        print(f"✅ Monster Cache Size: {monster_stats['cached_sprites']}")
    
    def test_tile_renderer(self):
        """Testet TileRenderer Performance."""
        print("\n📊 Test 3: TileRenderer Performance")
        print("-" * 30)
        
        # Erstelle Test-Layer
        test_layer = []
        for y in range(50):  # 50x50 Tiles
            row = []
            for x in range(50):
                row.append((x + y) % 10 + 1)  # Verschiedene Tile-IDs
            test_layer.append(row)
        
        # Initialisiere TileRenderer
        sprite_manager = SpriteManager()
        tile_renderer = TileRenderer(sprite_manager)
        
        # Teste Rendering-Performance
        render_start = time.time()
        for _ in range(10):  # 10 Frames
            tile_renderer.render_layer(self.screen, test_layer, (0, 0), "test")
        render_time = time.time() - render_start
        
        # Teste mit Culling
        tile_renderer.use_viewport_culling = True
        cull_start = time.time()
        for _ in range(10):
            tile_renderer.render_layer(self.screen, test_layer, (100, 100), "test")
        cull_time = time.time() - cull_start
        
        # Hole Performance-Statistiken
        stats = tile_renderer.get_performance_stats()
        
        self.test_results['tile_renderer'] = {
            'render_time_ms': render_time * 1000,
            'cull_time_ms': cull_time * 1000,
            'culling_efficiency': stats['culling_efficiency_percent'],
            'cache_hit_rate': stats['cache_hit_rate_percent'],
            'tiles_rendered': stats['tiles_rendered'],
            'tiles_culled': stats['tiles_culled']
        }
        
        print(f"✅ Render Time (10 frames): {render_time*1000:.2f}ms")
        print(f"✅ Cull Time (10 frames): {cull_time*1000:.2f}ms")
        print(f"✅ Culling Efficiency: {stats['culling_efficiency_percent']:.1f}%")
        print(f"✅ Cache Hit Rate: {stats['cache_hit_rate_percent']:.1f}%")
    
    def test_render_manager(self):
        """Testet RenderManager Performance."""
        print("\n📊 Test 4: RenderManager Performance")
        print("-" * 30)
        
        # Initialisiere RenderManager
        render_manager = RenderManager()
        
        # Teste verschiedene Performance-Modi
        modes = [60, 30, 15]  # FPS-Ziele
        mode_results = {}
        
        for target_fps in modes:
            render_manager.optimize_for_performance(target_fps)
            
            # Simuliere Rendering
            start_time = time.time()
            for _ in range(60):  # 1 Sekunde bei 60fps
                render_manager.update_performance_stats()
            end_time = time.time()
            
            stats = render_manager.get_performance_stats()
            mode_results[f'fps_{target_fps}'] = {
                'frames_rendered': stats['frames_rendered'],
                'culling_enabled': stats['culling_enabled'],
                'batch_rendering_enabled': stats['batch_rendering_enabled'],
                'entity_culling_enabled': stats['entity_culling_enabled']
            }
        
        self.test_results['render_manager'] = mode_results
        
        print(f"✅ Performance-Modi getestet: {list(mode_results.keys())}")
        print(f"✅ Culling: {mode_results['fps_60']['culling_enabled']}")
        print(f"✅ Batch Rendering: {mode_results['fps_60']['batch_rendering_enabled']}")
        print(f"✅ Entity Culling: {mode_results['fps_60']['entity_culling_enabled']}")
    
    def test_optimized_renderer(self):
        """Testet OptimizedRenderer Performance."""
        print("\n📊 Test 5: OptimizedRenderer Performance")
        print("-" * 30)
        
        # Initialisiere OptimizedRenderer
        optimized_renderer = OptimizedRenderer()
        
        # Teste Texture-Atlas
        atlas_start = time.time()
        for i in range(50):
            # Erstelle Test-Surface
            test_surface = pygame.Surface((32, 32))
            test_surface.fill((i * 5, i * 5, i * 5))
            optimized_renderer.add_to_atlas(f"test_{i}", test_surface)
        atlas_time = time.time() - atlas_start
        
        # Teste Font-Caching
        font_start = time.time()
        for i in range(100):
            optimized_renderer.render_text(f"Test {i}", "None", 16, (255, 255, 255))
        font_time = time.time() - font_start
        
        # Hole Statistiken
        stats = optimized_renderer.get_stats()
        
        self.test_results['optimized_renderer'] = {
            'atlas_time_ms': atlas_time * 1000,
            'font_time_ms': font_time * 1000,
            'atlas_usage': stats['atlas_usage'],
            'font_cache_size': stats['font_cache_size'],
            'surface_cache_size': stats['surface_cache_size']
        }
        
        print(f"✅ Atlas Time (50 textures): {atlas_time*1000:.2f}ms")
        print(f"✅ Font Time (100 texts): {font_time*1000:.2f}ms")
        print(f"✅ Atlas Usage: {stats['atlas_usage']:.1f}%")
        print(f"✅ Font Cache Size: {stats['font_cache_size']}")
    
    def test_monster_sprite_loading(self):
        """Testet Monster-Sprite Loading (1-151.png)."""
        print("\n📊 Test 6: Monster-Sprite Loading (1-151.png)")
        print("-" * 30)
        
        # Teste Loading aller Monster-Sprites
        start_time = time.time()
        loaded_count = 0
        missing_count = 0
        error_count = 0
        
        for i in range(1, 152):  # 1-151
            try:
                sprite = resources.load_monster_sprite(i, (56, 56), True)
                if sprite:
                    loaded_count += 1
                else:
                    missing_count += 1
            except Exception as e:
                error_count += 1
                print(f"⚠️  Fehler bei Monster {i}: {e}")
        
        load_time = time.time() - start_time
        
        # Teste verschiedene Größen
        size_test_start = time.time()
        for size in [(32, 32), (48, 48), (64, 64), (80, 80)]:
            for i in range(1, 21):  # Erste 20 Monster
                resources.load_monster_sprite(i, size, True)
        size_test_time = time.time() - size_test_start
        
        self.test_results['monster_sprites'] = {
            'total_monsters': 151,
            'loaded_count': loaded_count,
            'missing_count': missing_count,
            'error_count': error_count,
            'load_time_ms': load_time * 1000,
            'size_test_time_ms': size_test_time * 1000,
            'success_rate': (loaded_count / 151) * 100
        }
        
        print(f"✅ Loaded: {loaded_count}/151 ({loaded_count/151*100:.1f}%)")
        print(f"✅ Missing: {missing_count}")
        print(f"✅ Errors: {error_count}")
        print(f"✅ Load Time: {load_time*1000:.2f}ms")
        print(f"✅ Size Test Time: {size_test_time*1000:.2f}ms")
    
    def test_asset_validation(self):
        """Testet Asset-Validation."""
        print("\n📊 Test 7: Asset Validation")
        print("-" * 30)
        
        # Validiere Assets
        validation_report = resources.validate_assets()
        
        self.test_results['asset_validation'] = validation_report
        
        print(f"✅ Total Checked: {validation_report['total_checked']}")
        print(f"✅ Valid Assets: {validation_report['valid_assets']}")
        print(f"✅ Missing Assets: {len(validation_report['missing_assets'])}")
        print(f"✅ Corrupt Assets: {len(validation_report['corrupt_assets'])}")
        
        if validation_report['missing_assets']:
            print("⚠️  Missing Assets (first 10):")
            for asset in validation_report['missing_assets'][:10]:
                print(f"   - {asset}")
        
        if validation_report['corrupt_assets']:
            print("⚠️  Corrupt Assets (first 10):")
            for asset in validation_report['corrupt_assets'][:10]:
                print(f"   - {asset}")
    
    def test_memory_usage(self):
        """Testet Memory-Usage."""
        print("\n📊 Test 8: Memory Usage")
        print("-" * 30)
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Memory vor Tests
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Lade viele Assets
        for i in range(1, 51):
            resources.load_monster_sprite(i, (56, 56), True)
        
        # Memory nach Tests
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before
        
        # Cache-Statistiken
        cache_stats = resources.get_cache_stats()
        
        self.test_results['memory_usage'] = {
            'memory_before_mb': memory_before,
            'memory_after_mb': memory_after,
            'memory_increase_mb': memory_increase,
            'image_cache_memory_mb': cache_stats['sizes']['images'],
            'monster_cache_memory_mb': cache_stats['sizes']['monster_sprites']
        }
        
        print(f"✅ Memory Before: {memory_before:.2f}MB")
        print(f"✅ Memory After: {memory_after:.2f}MB")
        print(f"✅ Memory Increase: {memory_increase:.2f}MB")
        print(f"✅ Image Cache Memory: {cache_stats['sizes']['images']:.2f}MB")
        print(f"✅ Monster Cache Memory: {cache_stats['sizes']['monster_sprites']:.2f}MB")
    
    def test_fps_performance(self):
        """Testet FPS-Performance."""
        print("\n📊 Test 9: FPS Performance")
        print("-" * 30)
        
        # Teste verschiedene Szenarien
        scenarios = [
            ("Empty Scene", 0),
            ("Light Scene", 10),
            ("Medium Scene", 50),
            ("Heavy Scene", 100)
        ]
        
        scenario_results = {}
        
        for scenario_name, entity_count in scenarios:
            fps_values = []
            
            # Teste 5 Sekunden
            start_time = time.time()
            frame_count = 0
            
            while time.time() - start_time < 5.0:
                # Simuliere Rendering
                self.screen.fill((0, 0, 0))
                
                # Simuliere Entities
                for i in range(entity_count):
                    pygame.draw.rect(self.screen, (255, 0, 0), (i * 10, i * 10, 16, 16))
                
                pygame.display.flip()
                frame_count += 1
                
                # Messe FPS
                fps = self.clock.get_fps()
                if fps > 0:
                    fps_values.append(fps)
            
            avg_fps = sum(fps_values) / len(fps_values) if fps_values else 0
            min_fps = min(fps_values) if fps_values else 0
            max_fps = max(fps_values) if fps_values else 0
            
            scenario_results[scenario_name] = {
                'avg_fps': avg_fps,
                'min_fps': min_fps,
                'max_fps': max_fps,
                'frame_count': frame_count,
                'entity_count': entity_count
            }
        
        self.test_results['fps_performance'] = scenario_results
        
        for scenario, results in scenario_results.items():
            print(f"✅ {scenario}: {results['avg_fps']:.1f} FPS (min: {results['min_fps']:.1f}, max: {results['max_fps']:.1f})")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generiert einen detaillierten Performance-Bericht."""
        print("\n" + "=" * 50)
        print("📋 PERFORMANCE-BERICHT")
        print("=" * 50)
        
        # Gesamtbewertung
        total_score = 0
        max_score = 0
        
        # Bewerte SpriteManager
        if 'sprite_manager' in self.test_results:
            sm = self.test_results['sprite_manager']
            score = min(100, (sm['cache_hit_rate'] * 100) + (sm['total_sprites'] / 10))
            total_score += score
            max_score += 100
            print(f"🎯 SpriteManager Score: {score:.1f}/100")
        
        # Bewerte Resources
        if 'resources' in self.test_results:
            res = self.test_results['resources']
            score = min(100, res['cache_speedup'] * 20)
            total_score += score
            max_score += 100
            print(f"🎯 Resources Score: {score:.1f}/100")
        
        # Bewerte Monster-Sprites
        if 'monster_sprites' in self.test_results:
            ms = self.test_results['monster_sprites']
            score = ms['success_rate']
            total_score += score
            max_score += 100
            print(f"🎯 Monster Sprites Score: {score:.1f}/100")
        
        # Gesamtbewertung
        overall_score = (total_score / max_score * 100) if max_score > 0 else 0
        
        print(f"\n🏆 GESAMTBEWERTUNG: {overall_score:.1f}/100")
        
        if overall_score >= 90:
            print("🌟 AUSGEZEICHNET! Graphics-System ist optimal optimiert!")
        elif overall_score >= 75:
            print("✅ GUT! Graphics-System funktioniert gut mit kleineren Optimierungen.")
        elif overall_score >= 60:
            print("⚠️  BEFRIEDIGEND! Graphics-System funktioniert, aber braucht Optimierungen.")
        else:
            print("❌ UNGENÜGEND! Graphics-System braucht erhebliche Optimierungen.")
        
        # Speichere Bericht
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'overall_score': overall_score,
            'test_results': self.test_results,
            'recommendations': self.generate_recommendations()
        }
        
        # Speichere als JSON
        with open('graphics_performance_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Bericht gespeichert: graphics_performance_report.json")
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Generiert Optimierungsempfehlungen."""
        recommendations = []
        
        # SpriteManager Empfehlungen
        if 'sprite_manager' in self.test_results:
            sm = self.test_results['sprite_manager']
            if sm['cache_hit_rate'] < 0.8:
                recommendations.append("SpriteManager: Cache-Hit-Rate verbessern durch Preloading")
            if sm['memory_usage_mb'] > 100:
                recommendations.append("SpriteManager: Memory-Usage reduzieren durch besseres Cache-Management")
        
        # Resources Empfehlungen
        if 'resources' in self.test_results:
            res = self.test_results['resources']
            if res['cache_speedup'] < 5:
                recommendations.append("Resources: Cache-Performance verbessern")
        
        # Monster-Sprites Empfehlungen
        if 'monster_sprites' in self.test_results:
            ms = self.test_results['monster_sprites']
            if ms['success_rate'] < 95:
                recommendations.append("Monster-Sprites: Fehlende Sprites ergänzen")
        
        # FPS Empfehlungen
        if 'fps_performance' in self.test_results:
            fps = self.test_results['fps_performance']
            if fps['Heavy Scene']['avg_fps'] < 30:
                recommendations.append("FPS: Performance bei schweren Szenen verbessern")
        
        return recommendations

def main():
    """Hauptfunktion für den Performance-Test."""
    try:
        test = GraphicsPerformanceTest()
        report = test.run_all_tests()
        
        print("\n🎉 Performance-Test abgeschlossen!")
        print("Drücke eine beliebige Taste zum Beenden...")
        
        # Warte auf Benutzereingabe
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                    waiting = False
            pygame.time.wait(100)
        
    except Exception as e:
        print(f"❌ Fehler beim Performance-Test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
