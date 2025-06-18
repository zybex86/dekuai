# ===================================================================
# 🎮 AutoGen DekuDeals - Performance Monitoring (APM)
# Advanced Application Performance Monitoring system
# ===================================================================

import time
import threading
import functools
import traceback
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import json
from pathlib import Path
import logging
from contextlib import contextmanager

# ===================================================================
# Performance Data Models
# ===================================================================


class PerformanceLevel(Enum):
    """Performance levels based on response times"""

    EXCELLENT = "excellent"  # < 1s
    GOOD = "good"  # 1-3s
    ACCEPTABLE = "acceptable"  # 3-5s
    SLOW = "slow"  # 5-10s
    CRITICAL = "critical"  # > 10s


@dataclass
class PerformanceMetric:
    """Single performance measurement"""

    function_name: str
    execution_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    timestamp: datetime
    success: bool
    error_message: Optional[str]
    input_size: Optional[int]
    output_size: Optional[int]
    tags: Dict[str, str]


@dataclass
class PerformanceProfile:
    """Performance profile for a function/component"""

    function_name: str
    total_calls: int
    avg_execution_time: float
    min_execution_time: float
    max_execution_time: float
    p95_execution_time: float
    p99_execution_time: float
    success_rate: float
    avg_memory_usage: float
    avg_cpu_usage: float
    performance_level: PerformanceLevel
    trend: str  # "improving", "stable", "degrading"
    last_updated: datetime


@dataclass
class PerformanceAlert:
    """Performance alert/warning"""

    alert_id: str
    function_name: str
    alert_type: str  # "slow_performance", "high_memory", "high_cpu", "error_rate"
    severity: str  # "warning", "critical"
    message: str
    threshold_value: float
    actual_value: float
    timestamp: datetime
    resolved: bool


# ===================================================================
# Performance Monitoring System
# ===================================================================


