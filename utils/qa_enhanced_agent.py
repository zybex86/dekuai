"""
PHASE 4 Point 1: Enhanced QA Agent with Validation Rules
FAZA 4 Punkt 1: Zaawansowany QA Agent z regułami walidacji

Advanced quality assurance agent with sophisticated validation rules,
automated verification, and intelligent quality assessment capabilities.
"""

import logging
import time
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class QAValidationLevel(Enum):
    """Poziomy walidacji QA"""

    BASIC = "basic"  # Podstawowe sprawdzenia
    STANDARD = "standard"  # Standardowa walidacja
    COMPREHENSIVE = "comprehensive"  # Kompletna walidacja
    STRICT = "strict"  # Ścisłe kryteria jakości


class QAIssueLevel(Enum):
    """Poziomy problemów jakości"""

    INFO = "info"  # Informacyjne
    WARNING = "warning"  # Ostrzeżenia
    ERROR = "error"  # Błędy wymagające poprawek
    CRITICAL = "critical"  # Krytyczne błędy blokujące


@dataclass
class QAValidationRule:
    """Zaawansowana reguła walidacji QA"""

    rule_id: str
    name: str
    description: str
    validation_level: QAValidationLevel
    issue_level: QAIssueLevel
    weight: float  # 0.0 - 1.0 (ważność w ocenie końcowej)

    def validate(self, analysis_data: Dict[str, Any]) -> "QAValidationResult":
        """Wykonuje walidację - do implementacji w subclassach"""
        raise NotImplementedError("Subclasses must implement validate method")


@dataclass
class QAValidationResult:
    """Wynik walidacji QA"""

    rule_id: str
    rule_name: str
    passed: bool
    score: float  # 0.0 - 1.0
    issue_level: QAIssueLevel
    message: str
    recommendations: List[str]
    validation_time: float
    timestamp: datetime


class GameDataCompletenessRule(QAValidationRule):
    """Zaawansowana reguła sprawdzania kompletności danych gry"""

    def __init__(self):
        super().__init__(
            rule_id="GAME_DATA_COMPLETENESS",
            name="Game Data Completeness Validation",
            description="Comprehensive validation of game data completeness and quality",
            validation_level=QAValidationLevel.STANDARD,
            issue_level=QAIssueLevel.ERROR,
            weight=0.25,
        )

    def validate(self, analysis_data: Dict[str, Any]) -> QAValidationResult:
        """Sprawdza kompletność danych gry z zaawansowanymi kryteriami"""
        start_time = time.time()

        try:
            # Required critical fields
            critical_fields = ["title", "current_eshop_price", "MSRP"]
            # Important fields (can reduce score but not fail)
            important_fields = [
                "metacritic_score",
                "opencritic_score",
                "genres",
                "developer",
            ]
            # Optional but valuable fields
            optional_fields = ["release_date", "publisher", "platforms", "description"]

            missing_critical = []
            missing_important = []
            missing_optional = []

            score = 1.0
            recommendations = []

            # Check critical fields
            for field in critical_fields:
                if field not in analysis_data or not analysis_data.get(field):
                    missing_critical.append(field)
                    score -= 0.3  # Heavy penalty for missing critical data

            # Check important fields
            for field in important_fields:
                if field not in analysis_data or not analysis_data.get(field):
                    missing_important.append(field)
                    score -= 0.1  # Moderate penalty

            # Check optional fields
            for field in optional_fields:
                if field not in analysis_data or not analysis_data.get(field):
                    missing_optional.append(field)
                    score -= 0.05  # Small penalty

            # Generate recommendations
            if missing_critical:
                recommendations.append(
                    f"🚨 Critical: Add missing critical fields: {', '.join(missing_critical)}"
                )

            if missing_important:
                recommendations.append(
                    f"⚠️ Important: Consider adding: {', '.join(missing_important)}"
                )

            if missing_optional:
                recommendations.append(
                    f"💡 Enhancement: Could add: {', '.join(missing_optional)}"
                )

            # Data quality checks
            if analysis_data.get("current_eshop_price"):
                price_str = str(analysis_data["current_eshop_price"])
                if "N/A" in price_str or "n/a" in price_str.lower():
                    score -= 0.15
                    recommendations.append(
                        "🔍 Price data shows 'N/A' - verify actual price availability"
                    )

            # Score checks for validity
            for score_field in ["metacritic_score", "opencritic_score"]:
                if score_field in analysis_data:
                    score_val = str(analysis_data[score_field])
                    if score_val == "0" or score_val == "N/A":
                        score -= 0.05
                        recommendations.append(
                            f"📊 {score_field} appears to be unavailable or zero"
                        )

            # Final assessment
            score = max(0.0, score)  # Ensure non-negative
            passed = len(missing_critical) == 0 and score >= 0.7

            if passed:
                if score >= 0.9:
                    message = (
                        "✅ Excellent data completeness - all key information present"
                    )
                else:
                    message = f"✅ Good data completeness - score: {score:.2f}/1.0"
            else:
                message = f"❌ Insufficient data completeness - score: {score:.2f}/1.0, critical issues: {len(missing_critical)}"

            validation_time = time.time() - start_time

            return QAValidationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                passed=passed,
                score=score,
                issue_level=self.issue_level if not passed else QAIssueLevel.INFO,
                message=message,
                recommendations=recommendations,
                validation_time=validation_time,
                timestamp=datetime.now(),
            )

        except Exception as e:
            validation_time = time.time() - start_time

            return QAValidationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                passed=False,
                score=0.0,
                issue_level=QAIssueLevel.CRITICAL,
                message=f"❌ Validation error: {str(e)}",
                recommendations=["🔧 Fix data validation error"],
                validation_time=validation_time,
                timestamp=datetime.now(),
            )


