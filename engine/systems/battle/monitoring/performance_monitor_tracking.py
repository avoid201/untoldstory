"""
Performance Monitor Tracking - Event and Phase Tracking
======================================================
Event and phase performance tracking functionality.
Split from performance_monitor_detailed.py to comply with 300-line limit.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import deque
import time

logger = logging.getLogger(__name__)


@dataclass
class TrackingMetrics:
    """Container for tracking performance metrics."""
    event_processing_times: Dict[str, deque] = field(default_factory=dict)
    battle_phase_times: Dict[str, deque] = field(default_factory=dict)
    
    # Tracking thresholds
    MAX_EVENT_PROCESSING_TIME_MS = 10.0
    MAX_PHASE_TIME_MS = 1000.0


class PerformanceMonitorTracking:
    """
    Performance tracking functionality.
    Handles event and phase performance tracking.
    """
    
    def __init__(self, enabled: bool = True):
        """Initialize performance tracking monitor."""
        self.enabled = enabled
        self.metrics = TrackingMetrics()
        self.start_time = time.time()
        
        logger.info(f"PerformanceMonitorTracking initialized (enabled: {enabled})")
    
    def record_event_processing_time(self, event_type: str, processing_time: float):
        """Record event processing time for specific event types."""
        if not self.enabled:
            return
        
        try:
            if event_type not in self.metrics.event_processing_times:
                self.metrics.event_processing_times[event_type] = deque(maxlen=100)
            
            self.metrics.event_processing_times[event_type].append(processing_time)
            
        except Exception as e:
            logger.error(f"Error recording event processing time: {e}")
    
    def record_battle_phase_time(self, phase: str, phase_time: float):
        """Record battle phase processing time."""
        if not self.enabled:
            return
        
        try:
            if phase not in self.metrics.battle_phase_times:
                self.metrics.battle_phase_times[phase] = deque(maxlen=50)
            
            self.metrics.battle_phase_times[phase].append(phase_time)
            
        except Exception as e:
            logger.error(f"Error recording battle phase time: {e}")
    
    def analyze_event_performance(self) -> Dict[str, Any]:
        """Analyze event processing performance."""
        try:
            if not self.metrics.event_processing_times:
                return {'analysis': 'No event data available'}
            
            analysis = {}
            
            for event_type, times in self.metrics.event_processing_times.items():
                if not times:
                    continue
                
                avg_time = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)
                
                analysis[event_type] = {
                    'avg_processing_time_ms': avg_time * 1000,
                    'max_processing_time_ms': max_time * 1000,
                    'min_processing_time_ms': min_time * 1000,
                    'total_events': len(times),
                    'slow_events': sum(1 for t in times if t > 0.01)  # Events taking more than 10ms
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing event performance: {e}")
            return {'error': str(e)}
    
    def analyze_battle_phase_performance(self) -> Dict[str, Any]:
        """Analyze battle phase performance."""
        try:
            if not self.metrics.battle_phase_times:
                return {'analysis': 'No battle phase data available'}
            
            analysis = {}
            
            for phase, times in self.metrics.battle_phase_times.items():
                if not times:
                    continue
                
                avg_time = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)
                
                analysis[phase] = {
                    'avg_duration_ms': avg_time * 1000,
                    'max_duration_ms': max_time * 1000,
                    'min_duration_ms': min_time * 1000,
                    'total_occurrences': len(times)
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing battle phase performance: {e}")
            return {'error': str(e)}
    
    def get_tracking_report(self) -> Dict[str, Any]:
        """Get comprehensive tracking report."""
        try:
            current_time = time.time()
            uptime = current_time - self.start_time
            
            return {
                'uptime_seconds': uptime,
                'event_performance': self.analyze_event_performance(),
                'battle_phase_performance': self.analyze_battle_phase_performance(),
                'tracking_recommendations': self._generate_tracking_recommendations()
            }
            
        except Exception as e:
            logger.error(f"Error generating tracking report: {e}")
            return {'error': str(e)}
    
    def _generate_tracking_recommendations(self) -> List[str]:
        """Generate performance tracking recommendations."""
        recommendations = []
        
        try:
            # Check event performance
            event_analysis = self.analyze_event_performance()
            for event_type, data in event_analysis.items():
                if isinstance(data, dict) and data.get('slow_events', 0) > 0:
                    recommendations.append(f"Slow {event_type} events detected - consider optimizing event processing")
            
            # Check phase performance
            phase_analysis = self.analyze_battle_phase_performance()
            for phase, data in phase_analysis.items():
                if isinstance(data, dict):
                    avg_duration = data.get('avg_duration_ms', 0)
                    if avg_duration > self.metrics.MAX_PHASE_TIME_MS:
                        recommendations.append(f"Slow {phase} phase detected - consider optimizing phase processing")
            
        except Exception as e:
            logger.error(f"Error generating tracking recommendations: {e}")
            recommendations.append(f"Error generating tracking recommendations: {e}")
        
        return recommendations
    
    def get_event_type_statistics(self, event_type: str) -> Dict[str, Any]:
        """Get detailed statistics for a specific event type."""
        try:
            if event_type not in self.metrics.event_processing_times:
                return {'error': f'No data for event type: {event_type}'}
            
            times = self.metrics.event_processing_times[event_type]
            if not times:
                return {'error': f'No data for event type: {event_type}'}
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            return {
                'event_type': event_type,
                'total_events': len(times),
                'avg_processing_time_ms': avg_time * 1000,
                'max_processing_time_ms': max_time * 1000,
                'min_processing_time_ms': min_time * 1000,
                'slow_events': sum(1 for t in times if t > 0.01),
                'fast_events': sum(1 for t in times if t <= 0.001)
            }
            
        except Exception as e:
            logger.error(f"Error getting event type statistics: {e}")
            return {'error': str(e)}
    
    def get_phase_statistics(self, phase: str) -> Dict[str, Any]:
        """Get detailed statistics for a specific battle phase."""
        try:
            if phase not in self.metrics.battle_phase_times:
                return {'error': f'No data for phase: {phase}'}
            
            times = self.metrics.battle_phase_times[phase]
            if not times:
                return {'error': f'No data for phase: {phase}'}
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            return {
                'phase': phase,
                'total_occurrences': len(times),
                'avg_duration_ms': avg_time * 1000,
                'max_duration_ms': max_time * 1000,
                'min_duration_ms': min_time * 1000,
                'slow_occurrences': sum(1 for t in times if t > 1.0),
                'fast_occurrences': sum(1 for t in times if t <= 0.1)
            }
            
        except Exception as e:
            logger.error(f"Error getting phase statistics: {e}")
            return {'error': str(e)}
    
    def cleanup(self):
        """Cleanup performance tracking monitor resources."""
        try:
            # Clear all metrics
            self.metrics.event_processing_times.clear()
            self.metrics.battle_phase_times.clear()
            
            logger.info("Performance tracking monitor cleaned up")
            
        except Exception as e:
            logger.error(f"Error during tracking cleanup: {e}")
