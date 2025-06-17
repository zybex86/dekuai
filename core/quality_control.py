"""
Phase 4: Quality Control Integration
Faza 4: Integracja kontroli jakości

Core quality control module wrapping agent_tools quality validation functionality
Główny moduł kontroli jakości opakowujący funkcjonalność walidacji z agent_tools
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Import quality validation functions from agent_tools
from agent_tools import (
    perform_quality_validation as _perform_quality_validation,
)


def perform_quality_validation(
    complete_analysis_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Przeprowadza kompleksową walidację jakości analizy gry.

    Core interface for comprehensive quality validation of game analysis.
    Główny interfejs dla kompleksowej walidacji jakości analizy gry.

    Args:
        complete_analysis_data (Dict[str, Any]): Kompletne dane analizy gry
                                               (raw data + value analysis + review + recommendations)

    Returns:
        Dict: Raport jakości z wynikami validation, rekomendacjami i metrics

    Example:
        >>> validation = perform_quality_validation(complete_analysis)
        >>> print(validation["quality_assessment"]["overall_score"])
        >>> print(validation["quality_assessment"]["quality_level"])
    """
    try:
        logger.info("🔍 Core: Starting comprehensive quality validation...")

        # Validate input structure
        if not isinstance(complete_analysis_data, dict):
            error_msg = "Core quality validation requires dictionary input"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "validation_type": "input_structure_error",
            }

        result = _perform_quality_validation(complete_analysis_data)

        if result.get("success", False):
            quality_assessment = result.get("quality_assessment", {})
            overall_score = quality_assessment.get("overall_score", 0.0)
            quality_level = quality_assessment.get("quality_level", "UNKNOWN")
            critical_failures = quality_assessment.get("critical_failures_count", 0)
            publication_ready = quality_assessment.get("publication_ready", False)

            logger.info(
                f"✅ Core: Quality validation complete - {quality_level} ({overall_score:.2f}/1.0), "
                f"Critical failures: {critical_failures}, Publication ready: {publication_ready}"
            )
        else:
            logger.warning(
                f"⚠️ Core: Quality validation failed - {result.get('error', 'Unknown error')}"
            )

        return result

    except Exception as e:
        error_msg = f"Core quality validation error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "module": "core.quality_control.perform_quality_validation",
        }


def get_quality_control_capabilities() -> Dict[str, Any]:
    """
    Zwraca informacje o możliwościach systemu kontroli jakości.

    Returns information about quality control system capabilities.
    Zwraca informacje o możliwościach systemu kontroli jakości.

    Returns:
        Dict: Dostępne opcje i możliwości systemu QC
    """
    try:
        logger.info("📋 Core: Getting quality control capabilities...")

        capabilities = {
            "success": True,
            "validation_types": {
                "data_completeness": {
                    "description": "Validates that all required data fields are present",
                    "weight": 0.3,
                    "critical": True,
                    "checks": [
                        "Game title presence",
                        "Price data availability",
                        "Rating scores existence",
                        "Basic metadata completeness",
                    ],
                },
                "logical_consistency": {
                    "description": "Ensures analysis logic is coherent and consistent",
                    "weight": 0.4,
                    "critical": True,
                    "checks": [
                        "Recommendation alignment with scores",
                        "Price analysis consistency",
                        "Value proposition logic",
                        "Cross-analysis coherence",
                    ],
                },
                "content_quality": {
                    "description": "Assesses quality and usefulness of generated content",
                    "weight": 0.3,
                    "critical": False,
                    "checks": [
                        "Review completeness",
                        "Recommendation clarity",
                        "Analysis depth",
                        "User value assessment",
                    ],
                },
            },
            "quality_levels": {
                "EXCELLENT": {
                    "score_range": "0.85 - 1.0",
                    "description": "Exceptional analysis quality, publication ready",
                    "requirements": "All validations pass, no critical failures",
                },
                "GOOD": {
                    "score_range": "0.70 - 0.84",
                    "description": "High-quality analysis with minor issues",
                    "requirements": "Most validations pass, no critical failures",
                },
                "ACCEPTABLE": {
                    "score_range": "0.55 - 0.69",
                    "description": "Adequate analysis quality with some concerns",
                    "requirements": "Basic requirements met, potential minor failures",
                },
                "POOR": {
                    "score_range": "0.40 - 0.54",
                    "description": "Below-standard analysis quality",
                    "requirements": "Multiple validation failures present",
                },
                "UNACCEPTABLE": {
                    "score_range": "0.0 - 0.39",
                    "description": "Unacceptable analysis quality",
                    "requirements": "Critical validation failures or major issues",
                },
            },
            "output_metrics": {
                "overall_score": "Weighted combination of all validation checks (0.0-1.0)",
                "critical_failures_count": "Number of critical validation failures",
                "publication_ready": "Boolean indicating if analysis meets publication standards",
                "quality_level": "Overall quality classification (EXCELLENT, GOOD, etc.)",
                "improvement_recommendations": "Specific suggestions for quality enhancement",
            },
            "integration_features": [
                "Full analysis pipeline validation",
                "Phase 1-3 integration checking",
                "Automated quality scoring",
                "Detailed failure reporting",
                "Improvement recommendations",
                "Quality metrics tracking",
            ],
        }

        logger.info("✅ Core: Quality control capabilities retrieved successfully")
        return capabilities

    except Exception as e:
        error_msg = f"Core QC capabilities error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "module": "core.quality_control.get_quality_control_capabilities",
        }


