"""
Input Debug Tools für Untold Story
Erweiterte Debug-Funktionen für Keyboard-Input-Analyse
"""

import pygame
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import time
import json


@dataclass
class InputEvent:
    """Einzelner Input-Event mit allen relevanten Informationen"""
    timestamp: float
    frame: int
    event_type: str
    key_code: int
    key_name: str
    action: str
    scene: str
    handled: bool
    processing_time: float


class InputDebugger:
    """Erweiterter Input-Debugger für detaillierte Fehleranalyse"""
    
    def __init__(self):
        self.events: List[InputEvent] = []
        self.max_events = 1000
        self.recording = True
        self.analysis_mode = False
        
        # Performance-Tracking
        self.processing_times: List[float] = []
        self.frame_times: List[float] = []
        
        # Event-Filter
        self.filter_types: set = set()  # Leer = alle Event-Typen
        self.filter_keys: set = set()   # Leer = alle Keys
        
        print("🔍 INPUT DEBUGGER: Erweiterte Debug-Funktionen aktiviert")
        print("🔍 Alle Keyboard-Events werden detailliert aufgezeichnet")
    
    def record_event(self, event_type: str, key_code: int, key_name: str, 
                    action: str, scene: str, handled: bool, processing_time: float = 0.0):
        """Zeichnet einen Input-Event auf"""
        if not self.recording:
            return
        
        # Event erstellen
        event = InputEvent(
            timestamp=time.time(),
            frame=pygame.time.get_ticks() // 16,
            event_type=event_type,
            key_code=key_code,
            key_name=key_name,
            action=action,
            scene=scene,
            handled=handled,
            processing_time=processing_time
        )
        
        self.events.append(event)
        
        # Event-Liste begrenzen
        if len(self.events) > self.max_events:
            self.events.pop(0)
        
        # Performance-Tracking
        if processing_time > 0:
            self.processing_times.append(processing_time)
            if len(self.processing_times) > 100:
                self.processing_times.pop(0)
    
    def set_filter(self, event_types: Optional[set] = None, keys: Optional[set] = None):
        """Setzt Filter für Event-Aufzeichnung"""
        if event_types is not None:
            self.filter_types = event_types
        if keys is not None:
            self.filter_keys = keys
        
        print(f"🔍 INPUT DEBUGGER: Filter gesetzt - Types: {self.filter_types}, Keys: {self.filter_keys}")
    
    def clear_filter(self):
        """Entfernt alle Filter"""
        self.filter_types.clear()
        self.filter_keys.clear()
        print("🔍 INPUT DEBUGGER: Alle Filter entfernt")
    
    def get_filtered_events(self) -> List[InputEvent]:
        """Gibt gefilterte Events zurück"""
        filtered = []
        
        for event in self.events:
            # Event-Typ Filter
            if self.filter_types and event.event_type not in self.filter_types:
                continue
            
            # Key Filter
            if self.filter_keys and event.key_code not in self.filter_keys:
                continue
            
            filtered.append(event)
        
        return filtered
    
    def analyze_input_patterns(self) -> Dict:
        """Analysiert Input-Muster für Fehleranalyse"""
        if not self.events:
            return {"message": "Keine Events zum Analysieren"}
        
        # Gruppierung nach verschiedenen Kriterien
        by_type = {}
        by_key = {}
        by_scene = {}
        by_action = {}
        unhandled_events = []
        slow_events = []
        
        for event in self.events:
            # Nach Event-Typ gruppieren
            if event.event_type not in by_type:
                by_type[event.event_type] = []
            by_type[event.event_type].append(event)
            
            # Nach Taste gruppieren
            if event.key_code not in by_key:
                by_key[event.key_code] = []
            by_key[event.key_code].append(event)
            
            # Nach Scene gruppieren
            if event.scene not in by_scene:
                by_scene[event.scene] = []
            by_scene[event.scene].append(event)
            
            # Nach Aktion gruppieren
            if event.action not in by_action:
                by_action[event.action] = []
            by_action[event.action].append(event)
            
            # Unbehandelte Events
            if not event.handled:
                unhandled_events.append(event)
            
            # Langsame Events (> 16ms = 1 Frame bei 60 FPS)
            if event.processing_time > 0.016:
                slow_events.append(event)
        
        # Statistiken berechnen
        total_events = len(self.events)
        avg_processing_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        
        return {
            'total_events': total_events,
            'event_types': {k: len(v) for k, v in by_type.items()},
            'key_usage': {k: len(v) for k, v in by_key.items()},
            'scene_activity': {k: len(v) for k, v in by_scene.items()},
            'action_distribution': {k: len(v) for k, v in by_action.items()},
            'unhandled_events': len(unhandled_events),
            'slow_events': len(slow_events),
            'avg_processing_time': avg_processing_time,
            'performance_issues': len(slow_events) > 0
        }
    
    def find_unhandled_inputs(self) -> List[InputEvent]:
        """Findet alle unbehandelten Input-Events"""
        return [event for event in self.events if not event.handled]
    
    def find_performance_issues(self, threshold: float = 0.016) -> List[InputEvent]:
        """Findet Events mit Performance-Problemen"""
        return [event for event in self.events if event.processing_time > threshold]
    
    def export_analysis(self, filename: str = "input_analysis.json"):
        """Exportiert die Input-Analyse in eine JSON-Datei"""
        analysis = self.analyze_input_patterns()
        
        # Events für Export vorbereiten
        export_events = []
        for event in self.events[-100:]:  # Nur die letzten 100 Events
            export_events.append({
                'timestamp': event.timestamp,
                'frame': event.frame,
                'event_type': event.event_type,
                'key_code': event.key_code,
                'key_name': event.key_name,
                'action': event.action,
                'scene': event.scene,
                'handled': event.handled,
                'processing_time': event.processing_time
            })
        
        export_data = {
            'analysis': analysis,
            'recent_events': export_events,
            'export_timestamp': time.time(),
            'total_events_recorded': len(self.events)
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            print(f"🔍 INPUT DEBUGGER: Analyse exportiert nach {filename}")
        except Exception as e:
            print(f"🔍 INPUT DEBUGGER: Export fehlgeschlagen: {e}")
    
    def print_detailed_analysis(self):
        """Gibt eine detaillierte Analyse in der Konsole aus"""
        analysis = self.analyze_input_patterns()
        
        if 'message' in analysis:
            print(analysis['message'])
            return
        
        print("\n" + "="*60)
        print("🔍 INPUT DEBUGGER - DETAILLIERTE ANALYSE")
        print("="*60)
        
        print(f"Gesamtanzahl Events: {analysis['total_events']}")
        print(f"Durchschnittliche Verarbeitungszeit: {analysis['avg_processing_time']*1000:.2f}ms")
        print(f"Performance-Probleme: {'JA' if analysis['performance_issues'] else 'NEIN'}")
        
        print(f"\nUnbehandelte Events: {analysis['unhandled_events']}")
        print(f"Langsame Events (>16ms): {analysis['slow_events']}")
        
        print("\nEvent-Typ Verteilung:")
        for event_type, count in analysis['event_types'].items():
            percentage = (count / analysis['total_events']) * 100
            print(f"  {event_type}: {count} ({percentage:.1f}%)")
        
        print("\nHäufigste Tasten:")
        sorted_keys = sorted(analysis['key_usage'].items(), key=lambda x: x[1], reverse=True)
        for key_code, count in sorted_keys[:10]:
            percentage = (count / analysis['total_events']) * 100
            print(f"  Key {key_code}: {count} ({percentage:.1f}%)")
        
        print("\nScene-Aktivität:")
        for scene, count in analysis['scene_activity'].items():
            percentage = (count / analysis['total_events']) * 100
            print(f"  {scene}: {count} ({percentage:.1f}%)")
        
        print("\nAktions-Verteilung:")
        for action, count in analysis['action_distribution'].items():
            percentage = (count / analysis['total_events']) * 100
            print(f"  {action}: {count} ({percentage:.1f}%)")
        
        print("="*60 + "\n")
    
    def clear_events(self):
        """Löscht alle aufgezeichneten Events"""
        self.events.clear()
        self.processing_times.clear()
        print("🔍 INPUT DEBUGGER: Alle Events gelöscht")
    
    def get_recent_events(self, count: int = 20) -> List[InputEvent]:
        """Gibt die letzten N Events zurück"""
        return self.events[-count:] if len(self.events) >= count else self.events
    
    def search_events(self, query: str) -> List[InputEvent]:
        """Sucht Events nach einem Suchbegriff"""
        query = query.lower()
        results = []
        
        for event in self.events:
            if (query in event.event_type.lower() or 
                query in event.key_name.lower() or 
                query in event.action.lower() or 
                query in event.scene.lower()):
                results.append(event)
        
        return results


# Globale Instanz für einfachen Zugriff
input_debugger = InputDebugger()


def get_input_debugger() -> InputDebugger:
    """Gibt die globale Input-Debugger-Instanz zurück"""
    return input_debugger
