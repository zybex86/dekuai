"""
PHASE 4 Point 4: Quality Metrics Tracking
FAZA 4 Punkt 4: Śledzenie metryki jakości

Advanced quality metrics collection, analysis, and tracking system
with performance monitoring and improvement insights.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Typy metryki"""

    QUALITY_SCORE = "quality_score"  # Ogólny wynik jakości
    COMPLETENESS = "completeness"  # Kompletność danych
    CONSISTENCY = "consistency"  # Spójność analiz
    PERFORMANCE = "performance"  # Wydajność systemowa
    USER_SATISFACTION = "user_satisfaction"  # Satysfakcja użytkownika
    ACCURACY = "accuracy"  # Dokładność predykcji


class MetricCategory(Enum):
    """Kategorie metryki"""

    DATA_QUALITY = "data_quality"  # Jakość danych
    ANALYSIS_QUALITY = "analysis_quality"  # Jakość analiz
    SYSTEM_PERFORMANCE = "system_performance"  # Wydajność systemu
    USER_EXPERIENCE = "user_experience"  # Doświadczenie użytkownika


@dataclass
class QualityMetric:
    """Metryka jakości"""

    metric_id: str
    metric_type: MetricType
    category: MetricCategory
    value: float
    target_value: float
    unit: str
    timestamp: datetime
    game_name: str
    analysis_phase: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricTrend:
    """Trend metryki"""

    metric_type: MetricType
    values: List[float]
    timestamps: List[datetime]
    trend_direction: str  # "improving", "declining", "stable"
    change_rate: float
    confidence: float


@dataclass
class QualityReport:
    """Raport jakości z metrykami"""

    report_id: str
    game_name: str
    analysis_timestamp: datetime
    overall_quality_score: float
    metrics: List[QualityMetric]
    trend_analysis: List[MetricTrend]
    recommendations: List[str]
    benchmark_comparison: Dict[str, float]