def get_quality_standards() -> Dict[str, Any]:
    """
    Zwraca standardy jakości dla różnych typów analiz.

    Returns quality standards for different types of analysis.
    Zwraca standardy jakości dla różnych typów analiz.

    Returns:
        Dict: Standardy jakości i wymagania
    """
    try:
        logger.info("📐 Core: Getting quality standards...")

        standards = {
            "success": True,
            "minimum_requirements": {
                "data_collection": {
                    "required_fields": ["title", "current_price", "MSRP"],
                    "optional_but_preferred": [
                        "metacritic_score",
                        "genres",
                        "developer",
                    ],
                    "completeness_threshold": 0.7,
                },
                "value_analysis": {
                    "required_outputs": ["value_score", "recommendation", "timing"],
                    "score_validity_range": [0, 100],
                    "recommendation_consistency": True,
                },
                "review_generation": {
                    "required_sections": [
                        "overall_rating",
                        "strengths",
                        "final_verdict",
                    ],
                    "rating_range": [0, 10],
                    "minimum_content_length": 100,
                },
                "recommendations": {
                    "required_outputs": ["recommendation_score", "match_percentage"],
                    "user_preference_matching": True,
                    "reasoning_provided": True,
                },
            },
            "publication_standards": {
                "overall_score_minimum": 0.7,
                "critical_failures_maximum": 0,
                "required_validations": [
                    "data_completeness",
                    "logical_consistency",
                    "content_quality",
                ],
                "content_guidelines": {
                    "objectivity": "Analysis must be based on data, not speculation",
                    "completeness": "All major aspects should be covered",
                    "usefulness": "Must provide actionable insights for users",
                    "consistency": "Recommendations must align with evidence",
                },
            },
            "improvement_thresholds": {
                "automatic_approval": 0.85,  # No manual review needed
                "review_recommended": 0.70,  # Should be reviewed but acceptable
                "revision_required": 0.55,  # Needs improvement before publication
                "rejection_threshold": 0.40,  # Should not be published
            },
            "validation_rules": {
                "price_analysis": [
                    "Current price must be numeric and positive",
                    "MSRP comparison must be logical",
                    "Value score must be within expected range",
                    "Recommendation must align with value metrics",
                ],
                "review_quality": [
                    "Rating must be within 0-10 range",
                    "Strengths and weaknesses must be identified",
                    "Target audience must be specified",
                    "Final verdict must be supported by analysis",
                ],
                "recommendation_logic": [
                    "User preference matching must be evident",
                    "Score calculation must be transparent",
                    "Reasoning must be provided for recommendations",
                    "Warnings must be included where appropriate",
                ],
            },
        }

        logger.info("✅ Core: Quality standards retrieved successfully")
        return standards

    except Exception as e:
        error_msg = f"Core quality standards error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "module": "core.quality_control.get_quality_standards",
        }