class ValueAnalysisCoherenceRule(QAValidationRule):
    """Sprawdza spójność analizy wartości"""

    def __init__(self):
        super().__init__(
            rule_id="VALUE_ANALYSIS_COHERENCE",
            name="Value Analysis Coherence Check",
            description="Validates coherence and logic of value analysis results",
            validation_level=QAValidationLevel.COMPREHENSIVE,
            issue_level=QAIssueLevel.WARNING,
            weight=0.3,
        )

    def validate(self, analysis_data: Dict[str, Any]) -> QAValidationResult:
        """Sprawdza spójność analizy wartości"""
        start_time = time.time()

        try:
            value_analysis = analysis_data.get("value_analysis", {})

            if not value_analysis:
                return QAValidationResult(
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    passed=False,
                    score=0.0,
                    issue_level=QAIssueLevel.ERROR,
                    message="❌ No value analysis data found",
                    recommendations=["📊 Run value analysis before quality validation"],
                    validation_time=time.time() - start_time,
                    timestamp=datetime.now(),
                )

            score = 1.0
            recommendations = []
            issues = []

            # Check price-recommendation coherence
            current_price = value_analysis.get("current_price", 0)
            recommendation = value_analysis.get("recommendation", "")

            if current_price > 0 and recommendation:
                # High price (>100) with INSTANT BUY recommendation
                if current_price > 100 and "INSTANT" in recommendation.upper():
                    score -= 0.2
                    issues.append("High price with INSTANT BUY recommendation")
                    recommendations.append(
                        "💰 Review recommendation for high-priced game"
                    )

                # Very low price (<10) with SKIP recommendation
                if current_price < 10 and "SKIP" in recommendation.upper():
                    score -= 0.15
                    issues.append("Low price with SKIP recommendation")
                    recommendations.append(
                        "🤔 Verify why low-priced game is recommended to skip"
                    )

            # Check value score consistency
            value_score = value_analysis.get("value_score", 0)
            if value_score > 0:
                if value_score > 8.0 and "SKIP" in recommendation.upper():
                    score -= 0.25
                    issues.append("High value score with SKIP recommendation")
                    recommendations.append(
                        "📈 High value score conflicts with SKIP recommendation"
                    )
                elif value_score < 3.0 and any(
                    word in recommendation.upper() for word in ["BUY", "INSTANT"]
                ):
                    score -= 0.25
                    issues.append("Low value score with BUY recommendation")
                    recommendations.append(
                        "📉 Low value score conflicts with BUY recommendation"
                    )

            # Check buy timing consistency
            buy_timing = value_analysis.get("buy_timing", {})
            timing_assessment = (
                buy_timing.get("assessment", "")
                if isinstance(buy_timing, dict)
                else str(buy_timing)
            )

            if timing_assessment:
                if (
                    "WAIT" in timing_assessment.upper()
                    and "INSTANT" in recommendation.upper()
                ):
                    score -= 0.2
                    issues.append("WAIT timing with INSTANT BUY recommendation")
                    recommendations.append(
                        "⏰ Timing suggests waiting but recommendation is instant buy"
                    )

            # Final assessment
            score = max(0.0, score)
            passed = score >= 0.7 and len(issues) == 0

            if passed:
                message = "✅ Value analysis is coherent and logically consistent"
            else:
                message = (
                    f"⚠️ Value analysis coherence issues detected: {'; '.join(issues)}"
                )

            validation_time = time.time() - start_time

            return QAValidationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                passed=passed,
                score=score,
                issue_level=self.issue_level if not passed else QAIssueLevel.INFO,
                message=message,
                recommendations=recommendations,
                validation_time=validation_time,
                timestamp=datetime.now(),
            )

        except Exception as e:
            validation_time = time.time() - start_time

            return QAValidationResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                passed=False,
                score=0.0,
                issue_level=QAIssueLevel.CRITICAL,
                message=f"❌ Value coherence validation error: {str(e)}",
                recommendations=["🔧 Fix value analysis validation error"],
                validation_time=validation_time,
                timestamp=datetime.now(),
            )


