"""
Performance Report Generator
===========================
Generates comprehensive performance reports for the battle system.
Analyzes test results and creates detailed performance documentation.

Version: 1.0.0
Author: Performance Engineer Agent 5
"""

import json
import time
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import performance monitor
from engine.systems.battle.performance_monitor import get_performance_monitor


class PerformanceReportGenerator:
    """Generates comprehensive performance reports."""
    
    def __init__(self):
        """Initialize the report generator."""
        self.report_data = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self._get_system_info(),
            'test_results': {},
            'performance_metrics': {},
            'recommendations': [],
            'bottlenecks': [],
            'optimizations': []
        }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        import platform
        import psutil
        
        return {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': round(psutil.virtual_memory().total / 1024 / 1024 / 1024, 2),
            'memory_available_gb': round(psutil.virtual_memory().available / 1024 / 1024 / 1024, 2)
        }
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run all performance tests and collect results."""
        print("🚀 Running performance tests...")
        
        test_results = {}
        
        # Run memory leak tests
        print("  📊 Running memory leak tests...")
        memory_results = self._run_test_suite("tests/test_battle_performance.py::TestBattleMemoryLeaks")
        test_results['memory_leaks'] = memory_results
        
        # Run performance benchmarks
        print("  ⚡ Running performance benchmarks...")
        perf_results = self._run_test_suite("tests/test_battle_performance.py::TestBattlePerformance")
        test_results['performance'] = perf_results
        
        # Run stability tests
        print("  🔧 Running stability tests...")
        stability_results = self._run_test_suite("tests/test_battle_performance.py::TestBattleStability")
        test_results['stability'] = stability_results
        
        # Run integration tests
        print("  🔗 Running integration tests...")
        integration_results = self._run_test_suite("tests/test_battle_integration.py")
        test_results['integration'] = integration_results
        
        return test_results
    
    def _run_test_suite(self, test_path: str) -> Dict[str, Any]:
        """Run a specific test suite and return results."""
        try:
            # Run pytest with JSON output
            result = subprocess.run([
                sys.executable, "-m", "pytest", test_path, 
                "-v", "--tb=short", "--json-report", "--json-report-file=temp_report.json"
            ], capture_output=True, text=True, timeout=300)
            
            # Parse JSON report if available
            json_file = Path("temp_report.json")
            if json_file.exists():
                with open(json_file, 'r') as f:
                    json_data = json.load(f)
                json_file.unlink()  # Clean up
                return {
                    'success': result.returncode == 0,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'json_data': json_data
                }
            else:
                return {
                    'success': result.returncode == 0,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'json_data': None
                }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': 'Test suite timed out after 5 minutes',
                'json_data': None
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'json_data': None
            }
    
    def collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect performance metrics from the monitor."""
        monitor = get_performance_monitor()
        return monitor.get_performance_report()
    
    def analyze_bottlenecks(self, test_results: Dict[str, Any]) -> List[str]:
        """Analyze test results for performance bottlenecks."""
        bottlenecks = []
        
        # Check memory leak test results
        if 'memory_leaks' in test_results:
            memory_test = test_results['memory_leaks']
            if not memory_test['success']:
                bottlenecks.append("Memory leak detected in long-running battles")
        
        # Check performance test results
        if 'performance' in test_results:
            perf_test = test_results['performance']
            if not perf_test['success']:
                bottlenecks.append("Performance benchmarks failed - system too slow")
        
        # Check stability test results
        if 'stability' in test_results:
            stability_test = test_results['stability']
            if not stability_test['success']:
                bottlenecks.append("System instability under stress conditions")
        
        return bottlenecks
    
    def generate_recommendations(self, performance_metrics: Dict[str, Any], bottlenecks: List[str]) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []
        
        # FPS recommendations
        if 'fps' in performance_metrics:
            fps_data = performance_metrics['fps']
            if fps_data['average'] < 60:
                recommendations.append(f"Optimize rendering pipeline - current FPS: {fps_data['average']:.1f}")
        
        # Memory recommendations
        if 'memory' in performance_metrics:
            memory_data = performance_metrics['memory']
            if memory_data['growth_mb'] > 50:
                recommendations.append(f"Implement memory cleanup - growth: {memory_data['growth_mb']:.1f}MB")
        
        # Turn processing recommendations
        if 'turns' in performance_metrics:
            turn_data = performance_metrics['turns']
            if turn_data['avg_time_ms'] > 100:
                recommendations.append(f"Optimize turn processing - current: {turn_data['avg_time_ms']:.1f}ms")
        
        # Damage calculation recommendations
        if 'damage_calc' in performance_metrics:
            calc_data = performance_metrics['damage_calc']
            if calc_data['avg_time_ms'] > 1:
                recommendations.append(f"Optimize damage calculations - current: {calc_data['avg_time_ms']:.3f}ms")
        
        # Bottleneck-based recommendations
        for bottleneck in bottlenecks:
            if "memory leak" in bottleneck.lower():
                recommendations.append("Implement object pooling for frequently created objects")
            elif "performance" in bottleneck.lower():
                recommendations.append("Profile and optimize critical code paths")
            elif "stability" in bottleneck.lower():
                recommendations.append("Add more error handling and recovery mechanisms")
        
        return recommendations
    
    def generate_markdown_report(self) -> str:
        """Generate markdown performance report."""
        # Collect all data
        test_results = self.run_performance_tests()
        performance_metrics = self.collect_performance_metrics()
        bottlenecks = self.analyze_bottlenecks(test_results)
        recommendations = self.generate_recommendations(performance_metrics, bottlenecks)
        
        # Generate report
        report = f"""# 🚀 BATTLE SYSTEM PERFORMANCE REPORT

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**System:** {self.report_data['system_info']['platform']}
**Python:** {self.report_data['system_info']['python_version']}

## 📊 Performance Metrics

### Frame Rate
- **Average FPS:** {performance_metrics.get('fps', {}).get('average', 'N/A')}
- **Minimum FPS:** {performance_metrics.get('fps', {}).get('minimum', 'N/A')}
- **Maximum FPS:** {performance_metrics.get('fps', {}).get('maximum', 'N/A')}
- **Target:** 60 FPS
- **Status:** {performance_metrics.get('fps', {}).get('status', 'Unknown')}

### Memory Usage
- **Current:** {performance_metrics.get('memory', {}).get('current_mb', 'N/A')} MB
- **Growth:** {performance_metrics.get('memory', {}).get('growth_mb', 'N/A')} MB
- **Max Growth Limit:** 50 MB
- **Status:** {performance_metrics.get('memory', {}).get('status', 'Unknown')}

### Turn Processing
- **Average Time:** {performance_metrics.get('turns', {}).get('avg_time_ms', 'N/A')} ms
- **Turns/Second:** {performance_metrics.get('turns', {}).get('turns_per_second', 'N/A')}
- **Max Time Limit:** 100 ms
- **Status:** {performance_metrics.get('turns', {}).get('status', 'Unknown')}

### Damage Calculation
- **Average Time:** {performance_metrics.get('damage_calc', {}).get('avg_time_ms', 'N/A')} ms
- **Calcs/Second:** {performance_metrics.get('damage_calc', {}).get('calcs_per_second', 'N/A')}
- **Max Time Limit:** 1 ms
- **Status:** {performance_metrics.get('damage_calc', {}).get('status', 'Unknown')}

### Event Processing
- **Total Events:** {performance_metrics.get('events', {}).get('total', 'N/A')}
- **Events/Second:** {performance_metrics.get('events', {}).get('per_second', 'N/A')}

## 🧪 Test Results

### Memory Leak Tests
- **Status:** {'✅ PASSED' if test_results.get('memory_leaks', {}).get('success') else '❌ FAILED'}
- **Details:** {'All memory leak tests passed' if test_results.get('memory_leaks', {}).get('success') else 'Memory leaks detected'}

### Performance Benchmarks
- **Status:** {'✅ PASSED' if test_results.get('performance', {}).get('success') else '❌ FAILED'}
- **Details:** {'All performance benchmarks met' if test_results.get('performance', {}).get('success') else 'Performance targets not met'}

### Stability Tests
- **Status:** {'✅ PASSED' if test_results.get('stability', {}).get('success') else '❌ FAILED'}
- **Details:** {'System stable under stress' if test_results.get('stability', {}).get('success') else 'System instability detected'}

### Integration Tests
- **Status:** {'✅ PASSED' if test_results.get('integration', {}).get('success') else '❌ FAILED'}
- **Details:** {'All integration tests passed' if test_results.get('integration', {}).get('success') else 'Integration issues detected'}

## 🔥 Bottlenecks Identified

{self._format_list(bottlenecks) if bottlenecks else 'No major bottlenecks detected'}

## ✅ Optimizations Applied

- Performance monitoring system implemented
- Memory leak detection enabled
- Event queue size limits enforced
- Error recovery mechanisms in place
- Comprehensive test coverage added

## 📈 Recommendations

{self._format_list(recommendations) if recommendations else 'No specific recommendations at this time'}

## 🎯 Overall Performance Status

**Status:** {performance_metrics.get('overall_status', 'Unknown')}

### Summary
- **Memory Management:** {'✅ Good' if performance_metrics.get('memory', {}).get('status') == 'good' else '⚠️ Needs Attention'}
- **Frame Rate:** {'✅ Good' if performance_metrics.get('fps', {}).get('status') == 'good' else '⚠️ Needs Attention'}
- **Turn Processing:** {'✅ Good' if performance_metrics.get('turns', {}).get('status') == 'good' else '⚠️ Needs Attention'}
- **Damage Calculation:** {'✅ Good' if performance_metrics.get('damage_calc', {}).get('status') == 'good' else '⚠️ Needs Attention'}

## 🔧 Next Steps

1. **Monitor Performance:** Continue using the performance monitor during development
2. **Run Tests Regularly:** Execute performance tests before each release
3. **Profile Bottlenecks:** Use profiling tools to identify specific slow code paths
4. **Optimize Critical Paths:** Focus on the most frequently used code paths
5. **Memory Management:** Implement object pooling for frequently created objects

---

*Report generated by Performance Engineer Agent 5*
*For questions or issues, check the test logs and performance monitor output*
"""
        
        return report
    
    def _format_list(self, items: List[str]) -> str:
        """Format a list of items for markdown."""
        if not items:
            return "None"
        return "\n".join(f"- {item}" for item in items)
    
    def save_report(self, filename: str = "PERFORMANCE_REPORT.md") -> None:
        """Save the performance report to a file."""
        report_content = self.generate_markdown_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 Performance report saved to {filename}")
    
    def print_summary(self) -> None:
        """Print a summary of the performance report."""
        test_results = self.run_performance_tests()
        performance_metrics = self.collect_performance_metrics()
        
        print("\n" + "="*60)
        print("🚀 BATTLE SYSTEM PERFORMANCE SUMMARY")
        print("="*60)
        
        # Test results summary
        print("\n📊 Test Results:")
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result['success'] else "❌ FAILED"
            print(f"  {test_name}: {status}")
        
        # Performance metrics summary
        print("\n⚡ Performance Metrics:")
        if 'fps' in performance_metrics:
            print(f"  FPS: {performance_metrics['fps']['average']:.1f} (target: 60)")
        if 'memory' in performance_metrics:
            print(f"  Memory Growth: {performance_metrics['memory']['growth_mb']:.1f} MB (limit: 50)")
        if 'turns' in performance_metrics:
            print(f"  Turn Time: {performance_metrics['turns']['avg_time_ms']:.1f} ms (limit: 100)")
        
        # Overall status
        overall_status = performance_metrics.get('overall_status', 'Unknown')
        print(f"\n🎯 Overall Status: {overall_status}")
        
        print("="*60)


def main():
    """Main function to generate performance report."""
    print("🚀 Starting Battle System Performance Analysis...")
    
    generator = PerformanceReportGenerator()
    
    # Generate and save report
    generator.save_report("PERFORMANCE_REPORT.md")
    
    # Print summary
    generator.print_summary()
    
    print("\n✅ Performance analysis complete!")


if __name__ == "__main__":
    main()
