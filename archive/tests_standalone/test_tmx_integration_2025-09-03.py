#!/usr/bin/env python3
"""
TMX Integration Test für Untold Story
Testet TMX-Map-Loading und Layer-Rendering mit den optimierten Graphics-Systemen.
"""

import pygame
import sys
from pathlib import Path
from typing import Dict, Any, List

# Füge den Projektpfad hinzu
sys.path.insert(0, str(Path(__file__).parent))

from engine.world.map_loader import MapLoader, MapData
from engine.graphics.sprite_manager import SpriteManager
from engine.graphics.render_manager import RenderManager
from engine.graphics.tile_renderer import TileRenderer
from engine.core.resources import resources

class TMXIntegrationTest:
    """Test für TMX-Map-Integration und Layer-Rendering."""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Untold Story - TMX Integration Test")
        
        # Initialisiere Graphics-Systeme
        self.sprite_manager = SpriteManager()
        self.render_manager = RenderManager()
        self.tile_renderer = TileRenderer(self.sprite_manager)
        
        # Test-Ergebnisse
        self.test_results = {}
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Führt alle TMX-Integration-Tests aus."""
        print("🗺️  TMX INTEGRATION TEST STARTET")
        print("=" * 50)
        
        # Test 1: Map Loading
        self.test_map_loading()
        
        # Test 2: Layer Rendering
        self.test_layer_rendering()
        
        # Test 3: TMX Tileset Integration
        self.test_tmx_tileset_integration()
        
        # Test 4: Performance mit verschiedenen Map-Größen
        self.test_map_performance()
        
        # Test 5: Warp und Trigger Loading
        self.test_warp_trigger_loading()
        
        return self.generate_report()
    
    def test_map_loading(self):
        """Testet das Laden verschiedener Map-Formate."""
        print("\n📊 Test 1: Map Loading")
        print("-" * 30)
        
        # Verfügbare Maps finden
        maps_dir = Path("data/maps")
        json_maps = list(maps_dir.glob("*.json"))
        tmx_maps = list(maps_dir.glob("*.tmx"))
        
        print(f"✅ Gefundene JSON Maps: {len(json_maps)}")
        print(f"✅ Gefundene TMX Maps: {len(tmx_maps)}")
        
        loaded_maps = []
        failed_maps = []
        
        # Teste JSON Maps
        for map_file in json_maps[:5]:  # Teste erste 5
            try:
                map_id = map_file.stem
                map_data = MapLoader.load_map(map_id)
                loaded_maps.append({
                    'id': map_id,
                    'format': 'JSON',
                    'width': map_data.width,
                    'height': map_data.height,
                    'layers': len(map_data.layers),
                    'warps': len(map_data.warps),
                    'triggers': len(map_data.triggers)
                })
                print(f"✅ {map_id}: {map_data.width}x{map_data.height}, {len(map_data.layers)} Layers")
            except Exception as e:
                failed_maps.append({'id': map_id, 'error': str(e)})
                print(f"❌ {map_id}: {e}")
        
        # Teste TMX Maps
        for map_file in tmx_maps[:3]:  # Teste erste 3
            try:
                map_id = map_file.stem
                map_data = MapLoader.load_map(map_id)
                loaded_maps.append({
                    'id': map_id,
                    'format': 'TMX',
                    'width': map_data.width,
                    'height': map_data.height,
                    'layers': len(map_data.layers),
                    'warps': len(map_data.warps),
                    'triggers': len(map_data.triggers)
                })
                print(f"✅ {map_id}: {map_data.width}x{map_data.height}, {len(map_data.layers)} Layers")
            except Exception as e:
                failed_maps.append({'id': map_id, 'error': str(e)})
                print(f"❌ {map_id}: {e}")
        
        self.test_results['map_loading'] = {
            'total_maps_found': len(json_maps) + len(tmx_maps),
            'loaded_maps': loaded_maps,
            'failed_maps': failed_maps,
            'success_rate': len(loaded_maps) / (len(loaded_maps) + len(failed_maps)) * 100 if (len(loaded_maps) + len(failed_maps)) > 0 else 0
        }
    
    def test_layer_rendering(self):
        """Testet Layer-Rendering mit verschiedenen Map-Daten."""
        print("\n📊 Test 2: Layer Rendering")
        print("-" * 30)
        
        # Lade eine Test-Map
        try:
            map_data = MapLoader.load_map("route1")
            
            # Teste Rendering aller Layer
            layer_results = {}
            
            for layer_name, layer_data in map_data.layers.items():
                if not layer_data:
                    continue
                
                # Teste Rendering-Performance
                import time
                start_time = time.time()
                
                # Rendere Layer 10x
                for _ in range(10):
                    self.tile_renderer.render_layer(self.screen, layer_data, (0, 0), layer_name)
                
                render_time = time.time() - start_time
                
                # Zähle Tiles
                tile_count = sum(len(row) for row in layer_data)
                non_empty_tiles = sum(1 for row in layer_data for tile in row if tile and tile != 0)
                
                layer_results[layer_name] = {
                    'render_time_ms': render_time * 1000,
                    'tile_count': tile_count,
                    'non_empty_tiles': non_empty_tiles,
                    'width': len(layer_data[0]) if layer_data else 0,
                    'height': len(layer_data)
                }
                
                print(f"✅ {layer_name}: {render_time*1000:.2f}ms, {non_empty_tiles}/{tile_count} Tiles")
            
            self.test_results['layer_rendering'] = layer_results
            
        except Exception as e:
            print(f"❌ Fehler beim Layer-Rendering-Test: {e}")
            self.test_results['layer_rendering'] = {'error': str(e)}
    
    def test_tmx_tileset_integration(self):
        """Testet TMX-Tileset-Integration."""
        print("\n📊 Test 3: TMX Tileset Integration")
        print("-" * 30)
        
        # Teste Tileset-Loading
        tileset_results = {}
        
        # Lade TMX-Maps und teste Tilesets
        tmx_maps = list(Path("data/maps").glob("*.tmx"))
        
        for map_file in tmx_maps[:3]:
            try:
                map_id = map_file.stem
                
                # Lade Tilesets aus TMX
                self.sprite_manager.load_tmx_tilesets(map_file)
                
                # Zähle geladene Tilesets
                tileset_count = len(self.sprite_manager._loaded_tilesets)
                gid_count = len(self.sprite_manager.gid_to_surface)
                
                tileset_results[map_id] = {
                    'tilesets_loaded': tileset_count,
                    'gid_mappings': gid_count,
                    'success': True
                }
                
                print(f"✅ {map_id}: {tileset_count} Tilesets, {gid_count} GID-Mappings")
                
            except Exception as e:
                tileset_results[map_id] = {
                    'error': str(e),
                    'success': False
                }
                print(f"❌ {map_id}: {e}")
        
        self.test_results['tmx_tileset_integration'] = tileset_results
    
    def test_map_performance(self):
        """Testet Performance mit verschiedenen Map-Größen."""
        print("\n📊 Test 4: Map Performance")
        print("-" * 30)
        
        # Teste verschiedene Map-Größen
        map_sizes = [
            ("Small", 20, 20),
            ("Medium", 50, 50),
            ("Large", 100, 100),
            ("Huge", 200, 200)
        ]
        
        performance_results = {}
        
        for size_name, width, height in map_sizes:
            # Erstelle Test-Layer
            test_layer = []
            for y in range(height):
                row = []
                for x in range(width):
                    # Verschiedene Tile-IDs für Realismus
                    tile_id = (x + y) % 10 + 1
                    row.append(tile_id)
                test_layer.append(row)
            
            # Teste Rendering-Performance
            import time
            
            # Ohne Culling
            self.tile_renderer.use_viewport_culling = False
            start_time = time.time()
            for _ in range(10):
                self.tile_renderer.render_layer(self.screen, test_layer, (0, 0), "test")
            no_cull_time = time.time() - start_time
            
            # Mit Culling
            self.tile_renderer.use_viewport_culling = True
            start_time = time.time()
            for _ in range(10):
                self.tile_renderer.render_layer(self.screen, test_layer, (100, 100), "test")
            cull_time = time.time() - start_time
            
            performance_results[size_name] = {
                'width': width,
                'height': height,
                'total_tiles': width * height,
                'no_cull_time_ms': no_cull_time * 1000,
                'cull_time_ms': cull_time * 1000,
                'culling_speedup': no_cull_time / cull_time if cull_time > 0 else 0
            }
            
            print(f"✅ {size_name} ({width}x{height}): {no_cull_time*1000:.2f}ms → {cull_time*1000:.2f}ms ({no_cull_time/cull_time if cull_time > 0 else 0:.1f}x speedup)")
        
        self.test_results['map_performance'] = performance_results
    
    def test_warp_trigger_loading(self):
        """Testet Warp und Trigger Loading."""
        print("\n📊 Test 5: Warp und Trigger Loading")
        print("-" * 30)
        
        # Teste verschiedene Maps auf Warps und Triggers
        test_maps = ["route1", "kohlenstadt", "museum", "player_house"]
        
        warp_trigger_results = {}
        
        for map_id in test_maps:
            try:
                map_data = MapLoader.load_map(map_id)
                
                warp_trigger_results[map_id] = {
                    'warps': len(map_data.warps),
                    'triggers': len(map_data.triggers),
                    'warp_details': [
                        {
                            'x': warp.x, 'y': warp.y,
                            'to_map': warp.to_map,
                            'to_x': warp.to_x, 'to_y': warp.to_y
                        } for warp in map_data.warps
                    ],
                    'trigger_details': [
                        {
                            'x': trigger.x, 'y': trigger.y,
                            'event': trigger.event
                        } for trigger in map_data.triggers
                    ]
                }
                
                print(f"✅ {map_id}: {len(map_data.warps)} Warps, {len(map_data.triggers)} Triggers")
                
            except Exception as e:
                warp_trigger_results[map_id] = {'error': str(e)}
                print(f"❌ {map_id}: {e}")
        
        self.test_results['warp_trigger_loading'] = warp_trigger_results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generiert einen detaillierten TMX-Integration-Bericht."""
        print("\n" + "=" * 50)
        print("📋 TMX INTEGRATION BERICHT")
        print("=" * 50)
        
        # Bewerte Map Loading
        if 'map_loading' in self.test_results:
            ml = self.test_results['map_loading']
            success_rate = ml['success_rate']
            print(f"🎯 Map Loading Success Rate: {success_rate:.1f}%")
        
        # Bewerte Layer Rendering
        if 'layer_rendering' in self.test_results and 'error' not in self.test_results['layer_rendering']:
            lr = self.test_results['layer_rendering']
            total_render_time = sum(layer['render_time_ms'] for layer in lr.values())
            avg_render_time = total_render_time / len(lr) if lr else 0
            print(f"🎯 Average Layer Render Time: {avg_render_time:.2f}ms")
        
        # Bewerte TMX Tileset Integration
        if 'tmx_tileset_integration' in self.test_results:
            tti = self.test_results['tmx_tileset_integration']
            successful_maps = sum(1 for result in tti.values() if result.get('success', False))
            total_maps = len(tti)
            success_rate = (successful_maps / total_maps * 100) if total_maps > 0 else 0
            print(f"🎯 TMX Tileset Success Rate: {success_rate:.1f}%")
        
        # Bewerte Map Performance
        if 'map_performance' in self.test_results:
            mp = self.test_results['map_performance']
            avg_speedup = sum(result['culling_speedup'] for result in mp.values()) / len(mp)
            print(f"🎯 Average Culling Speedup: {avg_speedup:.1f}x")
        
        # Gesamtbewertung
        total_score = 0
        max_score = 0
        
        if 'map_loading' in self.test_results:
            total_score += self.test_results['map_loading']['success_rate']
            max_score += 100
        
        if 'tmx_tileset_integration' in self.test_results:
            tti = self.test_results['tmx_tileset_integration']
            successful_maps = sum(1 for result in tti.values() if result.get('success', False))
            total_maps = len(tti)
            success_rate = (successful_maps / total_maps * 100) if total_maps > 0 else 0
            total_score += success_rate
            max_score += 100
        
        overall_score = (total_score / max_score * 100) if max_score > 0 else 0
        
        print(f"\n🏆 GESAMTBEWERTUNG: {overall_score:.1f}/100")
        
        if overall_score >= 90:
            print("🌟 AUSGEZEICHNET! TMX-Integration funktioniert perfekt!")
        elif overall_score >= 75:
            print("✅ GUT! TMX-Integration funktioniert gut mit kleineren Verbesserungen.")
        elif overall_score >= 60:
            print("⚠️  BEFRIEDIGEND! TMX-Integration funktioniert, aber braucht Optimierungen.")
        else:
            print("❌ UNGENÜGEND! TMX-Integration braucht erhebliche Verbesserungen.")
        
        # Speichere Bericht
        import json
        import time
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'overall_score': overall_score,
            'test_results': self.test_results
        }
        
        with open('tmx_integration_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Bericht gespeichert: tmx_integration_report.json")
        
        return report

def main():
    """Hauptfunktion für den TMX-Integration-Test."""
    try:
        test = TMXIntegrationTest()
        report = test.run_all_tests()
        
        print("\n🎉 TMX-Integration-Test abgeschlossen!")
        print("Drücke eine beliebige Taste zum Beenden...")
        
        # Warte auf Benutzereingabe
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                    waiting = False
            pygame.time.wait(100)
        
    except Exception as e:
        print(f"❌ Fehler beim TMX-Integration-Test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