@dataclass
class EnhancedQAReport:
    """Zaawansowany raport jakości QA"""

    overall_score: float
    quality_level: str
    total_validation_time: float
    validation_results: List[QAValidationResult]
    critical_issues: List[QAValidationResult]
    warnings: List[QAValidationResult]
    recommendations: List[str]
    validation_summary: str
    timestamp: datetime

    # Metrics breakdown
    completeness_score: float
    coherence_score: float
    quality_score: float
    consistency_score: float


class EnhancedQAAgent:
    """Zaawansowany agent kontroli jakości z regułami walidacji"""

    def __init__(
        self, validation_level: QAValidationLevel = QAValidationLevel.STANDARD
    ):
        self.validation_level = validation_level
        self.validation_rules: List[QAValidationRule] = []

        # Initialize validation rules based on level
        self._initialize_validation_rules()

        logger.info(
            f"✅ Enhanced QA Agent initialized with {len(self.validation_rules)} rules (level: {validation_level.value})"
        )

    def _initialize_validation_rules(self):
        """Inicjalizuje reguły walidacji na podstawie poziomu"""

        # Basic rules (always included)
        self.validation_rules.append(GameDataCompletenessRule())

        if self.validation_level in [
            QAValidationLevel.STANDARD,
            QAValidationLevel.COMPREHENSIVE,
            QAValidationLevel.STRICT,
        ]:
            self.validation_rules.append(ValueAnalysisCoherenceRule())

    def validate_analysis(self, analysis_data: Dict[str, Any]) -> EnhancedQAReport:
        """
        Wykonuje kompleksową walidację analizy gry używając wszystkich reguł

        Args:
            analysis_data (Dict[str, Any]): Kompletne dane analizy gry

        Returns:
            EnhancedQAReport: Szczegółowy raport jakości
        """
        try:
            logger.info(
                f"🔍 Starting enhanced QA validation with {len(self.validation_rules)} rules..."
            )
            start_time = time.time()

            validation_results = []
            critical_issues = []
            warnings = []

            # Execute all validation rules
            for rule in self.validation_rules:
                logger.debug(f"  Running rule: {rule.name}")
                result = rule.validate(analysis_data)
                validation_results.append(result)

                # Categorize results
                if result.issue_level == QAIssueLevel.CRITICAL:
                    critical_issues.append(result)
                elif result.issue_level in [QAIssueLevel.ERROR, QAIssueLevel.WARNING]:
                    warnings.append(result)

            # Calculate overall metrics
            total_validation_time = time.time() - start_time
            overall_score = self._calculate_weighted_score(validation_results)
            quality_level = self._determine_quality_level(
                overall_score, critical_issues
            )

            # Extract component scores for metrics breakdown
            completeness_score = self._get_rule_score(
                validation_results, "GAME_DATA_COMPLETENESS"
            )
            coherence_score = self._get_rule_score(
                validation_results, "VALUE_ANALYSIS_COHERENCE"
            )
            quality_score = 0.0  # Placeholder for future quality rules
            consistency_score = 0.0  # Placeholder for future consistency rules

            # Aggregate all recommendations
            all_recommendations = []
            for result in validation_results:
                all_recommendations.extend(result.recommendations)

            # Generate validation summary
            validation_summary = self._generate_validation_summary(
                overall_score,
                len(critical_issues),
                len(warnings),
                len(validation_results),
            )

            report = EnhancedQAReport(
                overall_score=overall_score,
                quality_level=quality_level,
                total_validation_time=total_validation_time,
                validation_results=validation_results,
                critical_issues=critical_issues,
                warnings=warnings,
                recommendations=all_recommendations,
                validation_summary=validation_summary,
                timestamp=datetime.now(),
                completeness_score=completeness_score,
                coherence_score=coherence_score,
                quality_score=quality_score,
                consistency_score=consistency_score,
            )

            logger.info(
                f"✅ Enhanced QA validation completed: {quality_level} ({overall_score:.2f}/1.0) in {total_validation_time:.2f}s"
            )

            return report

        except Exception as e:
            logger.error(f"❌ Enhanced QA validation failed: {str(e)}")

            # Return error report
            return EnhancedQAReport(
                overall_score=0.0,
                quality_level="ERROR",
                total_validation_time=(
                    time.time() - start_time if "start_time" in locals() else 0.0
                ),
                validation_results=[],
                critical_issues=[],
                warnings=[],
                recommendations=[f"🚨 QA validation system error: {str(e)}"],
                validation_summary="QA validation failed due to system error",
                timestamp=datetime.now(),
                completeness_score=0.0,
                coherence_score=0.0,
                quality_score=0.0,
                consistency_score=0.0,
            )

    def _calculate_weighted_score(self, results: List[QAValidationResult]) -> float:
        """Oblicza ważony wynik jakości"""
        if not results:
            return 0.0

        total_weighted_score = 0.0
        total_weight = 0.0

        for result in results:
            # Find the rule to get its weight
            rule_weight = 1.0  # Default weight
            for rule in self.validation_rules:
                if rule.rule_id == result.rule_id:
                    rule_weight = rule.weight
                    break

            total_weighted_score += result.score * rule_weight
            total_weight += rule_weight

        return total_weighted_score / total_weight if total_weight > 0 else 0.0

    def _determine_quality_level(
        self, overall_score: float, critical_issues: List[QAValidationResult]
    ) -> str:
        """Określa poziom jakości na podstawie wyniku i błędów krytycznych"""

        if len(critical_issues) > 0:
            return "CRITICAL_ISSUES"

        if overall_score >= 0.9:
            return "EXCELLENT"
        elif overall_score >= 0.8:
            return "VERY_GOOD"
        elif overall_score >= 0.7:
            return "GOOD"
        elif overall_score >= 0.6:
            return "ACCEPTABLE"
        elif overall_score >= 0.4:
            return "POOR"
        else:
            return "UNACCEPTABLE"

    def _get_rule_score(self, results: List[QAValidationResult], rule_id: str) -> float:
        """Pobiera wynik dla konkretnej reguły"""
        for result in results:
            if result.rule_id == rule_id:
                return result.score
        return 0.0  # Rule not found or not executed

    def _generate_validation_summary(
        self,
        overall_score: float,
        critical_count: int,
        warning_count: int,
        total_rules: int,
    ) -> str:
        """Generuje podsumowanie walidacji"""

        if critical_count > 0:
            return f"🚨 Critical quality issues detected ({critical_count} critical, {warning_count} warnings) - immediate attention required"
        elif warning_count > 3:
            return f"⚠️ Multiple quality concerns identified ({warning_count} warnings) - review recommended before publication"
        elif overall_score >= 0.8:
            return f"✅ High quality analysis ({total_rules} checks passed) - ready for publication"
        elif overall_score >= 0.6:
            return f"✅ Acceptable quality with minor improvements possible ({warning_count} recommendations)"
        else:
            return f"❌ Quality below standards - significant improvements needed before publication"


# Factory function for creating QA agents
def create_qa_agent(validation_level: str = "standard") -> EnhancedQAAgent:
    """
    Tworzy instancję Enhanced QA Agent

    Args:
        validation_level (str): Poziom walidacji ('basic', 'standard', 'comprehensive', 'strict')

    Returns:
        EnhancedQAAgent: Skonfigurowany agent QA
    """
    try:
        level = QAValidationLevel(validation_level.lower())
        return EnhancedQAAgent(validation_level=level)
    except ValueError:
        logger.warning(
            f"⚠️ Invalid validation level '{validation_level}', using 'standard'"
        )
        return EnhancedQAAgent(validation_level=QAValidationLevel.STANDARD)