class QualityMetricsCollector:
    """Kolektor metryki jakości"""

    def __init__(self):
        self.metric_counter = 0

        # Define metric specifications
        self.metric_specs = {
            MetricType.QUALITY_SCORE: {
                "target": 0.85,
                "unit": "score",
                "weight": 1.0,
                "description": "Overall analysis quality score",
            },
            MetricType.COMPLETENESS: {
                "target": 0.90,
                "unit": "ratio",
                "weight": 0.8,
                "description": "Data completeness ratio",
            },
            MetricType.CONSISTENCY: {
                "target": 0.95,
                "unit": "ratio",
                "weight": 0.7,
                "description": "Cross-module consistency",
            },
            MetricType.PERFORMANCE: {
                "target": 30.0,
                "unit": "seconds",
                "weight": 0.5,
                "description": "Analysis completion time",
            },
        }

        logger.info("✅ Quality Metrics Collector initialized")

    def collect_quality_metrics(
        self, analysis_results: Dict[str, Any]
    ) -> List[QualityMetric]:
        """Zbiera metryki jakości z wyników analizy"""

        metrics = []
        game_name = analysis_results.get("game_name", "Unknown")

        try:
            # Quality Score Metric
            qa_report = analysis_results.get("qa_report", {})
            if qa_report:
                quality_score = qa_report.get("overall_score", 0.0)
                metrics.append(
                    self._create_metric(
                        MetricType.QUALITY_SCORE,
                        MetricCategory.ANALYSIS_QUALITY,
                        quality_score,
                        game_name,
                        "quality_validation",
                        {"qa_level": qa_report.get("quality_level")},
                    )
                )

            # Completeness Metric
            completeness_report = analysis_results.get("completeness_report", {})
            if completeness_report:
                completeness_score = completeness_report.get("overall_score", 0.0)
                metrics.append(
                    self._create_metric(
                        MetricType.COMPLETENESS,
                        MetricCategory.DATA_QUALITY,
                        completeness_score,
                        game_name,
                        "data_validation",
                        {
                            "present_fields": completeness_report.get(
                                "present_fields", 0
                            ),
                            "total_fields": completeness_report.get("total_fields", 0),
                        },
                    )
                )

            # Consistency Metric (calculated from analysis)
            consistency_score = self._calculate_consistency_score(analysis_results)
            if consistency_score is not None:
                metrics.append(
                    self._create_metric(
                        MetricType.CONSISTENCY,
                        MetricCategory.ANALYSIS_QUALITY,
                        consistency_score,
                        game_name,
                        "consistency_validation",
                    )
                )

            # Performance Metric
            analysis_time = analysis_results.get("analysis_time_seconds")
            if analysis_time is not None:
                metrics.append(
                    self._create_metric(
                        MetricType.PERFORMANCE,
                        MetricCategory.SYSTEM_PERFORMANCE,
                        analysis_time,
                        game_name,
                        "performance_tracking",
                        {
                            "analysis_phases": analysis_results.get(
                                "completed_phases", []
                            )
                        },
                    )
                )

            logger.info(f"📊 Collected {len(metrics)} quality metrics for {game_name}")
            return metrics

        except Exception as e:
            logger.error(f"❌ Error collecting metrics: {str(e)}")
            return []

    def collect_user_feedback_metrics(
        self, user_feedback: Dict[str, Any]
    ) -> List[QualityMetric]:
        """Zbiera metryki z feedbacku użytkownika"""

        metrics = []

        try:
            # User satisfaction score
            satisfaction = user_feedback.get("satisfaction_score")
            if satisfaction is not None:
                metrics.append(
                    self._create_metric(
                        MetricType.USER_SATISFACTION,
                        MetricCategory.USER_EXPERIENCE,
                        satisfaction,
                        user_feedback.get("game_name", "Unknown"),
                        "user_feedback",
                        {
                            "feedback_text": user_feedback.get("feedback_text", ""),
                            "recommendation_helpful": user_feedback.get(
                                "recommendation_helpful", False
                            ),
                        },
                    )
                )

            # Accuracy feedback (if user bought the game)
            purchase_decision = user_feedback.get("purchase_decision")
            recommendation = user_feedback.get("system_recommendation", "")

            if purchase_decision is not None and recommendation:
                # Calculate accuracy based on recommendation alignment
                accuracy = self._calculate_recommendation_accuracy(
                    purchase_decision, recommendation
                )
                metrics.append(
                    self._create_metric(
                        MetricType.ACCURACY,
                        MetricCategory.ANALYSIS_QUALITY,
                        accuracy,
                        user_feedback.get("game_name", "Unknown"),
                        "recommendation_tracking",
                        {
                            "purchase_decision": purchase_decision,
                            "system_recommendation": recommendation,
                        },
                    )
                )

            logger.info(f"👤 Collected {len(metrics)} user feedback metrics")
            return metrics

        except Exception as e:
            logger.error(f"❌ Error collecting user feedback metrics: {str(e)}")
            return []

    def _create_metric(
        self,
        metric_type: MetricType,
        category: MetricCategory,
        value: float,
        game_name: str,
        analysis_phase: str,
        metadata: Dict[str, Any] = None,
    ) -> QualityMetric:
        """Tworzy metrykę jakości"""

        self.metric_counter += 1
        spec = self.metric_specs.get(metric_type, {})

        return QualityMetric(
            metric_id=f"qm_{self.metric_counter:06d}",
            metric_type=metric_type,
            category=category,
            value=value,
            target_value=spec.get("target", 1.0),
            unit=spec.get("unit", "units"),
            timestamp=datetime.now(),
            game_name=game_name,
            analysis_phase=analysis_phase,
            metadata=metadata or {},
        )

    def _calculate_consistency_score(
        self, analysis_results: Dict[str, Any]
    ) -> Optional[float]:
        """Oblicza wynik spójności między modułami"""

        try:
            # Extract recommendations from different modules
            value_rec = analysis_results.get("value_analysis", {}).get(
                "recommendation", ""
            )
            review_rec = analysis_results.get("review", {}).get("recommendation", "")

            if not value_rec or not review_rec:
                return None

            # Simple consistency check - are recommendations aligned?
            value_buy = any(
                word in value_rec.upper() for word in ["BUY", "INSTANT", "STRONG"]
            )
            value_skip = any(
                word in value_rec.upper() for word in ["SKIP", "AVOID", "WAIT"]
            )

            review_buy = any(
                word in review_rec.upper() for word in ["BUY", "RECOMMEND", "EXCELLENT"]
            )
            review_skip = any(
                word in review_rec.upper() for word in ["SKIP", "AVOID", "POOR"]
            )

            # Check alignment
            if (value_buy and review_buy) or (value_skip and review_skip):
                return 1.0  # Perfect consistency
            elif (value_buy and review_skip) or (value_skip and review_buy):
                return 0.0  # Complete inconsistency
            else:
                return 0.5  # Neutral/unclear

        except Exception as e:
            logger.error(f"❌ Error calculating consistency: {str(e)}")
            return None

    def _calculate_recommendation_accuracy(
        self, purchase_decision: bool, recommendation: str
    ) -> float:
        """Oblicza dokładność rekomendacji na podstawie decyzji użytkownika"""

        try:
            rec_suggests_buy = any(
                word in recommendation.upper()
                for word in ["BUY", "INSTANT", "STRONG", "RECOMMEND"]
            )

            # Perfect prediction
            if (purchase_decision and rec_suggests_buy) or (
                not purchase_decision and not rec_suggests_buy
            ):
                return 1.0
            else:
                return 0.0

        except:
            return 0.5  # Unknown/neutral


