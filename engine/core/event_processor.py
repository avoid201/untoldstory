"""
Event Processor für Untold Story
Verarbeitet pygame Events und aktualisiert Input-Status
"""

import pygame
import time
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass


@dataclass
class DebugKeyConfig:
    """Konfiguration für Debug-Hotkeys"""
    tab: int = pygame.K_TAB
    grid: int = pygame.K_g
    f1: int = pygame.K_F1
    f2: int = pygame.K_F2
    f3: int = pygame.K_F3
    f4: int = pygame.K_F4
    f5: int = pygame.K_F5
    f6: int = pygame.K_F6
    f7: int = pygame.K_F7


class EventProcessor:
    """Verarbeitet pygame Events und aktualisiert Input-Status"""
    
    def __init__(self, game: 'Game'):
        self.game = game
        self.debug_keys = DebugKeyConfig()
        self._setup_debug_actions()
    
    def _setup_debug_actions(self) -> None:
        """Richtet Debug-Aktionen ein"""
        self.debug_actions: Dict[int, Callable] = {
            self.debug_keys.tab: self._toggle_debug_overlay,
            self.debug_keys.grid: self._toggle_grid,
            self.debug_keys.f1: self._show_input_summary,
            self.debug_keys.f2: self._clear_input_log,
            self.debug_keys.f3: self._toggle_input_debug,
            self.debug_keys.f4: self._show_current_input_status,
            self.debug_keys.f5: self._export_input_analysis,
            self.debug_keys.f6: self._find_unhandled_inputs,
            self.debug_keys.f7: self._find_performance_issues
        }
    
    def process_events(self) -> None:
        """Hauptmethode für Event-Verarbeitung"""
        # Store previous key state
        prev_keys = self.game.keys_pressed
        self.game.keys_just_pressed.clear()
        self.game.keys_just_released.clear()
        
        # Process events
        for event in pygame.event.get():
            start_time = time.time()
            
            if event.type == pygame.QUIT:
                self.game.quit()
                continue
            
            # Update key state tracking
            if event.type == pygame.KEYDOWN:
                self.game.keys_just_pressed.add(event.key)
                self._handle_debug_hotkeys(event)
                
            elif event.type == pygame.KEYUP:
                self.game.keys_just_released.add(event.key)
            
            # Convert mouse position to logical coordinates
            elif event.type == pygame.MOUSEMOTION:
                self.game.mouse_pos = self._screen_to_logical(event.pos)
            
            # Performance-Tracking für Event-Verarbeitung
            processing_time = time.time() - start_time
            
            # Erweiterten Input-Debugger nutzen
            self._log_input_event(event, processing_time)
            
            # Pass event to active scene
            self._pass_to_scenes(event)
        
        # Update current key state
        self.game.keys_pressed = pygame.key.get_pressed()
        self.game.mouse_buttons = pygame.mouse.get_pressed()
    
    def _handle_debug_hotkeys(self, event: pygame.event.Event) -> None:
        """Behandelt Debug-Hotkeys"""
        if event.key in self.debug_actions:
            self.debug_actions[event.key]()
    
    def _toggle_debug_overlay(self) -> None:
        """Debug-Overlay ein-/ausschalten"""
        self.game.debug_overlay_enabled = not self.game.debug_overlay_enabled
        status = "aktiviert" if self.game.debug_overlay_enabled else "deaktiviert"
        print(f"🔍 DEBUG: Debug-Overlay {status}")
    
    def _toggle_grid(self) -> None:
        """Grid ein-/ausschalten"""
        if self.game.debug_overlay_enabled:
            self.game.show_grid = not self.game.show_grid
            status = "angezeigt" if self.game.show_grid else "versteckt"
            print(f"🔍 DEBUG: Grid {status}")
    
    def _show_input_summary(self) -> None:
        """Input-Log Zusammenfassung anzeigen"""
        if hasattr(self.game, 'input_manager'):
            self.game.input_manager.print_input_log_summary()
        
        # Erweiterte Analyse
        if hasattr(self.game, 'input_debugger') and self.game.input_debugger:
            self.game.input_debugger.print_detailed_analysis()
    
    def _clear_input_log(self) -> None:
        """Input-Log löschen"""
        if hasattr(self.game, 'input_manager'):
            self.game.input_manager.clear_input_log()
        if hasattr(self.game, 'input_debugger') and self.game.input_debugger:
            self.game.input_debugger.clear_events()
    
    def _toggle_input_debug(self) -> None:
        """Input-Debug ein/ausschalten"""
        if hasattr(self.game, 'input_manager'):
            self.game.input_manager.debug_enabled = not self.game.input_manager.debug_enabled
            status = "aktiviert" if self.game.input_manager.debug_enabled else "deaktiviert"
            print(f"🔍 INPUT DEBUG: Vollständiger Debug {status}")
    
    def _show_current_input_status(self) -> None:
        """Aktuelle Input-Status anzeigen"""
        if hasattr(self.game, 'input_manager'):
            debug_info = self.game.input_manager.get_input_debug_info()
            print("\n🔍 AKTUELLER INPUT-STATUS:")
            print(f"  Gedrückte Tasten: {debug_info['pressed_keys']}")
            print(f"  Gerade gedrückt: {debug_info['just_pressed']}")
            print(f"  Gerade losgelassen: {debug_info['just_released']}")
            print(f"  Gebufferte Inputs: {debug_info['buffered_inputs']}")
            print(f"  Combo-Buffer: {debug_info['combo_buffer']}")
            print(f"  Repeat-Timer: {debug_info['repeat_timers']}")
    
    def _export_input_analysis(self) -> None:
        """Erweiterte Input-Analyse exportieren"""
        if hasattr(self.game, 'input_debugger') and self.game.input_debugger:
            self.game.input_debugger.export_analysis()
    
    def _find_unhandled_inputs(self) -> None:
        """Unbehandelte Inputs finden"""
        if hasattr(self.game, 'input_debugger') and self.game.input_debugger:
            unhandled = self.game.input_debugger.find_unhandled_inputs()
            print(f"\n🔍 UNBEHANDELTE INPUTS: {len(unhandled)} gefunden")
            for event in unhandled[-10:]:  # Letzte 10
                print(f"  Frame {event.frame}: {event.event_type} {event.key_name} -> {event.action}")
    
    def _find_performance_issues(self) -> None:
        """Performance-Probleme finden"""
        if hasattr(self.game, 'input_debugger') and self.game.input_debugger:
            slow_events = self.game.input_debugger.find_performance_issues()
            print(f"\n🔍 PERFORMANCE-PROBLEME: {len(slow_events)} Events > 16ms")
            for event in slow_events[-5:]:  # Letzte 5
                print(f"  Frame {event.frame}: {event.event_type} {event.key_name} - {event.processing_time*1000:.2f}ms")
    
    def _log_input_event(self, event: pygame.event.Event, processing_time: float) -> None:
        """Loggt Input-Events für Debug-Zwecke"""
        if not hasattr(self.game, 'input_debugger') or not self.game.input_debugger:
            return
        
        if event.type not in [pygame.KEYDOWN, pygame.KEYUP]:
            return
        
        # Aktuelle Scene ermitteln
        current_scene = self.game.scene_stack[-1].__class__.__name__ if self.game.scene_stack else "None"
        
        # Key-Name ermitteln
        key_name = "UNKNOWN"
        if hasattr(self.game, 'input_manager') and hasattr(self.game.input_manager, '_get_key_name'):
            key_name = self.game.input_manager._get_key_name(event.key)
        
        # Aktion ermitteln
        action = "UNKNOWN"
        if hasattr(self.game, 'input_manager') and hasattr(self.game.input_manager, '_check_action_for_key'):
            action = self.game.input_manager._check_action_for_key(event.key)
        
        # Event aufzeichnen
        self.game.input_debugger.record_event(
            event_type="KEYDOWN" if event.type == pygame.KEYDOWN else "KEYUP",
            key_code=event.key,
            key_name=key_name,
            action=action,
            scene=current_scene,
            handled=False,  # Wird später aktualisiert
            processing_time=processing_time
        )
    
    def _pass_to_scenes(self, event: pygame.event.Event) -> None:
        """Gibt Events an aktive Scenes weiter"""
        scene_handled = False
        if self.game.scene_stack:
            # Process from top to bottom until handled
            for scene in reversed(self.game.scene_stack):
                if scene.is_active and scene.handle_event(event):
                    scene_handled = True
                    break
        
        # Event als behandelt markieren wenn Scene es verarbeitet hat
        if hasattr(self.game, 'input_debugger') and self.game.input_debugger and event.type in [pygame.KEYDOWN, pygame.KEYUP]:
            # Letzten Event als behandelt markieren
            if self.game.input_debugger.events:
                self.game.input_debugger.events[-1].handled = scene_handled
    
    def _screen_to_logical(self, screen_pos: tuple[int, int]) -> tuple[int, int]:
        """
        Convert screen coordinates to logical coordinates.
        
        Args:
            screen_pos: Position in screen/window coordinates
            
        Returns:
            Position in logical coordinates
        """
        window_w, window_h = self.game.screen.get_size()
        logical_w, logical_h = self.game.logical_size
        
        scale_x = window_w / logical_w
        scale_y = window_h / logical_h
        scale = min(scale_x, scale_y)
        int_scale = max(1, int(scale))
        
        dest_w = logical_w * int_scale
        dest_h = logical_h * int_scale
        dest_x = (window_w - dest_w) // 2
        dest_y = (window_h - dest_h) // 2
        
        # Convert to logical coordinates
        logical_x = (screen_pos[0] - dest_x) // int_scale
        logical_y = (screen_pos[1] - dest_y) // int_scale
        
        # Clamp to logical bounds
        logical_x = max(0, min(logical_w - 1, logical_x))
        logical_y = max(0, min(logical_h - 1, logical_y))
        
        return (logical_x, logical_y)
