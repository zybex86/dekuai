# ===================================================================
# 🎮 AutoGen DekuDeals - Real-Time Monitoring Dashboard
# Enterprise-level monitoring and observability system
# ===================================================================

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from pathlib import Path
import logging

# ===================================================================
# Configuration and Data Models
# ===================================================================


class MetricType(Enum):
    """Types of metrics we can monitor"""

    PERFORMANCE = "performance"
    USAGE = "usage"
    QUALITY = "quality"
    SYSTEM = "system"
    BUSINESS = "business"
    ERROR = "error"


class AlertLevel(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class MetricPoint:
    """Single metric data point"""

    timestamp: datetime
    metric_name: str
    metric_type: MetricType
    value: Union[float, int, str]
    tags: Dict[str, str]
    metadata: Dict[str, Any]


@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""

    widget_id: str
    widget_type: str  # "chart", "counter", "gauge", "table", "alert"
    title: str
    metric_query: str
    refresh_interval: int  # seconds
    config: Dict[str, Any]


@dataclass
class SystemHealth:
    """Overall system health status"""

    status: str  # "healthy", "degraded", "critical"
    overall_score: float  # 0.0-1.0
    component_health: Dict[str, float]
    active_alerts: List[str]
    last_check: datetime


# ===================================================================
# Real-Time Monitoring Dashboard
# ===================================================================


class MonitoringDashboard:
    """
    Enterprise-level real-time monitoring dashboard

    Features:
    - Real-time metrics collection and display
    - Multiple dashboard layouts and widgets
    - Performance trend analysis
    - Health status monitoring
    - Custom metric queries
    """

    def __init__(self, data_dir: str = "monitoring_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Configuration
        self.metrics_file = self.data_dir / "metrics.json"
        self.dashboard_config_file = self.data_dir / "dashboard_config.json"

        # In-memory storage for real-time data
        self.live_metrics: List[MetricPoint] = []
        self.widgets: Dict[str, DashboardWidget] = {}
        self.system_health = SystemHealth(
            status="healthy",
            overall_score=1.0,
            component_health={},
            active_alerts=[],
            last_check=datetime.now(),
        )

        # Thread safety
        self._lock = threading.Lock()
        self._monitoring_active = False
        self._monitoring_thread: Optional[threading.Thread] = None

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Initialize dashboard
        self._initialize_dashboard()
        self._load_existing_data()

    def _initialize_dashboard(self):
        """Initialize default dashboard configuration"""
        default_widgets = {
            "performance_overview": DashboardWidget(
                widget_id="performance_overview",
                widget_type="chart",
                title="Performance Overview",
                metric_query="performance.*",
                refresh_interval=5,
                config={"chart_type": "line", "time_range": "1h", "aggregation": "avg"},
            ),
            "analysis_count": DashboardWidget(
                widget_id="analysis_count",
                widget_type="counter",
                title="Total Analyses",
                metric_query="usage.analysis_count",
                refresh_interval=10,
                config={"format": "integer", "trend": True},
            ),
            "error_rate": DashboardWidget(
                widget_id="error_rate",
                widget_type="gauge",
                title="Error Rate",
                metric_query="error.rate",
                refresh_interval=5,
                config={"max_value": 100, "thresholds": [70, 90], "unit": "%"},
            ),
            "quality_trend": DashboardWidget(
                widget_id="quality_trend",
                widget_type="chart",
                title="Quality Trend",
                metric_query="quality.overall_score",
                refresh_interval=30,
                config={
                    "chart_type": "line",
                    "time_range": "24h",
                    "aggregation": "avg",
                },
            ),
            "active_sessions": DashboardWidget(
                widget_id="active_sessions",
                widget_type="counter",
                title="Active Sessions",
                metric_query="usage.active_sessions",
                refresh_interval=5,
                config={"format": "integer", "real_time": True},
            ),
            "system_health": DashboardWidget(
                widget_id="system_health",
                widget_type="table",
                title="System Health",
                metric_query="system.*",
                refresh_interval=10,
                config={
                    "columns": ["Component", "Status", "Score", "Last Check"],
                    "status_colors": True,
                },
            ),
        }

        self.widgets.update(default_widgets)
        self._save_dashboard_config()

    def _load_existing_data(self):
        """Load existing metrics and configuration"""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, "r") as f:
                    data = json.load(f)
                    # Load recent metrics (last 24 hours)
                    cutoff = datetime.now() - timedelta(hours=24)
                    for item in data.get("metrics", []):
                        timestamp = datetime.fromisoformat(item["timestamp"])
                        if timestamp > cutoff:
                            metric = MetricPoint(
                                timestamp=timestamp,
                                metric_name=item["metric_name"],
                                metric_type=MetricType(item["metric_type"]),
                                value=item["value"],
                                tags=item.get("tags", {}),
                                metadata=item.get("metadata", {}),
                            )
                            self.live_metrics.append(metric)
        except Exception as e:
            self.logger.warning(f"Could not load existing metrics: {e}")

    def record_metric(
        self,
        metric_name: str,
        value: Union[float, int, str],
        metric_type: MetricType = MetricType.PERFORMANCE,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a new metric point"""
        metric = MetricPoint(
            timestamp=datetime.now(),
            metric_name=metric_name,
            metric_type=metric_type,
            value=value,
            tags=tags or {},
            metadata=metadata or {},
        )

        with self._lock:
            self.live_metrics.append(metric)
            # Keep only last 24 hours in memory
            cutoff = datetime.now() - timedelta(hours=24)
            self.live_metrics = [m for m in self.live_metrics if m.timestamp > cutoff]

        # Save to persistent storage periodically
        if len(self.live_metrics) % 100 == 0:
            self._save_metrics()

        self.logger.debug(f"Recorded metric: {metric_name}={value}")

    def get_metrics(
        self, metric_query: str, time_range: str = "1h", aggregation: str = "raw"
    ) -> List[Dict[str, Any]]:
        """Query metrics with filters and aggregation"""
        # Parse time range
        if time_range.endswith("m"):
            minutes = int(time_range[:-1])
            cutoff = datetime.now() - timedelta(minutes=minutes)
        elif time_range.endswith("h"):
            hours = int(time_range[:-1])
            cutoff = datetime.now() - timedelta(hours=hours)
        elif time_range.endswith("d"):
            days = int(time_range[:-1])
            cutoff = datetime.now() - timedelta(days=days)
        else:
            cutoff = datetime.now() - timedelta(hours=1)  # default 1 hour

        # Filter metrics
        filtered_metrics = []
        with self._lock:
            for metric in self.live_metrics:
                if metric.timestamp >= cutoff:
                    # Simple wildcard matching
                    if (
                        metric_query == "*"
                        or metric_query in metric.metric_name
                        or metric.metric_name.startswith(metric_query.replace("*", ""))
                    ):
                        filtered_metrics.append(metric)

        # Convert to dict format
        result = []
        for metric in filtered_metrics:
            result.append(
                {
                    "timestamp": metric.timestamp.isoformat(),
                    "metric_name": metric.metric_name,
                    "metric_type": metric.metric_type.value,
                    "value": metric.value,
                    "tags": metric.tags,
                    "metadata": metric.metadata,
                }
            )

        # Apply aggregation
        if aggregation != "raw" and result:
            result = self._aggregate_metrics(result, aggregation)

        return result

    def _aggregate_metrics(self, metrics: List[Dict], aggregation: str) -> List[Dict]:
        """Apply aggregation to metrics"""
        if not metrics or aggregation == "raw":
            return metrics

        # Group by metric name
        grouped = {}
        for metric in metrics:
            name = metric["metric_name"]
            if name not in grouped:
                grouped[name] = []
            if isinstance(metric["value"], (int, float)):
                grouped[name].append(metric["value"])

        # Apply aggregation
        result = []
        for name, values in grouped.items():
            if not values:
                continue

            if aggregation == "avg":
                agg_value = statistics.mean(values)
            elif aggregation == "sum":
                agg_value = sum(values)
            elif aggregation == "min":
                agg_value = min(values)
            elif aggregation == "max":
                agg_value = max(values)
            elif aggregation == "count":
                agg_value = len(values)
            else:
                agg_value = values[-1]  # latest

            result.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "metric_name": name,
                    "metric_type": "aggregated",
                    "value": (
                        round(agg_value, 2)
                        if isinstance(agg_value, float)
                        else agg_value
                    ),
                    "tags": {"aggregation": aggregation},
                    "metadata": {"sample_count": len(values)},
                }
            )

        return result

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data for rendering"""
        dashboard_data = {
            "timestamp": datetime.now().isoformat(),
            "system_health": asdict(self.system_health),
            "widgets": {},
        }

        # Get data for each widget
        for widget_id, widget in self.widgets.items():
            try:
                widget_data = self.get_metrics(
                    widget.metric_query,
                    widget.config.get("time_range", "1h"),
                    widget.config.get("aggregation", "raw"),
                )

                dashboard_data["widgets"][widget_id] = {
                    "config": asdict(widget),
                    "data": widget_data,
                    "last_updated": datetime.now().isoformat(),
                }
            except Exception as e:
                self.logger.error(f"Error getting data for widget {widget_id}: {e}")
                dashboard_data["widgets"][widget_id] = {
                    "config": asdict(widget),
                    "data": [],
                    "error": str(e),
                }

        return dashboard_data

    def update_system_health(
        self,
        component_health: Dict[str, float],
        active_alerts: Optional[List[str]] = None,
    ) -> None:
        """Update overall system health status"""
        with self._lock:
            self.system_health.component_health.update(component_health)
            self.system_health.last_check = datetime.now()

            if active_alerts is not None:
                self.system_health.active_alerts = active_alerts

            # Calculate overall score
            if self.system_health.component_health:
                self.system_health.overall_score = statistics.mean(
                    self.system_health.component_health.values()
                )

            # Determine status
            if self.system_health.overall_score >= 0.9:
                self.system_health.status = "healthy"
            elif self.system_health.overall_score >= 0.7:
                self.system_health.status = "degraded"
            else:
                self.system_health.status = "critical"

        # Record as metric
        self.record_metric(
            "system.overall_health",
            self.system_health.overall_score,
            MetricType.SYSTEM,
            tags={"status": self.system_health.status},
        )

    def start_monitoring(self):
        """Start background monitoring thread"""
        if self._monitoring_active:
            return

        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self._monitoring_thread.start()
        self.logger.info("Real-time monitoring started")

    def stop_monitoring(self):
        """Stop background monitoring"""
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        self.logger.info("Real-time monitoring stopped")

    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self._monitoring_active:
            try:
                # Collect system metrics
                self._collect_system_metrics()

                # Save metrics periodically
                self._save_metrics()

                # Sleep for monitoring interval
                time.sleep(30)  # 30 seconds

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Short sleep on error

    def _collect_system_metrics(self):
        """Collect basic system metrics"""
        import psutil
        import sys

        try:
            # Memory usage
            memory = psutil.virtual_memory()
            self.record_metric(
                "system.memory_usage_percent", memory.percent, MetricType.SYSTEM
            )

            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric(
                "system.cpu_usage_percent", cpu_percent, MetricType.SYSTEM
            )

            # Disk usage
            disk = psutil.disk_usage("/")
            self.record_metric(
                "system.disk_usage_percent",
                (disk.used / disk.total) * 100,
                MetricType.SYSTEM,
            )

            # Python process info
            process = psutil.Process()
            self.record_metric(
                "system.process_memory_mb",
                process.memory_info().rss / 1024 / 1024,
                MetricType.SYSTEM,
            )

        except Exception as e:
            self.logger.warning(f"Could not collect system metrics: {e}")

    def _save_metrics(self):
        """Save metrics to persistent storage"""
        try:
            with self._lock:
                data = {"timestamp": datetime.now().isoformat(), "metrics": []}

                for metric in self.live_metrics:
                    data["metrics"].append(
                        {
                            "timestamp": metric.timestamp.isoformat(),
                            "metric_name": metric.metric_name,
                            "metric_type": metric.metric_type.value,
                            "value": metric.value,
                            "tags": metric.tags,
                            "metadata": metric.metadata,
                        }
                    )

                with open(self.metrics_file, "w") as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save metrics: {e}")

    def _save_dashboard_config(self):
        """Save dashboard configuration"""
        try:
            config = {
                "widgets": {k: asdict(v) for k, v in self.widgets.items()},
                "last_updated": datetime.now().isoformat(),
            }

            with open(self.dashboard_config_file, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save dashboard config: {e}")

    def render_dashboard_text(self) -> str:
        """Render dashboard as formatted text for CLI display"""
        lines = []
        lines.append("=" * 80)
        lines.append("🎮 AutoGen DekuDeals - Real-Time Monitoring Dashboard")
        lines.append("=" * 80)
        lines.append("")

        # System Health
        lines.append(f"🏥 SYSTEM HEALTH: {self.system_health.status.upper()}")
        lines.append(f"   Overall Score: {self.system_health.overall_score:.2f}")
        lines.append(
            f"   Last Check: {self.system_health.last_check.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        if self.system_health.active_alerts:
            lines.append(
                f"   🚨 Active Alerts: {len(self.system_health.active_alerts)}"
            )
            for alert in self.system_health.active_alerts[:3]:  # Show first 3
                lines.append(f"     - {alert}")

        lines.append("")

        # Component Health
        if self.system_health.component_health:
            lines.append("🔧 COMPONENT HEALTH:")
            for component, health in self.system_health.component_health.items():
                status_emoji = "✅" if health >= 0.9 else "⚠️" if health >= 0.7 else "❌"
                lines.append(f"   {status_emoji} {component}: {health:.2f}")
            lines.append("")

        # Recent Metrics Summary
        lines.append("📊 RECENT METRICS (Last 1 Hour):")

        # Get some key metrics
        performance_metrics = self.get_metrics("performance.*", "1h", "avg")
        usage_metrics = self.get_metrics("usage.*", "1h", "sum")
        quality_metrics = self.get_metrics("quality.*", "1h", "avg")

        if performance_metrics:
            lines.append("   ⚡ Performance:")
            for metric in performance_metrics[:5]:  # Top 5
                lines.append(f"     - {metric['metric_name']}: {metric['value']}")

        if usage_metrics:
            lines.append("   📈 Usage:")
            for metric in usage_metrics[:5]:  # Top 5
                lines.append(f"     - {metric['metric_name']}: {metric['value']}")

        if quality_metrics:
            lines.append("   ✅ Quality:")
            for metric in quality_metrics[:5]:  # Top 5
                lines.append(f"     - {metric['metric_name']}: {metric['value']}")

        lines.append("")
        lines.append(
            f"📅 Dashboard Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        lines.append("=" * 80)

        return "\n".join(lines)

    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get comprehensive monitoring summary"""
        with self._lock:
            total_metrics = len(self.live_metrics)

            # Metrics by type
            metrics_by_type = {}
            for metric in self.live_metrics:
                metric_type = metric.metric_type.value
                metrics_by_type[metric_type] = metrics_by_type.get(metric_type, 0) + 1

            # Recent activity (last hour)
            recent_cutoff = datetime.now() - timedelta(hours=1)
            recent_metrics = [
                m for m in self.live_metrics if m.timestamp > recent_cutoff
            ]

            return {
                "monitoring_status": (
                    "active" if self._monitoring_active else "inactive"
                ),
                "total_metrics": total_metrics,
                "recent_metrics_count": len(recent_metrics),
                "metrics_by_type": metrics_by_type,
                "system_health": asdict(self.system_health),
                "widgets_count": len(self.widgets),
                "data_retention": "24 hours",
                "last_update": datetime.now().isoformat(),
            }


# ===================================================================
# Utility Functions
# ===================================================================


def create_default_dashboard() -> MonitoringDashboard:
    """Create a default monitoring dashboard instance"""
    dashboard = MonitoringDashboard()
    dashboard.start_monitoring()
    return dashboard


def record_analysis_metrics(
    dashboard: MonitoringDashboard,
    analysis_time: float,
    game_name: str,
    success: bool,
    quality_score: Optional[float] = None,
) -> None:
    """Record metrics for a game analysis"""
    # Performance metrics
    dashboard.record_metric(
        "performance.analysis_time_seconds",
        analysis_time,
        MetricType.PERFORMANCE,
        tags={"game": game_name, "success": str(success)},
    )

    # Usage metrics
    dashboard.record_metric(
        "usage.analysis_count", 1, MetricType.USAGE, tags={"game": game_name}
    )

    # Success/failure
    dashboard.record_metric(
        "usage.success_rate",
        1 if success else 0,
        MetricType.USAGE,
        tags={"outcome": "success" if success else "failure"},
    )

    # Quality metrics
    if quality_score is not None:
        dashboard.record_metric(
            "quality.overall_score",
            quality_score,
            MetricType.QUALITY,
            tags={"game": game_name},
        )


# ===================================================================
# Example Usage
# ===================================================================

if __name__ == "__main__":
    # Create dashboard
    dashboard = create_default_dashboard()

    # Record some sample metrics
    record_analysis_metrics(dashboard, 2.5, "Hollow Knight", True, 0.95)
    record_analysis_metrics(dashboard, 1.8, "Celeste", True, 0.88)

    # Update system health
    dashboard.update_system_health(
        {
            "data_collector": 0.95,
            "price_analyzer": 0.92,
            "review_generator": 0.89,
            "quality_assurance": 0.94,
            "cache_system": 0.98,
        }
    )

    # Display dashboard
    print(dashboard.render_dashboard_text())

    # Get dashboard data
    data = dashboard.get_dashboard_data()
    print("\nDashboard JSON:", json.dumps(data, indent=2)[:500] + "...")

    # Stop monitoring
    dashboard.stop_monitoring()
