"""
PHASE 4 Point 2: Automatic Completeness Checking
FAZA 4 Punkt 2: Automatyczne sprawdzanie kompletności

Automated data validation and completeness checking system with intelligent
field validation, data quality assessment, and completion suggestions.
"""

import logging
from typing import Dict, Any, List, Tuple, Optional, Set
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DataFieldType(Enum):
    """Typy pól danych"""

    REQUIRED = "required"  # Wymagane do funkcjonowania
    IMPORTANT = "important"  # Ważne dla jakości analizy
    OPTIONAL = "optional"  # Dodatkowe, ale przydatne
    DERIVED = "derived"  # Wyliczone na podstawie innych pól


class DataFieldCategory(Enum):
    """Kategorie pól danych"""

    BASIC_INFO = "basic_info"  # Podstawowe informacje o grze
    PRICING = "pricing"  # Dane cenowe
    RATINGS = "ratings"  # Oceny i recenzje
    METADATA = "metadata"  # Metadane (gatunki, developer, etc.)
    ANALYSIS_RESULTS = "analysis_results"  # Wyniki analiz
    TIMESTAMPS = "timestamps"  # Znaczniki czasowe


@dataclass
class DataFieldSpec:
    """Specyfikacja pola danych"""

    field_name: str
    field_type: DataFieldType
    category: DataFieldCategory
    description: str
    validation_rules: List[str]
    fallback_sources: List[str]  # Alternatywne źródła danych
    weight: float  # Waga w ocenie kompletności (0.0-1.0)


@dataclass
class CompletenessResult:
    """Wynik sprawdzania kompletności"""

    field_name: str
    present: bool
    valid: bool
    value_preview: str
    validation_messages: List[str]
    suggestions: List[str]
    completion_score: float  # 0.0-1.0


@dataclass
class CompletenessReport:
    """Raport kompletności danych"""

    overall_score: float
    completeness_level: str
    total_fields: int
    present_fields: int
    valid_fields: int
    field_results: List[CompletenessResult]
    missing_required: List[str]
    missing_important: List[str]
    completion_suggestions: List[str]
    data_quality_issues: List[str]
    timestamp: datetime