class QualityMetricsAnalyzer:
    """Analizator trendów metryki jakości"""

    def __init__(self):
        self.metrics_history: List[QualityMetric] = []
        logger.info("✅ Quality Metrics Analyzer initialized")

    def add_metrics(self, metrics: List[QualityMetric]):
        """Dodaje metryki do historii"""
        self.metrics_history.extend(metrics)
        logger.info(f"📈 Added {len(metrics)} metrics to history")

    def analyze_trends(
        self, metric_type: MetricType, days_back: int = 30
    ) -> Optional[MetricTrend]:
        """Analizuje trendy dla określonej metryki"""

        try:
            # Filter metrics by type and timeframe
            cutoff_date = datetime.now() - timedelta(days=days_back)
            relevant_metrics = [
                m
                for m in self.metrics_history
                if m.metric_type == metric_type and m.timestamp >= cutoff_date
            ]

            if len(relevant_metrics) < 2:
                return None

            # Sort by timestamp
            relevant_metrics.sort(key=lambda m: m.timestamp)

            values = [m.value for m in relevant_metrics]
            timestamps = [m.timestamp for m in relevant_metrics]

            # Calculate trend
            trend_direction = self._calculate_trend_direction(values)
            change_rate = self._calculate_change_rate(values)
            confidence = self._calculate_confidence(values)

            return MetricTrend(
                metric_type=metric_type,
                values=values,
                timestamps=timestamps,
                trend_direction=trend_direction,
                change_rate=change_rate,
                confidence=confidence,
            )

        except Exception as e:
            logger.error(f"❌ Error analyzing trends: {str(e)}")
            return None

    def generate_quality_insights(
        self, recent_metrics: List[QualityMetric]
    ) -> Dict[str, Any]:
        """Generuje wglądy w jakość na podstawie metryki"""

        insights = {
            "overall_assessment": "",
            "strengths": [],
            "areas_for_improvement": [],
            "trend_summary": {},
            "recommendations": [],
        }

        try:
            if not recent_metrics:
                insights["overall_assessment"] = "No metrics available for analysis"
                return insights

            # Group metrics by type
            metrics_by_type = {}
            for metric in recent_metrics:
                metric_type = metric.metric_type
                if metric_type not in metrics_by_type:
                    metrics_by_type[metric_type] = []
                metrics_by_type[metric_type].append(metric)

            # Analyze each metric type
            high_performing = []
            low_performing = []

            for metric_type, metrics in metrics_by_type.items():
                avg_value = statistics.mean([m.value for m in metrics])
                target_value = metrics[0].target_value if metrics else 1.0

                performance_ratio = avg_value / target_value

                if performance_ratio >= 0.9:
                    high_performing.append((metric_type.value, avg_value, target_value))
                elif performance_ratio < 0.7:
                    low_performing.append((metric_type.value, avg_value, target_value))

                # Add to trend summary
                insights["trend_summary"][metric_type.value] = {
                    "current_value": avg_value,
                    "target_value": target_value,
                    "performance_ratio": performance_ratio,
                }

            # Generate strengths and improvements
            insights["strengths"] = [
                f"✅ {metric_name}: {value:.2f}/{target:.2f} (excellent performance)"
                for metric_name, value, target in high_performing
            ]

            insights["areas_for_improvement"] = [
                f"⚠️ {metric_name}: {value:.2f}/{target:.2f} (below target)"
                for metric_name, value, target in low_performing
            ]

            # Overall assessment
            if len(high_performing) > len(low_performing):
                insights["overall_assessment"] = (
                    "Quality metrics are generally strong with good performance"
                )
            elif len(low_performing) > len(high_performing):
                insights["overall_assessment"] = (
                    "Quality metrics indicate room for improvement"
                )
            else:
                insights["overall_assessment"] = (
                    "Quality metrics show mixed performance"
                )

            # Generate recommendations
            if low_performing:
                insights["recommendations"].append(
                    "Focus on improving underperforming metrics"
                )
                insights["recommendations"].extend(
                    [
                        f"Address {metric_name} (current: {value:.2f}, target: {target:.2f})"
                        for metric_name, value, target in low_performing[:3]  # Top 3
                    ]
                )

            if high_performing:
                insights["recommendations"].append(
                    "Maintain excellent performance in strong areas"
                )

            logger.info(
                f"💡 Generated quality insights for {len(recent_metrics)} metrics"
            )
            return insights

        except Exception as e:
            logger.error(f"❌ Error generating insights: {str(e)}")
            insights["overall_assessment"] = f"Error analyzing metrics: {str(e)}"
            return insights

    def _calculate_trend_direction(self, values: List[float]) -> str:
        """Oblicza kierunek trendu"""

        if len(values) < 2:
            return "stable"

        # Simple linear trend calculation
        first_half = values[: len(values) // 2]
        second_half = values[len(values) // 2 :]

        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)

        change = (second_avg - first_avg) / first_avg if first_avg != 0 else 0

        if change > 0.05:  # 5% improvement
            return "improving"
        elif change < -0.05:  # 5% decline
            return "declining"
        else:
            return "stable"

    def _calculate_change_rate(self, values: List[float]) -> float:
        """Oblicza tempo zmian"""

        if len(values) < 2:
            return 0.0

        first_value = values[0]
        last_value = values[-1]

        if first_value == 0:
            return 0.0

        return (last_value - first_value) / first_value

    def _calculate_confidence(self, values: List[float]) -> float:
        """Oblicza poziom pewności trendu"""

        if len(values) < 3:
            return 0.5

        # Higher confidence with more data points and less variance
        variance = statistics.variance(values)
        data_points_factor = min(len(values) / 10, 1.0)  # Max confidence at 10+ points
        variance_factor = max(0.1, 1.0 - variance)  # Lower variance = higher confidence

        return (data_points_factor + variance_factor) / 2


class QualityMetricsTracker:
    """Główny tracker metryki jakości"""

    def __init__(self):
        self.collector = QualityMetricsCollector()
        self.analyzer = QualityMetricsAnalyzer()
        self.reports_history: List[QualityReport] = []
        self.report_counter = 0

        logger.info("✅ Quality Metrics Tracker initialized")

    def track_analysis_quality(self, analysis_results: Dict[str, Any]) -> QualityReport:
        """Śledzi jakość analizy i generuje raport"""

        try:
            game_name = analysis_results.get("game_name", "Unknown")

            # Collect metrics
            metrics = self.collector.collect_quality_metrics(analysis_results)

            # Add to analyzer history
            self.analyzer.add_metrics(metrics)

            # Calculate overall quality score
            overall_score = self._calculate_overall_quality_score(metrics)

            # Analyze trends
            trends = []
            for metric_type in MetricType:
                trend = self.analyzer.analyze_trends(metric_type)
                if trend:
                    trends.append(trend)

            # Generate insights and recommendations
            insights = self.analyzer.generate_quality_insights(metrics)

            # Create quality report
            self.report_counter += 1
            report = QualityReport(
                report_id=f"qr_{self.report_counter:06d}",
                game_name=game_name,
                analysis_timestamp=datetime.now(),
                overall_quality_score=overall_score,
                metrics=metrics,
                trend_analysis=trends,
                recommendations=insights.get("recommendations", []),
                benchmark_comparison=self._get_benchmark_comparison(metrics),
            )

            # Store report
            self.reports_history.append(report)

            logger.info(
                f"📊 Generated quality report {report.report_id} for {game_name}"
            )
            logger.info(f"🎯 Overall quality score: {overall_score:.2f}/1.0")

            return report

        except Exception as e:
            logger.error(f"❌ Error tracking analysis quality: {str(e)}")

            # Return minimal error report
            return QualityReport(
                report_id=f"qr_error_{self.report_counter:06d}",
                game_name=analysis_results.get("game_name", "Unknown"),
                analysis_timestamp=datetime.now(),
                overall_quality_score=0.0,
                metrics=[],
                trend_analysis=[],
                recommendations=[f"Error tracking quality: {str(e)}"],
                benchmark_comparison={},
            )

    def get_quality_dashboard(self, days_back: int = 7) -> Dict[str, Any]:
        """Generuje dashboard jakości"""

        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            recent_reports = [
                r for r in self.reports_history if r.analysis_timestamp >= cutoff_date
            ]

            if not recent_reports:
                return {
                    "period": f"Last {days_back} days",
                    "total_analyses": 0,
                    "average_quality_score": 0.0,
                    "message": "No analyses in selected period",
                }

            # Calculate dashboard metrics
            total_analyses = len(recent_reports)
            avg_quality = statistics.mean(
                [r.overall_quality_score for r in recent_reports]
            )

            # Metric summaries
            all_metrics = []
            for report in recent_reports:
                all_metrics.extend(report.metrics)

            metric_summaries = {}
            for metric_type in MetricType:
                type_metrics = [m for m in all_metrics if m.metric_type == metric_type]
                if type_metrics:
                    avg_value = statistics.mean([m.value for m in type_metrics])
                    target_value = type_metrics[0].target_value
                    metric_summaries[metric_type.value] = {
                        "average_value": avg_value,
                        "target_value": target_value,
                        "performance_ratio": (
                            avg_value / target_value if target_value > 0 else 0
                        ),
                        "sample_count": len(type_metrics),
                    }

            # Quality distribution
            quality_distribution = {
                "excellent": len(
                    [r for r in recent_reports if r.overall_quality_score >= 0.9]
                ),
                "good": len(
                    [r for r in recent_reports if 0.7 <= r.overall_quality_score < 0.9]
                ),
                "acceptable": len(
                    [r for r in recent_reports if 0.5 <= r.overall_quality_score < 0.7]
                ),
                "poor": len(
                    [r for r in recent_reports if r.overall_quality_score < 0.5]
                ),
            }

            dashboard = {
                "period": f"Last {days_back} days",
                "total_analyses": total_analyses,
                "average_quality_score": avg_quality,
                "quality_distribution": quality_distribution,
                "metric_summaries": metric_summaries,
                "top_performing_games": [
                    {"game": r.game_name, "score": r.overall_quality_score}
                    for r in sorted(
                        recent_reports,
                        key=lambda x: x.overall_quality_score,
                        reverse=True,
                    )[:5]
                ],
                "improvement_opportunities": self._identify_improvement_opportunities(
                    recent_reports
                ),
            }

            logger.info(f"📈 Generated quality dashboard for {total_analyses} analyses")
            return dashboard

        except Exception as e:
            logger.error(f"❌ Error generating dashboard: {str(e)}")
            return {"error": str(e)}

    def _calculate_overall_quality_score(self, metrics: List[QualityMetric]) -> float:
        """Oblicza ogólny wynik jakości"""

        if not metrics:
            return 0.0

        # Weight metrics by their specifications
        total_weighted_score = 0.0
        total_weight = 0.0

        for metric in metrics:
            spec = self.collector.metric_specs.get(metric.metric_type, {})
            weight = spec.get("weight", 1.0)

            # Normalize to 0-1 scale
            normalized_score = (
                min(metric.value / metric.target_value, 1.0)
                if metric.target_value > 0
                else 0.0
            )

            total_weighted_score += normalized_score * weight
            total_weight += weight

        return total_weighted_score / total_weight if total_weight > 0 else 0.0

    def _get_benchmark_comparison(
        self, metrics: List[QualityMetric]
    ) -> Dict[str, float]:
        """Porównuje z benchmarkami"""

        benchmark = {}

        for metric in metrics:
            performance_ratio = (
                metric.value / metric.target_value if metric.target_value > 0 else 0.0
            )
            benchmark[metric.metric_type.value] = performance_ratio

        return benchmark

    def _identify_improvement_opportunities(
        self, recent_reports: List[QualityReport]
    ) -> List[str]:
        """Identyfikuje możliwości poprawy"""

        opportunities = []

        # Analyze common low-performing metrics
        all_metrics = []
        for report in recent_reports:
            all_metrics.extend(report.metrics)

        metric_performance = {}
        for metric_type in MetricType:
            type_metrics = [m for m in all_metrics if m.metric_type == metric_type]
            if type_metrics:
                avg_performance = statistics.mean(
                    [
                        m.value / m.target_value
                        for m in type_metrics
                        if m.target_value > 0
                    ]
                )
                metric_performance[metric_type.value] = avg_performance

        # Identify underperforming areas
        for metric_name, performance in metric_performance.items():
            if performance < 0.7:  # Below 70% of target
                opportunities.append(
                    f"Improve {metric_name} (currently at {performance:.1%} of target)"
                )

        # Analyze quality distribution
        low_quality_count = len(
            [r for r in recent_reports if r.overall_quality_score < 0.7]
        )
        if low_quality_count > len(recent_reports) * 0.2:  # More than 20% low quality
            opportunities.append("Focus on reducing low-quality analyses")

        return opportunities


# Factory function
def create_quality_metrics_tracker() -> QualityMetricsTracker:
    """Tworzy instancję trackera metryki jakości"""
    return QualityMetricsTracker()
