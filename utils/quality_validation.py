"""
Advanced Quality Validation System for AutoGen DekuDeals
Zaawansowany system walidacji jakości dla AutoGen DekuDeals

PHASE 4: Advanced Quality Control Implementation
FAZA 4: Implementacja zaawansowanej kontroli jakości
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import re
import json

# Setup logging
logger = logging.getLogger(__name__)


class QualityLevel(Enum):
    """Poziomy jakości analiz"""

    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    ACCEPTABLE = "ACCEPTABLE"
    POOR = "POOR"
    UNACCEPTABLE = "UNACCEPTABLE"


class ValidationCategory(Enum):
    """Kategorie walidacji"""

    DATA_COMPLETENESS = "DATA_COMPLETENESS"
    LOGICAL_CONSISTENCY = "LOGICAL_CONSISTENCY"
    OPINION_COHERENCE = "OPINION_COHERENCE"
    EVIDENCE_SUPPORT = "EVIDENCE_SUPPORT"
    RECOMMENDATION_LOGIC = "RECOMMENDATION_LOGIC"
    CONTENT_QUALITY = "CONTENT_QUALITY"


@dataclass
class ValidationRule:
    """Pojedyncza zasada walidacji"""

    name: str
    category: ValidationCategory
    description: str
    weight: float  # 0.0 - 1.0
    critical: bool = False

    def validate(self, data: Dict[str, Any]) -> Tuple[bool, float, str]:
        """
        Waliduje dane według tej zasady

        Returns:
            Tuple[bool, float, str]: (passed, score, message)
        """
        raise NotImplementedError("Subclasses must implement validate method")


@dataclass
class ValidationResult:
    """Wynik walidacji"""

    rule_name: str
    category: ValidationCategory
    passed: bool
    score: float  # 0.0 - 1.0
    message: str
    weight: float
    critical: bool
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class QualityReport:
    """Kompletny raport jakości"""

    overall_score: float
    quality_level: QualityLevel
    validation_results: List[ValidationResult]
    critical_failures: List[ValidationResult]
    recommendations: List[str]
    data_completeness: float
    logical_consistency: float
    content_quality: float
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje raport do dictionary"""
        return {
            "overall_score": self.overall_score,
            "quality_level": self.quality_level.value,
            "critical_failures_count": len(self.critical_failures),
            "total_validations": len(self.validation_results),
            "data_completeness": self.data_completeness,
            "logical_consistency": self.logical_consistency,
            "content_quality": self.content_quality,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp.isoformat(),
            "details": [
                {
                    "rule": result.rule_name,
                    "category": result.category.value,
                    "passed": result.passed,
                    "score": result.score,
                    "message": result.message,
                }
                for result in self.validation_results
            ],
        }


# ======================== VALIDATION RULES ========================


class DataCompletenessRule(ValidationRule):
    """Sprawdza kompletność danych"""

    def __init__(self):
        super().__init__(
            name="Data Completeness Check",
            category=ValidationCategory.DATA_COMPLETENESS,
            description="Validates that essential game data fields are present",
            weight=0.25,
            critical=True,
        )

    def validate(self, data: Dict[str, Any]) -> Tuple[bool, float, str]:
        """Sprawdza kompletność kluczowych pól danych"""
        try:
            required_fields = [
                "title",
                "current_eshop_price",
                "MSRP",
                "metacritic_score",
                "genres",
                "developer",
            ]

            present_fields = 0
            total_fields = len(required_fields)
            missing_fields = []

            for field in required_fields:
                if field in data and data.get(field) not in [
                    None,
                    "",
                    "N/A",
                    "Unknown",
                ]:
                    present_fields += 1
                else:
                    missing_fields.append(field)

            completeness_ratio = present_fields / total_fields

            if completeness_ratio >= 0.9:
                return (
                    True,
                    completeness_ratio,
                    f"Excellent data completeness: {present_fields}/{total_fields} fields",
                )
            elif completeness_ratio >= 0.7:
                return (
                    True,
                    completeness_ratio,
                    f"Good data completeness: {present_fields}/{total_fields} fields",
                )
            elif completeness_ratio >= 0.5:
                return (
                    True,
                    completeness_ratio,
                    f"Acceptable data completeness: {present_fields}/{total_fields} fields",
                )
            else:
                return (
                    False,
                    completeness_ratio,
                    f"Insufficient data completeness: {present_fields}/{total_fields} fields. Missing: {', '.join(missing_fields)}",
                )

        except Exception as e:
            return False, 0.0, f"Error checking data completeness: {e}"


