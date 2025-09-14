"""
Performance Monitor Detailed - Consolidated Facade
=================================================
Facade for detailed performance monitoring logic split into specialized modules.
Consolidated from performance_monitor_detailed.py split into 2 modules.
"""

import psutil
import tracemalloc
import time
import gc
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import logging

# Import specialized performance monitoring modules
from .performance_monitor_analysis import PerformanceMonitorAnalysis, AnalysisMetrics
from .performance_monitor_tracking import PerformanceMonitorTracking, TrackingMetrics

logger = logging.getLogger(__name__)


@dataclass
class DetailedMetrics:
    """Detailed performance metrics data class."""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    memory_growth: float = 0.0
    gc_collections: int = 0
    gc_time: float = 0.0
    event_processing_times: Dict[str, List[float]] = field(default_factory=dict)
    battle_phase_times: Dict[str, List[float]] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class PerformanceMonitorDetailed:
    """
    CONSOLIDATED DETAILED PERFORMANCE MONITOR - Facade for detailed performance monitoring.
    Delegates to specialized modules for different aspects of detailed performance monitoring.
    """
    
    def __init__(self, enabled: bool = True):
        """Initialize detailed performance monitor with specialized modules."""
        self.enabled = enabled
        
        # Initialize specialized monitors
        self.analysis = PerformanceMonitorAnalysis(enabled)
        self.tracking = PerformanceMonitorTracking(enabled)
        
        # Compatibility attributes
        self.metrics = self.analysis.metrics
        self.start_time = time.time()
        self.last_cpu_check = time.time()
        self.last_gc_check = time.time()
        
        logger.info(f"PerformanceMonitorDetailed initialized with specialized modules (enabled: {enabled})")
    
    # Analysis methods - delegate to PerformanceMonitorAnalysis
    def record_cpu_usage(self):
        """Record CPU usage - delegates to PerformanceMonitorAnalysis."""
        self.analysis.record_cpu_usage()
    
    def record_memory_growth(self):
        """Record memory growth - delegates to PerformanceMonitorAnalysis."""
        self.analysis.record_memory_growth()
    
    def record_gc_stats(self):
        """Record GC stats - delegates to PerformanceMonitorAnalysis."""
        self.analysis.record_gc_stats()
    
    def analyze_memory_leaks(self) -> Dict[str, Any]:
        """Analyze memory leaks - delegates to PerformanceMonitorAnalysis."""
        return self.analysis.analyze_memory_leaks()
    
    def analyze_cpu_performance(self) -> Dict[str, Any]:
        """Analyze CPU performance - delegates to PerformanceMonitorAnalysis."""
        return self.analysis.analyze_cpu_performance()
    
    def get_analysis_report(self) -> Dict[str, Any]:
        """Get analysis report - delegates to PerformanceMonitorAnalysis."""
        return self.analysis.get_analysis_report()
    
    # Tracking methods - delegate to PerformanceMonitorTracking
    def record_event_processing_time(self, event_type: str, processing_time: float):
        """Record event processing time - delegates to PerformanceMonitorTracking."""
        self.tracking.record_event_processing_time(event_type, processing_time)
    
    def record_battle_phase_time(self, phase: str, phase_time: float):
        """Record battle phase time - delegates to PerformanceMonitorTracking."""
        self.tracking.record_battle_phase_time(phase, phase_time)
    
    def analyze_event_performance(self) -> Dict[str, Any]:
        """Analyze event performance - delegates to PerformanceMonitorTracking."""
        return self.tracking.analyze_event_performance()
    
    def analyze_battle_phase_performance(self) -> Dict[str, Any]:
        """Analyze battle phase performance - delegates to PerformanceMonitorTracking."""
        return self.tracking.analyze_battle_phase_performance()
    
    def get_tracking_report(self) -> Dict[str, Any]:
        """Get tracking report - delegates to PerformanceMonitorTracking."""
        return self.tracking.get_tracking_report()
    
    def get_event_type_statistics(self, event_type: str) -> Dict[str, Any]:
        """Get event type statistics - delegates to PerformanceMonitorTracking."""
        return self.tracking.get_event_type_statistics(event_type)
    
    def get_phase_statistics(self, phase: str) -> Dict[str, Any]:
        """Get phase statistics - delegates to PerformanceMonitorTracking."""
        return self.tracking.get_phase_statistics(phase)
    
    # Combined methods
    def get_detailed_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive detailed performance report."""
        try:
            analysis_report = self.get_analysis_report()
            tracking_report = self.get_tracking_report()
            
            return {
                'analysis': analysis_report,
                'tracking': tracking_report,
                'combined_recommendations': self._get_combined_recommendations()
            }
            
        except Exception as e:
            logger.error(f"Error generating detailed performance report: {e}")
            return {'error': str(e)}
    
    def _get_combined_recommendations(self) -> List[str]:
        """Get combined recommendations from both monitors."""
        try:
            recommendations = []
            
            # Get analysis recommendations
            analysis_recommendations = self.analysis._generate_recommendations()
            recommendations.extend(analysis_recommendations)
            
            # Get tracking recommendations
            tracking_recommendations = self.tracking._generate_tracking_recommendations()
            recommendations.extend(tracking_recommendations)
            
            # Remove duplicates
            return list(set(recommendations))
            
        except Exception as e:
            logger.error(f"Error getting combined recommendations: {e}")
            return [f"Error generating recommendations: {e}"]
    
    def update_all_detailed_metrics(self):
        """Update all detailed performance metrics."""
        try:
            # Update analysis metrics
            self.record_cpu_usage()
            self.record_memory_growth()
            self.record_gc_stats()
            
        except Exception as e:
            logger.error(f"Error updating all detailed metrics: {e}")
    
    def cleanup(self):
        """Cleanup all detailed performance monitor resources."""
        try:
            self.analysis.cleanup()
            self.tracking.cleanup()
            logger.info("All detailed performance monitors cleaned up")
            
        except Exception as e:
            logger.error(f"Error during detailed cleanup: {e}")