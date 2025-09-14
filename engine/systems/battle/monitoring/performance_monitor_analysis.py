"""
Performance Monitor Analysis - Performance Analysis
=================================================
Performance analysis and detailed metrics collection.
Split from performance_monitor_detailed.py to comply with 300-line limit.
"""

import psutil
import tracemalloc
import time
import gc
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class AnalysisMetrics:
    """Container for analysis performance metrics."""
    cpu_usage_history: deque = field(default_factory=lambda: deque(maxlen=100))
    memory_growth_history: deque = field(default_factory=lambda: deque(maxlen=100))
    gc_stats: deque = field(default_factory=lambda: deque(maxlen=50))
    
    # Advanced thresholds
    MAX_CPU_USAGE_PERCENT = 80.0
    MAX_MEMORY_LEAK_MB = 100.0
    MAX_GC_FREQUENCY = 10  # per minute


class PerformanceMonitorAnalysis:
    """
    Performance analysis functionality.
    Handles advanced performance analysis and metrics collection.
    """
    
    def __init__(self, enabled: bool = True):
        """Initialize performance analysis monitor."""
        self.enabled = enabled
        self.metrics = AnalysisMetrics()
        self.start_time = time.time()
        self.last_cpu_check = time.time()
        self.last_gc_check = time.time()
        
        logger.info(f"PerformanceMonitorAnalysis initialized (enabled: {enabled})")
    
    def record_cpu_usage(self):
        """Record current CPU usage."""
        if not self.enabled:
            return
        
        try:
            current_time = time.time()
            if current_time - self.last_cpu_check < 0.1:  # Limit to 10 times per second
                return
            
            cpu_percent = psutil.cpu_percent()
            self.metrics.cpu_usage_history.append({
                'timestamp': current_time,
                'cpu_percent': cpu_percent
            })
            
            self.last_cpu_check = current_time
            
        except Exception as e:
            logger.error(f"Error recording CPU usage: {e}")
    
    def record_memory_growth(self):
        """Record memory growth over time."""
        if not self.enabled:
            return
        
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            current_time = time.time()
            
            self.metrics.memory_growth_history.append({
                'timestamp': current_time,
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024
            })
            
        except Exception as e:
            logger.error(f"Error recording memory growth: {e}")
    
    def record_gc_stats(self):
        """Record garbage collection statistics."""
        if not self.enabled:
            return
        
        try:
            current_time = time.time()
            if current_time - self.last_gc_check < 1.0:  # Limit to once per second
                return
            
            gc_stats = gc.get_stats()
            self.metrics.gc_stats.append({
                'timestamp': current_time,
                'collections': gc_stats[0]['collections'] if gc_stats else 0,
                'collected': gc_stats[0]['collected'] if gc_stats else 0,
                'uncollectable': gc_stats[0]['uncollectable'] if gc_stats else 0
            })
            
            self.last_gc_check = current_time
            
        except Exception as e:
            logger.error(f"Error recording GC stats: {e}")
    
    def analyze_memory_leaks(self) -> Dict[str, Any]:
        """Analyze potential memory leaks."""
        try:
            if len(self.metrics.memory_growth_history) < 10:
                return {'leak_detected': False, 'message': 'Insufficient data'}
            
            recent_snapshots = list(self.metrics.memory_growth_history)[-10:]
            memory_values = [snapshot['rss_mb'] for snapshot in recent_snapshots]
            
            # Calculate memory growth trend
            growth_rate = (memory_values[-1] - memory_values[0]) / len(memory_values)
            
            # Check for consistent growth
            consistent_growth = all(
                memory_values[i] <= memory_values[i+1] 
                for i in range(len(memory_values) - 1)
            )
            
            leak_detected = (growth_rate > 1.0 and consistent_growth) or \
                           (memory_values[-1] - memory_values[0] > self.metrics.MAX_MEMORY_LEAK_MB)
            
            return {
                'leak_detected': leak_detected,
                'growth_rate_mb_per_second': growth_rate,
                'total_growth_mb': memory_values[-1] - memory_values[0],
                'current_memory_mb': memory_values[-1],
                'message': 'Memory leak detected' if leak_detected else 'No memory leak detected'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing memory leaks: {e}")
            return {'leak_detected': False, 'error': str(e)}
    
    def analyze_cpu_performance(self) -> Dict[str, Any]:
        """Analyze CPU performance patterns."""
        try:
            if not self.metrics.cpu_usage_history:
                return {'analysis': 'No CPU data available'}
            
            cpu_values = [entry['cpu_percent'] for entry in self.metrics.cpu_usage_history]
            
            avg_cpu = sum(cpu_values) / len(cpu_values)
            max_cpu = max(cpu_values)
            min_cpu = min(cpu_values)
            
            # Check for high CPU usage
            high_cpu_count = sum(1 for cpu in cpu_values if cpu > self.metrics.MAX_CPU_USAGE_PERCENT)
            high_cpu_percentage = (high_cpu_count / len(cpu_values)) * 100
            
            return {
                'avg_cpu_percent': avg_cpu,
                'max_cpu_percent': max_cpu,
                'min_cpu_percent': min_cpu,
                'high_cpu_percentage': high_cpu_percentage,
                'cpu_stress_detected': high_cpu_percentage > 20,  # More than 20% of time above threshold
                'recommendation': 'Consider optimization' if high_cpu_percentage > 20 else 'CPU usage normal'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing CPU performance: {e}")
            return {'error': str(e)}
    
    def get_analysis_report(self) -> Dict[str, Any]:
        """Get comprehensive analysis report."""
        try:
            current_time = time.time()
            uptime = current_time - self.start_time
            
            return {
                'uptime_seconds': uptime,
                'memory_leak_analysis': self.analyze_memory_leaks(),
                'cpu_performance': self.analyze_cpu_performance(),
                'gc_stats': list(self.metrics.gc_stats)[-5:] if self.metrics.gc_stats else [],
                'recommendations': self._generate_recommendations()
            }
            
        except Exception as e:
            logger.error(f"Error generating analysis report: {e}")
            return {'error': str(e)}
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []
        
        try:
            # Check memory leak analysis
            leak_analysis = self.analyze_memory_leaks()
            if leak_analysis.get('leak_detected', False):
                recommendations.append("Memory leak detected - consider reviewing object lifecycle management")
            
            # Check CPU performance
            cpu_analysis = self.analyze_cpu_performance()
            if cpu_analysis.get('cpu_stress_detected', False):
                recommendations.append("High CPU usage detected - consider optimizing hot code paths")
            
            # Check GC frequency
            if len(self.metrics.gc_stats) >= 2:
                recent_gc = list(self.metrics.gc_stats)[-2:]
                gc_frequency = recent_gc[1]['collections'] - recent_gc[0]['collections']
                if gc_frequency > self.metrics.MAX_GC_FREQUENCY:
                    recommendations.append("High garbage collection frequency - consider object pooling")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append(f"Error generating recommendations: {e}")
        
        return recommendations
    
    def cleanup(self):
        """Cleanup performance analysis monitor resources."""
        try:
            # Clear all metrics
            self.metrics.cpu_usage_history.clear()
            self.metrics.memory_growth_history.clear()
            self.metrics.gc_stats.clear()
            
            # Force garbage collection
            gc.collect()
            
            logger.info("Performance analysis monitor cleaned up")
            
        except Exception as e:
            logger.error(f"Error during analysis cleanup: {e}")