class PriceLogicRule(ValidationRule):
    """Sprawdza logiczność analiz cenowych"""

    def __init__(self):
        super().__init__(
            name="Price Logic Consistency",
            category=ValidationCategory.LOGICAL_CONSISTENCY,
            description="Validates logical consistency of price analysis",
            weight=0.2,
            critical=True,
        )

    def validate(self, data: Dict[str, Any]) -> Tuple[bool, float, str]:
        """Sprawdza logiczność analiz cenowych"""
        try:
            # Extract price data
            current_price = data.get("current_eshop_price", "N/A")
            msrp = data.get("MSRP", "N/A")
            lowest_price = data.get("lowest_historical_price", "N/A")

            # Extract analysis data
            value_analysis = data.get("value_analysis", {})
            recommendation = value_analysis.get("recommendation", "N/A")

            issues = []
            score = 1.0

            # Check price relationships
            if current_price != "N/A" and msrp != "N/A":
                try:
                    current_float = float(
                        str(current_price)
                        .replace("$", "")
                        .replace("zł", "")
                        .replace(",", ".")
                    )
                    msrp_float = float(
                        str(msrp).replace("$", "").replace("zł", "").replace(",", ".")
                    )

                    if (
                        current_float > msrp_float * 1.1
                    ):  # Allow 10% margin for currency/tax differences
                        issues.append("Current price significantly higher than MSRP")
                        score -= 0.3
                except ValueError:
                    issues.append("Price values not properly formatted")
                    score -= 0.2

            # Check recommendation consistency
            if "metacritic_score" in data:
                try:
                    score_value = float(
                        str(data["metacritic_score"]).replace("/100", "")
                    )
                    if score_value >= 90 and "SKIP" in str(recommendation).upper():
                        issues.append(
                            "High-rated game marked as SKIP without clear justification"
                        )
                        score -= 0.4
                    elif score_value <= 50 and "BUY" in str(recommendation).upper():
                        issues.append(
                            "Low-rated game marked as BUY without clear justification"
                        )
                        score -= 0.4
                except ValueError:
                    pass

            if score >= 0.8:
                return True, score, "Price logic is consistent"
            elif issues:
                return (
                    False,
                    max(score, 0.0),
                    f"Price logic issues: {'; '.join(issues)}",
                )
            else:
                return True, score, "Price logic appears consistent"

        except Exception as e:
            return False, 0.0, f"Error checking price logic: {e}"


class OpinionCoherenceRule(ValidationRule):
    """Sprawdza spójność opinii"""

    def __init__(self):
        super().__init__(
            name="Opinion Coherence Check",
            category=ValidationCategory.OPINION_COHERENCE,
            description="Validates coherence and quality of generated opinion",
            weight=0.25,
            critical=False,
        )

    def validate(self, data: Dict[str, Any]) -> Tuple[bool, float, str]:
        """Sprawdza spójność i jakość opinii"""
        try:
            review_data = data.get("review", {})

            if not review_data:
                return False, 0.0, "No review data found"

            score = 1.0
            issues = []

            # Check for key review components
            required_components = ["final_verdict", "strengths", "target_audience"]
            missing_components = []

            for component in required_components:
                if component not in review_data or not review_data[component]:
                    missing_components.append(component)
                    score -= 0.2

            if missing_components:
                issues.append(f"Missing components: {', '.join(missing_components)}")

            # Check final verdict quality
            final_verdict = review_data.get("final_verdict", "")
            if final_verdict:
                if len(final_verdict) < 50:
                    issues.append("Final verdict too short")
                    score -= 0.2
                elif len(final_verdict) > 500:
                    issues.append("Final verdict too long")
                    score -= 0.1

            # Check strengths/weaknesses balance
            strengths = review_data.get("strengths", [])
            weaknesses = review_data.get("weaknesses", [])

            if isinstance(strengths, list) and isinstance(weaknesses, list):
                if len(strengths) == 0 and len(weaknesses) == 0:
                    issues.append("No strengths or weaknesses identified")
                    score -= 0.3
                elif len(strengths) > 0 and len(weaknesses) == 0:
                    issues.append("Only strengths identified, no weaknesses")
                    score -= 0.1

            if score >= 0.7:
                return True, score, "Opinion is coherent and well-structured"
            else:
                return (
                    False,
                    max(score, 0.0),
                    f"Opinion coherence issues: {'; '.join(issues)}",
                )

        except Exception as e:
            return False, 0.0, f"Error checking opinion coherence: {e}"


