"""
Battle Performance Monitor - Consolidated Facade
===============================================
Facade for all performance monitoring logic split into specialized modules.
Consolidated from performance_monitor.py split into 2 modules.
"""

import psutil
import tracemalloc
import time
import gc
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import deque
import logging

# Import specialized performance monitoring modules
from .monitoring.performance_monitor_core import PerformanceMonitorCore, PerformanceMetrics
from .monitoring.performance_monitor_detailed import PerformanceMonitorDetailed, DetailedMetrics

logger = logging.getLogger(__name__)


class BattlePerformanceMonitor:
    """
    CONSOLIDATED BATTLE PERFORMANCE MONITOR - Facade for all performance monitoring.
    Delegates to specialized modules for different aspects of performance monitoring.
    """
    
    def __init__(self, enabled: bool = True):
        """Initialize performance monitor with specialized modules."""
        self.enabled = enabled
        
        # Initialize specialized monitors
        self.core = PerformanceMonitorCore(enabled)
        self.detailed = PerformanceMonitorDetailed(enabled)
        
        # Compatibility attributes
        self.metrics = self.core.metrics
        self.start_time = time.time()
        self.last_memory_check = time.time()
        self.memory_traced = False
        
        logger.info(f"BattlePerformanceMonitor initialized with specialized modules (enabled: {enabled})")
    
    # Core performance monitoring methods - delegate to PerformanceMonitorCore
    def record_frame_time(self, frame_time: float):
        """Record frame processing time - delegates to PerformanceMonitorCore."""
        self.core.record_frame_time(frame_time)
    
    def record_turn_time(self, turn_time: float):
        """Record turn processing time - delegates to PerformanceMonitorCore."""
        self.core.record_turn_time(turn_time)
    
    def record_damage_calculation(self, calc_time: float):
        """Record damage calculation time - delegates to PerformanceMonitorCore."""
        self.core.record_damage_calculation(calc_time)
    
    def record_event(self, event_type: str):
        """Record event occurrence - delegates to PerformanceMonitorCore."""
        self.core.record_event(event_type)
    
    def get_current_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage - delegates to PerformanceMonitorCore."""
        return self.core.get_current_memory_usage()
    
    def take_memory_snapshot(self):
        """Take memory snapshot - delegates to PerformanceMonitorCore."""
        self.core.take_memory_snapshot()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary - delegates to PerformanceMonitorCore."""
        return self.core.get_performance_summary()
    
    def _detect_performance_issues(self) -> List[str]:
        """Detect performance issues - delegates to PerformanceMonitorCore."""
        return self.core._detect_performance_issues()
    
    # Detailed performance monitoring methods - delegate to PerformanceMonitorDetailed
    def record_cpu_usage(self):
        """Record CPU usage - delegates to PerformanceMonitorDetailed."""
        self.detailed.record_cpu_usage()
    
    def record_memory_growth(self):
        """Record memory growth - delegates to PerformanceMonitorDetailed."""
        self.detailed.record_memory_growth()
    
    def record_gc_stats(self):
        """Record GC stats - delegates to PerformanceMonitorDetailed."""
        self.detailed.record_gc_stats()
    
    def record_event_processing_time(self, event_type: str, processing_time: float):
        """Record event processing time - delegates to PerformanceMonitorDetailed."""
        self.detailed.record_event_processing_time(event_type, processing_time)
    
    def record_battle_phase_time(self, phase: str, phase_time: float):
        """Record battle phase time - delegates to PerformanceMonitorDetailed."""
        self.detailed.record_battle_phase_time(phase, phase_time)
    
    def analyze_memory_leaks(self) -> Dict[str, Any]:
        """Analyze memory leaks - delegates to PerformanceMonitorDetailed."""
        return self.detailed.analyze_memory_leaks()
    
    def analyze_cpu_performance(self) -> Dict[str, Any]:
        """Analyze CPU performance - delegates to PerformanceMonitorDetailed."""
        return self.detailed.analyze_cpu_performance()
    
    def analyze_event_performance(self) -> Dict[str, Any]:
        """Analyze event performance - delegates to PerformanceMonitorDetailed."""
        return self.detailed.analyze_event_performance()
    
    def analyze_battle_phase_performance(self) -> Dict[str, Any]:
        """Analyze battle phase performance - delegates to PerformanceMonitorDetailed."""
        return self.detailed.analyze_battle_phase_performance()
    
    def get_detailed_performance_report(self) -> Dict[str, Any]:
        """Get detailed performance report - delegates to PerformanceMonitorDetailed."""
        return self.detailed.get_detailed_performance_report()
    
    # Combined methods
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report combining core and detailed metrics."""
        try:
            core_summary = self.get_performance_summary()
            detailed_report = self.get_detailed_performance_report()
            
            return {
                'core_metrics': core_summary,
                'detailed_analysis': detailed_report,
                'combined_recommendations': self._get_combined_recommendations()
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return {'error': str(e)}
    
    def _get_combined_recommendations(self) -> List[str]:
        """Get combined recommendations from both monitors."""
        try:
            recommendations = []
            
            # Get core recommendations
            core_issues = self.core._detect_performance_issues()
            recommendations.extend(core_issues)
            
            # Get detailed recommendations
            detailed_recommendations = self.detailed._generate_recommendations()
            recommendations.extend(detailed_recommendations)
            
            # Remove duplicates
            return list(set(recommendations))
            
        except Exception as e:
            logger.error(f"Error getting combined recommendations: {e}")
            return [f"Error generating recommendations: {e}"]
    
    def update_all_metrics(self):
        """Update all performance metrics."""
        try:
            # Update core metrics
            self.take_memory_snapshot()
            
            # Update detailed metrics
            self.record_cpu_usage()
            self.record_memory_growth()
            self.record_gc_stats()
            
        except Exception as e:
            logger.error(f"Error updating all metrics: {e}")
    
    def reset_metrics(self):
        """Reset all performance metrics."""
        try:
            # Reset core metrics
            if hasattr(self.core, 'reset_metrics'):
                self.core.reset_metrics()
            else:
                # Fallback: reinitialize core
                self.core = PerformanceMonitorCore(self.enabled)
            
            # Reset detailed metrics
            if hasattr(self.detailed, 'reset_metrics'):
                self.detailed.reset_metrics()
            else:
                # Fallback: reinitialize detailed
                self.detailed = PerformanceMonitorDetailed(self.enabled)
            
            logger.info("All performance metrics reset")
            
        except Exception as e:
            logger.error(f"Error resetting metrics: {e}")
    
    def cleanup(self):
        """Cleanup all performance monitor resources."""
        try:
            self.core.cleanup()
            self.detailed.cleanup()
            self.enabled = False  # Disable monitor after cleanup
            logger.info("All performance monitors cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    # Legacy compatibility methods
    def _start_memory_tracing(self):
        """Legacy method - delegates to PerformanceMonitorCore."""
        return self.core._start_memory_tracing()
    
    def _detect_performance_issues(self) -> List[str]:
        """Legacy method - delegates to PerformanceMonitorCore."""
        return self.core._detect_performance_issues()


# Global performance monitor instance
_performance_monitor = None


def get_performance_monitor() -> BattlePerformanceMonitor:
    """Get the global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = BattlePerformanceMonitor()
    return _performance_monitor


def reset_performance_monitor():
    """Reset the global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor:
        _performance_monitor.cleanup()
    _performance_monitor = None