class GameDataSpec:
    """Definicja specyfikacji danych gry"""

    def __init__(self):
        self.field_specs: List[DataFieldSpec] = []
        self._initialize_field_specs()

    def _initialize_field_specs(self):
        """Inicjalizuje specyfikacje pól danych gry"""

        # BASIC INFO - Required fields
        self.field_specs.extend(
            [
                DataFieldSpec(
                    field_name="title",
                    field_type=DataFieldType.REQUIRED,
                    category=DataFieldCategory.BASIC_INFO,
                    description="Game title/name",
                    validation_rules=["not_empty", "min_length:2", "max_length:200"],
                    fallback_sources=["game_name", "product_title"],
                    weight=1.0,
                ),
                DataFieldSpec(
                    field_name="developer",
                    field_type=DataFieldType.IMPORTANT,
                    category=DataFieldCategory.BASIC_INFO,
                    description="Game developer/studio",
                    validation_rules=["not_empty", "min_length:2"],
                    fallback_sources=["studio", "dev"],
                    weight=0.7,
                ),
                DataFieldSpec(
                    field_name="publisher",
                    field_type=DataFieldType.OPTIONAL,
                    category=DataFieldCategory.BASIC_INFO,
                    description="Game publisher",
                    validation_rules=["not_empty"],
                    fallback_sources=["pub"],
                    weight=0.4,
                ),
            ]
        )

        # PRICING - Critical for value analysis
        self.field_specs.extend(
            [
                DataFieldSpec(
                    field_name="current_eshop_price",
                    field_type=DataFieldType.REQUIRED,
                    category=DataFieldCategory.PRICING,
                    description="Current eShop price",
                    validation_rules=["not_empty", "not_na", "numeric_price"],
                    fallback_sources=["current_price", "price", "eshop_price"],
                    weight=1.0,
                ),
                DataFieldSpec(
                    field_name="MSRP",
                    field_type=DataFieldType.REQUIRED,
                    category=DataFieldCategory.PRICING,
                    description="Manufacturer's Suggested Retail Price",
                    validation_rules=["not_empty", "not_na", "numeric_price"],
                    fallback_sources=["msrp", "original_price", "launch_price"],
                    weight=1.0,
                ),
                DataFieldSpec(
                    field_name="lowest_historical_price",
                    field_type=DataFieldType.IMPORTANT,
                    category=DataFieldCategory.PRICING,
                    description="Lowest historical price",
                    validation_rules=["not_empty", "not_na", "numeric_price"],
                    fallback_sources=["lowest_price", "historic_low"],
                    weight=0.8,
                ),
            ]
        )

        # RATINGS - Important for quality assessment
        self.field_specs.extend(
            [
                DataFieldSpec(
                    field_name="metacritic_score",
                    field_type=DataFieldType.IMPORTANT,
                    category=DataFieldCategory.RATINGS,
                    description="Metacritic score (0-100)",
                    validation_rules=["numeric_score", "range:0-100"],
                    fallback_sources=["metacritic", "meta_score"],
                    weight=0.9,
                ),
                DataFieldSpec(
                    field_name="opencritic_score",
                    field_type=DataFieldType.IMPORTANT,
                    category=DataFieldCategory.RATINGS,
                    description="OpenCritic score (0-100)",
                    validation_rules=["numeric_score", "range:0-100"],
                    fallback_sources=["opencritic", "open_critic"],
                    weight=0.8,
                ),
            ]
        )

        # METADATA - Useful for analysis
        self.field_specs.extend(
            [
                DataFieldSpec(
                    field_name="genres",
                    field_type=DataFieldType.IMPORTANT,
                    category=DataFieldCategory.METADATA,
                    description="Game genres/categories",
                    validation_rules=["not_empty", "list_or_string"],
                    fallback_sources=["genre", "categories"],
                    weight=0.7,
                ),
                DataFieldSpec(
                    field_name="platforms",
                    field_type=DataFieldType.OPTIONAL,
                    category=DataFieldCategory.METADATA,
                    description="Available platforms",
                    validation_rules=["not_empty"],
                    fallback_sources=["platform", "consoles"],
                    weight=0.5,
                ),
                DataFieldSpec(
                    field_name="release_date",
                    field_type=DataFieldType.OPTIONAL,
                    category=DataFieldCategory.METADATA,
                    description="Game release date",
                    validation_rules=["not_empty", "valid_date"],
                    fallback_sources=["released", "launch_date"],
                    weight=0.6,
                ),
            ]
        )

        # ANALYSIS RESULTS - Derived data
        self.field_specs.extend(
            [
                DataFieldSpec(
                    field_name="value_analysis",
                    field_type=DataFieldType.DERIVED,
                    category=DataFieldCategory.ANALYSIS_RESULTS,
                    description="Value analysis results",
                    validation_rules=["is_dict", "has_recommendation"],
                    fallback_sources=[],
                    weight=0.9,
                ),
                DataFieldSpec(
                    field_name="review",
                    field_type=DataFieldType.DERIVED,
                    category=DataFieldCategory.ANALYSIS_RESULTS,
                    description="Generated review data",
                    validation_rules=["is_dict", "has_final_verdict"],
                    fallback_sources=[],
                    weight=0.8,
                ),
            ]
        )