class PerformanceMonitor:
    """
    Advanced Application Performance Monitoring (APM) system

    Features:
    - Automatic function performance tracking
    - Memory and CPU usage monitoring
    - Statistical analysis and trending
    - Performance alerts and thresholds
    - Bottleneck identification
    - Historical performance data
    """

    def __init__(self, data_dir: str = "performance_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Storage files
        self.metrics_file = self.data_dir / "performance_metrics.json"
        self.profiles_file = self.data_dir / "performance_profiles.json"
        self.alerts_file = self.data_dir / "performance_alerts.json"

        # In-memory storage
        self.metrics: List[PerformanceMetric] = []
        self.profiles: Dict[str, PerformanceProfile] = {}
        self.alerts: List[PerformanceAlert] = []

        # Configuration
        self.max_metrics_in_memory = 10000
        self.alert_thresholds = {
            "execution_time": 10.0,  # seconds
            "memory_usage": 500.0,  # MB
            "cpu_usage": 80.0,  # percent
            "error_rate": 5.0,  # percent
        }

        # Thread safety
        self._lock = threading.Lock()

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Load existing data
        self._load_existing_data()

    def _load_existing_data(self):
        """Load existing performance data"""
        try:
            # Load metrics (last 7 days)
            if self.metrics_file.exists():
                with open(self.metrics_file, "r") as f:
                    data = json.load(f)
                    cutoff = datetime.now() - timedelta(days=7)
                    for item in data.get("metrics", []):
                        timestamp = datetime.fromisoformat(item["timestamp"])
                        if timestamp > cutoff:
                            metric = PerformanceMetric(
                                function_name=item["function_name"],
                                execution_time=item["execution_time"],
                                memory_usage_mb=item["memory_usage_mb"],
                                cpu_usage_percent=item["cpu_usage_percent"],
                                timestamp=timestamp,
                                success=item["success"],
                                error_message=item.get("error_message"),
                                input_size=item.get("input_size"),
                                output_size=item.get("output_size"),
                                tags=item.get("tags", {}),
                            )
                            self.metrics.append(metric)

            # Load profiles
            if self.profiles_file.exists():
                with open(self.profiles_file, "r") as f:
                    data = json.load(f)
                    for name, profile_data in data.get("profiles", {}).items():
                        profile = PerformanceProfile(
                            function_name=profile_data["function_name"],
                            total_calls=profile_data["total_calls"],
                            avg_execution_time=profile_data["avg_execution_time"],
                            min_execution_time=profile_data["min_execution_time"],
                            max_execution_time=profile_data["max_execution_time"],
                            p95_execution_time=profile_data["p95_execution_time"],
                            p99_execution_time=profile_data["p99_execution_time"],
                            success_rate=profile_data["success_rate"],
                            avg_memory_usage=profile_data["avg_memory_usage"],
                            avg_cpu_usage=profile_data["avg_cpu_usage"],
                            performance_level=PerformanceLevel(
                                profile_data["performance_level"]
                            ),
                            trend=profile_data["trend"],
                            last_updated=datetime.fromisoformat(
                                profile_data["last_updated"]
                            ),
                        )
                        self.profiles[name] = profile

            # Load alerts
            if self.alerts_file.exists():
                with open(self.alerts_file, "r") as f:
                    data = json.load(f)
                    for item in data.get("alerts", []):
                        alert = PerformanceAlert(
                            alert_id=item["alert_id"],
                            function_name=item["function_name"],
                            alert_type=item["alert_type"],
                            severity=item["severity"],
                            message=item["message"],
                            threshold_value=item["threshold_value"],
                            actual_value=item["actual_value"],
                            timestamp=datetime.fromisoformat(item["timestamp"]),
                            resolved=item["resolved"],
                        )
                        self.alerts.append(alert)

        except Exception as e:
            self.logger.warning(f"Could not load existing performance data: {e}")

    def record_performance(
        self,
        function_name: str,
        execution_time: float,
        success: bool = True,
        error_message: Optional[str] = None,
        input_size: Optional[int] = None,
        output_size: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a performance measurement"""

        # Get system resource usage
        try:
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            cpu_usage = process.cpu_percent()
        except:
            memory_usage = 0.0
            cpu_usage = 0.0

        metric = PerformanceMetric(
            function_name=function_name,
            execution_time=execution_time,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            timestamp=datetime.now(),
            success=success,
            error_message=error_message,
            input_size=input_size,
            output_size=output_size,
            tags=tags or {},
        )

        with self._lock:
            self.metrics.append(metric)

            # Keep only recent metrics in memory
            if len(self.metrics) > self.max_metrics_in_memory:
                cutoff = datetime.now() - timedelta(days=1)
                self.metrics = [m for m in self.metrics if m.timestamp > cutoff]

        # Update profile and check alerts
        self._update_performance_profile(function_name)
        self._check_performance_alerts(metric)

        # Save periodically
        if len(self.metrics) % 100 == 0:
            self._save_data()

    def _update_performance_profile(self, function_name: str):
        """Update performance profile for a function"""
        # Get metrics for this function (last 24 hours)
        cutoff = datetime.now() - timedelta(hours=24)
        function_metrics = [
            m
            for m in self.metrics
            if m.function_name == function_name and m.timestamp > cutoff
        ]

        if not function_metrics:
            return

        # Calculate statistics
        execution_times = [m.execution_time for m in function_metrics]
        memory_usages = [m.memory_usage_mb for m in function_metrics]
        cpu_usages = [m.cpu_usage_percent for m in function_metrics]
        success_count = sum(1 for m in function_metrics if m.success)

        # Percentiles
        execution_times.sort()
        p95_index = int(len(execution_times) * 0.95)
        p99_index = int(len(execution_times) * 0.99)

        # Performance level
        avg_time = statistics.mean(execution_times)
        if avg_time < 1.0:
            performance_level = PerformanceLevel.EXCELLENT
        elif avg_time < 3.0:
            performance_level = PerformanceLevel.GOOD
        elif avg_time < 5.0:
            performance_level = PerformanceLevel.ACCEPTABLE
        elif avg_time < 10.0:
            performance_level = PerformanceLevel.SLOW
        else:
            performance_level = PerformanceLevel.CRITICAL

        # Trend analysis (compare with previous profile)
        trend = "stable"
        if function_name in self.profiles:
            old_avg = self.profiles[function_name].avg_execution_time
            if avg_time < old_avg * 0.9:
                trend = "improving"
            elif avg_time > old_avg * 1.1:
                trend = "degrading"

        # Create/update profile
        profile = PerformanceProfile(
            function_name=function_name,
            total_calls=len(function_metrics),
            avg_execution_time=avg_time,
            min_execution_time=min(execution_times),
            max_execution_time=max(execution_times),
            p95_execution_time=(
                execution_times[p95_index]
                if p95_index < len(execution_times)
                else max(execution_times)
            ),
            p99_execution_time=(
                execution_times[p99_index]
                if p99_index < len(execution_times)
                else max(execution_times)
            ),
            success_rate=(success_count / len(function_metrics)) * 100,
            avg_memory_usage=statistics.mean(memory_usages),
            avg_cpu_usage=statistics.mean(cpu_usages),
            performance_level=performance_level,
            trend=trend,
            last_updated=datetime.now(),
        )

        self.profiles[function_name] = profile

    def _check_performance_alerts(self, metric: PerformanceMetric):
        """Check if metric triggers any performance alerts"""
        alerts_to_create = []

        # Execution time alert
        if metric.execution_time > self.alert_thresholds["execution_time"]:
            alerts_to_create.append(
                {
                    "alert_type": "slow_performance",
                    "severity": "critical" if metric.execution_time > 30 else "warning",
                    "message": f"Slow execution time: {metric.execution_time:.2f}s",
                    "threshold_value": self.alert_thresholds["execution_time"],
                    "actual_value": metric.execution_time,
                }
            )

        # Memory usage alert
        if metric.memory_usage_mb > self.alert_thresholds["memory_usage"]:
            alerts_to_create.append(
                {
                    "alert_type": "high_memory",
                    "severity": (
                        "critical" if metric.memory_usage_mb > 1000 else "warning"
                    ),
                    "message": f"High memory usage: {metric.memory_usage_mb:.1f}MB",
                    "threshold_value": self.alert_thresholds["memory_usage"],
                    "actual_value": metric.memory_usage_mb,
                }
            )

        # CPU usage alert
        if metric.cpu_usage_percent > self.alert_thresholds["cpu_usage"]:
            alerts_to_create.append(
                {
                    "alert_type": "high_cpu",
                    "severity": (
                        "critical" if metric.cpu_usage_percent > 95 else "warning"
                    ),
                    "message": f"High CPU usage: {metric.cpu_usage_percent:.1f}%",
                    "threshold_value": self.alert_thresholds["cpu_usage"],
                    "actual_value": metric.cpu_usage_percent,
                }
            )

        # Error rate alert
        if not metric.success:
            # Check recent error rate for this function
            recent_metrics = [
                m
                for m in self.metrics
                if m.function_name == metric.function_name
                and m.timestamp > datetime.now() - timedelta(hours=1)
            ]

            if recent_metrics:
                error_rate = (
                    1
                    - sum(1 for m in recent_metrics if m.success) / len(recent_metrics)
                ) * 100
                if error_rate > self.alert_thresholds["error_rate"]:
                    alerts_to_create.append(
                        {
                            "alert_type": "error_rate",
                            "severity": "critical" if error_rate > 20 else "warning",
                            "message": f"High error rate: {error_rate:.1f}%",
                            "threshold_value": self.alert_thresholds["error_rate"],
                            "actual_value": error_rate,
                        }
                    )

        # Create alerts
        for alert_data in alerts_to_create:
            alert = PerformanceAlert(
                alert_id=f"{metric.function_name}_{alert_data['alert_type']}_{int(time.time())}",
                function_name=metric.function_name,
                alert_type=alert_data["alert_type"],
                severity=alert_data["severity"],
                message=alert_data["message"],
                threshold_value=alert_data["threshold_value"],
                actual_value=alert_data["actual_value"],
                timestamp=metric.timestamp,
                resolved=False,
            )

            self.alerts.append(alert)
            self.logger.warning(f"Performance alert: {alert.message}")

    @contextmanager
    def measure_performance(
        self, function_name: str, tags: Optional[Dict[str, str]] = None
    ):
        """Context manager for measuring performance"""
        start_time = time.time()
        start_memory = 0
        error_message = None
        success = True

        try:
            process = psutil.Process()
            start_memory = process.memory_info().rss / 1024 / 1024
        except:
            pass

        try:
            yield
        except Exception as e:
            success = False
            error_message = str(e)
            raise
        finally:
            execution_time = time.time() - start_time
            self.record_performance(
                function_name=function_name,
                execution_time=execution_time,
                success=success,
                error_message=error_message,
                tags=tags,
            )

    def performance_decorator(
        self, function_name: Optional[str] = None, tags: Optional[Dict[str, str]] = None
    ):
        """Decorator for automatic performance monitoring"""

        def decorator(func: Callable) -> Callable:
            name = function_name or f"{func.__module__}.{func.__name__}"

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                with self.measure_performance(name, tags):
                    return func(*args, **kwargs)

            return wrapper

        return decorator

    def get_performance_summary(self, time_range: str = "24h") -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        # Parse time range
        if time_range.endswith("h"):
            hours = int(time_range[:-1])
            cutoff = datetime.now() - timedelta(hours=hours)
        elif time_range.endswith("d"):
            days = int(time_range[:-1])
            cutoff = datetime.now() - timedelta(days=days)
        else:
            cutoff = datetime.now() - timedelta(hours=24)

        # Filter metrics
        recent_metrics = [m for m in self.metrics if m.timestamp > cutoff]

        if not recent_metrics:
            return {"error": "No metrics found for the specified time range"}

        # Overall statistics
        execution_times = [m.execution_time for m in recent_metrics]
        memory_usages = [m.memory_usage_mb for m in recent_metrics]
        cpu_usages = [m.cpu_usage_percent for m in recent_metrics]
        success_count = sum(1 for m in recent_metrics if m.success)

        # Function performance breakdown
        function_stats = {}
        for metric in recent_metrics:
            name = metric.function_name
            if name not in function_stats:
                function_stats[name] = {
                    "calls": 0,
                    "total_time": 0.0,
                    "max_time": 0.0,
                    "errors": 0,
                }

            stats = function_stats[name]
            stats["calls"] += 1
            stats["total_time"] += metric.execution_time
            stats["max_time"] = max(stats["max_time"], metric.execution_time)
            if not metric.success:
                stats["errors"] += 1

        # Calculate averages and error rates
        for name, stats in function_stats.items():
            stats["avg_time"] = stats["total_time"] / stats["calls"]
            stats["error_rate"] = (stats["errors"] / stats["calls"]) * 100

        # Active alerts
        active_alerts = [
            a for a in self.alerts if not a.resolved and a.timestamp > cutoff
        ]

        return {
            "time_range": time_range,
            "total_metrics": len(recent_metrics),
            "overall_stats": {
                "avg_execution_time": statistics.mean(execution_times),
                "p95_execution_time": (
                    sorted(execution_times)[int(len(execution_times) * 0.95)]
                    if execution_times
                    else 0
                ),
                "max_execution_time": max(execution_times) if execution_times else 0,
                "avg_memory_usage": statistics.mean(memory_usages),
                "max_memory_usage": max(memory_usages) if memory_usages else 0,
                "avg_cpu_usage": statistics.mean(cpu_usages),
                "success_rate": (success_count / len(recent_metrics)) * 100,
            },
            "function_performance": dict(
                sorted(
                    function_stats.items(), key=lambda x: x[1]["avg_time"], reverse=True
                )
            ),
            "active_alerts": len(active_alerts),
            "performance_profiles": len(self.profiles),
            "last_updated": datetime.now().isoformat(),
        }

    def get_bottlenecks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        bottlenecks = []

        for name, profile in self.profiles.items():
            # Calculate bottleneck score based on multiple factors
            time_score = min(profile.avg_execution_time / 10.0, 1.0)  # Normalize to 0-1
            memory_score = min(
                profile.avg_memory_usage / 1000.0, 1.0
            )  # Normalize to 0-1
            cpu_score = profile.avg_cpu_usage / 100.0  # Already 0-1
            error_score = (100 - profile.success_rate) / 100.0  # Invert success rate

            bottleneck_score = (
                time_score * 0.4
                + memory_score * 0.2
                + cpu_score * 0.2
                + error_score * 0.2
            )

            bottlenecks.append(
                {
                    "function_name": name,
                    "bottleneck_score": bottleneck_score,
                    "avg_execution_time": profile.avg_execution_time,
                    "performance_level": profile.performance_level.value,
                    "trend": profile.trend,
                    "success_rate": profile.success_rate,
                    "total_calls": profile.total_calls,
                    "recommendations": self._generate_recommendations(profile),
                }
            )

        # Sort by bottleneck score and return top results
        bottlenecks.sort(key=lambda x: x["bottleneck_score"], reverse=True)
        return bottlenecks[:limit]

    def _generate_recommendations(self, profile: PerformanceProfile) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []

        if profile.avg_execution_time > 5.0:
            recommendations.append(
                "Consider optimizing algorithm complexity or adding caching"
            )

        if profile.avg_memory_usage > 500:
            recommendations.append(
                "High memory usage - check for memory leaks or optimize data structures"
            )

        if profile.avg_cpu_usage > 80:
            recommendations.append(
                "High CPU usage - consider parallel processing or algorithm optimization"
            )

        if profile.success_rate < 95:
            recommendations.append(
                "Low success rate - improve error handling and input validation"
            )

        if profile.trend == "degrading":
            recommendations.append(
                "Performance is degrading - investigate recent changes"
            )

        if profile.performance_level == PerformanceLevel.CRITICAL:
            recommendations.append("CRITICAL: Immediate optimization required")

        return recommendations

    def _save_data(self):
        """Save performance data to disk"""
        try:
            # Save metrics
            metrics_data = {"timestamp": datetime.now().isoformat(), "metrics": []}

            for metric in self.metrics:
                metrics_data["metrics"].append(
                    {
                        "function_name": metric.function_name,
                        "execution_time": metric.execution_time,
                        "memory_usage_mb": metric.memory_usage_mb,
                        "cpu_usage_percent": metric.cpu_usage_percent,
                        "timestamp": metric.timestamp.isoformat(),
                        "success": metric.success,
                        "error_message": metric.error_message,
                        "input_size": metric.input_size,
                        "output_size": metric.output_size,
                        "tags": metric.tags,
                    }
                )

            with open(self.metrics_file, "w") as f:
                json.dump(metrics_data, f, indent=2)

            # Save profiles
            profiles_data = {"timestamp": datetime.now().isoformat(), "profiles": {}}

            for name, profile in self.profiles.items():
                profiles_data["profiles"][name] = {
                    "function_name": profile.function_name,
                    "total_calls": profile.total_calls,
                    "avg_execution_time": profile.avg_execution_time,
                    "min_execution_time": profile.min_execution_time,
                    "max_execution_time": profile.max_execution_time,
                    "p95_execution_time": profile.p95_execution_time,
                    "p99_execution_time": profile.p99_execution_time,
                    "success_rate": profile.success_rate,
                    "avg_memory_usage": profile.avg_memory_usage,
                    "avg_cpu_usage": profile.avg_cpu_usage,
                    "performance_level": profile.performance_level.value,
                    "trend": profile.trend,
                    "last_updated": profile.last_updated.isoformat(),
                }

            with open(self.profiles_file, "w") as f:
                json.dump(profiles_data, f, indent=2)

            # Save alerts
            alerts_data = {"timestamp": datetime.now().isoformat(), "alerts": []}

            for alert in self.alerts:
                alerts_data["alerts"].append(
                    {
                        "alert_id": alert.alert_id,
                        "function_name": alert.function_name,
                        "alert_type": alert.alert_type,
                        "severity": alert.severity,
                        "message": alert.message,
                        "threshold_value": alert.threshold_value,
                        "actual_value": alert.actual_value,
                        "timestamp": alert.timestamp.isoformat(),
                        "resolved": alert.resolved,
                    }
                )

            with open(self.alerts_file, "w") as f:
                json.dump(alerts_data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Could not save performance data: {e}")


# ===================================================================
# Global Performance Monitor Instance
# ===================================================================

# Create a global instance for easy use
_global_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get or create global performance monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


def monitor_performance(
    function_name: Optional[str] = None, tags: Optional[Dict[str, str]] = None
):
    """Decorator for automatic performance monitoring using global monitor"""
    return get_performance_monitor().performance_decorator(function_name, tags)


# ===================================================================
# Example Usage
# ===================================================================

if __name__ == "__main__":
    # Create performance monitor
    monitor = PerformanceMonitor()

    # Test performance monitoring
    @monitor.performance_decorator("test_function")
    def test_function(duration: float = 1.0):
        time.sleep(duration)
        return f"Slept for {duration} seconds"

    # Run some tests
    test_function(0.5)
    test_function(2.0)
    test_function(0.1)

    # Manual performance recording
    monitor.record_performance(
        function_name="manual_test",
        execution_time=1.5,
        success=True,
        tags={"type": "manual"},
    )

    # Get performance summary
    summary = monitor.get_performance_summary("1h")
    print("Performance Summary:", json.dumps(summary, indent=2))

    # Get bottlenecks
    bottlenecks = monitor.get_bottlenecks(5)
    print("\nBottlenecks:", json.dumps(bottlenecks, indent=2))

    # Save data
    monitor._save_data()