class RecommendationLogicRule(ValidationRule):
    """Sprawdza logikę rekomendacji"""

    def __init__(self):
        super().__init__(
            name="Recommendation Logic Check",
            category=ValidationCategory.RECOMMENDATION_LOGIC,
            description="Validates that recommendations are supported by evidence",
            weight=0.3,
            critical=True,
        )

    def validate(self, data: Dict[str, Any]) -> Tuple[bool, float, str]:
        """Sprawdza czy rekomendacje są logicznie uzasadnione"""
        try:
            review_data = data.get("review", {})
            value_analysis = data.get("value_analysis", {})

            recommendation = review_data.get(
                "recommendation", value_analysis.get("recommendation", "N/A")
            )
            overall_rating = review_data.get("overall_rating", 0)

            score = 1.0
            issues = []

            # Check recommendation vs rating consistency
            if overall_rating > 0:
                if overall_rating >= 8.5 and "SKIP" in str(recommendation).upper():
                    issues.append("High rating but SKIP recommendation")
                    score -= 0.4
                elif overall_rating <= 4.0 and any(
                    word in str(recommendation).upper() for word in ["BUY", "INSTANT"]
                ):
                    issues.append("Low rating but BUY recommendation")
                    score -= 0.4
                elif (
                    4.0 < overall_rating < 6.0
                    and "INSTANT" in str(recommendation).upper()
                ):
                    issues.append("Medium rating but INSTANT BUY recommendation")
                    score -= 0.3

            # Check if recommendation is supported by analysis
            final_verdict = review_data.get("final_verdict", "")
            if recommendation != "N/A" and final_verdict:
                # Simple keyword matching to check if verdict supports recommendation
                verdict_lower = final_verdict.lower()
                rec_upper = str(recommendation).upper()

                if "BUY" in rec_upper and not any(
                    word in verdict_lower
                    for word in [
                        "recommend",
                        "worth",
                        "buy",
                        "excellent",
                        "great",
                        "good",
                    ]
                ):
                    issues.append("BUY recommendation not clearly supported in verdict")
                    score -= 0.2
                elif "SKIP" in rec_upper and not any(
                    word in verdict_lower
                    for word in ["avoid", "skip", "not worth", "poor", "disappointing"]
                ):
                    issues.append(
                        "SKIP recommendation not clearly supported in verdict"
                    )
                    score -= 0.2

            if score >= 0.7:
                return True, score, "Recommendation logic is sound"
            else:
                return (
                    False,
                    max(score, 0.0),
                    f"Recommendation logic issues: {'; '.join(issues)}",
                )

        except Exception as e:
            return False, 0.0, f"Error checking recommendation logic: {e}"


