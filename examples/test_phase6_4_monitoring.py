#!/usr/bin/env python3
# ===================================================================
# 🎮 AutoGen DekuDeals - Phase 6.4 Monitoring & Analytics Test
# Comprehensive testing of monitoring and analytics systems
# ===================================================================

import json
import time
import asyncio
from datetime import datetime
from typing import Dict, List
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test framework
print("=" * 80)
print("🔍 AUTOGEN DEKUDEALS - PHASE 6.4 MONITORING & ANALYTICS TEST")
print("=" * 80)
print()


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'=' * 60}")
    print(f"🧪 {title}")
    print(f"{'=' * 60}")


def print_status(message: str, success: bool = True):
    """Print status message"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")


def print_info(message: str):
    """Print info message"""
    print(f"🔍 {message}")


def print_result(data: Dict, max_lines: int = 10):
    """Print formatted result data"""
    result_json = json.dumps(data, indent=2, default=str)
    lines = result_json.split("\n")

    if len(lines) <= max_lines:
        print(result_json)
    else:
        print("\n".join(lines[: max_lines // 2]))
        print(f"... ({len(lines) - max_lines} lines truncated) ...")
        print("\n".join(lines[-max_lines // 2 :]))


# ===================================================================
# Phase 6.4 Monitoring & Analytics Tests
# ===================================================================


def test_monitoring_dashboard():
    """Test real-time monitoring dashboard"""
    print_section("MONITORING DASHBOARD TEST")

    try:
        from utils.monitoring_dashboard import (
            create_default_dashboard,
            record_analysis_metrics,
        )

        print_info("Creating monitoring dashboard...")
        dashboard = create_default_dashboard()

        print_info("Recording sample metrics...")
        # Record some test metrics
        record_analysis_metrics(dashboard, 2.5, "Hollow Knight", True, 0.95)
        record_analysis_metrics(dashboard, 1.8, "Celeste", True, 0.92)
        record_analysis_metrics(dashboard, 3.2, "INSIDE", True, 0.88)
        record_analysis_metrics(dashboard, 0.9, "Moving Out", True, 0.85)

        print_info("Updating system health...")
        dashboard.update_system_health(
            {
                "data_collector": 0.95,
                "price_analyzer": 0.92,
                "review_generator": 0.89,
                "quality_assurance": 0.94,
                "cache_system": 0.98,
            }
        )

        print_info("Getting dashboard data...")
        dashboard_data = dashboard.get_dashboard_data()

        print_info("Getting monitoring summary...")
        summary = dashboard.get_monitoring_summary()

        print_status("Monitoring dashboard test completed successfully!")
        print("\n📊 DASHBOARD SUMMARY:")
        print_result(
            {
                "system_status": dashboard_data["system_health"]["status"],
                "overall_score": dashboard_data["system_health"]["overall_score"],
                "total_metrics": summary["total_metrics"],
                "widgets_count": summary["widgets_count"],
                "monitoring_status": summary["monitoring_status"],
            }
        )

        # Test text rendering
        print("\n📋 DASHBOARD TEXT RENDER:")
        print(dashboard.render_dashboard_text())

        return True

    except Exception as e:
        print_status(f"Monitoring dashboard test failed: {e}", False)
        return False


def test_performance_monitoring():
    """Test performance monitoring system"""
    print_section("PERFORMANCE MONITORING TEST")

    try:
        from utils.performance_monitor import PerformanceMonitor, monitor_performance

        print_info("Creating performance monitor...")
        monitor = PerformanceMonitor()

        print_info("Testing performance decorator...")

        @monitor.performance_decorator("test_function")
        def test_function(duration: float = 1.0):
            time.sleep(duration)
            return f"Completed in {duration}s"

        # Run some test functions
        test_function(0.5)
        test_function(2.0)
        test_function(0.1)
        test_function(1.5)

        print_info("Recording manual performance metrics...")
        monitor.record_performance(
            function_name="manual_test",
            execution_time=3.2,
            success=True,
            tags={"type": "manual", "category": "test"},
        )

        monitor.record_performance(
            function_name="slow_operation",
            execution_time=8.5,
            success=False,
            error_message="Timeout error",
            tags={"type": "automated"},
        )

        print_info("Getting performance summary...")
        summary = monitor.get_performance_summary("1h")

        print_info("Identifying bottlenecks...")
        bottlenecks = monitor.get_bottlenecks(5)

        print_status("Performance monitoring test completed successfully!")
        print("\n⚡ PERFORMANCE SUMMARY:")
        print_result(
            {
                "total_metrics": summary["total_metrics"],
                "avg_execution_time": summary["overall_stats"]["avg_execution_time"],
                "success_rate": summary["overall_stats"]["success_rate"],
                "bottlenecks_found": len(bottlenecks),
                "performance_profiles": summary["performance_profiles"],
            }
        )

        if bottlenecks:
            print("\n🚨 TOP BOTTLENECKS:")
            for i, bottleneck in enumerate(bottlenecks[:3], 1):
                print(
                    f"  {i}. {bottleneck['function_name']}: {bottleneck['bottleneck_score']:.2f}"
                )
                for rec in bottleneck["recommendations"][:2]:
                    print(f"     - {rec}")

        return True

    except Exception as e:
        print_status(f"Performance monitoring test failed: {e}", False)
        return False


def test_usage_analytics():
    """Test usage analytics system"""
    print_section("USAGE ANALYTICS TEST")

    try:
        from utils.usage_analytics import UsageAnalytics, EventType

        print_info("Creating usage analytics...")
        analytics = UsageAnalytics()

        print_info("Tracking sample events...")

        # Track various events
        analytics.track_event(
            event_type=EventType.GAME_ANALYSIS,
            success=True,
            execution_time=2.5,
            game_name="Hollow Knight",
            command="analyze",
            parameters={"type": "comprehensive"},
        )

        analytics.track_event(
            event_type=EventType.BATCH_ANALYSIS,
            success=True,
            execution_time=15.2,
            command="batch_analyze",
            parameters={"games": ["INSIDE", "Celeste", "Moving Out"]},
        )

        analytics.track_event(
            event_type=EventType.QUICK_ANALYSIS,
            success=True,
            execution_time=1.8,
            game_name="Celeste",
            command="quick_analyze",
        )

        analytics.track_event(
            event_type=EventType.CACHE_HIT,
            success=True,
            execution_time=0.1,
            game_name="Stardew Valley",
        )

        analytics.track_event(
            event_type=EventType.ERROR,
            success=False,
            execution_time=5.0,
            error_message="Network timeout",
            command="scrape_game",
        )

        print_info("Getting usage statistics...")
        usage_stats = analytics.get_usage_statistics("1d")

        print_info("Getting user insights...")
        user_insights = analytics.get_user_insights()

        print_info("Getting analytics summary...")
        summary = analytics.get_analytics_summary()

        print_status("Usage analytics test completed successfully!")
        print("\n📈 USAGE STATISTICS:")
        print_result(
            {
                "total_users": usage_stats.total_users,
                "total_sessions": usage_stats.total_sessions,
                "total_events": usage_stats.total_events,
                "unique_games": usage_stats.unique_games_analyzed,
                "error_rate": usage_stats.error_rate,
                "cache_hit_rate": usage_stats.cache_hit_rate,
                "most_popular_games": usage_stats.most_popular_games[:3],
                "user_segments": usage_stats.user_segments,
            }
        )

        print("\n👤 USER INSIGHTS:")
        print_result(
            {
                "user_id": user_insights.get("user_id", "unknown"),
                "total_events": user_insights.get("activity_summary", {}).get(
                    "total_events", 0
                ),
                "events_per_day": user_insights.get("activity_summary", {}).get(
                    "events_per_day", 0
                ),
                "behavior_patterns": user_insights.get("behavior_patterns", {}),
                "time_patterns": user_insights.get("time_patterns", {}),
            }
        )

        # End session
        analytics.end_session()

        return True

    except Exception as e:
        print_status(f"Usage analytics test failed: {e}", False)
        return False


def test_alerting_system():
    """Test alerting and notification system"""
    print_section("ALERTING SYSTEM TEST")

    try:
        from utils.alerting_system import AlertingSystem

        print_info("Creating alerting system...")
        alerting = AlertingSystem()

        print_info("Testing alert rule evaluation...")

        # Test metrics that should trigger alerts
        test_metrics = {
            "error_rate": 15.0,  # Should trigger high error rate alert
            "avg_response_time": 12.0,  # Should trigger slow performance alert
            "memory_usage_percent": 85.0,  # Should trigger high memory alert
            "cpu_usage_percent": 45.0,
            "system_failure_count": 0,
            "max_response_time": 8.0,
        }

        print_info("Evaluating metrics against alert rules...")
        triggered_alerts = alerting.evaluate_metrics(test_metrics)

        print_info("Getting alerting summary...")
        summary = alerting.get_alerting_summary()

        print_info("Getting active alerts...")
        active_alerts = alerting.get_active_alerts()

        print_status(
            f"Alerting system test completed! Triggered {len(triggered_alerts)} alerts"
        )
        print("\n🚨 ALERTING SUMMARY:")
        print_result(
            {
                "triggered_alerts": len(triggered_alerts),
                "total_rules": summary.total_rules,
                "active_rules": summary.active_rules,
                "active_alerts": summary.active_alerts,
                "system_health": summary.system_health,
                "alerts_by_severity": summary.alerts_by_severity,
                "alerts_by_category": summary.alerts_by_category,
            }
        )

        if active_alerts:
            print("\n🔴 ACTIVE ALERTS:")
            for alert in active_alerts[:3]:  # Show first 3
                print(f"  - [{alert.severity.value.upper()}] {alert.title}")
                print(f"    {alert.message}")
                print(f"    Created: {alert.created_at.strftime('%H:%M:%S')}")

        # Test alert acknowledgment
        if triggered_alerts:
            print_info(f"Acknowledging alert: {triggered_alerts[0]}")
            alerting.acknowledge_alert(triggered_alerts[0], "test_user")

        return True

    except Exception as e:
        print_status(f"Alerting system test failed: {e}", False)
        return False


def test_agent_tools_integration():
    """Test monitoring tools integration with agent_tools"""
    print_section("AGENT TOOLS INTEGRATION TEST")

    try:
        # Import agent tools functions
        from agent_tools import (
            get_monitoring_dashboard_data,
            get_performance_monitoring_summary,
            get_usage_analytics_summary,
            evaluate_system_alerts,
            get_comprehensive_monitoring_overview,
        )

        print_info("Testing monitoring dashboard tool...")
        dashboard_result = get_monitoring_dashboard_data("1h")

        print_info("Testing performance monitoring tool...")
        performance_result = get_performance_monitoring_summary("24h")

        print_info("Testing usage analytics tool...")
        usage_result = get_usage_analytics_summary("7d")

        print_info("Testing alerting system tool...")
        test_metrics = {
            "error_rate": 8.0,
            "avg_response_time": 4.5,
            "memory_usage_percent": 70.0,
        }
        alerts_result = evaluate_system_alerts(test_metrics)

        print_info("Testing comprehensive monitoring overview...")
        overview_result = get_comprehensive_monitoring_overview()

        # Check results
        tools_tested = 0
        tools_successful = 0

        for tool_name, result in [
            ("Dashboard", dashboard_result),
            ("Performance", performance_result),
            ("Usage Analytics", usage_result),
            ("Alerts", alerts_result),
            ("Overview", overview_result),
        ]:
            tools_tested += 1
            if result.get("success", False):
                tools_successful += 1
                print_status(f"{tool_name} tool: SUCCESS")
            else:
                print_status(
                    f"{tool_name} tool: FAILED - {result.get('error', 'Unknown error')}",
                    False,
                )

        print_status(
            f"Agent tools integration test completed: {tools_successful}/{tools_tested} tools successful!"
        )

        if overview_result.get("success"):
            print("\n🌟 COMPREHENSIVE OVERVIEW:")
            overview = overview_result["monitoring_overview"]
            print_result(
                {
                    "overall_health_score": overview["overall_health_score"],
                    "overall_status": overview["overall_status"],
                    "systems_operational": overview["systems_operational"],
                    "recommendations_count": len(
                        overview_result.get("comprehensive_recommendations", [])
                    ),
                }
            )

            print("\n💡 TOP RECOMMENDATIONS:")
            for i, rec in enumerate(
                overview_result.get("comprehensive_recommendations", [])[:3], 1
            ):
                print(f"  {i}. {rec}")

        return tools_successful == tools_tested

    except Exception as e:
        print_status(f"Agent tools integration test failed: {e}", False)
        return False


def test_system_integration():
    """Test integration between all monitoring systems"""
    print_section("SYSTEM INTEGRATION TEST")

    try:
        print_info("Testing cross-system data flow...")

        # Import all systems
        from utils.monitoring_dashboard import (
            create_default_dashboard,
            record_analysis_metrics,
        )
        from utils.performance_monitor import get_performance_monitor
        from utils.usage_analytics import get_usage_analytics, EventType
        from utils.alerting_system import get_alerting_system

        # Create all systems
        dashboard = create_default_dashboard()
        performance = get_performance_monitor()
        analytics = get_usage_analytics()
        alerting = get_alerting_system()

        print_info("Simulating user activity...")

        # Simulate a complete user session
        games_to_analyze = ["Hollow Knight", "Celeste", "INSIDE"]

        for i, game in enumerate(games_to_analyze):
            print_info(f"Analyzing game {i+1}/{len(games_to_analyze)}: {game}")

            # Record performance metrics
            execution_time = 2.0 + i * 0.5  # Varying execution times
            success = i < len(games_to_analyze) - 1  # Last one fails

            with performance.measure_performance(
                f"analyze_{game.lower().replace(' ', '_')}",
                tags={"game": game, "session": "integration_test"},
            ):
                time.sleep(execution_time * 0.1)  # Simulate work (faster for testing)

            # Record dashboard metrics
            record_analysis_metrics(
                dashboard, execution_time, game, success, 0.9 - i * 0.1
            )

            # Track usage analytics
            analytics.track_event(
                event_type=EventType.GAME_ANALYSIS,
                success=success,
                execution_time=execution_time,
                game_name=game,
                command="comprehensive_analyze",
                parameters={"quality_threshold": 0.8},
            )

        print_info("Evaluating system health...")

        # Update system components health
        dashboard.update_system_health(
            {
                "data_collector": 0.95,
                "price_analyzer": 0.92,
                "review_generator": 0.89,
                "quality_assurance": 0.94,
                "cache_system": 0.98,
            }
        )

        # Check for alerts
        system_metrics = {
            "error_rate": 33.3,  # 1 out of 3 failed
            "avg_response_time": 2.5,
            "memory_usage_percent": 75.0,
            "cpu_usage_percent": 60.0,
        }

        triggered_alerts = alerting.evaluate_metrics(system_metrics)

        print_info("Collecting integrated results...")

        # Get results from all systems
        dashboard_summary = dashboard.get_monitoring_summary()
        performance_summary = performance.get_performance_summary("1h")
        usage_stats = analytics.get_usage_statistics("1h")
        alert_summary = alerting.get_alerting_summary()

        print_status("System integration test completed successfully!")

        print("\n🔗 INTEGRATION RESULTS:")
        integration_results = {
            "dashboard_metrics": dashboard_summary["total_metrics"],
            "performance_profiles": len(
                performance_summary.get("function_performance", {})
            ),
            "usage_events": usage_stats.total_events,
            "triggered_alerts": len(triggered_alerts),
            "overall_health": dashboard_summary["system_health"]["overall_score"],
            "error_correlation": {
                "performance_errors": sum(
                    1
                    for stats in performance_summary.get(
                        "function_performance", {}
                    ).values()
                    if stats.get("error_rate", 0) > 0
                ),
                "usage_error_rate": usage_stats.error_rate,
                "alerts_triggered": len(triggered_alerts),
            },
        }

        print_result(integration_results)

        # Check correlation
        if usage_stats.error_rate > 20 and len(triggered_alerts) > 0:
            print_status(
                "✨ Cross-system correlation detected: High error rate triggered alerts!"
            )

        return True

    except Exception as e:
        print_status(f"System integration test failed: {e}", False)
        return False


# ===================================================================
# Main Test Execution
# ===================================================================


def main():
    """Run all Phase 6.4 tests"""
    print_info("Starting Phase 6.4 Monitoring & Analytics comprehensive test suite...")

    tests = [
        ("Monitoring Dashboard", test_monitoring_dashboard),
        ("Performance Monitoring", test_performance_monitoring),
        ("Usage Analytics", test_usage_analytics),
        ("Alerting System", test_alerting_system),
        ("Agent Tools Integration", test_agent_tools_integration),
        ("System Integration", test_system_integration),
    ]

    results = []
    start_time = time.time()

    for test_name, test_func in tests:
        print_info(f"Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_status(f"{test_name} test crashed: {e}", False)
            results.append((test_name, False))

    end_time = time.time()
    total_time = end_time - start_time

    # Print final results
    print_section("FINAL TEST RESULTS")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"📊 Test Summary:")
    print(f"   Total Tests: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")
    print(f"   Total Time: {total_time:.2f}s")
    print()

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")

    print()
    if passed == total:
        print(
            "🎉 ALL TESTS PASSED! Phase 6.4 Monitoring & Analytics system is fully operational!"
        )
        print()
        print(
            "🚀 Ready for production deployment with comprehensive monitoring capabilities:"
        )
        print("   • Real-time monitoring dashboard")
        print("   • Advanced performance monitoring (APM)")
        print("   • User behavior analytics")
        print("   • Automated alerting system")
        print("   • Integrated cross-system insights")
    else:
        print(
            f"⚠️  {total - passed} test(s) failed. Please investigate and fix issues before deployment."
        )

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