class DataValidator:
    """Walidator danych z regułami sprawdzania"""

    @staticmethod
    def validate_field(
        value: Any, validation_rules: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Waliduje wartość pola według podanych reguł

        Args:
            value: Wartość do walidacji
            validation_rules: Lista reguł walidacji

        Returns:
            Tuple[bool, List[str]]: (is_valid, validation_messages)
        """
        is_valid = True
        messages = []

        try:
            value_str = str(value) if value is not None else ""

            for rule in validation_rules:
                rule_valid, rule_message = DataValidator._apply_validation_rule(
                    value, value_str, rule
                )

                if not rule_valid:
                    is_valid = False
                    messages.append(rule_message)

            if is_valid and not messages:
                messages.append("✅ Field validation passed")

        except Exception as e:
            is_valid = False
            messages.append(f"❌ Validation error: {str(e)}")

        return is_valid, messages

    @staticmethod
    def _apply_validation_rule(
        value: Any, value_str: str, rule: str
    ) -> Tuple[bool, str]:
        """Stosuje pojedynczą regułę walidacji"""

        try:
            if rule == "not_empty":
                if not value or (isinstance(value, str) and len(value.strip()) == 0):
                    return False, "❌ Field cannot be empty"
                return True, "✅ Field is not empty"

            elif rule == "not_na":
                if value_str.upper() in ["N/A", "NA", "NULL", "NONE", ""]:
                    return False, "❌ Field contains N/A or null value"
                return True, "✅ Field has valid value"

            elif rule.startswith("min_length:"):
                min_len = int(rule.split(":")[1])
                if len(value_str) < min_len:
                    return False, f"❌ Field too short (min {min_len} characters)"
                return True, f"✅ Field meets minimum length ({min_len})"

            elif rule.startswith("max_length:"):
                max_len = int(rule.split(":")[1])
                if len(value_str) > max_len:
                    return False, f"❌ Field too long (max {max_len} characters)"
                return True, f"✅ Field within maximum length ({max_len})"

            elif rule == "numeric_price":
                try:
                    # Extract numeric value from price string
                    import re

                    numeric_match = re.search(r"[\d.,]+", value_str)
                    if not numeric_match:
                        return False, "❌ No numeric price found"

                    price_val = float(numeric_match.group().replace(",", "."))
                    if price_val < 0:
                        return False, "❌ Price cannot be negative"
                    if price_val > 1000:  # Sanity check for extremely high prices
                        return (
                            False,
                            f"⚠️ Very high price ({price_val}) - verify accuracy",
                        )

                    return True, f"✅ Valid price: {price_val}"
                except:
                    return False, f"❌ Invalid price format: {value_str}"

            elif rule == "numeric_score":
                try:
                    if value_str.upper() in ["N/A", "NA", "TBD", ""]:
                        return True, "ℹ️ Score not available (acceptable)"

                    score_val = float(value_str)
                    return True, f"✅ Valid score: {score_val}"
                except:
                    return False, f"❌ Invalid score format: {value_str}"

            elif rule.startswith("range:"):
                range_spec = rule.split(":")[1]
                min_val, max_val = map(float, range_spec.split("-"))

                try:
                    numeric_val = float(value_str)
                    if min_val <= numeric_val <= max_val:
                        return True, f"✅ Value in range {min_val}-{max_val}"
                    else:
                        return (
                            False,
                            f"❌ Value {numeric_val} outside range {min_val}-{max_val}",
                        )
                except:
                    return (
                        False,
                        f"❌ Cannot validate range for non-numeric: {value_str}",
                    )

            elif rule == "list_or_string":
                if isinstance(value, (list, tuple, str)):
                    return True, "✅ Valid list or string format"
                return False, f"❌ Expected list or string, got {type(value)}"

            elif rule == "is_dict":
                if isinstance(value, dict):
                    return True, "✅ Valid dictionary format"
                return False, f"❌ Expected dictionary, got {type(value)}"

            elif rule == "has_recommendation":
                if isinstance(value, dict) and "recommendation" in value:
                    return True, "✅ Has recommendation field"
                return False, "❌ Missing recommendation in analysis"

            elif rule == "has_final_verdict":
                if isinstance(value, dict) and "final_verdict" in value:
                    return True, "✅ Has final verdict field"
                return False, "❌ Missing final verdict in review"

            elif rule == "valid_date":
                # Basic date validation - could be enhanced
                import re

                date_patterns = [
                    r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
                    r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
                    r"\d{2}\.\d{2}\.\d{4}",  # DD.MM.YYYY
                ]

                for pattern in date_patterns:
                    if re.match(pattern, value_str):
                        return True, "✅ Valid date format"

                return False, f"❌ Invalid date format: {value_str}"

            else:
                return True, f"⚠️ Unknown validation rule: {rule}"

        except Exception as e:
            return False, f"❌ Rule validation error: {str(e)}"


class AutomaticCompletenessChecker:
    """Automatyczny system sprawdzania kompletności danych"""

    def __init__(self):
        # Define required fields for game analysis
        self.required_fields = ["title", "current_eshop_price", "MSRP"]

        # Define important fields that improve analysis quality
        self.important_fields = [
            "metacritic_score",
            "opencritic_score",
            "genres",
            "developer",
            "lowest_historical_price",
            "release_date",
        ]

        # Define optional fields for enhanced analysis
        self.optional_fields = ["publisher", "platforms", "description", "screenshots"]

        logger.info("✅ Automatic Completeness Checker initialized")

    def check_completeness(self, game_data: Dict[str, Any]) -> CompletenessReport:
        """
        Sprawdza kompletność danych gry

        Args:
            game_data (Dict[str, Any]): Dane gry do sprawdzenia

        Returns:
            CompletenessReport: Kompletny raport kompletności
        """
        try:
            logger.info("🔍 Starting automatic completeness checking...")

            # Check each category of fields
            missing_required = self._check_field_category(
                game_data, self.required_fields
            )
            missing_important = self._check_field_category(
                game_data, self.important_fields
            )
            missing_optional = self._check_field_category(
                game_data, self.optional_fields
            )

            # Count present and valid fields
            all_fields = (
                self.required_fields + self.important_fields + self.optional_fields
            )
            present_fields = 0
            valid_fields = 0
            data_quality_issues = []

            for field in all_fields:
                if field in game_data and game_data[field] is not None:
                    present_fields += 1

                    # Validate field quality
                    if self._is_field_valid(field, game_data[field]):
                        valid_fields += 1
                    else:
                        data_quality_issues.append(
                            f"⚠️ Quality issue in {field}: {str(game_data[field])}"
                        )

            # Calculate overall score
            total_fields = len(all_fields)

            # Weighted scoring (required fields have higher weight)
            required_score = (len(self.required_fields) - len(missing_required)) / len(
                self.required_fields
            )
            important_score = (
                (len(self.important_fields) - len(missing_important))
                / len(self.important_fields)
                if self.important_fields
                else 1.0
            )
            optional_score = (
                (len(self.optional_fields) - len(missing_optional))
                / len(self.optional_fields)
                if self.optional_fields
                else 1.0
            )

            # Weight: Required (60%), Important (30%), Optional (10%)
            overall_score = (
                (required_score * 0.6)
                + (important_score * 0.3)
                + (optional_score * 0.1)
            )

            # Determine completeness level
            completeness_level = self._determine_completeness_level(
                overall_score, missing_required
            )

            # Generate completion suggestions
            completion_suggestions = self._generate_suggestions(
                missing_required, missing_important, missing_optional
            )

            report = CompletenessReport(
                overall_score=overall_score,
                completeness_level=completeness_level,
                total_fields=total_fields,
                present_fields=present_fields,
                valid_fields=valid_fields,
                field_results=[],
                missing_required=missing_required,
                missing_important=missing_important,
                completion_suggestions=completion_suggestions,
                data_quality_issues=data_quality_issues,
                timestamp=datetime.now(),
            )

            logger.info(
                f"✅ Completeness check completed: {completeness_level} ({overall_score:.2f}/1.0)"
            )
            logger.info(
                f"📊 Fields: {present_fields}/{total_fields} present, {valid_fields} valid"
            )

            return report

        except Exception as e:
            logger.error(f"❌ Completeness checking failed: {str(e)}")

            return CompletenessReport(
                overall_score=0.0,
                completeness_level="ERROR",
                total_fields=0,
                present_fields=0,
                valid_fields=0,
                field_results=[],
                missing_required=[],
                missing_important=[],
                completion_suggestions=[
                    f"🚨 Completeness checking system error: {str(e)}"
                ],
                data_quality_issues=[],
                timestamp=datetime.now(),
            )

    def _check_field_category(
        self, game_data: Dict[str, Any], field_list: List[str]
    ) -> List[str]:
        """Sprawdza które pola z kategorii są brakujące"""
        missing = []

        for field in field_list:
            if (
                field not in game_data
                or game_data[field] is None
                or game_data[field] == ""
            ):
                missing.append(field)

        return missing

    def _is_field_valid(self, field_name: str, field_value: Any) -> bool:
        """Sprawdza czy wartość pola jest poprawna"""
        try:
            value_str = str(field_value).strip().lower()

            # Check for invalid/placeholder values
            invalid_values = [
                "n/a",
                "na",
                "null",
                "none",
                "undefined",
                "tbd",
                "unknown",
            ]
            if value_str in invalid_values:
                return False

            # Field-specific validation
            if "price" in field_name.lower():
                # Price should contain numeric value
                import re

                return bool(re.search(r"[\d.,]+", str(field_value)))

            elif "score" in field_name.lower():
                # Score should be numeric or N/A (which is acceptable)
                if value_str in ["n/a", "na", "tbd"]:
                    return True  # Acceptable for scores
                try:
                    score = float(value_str)
                    return 0 <= score <= 100
                except:
                    return False

            elif field_name in ["title", "developer", "publisher"]:
                # Text fields should have meaningful content
                return len(value_str) > 1

            else:
                # General validation - just not empty
                return len(value_str) > 0

        except:
            return False

    def _determine_completeness_level(
        self, overall_score: float, missing_required: List[str]
    ) -> str:
        """Określa poziom kompletności danych"""

        if missing_required:
            return "INCOMPLETE"  # Missing required fields
        elif overall_score >= 0.9:
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
            return "VERY_POOR"

    def _generate_suggestions(
        self,
        missing_required: List[str],
        missing_important: List[str],
        missing_optional: List[str],
    ) -> List[str]:
        """Generuje sugestie uzupełnienia danych"""
        suggestions = []

        if missing_required:
            suggestions.append(
                f"🚨 CRITICAL: Add missing required fields: {', '.join(missing_required)}"
            )
            suggestions.append(
                "💡 Required fields are essential for basic analysis functionality"
            )

        if missing_important:
            suggestions.append(
                f"⚠️ IMPORTANT: Consider adding important fields: {', '.join(missing_important)}"
            )
            suggestions.append(
                "📈 Important fields significantly improve analysis quality"
            )

        if missing_optional:
            suggestions.append(
                f"💡 ENHANCEMENT: Could add optional fields: {', '.join(missing_optional[:3])}"
            )  # Limit to 3
            suggestions.append("✨ Optional fields provide richer context for analysis")

        # Specific suggestions for common missing fields
        if "metacritic_score" in missing_important:
            suggestions.append("🎯 Try searching Metacritic website for review scores")

        if "genres" in missing_important:
            suggestions.append("🎮 Game genres help with targeted value analysis")

        if "lowest_historical_price" in missing_important:
            suggestions.append("💰 Historical pricing improves deal assessment")

        return suggestions

    def get_completeness_requirements(self) -> Dict[str, Any]:
        """Zwraca wymagania kompletności danych"""
        return {
            "required_fields": {
                "fields": self.required_fields,
                "description": "Essential fields for basic functionality",
                "weight": 0.6,
            },
            "important_fields": {
                "fields": self.important_fields,
                "description": "Fields that significantly improve analysis quality",
                "weight": 0.3,
            },
            "optional_fields": {
                "fields": self.optional_fields,
                "description": "Additional fields for enhanced analysis",
                "weight": 0.1,
            },
            "scoring": {
                "excellent": ">= 0.9",
                "very_good": ">= 0.8",
                "good": ">= 0.7",
                "acceptable": ">= 0.6",
                "poor": ">= 0.4",
                "very_poor": "< 0.4",
            },
        }

    def suggest_data_improvements(
        self, completeness_report: CompletenessReport
    ) -> Dict[str, Any]:
        """Generuje szczegółowe sugestie poprawy danych"""

        improvements = {
            "priority_actions": [],
            "data_collection_tips": [],
            "validation_fixes": [],
            "enhancement_opportunities": [],
        }

        # Priority actions for missing required fields
        if completeness_report.missing_required:
            improvements["priority_actions"].append(
                {
                    "action": "Add missing required fields",
                    "fields": completeness_report.missing_required,
                    "impact": "Critical - system cannot function without these fields",
                }
            )

        # Data collection tips for important fields
        if completeness_report.missing_important:
            improvements["data_collection_tips"].append(
                {
                    "tip": "Enhance data collection for important fields",
                    "fields": completeness_report.missing_important,
                    "benefit": "Significantly improves analysis quality and accuracy",
                }
            )

        return improvements

    def auto_fix_data_issues(
        self, game_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], List[str]]:
        """
        Próbuje automatycznie naprawić typowe problemy z danymi

        Args:
            game_data: Oryginalne dane gry

        Returns:
            Tuple[Dict, List]: (poprawione_dane, lista_zmian)
        """
        fixed_data = game_data.copy()
        fixes_applied = []

        try:
            # Fix common price formatting issues
            price_fields = ["current_eshop_price", "MSRP", "lowest_historical_price"]
            for field in price_fields:
                if field in fixed_data:
                    original_value = fixed_data[field]
                    fixed_value = self._fix_price_format(original_value)
                    if fixed_value != original_value:
                        fixed_data[field] = fixed_value
                        fixes_applied.append(
                            f"📊 Fixed price format for {field}: '{original_value}' → '{fixed_value}'"
                        )

            # Fix score formatting
            score_fields = ["metacritic_score", "opencritic_score"]
            for field in score_fields:
                if field in fixed_data:
                    original_value = fixed_data[field]
                    fixed_value = self._fix_score_format(original_value)
                    if fixed_value != original_value:
                        fixed_data[field] = fixed_value
                        fixes_applied.append(
                            f"🎯 Fixed score format for {field}: '{original_value}' → '{fixed_value}'"
                        )

            # Clean up text fields
            text_fields = ["title", "developer", "publisher"]
            for field in text_fields:
                if field in fixed_data and isinstance(fixed_data[field], str):
                    original_value = fixed_data[field]
                    fixed_value = original_value.strip()
                    if fixed_value != original_value:
                        fixed_data[field] = fixed_value
                        fixes_applied.append(f"✂️ Trimmed whitespace from {field}")

            if fixes_applied:
                logger.info(f"🔧 Auto-fixed {len(fixes_applied)} data issues")

            return fixed_data, fixes_applied

        except Exception as e:
            logger.error(f"❌ Auto-fix failed: {str(e)}")
            return game_data, [f"❌ Auto-fix error: {str(e)}"]

    def _fix_price_format(self, price_value: Any) -> Any:
        """Naprawia format ceny"""
        try:
            if not price_value:
                return price_value

            price_str = str(price_value).strip()

            # Already numeric - return as is
            try:
                float(price_str)
                return price_value
            except:
                pass

            # Extract numeric part from string like "19.99 PLN" or "$19.99"
            import re

            numeric_match = re.search(r"[\d.,]+", price_str)
            if numeric_match:
                numeric_part = numeric_match.group()
                # Standardize decimal separator
                standardized = numeric_part.replace(",", ".")
                return standardized

            return price_value

        except:
            return price_value

    def _fix_score_format(self, score_value: Any) -> Any:
        """Naprawia format wyniku"""
        try:
            if not score_value:
                return score_value

            score_str = str(score_value).strip().lower()

            # Handle common N/A variations
            if score_str in ["n/a", "na", "tbd", "unknown", "null", "none"]:
                return "N/A"

            # Try to extract numeric score
            import re

            numeric_match = re.search(r"[\d.]+", score_str)
            if numeric_match:
                try:
                    numeric_score = float(numeric_match.group())
                    # Ensure score is in valid range
                    if 0 <= numeric_score <= 100:
                        return (
                            int(numeric_score)
                            if numeric_score == int(numeric_score)
                            else numeric_score
                        )
                except:
                    pass

            return score_value

        except:
            return score_value


# Factory function
def create_completeness_checker() -> AutomaticCompletenessChecker:
    """Tworzy instancję automatycznego checkera kompletności"""
    return AutomaticCompletenessChecker()