class QualityValidator:
    """Główny walidator jakości"""

    def __init__(self):
        self.rules: List[ValidationRule] = [
            DataCompletenessRule(),
            PriceLogicRule(),
            OpinionCoherenceRule(),
            RecommendationLogicRule(),
        ]

        logger.info(f"✅ Quality Validator initialized with {len(self.rules)} rules")

    def validate_analysis(self, analysis_data: Dict[str, Any]) -> QualityReport:
        """
        Waliduje kompletną analizę gry

        Args:
            analysis_data: Pełne dane analizy gry

        Returns:
            QualityReport: Kompletny raport jakości
        """
        try:
            validation_results = []
            critical_failures = []

            # Run all validation rules
            for rule in self.rules:
                passed, score, message = rule.validate(analysis_data)

                result = ValidationResult(
                    rule_name=rule.name,
                    category=rule.category,
                    passed=passed,
                    score=score,
                    message=message,
                    weight=rule.weight,
                    critical=rule.critical,
                )

                validation_results.append(result)

                if rule.critical and not passed:
                    critical_failures.append(result)

            # Calculate overall scores
            overall_score = self._calculate_overall_score(validation_results)
            quality_level = self._determine_quality_level(
                overall_score, critical_failures
            )

            # Calculate category scores
            data_completeness = self._calculate_category_score(
                validation_results, ValidationCategory.DATA_COMPLETENESS
            )
            logical_consistency = self._calculate_category_score(
                validation_results, ValidationCategory.LOGICAL_CONSISTENCY
            )
            content_quality = self._calculate_category_score(
                validation_results, ValidationCategory.OPINION_COHERENCE
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(
                validation_results, critical_failures
            )

            report = QualityReport(
                overall_score=overall_score,
                quality_level=quality_level,
                validation_results=validation_results,
                critical_failures=critical_failures,
                recommendations=recommendations,
                data_completeness=data_completeness,
                logical_consistency=logical_consistency,
                content_quality=content_quality,
            )

            logger.info(
                f"📊 Quality validation completed: {quality_level.value} ({overall_score:.2f}/1.0)"
            )

            return report

        except Exception as e:
            logger.error(f"❌ Error during quality validation: {e}")
            # Return minimal report indicating validation failure
            return QualityReport(
                overall_score=0.0,
                quality_level=QualityLevel.UNACCEPTABLE,
                validation_results=[],
                critical_failures=[],
                recommendations=[f"Validation failed due to error: {e}"],
                data_completeness=0.0,
                logical_consistency=0.0,
                content_quality=0.0,
            )

    def _calculate_overall_score(self, results: List[ValidationResult]) -> float:
        """Oblicza ogólny wynik jakości"""
        if not results:
            return 0.0

        weighted_score = 0.0
        total_weight = 0.0

        for result in results:
            weighted_score += result.score * result.weight
            total_weight += result.weight

        return weighted_score / total_weight if total_weight > 0 else 0.0

    def _determine_quality_level(
        self, overall_score: float, critical_failures: List[ValidationResult]
    ) -> QualityLevel:
        """Określa poziom jakości na podstawie wyniku i krytycznych błędów"""
        if critical_failures:
            return QualityLevel.UNACCEPTABLE
        elif overall_score >= 0.9:
            return QualityLevel.EXCELLENT
        elif overall_score >= 0.8:
            return QualityLevel.GOOD
        elif overall_score >= 0.6:
            return QualityLevel.ACCEPTABLE
        elif overall_score >= 0.4:
            return QualityLevel.POOR
        else:
            return QualityLevel.UNACCEPTABLE

    def _calculate_category_score(
        self, results: List[ValidationResult], category: ValidationCategory
    ) -> float:
        """Oblicza wynik dla konkretnej kategorii"""
        category_results = [r for r in results if r.category == category]

        if not category_results:
            return 1.0  # Default to perfect if no rules for this category

        total_score = sum(r.score * r.weight for r in category_results)
        total_weight = sum(r.weight for r in category_results)

        return total_score / total_weight if total_weight > 0 else 1.0

    def _generate_recommendations(
        self, results: List[ValidationResult], critical_failures: List[ValidationResult]
    ) -> List[str]:
        """Generuje rekomendacje na podstawie wyników walidacji"""
        recommendations = []

        # Handle critical failures first
        if critical_failures:
            recommendations.append(
                "🚨 Critical issues must be resolved before publication:"
            )
            for failure in critical_failures:
                recommendations.append(f"  • {failure.message}")

        # Add specific improvement suggestions
        for result in results:
            if not result.passed and result.score < 0.5:
                recommendations.append(
                    f"⚠️ Improve {result.category.value.lower()}: {result.message}"
                )

        # Add general quality suggestions
        low_scoring_categories = [r for r in results if r.score < 0.7]
        if low_scoring_categories:
            recommendations.append(
                "💡 Consider reviewing data collection and analysis processes"
            )

        return (
            recommendations
            if recommendations
            else ["✅ Analysis meets quality standards"]
        )


def validate_game_analysis(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Główna funkcja walidacji analizy gry - AutoGen tool wrapper

    Args:
        analysis_data: Kompletne dane analizy gry

    Returns:
        Dict: Raport jakości w formacie dictionary
    """
    try:
        validator = QualityValidator()
        report = validator.validate_analysis(analysis_data)

        logger.info(f"🎯 Quality validation completed: {report.quality_level.value}")

        return {
            "success": True,
            "quality_report": report.to_dict(),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Quality validation failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "quality_report": None,
            "timestamp": datetime.now().isoformat(),
        }


if __name__ == "__main__":
    # Test the quality validation system
    print("🧪 Testing Quality Validation System...")

    # Sample analysis data for testing
    test_data = {
        "title": "Test Game",
        "current_eshop_price": "$29.99",
        "MSRP": "$39.99",
        "metacritic_score": "85",
        "genres": ["Action", "Adventure"],
        "developer": "Test Studio",
        "value_analysis": {"recommendation": "BUY"},
        "review": {
            "overall_rating": 8.5,
            "recommendation": "BUY",
            "final_verdict": "This is an excellent game that offers great value for money with engaging gameplay and high production values.",
            "strengths": ["Great gameplay", "Beautiful visuals"],
            "weaknesses": ["Short campaign"],
            "target_audience": ["Action game fans", "Adventure lovers"],
        },
    }

    result = validate_game_analysis(test_data)

    if result["success"]:
        report = result["quality_report"]
        print(f"✅ Quality Level: {report['quality_level']}")
        print(f"📊 Overall Score: {report['overall_score']:.2f}")
        print(f"🔍 Critical Failures: {report['critical_failures_count']}")
        print("📋 Recommendations:")
        for rec in report["recommendations"]:
            print(f"  {rec}")
    else:
        print(f"❌ Validation failed: {result['error']}")
