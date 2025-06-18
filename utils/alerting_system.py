# ===================================================================
# 🎮 AutoGen DekuDeals - Alerting & Notification System
# Comprehensive automated alerting and notification system
# ===================================================================

import json
import time
import threading
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

# ===================================================================
# Alert Data Models
# ===================================================================


class AlertSeverity(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertCategory(Enum):
    """Alert categories"""

    PERFORMANCE = "performance"
    SYSTEM = "system"
    USAGE = "usage"
    QUALITY = "quality"
    SECURITY = "security"
    BUSINESS = "business"


class AlertStatus(Enum):
    """Alert lifecycle status"""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class NotificationChannel(Enum):
    """Available notification channels"""

    EMAIL = "email"
    WEBHOOK = "webhook"
    LOG = "log"
    FILE = "file"
    CONSOLE = "console"


@dataclass
class AlertRule:
    """Alert rule configuration"""

    rule_id: str
    name: str
    description: str
    category: AlertCategory
    severity: AlertSeverity
    condition: str  # Python expression to evaluate
    threshold_value: float
    comparison_operator: str  # ">", "<", ">=", "<=", "==", "!="
    evaluation_window: int  # minutes
    trigger_count: int  # how many times condition must be true
    cooldown_period: int  # minutes before re-alerting
    enabled: bool
    notification_channels: List[NotificationChannel]
    metadata: Dict[str, Any]


@dataclass
class Alert:
    """Individual alert instance"""

    alert_id: str
    rule_id: str
    title: str
    message: str
    severity: AlertSeverity
    category: AlertCategory
    status: AlertStatus
    created_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    trigger_value: float
    threshold_value: float
    context: Dict[str, Any]
    notifications_sent: List[str]
    metadata: Dict[str, Any]


@dataclass
class NotificationConfig:
    """Notification channel configuration"""

    channel: NotificationChannel
    enabled: bool
    config: Dict[str, Any]  # Channel-specific configuration


@dataclass
class AlertingSummary:
    """Alerting system summary"""

    total_rules: int
    active_rules: int
    total_alerts: int
    active_alerts: int
    alerts_by_severity: Dict[str, int]
    alerts_by_category: Dict[str, int]
    recent_alerts: List[Dict[str, Any]]
    system_health: str
    last_evaluation: datetime


# ===================================================================
# Alerting System
# ===================================================================


class AlertingSystem:
    """
    Comprehensive alerting and notification system

    Features:
    - Configurable alert rules and thresholds
    - Multiple notification channels (email, webhook, log, etc.)
    - Alert lifecycle management (active, acknowledged, resolved)
    - Alert suppression and cooldown periods
    - Performance and system health monitoring
    - Escalation and notification policies
    """

    def __init__(self, data_dir: str = "alerting_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Storage files
        self.rules_file = self.data_dir / "alert_rules.json"
        self.alerts_file = self.data_dir / "alerts.json"
        self.config_file = self.data_dir / "notification_config.json"

        # In-memory storage
        self.alert_rules: Dict[str, AlertRule] = {}
        self.alerts: Dict[str, Alert] = {}
        self.notification_configs: Dict[NotificationChannel, NotificationConfig] = {}

        # Alert evaluation state
        self.last_evaluation: Dict[str, datetime] = {}
        self.trigger_counts: Dict[str, int] = {}
        self.last_notification: Dict[str, datetime] = {}

        # Background monitoring
        self._monitoring_active = False
        self._monitoring_thread: Optional[threading.Thread] = None

        # Thread safety
        self._lock = threading.Lock()

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Load existing data
        self._load_existing_data()
        self._initialize_default_rules()
        self._initialize_default_notifications()

    def _load_existing_data(self):
        """Load existing alerting data"""
        try:
            # Load alert rules
            if self.rules_file.exists():
                with open(self.rules_file, "r") as f:
                    data = json.load(f)
                    for rule_id, rule_data in data.get("rules", {}).items():
                        rule = AlertRule(
                            rule_id=rule_data["rule_id"],
                            name=rule_data["name"],
                            description=rule_data["description"],
                            category=AlertCategory(rule_data["category"]),
                            severity=AlertSeverity(rule_data["severity"]),
                            condition=rule_data["condition"],
                            threshold_value=rule_data["threshold_value"],
                            comparison_operator=rule_data["comparison_operator"],
                            evaluation_window=rule_data["evaluation_window"],
                            trigger_count=rule_data["trigger_count"],
                            cooldown_period=rule_data["cooldown_period"],
                            enabled=rule_data["enabled"],
                            notification_channels=[
                                NotificationChannel(ch)
                                for ch in rule_data["notification_channels"]
                            ],
                            metadata=rule_data.get("metadata", {}),
                        )
                        self.alert_rules[rule_id] = rule

            # Load alerts (last 30 days)
            if self.alerts_file.exists():
                with open(self.alerts_file, "r") as f:
                    data = json.load(f)
                    cutoff = datetime.now() - timedelta(days=30)
                    for alert_id, alert_data in data.get("alerts", {}).items():
                        created_at = datetime.fromisoformat(alert_data["created_at"])
                        if created_at > cutoff:
                            alert = Alert(
                                alert_id=alert_data["alert_id"],
                                rule_id=alert_data["rule_id"],
                                title=alert_data["title"],
                                message=alert_data["message"],
                                severity=AlertSeverity(alert_data["severity"]),
                                category=AlertCategory(alert_data["category"]),
                                status=AlertStatus(alert_data["status"]),
                                created_at=created_at,
                                acknowledged_at=(
                                    datetime.fromisoformat(
                                        alert_data["acknowledged_at"]
                                    )
                                    if alert_data.get("acknowledged_at")
                                    else None
                                ),
                                resolved_at=(
                                    datetime.fromisoformat(alert_data["resolved_at"])
                                    if alert_data.get("resolved_at")
                                    else None
                                ),
                                trigger_value=alert_data["trigger_value"],
                                threshold_value=alert_data["threshold_value"],
                                context=alert_data.get("context", {}),
                                notifications_sent=alert_data.get(
                                    "notifications_sent", []
                                ),
                                metadata=alert_data.get("metadata", {}),
                            )
                            self.alerts[alert_id] = alert

            # Load notification configs
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    for channel_name, config_data in data.get(
                        "notifications", {}
                    ).items():
                        channel = NotificationChannel(channel_name)
                        config = NotificationConfig(
                            channel=channel,
                            enabled=config_data["enabled"],
                            config=config_data["config"],
                        )
                        self.notification_configs[channel] = config

        except Exception as e:
            self.logger.warning(f"Could not load existing alerting data: {e}")

    def _initialize_default_rules(self):
        """Initialize default alert rules"""
        default_rules = [
            {
                "rule_id": "high_error_rate",
                "name": "High Error Rate",
                "description": "Alert when error rate exceeds 10%",
                "category": AlertCategory.QUALITY,
                "severity": AlertSeverity.WARNING,
                "condition": "error_rate > threshold_value",
                "threshold_value": 10.0,
                "comparison_operator": ">",
                "evaluation_window": 15,
                "trigger_count": 2,
                "cooldown_period": 30,
                "notification_channels": [
                    NotificationChannel.LOG,
                    NotificationChannel.CONSOLE,
                ],
            },
            {
                "rule_id": "slow_performance",
                "name": "Slow Performance",
                "description": "Alert when average response time exceeds 10 seconds",
                "category": AlertCategory.PERFORMANCE,
                "severity": AlertSeverity.WARNING,
                "condition": "avg_response_time > threshold_value",
                "threshold_value": 10.0,
                "comparison_operator": ">",
                "evaluation_window": 10,
                "trigger_count": 3,
                "cooldown_period": 15,
                "notification_channels": [
                    NotificationChannel.LOG,
                    NotificationChannel.CONSOLE,
                ],
            },
            {
                "rule_id": "critical_performance",
                "name": "Critical Performance",
                "description": "Alert when any operation takes more than 30 seconds",
                "category": AlertCategory.PERFORMANCE,
                "severity": AlertSeverity.CRITICAL,
                "condition": "max_response_time > threshold_value",
                "threshold_value": 30.0,
                "comparison_operator": ">",
                "evaluation_window": 5,
                "trigger_count": 1,
                "cooldown_period": 10,
                "notification_channels": [
                    NotificationChannel.LOG,
                    NotificationChannel.CONSOLE,
                    NotificationChannel.EMAIL,
                ],
            },
            {
                "rule_id": "high_memory_usage",
                "name": "High Memory Usage",
                "description": "Alert when memory usage exceeds 80%",
                "category": AlertCategory.SYSTEM,
                "severity": AlertSeverity.WARNING,
                "condition": "memory_usage_percent > threshold_value",
                "threshold_value": 80.0,
                "comparison_operator": ">",
                "evaluation_window": 5,
                "trigger_count": 3,
                "cooldown_period": 20,
                "notification_channels": [
                    NotificationChannel.LOG,
                    NotificationChannel.CONSOLE,
                ],
            },
            {
                "rule_id": "system_failure",
                "name": "System Failure",
                "description": "Alert on system failures or crashes",
                "category": AlertCategory.SYSTEM,
                "severity": AlertSeverity.EMERGENCY,
                "condition": "system_failure_count > threshold_value",
                "threshold_value": 0.0,
                "comparison_operator": ">",
                "evaluation_window": 1,
                "trigger_count": 1,
                "cooldown_period": 5,
                "notification_channels": [
                    NotificationChannel.LOG,
                    NotificationChannel.CONSOLE,
                    NotificationChannel.EMAIL,
                ],
            },
        ]

        for rule_data in default_rules:
            if rule_data["rule_id"] not in self.alert_rules:
                rule = AlertRule(
                    rule_id=rule_data["rule_id"],
                    name=rule_data["name"],
                    description=rule_data["description"],
                    category=rule_data["category"],
                    severity=rule_data["severity"],
                    condition=rule_data["condition"],
                    threshold_value=rule_data["threshold_value"],
                    comparison_operator=rule_data["comparison_operator"],
                    evaluation_window=rule_data["evaluation_window"],
                    trigger_count=rule_data["trigger_count"],
                    cooldown_period=rule_data["cooldown_period"],
                    enabled=True,
                    notification_channels=rule_data["notification_channels"],
                    metadata={},
                )
                self.alert_rules[rule_data["rule_id"]] = rule

    def _initialize_default_notifications(self):
        """Initialize default notification configurations"""
        default_configs = {
            NotificationChannel.LOG: {
                "enabled": True,
                "config": {
                    "log_level": "WARNING",
                    "format": "%(asctime)s - ALERT - %(message)s",
                },
            },
            NotificationChannel.CONSOLE: {
                "enabled": True,
                "config": {
                    "colored": True,
                    "format": "[{severity}] {title}: {message}",
                },
            },
            NotificationChannel.FILE: {
                "enabled": True,
                "config": {
                    "file_path": str(self.data_dir / "alerts.log"),
                    "format": "{timestamp} - {severity} - {title}: {message}",
                    "max_size_mb": 10,
                },
            },
            NotificationChannel.EMAIL: {
                "enabled": False,
                "config": {
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "from_email": "",
                    "to_emails": [],
                    "subject_prefix": "[AutoGen DekuDeals Alert]",
                },
            },
            NotificationChannel.WEBHOOK: {
                "enabled": False,
                "config": {
                    "url": "",
                    "method": "POST",
                    "headers": {"Content-Type": "application/json"},
                    "timeout": 10,
                },
            },
        }

        for channel, config_data in default_configs.items():
            if channel not in self.notification_configs:
                config = NotificationConfig(
                    channel=channel,
                    enabled=config_data["enabled"],
                    config=config_data["config"],
                )
                self.notification_configs[channel] = config

    def evaluate_metrics(self, metrics: Dict[str, float]) -> List[str]:
        """Evaluate metrics against alert rules and trigger alerts if needed"""
        triggered_alerts = []

        with self._lock:
            for rule_id, rule in self.alert_rules.items():
                if not rule.enabled:
                    continue

                try:
                    # Check cooldown period
                    if rule_id in self.last_notification:
                        time_since_last = (
                            datetime.now() - self.last_notification[rule_id]
                        )
                        if time_since_last.total_seconds() < rule.cooldown_period * 60:
                            continue

                    # Evaluate condition
                    threshold_value = rule.threshold_value
                    condition_met = self._evaluate_condition(
                        rule.condition, metrics, threshold_value
                    )

                    if condition_met:
                        # Increment trigger count
                        self.trigger_counts[rule_id] = (
                            self.trigger_counts.get(rule_id, 0) + 1
                        )

                        # Check if we should trigger the alert
                        if self.trigger_counts[rule_id] >= rule.trigger_count:
                            alert_id = self._create_alert(rule, metrics)
                            triggered_alerts.append(alert_id)
                            self.trigger_counts[rule_id] = 0  # Reset counter
                            self.last_notification[rule_id] = datetime.now()
                    else:
                        # Reset trigger count if condition not met
                        self.trigger_counts[rule_id] = 0

                except Exception as e:
                    self.logger.error(f"Error evaluating rule {rule_id}: {e}")

        return triggered_alerts

    def _evaluate_condition(
        self, condition: str, metrics: Dict[str, float], threshold_value: float
    ) -> bool:
        """Evaluate alert condition"""
        # Create safe evaluation context
        eval_context = {
            "threshold_value": threshold_value,
            **metrics,  # Add all metrics to context
        }

        try:
            # Replace condition variables
            # Simple condition evaluation for common patterns
            if "error_rate" in condition:
                return eval_context.get("error_rate", 0) > threshold_value
            elif "avg_response_time" in condition:
                return eval_context.get("avg_response_time", 0) > threshold_value
            elif "max_response_time" in condition:
                return eval_context.get("max_response_time", 0) > threshold_value
            elif "memory_usage_percent" in condition:
                return eval_context.get("memory_usage_percent", 0) > threshold_value
            elif "cpu_usage_percent" in condition:
                return eval_context.get("cpu_usage_percent", 0) > threshold_value
            elif "system_failure_count" in condition:
                return eval_context.get("system_failure_count", 0) > threshold_value
            else:
                # Generic evaluation (be careful with eval!)
                return eval(condition, {"__builtins__": {}}, eval_context)
        except Exception as e:
            self.logger.error(f"Error evaluating condition '{condition}': {e}")
            return False

    def _create_alert(self, rule: AlertRule, metrics: Dict[str, float]) -> str:
        """Create and send a new alert"""
        alert_id = f"alert_{int(time.time())}_{rule.rule_id}"

        # Determine trigger value
        trigger_value = 0.0
        if "error_rate" in rule.condition:
            trigger_value = metrics.get("error_rate", 0)
        elif "response_time" in rule.condition:
            trigger_value = metrics.get("avg_response_time", 0) or metrics.get(
                "max_response_time", 0
            )
        elif "memory_usage" in rule.condition:
            trigger_value = metrics.get("memory_usage_percent", 0)
        elif "cpu_usage" in rule.condition:
            trigger_value = metrics.get("cpu_usage_percent", 0)

        # Create alert
        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            title=rule.name,
            message=f"{rule.description}. Current value: {trigger_value:.2f}, Threshold: {rule.threshold_value}",
            severity=rule.severity,
            category=rule.category,
            status=AlertStatus.ACTIVE,
            created_at=datetime.now(),
            acknowledged_at=None,
            resolved_at=None,
            trigger_value=trigger_value,
            threshold_value=rule.threshold_value,
            context={"metrics": metrics, "rule": rule.rule_id},
            notifications_sent=[],
            metadata={},
        )

        self.alerts[alert_id] = alert

        # Send notifications
        self._send_notifications(alert, rule.notification_channels)

        self.logger.warning(f"Alert triggered: {alert.title} (ID: {alert_id})")
        return alert_id

    def _send_notifications(self, alert: Alert, channels: List[NotificationChannel]):
        """Send alert notifications through configured channels"""
        for channel in channels:
            if channel not in self.notification_configs:
                continue

            config = self.notification_configs[channel]
            if not config.enabled:
                continue

            try:
                if channel == NotificationChannel.LOG:
                    self._send_log_notification(alert, config)
                elif channel == NotificationChannel.CONSOLE:
                    self._send_console_notification(alert, config)
                elif channel == NotificationChannel.FILE:
                    self._send_file_notification(alert, config)
                elif channel == NotificationChannel.EMAIL:
                    self._send_email_notification(alert, config)
                elif channel == NotificationChannel.WEBHOOK:
                    self._send_webhook_notification(alert, config)

                alert.notifications_sent.append(channel.value)

            except Exception as e:
                self.logger.error(
                    f"Failed to send notification via {channel.value}: {e}"
                )

    def _send_log_notification(self, alert: Alert, config: NotificationConfig):
        """Send log notification"""
        log_level = config.config.get("log_level", "WARNING")
        message = f"[{alert.severity.value.upper()}] {alert.title}: {alert.message}"

        if log_level == "WARNING":
            self.logger.warning(message)
        elif log_level == "ERROR":
            self.logger.error(message)
        elif log_level == "CRITICAL":
            self.logger.critical(message)
        else:
            self.logger.info(message)

    def _send_console_notification(self, alert: Alert, config: NotificationConfig):
        """Send console notification"""
        colored = config.config.get("colored", True)
        format_str = config.config.get("format", "[{severity}] {title}: {message}")

        message = format_str.format(
            severity=alert.severity.value.upper(),
            title=alert.title,
            message=alert.message,
            timestamp=alert.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        )

        if colored:
            # Add color based on severity
            if alert.severity == AlertSeverity.EMERGENCY:
                message = f"\033[91m{message}\033[0m"  # Red
            elif alert.severity == AlertSeverity.CRITICAL:
                message = f"\033[95m{message}\033[0m"  # Magenta
            elif alert.severity == AlertSeverity.WARNING:
                message = f"\033[93m{message}\033[0m"  # Yellow
            else:
                message = f"\033[94m{message}\033[0m"  # Blue

        print(message)

    def _send_file_notification(self, alert: Alert, config: NotificationConfig):
        """Send file notification"""
        file_path = Path(config.config.get("file_path", "alerts.log"))
        format_str = config.config.get(
            "format", "{timestamp} - {severity} - {title}: {message}"
        )

        message = format_str.format(
            timestamp=alert.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            severity=alert.severity.value.upper(),
            title=alert.title,
            message=alert.message,
        )

        # Append to file
        with open(file_path, "a") as f:
            f.write(message + "\n")

        # Check file size and rotate if needed
        max_size_mb = config.config.get("max_size_mb", 10)
        if file_path.stat().st_size > max_size_mb * 1024 * 1024:
            # Simple rotation: rename current file and start new one
            backup_path = file_path.with_suffix(f".{int(time.time())}.log")
            file_path.rename(backup_path)

    def _send_email_notification(self, alert: Alert, config: NotificationConfig):
        """Send email notification"""
        smtp_config = config.config
        if not smtp_config.get("username") or not smtp_config.get("to_emails"):
            return

        subject = f"{smtp_config.get('subject_prefix', '[Alert]')} {alert.title}"

        body = f"""
Alert Details:
- Title: {alert.title}
- Severity: {alert.severity.value.upper()}
- Category: {alert.category.value}
- Message: {alert.message}
- Triggered: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}
- Trigger Value: {alert.trigger_value}
- Threshold: {alert.threshold_value}

Alert ID: {alert.alert_id}
Rule ID: {alert.rule_id}
        """

        msg = MIMEMultipart()
        msg["From"] = smtp_config["from_email"]
        msg["To"] = ", ".join(smtp_config["to_emails"])
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(smtp_config["smtp_server"], smtp_config["smtp_port"])
        server.starttls()
        server.login(smtp_config["username"], smtp_config["password"])
        server.sendmail(
            smtp_config["from_email"], smtp_config["to_emails"], msg.as_string()
        )
        server.quit()

    def _send_webhook_notification(self, alert: Alert, config: NotificationConfig):
        """Send webhook notification"""
        webhook_config = config.config
        if not webhook_config.get("url"):
            return

        payload = {
            "alert_id": alert.alert_id,
            "rule_id": alert.rule_id,
            "title": alert.title,
            "message": alert.message,
            "severity": alert.severity.value,
            "category": alert.category.value,
            "status": alert.status.value,
            "created_at": alert.created_at.isoformat(),
            "trigger_value": alert.trigger_value,
            "threshold_value": alert.threshold_value,
            "context": alert.context,
        }

        response = requests.post(
            webhook_config["url"],
            json=payload,
            headers=webhook_config.get("headers", {}),
            timeout=webhook_config.get("timeout", 10),
        )
        response.raise_for_status()

    def acknowledge_alert(self, alert_id: str, acknowledger: str = "system") -> bool:
        """Acknowledge an alert"""
        if alert_id not in self.alerts:
            return False

        alert = self.alerts[alert_id]
        if alert.status == AlertStatus.ACTIVE:
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            alert.metadata["acknowledged_by"] = acknowledger
            self._save_data()
            return True

        return False

    def resolve_alert(self, alert_id: str, resolver: str = "system") -> bool:
        """Resolve an alert"""
        if alert_id not in self.alerts:
            return False

        alert = self.alerts[alert_id]
        if alert.status in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]:
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            alert.metadata["resolved_by"] = resolver
            self._save_data()
            return True

        return False

    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return [
            alert
            for alert in self.alerts.values()
            if alert.status == AlertStatus.ACTIVE
        ]

    def get_alerting_summary(self) -> AlertingSummary:
        """Get comprehensive alerting summary"""
        active_alerts = self.get_active_alerts()

        # Count by severity
        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = len(
                [a for a in active_alerts if a.severity == severity]
            )

        # Count by category
        category_counts = {}
        for category in AlertCategory:
            category_counts[category.value] = len(
                [a for a in active_alerts if a.category == category]
            )

        # Recent alerts (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_alerts = [
            {
                "alert_id": alert.alert_id,
                "title": alert.title,
                "severity": alert.severity.value,
                "status": alert.status.value,
                "created_at": alert.created_at.isoformat(),
            }
            for alert in self.alerts.values()
            if alert.created_at > recent_cutoff
        ]
        recent_alerts.sort(key=lambda x: x["created_at"], reverse=True)

        # System health
        critical_alerts = len(
            [
                a
                for a in active_alerts
                if a.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]
            ]
        )
        if critical_alerts > 0:
            system_health = "critical"
        elif len(active_alerts) > 5:
            system_health = "degraded"
        else:
            system_health = "healthy"

        return AlertingSummary(
            total_rules=len(self.alert_rules),
            active_rules=len([r for r in self.alert_rules.values() if r.enabled]),
            total_alerts=len(self.alerts),
            active_alerts=len(active_alerts),
            alerts_by_severity=severity_counts,
            alerts_by_category=category_counts,
            recent_alerts=recent_alerts[:20],  # Last 20
            system_health=system_health,
            last_evaluation=datetime.now(),
        )

    def _save_data(self):
        """Save alerting data to disk"""
        try:
            # Save alert rules
            rules_data = {"timestamp": datetime.now().isoformat(), "rules": {}}

            for rule_id, rule in self.alert_rules.items():
                rules_data["rules"][rule_id] = {
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "description": rule.description,
                    "category": rule.category.value,
                    "severity": rule.severity.value,
                    "condition": rule.condition,
                    "threshold_value": rule.threshold_value,
                    "comparison_operator": rule.comparison_operator,
                    "evaluation_window": rule.evaluation_window,
                    "trigger_count": rule.trigger_count,
                    "cooldown_period": rule.cooldown_period,
                    "enabled": rule.enabled,
                    "notification_channels": [
                        ch.value for ch in rule.notification_channels
                    ],
                    "metadata": rule.metadata,
                }

            with open(self.rules_file, "w") as f:
                json.dump(rules_data, f, indent=2)

            # Save alerts
            alerts_data = {"timestamp": datetime.now().isoformat(), "alerts": {}}

            for alert_id, alert in self.alerts.items():
                alerts_data["alerts"][alert_id] = {
                    "alert_id": alert.alert_id,
                    "rule_id": alert.rule_id,
                    "title": alert.title,
                    "message": alert.message,
                    "severity": alert.severity.value,
                    "category": alert.category.value,
                    "status": alert.status.value,
                    "created_at": alert.created_at.isoformat(),
                    "acknowledged_at": (
                        alert.acknowledged_at.isoformat()
                        if alert.acknowledged_at
                        else None
                    ),
                    "resolved_at": (
                        alert.resolved_at.isoformat() if alert.resolved_at else None
                    ),
                    "trigger_value": alert.trigger_value,
                    "threshold_value": alert.threshold_value,
                    "context": alert.context,
                    "notifications_sent": alert.notifications_sent,
                    "metadata": alert.metadata,
                }

            with open(self.alerts_file, "w") as f:
                json.dump(alerts_data, f, indent=2)

            # Save notification configs
            config_data = {"timestamp": datetime.now().isoformat(), "notifications": {}}

            for channel, config in self.notification_configs.items():
                config_data["notifications"][channel.value] = {
                    "enabled": config.enabled,
                    "config": config.config,
                }

            with open(self.config_file, "w") as f:
                json.dump(config_data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Could not save alerting data: {e}")


# ===================================================================
# Global Alerting System Instance
# ===================================================================

# Create a global instance for easy use
_global_alerting: Optional[AlertingSystem] = None


def get_alerting_system() -> AlertingSystem:
    """Get or create global alerting system instance"""
    global _global_alerting
    if _global_alerting is None:
        _global_alerting = AlertingSystem()
    return _global_alerting


def evaluate_alerts(metrics: Dict[str, float]) -> List[str]:
    """Evaluate metrics and trigger alerts using global system"""
    return get_alerting_system().evaluate_metrics(metrics)


# ===================================================================
# Example Usage
# ===================================================================

if __name__ == "__main__":
    # Create alerting system
    alerting = AlertingSystem()

    # Test metrics that would trigger alerts
    test_metrics = {
        "error_rate": 15.0,  # Should trigger high error rate alert
        "avg_response_time": 12.0,  # Should trigger slow performance alert
        "memory_usage_percent": 85.0,  # Should trigger high memory alert
        "cpu_usage_percent": 45.0,
        "system_failure_count": 0,
    }

    # Evaluate metrics
    triggered = alerting.evaluate_metrics(test_metrics)
    print(f"Triggered alerts: {triggered}")

    # Get summary
    summary = alerting.get_alerting_summary()
    print("\nAlerting Summary:", json.dumps(asdict(summary), indent=2, default=str))

    # Acknowledge an alert
    if triggered:
        alerting.acknowledge_alert(triggered[0], "admin")
        print(f"Acknowledged alert: {triggered[0]}")

    # Save data
    alerting._save_data()