def validate_analysis_pipeline(
    game_name: str, include_all_phases: bool = True
) -> Dict[str, Any]:
    """
    Waliduje cały pipeline analizy dla konkretnej gry.

    Validates the complete analysis pipeline for a specific game.
    Waliduje cały pipeline analizy dla konkretnej gry.

    Args:
        game_name (str): Nazwa gry do walidacji
        include_all_phases (bool): Czy dołączyć wszystkie fazy analizy

    Returns:
        Dict: Kompletny raport walidacji pipeline
    """
    try:
        logger.info(f"🔗 Core: Validating analysis pipeline for '{game_name}'...")

        # Import core functions for pipeline testing
        from core import (
            search_and_scrape_game,
            calculate_value_score,
            calculate_advanced_value_analysis,
            generate_comprehensive_game_review,
            generate_personalized_recommendations,
        )

        pipeline_result = {
            "success": True,
            "game_name": game_name,
            "pipeline_stages": {},
            "overall_pipeline_health": "UNKNOWN",
            "critical_issues": [],
            "recommendations": [],
        }

        # Stage 1: Data Collection
        logger.info("📊 Testing data collection stage...")
        data_result = search_and_scrape_game(game_name)
        pipeline_result["pipeline_stages"]["data_collection"] = {
            "success": data_result.get("success", False),
            "error": (
                data_result.get("error") if not data_result.get("success") else None
            ),
        }

        if not data_result.get("success"):
            pipeline_result["critical_issues"].append("Data collection failed")
            pipeline_result["success"] = False

        # Stage 2: Value Analysis (if data collection succeeded)
        if data_result.get("success") and include_all_phases:
            logger.info("💰 Testing value analysis stage...")
            value_result = calculate_value_score(data_result)
            advanced_result = calculate_advanced_value_analysis(data_result)

            pipeline_result["pipeline_stages"]["value_analysis"] = {
                "basic_success": value_result.get("success", False),
                "advanced_success": advanced_result.get("success", False),
                "both_successful": value_result.get("success", False)
                and advanced_result.get("success", False),
            }

            # Stage 3: Review Generation
            logger.info("📝 Testing review generation stage...")
            review_result = generate_comprehensive_game_review(game_name)

            pipeline_result["pipeline_stages"]["review_generation"] = {
                "success": review_result.get("success", False),
                "error": (
                    review_result.get("error")
                    if not review_result.get("success")
                    else None
                ),
            }

            # Stage 4: Recommendations
            logger.info("🎯 Testing recommendations stage...")
            rec_result = generate_personalized_recommendations(
                [game_name], "indie_lover", 1
            )

            pipeline_result["pipeline_stages"]["recommendations"] = {
                "success": rec_result.get("success", False),
                "error": (
                    rec_result.get("error") if not rec_result.get("success") else None
                ),
            }

        # Determine overall pipeline health
        stages = pipeline_result["pipeline_stages"]
        successful_stages = sum(
            1 for stage in stages.values() if stage.get("success", False)
        )
        total_stages = len(stages)

        if successful_stages == total_stages:
            pipeline_result["overall_pipeline_health"] = "EXCELLENT"
        elif successful_stages >= total_stages * 0.75:
            pipeline_result["overall_pipeline_health"] = "GOOD"
        elif successful_stages >= total_stages * 0.5:
            pipeline_result["overall_pipeline_health"] = "ACCEPTABLE"
        else:
            pipeline_result["overall_pipeline_health"] = "POOR"

        logger.info(
            f"✅ Core: Pipeline validation complete - {pipeline_result['overall_pipeline_health']}"
        )
        return pipeline_result

    except Exception as e:
        error_msg = f"Core pipeline validation error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "module": "core.quality_control.validate_analysis_pipeline",
        }
