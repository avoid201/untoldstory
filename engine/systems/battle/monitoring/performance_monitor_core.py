"""
Performance Monitor Core - Basic Performance Tracking
====================================================
Core performance monitoring and metrics collection.
Split from performance_monitor.py to comply with 300-line limit.
"""

import psutil
import tracemalloc
import time
import gc
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    frame_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    memory_snapshots: deque = field(default_factory=lambda: deque(maxlen=100))
    event_counts: Dict[str, int] = field(default_factory=dict)
    turn_times: deque = field(default_factory=lambda: deque(maxlen=100))
    damage_calc_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    # Performance thresholds
    TARGET_FPS = 60.0
    MAX_MEMORY_GROWTH_MB = 50.0
    MAX_TURN_TIME_MS = 100.0
    MAX_DAMAGE_CALC_TIME_MS = 1.0


class PerformanceMonitorCore:
    """
    Core performance monitoring functionality.
    Handles basic metrics collection and monitoring.
    """
    
    def __init__(self, enabled: bool = True):
        """Initialize performance monitor."""
        self.enabled = enabled
        self.metrics = PerformanceMetrics()
        self.start_time = time.time()
        self.last_memory_check = time.time()
        self.memory_traced = False
        
        if self.enabled:
            self._start_memory_tracing()
        
        logger.info(f"PerformanceMonitorCore initialized (enabled: {enabled})")
    
    def _start_memory_tracing(self):
        """Start memory tracing for leak detection."""
        try:
            if not self.memory_traced:
                tracemalloc.start()
                self.memory_traced = True
                logger.debug("Memory tracing started")
        except Exception as e:
            logger.error(f"Failed to start memory tracing: {e}")
    
    def record_frame_time(self, frame_time: float):
        """Record frame processing time."""
        if not self.enabled:
            return
        
        try:
            self.metrics.frame_times.append(frame_time)
            
            # Check for performance issues
            if frame_time > 1.0 / self.metrics.TARGET_FPS:
                logger.warning(f"Frame time exceeded target: {frame_time:.3f}s")
                
        except Exception as e:
            logger.error(f"Error recording frame time: {e}")
    
    def record_turn_time(self, turn_time: float):
        """Record turn processing time."""
        if not self.enabled:
            return
        
        try:
            self.metrics.turn_times.append(turn_time)
            
            # Check for slow turns
            if turn_time > self.metrics.MAX_TURN_TIME_MS / 1000.0:
                logger.warning(f"Slow turn detected: {turn_time:.3f}s")
                
        except Exception as e:
            logger.error(f"Error recording turn time: {e}")
    
    def record_damage_calculation(self, calc_time: float):
        """Record damage calculation time."""
        if not self.enabled:
            return
        
        try:
            self.metrics.damage_calc_times.append(calc_time)
            
            # Check for slow damage calculations
            if calc_time > self.metrics.MAX_DAMAGE_CALC_TIME_MS / 1000.0:
                logger.warning(f"Slow damage calculation: {calc_time:.3f}s")
                
        except Exception as e:
            logger.error(f"Error recording damage calculation time: {e}")
    
    def record_event(self, event_type: str):
        """Record event occurrence."""
        if not self.enabled:
            return
        
        try:
            if event_type not in self.metrics.event_counts:
                self.metrics.event_counts[event_type] = 0
            self.metrics.event_counts[event_type] += 1
            
        except Exception as e:
            logger.error(f"Error recording event: {e}")
    
    def get_current_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics."""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
                'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
                'percent': process.memory_percent(),
                'available_mb': psutil.virtual_memory().available / 1024 / 1024
            }
            
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return {'rss_mb': 0, 'vms_mb': 0, 'percent': 0, 'available_mb': 0}
    
    def take_memory_snapshot(self):
        """Take a memory snapshot for leak detection."""
        if not self.enabled or not self.memory_traced:
            return
        
        try:
            current_time = time.time()
            if current_time - self.last_memory_check < 1.0:  # Limit to once per second
                return
            
            snapshot = tracemalloc.take_snapshot()
            memory_usage = self.get_current_memory_usage()
            
            self.metrics.memory_snapshots.append({
                'timestamp': current_time,
                'snapshot': snapshot,
                'memory_usage': memory_usage
            })
            
            self.last_memory_check = current_time
            
        except Exception as e:
            logger.error(f"Error taking memory snapshot: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary."""
        try:
            current_time = time.time()
            uptime = current_time - self.start_time
            
            # Calculate average frame time
            avg_frame_time = 0.0
            if self.metrics.frame_times:
                avg_frame_time = sum(self.metrics.frame_times) / len(self.metrics.frame_times)
            
            # Calculate FPS
            current_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0
            
            # Calculate average turn time
            avg_turn_time = 0.0
            if self.metrics.turn_times:
                avg_turn_time = sum(self.metrics.turn_times) / len(self.metrics.turn_times)
            
            # Calculate average damage calc time
            avg_damage_calc_time = 0.0
            if self.metrics.damage_calc_times:
                avg_damage_calc_time = sum(self.metrics.damage_calc_times) / len(self.metrics.damage_calc_times)
            
            # Get current memory usage
            memory_usage = self.get_current_memory_usage()
            
            return {
                'uptime_seconds': uptime,
                'current_fps': current_fps,
                'target_fps': self.metrics.TARGET_FPS,
                'avg_frame_time_ms': avg_frame_time * 1000,
                'avg_turn_time_ms': avg_turn_time * 1000,
                'avg_damage_calc_time_ms': avg_damage_calc_time * 1000,
                'memory_usage': memory_usage,
                'total_events': sum(self.metrics.event_counts.values()),
                'event_breakdown': dict(self.metrics.event_counts),
                'performance_issues': self._detect_performance_issues()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {'error': str(e)}
    
    def _detect_performance_issues(self) -> List[str]:
        """Detect current performance issues."""
        issues = []
        
        try:
            # Check FPS
            if self.metrics.frame_times:
                avg_frame_time = sum(self.metrics.frame_times) / len(self.metrics.frame_times)
                current_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
                if current_fps < self.metrics.TARGET_FPS * 0.8:  # 20% below target
                    issues.append(f"Low FPS: {current_fps:.1f} (target: {self.metrics.TARGET_FPS})")
            
            # Check turn times
            if self.metrics.turn_times:
                avg_turn_time = sum(self.metrics.turn_times) / len(self.metrics.turn_times)
                if avg_turn_time > self.metrics.MAX_TURN_TIME_MS / 1000.0:
                    issues.append(f"Slow turns: {avg_turn_time*1000:.1f}ms (max: {self.metrics.MAX_TURN_TIME_MS}ms)")
            
            # Check damage calc times
            if self.metrics.damage_calc_times:
                avg_damage_calc_time = sum(self.metrics.damage_calc_times) / len(self.metrics.damage_calc_times)
                if avg_damage_calc_time > self.metrics.MAX_DAMAGE_CALC_TIME_MS / 1000.0:
                    issues.append(f"Slow damage calc: {avg_damage_calc_time*1000:.1f}ms (max: {self.metrics.MAX_DAMAGE_CALC_TIME_MS}ms)")
            
            # Check memory growth
            if len(self.metrics.memory_snapshots) >= 2:
                recent_snapshots = list(self.metrics.memory_snapshots)[-2:]
                memory_growth = (recent_snapshots[1]['memory_usage']['rss_mb'] - 
                               recent_snapshots[0]['memory_usage']['rss_mb'])
                if memory_growth > self.metrics.MAX_MEMORY_GROWTH_MB:
                    issues.append(f"High memory growth: {memory_growth:.1f}MB")
            
        except Exception as e:
            logger.error(f"Error detecting performance issues: {e}")
            issues.append(f"Error detecting issues: {e}")
        
        return issues
    
    def cleanup(self):
        """Cleanup performance monitor resources."""
        try:
            if self.memory_traced:
                tracemalloc.stop()
                self.memory_traced = False
            
            # Clear metrics
            self.metrics.frame_times.clear()
            self.metrics.memory_snapshots.clear()
            self.metrics.event_counts.clear()
            self.metrics.turn_times.clear()
            self.metrics.damage_calc_times.clear()
            
            # Force garbage collection
            gc.collect()
            
            logger.info("Performance monitor cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
